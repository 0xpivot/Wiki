---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.08 Evasion Techniques in Sliver Process Hollowing BlockDLLs"
---

# 95.08 Evasion Techniques in Sliver Process Hollowing BlockDLLs

## Introduction to Evasion in Sliver

Modern Endpoint Detection and Response (EDR) agents rely heavily on telemetry from process creation, thread injection, API hooking, and DLL loading to detect malicious activity. When a Sliver implant needs to perform post-exploitation activities—such as executing an arbitrary executable, injecting shellcode, or running an interactive shell—it must do so securely to avoid detection.

Sliver provides advanced opsec primitives built directly into its post-exploitation commands. Two of the most critical evasion techniques supported natively are **Process Hollowing** (and related injection methods) and **BlockDLLs** (Arbitrary Code Guard / ACG). Understanding and correctly configuring these features is paramount for maintaining persistence in a mature environment.

## Execution and Injection Architecture

Below is an ASCII representation of how Sliver combines PPID Spoofing, Process Hollowing, and BlockDLLs to achieve stealthy execution.

```text
    [ Sliver Implant (Session 1) ]
                  |
                  | 1. Operator requests execution (e.g., 'execute-assembly')
                  |    with arguments: --ppid 1044 --block-dlls
                  v
+-------------------------------------------------------+
|                Sliver Execution Engine                |
|                                                       |
|  [a] Update Thread Attributes                         |
|      -> Set Parent Process ID (PPID) to 1044          |
|      -> Set Mitigation Policy:                        |
|         PROCESS_CREATION_MITIGATION_POLICY_           |
|         BLOCK_NON_MICROSOFT_BINARIES_ALWAYS_ON        |
|                                                       |
|  [b] CreateProcess( "notepad.exe", CREATE_SUSPENDED ) |
+-------------------------------------------------------+
                  |
                  | 2. Spawns suspended process spoofing PPID
                  v
    [ Suspended 'notepad.exe' Process ]
     - Parent is Process 1044 (explorer.exe)
     - BlockDLLs restricts unsigned/EDR DLLs
                  |
                  | 3. Sliver performs Process Hollowing / Injection
                  v
+-------------------------------------------------------+
|              Memory Manipulation                      |
|                                                       |
|  [c] NtUnmapViewOfSection (Unmap original code)       |
|  [d] VirtualAllocEx (Allocate RWX / RX memory)        |
|  [e] WriteProcessMemory (Write Malicious Payload)     |
|  [f] SetThreadContext (Point EIP/RIP to Payload)      |
|  [g] ResumeThread (Start Execution)                   |
+-------------------------------------------------------+
                  |
                  | 4. Malicious code runs undetected
                  v
       [ Code Execution in 'notepad.exe' ]
```

## Core Evasion Mechanisms

### 1. Parent Process ID (PPID) Spoofing
By default, when an implant spawns a new process (like `cmd.exe` or an injection target), the new process is a child of the implant. If the implant is running as an unusual process (e.g., `update.exe` in a Temp folder), seeing it spawn `notepad.exe` is highly suspicious to EDRs.

PPID Spoofing uses `UpdateProcThreadAttribute` during process creation to manipulate the `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` flag. This tricks the operating system into thinking a different, legitimate process (like `explorer.exe` or `svchost.exe`) spawned the new process.

**Sliver Usage:**
```bash
# Execute a command in a new process, spoofing PPID to process 1337
sliver (IMPLANT) > execute -p 1337 -c "whoami"
```

### 2. BlockDLLs (Arbitrary Code Guard)
EDR products often inject their own user-land DLLs into newly created processes to hook Windows APIs (e.g., `NtCreateProcess`, `NtAllocateVirtualMemory`). If an EDR DLL is loaded into your sacrificial process, it will monitor your process hollowing and memory injection activities.

To counter this, Microsoft introduced a process mitigation policy to block non-Microsoft signed DLLs from loading. By applying this policy to our sacrificial process during creation, the OS kernel will actively block the EDR from injecting its user-land DLLs into the process.

