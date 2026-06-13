---
tags: [defense, hardening, security, vapt, forensics]
difficulty: advanced
module: "56 - Defensive Security and Hardening"
topic: "56.20 EDR Solutions"
---

# 20 - EDR Solutions: CrowdStrike, SentinelOne, Defender

Traditional Antivirus (AV) relies primarily on signature-based detection. It scans files against a known database of malicious hashes. As attackers evolved to use fileless malware, living-off-the-land (LotL) techniques, and polymorphic code, traditional AV became largely ineffective.

**Endpoint Detection and Response (EDR)** represents the evolution of endpoint security. Rather than just looking at files, EDR focuses on continuous monitoring, behavioral analysis, and the collection of deep endpoint telemetry (process execution, registry changes, network connections) to detect and respond to advanced threats. EDR platforms often incorporate Next-Generation Antivirus (NGAV) for pre-execution prevention, acting as a comprehensive endpoint security suite.

## The Architecture of EDR

Modern EDR solutions share a common architectural pattern, designed to balance endpoint performance with cloud-scale analytics.

```text
+---------------------------------------------------------------------------------------------------+
|                                       Cloud Platform (SaaS)                                       |
|                                                                                                   |
|  +------------------+   +------------------+   +------------------+   +-----------------------+   |
|  |   Threat Intel   |   |   Data Lake /    |   | Behavioral AI &  |   | Security Analyst Console|   |
|  |   (Global Feeds) |-->|   Telemetry DB   |<--| Machine Learning |<--| (Triage, Hunting,     |   |
|  +------------------+   +--------+---------+   +------------------+   |  Response Actions)    |   |
|                                  ^                                    +-----------------------+   |
|                                  | (Continuous Telemetry Stream)                                  |
+----------------------------------|----------------------------------------------------------------+
                                   |
                                   | (Encrypted TLS Connection)
                                   |
+---------------------------------------------------------------------------------------------------+
|                                       Corporate Endpoint                                          |
|                                                                                                   |
|  +---------------------------------------------------------------------------------------------+  |
|  |                                      EDR Agent                                              |  |
|  |                                                                                             |  |
|  |  +------------------+ +------------------+ +------------------+ +------------------------+  |  |
|  |  | NGAV Engine      | | Local AI Model   | | Telemetry Buffer | | Response Engine        |  |  |
|  |  | (Signatures/ML)  | | (Offline Detect) | | (Processes, Net) | | (Kill, Isolate, Block) |  |  |
|  |  +---------+--------+ +---------+--------+ +---------+--------+ +-----------+------------+  |  |
|  +------------|--------------------|--------------------|----------------------|---------------+  |
|               |                    |                    |                      |                  |
|               v                    v                    v                      v                  |
|  +---------------------------------------------------------------------------------------------+  |
|  |                                   Operating System (Kernel)                                 |  |
|  |                                                                                             |  |
|  | - File System Filter Drivers (e.g., FltMgr)                                                 |  |
|  | - Network Drivers (e.g., WFP - Windows Filtering Platform)                                  |  |
|  | - Kernel Callbacks (e.g., PsSetCreateProcessNotifyRoutine)                                  |  |
|  | - Userland API Hooking (Injecting DLLs into running processes like ntdll.dll)               |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```

### Core EDR Components

1.  **The Agent:** A lightweight software deployed to endpoints (Windows, macOS, Linux). It hooks deep into the OS kernel and userland to monitor activity.
2.  **Continuous Telemetry Collection:** The agent records almost everything: process creations (with full command lines), module loads (DLLs), network connections, registry modifications, and file creations.
3.  **Detection Engine (Local & Cloud):** The agent performs local analysis using behavioral models to block obvious threats immediately (even offline). Simultaneously, it streams telemetry to the cloud, where massive compute power analyzes the data across the entire organization (and globally) to spot complex, slow-moving attacks.
4.  **Response Capabilities:** Allows analysts to take immediate action from the cloud console: killing processes, deleting files, isolating the host from the network (except for EDR communication), or even accessing a remote live shell on the endpoint.

## Comparative Analysis of Industry Leaders

While all major EDRs share the architecture above, their underlying philosophies and specific features differ.

### 1. CrowdStrike Falcon

CrowdStrike is a pioneer in cloud-native EDR. Its philosophy centers heavily on its "Threat Graph" and human-led threat hunting.

*   **Lightweight Agent:** Falcon is famous for having a single, highly optimized agent that operates primarily at the kernel level. It does very little heavy lifting locally, pushing the data to the cloud for analysis.
*   **Threat Graph:** CrowdStrike's proprietary database that correlates trillions of endpoint events globally in real-time, allowing for rapid detection of novel threats across their entire customer base.
*   **OverWatch:** A massive selling point for CrowdStrike. OverWatch is their managed threat hunting service. Dedicated human hunters actively monitor customer telemetry 24/7 for subtle signs of hands-on-keyboard adversary activity that automated AI might miss.
*   **Strengths:** Unparalleled threat intelligence, low endpoint footprint, excellent managed hunting.

