---
tags: [interview, threat-hunting, ir, qna, scenario]
difficulty: expert
module: "Interview Prep - Threat Hunting and IR"
topic: "QnA - TH Module 89"
---

# Endpoint Threat Hunting (Windows, Sysmon, EDR) QnA

## Introduction
This document contains expert-level interview questions and deep-dive technical answers focused on Windows Endpoint Threat Hunting. It covers advanced telemetry sources like Sysmon, Event Tracing for Windows (ETW), EDR evasion techniques (API hooking, process injection), and forensic analysis of Windows internals.

## Custom ASCII Diagram: EDR Telemetry & Process Injection Hunting

```text
  [ Attacker Process ]                          [ Target Process (e.g., svchost.exe) ]
   (Malware.exe)                                       |
        |                                              |
        | 1. OpenProcess()                             |
        |--------------------------------------------> | [ Sysmon Event ID 10: ProcessAccess ]
        |                                              |   (GrantedAccess: 0x1F0FFF)
        | 2. VirtualAllocEx()                          |
        |--------------------------------------------> | [ ETW Ti: NtAllocateVirtualMemory ]
        |    (Allocates PAGE_EXECUTE_READWRITE)        |
        |                                              |
        | 3. WriteProcessMemory()                      |
        |--------------------------------------------> | [ ETW Ti: NtWriteVirtualMemory ]
        |    (Writes malicious shellcode)              |
        |                                              |
        | 4. CreateRemoteThread()                      |
        |--------------------------------------------> | [ Sysmon Event ID 8: CreateRemoteThread ]
        v                                              v
  [ Continues Execution ]                       [ Malicious Thread Starts ]
                                                       |
                                                       | [ Sysmon Event ID 3: Network Connection ]
                                                       |   (svchost.exe connects to C2 IP)
```

---

## Formal Technical Questions

### Q1: Compare and contrast User-Mode API Hooking and Event Tracing for Windows Threat Intelligence (ETW-Ti). How do modern EDRs utilize them, and how do attackers bypass them?
**Expert Answer:**
*   **User-Mode API Hooking:**
    *   *Mechanism:* EDRs inject a DLL (e.g., `ntdll.dll` wrapping) into user-land processes. When a process calls a Windows API function like `CreateProcessW` or `VirtualAlloc`, the EDR intercepts the call via a JMP instruction (inline hook), inspects the parameters, logs the telemetry, and then returns execution to the original function if it's benign.
    *   *Bypass:* Attackers use **Direct System Calls (Syscalls)** (e.g., Hell's Gate, Halo's Gate). By manually setting up the CPU registers and calling the `syscall` instruction directly, they entirely bypass the user-mode hooks placed in `ntdll.dll`. Another method is "unhooking" by loading a fresh copy of `ntdll.dll` from disk (`C:\Windows\System32\ntdll.dll`) into memory, overwriting the EDR's hooks.
*   **ETW-Ti (Event Tracing for Windows - Threat Intelligence):**
    *   *Mechanism:* A kernel-level telemetry provider introduced in Windows 10. It monitors system calls directly from the kernel (Ring 0), making it immune to user-mode unhooking or direct syscalls. It provides high-fidelity logs for memory allocations, thread creation, and handle manipulation. EDRs use the Early Launch Anti-Malware (ELAM) driver to subscribe to ETW-Ti.
    *   *Bypass:* Since ETW-Ti operates in the kernel, bypassing it requires exploiting a vulnerable signed driver (Bring Your Own Vulnerable Driver - BYOVD) to gain kernel read/write primitives, allowing the attacker to patch the ETW-Ti callbacks or blind the EDR's driver directly.

