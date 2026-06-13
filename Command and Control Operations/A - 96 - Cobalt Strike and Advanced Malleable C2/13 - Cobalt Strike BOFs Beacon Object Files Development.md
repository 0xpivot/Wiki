---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.13 Cobalt Strike BOFs Beacon Object Files Development"
---

# 96.13 Cobalt Strike BOFs Beacon Object Files Development

## 1. Executive Summary
Beacon Object Files (BOFs) represent a fundamental paradigm shift in how Cobalt Strike executes post-exploitation tasks. Traditionally, Red Teams relied on the noisy "fork and run" pattern, where Beacon would spawn a sacrificial child process (like `rundll32.exe` or `werfault.exe`), inject a capability (e.g., a keylogger or credential dumper) into it, and retrieve the output via named pipes. This pattern is highly visible to modern EDRs. BOFs solve this by allowing compiled C code to execute directly within the memory space of the Beacon process itself, significantly reducing the forensic footprint and avoiding process creation events entirely.

## 2. Core Mechanics of BOFs
A BOF is a compiled C program (an Object file, usually `.o`) that conforms to specific conventions. It is critical to understand that a BOF is *not* a fully linked executable or DLL. When a BOF is executed, the Cobalt Strike Team Server parses the object file, resolves its internal relocations, and sends the raw execution payload to the Beacon.

### The Execution Process:
1. **Compilation:** The operator compiles C code into an object file using a compiler like MinGW (e.g., `x86_64-w64-mingw32-gcc -c bof.c -o bof.o`). No linking stage occurs.
2. **Parsing:** The `inline-execute` command is used in Cobalt Strike. The Team Server parses the `.o` file to extract the text and data segments.
3. **Transmission:** The resolved machine code is sent over the C2 channel.
4. **Execution:** Beacon allocates memory dynamically, copies the code, resolves external API calls, and creates a thread to execute the BOF's entry point (the `go` function).
5. **Cleanup:** Once execution completes, Beacon retrieves the output and gracefully frees the allocated memory.

## 3. Dynamic API Resolution
Because BOFs are not fully linked executables, they cannot rely on standard Import Address Tables (IAT) for calling Windows APIs. Instead, they use Dynamic API Resolution provided natively by the Beacon loader.

### Syntax for API Resolution
Developers must declare the APIs using a specific syntax recognized by the Beacon parser: `LIBRARY$Function`. During execution, Beacon manually uses `LoadLibrary` and `GetProcAddress` to map these functions before execution begins.

```c
// Declaration
DECLSPEC_IMPORT WINBASEAPI HANDLE WINAPI KERNEL32$OpenProcess(DWORD dwDesiredAccess, BOOL bInheritHandle, DWORD dwProcessId);
DECLSPEC_IMPORT WINBASEAPI BOOL WINAPI KERNEL32$CloseHandle(HANDLE hObject);

// Usage inside the BOF
void go(char * args, int alen) {
    HANDLE hProcess = KERNEL32$OpenProcess(PROCESS_ALL_ACCESS, FALSE, 1234);
    if (hProcess) {
        BeaconPrintf(CALLBACK_OUTPUT, "Process handle acquired successfully!");
        KERNEL32$CloseHandle(hProcess);
    }
}
```

## 4. Architecture Diagram: Fork & Run vs. BOF Execution

```text
TRADITIONAL "FORK AND RUN"                 BEACON OBJECT FILE (BOF)
+-------------------------+                +-------------------------+
|      Beacon.exe         |                |      Beacon.exe         |
|                         |                |                         |
|  1. Spawns child        |                |  1. Allocates memory    |
|  2. Injects DLL         |                |  2. Copies BOF to mem   |
|  3. Reads Named Pipe    |                |  3. Executes in-thread  |
+-------------------------+                |  4. Returns output      |
           |                               |  5. Frees memory        |
           v                               +-------------------------+
+-------------------------+                             ^
|    rundll32.exe         |                             |
|    (Sacrificial)        |                             | (No child process)
|  Executes payload       |                             | (No named pipe)
+-------------------------+                             | (No disk I/O)
```

## 5. The Internal Beacon API
Cobalt Strike provides an internal API (defined in `beacon.h`) for BOFs to extract arguments and return output to the operator.
- `BeaconDataParse`: Initializes the argument parsing structure.
- `BeaconDataInt` / `BeaconDataString`: Extracts integers or strings passed from the Aggressor script wrapper.
- `BeaconPrintf`: Sends formatted output back to the Cobalt Strike console.
- `BeaconOutput`: Sends raw binary data or unformatted text back to the console.
- `BeaconUseToken`: Instructs the BOF to adopt the security context of an impersonated token.

## 6. Threat Hunting and Detection Engineering
While BOFs eliminate the noisy "fork and run" process creation events, they are not invisible. They essentially trade process creation anomalies for memory anomalies.

