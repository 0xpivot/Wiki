---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.06 Enumerating SMB Shares and Null Sessions"
---

# 06 - Enumerating SMB Shares and Null Sessions

## 1. Introduction to SMB in Active Directory

The Server Message Block (SMB) protocol is a network file sharing protocol that allows applications on a computer to read and write to files and to request services from server programs in a computer network. Within an Active Directory (AD) environment, SMB is ubiquitous. It is the primary mechanism by which Group Policy Objects (GPOs) are distributed, login scripts are accessed, and shared network drives are mapped for end-users.

Because of its fundamental role in Windows domains, SMB is often the first port of call (literally, TCP port 445, and historically TCP 139) for attackers performing reconnaissance. By interrogating SMB services, an attacker can extract a wealth of information, ranging from domain password policies and user lists to actual sensitive files containing cleartext credentials. SMB has evolved through several versions (SMBv1, SMBv2, SMBv3), each introducing new features and security enhancements like encryption and signing. However, misconfigurations in any version can lead to severe data leakage.

## 2. The Concept of Null Sessions

### 2.1 What is a Null Session?
A Null Session (also known as an anonymous logon) occurs when a client connects to an SMB share or the IPC$ (Inter-Process Communication) share without providing a username or password. Historically, in older versions of Windows (such as Windows NT and Windows 2000), Null Sessions were enabled by default to allow unauthenticated computers to obtain lists of accounts and shares, which was necessary for certain legacy network browsing features and pre-Windows 2000 domain trust architectures.

### 2.2 Why do they still exist?
While modern Windows operating systems (Windows Server 2012+ and Windows 10+) severely restrict Null Session access by default, misconfigurations often re-introduce this vulnerability. Administrators might enable anonymous access to specific shares for legacy application compatibility, or third-party NAS devices (Network Attached Storage) joined to the domain might incorrectly implement SMB access controls.

When a Null Session is permitted, it allows an attacker to query the domain controller or a member server via RPC (Remote Procedure Call) over SMB. This query can reveal:
- The complete list of domain users and their associated Security Identifiers (SIDs)
- Domain groups and their memberships
- Password policies (minimum length, complexity requirements, lockout thresholds)
- Network shares, hidden shares, and their respective permissions
- Active sessions and logged-on users across the network

## 3. Architecture and Attack Flow Diagram

Below is an ASCII diagram illustrating the attack path when an attacker exploits a Null Session to enumerate detailed domain information from a misconfigured Domain Controller.

```text
+-----------------------+                                      +-------------------------------+
|   Attacker Machine    |                                      |   Target Domain Controller    |
|   IP: 192.168.1.100   |                                      |        IP: 192.168.1.10       |
+-----------+-----------+                                      +---------------+---------------+
            |                                                                  |
            | 1. Initiate SMB Connection (TCP 445)                             |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 2. SMB Negotiate Protocol Response (Supported Dialects)          |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 3. Session Setup Request (User: "", Pass: "")                    |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 4. Session Setup Response (STATUS_SUCCESS / Guest/Anon Logon)    |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 5. Tree Connect Request (\\192.168.1.10\IPC$)                    |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 6. Tree Connect Response (STATUS_SUCCESS)                        |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 7. Bind to SAMR / LSA RPC Pipes over IPC$                        |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 8. Query Account Policies, Enumerate Users/Groups via SAMR       |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 9. Returned Domain Data (Users, Lockout thresholds, SIDs)        |
            |<-----------------------------------------------------------------|
            |                                                                  |
+-----------+-----------+                                      +---------------+---------------+
| Attacker extracts the |                                      | DC complies because "Network  |
| domain data to plan   |                                      | Access: Restrict Anonymous"   |
| password spraying or  |                                      | is improperly configured or   |
| user impersonation.   |                                      | legacy support is enabled.    |
+-----------------------+                                      +-------------------------------+
```

## 4. Enumeration Tooling Deep Dive

To effectively enumerate SMB shares and test for Null Sessions, several tools are commonly employed during the initial reconnaissance phase of a VAPT engagement. Each tool has its own strengths, specific use cases, and levels of noisiness on the network.

