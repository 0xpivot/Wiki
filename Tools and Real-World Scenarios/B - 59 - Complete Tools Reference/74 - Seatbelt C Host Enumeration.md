---
tags: [tools, privesc, enumeration, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.74 Seatbelt C Host Enumeration"
---

# Seatbelt: C# Host Enumeration

## 1. Introduction and Core Philosophy

`Seatbelt` is an advanced, C#-based post-exploitation framework focused on system situational awareness and local host enumeration. Developed by the SpecterOps team as part of the GhostPack toolset, Seatbelt differs significantly in philosophy from tools like WinPEAS. 

While WinPEAS is designed as a broad-spectrum "vulnerability scanner" that actively hunts for specific privilege escalation paths and highlights them in red, Seatbelt is described as an "information collection" tool. It gathers a highly structured, comprehensive dataset about the host's configuration, defensive posture, and current state. It assumes the operator has the knowledge to analyze this raw intelligence to formulate an attack path, rather than explicitly pointing out vulnerabilities. This makes Seatbelt highly favored in advanced Red Team engagements where stealth and OPSEC are prioritized over automated exploitation.

## 2. ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                            Seatbelt Execution Model                               |
|                                                                                   |
|  +-----------------+       +---------------------------------------------------+  |
|  |     C2 Server   |       |             Memory-Safe Execution                 |  |
|  |   (Cobalt Strike)------>| Seatbelt.exe is loaded reflectively into memory   |  |
|  +-----------------+       | via execute-assembly. No disk artifacts created.  |  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |               Command Dispatcher                  |  |
|                            | Parses arguments (e.g., -group=system, -q)        |  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |               Enumeration Modules                 |  |
|  +---------------+         | - AntiVirus/EDR discovery (WMI queries)           |  |
|  | Windows APIs  |<--------| - LAPS configuration checks                       |  |
|  +---------------+         | - Network connections & DNS Cache                 |  |
|  +---------------+         | - Non-standard services & autoruns                |  |
|  | WMI Providers |<--------| - PowerShell history & AMSI status                |  |
|  +---------------+         | - Browser artifacts & vault credentials           |  |
|  +---------------+         | - Active Directory domain trust info              |  |
|  |   Registry    |<--------| - Token privileges (SeImpersonate, etc.)          |  |
|  +---------------+         +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |               Output Formatting                   |  |
|                            | Organizes data logically without aggressive       |  |
|                            | color-coding. Presents "the state of the union."  |  |
|                            +---------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 3. Deployment and OPSEC

Seatbelt is almost exclusively designed to be executed in-memory. Because it relies heavily on native Windows APIs rather than dropping scripts or executing shell commands (like `net user` or `sc query`), its execution profile is significantly stealthier than traditional batch scripts.

**Execution via Cobalt Strike (execute-assembly):**
The standard deployment mechanism involves using the `execute-assembly` command within a C2 framework. This loads the compiled `Seatbelt.exe` binary over the network directly into the memory space of a sacrificial process, completely bypassing static disk-based AV signatures.
```text
beacon> execute-assembly /path/to/Seatbelt.exe -group=system
```

**Compilation:**
Operators must compile Seatbelt themselves using Visual Studio, ensuring they use the correct .NET framework version for the target environment. Pre-compiled binaries are intentionally not provided by the developers to prevent script-kiddie abuse and encourage custom compilation.

## 4. Command Groups and Targeted Enumeration

Seatbelt uses specific modules. Running `Seatbelt.exe` without arguments is not recommended as it runs all modules, generating excessive noise. Instead, operators use command groups or specify individual modules.

### 4.1 System Group (`-group=system`)
Provides baseline situational awareness. What kind of machine is this? What defenses are in place?
- **`AntiVirus`:** Uses WMI (`root\SecurityCenter2`) to enumerate installed AV/EDR products. Crucial for determining payload types.
- **`LAPS`:** Checks registry keys to see if Local Administrator Password Solution is active, dictating lateral movement strategy.
- **`TokenPrivileges`:** Enumerates the exact tokens held by the current user session (e.g., `SeDebugPrivilege`).
- **`UAC`:** Checks User Account Control settings to determine if UAC bypass techniques are required or possible.
- **`WindowsDefender`:** Extracts specific configuration details, exclusions, and real-time protection status of Defender.

### 4.2 User Group (`-group=user`)
Focuses on artifacts specific to the currently logged-on user.
- **`CloudCredentials`:** Searches common locations for AWS, Azure, and GCP token files.
- **`CredEnum`:** Enumerates credentials saved in the Windows Vault.
- **`MasterKeys`:** Locates DPAPI Master Keys, which are essential if the operator intends to decrypt Chrome cookies, saved passwords, or certificates later.
- **`SlackDownloads` / `ChromeHistory`:** Extracts user activity data which can reveal internal portal URLs, project names, or downloaded configuration files.

### 4.3 Misc Group (`-group=misc`)
More aggressive or noisy checks that are not part of standard triage.
- **`NonstandardProcesses`:** Filters out known good Windows processes to highlight unique applications or potential security agents.
- **`TCPConnections`:** Maps internal network connectivity.

### 4.4 Specific Module Execution
For highly targeted surgical strikes, specific modules are invoked.
```text
Seatbelt.exe SysmonConfig
Seatbelt.exe PowerShellHistory
```
The `SysmonConfig` module is particularly valuable. It parses the active Sysmon XML configuration from the registry to tell the attacker exactly which Event IDs are being logged and which are being ignored, allowing the attacker to tailor their actions to remain invisible to the SIEM.

## 5. Analyzing Seatbelt Output

The output of Seatbelt is raw intelligence. The attacker must correlate the findings.

**Scenario A: Evasion**
1. Seatbelt output from `AntiVirus` reveals CrowdStrike Falcon is installed.
2. Seatbelt output from `SysmonConfig` reveals Event ID 1 (Process Creation) is logged, but Event ID 8 (CreateRemoteThread) is excluded for certain applications.
3. *Analysis:* The attacker knows they cannot drop executables to disk (CrowdStrike) and should utilize process injection via `CreateRemoteThread` into the excluded applications to avoid Sysmon logging.

**Scenario B: Credential Harvesting**
1. Seatbelt output from `TokenPrivileges` shows `SeBackupPrivilege`.
2. Seatbelt output from `LAPS` shows LAPS is *not* installed.
3. *Analysis:* The attacker uses their `SeBackupPrivilege` to extract the `SAM` hive, crack the local administrator password, and reuse that password across the network since LAPS is not randomizing it.

**Scenario C: Situational Awareness**
1. Seatbelt output from `DotNet` shows .NET Framework 2.0 is installed, but 4.0 is missing.
2. *Analysis:* The attacker must ensure any subsequent C# assemblies loaded via `execute-assembly` are compiled for .NET 2.0.

## 6. Comparison with WinPEAS

| Feature | WinPEAS | Seatbelt |
| :--- | :--- | :--- |
| **Primary Goal** | Automated Privilege Escalation Discovery | Situational Awareness / Reconnaissance |
| **Output Style** | Color-coded, heavily editorialized (red = exploit) | Raw data, structured, objective |
| **Implementation** | Scripts (.bat, .ps1, C# executable) | Pure C# (.NET assembly) |
| **Execution** | Often run from disk or piped into memory | Exclusively `execute-assembly` via C2 |
| **Target Audience** | Penetration Testers, OSCP candidates | Red Teamers, Advanced APT simulation |
| **Stealth** | Extremely noisy, highly signatured | Moderate to Stealthy, customizable |

## 7. Chaining Opportunities
- **[[EDR Evasion Techniques]]:** Seatbelt's primary use case is mapping the defensive terrain to inform evasion strategies.
- **[[DPAPI Exploitation]]:** Seatbelt locates the Master Keys necessary for tools like Mimikatz or SharpDPAPI to decrypt secrets.
- **[[Cobalt Strike Execution Methods]]:** Deep dive into how `execute-assembly` safely loads Seatbelt into memory.
- **[[Sysmon Configuration Analysis]]:** Understanding the output of Seatbelt's `SysmonConfig` module to find logging blind spots.

## 8. Related Notes
- [[73 - WinPEAS Complete Output Analysis]]: Contrast this with Seatbelt's approach.
- [[Windows Situational Awareness]]: Broader strategies for understanding a compromised host.
- [[GhostPack Toolkit Overview]]: Contextualizing Seatbelt within the larger SpecterOps ecosystem.
