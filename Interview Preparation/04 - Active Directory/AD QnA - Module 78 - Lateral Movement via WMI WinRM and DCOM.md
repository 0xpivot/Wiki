---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 78"
---

# Lateral Movement via WMI, WinRM, and DCOM

## Custom ASCII Diagram: WMI Event Subscription Execution Flow

```text
  +-----------------------+                            +-------------------------+
  |    Attacker Machine   |                            |   Target Machine        |
  |                       |                            |   (Compromised)         |
  +-----------+-----------+                            +-------------------------+
              |                                                    |
              | (1) Bind to WMI via RPC (Port 135 -> High Port)    |
              |     Authenticate as Local Admin                    |
              |--------------------------------------------------->|
              |                                                    |
              | (2) Create __EventFilter                           |
              |     (e.g., TargetInstance ISA 'Win32_LogonSession')|
              |--------------------------------------------------->|  WMI Repository
              |                                                    |  (OBJECTS.DATA)
              | (3) Create CommandLineEventConsumer                |
              |     (e.g., cmd.exe /c "powershell -enc ...")       |
              |--------------------------------------------------->|
              |                                                    |
              | (4) Create __FilterToConsumerBinding               |
              |     (Links Filter to Consumer)                     |
              |--------------------------------------------------->|
              |                                                    |
                                                                   |
  +-----------------------+                                        |
  |      Victim User      |                                        |
  |                       |   (5) Logs into machine                |
  +-----------+-----------+--------------------------------------->|
                                                                   |
                                                                   | (6) WMI Service (WmiPrvSE.exe)
                                                                   |     detects logon event.
                                                                   |     Filter condition met!
                                                                   |
                                                                   | (7) Consumer triggered.
                                                                   |     Executes Attacker Payload
                                                                   |     as SYSTEM implicitly.
                                                                   v
                                                        +-------------------------+
                                                        |  Reverse Shell to C2    |
                                                        +-------------------------+
```

## Formal Technical Questions

### Q1: Detail the architectural differences between lateral movement via WMI (Windows Management Instrumentation) over RPC versus WinRM.
**Expert Answer:**
**WMI over RPC (DCOM):**
Historically, WMI communication occurs over DCOM (Distributed Component Object Model). The attacker initiates a connection to the RPC Endpoint Mapper on TCP port 135. The Endpoint Mapper then assigns a dynamic high port (usually in the 49152-65535 range) for the actual WMI communication. This requires relatively open firewall rules between internal segments. From an execution standpoint, invoking the `Win32_Process::Create` method over DCOM spawns the malicious process under the `WmiPrvSE.exe` (WMI Provider Host) parent process.

**WinRM (Windows Remote Management):**
WinRM is the Microsoft implementation of WS-Management Protocol, which relies on SOAP over HTTP/HTTPS. It operates on predictable ports: TCP 5985 (HTTP) and 5986 (HTTPS). WinRM is highly firewall-friendly and is the transport layer for PowerShell Remoting. When an attacker executes commands via WinRM (e.g., `Invoke-Command`), the target spawns a `wsmprovhost.exe` (WinRM Provider Host) process, and the malicious payload is executed as a child of this process. 

### Q2: What is DCOM lateral movement, and how does the `MMC20.Application` object facilitate it?
**Expert Answer:**
DCOM (Distributed Component Object Model) allows COM software components to communicate over a network. Lateral movement via DCOM involves instantiating a COM object on a remote machine and invoking its methods to achieve code execution. 
The `MMC20.Application` (Microsoft Management Console) is a well-known COM object exposed via DCOM. It has an `ExecuteShellCommand` method.
An attacker with local administrator privileges on the target can use PowerShell to instantiate this object remotely:
`$com = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application", "192.168.1.100"))`
Once instantiated, the attacker calls the method:
`$com.Document.ActiveView.ExecuteShellCommand("cmd.exe", $null, "/c calc.exe", "7")`
This causes the remote machine to execute the command. The parent process for this execution is typically `mmc.exe`, making it blend in with standard administrative activity.

### Q3: Explain WMI Event Subscriptions. Why are they heavily favored for fileless persistence and lateral movement?
**Expert Answer:**
WMI Event Subscriptions are a mechanism that allows administrators (and attackers) to configure WMI to trigger specific actions when particular system events occur. It requires three components:
1. **Event Filter (`__EventFilter`):** A WQL query that defines the trigger condition (e.g., "A specific service starts", "System uptime reaches 5 minutes", "A user logs on").
2. **Event Consumer (`CommandLineEventConsumer`, `ActiveScriptEventConsumer`):** The action to perform when the trigger is met. This can be executing a command line, running a VBScript, or writing to a log file.
3. **Filter To Consumer Binding (`__FilterToConsumerBinding`):** The linkage that connects the specific Filter to the specific Consumer.

