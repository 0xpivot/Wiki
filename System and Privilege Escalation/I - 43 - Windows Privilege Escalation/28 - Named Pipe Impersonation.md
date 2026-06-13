---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.28 Named Pipe Impersonation"
---

# 28 - Named Pipe Impersonation

## Executive Summary

Named Pipe Impersonation represents a classic, highly reliable, and profoundly effective Windows privilege escalation technique. It leverages a legitimate, built-in Windows inter-process communication (IPC) mechanism where a server process is permitted to temporarily assume the security context of a connecting client. If an attacker can successfully coerce or trick a highly privileged process—such as a service running as `NT AUTHORITY\SYSTEM` or a Domain Administrator's process—into authenticating to a named pipe they control, the attacker can "impersonate" that connecting client. This effectively grants the attacker the ability to execute arbitrary code utilizing the absolute privileges of the victim process.

This technique is the foundational mechanism behind the infamous "Potato" family of exploits (RottenPotato, JuicyPotato, PrintSpoofer, RogueWinRM, etc.), which are standard post-exploitation tools deployed following initial web application compromise.

## Theoretical Foundation

**Named Pipes:**
A named pipe is a heavily utilized IPC mechanism within the Windows architecture that allows diverse processes to communicate securely, both locally and across network boundaries. They operate analogously to a shared memory segment with a specific, resolvable name format (e.g., `\\.\pipe\PipeName`). 

**The Impersonation Paradigm:**
To facilitate secure communication and authorization checks, Windows provides a specific API function for named pipe servers: `ImpersonateNamedPipeClient()`. When a client connects and writes to or reads from the pipe, the server application can invoke this function to temporarily adopt the client's access token. The architectural intent is to allow the server to securely access remote resources on behalf of the client, ensuring the client intrinsically possesses the necessary permissions without the server needing to maintain a database of credentials.

**The Attack Vector:**
1. **Creation:** The attacker instantiates a malicious named pipe server.
2. **Coercion (The "Lure"):** The attacker utilizes various remote procedure calls (RPCs) or protocol weaknesses to force a highly privileged system process into connecting to their malicious named pipe.
3. **Impersonation:** Immediately upon connection, the attacker's server script invokes `ImpersonateNamedPipeClient()`.
4. **Execution:** The attacker's executing thread now temporarily holds the privileged token. It duplicates this token and spawns a new process (e.g., `cmd.exe`), granting the attacker a persistent, highly privileged shell.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|               Named Pipe Impersonation Execution Flow              |
|                                                                    |
|  +-----------------------+           +--------------------------+  |
|  |   Target Service      |           |   Attacker Process       |  |
|  | (NT AUTHORITY\SYSTEM) |           | (Low Priv / IIS AppPool) |  |
|  +-----------+-----------+           +-------------+------------+  |
|              |                                     |               |
|              |         (1) CreatePipe()            |               |
|              |   <---------------------------------+               |
|              |                                                     |
|              |         (2) Trigger RPC Coercion                    |
|              |   <---------------------------------+               |
|              |                                                     |
|              |         (3) ConnectNamedPipe()                      |
|              +-----------------------------------> |               |
|                                                    |               |
|                    (4) ImpersonateNamedPipeClient()|               |
|                    (5) DuplicateTokenEx()          |               |
|                    (6) CreateProcessAsUser()       |               |
|                                                    v               |
|                                      +-------------+------------+  |
|                                      | Elevated cmd.exe shell   |  |
|                                      | (NT AUTHORITY\SYSTEM)    |  |
|                                      +--------------------------+  |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To execute this attack effectively, the attacker must satisfy the following strict requirements:

1. **Required Privileges:** The compromised account must possess either `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`. These privileges are typically held by the local `Administrators` group, and crucially, by local `SERVICE` accounts (such as IIS AppPools, Network Service, and Local Service).
2. **Coercion Vector:** A viable method to coerce a privileged process to authenticate to the attacker's pipe. The availability of this vector depends heavily on the OS version and patch level.

You can verify if your currently compromised account holds the necessary privilege using the standard `whoami` utility:

```cmd
whoami /priv | findstr "SeImpersonatePrivilege"

# Example Output
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
```
*(Note: If the state is 'Disabled', exploit tools will programmatically enable it prior to execution.)*

## Detailed Exploitation Walkthrough

### Scenario: The PrintSpoofer Exploit

The PrintSpoofer technique represents a highly reliable evolution in this attack class, operating effectively on modern Windows versions (Windows 10 / Server 2016 and above) and abandoning the complex DCOM object instantiations required by older iterations like JuicyPotato.

**Step 1: Understanding the Print Spooler Coercion**

The PrintSpoofer exploit abuses the ubiquitous Windows Print Spooler service (`spoolsv.exe`), which inherently executes as `NT AUTHORITY\SYSTEM`. The Spooler service exposes an RPC interface (MS-RPRN). The exploit explicitly targets the `RpcRemoteFindFirstPrinterChangeNotificationEx()` function. 