### 4.1 Nmap SMB Scripts

Nmap offers a suite of NSE (Nmap Scripting Engine) scripts specifically designed for deep SMB enumeration. It is highly scriptable and excellent for large subnets.

**Command:**
```bash
nmap -p 139,445 --script smb-enum-shares,smb-enum-users,smb-os-discovery 192.168.1.10
```

**What it does:**
- `smb-os-discovery`: Determines the OS version, computer name, netBIOS name, and whether the target is part of an AD domain or standalone.
- `smb-enum-shares`: Attempts to list all available shares and determines the access level (Read/Write) explicitly for the anonymous/null user.
- `smb-enum-users`: Attempts to pull the complete list of users from the target system using MSRPC over SMB.

**Sample Output Snippet:**
```text
Host script results:
| smb-enum-shares: 
|   account_used: <blank>
|   \\192.168.1.10\IPC$: 
|     Type: STYPE_IPC
|     Comment: IPC Service (DC01)
|     Users: 1
|     Max Users: <unlimited>
|     Path: C:\tmp
|     Anonymous access: READ
|   \\192.168.1.10\Public_Shares: 
|     Type: STYPE_DISKTREE
|     Comment: Public Share for All Department Users
|     Anonymous access: READ/WRITE
|_    Current user access: READ/WRITE
```
In this scenario, the `Public_Shares` folder allows READ/WRITE access for anonymous users, representing a critical misconfiguration that could be used to host malicious payloads.

### 4.2 smbclient

`smbclient` is an FTP-like client used to interact with SMB/CIFS resources on servers. It is excellent for manual, interactive browsing of shares.

**Testing for Null Sessions and Listing Shares:**
```bash
smbclient -N -L //192.168.1.10
```
- `-N`: Suppresses the password prompt, forcing a Null session.
- `-L`: Lists shares available on the specified target.

**Connecting to an Accessible Share:**
Once a readable share is identified (e.g., `Public_Shares`), you can establish an interactive session:
```bash
smbclient -N //192.168.1.10/Public_Shares
```
Inside the interactive prompt, commands like `ls` (list files), `cd` (change directory), `get` (download), and `put` (upload) operate exactly like standard FTP commands.

### 4.3 enum4linux and enum4linux-ng

`enum4linux` is a legacy wrapper script built around standard Samba tools (`smbclient`, `rpcclient`, `net`, etc.) designed specifically to extract maximum information from Windows and Samba hosts. `enum4linux-ng` is its modern, Python-based rewrite that operates much faster, supports JSON export, and produces cleaner output.

**Command Example:**
```bash
enum4linux -a 192.168.1.10
# OR the modern variant
enum4linux-ng -A 192.168.1.10
```

**Key Information Gathered Iteratively:**
- `-U`: User lists extraction
- `-M`: Machine lists extraction
- `-S`: Share lists extraction
- `-P`: Password policy information (crucial for spraying)
- `-G`: Group and member lists

### 4.4 rpcclient

`rpcclient` is a utility initially developed to test MS-RPC functionality in Samba. It allows an attacker to execute arbitrary RPC commands on the target if a Null Session (or an authenticated session) is successfully established via the `IPC$` share.

**Establishing a Null Session:**
```bash
rpcclient -U "" -N 192.168.1.10
```

**Highly Useful rpcclient Commands:**
- `srvinfo`: Retrieve server OS information and build numbers.
- `enumdomusers`: Enumerate all domain users and their RIDs (Relative Identifiers).
- `enumdomgroups`: Enumerate all domain groups.
- `querydominfo`: Query the domain's high-level information including the active password policy, lockout thresholds, and lockout duration.
- `queryuser <RID>`: Get detailed information about a specific user by their RID, including last logon time, bad password counts, and description fields (which sometimes contain passwords).

