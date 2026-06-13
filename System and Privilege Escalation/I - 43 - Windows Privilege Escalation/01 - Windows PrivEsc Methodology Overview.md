---
tags: [windows, privesc, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.01 Windows PrivEsc Methodology Overview"
---

# Windows Privilege Escalation Methodology Overview

## Introduction

Windows Privilege Escalation is a critical phase in the penetration testing and red teaming lifecycle. Once initial access is achieved—often as a low-privileged domain user, a compromised service account (like `NT AUTHORITY\Local Service` or an IIS AppPool identity), or via a web shell—the immediate objective shifts toward obtaining administrative rights. In the Windows ecosystem, this translates to elevating privileges to a Local Administrator, or ideally, the ultimate goal: `NT AUTHORITY\SYSTEM`.

Privilege escalation occurs when a vulnerability, design flaw, or configuration oversight allows an attacker to execute code or perform actions under the context of an account with higher privileges. The methodology is structured and systematic. Rather than firing exploits blindly, a mature approach emphasizes exhaustive enumeration. The foundational principle is: **"Enumeration is the key to privilege escalation."** Without a deep understanding of the host environment, an attacker is essentially guessing, which often leads to instability, system crashes, or immediate detection by Endpoint Detection and Response (EDR) solutions.

## The Core Foundations of Windows Access Control

To understand how to escalate privileges, one must first grasp the underlying mechanisms of Windows Access Control. Windows handles security boundaries using a combination of subjects, objects, and access checks.

### Security Identifiers (SIDs)
Every user, group, and computer in a Windows domain is assigned a unique Security Identifier (SID). SIDs are immutable; even if a user account is renamed, the SID remains constant. Well-known SIDs are predefined and standard across all Windows installations. For example:
- `S-1-5-18` represents `Local System` (`NT AUTHORITY\SYSTEM`).
- `S-1-5-19` represents `NT Authority\Local Service`.
- `S-1-5-20` represents `NT Authority\Network Service`.
- `S-1-5-32-544` represents the built-in Administrators group.
- `S-1-5-32-545` represents the built-in Users group.

### Access Control Lists (ACLs) and Access Control Entries (ACEs)
Securable objects in Windows (files, folders, registry keys, services, named pipes, etc.) possess a Security Descriptor. The most relevant component of this descriptor is the Discretionary Access Control List (DACL). 
- A **DACL** is essentially a list of permissions.
- Each entry in a DACL is an **Access Control Entry (ACE)**. 
- An ACE dictates whether a specific SID (user or group) is allowed or denied specific types of access (e.g., Read, Write, Execute, Full Control).

During an access check, the Windows Security Reference Monitor (SRM) compares the user's access token against the object's DACL. If the token holds SIDs that are explicitly granted the requested permissions by the ACEs (and not explicitly denied), access is granted. Misconfigurations in these DACLs are the root cause of many privilege escalation vectors.

### The Anatomy of a Windows Process Token
When a user logs into Windows, the Local Security Authority (LSA) authenticates the user and generates an Access Token. This token is then attached to the `userinit.exe` process and inherited by all subsequent child processes (like `explorer.exe`). The token contains:
- The user's SID.
- The SIDs of all groups the user belongs to.
- The privileges assigned to the user (e.g., `SeBackupPrivilege`, `SeImpersonatePrivilege`).
- The Default DACL applied to new objects created by the process.
- The token's Integrity Level (IL) - Low, Medium, High, or System.

Privilege escalation essentially means obtaining a token with a higher Integrity Level and more powerful SIDs/privileges.

## Privilege Escalation Attack Surface

The attack surface for local privilege escalation on Windows can be broadly categorized into several core domains. 

1.  **Service Configuration Flaws:**
    Services execute under high-privileged accounts (often SYSTEM) in the background. If a low-privileged user can manipulate the service's execution path, its configuration, or the binary it executes, they can force the service to run malicious code. Examples include Unquoted Service Paths, Weak Service Permissions, and Modifiable Service Binaries.
    
2.  **Registry Misconfigurations:**
    The Windows Registry holds critical configuration data. If high-privileged processes read configuration data from registry keys that are writable by low-privileged users, it can lead to command execution. The `AlwaysInstallElevated` policy, AutoRun keys, and Autologon credentials are prime examples.

3.  **File System Flaws and Search Order:**
    Overly permissive folders, especially those in the `PATH` environment variable or containing executable binaries, can be exploited via DLL Hijacking or Search Order Abuse. Applications that do not explicitly define the absolute path to their dependencies might load malicious libraries dropped by an attacker.

4.  **Token Privileges:**
    Certain privileges assigned to a user token are inherently dangerous and can be leveraged directly to escalate privileges. Notable examples include `SeImpersonatePrivilege` (exploitable via the Potato family of attacks like PrintSpoofer, RoguePotato, JuicyPotato), `SeAssignPrimaryTokenPrivilege`, `SeBackupPrivilege`, `SeRestorePrivilege`, and `SeTakeOwnershipPrivilege`.

5.  **Stored Credentials and Passwords:**
    Users and administrators often leave passwords in clear text across the filesystem. This includes unattended installation files (e.g., `unattend.xml`, `sysprep.inf`), PowerShell transcripts, configuration files, and the Windows Credential Manager. Searching for passwords is the lowest-hanging fruit but often the most rewarding.

6.  **Kernel Vulnerabilities:**
    When misconfigurations are absent, attackers often turn to kernel exploits. These leverage memory corruption, integer overflows, or logical bugs in `win32k.sys`, third-party device drivers, or the NT OS kernel to execute code in Ring 0. Examples include `CVE-2021-36934` (SeriousSAM), `CVE-2023-21768` (Afd.sys LPE), or various Advanced Local Procedure Call (ALPC) bugs.

## Privilege Escalation Methodology Flow

The general workflow for approaching Windows Privilege Escalation follows a cyclical pattern of Enumeration, Analysis, Exploitation, and Post-Exploitation.

```text
+-------------------------------------------------------------------------+
|                    WINDOWS PRIVILEGE ESCALATION WORKFLOW                |
+-------------------------------------------------------------------------+

[ 1. INITIAL RECONNAISSANCE ]
      |
      +---> System Info (OS version, Architecture, Applied Patches)
      |
      +---> User & Token Privileges (whoami /all, local groups)
      |
      +---> Network Configuration (netstat, arp, ipconfig)
      
             |
             v
             
[ 2. AUTOMATED & MANUAL ENUMERATION ]
      |
      +---> Run Automated Checkers: WinPEAS / PowerUp / Seatbelt
      |
      +---> Manual checks: Services (accesschk), Registry (reg query)
      |
      +---> Credential hunting: Filesystem search, DPAPI, SAM backups

             |
             v
             
[ 3. ANALYSIS & VULNERABILITY IDENTIFICATION ]
      |
      +---> Correlate findings (e.g., writable folder + service path)
      |
      +---> Cross-reference missing OS patches with exploit databases
      |
      +---> Identify exploitable token privileges

             |
             v
             
[ 4. EXPLOITATION & WEAPONIZATION ]
      |
      +---> Craft targeted payload (msfvenom, custom compile C++/C#)
      |
      +---> Stage payload in accessible directory (e.g., C:\Temp)
      |
      +---> Trigger execution (Restart service, reboot, wait for task)

             |
             v
             
[ 5. VERIFICATION & POST-EXPLOITATION ]
      |
      +---> Verify Administrator/SYSTEM shell (whoami)
      |
      +---> Establish persistence (Scheduled tasks, backdoors)
      |
      +---> Dump Hashes (LSASS memory dump, SAM/SYSTEM hives)
```

### Phase 1: Information Gathering
The first step upon obtaining a shell is to understand the context of your execution environment.
- **Who are you?** Understand your user context, the groups you belong to, and your explicit token privileges. 
- **Where are you?** Understand the system architecture (32-bit vs 64-bit is crucial for compiling exploits), the hostname, OS version, and network topology.
- **What is running?** Enumerate processes, scheduled tasks, and services. Knowing what is running helps identify potential target processes for injection or hijacking.

### Phase 2: Automated and Manual Enumeration
Modern engagements rely heavily on automated tools to accelerate the enumeration process. However, manual enumeration is equally crucial because automated tools can miss subtle misconfigurations, or EDR/AV might actively block tools like WinPEAS.

**Automated Tools:**
- **WinPEAS (Windows Privilege Escalation Awesome Scripts):** An expansive script/binary that checks for almost every known privesc vector. It is highly noisy but extremely thorough. It color-codes output to highlight high-probability vectors.
- **PowerUp.ps1:** A famous PowerShell module from the Empire framework focused on service, registry, and file-based misconfigurations. It includes functions like `Invoke-AllChecks` and also functions to exploit findings directly (e.g., `Invoke-ServiceAbuse`).
- **Seatbelt:** A C# tool from the GhostPack project that performs "safety checks" which are inherently useful for offensive operations. Seatbelt focuses on gathering data rather than explicit exploitation and is generally considered more opsec-safe than WinPEAS.
- **JAWS (Just Another Windows (Enum) Script):** A PowerShell script that is lighter than WinPEAS and useful in restricted environments where execution policies or AV might flag larger binaries.

**Manual Checks:** 
Relying on built-in tools (Living Off The Land - LOTL) minimizes the footprint and avoids triggering static AV signatures. Proficiency with `cmd.exe`, `PowerShell`, `wmic`, `icacls`, `sc`, and `reg` is mandatory for a skilled operator.

### Phase 3: Exploitation and Weaponization
Once a vulnerability is identified, the next phase is weaponization. This involves creating a payload tailored specifically to the vulnerability and the system architecture.

**Payload Types:**
- **Reverse Shells:** The target machine connects back to the attacker machine (e.g., via Netcat or Metasploit).
- **Bind Shells:** The target machine opens a listening port for the attacker to connect to. Often blocked by local Windows Firewalls.
- **Command Execution:** Executing a specific command without an interactive shell, such as adding a new user to the local Administrators group (`net localgroup Administrators attacker /add`).

**Payload Formats:**
Depending on the vector, the payload might need to be a standard `.exe` file, a `.dll` with specific exported functions, a Windows Installer `.msi`, or a raw script. Furthermore, a payload replacing a Windows Service *must* implement the Service Control Handler functions, otherwise the Service Control Manager will terminate it prematurely.

**Execution Triggers:**
Triggering the vulnerability requires understanding how the vulnerable component starts. This could require manually restarting a service (if you have the rights), waiting for a scheduled task to execute (requiring patience), or rebooting the machine entirely (which is highly disruptive and noticeable).

### Phase 4: Verification and Post-Exploitation
After execution, it is critical to verify the privilege escalation. A simple `whoami` or `whoami /groups` confirms whether the new shell operates under the intended high-privileged context. 

If the exploit fails, rigorous troubleshooting is required:
- Are there file locks preventing you from overwriting a binary?
- Did you compile the payload for the correct architecture (x86 vs x64)?
- Did the Service Control Manager kill your payload before it could spawn a shell because it didn't respond to service requests?
- Is an Antivirus intercepting your payload upon execution?

Once elevated, the attacker moves into the Post-Exploitation phase, focusing on credential harvesting (dumping SAM, LSASS), lateral movement, and establishing long-term persistence.

## Common Pitfalls During Escalation

1.  **Architecture Mismatches:** Running a 32-bit exploit or payload on a 64-bit architecture (or vice versa) is the most common reason for exploit failure. Always verify via `systeminfo`.
2.  **Dropping Payloads to Disk:** Writing compiled binaries directly to disk (especially standard Metasploit payloads) is highly likely to be flagged by Windows Defender. Using in-memory execution or heavily obfuscated payloads is necessary in modern environments.
3.  **Crashing Services:** When replacing service binaries or performing DLL hijacking, failing to proxy the original functionality can cause the service (or the entire application) to crash, alerting system administrators.
4.  **Ignoring the Basics:** Attackers often rush to look for kernel exploits while completely ignoring plain-text passwords sitting in the user's `Documents` folder or in sticky notes files. Always start with the simplest vectors.

## Defensive Perspectives

Understanding privilege escalation is not solely an offensive endeavor. From a defensive standpoint, neutralizing these vectors involves strict adherence to the Principle of Least Privilege and robust configuration management.

- **Patch Management:** Regularly updating the OS and third-party applications is the primary defense against kernel and application-level exploits.
- **Configuration Management:** Using Group Policy Objects (GPOs) to enforce secure service permissions, restrict registry settings (disabling `AlwaysInstallElevated`), and standardize file system ACLs.
- **Credential Hygiene:** Disabling Autologon, clearing plain-text credentials from scripts, prohibiting password storage in scripts, and utilizing robust secret management solutions (like LAPS for local admin passwords).
- **Endpoint Protection:** Deploying EDR solutions capable of detecting anomalous behavior, such as a web server process spawning `cmd.exe` or a low-privileged user modifying a service binary or dropping an unfamiliar DLL into a system path.
- **Auditing and Logging:** Ensuring PowerShell Script Block Logging, Command Line Auditing, and detailed file share auditing are enabled and forwarded to a SIEM.

## Conclusion

Windows Privilege Escalation is a vast and deeply technical domain. The methodology outlined here provides a structured approach, but adaptability in the field is paramount. As operating systems evolve and defensive technologies advance, new escalation techniques emerge while older ones are patched. The core principle, however, remains unchanged: meticulous, exhaustive enumeration and a profound understanding of Windows internals are the true keys to successful privilege escalation.

## Chaining Opportunities
- **Initial Access:** The methodology kicks in immediately following successful exploitation via [[02 - Web Application Exploitation]], phishing, or compromising a host via password spraying.
- **Lateral Movement:** Once SYSTEM is achieved, the next logical step is dumping credentials (e.g., via Mimikatz or a specialized BOF) to facilitate [[Lateral Movement Overview]] across the Active Directory environment.
- **Persistence:** Elevated privileges are generally required to establish robust [[Windows Persistence Mechanisms]] (e.g., creating high-privileged scheduled tasks, installing malicious services, or modifying registry run keys).

## Related Notes
- [[02 - Enumerating Windows System Info]]
- [[03 - Unquoted Service Paths]]
- [[04 - Weak Service Permissions]]
- [[05 - Modifiable Service Binaries]]
- [[06 - DLL Hijacking]]
- [[07 - DLL Search Order Abuse]]
- [[08 - AlwaysInstallElevated]]
