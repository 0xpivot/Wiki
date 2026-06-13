---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.07 Discovering GPOs and SYSVOL"
---

# 07 - Discovering GPOs and Analyzing Passwords in SYSVOL

## 1. Introduction to GPOs and the SYSVOL Share

In an Active Directory (AD) environment, Group Policy Objects (GPOs) are the primary mechanism used by administrators to manage configurations, deploy software, enforce security policies, and execute logon/logoff scripts across fleets of Windows machines. 

To ensure that every machine in the domain can seamlessly access and apply these policies, Domain Controllers (DCs) host a vital network share called **SYSVOL**. 
The SYSVOL share contains the public files of the domain, primarily GPOs and logon scripts, and is replicated across all Domain Controllers in the domain using the File Replication Service (FRS) or Distributed File System Replication (DFS-R).

Because any authenticated domain user (and sometimes even unauthenticated users, if misconfigured) needs to be able to read Group Policy settings to apply them locally, the SYSVOL share is universally readable by the `Authenticated Users` group. This inherent accessibility makes SYSVOL a goldmine for attackers during the enumeration phase.

## 2. The Danger of Group Policy Preferences (GPP) Passwords

### 2.1 What are Group Policy Preferences?
Introduced in Windows Server 2008, Group Policy Preferences (GPP) allowed administrators to perform tasks that previously required complex logon scripts. Common GPP use cases included:
- Mapping network drives
- Configuring local users and groups (e.g., setting the local Administrator password across the domain)
- Creating scheduled tasks
- Configuring services

### 2.2 The `cpassword` Vulnerability (MS14-025)
When an administrator used GPP to, for example, create a new local admin account and set its password, the Group Policy Management Console (GPMC) would store the password in the GPO's configuration XML file. To "secure" this, Microsoft encrypted the password field (known as `cpassword`) using AES-256.

However, in a catastrophic cryptographic blunder, Microsoft published the static AES private key used for decryption directly on MSDN. Because the SYSVOL share is readable by any domain user, an attacker simply needed to:
1. Search the SYSVOL share for XML files containing `cpassword`.
2. Extract the base64-encoded encrypted string.
3. Decrypt it using the publicly known Microsoft AES key.

Although Microsoft released a patch (MS14-025) in 2014 that prevented the creation of *new* GPP passwords, it did **not** delete existing XML files containing older `cpassword` entries. In legacy environments, these files often still linger, yielding valid credentials.

## 3. Architecture and Attack Flow Diagram

The following ASCII diagram maps out the attack path for hunting and decrypting GPP passwords from SYSVOL.

```text
+-----------------------+                                      +-------------------------------+
|   Attacker Machine    |                                      |   Target Domain Controller    |
|   Domain Authenticated|                                      |        IP: 192.168.1.10       |
+-----------+-----------+                                      +---------------+---------------+
            |                                                                  |
            | 1. Query DNS for DC Locator (_ldap._tcp.dc._msdcs)               |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 2. Connect to \\192.168.1.10\SYSVOL (SMB TCP 445)                |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 3. Authenticate as Low-Privileged Domain User                    |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 4. SMB Read Request: Recursive search for Groups.xml,            |
            |    Services.xml, ScheduledTasks.xml, Printers.xml                |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 5. DC returns XML files (Readable by Authenticated Users)        |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 6. Parse XML for 'cpassword' attribute                           |
            |    Ex: cpassword="j/zJ...="                                      |
            |                                                                  |
            | 7. Local Offline Decryption using static MSDN AES Key            |
            |    (No further interaction with DC needed)                       |
            |                                                                  |
            | 8. Recovered Cleartext Password: "LocalAdminPassword2020!"       |
            |                                                                  |
+-----------+-----------+                                      +-------------------------------+
| Attacker uses the     |                                      | The DC simply served standard |
| recovered password to |                                      | GPO files as requested by     |
| laterally move via    |                                      | an authenticated domain user. |
| SMB/RDP to endpoints. |                                      +-------------------------------+
+-----------------------+
```

## 4. Enumeration Tooling Deep Dive

Identifying GPOs and digging through SYSVOL can be done manually or via automated tooling.

### 4.1 Manual Enumeration via SMB

