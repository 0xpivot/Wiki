---
tags: [c2, opsec, evasion, edr, vapt]
difficulty: advanced
module: "99 - C2 OPSEC and EDR Evasion Techniques"
topic: "99.12 Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD"
---

# 99.12 Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD

## Overview
Bring Your Own Vulnerable Driver (BYOVD) is a sophisticated technique used by advanced persistent threats and red teams to bypass Windows Driver Signature Enforcement (DSE) and gain kernel-level (Ring 0) execution capabilities. By dropping a legitimately signed but inherently flawed driver, attackers can exploit these vulnerabilities to manipulate core operating system structures, effectively blinding or neutralizing Endpoint Detection and Response (EDR) solutions from the inside out.

## In-Depth Technical Mechanics
Windows DSE mandates that all kernel-mode drivers be digitally signed by a trusted authority, preventing the direct loading of malicious, unsigned drivers. The BYOVD technique circumvents this protection.

The attack sequence typically follows these steps:
1. **Deployment:** An attacker with administrative privileges drops a known, legitimately signed driver that contains vulnerabilities (e.g., `RTCore64.sys`, `gdrv.sys`, or `Capcom.sys`). These vulnerabilities often include arbitrary memory read/write primitives or out-of-bounds access via specific IOCTLs (Input/Output Control).
2. **Service Installation:** The attacker uses the Service Control Manager (SCM) or the `NtLoadDriver` API to load the vulnerable driver. Because the signature is valid, DSE allows the driver to load into the kernel space.
3. **Exploitation:** The attacker's user-mode application interacts with the loaded driver using `DeviceIoControl`. By sending carefully crafted IOCTL requests, the attacker exploits the vulnerability to achieve arbitrary read and write access to kernel memory.
4. **EDR Neutralization:** With kernel memory access, the attacker locates critical OS structures. They can modify the `EPROCESS` block to remove Protected Process Light (PPL) attributes from EDR agents, allowing them to be terminated using standard user-mode APIs. Alternatively, they can locate and zero out the arrays holding EDR kernel callbacks (e.g., `PspCreateProcessNotifyRoutine`), which blinds the EDR to new process creations and other system events.

## Memory and Kernel Structures
Executing a successful BYOVD attack requires precise manipulation of several undocumented kernel structures:
- **`EPROCESS` Structure:** Represents a process object in the kernel. It contains vital attributes, including the process ID, image filename, and protection flags (such as PPL). Overwriting the protection byte allows the termination of otherwise protected security processes.
- **`ActiveProcessLinks`:** A doubly linked list within the `EPROCESS` structure that tracks all running processes. Unlinking an EDR process from this list can hide it from standard API calls like `EnumProcesses`.
- **Kernel Callback Arrays:** EDR drivers register monitoring functions (callbacks) in specific kernel arrays. Key callbacks include:
    - `PspCreateProcessNotifyRoutine`: For process creation/termination.
    - `PspCreateThreadNotifyRoutine`: For thread creation/termination.
    - `PspLoadImageNotifyRoutine`: For image (DLL/EXE) loading.
    Zeroing out the entries in these arrays effectively stops the OS from sending telemetry to the EDR.

## Architectural Diagram
```text
    User Mode (Ring 3)                          Kernel Mode (Ring 0)
    +-----------------------+                   +-----------------------+
    | Attacker Process      |                   | Windows Kernel        |
    | (High Privileges)     |                   |                       |
    |                       |                   |                       |
    | 1. Drops Driver       +---(File Write)--->| File System           |
    |                       |                   |                       |
    | 2. Loads Driver       +---(Service)------>| Load Image Callback   |
    |                       |                   | (DSE Checks Signature)|
    |                       |                   |       | (Pass)        |
    |                       |                   |       v               |
    |                       |                   | +-------------------+ |
    |                       |                   | | Vulnerable Driver | |
    | 3. Exploit via IOCTL  +---(DeviceIoCtrl)->| | (e.g., RTCore64)  | |
    |                       |                   | +---------+---------+ |
    |                       |                   |           |           |
    |                       |                   |   (Arbitrary Read/Write)
    |                       |                   |           |           |
    |                       |                   |           v           |
    |                       |                   | Target: EDR Callbacks,|
    |                       |                   | Process Protected Light
    +-----------------------+                   +-----------------------+
```