They are heavily favored for **fileless persistence** because the payload and logic are stored entirely within the WMI repository (`C:\Windows\System32\wbem\Repository\OBJECTS.DATA`), a complex proprietary database, rather than as a file on disk or a standard registry run key. This evades traditional Anti-Virus file scanning. Furthermore, when the consumer executes the payload, it typically runs as `NT AUTHORITY\SYSTEM` under `WmiPrvSE.exe`, granting maximum privileges.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You have a valid set of Domain Admin credentials but SMB port 445 is strictly blocked by host firewalls on your target servers. You verify TCP 5985 is open. How do you obtain an interactive shell on the remote server without dropping any binaries to disk?
**Expert Answer:**
Since TCP 5985 is open, WinRM is listening. Because I have Domain Admin credentials, my user is part of the Remote Management Users and Local Administrators groups, satisfying WinRM authorization requirements.
To obtain an interactive shell without dropping binaries, I will use **PowerShell Remoting**, which is built entirely on WinRM.
From my attacker machine (if Windows), I can simply execute:
`Enter-PSSession -ComputerName TargetServer -Credential $cred`
This creates a persistent, interactive remote PowerShell session over WS-Man. The connection is encrypted (even over HTTP via SPNEGO/Kerberos). The payload remains entirely in memory on the target server within the `wsmprovhost.exe` process, meaning no AV/EDR file-drop alerts will be triggered. 
If I am on a Linux attacking machine, I can use `Evil-WinRM`:
`evil-winrm -i TargetServer -u Administrator -p Password`
This tool provides a pseudo-interactive shell utilizing the same WinRM protocol, entirely fileless.

### Q2: During a penetration test, you need to execute a Cobalt Strike beacon via WMI on a target (`10.10.10.50`). You want to use `Win32_Process::Create`. Walk through the exact command using Impacket's `wmiexec.py` and explain the underlying mechanism. What OPSEC flaw does standard `wmiexec.py` have?
**Expert Answer:**
**Command:** 
`wmiexec.py DOMAIN/Administrator:Password@10.10.10.50`
Once the semi-interactive shell spawns, I execute my PowerShell download-cradle for the beacon.
**Mechanism:** 
Under the hood, `wmiexec.py` does not give a true interactive shell. When I type a command, Impacket connects to DCOM via port 135, negotiates a dynamic RPC port, and invokes `Win32_Process::Create` to run `cmd.exe /Q /c <my_command> 1> \\127.0.0.1\ADMIN$\__<timestamp> 2>&1`. 
It executes the command, pipes the output to a temporary file on the target's `ADMIN$` share via SMB, reads that file over SMB to display the output to my screen, and then deletes the file.
**OPSEC Flaw:**
The major OPSEC flaw in standard `wmiexec.py` is its heavy reliance on SMB and disk I/O. Even though WMI handles the execution, the output redirection writes a physical file to `C:\Windows\__<timestamp>` for every single command executed. Advanced EDRs immediately flag the creation of files with this specific naming convention in the Windows directory, and SOCs monitor SMB traffic for this exact pattern.

### Q3: You want to persist on a target using WMI Event Subscriptions. You want a reverse shell to execute every time the system boots. Explain how you craft the Event Filter specifically to trigger on system startup without relying on a user logging in.
**Expert Answer:**
To trigger on system startup without user interaction, I must query a system-level event class. A highly reliable method is querying the `Win32_ComputerSystem` class for an initialization event, or using the `__InstanceModificationEvent` on `Win32_PerfFormattedData_PerfOS_System` checking the `SystemUpTime`.
A simpler and stealthier trigger is targeting the `Win32_LocalTime` class or the start of a core service.
However, for pure boot persistence, I would craft an `__EventFilter` using the `Win32_ProcessStartTrace` class, looking for a process that always starts at boot, like `lsass.exe` or `svchost.exe`:
```sql
SELECT * FROM __InstanceCreationEvent WITHIN 60 
WHERE TargetInstance ISA 'Win32_Process' 
AND TargetInstance.Name = 'lsass.exe'
```
Alternatively, I can use an absolute timer:
```sql
SELECT * FROM __InstanceModificationEvent WITHIN 60
WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' 
AND TargetInstance.SystemUpTime >= 240 AND TargetInstance.SystemUpTime < 325
```
This triggers the `CommandLineEventConsumer` (my payload) roughly 4 minutes after the system boots, running as SYSTEM, completely independent of user login.

## Deep-Dive Defensive Questions

### Q1: How does an EDR or SOC distinguish between legitimate WMI activity and malicious lateral movement via `Win32_Process::Create`? What are the key process telemetry indicators?
**Expert Answer:**
Distinguishing legitimate WMI from malicious activity relies on parent-child process relationships and command-line arguments.
1. **Parent Process:** Any process spawned via `Win32_Process::Create` will have `WmiPrvSE.exe` (WMI Provider Host) as its parent.
2. **Suspicious Children:** Legitimate IT administration rarely uses WMI to spawn `cmd.exe`, `powershell.exe`, or `rundll32.exe`. If a SOC sees `WmiPrvSE.exe -> cmd.exe -> powershell.exe -enc <base64>`, it is an immediate critical alert.
3. **Network Telemetry:** Correlating the process execution with inbound network connections. Malicious WMI lateral movement will show an inbound network connection on RPC port 135 followed by a high dynamic port, immediately preceding the `WmiPrvSE.exe` spawning the suspicious child process.
4. **Event Logging:** Event ID 4688 (Process Creation) with Command Line auditing enabled is critical to capture the payload. Furthermore, WMI-specific Event ID 5861 (WMI Activity) logs the client IP address, user, and the exact WMI namespace/method called, definitively tying the remote attacker to the local execution.

