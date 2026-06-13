---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.14 Adding Lateral Movement Modules to Custom C2"
---

# 98.14 Adding Lateral Movement Modules to Custom C2

## Expanding the Foothold
Initial access is only the first step in a Red Team engagement. To achieve the engagement's objectives (e.g., accessing the domain controller or sensitive database servers), the C2 framework must facilitate Lateral Movement. This is the process of moving from the initially compromised host to adjacent systems within the network.

Modern networks are highly segmented. A compromised workstation might not have direct internet access to communicate with the external Teamserver. Therefore, custom C2 frameworks must implement Peer-to-Peer (P2P) communication architectures, allowing agents to chain together and route traffic through a mesh network using internal protocols.

## Core Lateral Movement and P2P Concepts

### 1. SMB Named Pipes (P2P Communication)
Server Message Block (SMB) is ubiquitous in Windows environments (Port 445). Named Pipes provide a mechanism for inter-process communication (IPC).
- **Concept:** A C2 agent on Host A (the parent) creates a Named Pipe listener. A newly executed agent on Host B (the child) connects to this pipe over the network.
- **Mechanism:** Host B encapsulates its C2 traffic (check-ins, task results) and writes it into the Named Pipe. Host A reads this data and forwards it out to the Teamserver (or to another parent in the chain).
- **Defensive View:** Defenders monitor for anomalous Named Pipe creations (e.g., dynamically generated or hardcoded malicious pipe names) and unexpected SMB traffic between workstations (workstation-to-workstation SMB is often a red flag, whereas workstation-to-server is normal).

### 2. Windows Management Instrumentation (WMI)
WMI is a powerful administrative framework in Windows used for querying system information and executing tasks.
- **Concept:** Using WMI to remotely execute the C2 agent binary or shellcode on a target machine.
- **Mechanism:** The agent utilizes COM interfaces (e.g., `IWbemServices`) to connect to the remote host and create a new `Win32_Process`. This avoids dropping typical artifacts like Windows Services.
- **Defensive View:** EDRs heavily monitor WMI activity, specifically the `Win32_Process::Create` method, and correlate it with process parent-child relationships (e.g., `WmiPrvSE.exe` spawning an anomalous executable).

### 3. Distributed Component Object Model (DCOM)
DCOM extends the Component Object Model to allow applications to interact across a network.
- **Concept:** Instantiating specific COM objects (like `MMC20.Application` or `ShellWindows`) on a remote machine and invoking their methods to execute code.
- **Mechanism:** The agent authenticates to the remote host and uses APIs like `CoCreateInstanceEx` to instantiate the object, then calls methods like `ExecuteShellCommand`.
- **Defensive View:** Network telemetry can detect anomalous RPC/DCOM traffic. Host-based defenses monitor the registry for unauthorized COM object modifications and anomalous processes spawned by `svchost.exe` hosting DCOM services.

## Architectural ASCII Diagram: P2P Named Pipe Mesh

```text
    +------------------+          +------------------+
    |   Teamserver     |          |  External HTTPS  |
    |  (C2 Infrastructure| <======> |  (Port 443)      |
    +------------------+          +------------------+
                                           ^
                                           | HTTP/HTTPS
                                           v
    +-------------------------------------------------------+
    | COMPROMISED WORKSTATION A (Egress Node)               |
    | IP: 10.0.1.5                                          |
    | Status: Has Internet Access                           |
    |                                                       |
    | [Agent A] --> Communicates directly with Teamserver   |
    |     |                                                 |
    |     +--> Starts SMB Named Pipe Listener               |
    |          (\\. \pipe\mojo_54321)                       |
    +-------------------------------------------------------+
               ^
               | SMB (Port 445)
               v
    +-------------------------------------------------------+
    | COMPROMISED SERVER B (Internal Node)                  |
    | IP: 10.0.2.10                                         |
    | Status: NO Internet Access                            |
    |                                                       |
    | [Agent B] --> Connects to \\10.0.1.5\pipe\mojo_54321  |
    |     |                                                 |
    |     +--> Starts SMB Named Pipe Listener               |
    |          (\\. \pipe\mojo_98765)                       |
    +-------------------------------------------------------+
               ^
               | SMB (Port 445)
               v
    +-------------------------------------------------------+
    | COMPROMISED DATABASE C (Deep Internal Node)           |
    | IP: 10.0.3.50                                         |
    | Status: Isolated Segment                              |
    |                                                       |
    | [Agent C] --> Connects to \\10.0.2.10\pipe\mojo_98765 |
    +-------------------------------------------------------+
```