### 2. SentinelOne Singularity

SentinelOne's philosophy leans heavily on localized Artificial Intelligence and autonomous response, reducing the reliance on constant cloud connectivity.

*   **Storyline Technology:** SentinelOne tracks all concurrent activities on an endpoint and links them together into a "Storyline." If a process suddenly acts maliciously, the agent can instantly trace the entire execution chain back to the root cause (e.g., identifying that the malicious PowerShell script originated from an embedded macro in an Excel file downloaded via Chrome).
*   **Behavioral AI:** Heavy reliance on machine learning models residing *on the endpoint*. This allows the agent to make autonomous decisions to kill/quarantine threats even if the endpoint is completely disconnected from the network.
*   **Rollback Capability:** A unique feature (especially on Windows via VSS integration). If ransomware successfully encrypts files, SentinelOne can theoretically "rollback" the endpoint to its pre-infected state autonomously.
*   **Strengths:** Strong offline protection, excellent automated context generation (Storyline), autonomous response features.

### 3. Microsoft Defender for Endpoint (MDE)

MDE has evolved from a basic AV into a top-tier EDR solution, largely due to its unprecedented integration with the Windows operating system.

*   **OS Integration:** Unlike third-party EDRs that must use supported kernel callbacks or userland hooking, MDE is built directly into Windows 10/11. There is no separate "agent" to deploy; it's a feature that is simply enabled via licensing and configuration. This provides MDE with incredible visibility and stability.
*   **Kusto Query Language (KQL):** MDE's advanced hunting feature uses KQL, a powerful and fast query language. Analysts can run incredibly complex, customized queries across months of telemetry data.
*   **Microsoft Security Stack Integration:** MDE integrates seamlessly with Azure AD (Identity), Microsoft Defender for Office 365 (Email), and Microsoft Cloud App Security (CASB), creating a cohesive XDR (Extended Detection and Response) ecosystem.
*   **Strengths:** Deep Windows OS integration, powerful hunting language (KQL), synergy with the broader Microsoft ecosystem.

## EDR Evasion Techniques (Red Team Perspective)

As EDRs became prevalent, attackers developed sophisticated techniques to blind or bypass them. Understanding these is crucial for defenders evaluating EDR effectiveness.

1.  **Userland API Unhooking:**
    *   *The Problem:* EDRs often inject their own DLL (e.g., `cybereason_sensor.dll`) into every running user process to "hook" crucial Windows APIs (like `NtCreateProcess` or `NtAllocateVirtualMemory`) in `ntdll.dll`. This allows the EDR to intercept the request and analyze it before passing it to the kernel.
    *   *The Evasion:* Malware can read a clean copy of `ntdll.dll` directly from the hard drive and overwrite the EDR's hooked functions in memory, effectively blinding the EDR to subsequent API calls from that process.

2.  **Direct System Calls (Syscalls):**
    *   *The Evasion:* Instead of calling the standard Windows APIs (which are monitored), the malware figures out the underlying System Service Number (SSN) and executes the assembly `syscall` instruction directly, jumping straight into the kernel and entirely bypassing the EDR's userland hooks.

3.  **BYOVD (Bring Your Own Vulnerable Driver):**
    *   *The Evasion:* Attackers drop a legitimate, digitally signed driver (e.g., an old anti-cheat engine or a specific hardware driver) that contains a known vulnerability. They exploit this vulnerability locally to execute code in the kernel (Ring 0). Once in the kernel, they can disable the EDR's kernel callbacks or terminate the EDR service entirely, as kernel-level code operates at a higher privilege than the EDR's userland agent.

4.  **Living off the Land (LotL):**
    *   *The Evasion:* Avoiding custom malware altogether. Attackers use legitimate tools like PowerShell, WMI, or LOLBins (Living Off The Land Binaries like `certutil.exe` or `msbuild.exe`) to execute their attacks. Because these tools are trusted and frequently used by administrators, behavioral detection becomes much harder and prone to false positives.

## Chaining Opportunities

*   **Threat Hunting:** EDR platforms are the primary tool used by threat hunters to execute complex queries and stack data. Connects to `[[19 - Threat Hunting Hypothesis-Driven Approach]]`.
*   **Malware Analysis:** Reverse engineers often analyze how specific malware samples attempt to bypass EDR hooks. Connects to `[[22 - Malware Analysis Reverse Engineering]]`.
*   **Windows Privilege Escalation:** Understanding EDR evasion is crucial during privilege escalation phases of an engagement. Connects to `[[05 - Windows Privilege Escalation]]`.

## Related Notes
*   `[[14 - Digital Forensics Fundamentals]]`
*   `[[17 - Log Analysis for Attack Detection]]`
*   `[[02 - Endpoint Security Architecture]]`
