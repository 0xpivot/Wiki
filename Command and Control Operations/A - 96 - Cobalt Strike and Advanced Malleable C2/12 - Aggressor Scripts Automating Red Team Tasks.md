---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.12 Aggressor Scripts Automating Red Team Tasks"
---

# 96.12 Aggressor Scripts Automating Red Team Tasks

## 1. Executive Summary
Aggressor Script is the powerful, event-driven scripting engine built natively into Cobalt Strike. Based on the Sleep programming language, it empowers Red Team operators and penetration testers to automate repetitive tasks, extend the Cobalt Strike user interface, interact dynamically with the data model, and orchestrate complex offensive workflows. For Threat Hunters and Detection Engineers, understanding the capabilities of Aggressor Scripts is vital because these scripts heavily influence the speed, operational tempo, and artifacts generated during an active network intrusion.

## 2. Architecture and the Sleep Language
A common misconception is that Aggressor scripts are deployed to the compromised target. This is incorrect. Aggressor scripts are executed client-side by the Cobalt Strike client (GUI), not on the Team Server or the target endpoint. When an operator loads an Aggressor script, the client parses the Sleep code and registers hooks, commands, or event listeners.

### The Sleep Language
Sleep is a Java-based scripting language that syntax-wise resembles a hybrid of Perl and Objective-C. It provides seamless integration with Java objects, which is critical since the Cobalt Strike client is a Java application. 

### Key Capabilities:
- **Event-Driven Automation:** Scripts can react immediately to events such as a new beacon checking in, a keystroke logger completing its run, or credentials being parsed by the team server.
- **UI Extension:** Custom menus, popups, customized visual elements, and right-click context dialogs can be added to the Cobalt Strike GUI.
- **Alias Creation:** Complex multi-step operations can be condensed into a single custom command for the Beacon console, ensuring consistency across operations.

## 3. Interacting with the Cobalt Strike Data Model
Cobalt Strike maintains a comprehensive, real-time data model encompassing all compromised hosts, dumped credentials, logged keystrokes, targets, and services. Aggressor scripts can query this data model to make intelligent, conditional automation decisions.

```perl
# Example: Querying all beacons and extracting the internal IP and OS
foreach $beacon (beacons()) {
    println("Active Beacon on: " . $beacon['internal'] . " running " . $beacon['os']);
    
    # Conditional logic based on OS version
    if ($beacon['os'] eq "Windows") {
        # Queue specific Windows commands
    }
}
```

## 4. Automation Workflows

### 4.1 Auto-Reconnaissance
Upon a new beacon check-in, an Aggressor script can automatically queue a series of situational awareness commands. This significantly reduces the time between initial compromise and data collection, operating much faster than a human operator could type.

### 4.2 Auto-Persistence
Scripts can be designed to automatically evaluate the privilege level of a new beacon. If the beacon is running as `NT AUTHORITY\SYSTEM` or High Integrity, the script can autonomously deploy a stealthy persistence mechanism (e.g., creating a scheduled task, modifying the registry, or backdooring a service).

## 5. Architecture Diagram: Event-Driven Automation

```text
+-------------------------------------------------------------------------+
|                          Cobalt Strike Client                           |
|                                                                         |
|  +--------------------+       Event Trigger      +-------------------+  |
|  |   Aggressor Engine | <----------------------- |  Event Bus        |  |
|  |  (Sleep Script)    |                          | (New Beacon, etc) |  |
|  +--------------------+                          +-------------------+  |
|           |                                                ^            |
|           | 1. Auto-Recon Commands Queued                  |            |
|           v                                                |            |
|  +--------------------+                                    |            |
|  |  Beacon Console    |------------------------------------+            |
|  +--------------------+                                                 |
+----------|--------------------------------------------------------------+
           | 2. Commands sent to Team Server via TLS
           v
+-------------------------------------------------------------------------+
|                            Team Server                                  |
|  (Stores taskings in the database until beacon checks in)               |
+-------------------------------------------------------------------------+
           | 3. Tasks pulled by Beacon (HTTPS/DNS/SMB)
           v
+-------------------------------------------------------------------------+
|                        Compromised Endpoint                             |
|  > whoami /groups                                                       |
|  > netstat -ano                                                         |
|  > ipconfig /all                                                        |
+-------------------------------------------------------------------------+
```

## 6. Threat Hunting and Detection Engineering
Because Aggressor scripts run exclusively on the operator's client machine, defenders will never see the `.cna` (Cobalt Strike Node Script) file itself on a compromised endpoint. Instead, detection must focus entirely on the *behavior* produced by the automation.

### Detection Strategies:
- **Speed of Execution:** Human operators type at a specific cadence. Aggressor scripts can queue dozens of commands in milliseconds. Detecting a rapid succession of discovery commands (`whoami`, `ipconfig`, `net localgroup`, `nltest`, `systeminfo`) originating from the exact same process within a sub-second timeframe is a massive indicator of scripted automation.
- **Command Line Signatures:** Scripts often use hardcoded, standard command-line arguments that lack the variability of human input over time.
- **Predictable Action Chains:** If every new endpoint compromised follows the exact same sequence of actions (e.g., process injection -> discovery -> credential dumping -> sleep modification), behavioral analytics can flag this chain.