## Educational Implementation: Conceptual Named Pipe Server

This abstract C++ snippet demonstrates how a C2 agent sets up an SMB Named Pipe listener to receive connections from lateral agents.

```cpp
#include <windows.h>
#include <iostream>

// Abstract conceptual function to host a P2P Named Pipe
void Concept_StartNamedPipeListener(const char* pipeName) {
    // 1. Format the pipe name correctly for the local system
    char fullPipeName[256];
    snprintf(fullPipeName, sizeof(fullPipeName), "\\\\.\\pipe\\%s", pipeName);

    // 2. Create the Named Pipe with specific permissions
    // PIPE_ACCESS_DUPLEX: Bidirectional communication
    // FILE_FLAG_OVERLAPPED: Asynchronous I/O (essential so the agent doesn't block)
    HANDLE hPipe = CreateNamedPipeA(
        fullPipeName,
        PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED,
        PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
        PIPE_UNLIMITED_INSTANCES,
        4096, // Out buffer size
        4096, // In buffer size
        0,    // Default timeout
        NULL  // Security attributes (requires careful configuration in a real agent)
    );

    if (hPipe == INVALID_HANDLE_VALUE) {
        return; // Failed to create pipe
    }

    std::cout << "[+] Listening on " << fullPipeName << std::endl;

    // 3. Wait for a child agent to connect laterally
    OVERLAPPED overlapped = { 0 };
    overlapped.hEvent = CreateEvent(NULL, TRUE, FALSE, NULL);

    BOOL connected = ConnectNamedPipe(hPipe, &overlapped);
    if (!connected && GetLastError() == ERROR_IO_PENDING) {
        // Wait for the connection asynchronously
        WaitForSingleObject(overlapped.hEvent, INFINITE);
    }

    std::cout << "[+] Child agent connected via SMB!" << std::endl;

    // 4. Read data from the child agent (e.g., its registration info or task output)
    char buffer[4096];
    DWORD bytesRead;
    if (ReadFile(hPipe, buffer, sizeof(buffer), &bytesRead, NULL)) {
        // Process the data, encrypt it, and forward it to the Teamserver
        // ForwardToTeamServer(buffer, bytesRead);
    }

    CloseHandle(hPipe);
    CloseHandle(overlapped.hEvent);
}
```

## Real-World Attack Scenario

### Operation "Silent Bridge"
A Red Team compromised a receptionist's workstation at a manufacturing facility. The objective was the Engineering file share, located on an isolated VLAN with no internet routing.
1.  **Initial Egress:** The primary agent (Agent A) on the receptionist's PC beaconed out via HTTPS to the Teamserver.
2.  **Reconnaissance & Staging:** Operator queried Active Directory and identified the target file server. They tasked Agent A to start an SMB Named Pipe listener named `\pipe\spoolss` (mimicking the legitimate Print Spooler service pipe).
3.  **Lateral Movement (WMI):** Using captured credentials, the operator instructed Agent A to use WMI to execute a secondary, diskless payload on the file server (Host B).
4.  **P2P Link:** The payload on Host B executed entirely in memory and connected back to Agent A over Port 445 using the `spoolss` named pipe.
5.  **Exfiltration:** Agent B compressed the sensitive CAD files and streamed them through the Named Pipe to Agent A. Agent A then multiplexed this data into its HTTPS beacon traffic and exfiltrated it to the Teamserver. The isolated file server was successfully compromised without triggering network boundary alarms.

## Chaining Opportunities

- **Named Pipes + Process Injection:** Instead of spawning a new process for lateral movement, inject the P2P listener code into a legitimate, persistent service (like `spoolsv.exe`) to hide the named pipe creation within expected administrative behavior.
- **WMI + Token Impersonation:** Combine WMI lateral movement with **Token Manipulation**. Steal the access token of a logged-in Domain Admin on the initial host, impersonate it, and then execute the WMI lateral movement payload to bypass restricted access controls.
- **Pass-the-Hash (PtH) + DCOM:** Utilize harvested NTLM hashes to authenticate via DCOM, completely bypassing the need for plaintext passwords during lateral spread.

## Related Notes

- [[12 - Developing a Web Interface for the C2 React Vue]]
- [[26 - Deep Dive into Token Impersonation and Manipulation]]
- [[30 - Active Directory Reconnaissance and BloodHound Integration]]
- [[33 - Implementing Custom RPC Communications]]
- [[09 - OPSEC Safe Lateral Movement Strategies]]
