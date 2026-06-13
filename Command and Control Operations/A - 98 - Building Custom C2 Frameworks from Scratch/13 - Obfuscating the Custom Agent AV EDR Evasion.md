---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.13 Obfuscating the Custom Agent AV EDR Evasion"
---

# 98.13 Obfuscating the Custom Agent AV EDR Evasion

## The Cat and Mouse Game of Code Obfuscation
While behavioral evasion (like sleep obfuscation) handles the runtime aspect of avoiding detection, static and dynamic code obfuscation is essential for bypassing Antivirus (AV) signatures, pre-execution heuristics, and automated sandbox analysis. When a Blue Team acquires a copy of the custom agent, their first step is to reverse engineer it. Obfuscation delays this process, increasing the "shelf life" of the custom C2 toolset.

This document delves into the educational concepts of API unhooking, direct system calls, control flow flattening, and string obfuscation—techniques employed to make the static binary opaque and its runtime execution clandestine.

## Advanced Obfuscation Concepts

### 1. Direct System Calls (Syscalls)
Traditional Windows applications interact with the OS kernel by calling APIs in `kernel32.dll`, which then call Native APIs (NTAPIs) in `ntdll.dll`. EDRs heavily monitor `ntdll.dll` by injecting their own DLLs into every process and placing inline hooks (JMP instructions) on critical functions like `NtAllocateVirtualMemory` or `NtCreateThreadEx`.
- **Concept:** Direct syscalls bypass `ntdll.dll` entirely by executing the assembly `syscall` instruction directly from the agent's memory, completely avoiding the EDR's userland hooks.
- **Mechanism:** The agent dynamically resolves the Syscall Number (SSN) for the required NTAPI. Techniques like "Hell's Gate" parse the in-memory `ntdll.dll` to find the SSN. If the function is hooked (meaning the SSN is overwritten or moved), techniques like "Halo's Gate" or "Tartarus' Gate" analyze adjacent, unhooked functions to mathematically calculate the target function's SSN.
- **Defensive View:** Defenders counter direct syscalls using kernel-level telemetry (ETW-Ti) or by monitoring for `syscall` instructions originating from outside the `ntdll.dll` memory space (a highly anomalous event).

### 2. API Unhooking (Reflective NTDLL Loading)
Instead of executing direct syscalls (which can be caught by Mark of the Web/ETW-Ti analysis), another approach is to simply remove the EDR's hooks from `ntdll.dll`.
- **Concept:** Overwriting the hooked, in-memory version of `ntdll.dll` with a clean, original copy.
- **Mechanism:** The agent reads the raw `ntdll.dll` file directly from the disk (`C:\Windows\System32\ntdll.dll`), maps it into memory, and copies the `.text` section (containing the executable code and clean system calls) over the modified `.text` section of the currently loaded `ntdll.dll`.
- **Defensive View:** EDRs monitor file access to system DLLs and flag processes that attempt to modify memory protections on module `.text` sections.

### 3. Control Flow Flattening
Reverse engineers use decompilers (like IDA Pro or Ghidra) to understand the logical flow of an agent (if/else statements, loops).
- **Concept:** Control Flow Flattening destroys the logical structure of the program by breaking basic blocks into independent chunks and putting them inside a massive `switch` statement controlled by a state variable.
- **Mechanism:** Implemented at compile-time using tools like O-LLVM (Obfuscator-LLVM). The resulting code executes the same logic but looks like an incomprehensible, flat loop of switch-case statements, vastly increasing the time required for manual analysis.

## ASCII Diagram: API Hooking vs Direct Syscalls

```text
    +-------------------------------------------------------+
    | Normal / Hooked Execution Flow (Caught by EDR)        |
    +-------------------------------------------------------+
    Agent.exe -> kernel32.dll!VirtualAlloc
                      |
                      v
                 ntdll.dll!NtAllocateVirtualMemory
                      |
                      +---> [EDR HOOK: JMP EDR.dll] ---> (Scans memory, alerts Blue Team)
                                      |
                      <---------------+ (If clean, returns execution)
                      |
                      v
                   syscall (Transitions to Kernel)

    +-------------------------------------------------------+
    | Direct Syscall Execution Flow (Bypasses Userland EDR) |
    +-------------------------------------------------------+
    Agent.exe
        |
        |---> Dynamically resolves SSN for NtAllocateVirtualMemory (e.g., 0x18)
        |---> Sets up registers (MOV R10, RCX; MOV EAX, 0x18)
        |
        +---> syscall ---> (Transitions directly to Kernel, completely skipping ntdll.dll)
```

## Educational Implementation: Conceptual Dynamic Syscall Resolution

The following snippet demonstrates the theoretical concept of dynamically extracting a syscall number by parsing the PE headers of `ntdll.dll`. This illustrates how malware developers avoid hardcoding system call numbers, which change between Windows versions.

