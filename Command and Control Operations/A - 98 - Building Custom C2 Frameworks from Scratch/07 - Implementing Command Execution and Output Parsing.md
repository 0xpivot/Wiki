---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.07 Implementing Command Execution and Output Parsing"
---

# Implementing Command Execution and Output Parsing

## 1. Introduction to Command Execution Execution
A C2 agent's primary directive—after establishing persistence and communication—is to execute commands on the victim machine and retrieve the results. This capability requires a deep understanding of Operating System execution APIs, Inter-Process Communication (IPC), and proper data serialization. From a threat hunting and defensive perspective, monitoring how processes are spawned and how data flows between them is one of the highest-fidelity mechanisms for detecting malicious activity.

## 2. Windows OS Execution Internals
When an agent needs to execute a command (e.g., running `whoami /all` or spawning PowerShell), it relies on OS-level APIs.

### Standard Execution: CreateProcess
The fundamental Windows API for execution is `CreateProcessA` or `CreateProcessW`. This API requires the agent to define a `STARTUPINFO` and `PROCESS_INFORMATION` structure. 
While straightforward, calling `CreateProcess` directly to spawn `cmd.exe` or `powershell.exe` is heavily monitored. EDR solutions hook `CreateProcess` in user-land (via `ntdll.dll`'s `NtCreateUserProcess`) and monitor kernel-level process creation via ETW (Event Tracing for Windows) and kernel callbacks (`PsSetCreateProcessNotifyRoutine`).

### Alternative Execution APIs
To evade basic monitoring, agents might utilize alternative APIs:
*   **ShellExecute / ShellExecuteEx:** Higher-level APIs that can execute files based on file extension associations.
*   **WinExec:** A legacy, older API that wraps around `CreateProcess`. While mostly deprecated, it is sometimes used to bypass poorly written EDR hooks that only target modern APIs.
*   **WMI (Windows Management Instrumentation):** Using COM objects to instantiate the `Win32_Process` class to create processes remotely or locally, often evading parent-child relationship detection.

## 3. Capturing Output via Anonymous Pipes
Executing a command is only half the battle; the C2 server needs the output (Standard Output `stdout` and Standard Error `stderr`). In a standard console application, this output prints to the screen. For a hidden, background C2 agent, this data must be intercepted.

### The CreatePipe Paradigm
The standard method to capture output involves Anonymous Pipes. The flow is as follows:
1.  **Create Pipes:** The agent calls `CreatePipe` twice: once for the output pipe and once for the input pipe. This yields Read and Write handles.
2.  **Inheritance:** The agent modifies the `STARTUPINFO` structure, setting the `hStdOutput` and `hStdError` to the Write handle of the pipe. The `dwFlags` must include `STARTF_USESTDHANDLES`.
3.  **Process Creation:** `CreateProcess` is called with the modified `STARTUPINFO`. The child process (e.g., `cmd.exe`) writes its output into the pipe instead of a console window.
4.  **Reading Output:** The agent enters a loop, using `ReadFile` on the Read handle of the pipe, buffering the output until the process terminates.

### Defensive Considerations: Anomalous Pipes
Threat hunters actively monitor pipe creation. A hidden, unsigned binary creating anonymous pipes and immediately spawning `cmd.exe` is a high-confidence indicator of a reverse shell or command execution module. Sysmon Event ID 1 (Process Creation) logs the command line, while Event ID 17/18 can log named pipe events (though anonymous pipes are harder to track purely via Event Logs, memory analysis tools detect them).

## 4. Output Parsing and Serialization
Once raw bytes are read from the pipe, the agent must structure them before transmission to avoid network layer corruption and to allow the C2 server to parse the response properly.

### Structuring the Data
Agents typically wrap the raw output in a structured format (JSON, XML, or custom binary structs). A common JSON structure might look like:
```json
{
  "agent_id": "8f9a2b1c",
  "task_id": "task-9921",
  "status": "success",
  "output_length": 1024,
  "output": "Base64EncodedStringOfOutput"
}
```

### Encryption and Evasion
Before serialization, advanced agents will compress the output (e.g., zlib or gzip) to reduce network footprint, and encrypt it (e.g., AES-256-GCM) with a session key established during the initial beaconing phase. Base64 encoding the encrypted blob ensures HTTP-safe transmission. 

## 5. ASCII Architecture Diagram

```ascii
+-----------------------+                       +-----------------------+
|   C2 Agent Process    |                       |   Child Process       |
|                       |                       |   (e.g., cmd.exe)     |
| 1. CreatePipe()       |                       |                       |
|    [Read Handle]      |<------ Data Flow -----| [Standard Output]     |
|    [Write Handle] ----|------- Inherited ---->|                       |
|                       |                       |                       |
| 2. CreateProcess() ---|------- Spawns ------->|                       |
|                       |                       |                       |
| 3. ReadFile() Loop    |                       |                       |
|    reads [Read Handle]|                       |                       |
|                       |                       |                       |
| 4. Serialize & Encrypt|                       |                       |
|    |                  |                       |                       |
+----|------------------+                       +-----------------------+
     |
     v
[ Encrypted Network Transfer ]
```

## 6. Token Manipulation and Context Execution
Execution isn't always straight forward. Agents often need to execute commands in the context of other users. This requires interacting with Access Tokens.
*   **Impersonation:** The agent uses APIs like `LogonUser`, `DuplicateTokenEx`, and `ImpersonateLoggedOnUser` to temporarily adopt the privileges of another user.
*   **CreateProcessWithTokenW:** To spawn a new process under the stolen token context, the agent must use this specialized API. From a threat hunting perspective, tracking `SeDebugPrivilege` and anomalous token duplication events (Security Event 4624/4672) is critical to spotting privilege escalation and lateral movement via command execution.

## 7. Telemetry and Threat Hunting Strategies

### Sysmon Event ID 1 (Process Creation)
Defenders baseline normal parent-child relationships. `svchost.exe` spawning `cmd.exe` or a recently downloaded `update.exe` spawning `powershell.exe -NoP -Enc...` are classic C2 execution anomalies. 

### ETW (Event Tracing for Windows)
Modern EDRs utilize the `Microsoft-Windows-Kernel-Process` ETW provider. This provider gives kernel-level visibility into process creations, making it difficult for user-land API unhooking to mask the execution. If an agent unhooks `CreateProcessW` in `ntdll.dll`, the ETW kernel trace will still fire, alerting the SOC.

### Advanced Memory Forensics
During incident response, memory dumps are parsed (e.g., using Volatility) to find orphaned processes or to inspect the VAD (Virtual Address Descriptor) of running processes for injected code that might be acting as a silent command execution engine without a standard parent file.

## Real-World Attack Scenario
An attacker establishes a foothold using a custom C++ implant. The SOC is monitoring for standard `cmd.exe` or `powershell.exe` execution. Knowing this, the implant utilizes a technique called "Bring Your Own Interpreter" (BYOI) or "Living Off The Land". Instead of calling `cmd.exe`, the agent reflects a lightweight Lua or Python interpreter directly into its own memory space. When the C2 server issues a command, the agent executes it natively within the loaded interpreter, entirely bypassing `CreateProcess` and avoiding Sysmon Event ID 1. The output is captured in-memory, serialized via JSON, and beaconed out. Defenders eventually catch the intrusion not by process creation, but by analyzing the anomalous network beaconing cadence and identifying the embedded Lua runtime via YARA scanning the agent's memory space.

## Chaining Opportunities
*   Command execution can be decoupled from the main agent loop using asynchronous threads, which prevents the agent from freezing if a command hangs.
*   Instead of standard API execution, agents can chain command execution with API unhooking to bypass EDR interception.

## Related Notes
*   [[06 - Developing the Agent C C++ Golang]]
*   [[10 - Asynchronous Execution and Background Jobs]]
*   [[15 - Parent Process ID (PPID) Spoofing]]
*   [[16 - Process Hollowing and Injection Techniques]]
*   [[12 - Advanced Memory Evasion and API Unhooking]]