### KQL Query: Rapid Sequential Discovery Commands
```kusto
DeviceProcessEvents
| where TimeGenerated > ago(1h)
| where FileName in ("whoami.exe", "ipconfig.exe", "net.exe", "nltest.exe", "systeminfo.exe", "tasklist.exe", "arp.exe")
| summarize CommandCount = count(), CommandSet = make_set(ProcessCommandLine), TimeRange = max(TimeGenerated) - min(TimeGenerated) by InitiatingProcessFileName, DeviceName, bin(TimeGenerated, 5s)
| where CommandCount > 4 and TimeRange < 2s // Extremely fast execution
| project TimeGenerated, DeviceName, InitiatingProcessFileName, CommandCount, CommandSet, TimeRange
| order by TimeGenerated desc
```

## 7. Sample Aggressor Script: Auto-Enumerate
Below is an example of an Aggressor script that intercepts the `beacon_initial` event to automatically enumerate the environment without user interaction.

```perl
# Hook into the initial check-in of a new Beacon
on beacon_initial {
    local('$bid $user $isadmin');
    $bid = $1;
    
    # Extract metadata
    $user = binfo($bid, "user");
    $isadmin = binfo($bid, "isadmin");
    
    blog($bid, "Automation Triggered: Starting initial enumeration for " . $user);
    
    # Queue lightweight situational awareness
    bexecute_assembly($bid, "script/Seatbelt.exe", "System");
    bshell($bid, "ipconfig /all");
    bshell($bid, "netstat -anp tcp");
    
    # If high integrity, automatically dump hashes
    if ($isadmin eq "true" || $user eq "SYSTEM") {
        blog($bid, "High Integrity detected. Executing LogonPasswords...");
        bexecute_assembly($bid, "script/Rubeus.exe", "triage");
        blogonpasswords($bid);
    }
}
```
From a hunting perspective, this means the beacon process will immediately spawn `.NET` assemblies and `cmd.exe` sub-processes in an identical pattern every time this alias is invoked or a new system is popped.

## 8. Real-World Attack Scenario

### The Setup
An attacker leverages a valid credential to log into an exposed VPN portal. They deploy a Cobalt Strike beacon to an engineering workstation. The Red Team operator, monitoring multiple campaigns simultaneously, has an Aggressor script loaded named `Auto-Infect-And-Pivot.cna`.

### The Execution
1. The beacon executes on the workstation and checks in to the Team Server.
2. The Cobalt Strike client fires the `beacon_initial` event locally.
3. The `Auto-Infect-And-Pivot.cna` script catches this event. It parses the metadata and identifies that the beacon is running in a High Integrity process context.
4. The script automatically executes `hashdump` and queues a memory-safe credential dumper.
5. Simultaneously, it queues a BOF (Beacon Object File) to query the domain controller for active Domain Admins.
6. All of this occurs within 1.5 seconds of the initial check-in, long before the human operator has even clicked on the beacon in the GUI.

### The Defender's View
The EDR agent on the compromised workstation triggers a critical alert for rapid execution of credential access techniques. The timeline shows `lsass.exe` memory access followed immediately by LDAP queries originating from the beacon process (`rundll32.exe`). The sheer speed of execution allows the SOC to categorize the activity as highly automated, likely originating from a C2 framework's scripting engine rather than manual hands-on-keyboard activity.

## 9. Developing Defensive Aggressor Scripts
Interestingly, Aggressor scripts can be utilized defensively. Blue teams and purple teams testing their detection coverage can write scripts to continuously blast known Indicators of Compromise (IOCs) or perform specific API calls across a fleet of test machines to ensure their EDR, Sysmon, and SIEM solutions are generating the appropriate alerts.

## 10. MITRE ATT&CK Mapping
- **TA0002 Execution**
- **T1059 Command and Scripting Interpreter:** Leveraging scripting for automation.
- **TA0007 Discovery**
- **T1087 Account Discovery:** Automated queries for local and domain accounts.
- **T1049 System Network Connections Discovery:** Automated `netstat` and `arp` queries.

## 11. Chaining Opportunities
- Aggressor scripts frequently automate the deployment of Elevate Kits to automatically escalate privileges on standard user beacons, as discussed in [[11 - Elevate Kit for Privilege Escalation]].
- Automation can orchestrate complex lateral movement workflows, parsing newly found credentials and automatically attempting SMB connections across /24 subnets. See [[14 - Lateral Movement and Pivoting with Cobalt Strike]].
- Scripts can be used to dynamically load and configure evasive artifacts before injection, linking directly into [[15 - EDR Evasion with Custom Cobalt Strike Kits]].

## 12. Related Notes
- [[13 - Cobalt Strike BOFs Beacon Object Files Development]]
- [[Automated Post-Exploitation Frameworks]]
- [[Red Team Infrastructure Setup]]
- [[SIEM Behavioral Analytics]]
- [[Sleep Programming Language Syntax]]