## Real-World Attack Scenario
An advanced threat actor compromises a hardened server protected by a top-tier EDR running under PPL. Knowing their C2 framework will be quickly identified, they pivot to a BYOVD strategy. They deploy an MSI driver, `RTCore64.sys`, which is vulnerable to arbitrary memory reads/writes. They install it as a service named `TempSvc`. Using a custom implant, they send malicious IOCTLs to `RTCore64.sys` to scan kernel memory, locate the EDR service's `EPROCESS` block, and change the protection flag from 0x31 (PPL-Antimalware) to 0x00. With PPL stripped, the implant calls `TerminateProcess` on the EDR agent. The server is left completely unmonitored, enabling the attacker to move laterally and deploy ransomware without detection.

## EDR Telemetry and Detection Engineering
Detecting BYOVD attacks relies heavily on monitoring driver loading and system integrity:
- **Service Creation Anomalies:** Monitor Event ID 7045 (A service was installed in the system) specifically for `Kernel Mode Driver` types. Pay close attention to unexpected parent processes or drivers loaded from unusual paths (e.g., `C:\Windows\Temp` or `C:\Users\Public`).
- **Driver Load Monitoring:** Track Event ID 6 (Driver loaded) from Sysmon or equivalent ETW providers. Maintain a comprehensive hash list of known vulnerable drivers (e.g., utilizing resources like the LOLDrivers project) and alert on their execution.
- **Telemetry Loss:** A sudden, unexplained drop in telemetry—such as a halt in process creation logs or network connection events from a specific endpoint—can indicate that kernel callbacks have been tampered with or the EDR agent has been forcefully terminated.

## Mitigation Strategies
Mitigating BYOVD requires strict control over what executes in the kernel space:
- **Microsoft Vulnerable Driver Blocklist:** Ensure this feature is enabled in Windows Security (Core Isolation). It leverages a frequently updated list to block known vulnerable drivers from loading, regardless of whether their signature is valid.
- **Windows Defender Application Control (WDAC):** Implement aggressive WDAC policies that explicitly allow only approved, necessary drivers to run in the environment, implicitly blocking all others.
- **Virtualization-Based Security (VBS) and HVCI:** Enable Hypervisor-Protected Code Integrity (HVCI). HVCI uses hardware virtualization to protect kernel memory, significantly increasing the difficulty of exploiting arbitrary read/write vulnerabilities to manipulate critical structures.

## Chaining Opportunities
BYOVD is frequently used as a precursor step in complex attack chains:
- It is often utilized before deploying a FUD payload (see [[14 - Creating FUD Fully Undetectable Payloads]]) to ensure that once the payload executes, the EDR is completely blind to its operations.
- It can be combined with techniques discussed in [[13 - Living off the Land C2 using Native APIs]] to obscure the initial loading of the vulnerable driver.

## Related Notes
- [[11 - Evading Memory Scanners Sleeping and Encrypting Memory]]
- [[12 - Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD]]
- [[13 - Living off the Land C2 using Native APIs]]
- [[14 - Creating FUD Fully Undetectable Payloads]]
- [[15 - Continuous Testing against EDR Sandboxes]]

## Extended Technical Glossary and Context
- **DSE:** Driver Signature Enforcement, prevents loading of unsigned drivers.
- **IOCTL:** Input/Output Control, used for user-space to kernel-space communication.
- **Ring 0:** Kernel mode, the highest privilege level in the OS.
- **Ring 3:** User mode, where normal applications run.
- **SCM:** Service Control Manager, manages Windows services.
- **EPROCESS:** Kernel structure representing a process.
- **PPL:** Protected Process Light, safeguards critical processes.
- **Kernel Callbacks:** Mechanisms for drivers to register for system event notifications.
- **ETW:** Event Tracing for Windows.
- **LOLDrivers:** Living Off The Land Drivers, a project tracking vulnerable drivers.
- **WDAC:** Windows Defender Application Control.
- **VBS:** Virtualization-Based Security.
- **HVCI:** Hypervisor-Protected Code Integrity.
- **Arbitrary Read/Write:** Vulnerability allowing an attacker to read/write memory anywhere.
- **Sysmon:** System Monitor, a Windows system service and device driver.
- **API:** Application Programming Interface.
- **C2:** Command and Control.
- **EDR:** Endpoint Detection and Response.
- **VAPT:** Vulnerability Assessment and Penetration Testing.
- **OPSEC:** Operations Security.
- **FUD:** Fully Undetectable.
- **NTAPI:** Native API used by Windows.
- **Syscalls:** Direct system calls.
- **Process Hollowing:** Replacing a legitimate process with malicious code.
- **Code Cave:** Unused memory section.