### Q2: Deep Dive into Sysmon Event ID 10 (ProcessAccess). Why is it critical for threat hunting, and what specific `GrantedAccess` masks indicate malicious activity?
**Expert Answer:**
Sysmon Event ID 10 logs when a process opens a handle to another process. This is the fundamental precursor to process injection, credential dumping (e.g., reading LSASS memory), and debugging.
*   **Why it's critical:** Many fileless attacks inject code into legitimate processes (like `explorer.exe` or `svchost.exe`). Event ID 10 allows hunters to detect the *preparation* phase of the injection before the malicious thread even starts.
*   **Key `GrantedAccess` Masks:**
    *   `0x1F0FFF` (PROCESS_ALL_ACCESS): Highly suspicious if requested by a non-system process to a critical process like LSASS. It means the source process wants full control (read, write, terminate). Mimikatz historically requests this.
    *   `0x1410` (PROCESS_VM_READ | PROCESS_QUERY_INFORMATION): Frequently used by credential dumpers (like Procdump or custom loaders) to read `lsass.exe` memory without requesting full, noisy access.
    *   `0x143A` (PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_CREATE_THREAD): The exact permissions needed to perform classic DLL injection or shellcode injection (Allocate memory, write memory, and spawn a thread).
*   **Hunting Strategy:** Filter out legitimate access (e.g., Antivirus/EDR processes, taskmgr, svchost) and hunt for unusual processes (e.g., `powershell.exe`, `excel.exe`, or unknown binaries in `AppData`) requesting `0x1410` against `lsass.exe` or `0x143A` against `svchost.exe`.

### Q3: Explain the difference between Process Hollowing and Process Doppelgänging. What specific endpoint artifacts would a threat hunter look for?
**Expert Answer:**
Both are defense evasion techniques designed to execute malicious code under the guise of a legitimate Windows process.
*   **Process Hollowing (T1055.012):**
    *   *Mechanism:* The attacker creates a legitimate process (e.g., `svchost.exe`) in a suspended state. They then use `NtUnmapViewOfSection` to "hollow out" the legitimate code from memory, allocate new memory, write the malicious payload into the hollowed space, and call `ResumeThread`.
    *   *Artifacts:*
        *   Sysmon Event ID 1 (Process Create) showing process spawned suspended.
        *   Memory analysis (Volatility/Rekall) reveals that the VAD (Virtual Address Descriptor) mapping for the executable differs from the PE header mapped on disk. The memory page permissions will often be `PAGE_EXECUTE_READWRITE` (RWX).
*   **Process Doppelgänging (T1055.013):**
    *   *Mechanism:* Abuses Windows Transactional NTFS (TxF). The attacker creates a transaction, overwrites a legitimate executable file with a malicious payload *within* the transaction, maps the malicious payload into memory, and then *rolls back* the transaction. The file on disk remains completely untouched and pristine, but the malicious code executes in memory. It avoids the noisy `NtUnmapViewOfSection` call.
    *   *Artifacts:*
        *   Since TxF is used, hunting for unusual usage of TxF APIs (via ETW or API hooking).
        *   In memory, the process block (PEB) will point to a file path that, when hashed, does not match the memory resident code.
        *   Sysmon Event ID 1 might show execution of a binary, but subsequent hashing of the disk file shows it is benign.

---

## Scenario-Based Questions

### Q4: You observe an alert indicating `rundll32.exe` executed without any command-line parameters. The process then made an outbound HTTPS connection. You are conducting the IR. Walk me through your analysis.
**Expert Answer:**
Legitimate `rundll32.exe` execution absolutely requires command-line parameters (specifically, the path to the DLL and the exported function to call). An execution with no parameters is a massive red flag indicating **Process Injection**, specifically a technique like Thread Execution Hijacking, Hollow Process, or a Cobalt Strike / Metasploit payload.
1.  **Analyze Parent Process:** I check Sysmon Event ID 1. What spawned `rundll32.exe`? If it was `powershell.exe`, `wscript.exe`, or a Microsoft Office product (via macro), it confirms a malicious loader chain.
2.  **Analyze Cross-Process Access (Event ID 10 / 8):** I look for Sysmon Event 10 or 8 immediately preceding the `rundll32.exe` execution. Which process opened a handle to `rundll32.exe` and injected into it? This reveals the true source of the malware (the "loader").
3.  **Network Telemetry:** Since it made an outbound connection, I investigate Sysmon Event ID 3 or firewall/proxy logs. I look at the destination IP, ASN, and check for JA3/JA4 TLS fingerprinting to identify if it's a known C2 framework (e.g., Cobalt Strike beacon).
4.  **Memory Acquisition:** Because the payload is memory-resident (running inside `rundll32.exe`), pulling the disk image is useless. I would immediately trigger an EDR live-response script to capture a memory dump of the `rundll32.exe` process (using `procdump` or EDR native tools) for reverse engineering and string extraction to find C2 configs.
5.  **Containment:** Isolate the host from the network while preserving its memory state.

