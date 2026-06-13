---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 35"
---

# Broken Function Level Authorization (Privilege Escalation & Tokens)

Function-level authorization refers to the controls that dictate which users or processes can execute highly privileged operations at the operating system or kernel level. When these controls fail, attackers can escalate from standard user contexts to SYSTEM or root-level authority. This module delves into Windows Access Tokens, kernel privileges, Named Pipe impersonation, and Linux SUID mechanisms, exploring how broken function-level restrictions lead to total host compromise.

## Formal Technical Questions

### Q1: Explain how Windows Access Tokens and Privileges (e.g., `SeDebugPrivilege`, `SeImpersonatePrivilege`) act as function-level authorization, and how their abuse leads to SYSTEM access.
In the Windows OS, function-level authorization is governed by Access Tokens. When a user authenticates, the Local Security Authority (LSA) creates an Access Token. This token contains the user's SID, group SIDs, Integrity Level, and a list of specific rights known as NT Privileges. Every time a process attempts an action, the OS kernel checks the token's privileges to authorize the function.

- **SeDebugPrivilege:** Authorizes a process to debug and access the memory of *any* other process, bypassing the standard Discretionary Access Control List (DACL) of the target process. If an attacker gains this privilege, they can bypass function-level restrictions, call `OpenProcess` with `PROCESS_VM_READ` on `lsass.exe`, and extract plaintext passwords or Kerberos tickets from memory.
- **SeImpersonatePrivilege:** Authorizes a process to impersonate the security context of a client that connects to it. Attackers abuse this by coercing a SYSTEM process to connect to an attacker-controlled service (like a Named Pipe), capturing the SYSTEM token, and calling `DuplicateTokenEx` to spawn a new thread acting with SYSTEM authority, entirely bypassing the function-level isolation.

### Q2: Detail the exploitation of Linux SUID (Set Owner User ID) binaries. Why does this represent a failure in function-level authorization?
In Linux, the function-level authorization model relies on the Effective User ID (EUID). Normally, a process executes with the EUID of the user who launched it. The SUID bit is a special permission on an executable file that overrides this behavior: when executed, the process assumes the EUID of the file's owner (often `root`), regardless of who executed it.

This represents a severe function-level authorization failure when the SUID binary is poorly programmed or uses insecure environment variables.
If a binary owned by root has the SUID bit set (`chmod u+s`), and it internally calls a system command (e.g., `system("cat /etc/shadow")`) without specifying an absolute path, it inherits the `$PATH` environment variable of the low-privileged attacker executing it. The attacker can modify their `$PATH` to point to a malicious binary named `cat`, run the SUID executable, and the binary will inadvertently execute the attacker's code with `root` privileges. This violates function-level authorization because the system intended to restrict root functions to specific logic, but the attacker manipulated the execution environment to hijack that authority.

### Q3: How do named pipe impersonation attacks bypass function-level authorization in Windows IPC mechanisms?
Inter-Process Communication (IPC) via Named Pipes is a core mechanism in Windows. To facilitate seamless communication, the Windows API provides the `ImpersonateNamedPipeClient` function. If a high-privileged service connects to a named pipe hosted by a lower-privileged service, the host service can call this API to temporarily adopt the security token of the client to perform operations on its behalf.

This breaks function-level authorization when an attacker controls the Named Pipe. 
If a service account (e.g., `NETWORK SERVICE` running IIS) possesses `SeImpersonatePrivilege`, an attacker who compromises this account can create a malicious Named Pipe. The attacker then leverages RPC calls (like `RpcRemoteFindFirstPrinterChangeNotification` in the PrintSpoofer attack) to force a highly privileged SYSTEM service (like the Print Spooler) to authenticate to their Named Pipe. Once the SYSTEM service connects, the attacker's script calls `ImpersonateNamedPipeClient`, legally stealing the SYSTEM token provided by the OS, and utilizes it to execute code, bypassing all intended boundaries between the Network Service and SYSTEM.

## Scenario-Based Questions

### Q1: Red Team Scenario: You have a shell as a service account (`NETWORK SERVICE`) with `SeImpersonatePrivilege`. Walk me through the exact API calls and tools to escalate to SYSTEM.
**Scenario Context:** Post-exploitation privilege escalation via Token Impersonation.
**Execution:**
1. I deploy a tool like `PrintSpoofer` or `RoguePotato` to the target.
2. The tool creates a new Named Pipe (e.g., `\\.\pipe\test\pipe\spoolss`).
3. The tool initiates an RPC connection to the local Print Spooler service and executes the `RpcRemoteFindFirstPrinterChangeNotification` API call. This function tells the Print Spooler to send notifications of changes to my maliciously crafted Named Pipe.
4. The Print Spooler service, running as `NT AUTHORITY\SYSTEM`, connects to my Named Pipe.
5. My tool executes the `ImpersonateNamedPipeClient` API. The OS validates that I have `SeImpersonatePrivilege` and grants my thread a SYSTEM impersonation token.
6. To stabilize the access, the tool calls `DuplicateTokenEx` to convert the impersonation token into a primary token.
7. Finally, it calls `CreateProcessAsUser` using the newly minted SYSTEM primary token, spawning `cmd.exe` or executing my payload with complete root-level authority.

