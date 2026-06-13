---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.11 Extracting Credentials from Configuration Files"
---
# 11 - Extracting Credentials from Configuration Files

## 1. Introduction and Architectural Context

During post-exploitation within an Active Directory environment, one of the most fruitful avenues for privilege escalation and lateral movement involves scouring the file system of compromised hosts for hardcoded credentials. System administrators, developers, and automated deployment pipelines frequently leave credentials embedded within configuration files, scripts, unattended installation files, and database connection strings.

This technique is often stealthier than memory-based credential dumping (like Mimikatz) because it relies heavily on native file-read operations rather than injecting into `lsass.exe`, which modern Endpoint Detection and Response (EDR) solutions monitor heavily. Native operations blend in seamlessly with legitimate administrative activities.

### 1.1 The Problem of Hardcoded Credentials

The presence of hardcoded credentials usually stems from several systemic issues:
1. **Automated Deployments:** Using tools like SCCM, MDT, or custom PowerShell scripts where administrative credentials are required to join domains, map drives, or install software quietly without user interaction.
2. **Legacy Applications:** Older applications that cannot leverage Managed Service Accounts (gMSA) and instead rely on hardcoded plaintext credentials or poorly obfuscated credentials in configuration files.
3. **Developer Negligence:** Storing connection strings for databases, API keys, or LDAP bind accounts in web applications (`web.config`, `appsettings.json`), often pushed directly from version control systems.
4. **Administrative Convenience:** Administrators keeping `.txt` or `.ps1` files on their desktops containing service account passwords to quickly restart services or troubleshoot issues.

## 2. Typical Target Files and Locations

When hunting for configuration files, attackers typically look for specific extensions and file names. A deep understanding of Windows deployment mechanics provides an attacker with exact file paths to target.

### 2.1 Unattended Installation Files

Unattended Windows Setup answer files are used to automate the deployment of Windows operating systems. These files can contain local administrator passwords, domain join credentials, and product keys. The passwords might be Base64 encoded, but are easily decoded.

**Common Locations:**
- `C:\sysprep.inf`
- `C:\sysprep\sysprep.xml`
- `C:\Windows\System32\sysprep.inf`
- `C:\Windows\Panther\Unattend\Unattended.xml`
- `C:\Windows\Panther\Unattend.xml`

**Command to Search:**
```cmd
dir /s /b C:\*unattend*.xml
dir /s /b C:\*sysprep*.inf
```

### 2.2 IIS Configuration Files

Internet Information Services (IIS) servers often contain connection strings, application pool identities, and sometimes hardcoded credentials within configuration files.

**Web.config:**
Often located in the web root (e.g., `C:\inetpub\wwwroot\web.config`), these files might contain plaintext or encrypted connection strings. A connection string containing `User ID=sa;Password=SuperSecretPassword` is a goldmine.

**ApplicationHost.config:**
Located at `C:\Windows\System32\inetsrv\config\applicationHost.config`, this file manages application pools. Sometimes, the identities used to run these pools are saved here. If encrypted, `appcmd.exe` can sometimes be used to decrypt them if run as SYSTEM.

### 2.3 Group Policy Preferences (GPP) cpassword

Historically, administrators could set local administrator passwords across a domain using Group Policy Preferences. Microsoft encrypted these passwords (known as `cpassword`) using a static AES key that was inadvertently published on MSDN. Although patched in MS14-025, many legacy environments still have these XML files lying dormant in SYSVOL.

**Location:**
`\\<DOMAIN>\SYSVOL\<DOMAIN>\Policies\{GUID}\Machine\Preferences\Groups\Groups.xml`

### 2.4 Application Settings and Scripts

Developers often leave credentials in scripts (.ps1, .bat, .vbs) or application configuration files (.json, .xml, .ini). 
- `appsettings.json` (ASP.NET Core)
- `tomcat-users.xml` (Tomcat)
- `Jenkins/credentials.xml`
- PowerShell profiles: `C:\Users\<user>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`

## 3. Extraction Methodologies in Depth

### 3.1 Unattend.xml Extraction

Within an `Unattend.xml` file, you might see a block like this:

```xml
<UserAccounts>
    <LocalAccounts>
        <LocalAccount wcm:action="add">
            <Password>
                <Value>UEBzc3dvcmQxMjM=</Value>
                <PlainText>false</PlainText>
            </Password>
            <Description>Local Administrator</Description>
            <DisplayName>Admin</DisplayName>
            <Group>Administrators</Group>
            <Name>Admin</Name>
        </LocalAccount>
    </LocalAccounts>
</UserAccounts>
```

If `PlainText` is false, the value is typically Base64 encoded, sometimes with an appended word "Password". In PowerShell, you can easily decode it:

```powershell
# Decode the base64 string
$encodedString = "UEBzc3dvcmQxMjM="
$decoded = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($encodedString))
Write-Output "Decoded Password: $decoded"
# Outputs: P@ssword123
```

### 3.2 Automated Hunting with PowerShell