You can use standard command-line tools or `smbclient` to explore the SYSVOL share. The typical path is:
`\\<Domain Controller>\SYSVOL\<Domain Name>\Policies\`

Within the `Policies` directory, GPOs are stored in folders named after their GUIDs. Attackers look specifically for:
- `\Machine\Preferences\Groups\Groups.xml`
- `\Machine\Preferences\Services\Services.xml`
- `\User\Preferences\Printers\Printers.xml`
- `\Machine\Preferences\ScheduledTasks\ScheduledTasks.xml`

**Example using Linux `smbclient`:**
```bash
smbclient -U 'user%password' //192.168.1.10/SYSVOL
smb: \> cd domain.local\Policies\
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *.xml
```
Once downloaded, a simple `grep` or `findstr` command can locate the `cpassword` string.

```bash
grep -ri "cpassword" .
```

### 4.2 Automated Decryption with `gpp-decrypt`

If you manually extract a `cpassword` string, you can decrypt it offline using the `gpp-decrypt` utility available in Kali Linux.

**Command:**
```bash
gpp-decrypt "j/zJ0b... base64 string ..."
```
**Output:**
```text
[+] Decrypted Password: AdminWinter2019!
```

### 4.3 NetExec (formerly CrackMapExec)

NetExec automates the entire process of mounting the SYSVOL share, searching for GPP XML files, extracting the `cpassword`, and decrypting it on the fly.

**Command:**
```bash
nxc smb 192.168.1.10 -u 'user' -p 'password' -M gpp_password
```
If successful, NetExec will output the identified file, the username, and the decrypted cleartext password directly to the console.

### 4.4 Metasploit Framework

Metasploit contains a specific post-exploitation module for this exact vulnerability.

**Command:**
```ruby
msf> use post/windows/gather/credentials/gpp
msf> set SESSION 1
msf> run
```
This module relies on an existing Meterpreter session to query SYSVOL.

### 4.5 PowerView / BloodHound

BloodHound maps out GPO links and their impacts. If an attacker controls a user that has permission to *edit* a GPO, BloodHound will flag this as a potential attack path. PowerView can be used to query GPO configurations via LDAP.

**PowerView Command:**
```powershell
Get-DomainGPO | Select-Object displayname, whenchanged
```

## 5. Beyond `cpassword`: Other SYSVOL Treasures

While GPP passwords are the most famous vulnerability, SYSVOL often contains other misconfigurations:
1. **Logon/Logoff Scripts (`.bat`, `.vbs`, `.ps1`):** Administrators frequently write custom scripts to mount drives or query databases upon user logon. These scripts often contain hardcoded service account credentials or API keys.
2. **Configuration Files (`.ini`, `.config`):** Deployed software configurations might be stored in SYSVOL, leaking database connection strings or internal URLs.
3. **Registry Manipulations:** GPOs can push registry changes containing sensitive data in plaintext.

## 6. Defensive Considerations and Remediation

### 6.1 Identify and Delete Legacy GPP Passwords
Administrators must actively hunt for and remove residual GPP password XML files. Even if the GPO is no longer linked or active, the XML file residing in SYSVOL is still a risk. Microsoft provides a PowerShell script specifically designed to search for and remove `cpassword` attributes.

### 6.2 Apply MS14-025
Ensure all systems are fully patched to prevent the creation of new GPP passwords. Modern administrators should use **Local Administrator Password Solution (LAPS)** instead of GPP to manage local admin passwords securely.

### 6.3 Secure Scripting Practices
Never hardcode credentials in logon scripts or batch files stored in SYSVOL. Use managed service accounts (gMSA) or retrieve credentials securely from a vault at runtime if absolutely necessary.

### 6.4 Telemetry and Monitoring
- Monitor access to the `SYSVOL` share. While standard read access is normal, recursive directory listings or mass file downloads (especially targeting `.xml` or `.ps1` files) from non-system processes should trigger alerts.
- **Event ID 5140 / 5145:** Monitor for suspicious network share access patterns against Domain Controllers.

## 7. Chaining Opportunities

- **GPP to Local Admin:** The recovered GPP password is often the local administrator password for multiple machines. This immediately allows lateral movement via Pass-the-Hash or cleartext authentication (RDP/SMB) to endpoints.
- **Logon Script Modification:** If an attacker finds a misconfigured GPO where they have *write* access to the SYSVOL script directory, they can append malicious code (e.g., a reverse shell) to a logon script. Every user who logs in will execute the attacker's payload.

## 8. Related Notes
- [[06 - Enumerating SMB Shares and Null Sessions]]
- [[18 - Lateral Movement via SMB and WMI]]
- [[21 - Local Administrator Password Solution (LAPS) Evasion]]
- [[13 - BloodHound and Active Directory Graph Analysis]]

## Real-World Attack Scenario
## Real-World Attack Scenario

During an internal security assessment for a regional financial institution, I established an initial unauthenticated foothold. My goal was to escalate privileges by identifying misconfigurations in Active Directory Group Policy Objects (GPOs), specifically looking for legacy Group Policy Preferences (GPP) that might expose encrypted passwords. The environment was mature, but had undergone numerous migrations over the last decade.

**Thought Process:**
The `SYSVOL` share is accessible to any authenticated domain user and contains all the GPOs for the domain. Historically, administrators used GPP to push out local administrator passwords or map drives, which stored the password (known as `cPassword`) in an AES-256 encrypted format. However, Microsoft accidentally published the static AES private key in 2012. If I could locate an old `Groups.xml` or `Printers.xml` file within SYSVOL, I could decrypt the `cPassword` and potentially gain local administrator access across multiple endpoints.

**Execution:**
First, I authenticated to the domain controller's SYSVOL share to verify access using my low-privileged compromised account:
```bash
smbclient -U 'jsmith' //192.168.100.10/SYSVOL
```
Instead of manually crawling through the complex `{GUID}` folder structures, I leveraged NetExec to automate the search for `cPassword` attributes within the SYSVOL share across the domain controller:
```bash
nxc smb 192.168.100.10 -u 'jsmith' -p 'Welcome2023!' -M gpp_password
```
The module successfully identified a `Groups.xml` file located in `\domain.local\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\Machine\Preferences\Groups\`. NetExec automatically extracted the `cPassword` hash and decrypted it using the well-known static Microsoft AES key.

The decrypted password was `Admin!@#2015`. I immediately checked where this password was valid by spraying it across the server subnet:
```bash
nxc smb 192.168.100.0/24 -u 'Administrator' -p 'Admin!@#2015' --local-auth
```

**Outcome:**
The command returned `(Pwn3d!)` on over 40 servers, including the primary backup server. The organization had created a GPO years ago to set the local administrator password and never removed the GPP file after the Microsoft patch. By exploiting this legacy SYSVOL misconfiguration, I escalated from a standard domain user to local administrator on a significant portion of the server infrastructure in under ten minutes.