### Q2: Threat Hunt: You suspect an attacker is abusing `SeDebugPrivilege` to dump LSASS. What ETW providers or Event IDs indicate this function-level authorization abuse?
**Investigation Methodology:**
Dumping LSASS requires abusing function-level authorization to read sensitive process memory.
1. **Event Log Hunting:** I query Event ID 4656 (A handle to an object was requested) and Event ID 4663 (An attempt was made to access an object). I filter for `TargetUserName: lsass.exe` and `AccessMask: 0x1010` or `0x1410` (which map to `PROCESS_VM_READ`).
2. **ETW Telemetry:** Modern EDRs leverage the `Microsoft-Windows-Threat-Intelligence` ETW provider. I look for the `KEEPALIVE` and `ALLOCVM` events originating from suspicious binaries. Specifically, I monitor the `NtOpenProcess` and `NtReadVirtualMemory` system calls targeting the PID of `lsass.exe`.
3. If I observe a process executing from `C:\Users\Public` requesting `PROCESS_VM_READ` against LSASS, it is an undeniable indication of a function-level authorization abuse via `SeDebugPrivilege` (e.g., Mimikatz, Procdump, or specialized API hashing tools).

### Q3: Red Team Scenario: You are on a Linux box and find a custom binary with SUID root that executes `curl`. How do you exploit this function-level flaw to gain a root shell?
**Scenario Context:** Linux Privilege Escalation via environment variable injection.
**Execution:**
1. I inspect the SUID binary via `strings` or `ltrace` to confirm it is calling `curl` without an absolute path (e.g., `system("curl http://example.com")`).
2. I create a malicious script named `curl` in my `/tmp` directory. The script contains `#!/bin/bash` followed by `chmod +s /bin/bash` (which makes the bash shell itself an SUID root binary).
3. I modify my `$PATH` environment variable so that `/tmp` is checked before standard system directories: `export PATH=/tmp:$PATH`.
4. I execute the vulnerable SUID binary. When it attempts to execute `curl`, the OS searches my manipulated `$PATH`, finds my malicious `/tmp/curl` script, and executes it.
5. Because the initial binary had SUID root, my malicious script is executed with root function-level authority. The script executes, setting the SUID bit on `/bin/bash`.
6. I then execute `/bin/bash -p` (preserving privileges) to gain an interactive root shell.

## Deep-Dive Defensive Questions

### Q1: How do you implement Token Filter Policies and LSA Protection to mitigate function-level authorization bypasses via LSASS memory access?
**Architecture Design:**
1. **LSA Protection (RunAsPPL):** By configuring the registry key `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\RunAsPPL` to `1`, LSASS runs as a Protected Process Light. This enforces kernel-level authorization. Even if an attacker possesses `SeDebugPrivilege`, the kernel will block `OpenProcess` calls to LSASS from non-protected processes, neutralizing standard memory dumping techniques.
2. **Credential Guard:** Enable Windows Defender Credential Guard via Group Policy. This leverages virtualization-based security (VBS) to isolate the LSA secrets into a secure enclave (Isolated LSA). The main OS instance, even operating as SYSTEM with all privileges, literally cannot access the memory space where the NTLM hashes and Kerberos tickets are stored, providing hardware-backed function-level authorization enforcement.

### Q2: Discuss the use of Linux Capabilities (e.g., `CAP_SYS_ADMIN`, `CAP_NET_RAW`) as a granular alternative to SUID, and how attackers can still abuse them.
**Linux Capabilities:**
Capabilities decompose the monolithic "root" function-level authorization into smaller, discrete units. Instead of granting a binary SUID root, administrators can assign specific capabilities. For example, `ping` only needs `CAP_NET_RAW` to open raw sockets, not full system access.
**Abuse Vectors:**
Attackers look for binaries with overly permissive capabilities.
- **CAP_SYS_ADMIN:** Equivalent to root. Allows mounting filesystems. An attacker can mount a malicious filesystem or manipulate namespace structures to gain root.
- **CAP_DAC_READ_SEARCH:** Bypasses file read permission checks. An attacker can read `/etc/shadow` directly.
- **CAP_SETUID:** Allows a process to arbitrarily change its UID. If Python has `CAP_SETUID` (`setcap cap_setuid+ep /usr/bin/python`), an attacker can simply run `python -c 'import os; os.setuid(0); os.system("/bin/sh")'` to bypass function-level restrictions and become root.