Attackers use automated scripts to find these files quickly. Here is an example of an aggressive script that hunts for passwords in files:

```powershell
# Hunt for specific file types containing "password" or "pwd"
$pathsToSearch = @("C:\Windows\Panther\", "C:\inetpub\", "C:\Users\")
foreach ($path in $pathsToSearch) {
    $files = Get-ChildItem -Path $path -Include *.xml,*.ini,*.txt,*.config,*.json -Recurse -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # Checking file content for keyword matches
        if (Select-String -Path $file.FullName -Pattern "password=|pwd=|secret=" -Quiet -ErrorAction SilentlyContinue) {
            Write-Output "[!] Potential credentials found in: $($file.FullName)"
        }
    }
}
```

A more refined approach uses known paths to minimize disk I/O and evade detection by behavioral analytics that monitor for excessive file reads.

### 3.3 Decrypting IIS AppPool Credentials

If you discover an application pool running as a custom domain user, the credentials are encrypted in `applicationHost.config`. If you have local administrative rights, you can extract these passwords using `appcmd.exe`.

```cmd
# List app pools and extract config
%systemroot%\system32\inetsrv\appcmd.exe list apppool /config
```

Sometimes you need to use tools like `APPCMD` combined with specific encryption keys, or specialized tools like `IIS-ShortName-Scanner` or Metasploit/Cobalt Strike modules to fully decrypt these values if they are protected by DPAPI. If the system is highly restricted, an attacker might copy the machine keys and the config offline for local decryption.

## 4. Visualizing the Credential Hunting Flow

```text
+------------------------------------------------------------------+
|                  Credential Hunting Execution Flow                 |
+------------------------------------------------------------------+

[Attacker Node / Compromised Endpoint]
         |
         | 1. Execute Search Query (dir, Select-String, findstr)
         v
+------------------+     2. Match known    +-----------------------+
| Local Filesystem | <-------------------> | Target Config Files   |
+------------------+     file patterns     +-----------------------+
         |                                 | - Unattend.xml        |
         |                                 | - web.config          |
         |                                 | - Groups.xml (SYSVOL) |
         |                                 | - appsettings.json    |
         |                                 +-----------------------+
         | 3. Read Content
         v
+------------------+
| Parsing Engine   | ---> 4. Identify 'password', 'pwd', 'secret'
+------------------+
         |
         | 5. Extraction & Decoding (Base64, AES, DPAPI)
         v
+------------------+
| Credential Store | ---> 6. Lateral Movement / PrivEsc
+------------------+
```

## 5. Advanced Extraction: Registry-Based Configuration

While files are the primary target, the Windows Registry acts as a massive configuration database and is often scoured alongside files. Administrators frequently save connection parameters and autologon details within registry hives.

- **PuTTY Sessions:** Stored at `HKCU\Software\SimonTatham\PuTTY\Sessions`. Can reveal target hostnames, usernames, and sometimes proxy credentials.
- **VNC Passwords:** Various VNC implementations store obfuscated passwords in the registry. These are easily reversed.
- **Autologon Credentials:** `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` might contain `DefaultUserName` and `DefaultPassword` in plaintext. This is incredibly common for kiosk machines, display boards, or automated testing environments.

Extracting Autologon keys:
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v DefaultPassword
```

## 6. Operational Security (OPSEC) for Attackers

When performing these searches, dropping a massive PowerShell script that heavily utilizes `Get-ChildItem -Recurse` on the `C:\` drive will generate massive disk I/O. This behavior is highly anomalous and might trigger EDR heuristics designed to detect ransomware-like behavior or mass-discovery. 

Instead, an OPSEC-safe approach involves targeting specific files directly or querying file metadata via the Windows API (e.g., using BOFs in Cobalt Strike) rather than relying on native shells. Furthermore, large searches may crash legacy systems due to resource exhaustion.

It is highly recommended to perform selective discovery. Only search the `C:\Windows\Panther` or `C:\inetpub` directories instead of indexing the whole `C:\` drive. Using WMI to query specific files can also bypass some simplistic command line logging mechanisms.

```powershell
# OPSEC safe WMI query for specific files without triggering massive I/O
Get-WmiObject -Class CIM_DataFile -Filter "Drive='C:' AND Path='\\Windows\\Panther\\' AND Extension='xml'"
```

## 7. Defensive Considerations and Mitigation

### 7.1 Mitigation Strategies

- **LAPS (Local Administrator Password Solution):** Eliminate the need for `Unattend.xml` files containing hardcoded local administrator passwords by implementing LAPS, which randomizes and securely stores local admin passwords in AD.
- **Managed Service Accounts (gMSA):** Instead of placing service account passwords in `web.config` or IIS, use gMSAs, where AD manages the password automatically and applications can request it dynamically.
- **Secrets Management:** Utilize dedicated secrets management vaults (e.g., HashiCorp Vault, Azure Key Vault, AWS Secrets Manager) instead of placing connection strings in source code or flat files. Applications should authenticate to the vault using certificates or managed identities to retrieve the database credentials at runtime.
- **Clean Up Artifacts:** Ensure deployment pipelines (MDT, SCCM, Ansible) automatically delete or sanitize deployment files (like `sysprep.inf` or `Unattend.xml`) immediately after the setup process concludes.

### 7.2 Detection Mechanisms

- **File Access Monitoring:** Monitor for abnormal, recursive `findstr`, `Select-String`, or `dir /s` commands traversing `C:\` or `C:\Windows\Panther\`.
- **Command Line Auditing:** Look for command lines referencing `Unattend.xml`, `sysprep`, or `Groups.xml`. Event ID 4688 (Process Creation) with full command-line logging enabled is vital here.
- **Honeypot Files:** Place dummy configuration files with traceable, fake credentials (honeytokens). If an attacker attempts to authenticate using these fake credentials, an immediate high-fidelity alert is triggered.

## 8. Sigma Rule Example for Detection

A Sigma rule can be crafted to detect suspicious command line activity hunting for passwords.

```yaml
title: Suspicious Password File Discovery via Command Line
id: 12345678-1234-1234-1234-123456789012
status: experimental
description: Detects command lines used to search for files containing passwords.
author: Blue Team
logsource:
    category: process_creation
    product: windows