### Detection Strategies:
- **Memory Allocations:** When Beacon executes a BOF, it must allocate memory (often `PAGE_EXECUTE_READWRITE` or `PAGE_EXECUTE_READ`). EDRs utilizing memory scanners can detect these unbacked executable regions.
- **Event Tracing for Windows (ETW):** The `ETWti` (ETW Threat Intelligence) provider can log dynamic API resolutions and cross-process thread creations initiated by the BOF.
- **Call Stack Analysis:** When a BOF calls a Windows API, the return address on the call stack points to unbacked memory (the dynamically allocated memory region for the BOF), rather than a valid DLL on disk. EDRs heavily scrutinize call stacks for these exact anomalies.

### KQL Query: Suspicious In-Memory Execution (Conceptual)
```kusto
DeviceEvents
| where ActionType == "MemoryAllocation" or ActionType == "VirtualAlloc"
| where AllocationProtection in ("PAGE_EXECUTE_READWRITE", "PAGE_EXECUTE_READ")
| where AllocationState == "MEM_COMMIT"
| where isempty(MappedFileName) // Unbacked memory, not pointing to a valid DLL
| project TimeGenerated, DeviceName, ProcessFileName, AllocationSize, AllocationBaseAddress
| order by TimeGenerated desc
```

## 7. Developing a Custom BOF (Complete Example)

```c
#include <windows.h>
#include "beacon.h"

// Define the APIs to use dynamically
DECLSPEC_IMPORT WINBASEAPI DWORD WINAPI KERNEL32$GetCurrentProcessId(void);
DECLSPEC_IMPORT WINBASEAPI DWORD WINAPI KERNEL32$GetCurrentThreadId(void);

// Entry point for the BOF, required to be named 'go'
void go(char * args, int alen) {
    // Parse arguments if necessary (not used in this simple example)
    datap parser;
    BeaconDataParse(&parser, args, alen);
    
    // Execute logic using dynamic APIs
    DWORD pid = KERNEL32$GetCurrentProcessId();
    DWORD tid = KERNEL32$GetCurrentThreadId();
    
    // Return output securely over the C2 channel
    BeaconPrintf(CALLBACK_OUTPUT, "[+] BOF Executed successfully!");
    BeaconPrintf(CALLBACK_OUTPUT, "[+] Current PID: %d | Current TID: %d", pid, tid);
    
    // Memory cleanup is handled by Beacon automatically
}
```

## 8. Real-World Attack Scenario

### The Setup
An attacker has established a foothold on a Windows 11 endpoint running a modern, aggressively tuned EDR. They need to enumerate active network connections and running processes.

### The Execution
If the attacker uses built-in OS commands like `shell netstat -ano` or `execute-assembly`, the EDR will instantly intercept the process creation or the .NET CLR load event and terminate the beacon. Instead, the attacker uses the `Netstat BOF` and `ProcessList BOF` from a public repository like TrustedSec's C2-Tool-Collection.
The operator types `inline-execute netstat.o` in the Cobalt Strike interface.

### The Defender's View
The C code executes entirely within the memory space of `explorer.exe` (where the beacon is currently injected). No new processes are spawned, meaning Sysmon Event ID 1 is silent. However, the EDR's continuous memory scanning module identifies a small region of `PAGE_EXECUTE_READ` memory that is not backed by a signed DLL on disk. A subsequent call stack analysis during an API hook reveals the execution originated from this anomalous memory region. The EDR isolates the machine and flags a "Suspicious Unbacked Memory Execution" alert.

## 9. MITRE ATT&CK Mapping
- **TA0005 Defense Evasion**
- **T1620 Reflective Code Loading:** Loading BOFs entirely in memory.
- **T1106 Native API:** Direct interaction with Windows APIs to avoid command-line logging.
- **T1055 Process Injection:** Executing code within the current process space.

## 10. Defensive Countermeasures
- Ensure EDR solutions are configured to perform aggressive memory scanning and active call stack tracing.
- Monitor for the initial injection techniques commonly used to implant the beacon, as stopping the initial shellcode execution prevents BOF usage entirely.
- Utilize Microsoft Defender for Endpoint (MDE) attack surface reduction (ASR) rules to block credential access from LSASS, which many offensive BOFs target directly via memory reading.

## 11. Chaining Opportunities
- BOFs are heavily integrated into Aggressor Scripts to automate stealthy tasks without triggering process alarms. See [[12 - Aggressor Scripts Automating Red Team Tasks]].
- Red teams often use BOFs to initiate lateral movement APIs natively (e.g., directly calling WMI COM interfaces in C) instead of relying on external tools. See [[14 - Lateral Movement and Pivoting with Cobalt Strike]].

## 12. Related Notes
- [[15 - EDR Evasion with Custom Cobalt Strike Kits]]
- [[Windows APIs for Red Teaming]]
- [[Memory Evasion Techniques]]
- [[ETW Threat Intelligence]]
- [[Detecting Unbacked Memory Executions]]