Crucially, this function allows an arbitrary client to specify a notification target (a named pipe) where the Spooler should deliver status updates. The Spooler service will dutifully attempt to connect to this target pipe.

**Step 2: Execution Mechanics**

1. The attacker transfers the `PrintSpoofer.exe` binary to the target system.
2. The tool creates a listening malicious named pipe, e.g., `\\.\pipe\test\pipe\spoolss`.
3. The tool connects to the local Print Spooler service via the MS-RPRN RPC interface.
4. It calls `RpcRemoteFindFirstPrinterChangeNotificationEx()` and instructs the Spooler to direct notifications to the attacker's custom pipe.
5. The Spooler service (executing as SYSTEM) obliges and connects to the attacker's named pipe.
6. `PrintSpoofer.exe` intercepts the connection, invokes `ImpersonateNamedPipeClient()`, and captures the SYSTEM token.
7. It duplicates the token and spawns a new interactive process utilizing the stolen token.

**Step 3: Practical Command Execution**

Assume the attacker has secured a reverse shell as an IIS web user (`iis apppool\defaultapppool`), which natively possesses `SeImpersonatePrivilege`:

```cmd
C:\temp> whoami
iis apppool\defaultapppool

# Execute PrintSpoofer64.exe (-i for interactive, -c for command)
C:\temp> PrintSpoofer64.exe -i -c cmd.exe
[+] Found privilege: SeImpersonatePrivilege
[+] Named pipe listening...
[+] CreateProcessAsUser() OK
Microsoft Windows [Version 10.0.19042.1288]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\system32> whoami
nt authority\system
```

## Advanced Techniques & Bypasses

1. **Rogue WinRM / SweetPotato:** As Microsoft patches specific coercion vectors (like the Print Spooler), new variants emerge. Rogue WinRM targets the Background Intelligent Transfer Service (BITS), forcing it to connect to a local WinRM listener controlled by the attacker via a custom COM object instantiation.
2. **EfsPotato (PetitPotam):** This variant targets the Encrypting File System (EFS) RPC interface (`MS-EFSR`) to achieve identical coercion results.
3. **Token Duplication intricacies:** After `ImpersonateNamedPipeClient()` succeeds, the attacker's thread temporarily holds the token (an Impersonation Token). To spawn a completely new, independent process (like a stable reverse shell), this token must be duplicated into a Primary Token utilizing the `DuplicateTokenEx` API, and subsequently applied using `CreateProcessAsUser` or `CreateProcessWithTokenW`.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs:**
   - `Event ID 4688` (A new process has been created): This is paramount. Alert on the sudden creation of `cmd.exe` or `powershell.exe` where the parent process is an IIS AppPool or SQL Server process, especially if the new process executes as SYSTEM.
   - `Event ID 4624` (Successful Logon): Look for Logon Type 3 (Network) connections occurring locally (`127.0.0.1` to `127.0.0.1`) corresponding to anomalous named pipe activity.
   - `Event ID 5145` (A network share object was checked to see whether client can be granted desired access): Monitor for connections to highly unusual or randomly generated named pipe strings (e.g., `\pipe\test\pipe\spoolss`).

2. **Sysmon / EDR:**
   - `Event ID 17/18` (Pipe Created / Pipe Connected): Configure Sysmon to meticulously monitor named pipe creation. Alert aggressively on pipe names commonly associated with known exploit frameworks, or anomalous pipe connections originating from core system services like `spoolsv.exe` directed towards non-standard user-space pipes.

### Mitigation Strategies

1. **Disable Unnecessary Services:** If a server does not explicitly require printing capabilities, fundamentally disable the Print Spooler service. This immediately neutralizes the PrintSpoofer attack vector.
2. **Strict Principle of Least Privilege:** Audit service accounts rigorously. While IIS requires `SeImpersonatePrivilege` by default to function properly, ensure custom application services do not possess this privilege unless strictly architecturally mandated.
3. **Network Isolation:** Utilize Host-based Firewalls to restrict localhost RPC communications unless absolutely required by specific enterprise applications.

## Chaining Opportunities

- **Web Application Exploitation:** Named Pipe Impersonation is the de-facto, industry-standard privilege escalation route utilized immediately following the exploitation of a web application (e.g., an unpatched Microsoft Exchange server, a vulnerable IIS application, or a Tomcat server) to escalate from a service account to complete system control.
- **Lateral Movement Preparation:** Once `NT AUTHORITY\SYSTEM` is achieved, the attacker holds absolute control over the host. They can proceed to extract credentials from memory (LSASS dumping) or registry hives to facilitate rapid lateral movement across the Active Directory domain.

## Related Notes
- [[25 - Abusing SeBackupPrivilege SeRestorePrivilege]]
- [[29 - COM Object Hijacking]]
- [[31 - Credential Dumping]]