detection:
    selection_tools:
        CommandLine|contains:
            - 'findstr'
            - 'Select-String'
            - 'dir /s'
    selection_keywords:
        CommandLine|contains_all:
            - 'password'
            - '.xml'
    condition: selection_tools and selection_keywords
falsepositives:
    - Legitimate administrative scripts searching for specific configurations.
level: medium
```

## Real-World Attack Scenario

In a recent engagement against a large healthcare provider, the internal network was heavily segmented, and the initial foothold was limited to a low-privileged Citrix virtual desktop. The primary objective was to escalate privileges and move laterally to the internal server VLAN. Given the restrictive nature of the environment, running noisy enumeration tools like BloodHound or aggressive port scans would immediately trigger the organization's EDR solutions. Instead, the attacker decided to leverage the "Living off the Land" (LotL) approach, focusing on local file system enumeration to find sensitive configuration files.

The attacker recognized that the Citrix golden image was likely deployed using an automated provisioning system such as Microsoft Deployment Toolkit (MDT) or System Center Configuration Manager (SCCM). Often, these deployments leave behind answer files that contain plaintext or poorly encrypted credentials used during the build process. To search for these remnants without triggering excessive disk I/O alerts, the attacker executed a targeted search using native Windows commands rather than a heavy recursive script. 

Opening a standard command prompt, the attacker ran:
```cmd
dir /b /s C:\Windows\Panther\Unattend.xml
dir /b /s C:\Windows\System32\sysprep\sysprep.inf
```
The first command successfully located an `Unattend.xml` file at `C:\Windows\Panther\Unattend.xml`. Knowing that reading the file with `type` is generally safe and flies under the radar of most behavioral analytics, the attacker dumped the contents:
```cmd
type C:\Windows\Panther\Unattend.xml | findstr /i "password"
```

The output revealed a `<Password>` tag containing a Base64-encoded string: `QWRtMW5QYXNzdzByZCE=`. The attacker quickly decoded this locally using PowerShell:
```powershell
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("QWRtMW5QYXNzdzByZCE="))
```
The decoded string was `Adm1nPassw0rd!`. Because the organization reused the local Administrator password across all workstations instead of using LAPS (Local Administrator Password Solution), the attacker now had local administrative access to the entire VDI subnet.

To verify the credentials, the attacker used `net use` to test access against a nearby server within the VDI subnet.
```cmd
net use \\10.10.5.50\IPC$ /user:Administrator Adm1nPassw0rd!
```
The command completed successfully. With local admin rights, the attacker then extracted the LSASS process memory from the targeted machine, successfully dumping the NTLM hash of an enterprise Domain Admin who had previously logged in via RDP to troubleshoot an issue. This single overlooked deployment file directly facilitated a complete domain compromise.

## 9. Chaining Opportunities

- **[[12 - Harvesting Credentials from Password Managers]]:** If configuration files contain master passwords or encryption keys for local password databases.
- **[[15 - Token Impersonation and Stealing Incognito]]:** Once credentials are found, they can be used to spawn processes or impersonate users across the network using tokens.
- **[[08 - Pass the Hash]]:** If the extracted configuration file yields an NTLM hash rather than a plaintext password, or if the password leads to a user hash elsewhere.
- **[[17 - Lateral Movement via WMI and WinRM]]:** Valid credentials extracted from config files can be plugged directly into WinRM sessions for remote execution.

## 10. Related Notes

- [[02 - Local Privilege Escalation Essentials]]
- [[05 - Windows Post-Exploitation Enumeration]]
- [[21 - Abusing Group Policy Preferences]]
- [[03 - Windows PrivEsc - Unquoted Service Paths]]