```cpp
#include <windows.h>
#include <iostream>

// Abstract structure to hold parsed Syscall info
struct SyscallInformation {
    DWORD SyscallNumber;
    PVOID FunctionAddress;
};

// Theoretical function to extract a syscall number by parsing the EAT
bool Concept_ResolveSyscall(const char* functionName, SyscallInformation* outInfo) {
    // 1. Get base address of ntdll.dll (using PEB walk in reality to avoid GetModuleHandle)
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    if (!hNtdll) return false;

    // 2. Parse PE Headers to find the Export Address Table (EAT)
    PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)hNtdll;
    PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)((BYTE*)hNtdll + dosHeader->e_lfanew);
    PIMAGE_EXPORT_DIRECTORY exportDir = (PIMAGE_EXPORT_DIRECTORY)((BYTE*)hNtdll +
        ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress);

    // 3. Iterate through exported names
    DWORD* nameRVA = (DWORD*)((BYTE*)hNtdll + exportDir->AddressOfNames);
    DWORD* funcRVA = (DWORD*)((BYTE*)hNtdll + exportDir->AddressOfFunctions);
    WORD* ordRVA = (WORD*)((BYTE*)hNtdll + exportDir->AddressOfNameOrdinals);

    for (DWORD i = 0; i < exportDir->NumberOfNames; i++) {
        char* currentFuncName = (char*)((BYTE*)hNtdll + nameRVA[i]);

        if (strcmp(currentFuncName, functionName) == 0) {
            // Function found. Get its memory address.
            PVOID funcAddress = (PVOID)((BYTE*)hNtdll + funcRVA[ordRVA[i]]);
            outInfo->FunctionAddress = funcAddress;

            // 4. Extract the Syscall Number
            // In a clean ntdll, the syscall stub looks like:
            // 4C 8B D1   mov r10, rcx
            // B8 XX 00   mov eax, XX (XX is the Syscall Number)
            BYTE* pCode = (BYTE*)funcAddress;
            if (pCode[0] == 0x4C && pCode[1] == 0x8B && pCode[2] == 0xD1 && pCode[3] == 0xB8) {
                // The syscall number is at offset 4
                outInfo->SyscallNumber = *((DWORD*)(pCode + 4));
                return true;
            }
        }
    }
    return false;
}
```

*Note: This code demonstrates parsing for a clean NTDLL. If an EDR has placed a `JMP` instruction at the start of the function (a hook), the bytes `4C 8B D1` will not be present, and this simple approach fails—necessitating advanced techniques like Halo's Gate.*

## Real-World Attack Scenario

### Operation "Phantom Shell"
An advanced persistent threat (APT) targeted a defense contractor utilizing a highly aggressive EDR solution that killed any unknown binary within milliseconds of execution.
1.  **Delivery:** The APT utilized an ISO payload containing a benign binary and an obfuscated malicious DLL.
2.  **Unhooking:** Upon side-loading, the DLL first executed a routine to map a fresh copy of `ntdll.dll` from the disk. It dynamically patched the in-memory, EDR-hooked `ntdll.dll` `.text` section, blinding the EDR to the process's subsequent actions.
3.  **String Encryption:** All internal strings (e.g., C2 domains, API names, registry paths) were encrypted using compile-time string obfuscation macros (e.g., `skCrypter`). The strings were only decrypted in memory microseconds before being used, and zeroed out immediately after, leaving no static indicators.
4.  **Action:** With the EDR blinded and strings encrypted, the agent successfully utilized process hollowing to inject its final C2 beacon into `svchost.exe`, establishing outbound C2 communication without triggering behavioral or static alerts.

## Chaining Opportunities

- **Obfuscation + Sleep:** Combine compile-time **Control Flow Flattening** with runtime **Sleep Obfuscation**. Even if the Blue Team dumps the memory while the agent is executing (awake), the flattened control flow makes analyzing the dumped shellcode incredibly tedious.
- **Syscalls + BOFs:** Utilize **Direct Syscalls** not just in the core agent, but within dynamically loaded Beacon Object Files (BOFs) executed in-memory. This ensures that even modular payloads fetched post-exploitation remain stealthy.
- **Environmental Keying:** Use the decrypted strings (like the target domain) as a key to decrypt the next stage of the payload. If run in a sandbox, the domain won't match, and the payload decrypts into garbage bytes.

## Related Notes

- [[11 - Implementing Evasion Techniques directly in the Agent]]
- [[19 - Understanding and Bypassing Kernel Callbacks]]
- [[24 - Compile-Time Obfuscation with LLVM]]
- [[31 - Developing Custom Beacon Object Files BOFs]]
- [[08 - Advanced Sandbox Evasion Techniques]]