### Q5: A suspected supply-chain compromise has occurred. A signed, legitimate IT management agent (e.g., SolarWinds, Kaseya) is dropping malicious webshells, but EDR is largely silent because the agent folder is globally excluded from scanning. How do you hunt for this?
**Expert Answer:**
Exclusions are the Achilles' heel of EDR deployments. Attackers routinely map out EDR blind spots (like `C:\Program Files\IT_Agent\*`) and utilize them as staging directories.
1.  **Pivot to Un-Excluded Telemetry:** Even if file scanning (AV) is disabled for the directory, process creation (Sysmon 1) and network connections (Sysmon 3) usually are still logged.
2.  **Hunt for Anomalous Child Processes:** The IT agent should have a predictable process tree. I would baseline its normal child processes over 30 days. If the agent (`it_agent.exe`) suddenly starts spawning `cmd.exe`, `powershell.exe`, `certutil.exe`, or `w3wp.exe` (IIS worker), this breaks the baseline and indicates exploitation.
3.  **Hunt for File Creation Outside the Exclusion:** The agent might drop files in its excluded folder, but to achieve broader goals, it will write outside of it. I would query for Sysmon Event ID 11 (File Create) where the `Image` (source process) is the IT agent, but the `TargetFilename` is in a sensitive web directory (e.g., `C:\inetpub\wwwroot\`, indicating a webshell drop) or `C:\Windows\System32\`.
4.  **Analyze Network Beacons:** Review network flow data for the IT agent. Supply chain malware often introduces a secondary, anomalous beaconing pattern. I would look for connections to unregistered domains, non-standard ASNs, or sudden spikes in data transfer (exfiltration) that differ from the agent's normal telemetry endpoints.

---

## Deep-Dive Defensive Questions

### Q6: What are "Unbacked Memory Regions" (Floating Code) and how can defenders hunt for execution occurring within them?
**Expert Answer:**
**Unbacked memory** refers to executable memory regions in a process's virtual address space that do not correspond (are not backed by) a file on disk. Normal Windows executables and DLLs are "memory-mapped" from disk; the memory is backed by the physical PE file.
*   **The Threat:** When an attacker uses reflective DLL injection, shellcode injection, or Cobalt Strike's execute-assembly, the malicious code is written directly into dynamically allocated memory (via `VirtualAlloc`). This memory is unbacked.
*   **Hunting for it:**
    *   **Memory Scanning (YARA via EDR):** Modern EDRs periodically scan memory for known malicious signatures.
    *   **Call Stack Analysis (Advanced):** By hooking sensitive APIs (like `CreateProcess` or `InternetOpen`), EDRs inspect the thread's call stack. If the return address points to an unbacked memory region (a memory address not belonging to a loaded module/DLL), it is highly indicative of injected shellcode.
    *   **ETW-Ti Profiling:** Monitoring `ThreatInt-Allocation` events for processes requesting `PAGE_EXECUTE_READWRITE` (RWX) memory regions and subsequently executing threads starting at those addresses.

### Q7: Attackers frequently disable or blind EDR solutions. What telemetry can you use to hunt for the act of EDR tampering or blinding?
**Expert Answer:**
EDR tampering is a critical, high-priority event. Attackers use techniques like unloading the driver, patching the user-mode hooks, or blocking the EDR's network communication.
*   **Hunting via Service/Registry Modifications:**
    *   Monitor for changes to the `ImagePath` or `Start` values of known EDR services in the Registry (e.g., `HKLM\SYSTEM\CurrentControlSet\Services\Sense` for Defender for Endpoint).
    *   Hunt for `fltmc.exe unload <filter>` commands used to unload EDR kernel minifilters.
*   **Hunting via Process Terminations:**
    *   Monitor Sysmon Event ID 10 where the target is the EDR process, specifically looking for `PROCESS_TERMINATE` rights.
*   **Hunting via Missing Telemetry (The "Silent Host" Hunt):**
    *   Create a SIEM dashboard measuring log volume per host. If a host suddenly stops sending EDR telemetry but is still authenticating to Active Directory (Windows Event 4624) or generating firewall traffic, the EDR has been blinded or isolated.
*   **Hunting via Firewall/Null Routing:**
    *   Attackers often use Windows Firewall or the `route` command to blackhole EDR telemetry IPs (e.g., `route add <EDR_IP> mask 255.255.255.255 0.0.0.0`). Hunt for `netsh advfirewall` or `route ADD` commands in process execution logs.

---

## Real-World Attack Scenario

### Cobalt Strike Beacon with Sleep Mask and Module Stomping
**Background:** A highly sophisticated threat actor gained access via a spear-phishing payload. They deployed a Cobalt Strike beacon. To evade memory scanners and unbacked memory detections, they utilized "Module Stomping" and a "Sleep Mask".
**The Attack:**
1.  **Module Stomping:** Instead of using `VirtualAlloc` for unbacked memory, the malware loaded a legitimate, benign Windows DLL (e.g., `xpsprint.dll`) that the process wasn't actually using. It then overwrote the executable `.text` section of that loaded DLL with its malicious Cobalt Strike payload. Now, the memory *is* backed by a file on disk, evading basic unbacked memory checks.
2.  **Sleep Mask:** When the beacon was idle (waiting for the C2 callback interval), it encrypted its own executable memory region and changed its memory protections to `PAGE_READWRITE` (RW). Right before calling home, it decrypted itself and changed permissions back to `PAGE_EXECUTE_READWRITE` (RWX). This evaded EDR memory scanners that look for RWX pages or plain-text malware strings.

**The Hunt:**
*   A threat hunter reviewing SIEM data noticed a rare network connection from `dllhost.exe` to an uncategorized IP address.
*   **Hunt Execution:** Pulling the ETW-Ti telemetry for that specific `dllhost.exe` process ID, the hunter looked at memory allocation anomalies.
*   **Discovery:** They observed a rapid sequence of `NtProtectVirtualMemory` calls changing memory permissions from RX -> RW -> RWX -> RW in a cyclic pattern every 60 seconds (matching the beacon interval). Furthermore, checking the thread start address, they found execution originating from the `.text` section of `xpsprint.dll`, but the thread call stack contained anomalies that didn't match legitimate `xpsprint.dll` functions.
*   **Response:** The hunter performed a live memory acquisition of `dllhost.exe` at the exact moment the beacon was communicating (when memory was decrypted), extracted the beacon configuration, and blocked the C2 infrastructure enterprise-wide.

---

## Chaining Opportunities
*   To understand the network side of the Cobalt Strike beaconing detected in the scenario above, review [[TH QnA - Module 90 - Network Threat Hunting Zeek Suricata PCAP]].
*   For the broader methodological approaches to formulating hypotheses like "adversaries are module stomping", revisit [[TH QnA - Module 88 - Threat Hunting Foundations and Methodologies]].
*   For deep dives into memory forensics and extracting the specific configs mentioned, see [[Advanced Memory Forensics and Volatility]].

## Related Notes
*   [[Windows Process Internals and Memory Management]]
*   [[Sysmon Configuration and Event IDs]]
*   [[Bypassing User-Mode API Hooking]]
*   [[Event Tracing for Windows (ETW) Fundamentals]]