### Q3: Design an EDR logic rule using API hooking to detect illegitimate usage of `NtImpersonateThread` and `NtDuplicateToken`.
**EDR Logic Rule Design:**
1. **API Hooking:** The EDR deploys a user-mode DLL into all running processes, hooking the `ntdll.dll` functions `NtImpersonateThread` and `NtDuplicateToken`.
2. **Contextual Evaluation:** When the hook intercepts a call, it evaluates the calling thread's context. Legitimate impersonation is highly predictable (e.g., WMI provider host, IIS worker processes).
3. **Detection Criteria:**
   - Trigger an alert if the calling process is a known LOLBin (Living off the Land Binary) or unverified executable.
   - Trigger if `NtDuplicateToken` is called requesting `TOKEN_ALL_ACCESS` on an impersonation token belonging to `NT AUTHORITY\SYSTEM`.
   - Monitor the subsequent execution flow. If an `NtCreateUserProcess` is immediately spawned utilizing the duplicated SYSTEM token by a process that did not originally possess SYSTEM rights, immediately block the execution and isolate the host, as this is the definitive signature of a function-level impersonation bypass.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------------+
|                  Token Impersonation via Named Pipes (PrintSpoofer)                     |
|                                                                                         |
|  [Attacker Service] (NETWORK SERVICE)                                                   |
|          | (Has SeImpersonatePrivilege)                                                 |
|          |                                                                              |
|          | 1. Create Named Pipe: \\.\pipe\test\pipe\spoolss                             |
|          +-------------------------------------------------------------+                |
|                                                                        |                |
|  2. RPC Call: RpcRemoteFindFirstPrinterChangeNotification              |                |
|     (Target: Localhost Print Spooler)                                  |                |
|     (Tells Spooler to notify our custom Named Pipe)                    |                |
|          |                                                             |                |
|          v                                                             |                |
|  [Print Spooler Service] (NT AUTHORITY\SYSTEM)                         |                |
|          |                                                             |                |
|          | 3. Connects to Attacker's Named Pipe to send notification   |                |
|          +------------------------------------------------------------>|                |
|                                                                        |                |
|                                         4. Call ImpersonateNamedPipeClient()            |
|                                            (Steal SYSTEM Token via Kernel RPC check)    |
|                                                                        |                |
|                                         5. Call DuplicateTokenEx()                      |
|                                            (Convert Impersonation to Primary Token)     |
|                                                                        |                |
|                                         6. Call CreateProcessAsUser()                   |
|                                            (Spawn Payload as SYSTEM)                    |
|                                                                        |                |
|                                            +---------------------------------+          |
|                                            | root/SYSTEM Command Prompt      |          |
|                                            +---------------------------------+          |
+-----------------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

During an APT investigation on a high-security defense contractor, incident responders discovered a persistent threat that had bypassed all EDR solutions. The initial vector was a zero-day vulnerability in a popular third-party monitoring agent running on the perimeter DMZ servers.

The monitoring agent ran under a low-privileged service account. However, because the agent needed to restart services, the software vendor had documented that the service account required `SeImpersonatePrivilege` in the Local Security Policy.

The threat actors utilized a custom memory-resident implant that entirely avoided touching the disk. Once the implant executed within the context of the monitoring agent, it leveraged a variation of the RoguePotato exploit. It coaxed the DCOM service (running as SYSTEM) into authenticating over local RPC to an attacker-controlled endpoint. 

By abusing the broken function-level authorization inherent in the `SeImpersonatePrivilege` token architecture, the implant seamlessly elevated its thread to SYSTEM authority. Operating within memory and utilizing legitimate API calls (`ImpersonateLoggedOnUser`), the implant disabled the EDR sensor's telemetry forwarding by altering the sensor's own registry keys before the EDR could parse the anomalous API chain, leading to a massive, undetected exfiltration of classified schematics.

## Chaining Opportunities

- **Function Level Bypass to Object Level Abuse:** Escalating to SYSTEM via Token Impersonation, and then using that SYSTEM context to overwrite the DACL (Object Level) of the Domain Admin group via LDAP.
- **Function Level Bypass to Defense Evasion:** Exploiting SUID root binaries on a Linux host to load a malicious kernel module (LKM) that hooks system calls, rendering the attacker's processes completely invisible to `ps`, `top`, or anti-malware tools.
- **Function Level Bypass to Authentication Forgery:** Using `SeDebugPrivilege` to extract the KRBTGT hash from a Domain Controller's LSASS memory, chaining directly into Golden Ticket generation.

## Related Notes
- [[Windows Access Tokens and Privileges]]
- [[Named Pipe Communication and RPC]]
- [[Linux SUID, SGID, and Capabilities]]
- [[EDR API Hooking and Bypass Techniques]]
- [[Credential Guard and LSA Protection]]
- [[Inter-Process Communication (IPC) Exploitation]]