**Example Execution Flow:**
```bash
rpcclient $> enumdomusers
user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[jsmith] rid:[0x450]
user:[svc_sql_prod] rid:[0x451]

rpcclient $> queryuser 0x451
	User Name   :	svc_sql_prod
	Full Name   :	SQL Production Service Account
	Home Drive  :
	Dir Drive   :
	Profile Path:
	Logon Script:
	Description :	Password is SQLAdmin2023! Do not change.
	Workstations:
	Comment     :
	Remote Dial :
	Logon Time               :	Wed, 10 Jun 2026 09:00:00 UTC
```
*Note the incredibly sensitive data often leaked in the Description field!*

### 4.5 NetExec (formerly CrackMapExec)

NetExec (nxc) is a modern, Swiss-army-knife tool for AD enumeration and post-exploitation. It relies heavily on Python's Impacket library to interact directly with SMB and RPC.

**Checking SMB Access and Null Sessions Across a Subnet:**
```bash
nxc smb 192.168.1.0/24 -u '' -p '' --shares
```

**Extracting Domain Password Policy:**
```bash
nxc smb 192.168.1.10 -u '' -p '' --pass-pol
```

**Enumerating Domain Users via Null Session:**
```bash
nxc smb 192.168.1.10 -u '' -p '' --users
```

NetExec's concurrent architecture makes it ideal for sweeping entire corporate subnets rapidly, identifying misconfigured endpoints that allow anonymous access in seconds rather than minutes.

## 5. Hunting for Sensitive Files in Accessible Shares

Discovering an accessible share is merely the beginning. The subsequent objective is to parse through the share's contents to locate sensitive data. Attackers systematically search for:
- **Configuration Files:** `web.config`, `appsettings.json`, `Unattend.xml`, `sysprep.inf` (which often contain deployment credentials).
- **Automation Scripts:** `.ps1`, `.bat`, `.vbs` files used by IT admins containing hardcoded credentials or API keys.
- **Backups and Databases:** `.bak`, `.sql`, `.vhd`, or even standalone `.kdbx` (KeePass) files.
- **Corporate Documentation:** Network topology diagrams, onboarding guides, and password spreadsheets (e.g., `Passwords.xlsx`, `IT_Inventory.csv`).

**Automating the Hunt with Snaffler:**
Snaffler is a robust, Windows-based tool designed to automatically crawl accessible SMB shares across an entire domain and use regex matching to highlight sensitive files (passwords, keys, PII). While it typically requires domain credentials to crawl the whole domain, if a Null Session grants access to specific wide-open shares, Snaffler or custom bash scripts (like `find` mounted over `cifs`) can automate the extraction process.

## 6. Defensive Considerations and Remediation Strategies

### 6.1 Disabling Null Sessions Systematically
To permanently prevent Null Sessions, administrators must configure the following Group Policy settings applied to all workstations and servers under `Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> Security Options`:
1. **Network access: Restrict anonymous access to Named Pipes and Shares** -> `Enabled`
2. **Network access: Do not allow anonymous enumeration of SAM accounts** -> `Enabled`
3. **Network access: Do not allow anonymous enumeration of SAM accounts and shares** -> `Enabled`
4. **Network access: Let Everyone permissions apply to anonymous users** -> `Disabled`

### 6.2 Eradicating SMBv1
SMBv1 is heavily deprecated, lacks modern encryption/signing, and is fundamentally insecure (famously exploited by the EternalBlue / MS17-010 vulnerability). It must be disabled entirely on all endpoints and servers.
```powershell
# Check SMBv1 status
Get-SmbServerConfiguration | Select EnableSMB1Protocol

# Disable SMBv1 forcefully
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force
```

### 6.3 Telemetry, Logging, and Detection
Defenders should baseline normal SMB traffic and monitor for anomalous enumeration behavior:
- **Event ID 4624 (Logon Success):** Look for Logon Type 3 (Network Logon) where the `TargetUserName` is explicitly `ANONYMOUS LOGON`. A high volume of these events originating from a single IP address strongly indicates automated enumeration.
- **Event ID 5140 (A network share object was accessed):** Triggers when a network share is accessed. Monitor specifically for access to the `IPC$` share by the anonymous user.
- **Event ID 4648 (A logon was attempted using explicit credentials):** Useful to correlate with other anomalous activities.
- Implement network IDS/IPS rules to alert on excessive MSRPC traffic targeting the SAMR and LSA pipes from non-administrative subnets.