**Sliver Usage:**
```bash
# Execute a .NET assembly, spoofing PPID, and blocking non-Microsoft DLLs
sliver (IMPLANT) > execute-assembly --ppid 2048 --block-dlls /path/to/Rubeus.exe
```

### 3. Process Hollowing
Process hollowing involves creating a legitimate process in a suspended state, unmapping (hollowing out) its original executable code, injecting malicious code, and resuming the thread. Because the process is backed by a legitimate binary on disk, it evades simple task-manager and process-list inspections.

In Sliver, many commands that execute code (like `execute-assembly`, `spawndll`, `shellcode`) will default to spawning a sacrificial process (often `notepad.exe`) and injecting into it.

**Configuring Sacrificial Processes:**
Operators can configure which process Sliver hollows out. This should be tailored to the environment to blend in.
```bash
# View current injection process
sliver (IMPLANT) > getpid
# Change the default hosting process for post-exploitation jobs
sliver (IMPLANT) > set-hosting-process C:\Windows\System32\svchost.exe
```

## Combining Evasion Strategies for Maximum Stealth

Running tools like `Mimikatz` or `Rubeus` is highly signatured. To execute them safely in Sliver, operators must layer these OPSEC features.

1. Find a suitable parent process (e.g., `explorer.exe` or `spoolsv.exe`) using the `ps` command.
2. Select an inconspicuous sacrificial process (e.g., `werfault.exe` or `dllhost.exe`).
3. Execute the payload specifying the PPID, enabling BlockDLLs, and applying AMSI/ETW bypasses.

```bash
sliver (IMPLANT) > execute-assembly -p 4512 -E -A --block-dlls /opt/tools/Seatbelt.exe
```
*Flags Breakdown:*
- `-p 4512`: Spoof PPID to 4512.
- `-E`: Bypass ETW in the new process.
- `-A`: Bypass AMSI in the new process.
- `--block-dlls`: Prevent EDR user-land hooks.

## Real-World Attack Scenario

### Bypassing CrowdStrike Falcon Hooking
The Red Team has established a foothold on a Windows 11 workstation protected by CrowdStrike Falcon. The operator attempts to run a standard memory injection, but the EDR immediately terminates the process because Falcon's user-land DLL hooks the `NtWriteVirtualMemory` API.

**The Solution:**
1. The operator uses `ps` to identify the PID of `explorer.exe` (PID: 3392).
2. The operator prepares to dump credentials using a custom memory dumper assembly.
3. The operator runs the execution command using BlockDLLs and PPID spoofing.
   `execute-assembly -p 3392 --block-dlls /opt/tools/MemDumper.exe`
4. The OS creates a suspended child process under `explorer.exe`.
5. Because of the `--block-dlls` flag, the OS refuses to load `cybkernel.dll` (CrowdStrike's hook DLL) into the new process.
6. The new process runs entirely unhooked in user-land.
7. Sliver seamlessly injects the `MemDumper.exe` assembly into this clean, unmonitored process.
8. The credentials are dumped successfully, and the process terminates gracefully.

## Chaining Opportunities

- **Shellcode Loaders:** Implement BlockDLLs and PPID spoofing in your initial loaders before staging the Sliver shellcode (refer to [[06 - Sliver Stagers and Shellcode Execution]]).
- **BOF Integration:** Use Beacon Object Files to modify process mitigation policies dynamically, or to perform unhooking if BlockDLLs is not feasible on older OS versions (see [[10 - Integrating BOFs Beacon Object Files in Sliver]]).
- **Lateral Movement:** Spoof PPIDs to trusted system processes before spawning instances of `PsExec` or `WMI` to obscure lateral movement chains.

## Related Notes

- [[06 - Sliver Stagers and Shellcode Execution]]
- [[07 - Sliver Armory Installing Custom Extensions]]
- [[09 - Sliver Lateral Movement PsExec WMI]]
- [[10 - Integrating BOFs Beacon Object Files in Sliver]]
- [[13 - Advanced EDR Evasion and API Unhooking]]