### Q2: What PowerShell cmdlet would a defender use to hunt for hidden WMI Event Subscriptions, and what specific classes must be queried?
**Expert Answer:**
Defenders cannot rely on standard file system searches to find WMI persistence. They must query the WMI repository directly using PowerShell.
The defender must enumerate three specific WMI classes located in the `ROOT\subscription` namespace:
1. `Get-WmiObject -Namespace root\subscription -Class __EventFilter`
2. `Get-WmiObject -Namespace root\subscription -Class __EventConsumer`
3. `Get-WmiObject -Namespace root\subscription -Class __FilterToConsumerBinding`

A robust hunting script will pull all `FilterToConsumerBindings` and format the output to show the linked Filter (the trigger condition) and the linked Consumer (the malicious payload). 
For modern systems, defenders should use the CIM cmdlets (which use WinRM under the hood):
`Get-CimInstance -Namespace root\subscription -ClassName __FilterToConsumerBinding`
If the output contains consumers invoking `powershell.exe`, heavily obfuscated VBScript, or unknown executables, it indicates compromise.

### Q3: Microsoft introduced AMSI (Anti-Malware Scan Interface). How does AMSI interact with WMI Event Subscriptions, and can an attacker bypass it when executing lateral movement via WMI?
**Expert Answer:**
Historically, WMI was a massive blind spot. However, Microsoft integrated WMI with AMSI in Windows 10/Server 2019. When an `ActiveScriptEventConsumer` executes a VBScript or JScript payload, or a `CommandLineEventConsumer` invokes PowerShell, the script content is intercepted and passed to AMSI for scanning before execution.
**Bypassing it:** 
If an attacker uses WMI lateral movement to simply launch a compiled binary that is NOT an AMSI-integrated script host (e.g., executing a custom C++ executable or a shellcode runner directly via `Win32_Process::Create`), AMSI is not invoked on the payload execution.
Furthermore, if an attacker uses `CommandLineEventConsumer` to launch PowerShell, they can prepend an AMSI bypass to the PowerShell command line (e.g., patching `amsi.dll` in memory using reflection) before executing the main malicious script logic, though modern EDRs heavily monitor for memory patching of AMSI.

## Real-World Attack Scenario

### Fileless Ransomware Deployment via DCOM
During an Incident Response engagement for a manufacturing firm, the IR team discovered that the entire server infrastructure was encrypted simultaneously. The attacker did not use traditional lateral movement tools like PsExec or standard WMI `Win32_Process` because the environment's EDR heavily monitored those behaviors.

Instead, the attacker compromised an IT administrator's workstation and extracted the credentials for a Domain Admin service account.
Knowing that the EDR was blind to complex COM object instantiation, the attacker utilized a PowerShell script to iterate through the domain's server IP list.
For each server, the script remotely instantiated the `MMC20.Application` DCOM object:
`$dcom = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application", $ip))`
They then used the `ExecuteShellCommand` method to invoke PowerShell:
`$dcom.Document.ActiveView.ExecuteShellCommand("powershell.exe", $null, "-w hidden -enc <BASE64_RANSOMWARE_LOADER>", "7")`

Because the payload was executed under the context of `mmc.exe` (a trusted Microsoft management console process), the EDR did not immediately flag the parent-child relationship as malicious. The base64 payload downloaded the ransomware directly into memory and executed it. The IR team only found the vector by correlating anomalous DCOM RPC traffic (Port 135) originating from the IT admin's workstation with Event ID 4688 showing `mmc.exe` spawning `powershell.exe` on the victim servers.

## Chaining Opportunities
*   **Pass-the-Hash (Module 71):** WMI and WinRM fully support NTLM authentication, allowing attackers to use Pass-the-Hash (via tools like `wmiexec.py` or `CrackMapExec`) to move laterally without ever cracking the plaintext password.
*   **Kerberos Tickets (Module 75):** Attackers can inject a TGT into their session and use it to authenticate to WinRM (PowerShell Remoting) or WMI seamlessly.
*   **Living off the Land (Module 60):** WMI and WinRM are prime examples of Living off the Land Binaries/Scripts (LOLBas), utilizing native OS administrative tools to evade detection.

## Related Notes
*   [[04 - Active Directory/AD QnA - Module 71 - NTLM Relay and Pass-The-Hash]]
*   [[04 - Active Directory/AD QnA - Module 75 - Kerberos Attacks and Tickets]]
*   [[04 - Active Directory/AD QnA - Module 60 - Living off the Land Techniques]]
*   [[04 - Active Directory/AD QnA - Module 40 - Privilege Escalation via Windows Services]]