## 7. Chaining Opportunities for Attackers

The foundational information gathered via SMB enumeration and Null Sessions acts as the springboard for numerous advanced attacks:
- **User Enumeration -> Password Spraying:** The exhaustive list of valid usernames obtained via `rpcclient` can be aggregated and fed into tools like NetExec to perform password spraying (e.g., guessing `Spring2026!`). See `[[12 - Password Spraying and Credential Stuffing in AD]]`.
- **Password Policy -> Safe Brute-forcing:** Knowing the exact lockout threshold (e.g., 5 attempts within 15 minutes) allows attackers to safely throttle their password sprays without ever locking out legitimate accounts, thereby avoiding immediate detection by SOC analysts.
- **Sensitive Files -> Instant Initial Access:** Finding hardcoded domain admin credentials in a backup script on an open share instantly escalates an unauthenticated attacker to an authenticated foothold, bypassing the need for complex exploitation.

## 8. Related Notes
- [[07 - Discovering GPOs and Analyzing Passwords in SYSVOL]]
- [[08 - Enumerating SPNs and Finding Service Accounts]]
- [[12 - Password Spraying and Credential Stuffing in AD]]
- [[05 - Active Directory Architecture Overview]]
- [[15 - SMB Relay Attacks and NTLM Relaying]]

## Real-World Attack Scenario
## Real-World Attack Scenario

In a recent internal penetration test for a mid-sized healthcare provider, the objective was to identify initial access vectors from an unauthenticated network perspective. The environment consisted of a flat `/24` subnet populated with both modern Windows Server 2019 machines and legacy Windows Server 2008 R2 systems used for old medical imaging software.

**Thought Process:**
Given the presence of legacy systems, there was a high probability of misconfigured SMB shares and potentially enabled Null Sessions. My first priority was to sweep the subnet to identify active SMB services and immediately check if any host permitted anonymous access. If a Null Session was allowed, I could extract the domain's password policy and a complete list of users, which would perfectly set up a targeted password spraying attack without triggering account lockouts.

**Execution:**
I began by sweeping the subnet using NetExec to rapidly identify SMB hosts and test for Null Session capabilities in a single command:
```bash
nxc smb 192.168.50.0/24 -u '' -p '' --shares
```
The output highlighted several hosts, but one legacy file server (`FS-ARCHIVE.medcorp.local` at `192.168.50.45`) returned `[+] medcorp.local\ : (Pwn3d!)` indicating a successful Null Session and listed multiple accessible shares, including `IPC$` and `IT_Backups`.

Realizing I had unauthenticated RPC access, I used `rpcclient` to enumerate domain users and the password policy:
```bash
rpcclient -U "" -N 192.168.50.45
rpcclient $> querydominfo
rpcclient $> enumdomusers
```
The `querydominfo` command revealed a password lockout threshold of 5 attempts. The `enumdomusers` command provided a list of over 300 valid domain usernames. 

Simultaneously, I connected to the readable `IT_Backups` share using `smbclient`:
```bash
smbclient -N //192.168.50.45/IT_Backups
```
Inside the share, I found an old PowerShell script named `Map-Drives.ps1`. Downloading and inspecting the script revealed hardcoded credentials for a service account (`svc_storage : Storage@Admin2019!`).

**Outcome:**
Without ever having to guess a password or risk account lockouts, the Null Session misconfiguration provided both the entire domain user roster and an initial set of valid credentials. I immediately validated the `svc_storage` account using NetExec:
```bash
nxc smb 192.168.50.0/24 -u 'svc_storage' -p 'Storage@Admin2019!'
```
The credentials were valid across multiple servers, granting an authenticated foothold into the Active Directory environment and setting the stage for further privilege escalation and lateral movement.

