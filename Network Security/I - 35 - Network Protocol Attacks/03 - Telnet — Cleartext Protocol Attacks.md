---
tags: [telnet, cleartext, sniffing, mitm, network]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.03 Telnet"
---

# Telnet — Cleartext Protocol Attacks

## 1. Introduction to Telnet
Telnet (Teletype Network) is one of the oldest network protocols, developed in 1969 (RFC 15). It provides a bidirectional interactive text-oriented communication facility using a virtual terminal connection. It operates on the client-server model, traditionally running over **TCP Port 23**.

For decades, Telnet was the standard tool for remote administration of servers, routers, switches, and mainframes. However, its fundamental design contains a fatal security flaw for modern networks: **it completely lacks encryption.**

Every single byte of data transmitted during a Telnet session—including the username, the password, the commands typed by the administrator, and the resulting output from the server—is sent across the network in plain, readable cleartext. Because of this, Telnet is considered highly insecure and has been almost entirely deprecated in enterprise environments, replaced by Secure Shell (SSH).

### 1.1 The Telnet Protocol Mechanics
Telnet operates using in-band signaling. Protocol control information is interleaved with the actual data. Telnet commands are prefixed by the "Interpret as Command" (IAC) character, which is the byte `255` (0xFF).
When a client connects to a server, they negotiate options (like terminal echoing, terminal type, and window size) using a series of `DO`, `DONT`, `WILL`, and `WONT` commands.

## 2. ASCII Diagram: Telnet Interception Architecture

```text
    [Legitimate Admin]                      [Telnet Server (Router/Switch)]
           |                                             |
           |----(1) Telnet Auth Request (TCP 23)-------->|
           |       User: admin                           |
           |       Pass: SuperSecret123                  |
           |                                             |
           |                                             |
           |      [Attacker Network Sniffer]             |
           |                  |                          |
           |<---------(2) ARP Spoofing (MITM)----------->|
           |                  |                          |
           |                  V                          |
           |        (3) Attacker captures ALL            |
           |            traffic in cleartext via         |
           |            Wireshark/tcpdump. Extracts      |
           |            credentials immediately.         |
```

## 3. Cleartext Sniffing and Eavesdropping
Because Telnet uses no encryption, any actor capable of observing the network traffic can read the contents of the session.

**The Mechanics:**
In modern switched networks, simply plugging in a packet sniffer won't capture traffic not destined for the attacker's machine. Therefore, attackers typically employ Man-in-the-Middle (MITM) techniques, most commonly **ARP Spoofing (ARP Poisoning)**, to force the victim's network traffic to flow through the attacker's machine.

**The Attack:**
1. The attacker uses a tool like `arpspoof` or `Ettercap` to broadcast forged ARP messages on the local area network.
2. These messages deceive the victim's computer into believing the attacker's MAC address is the gateway's MAC address, and deceive the gateway into believing the attacker is the victim.
3. Once the traffic is routed through the attacker's machine, the attacker uses packet capture tools to passively record the Telnet session.

**Exploitation Capture:**
Running a simple tcpdump filter:
```bash
tcpdump -i eth0 port 23 -A
```
The `-A` flag prints each packet in ASCII format. Because Telnet sends characters one by one as they are typed, the attacker will see the username and password stream directly to their terminal. Wireshark simplifies this further with the "Follow TCP Stream" feature, reconstructing the entire session flawlessly.

## 4. Credential Harvesting and Replay Attacks
Once credentials are captured from a cleartext Telnet session, the attacker possesses the exact keys used by the administrator.

### 4.1 Direct Credential Reuse
The attacker can immediately initiate their own Telnet session using the stolen credentials to gain administrative access to the router, switch, or server. Because network administrators frequently reuse passwords across multiple systems, a single captured Telnet login can often compromise dozens of other devices on the network.

### 4.2 Session Hijacking
While more complex, an attacker actively performing a MITM attack can theoretically hijack the active TCP session. By predicting TCP sequence numbers, the attacker can inject their own commands into the established Telnet session, executing commands with the privileges of the currently logged-in administrator, completely bypassing the authentication phase.

## 5. Brute Force and Dictionary Attacks
Like SSH and FTP, Telnet is heavily targeted by automated brute-force attacks, particularly targeting legacy systems, IoT devices, and neglected infrastructure.

**The Mechanics:**
Many legacy devices ship with default credentials (e.g., `admin:admin`, `root:root`, `cisco:cisco`) that are never changed by the deployment team. Attackers scan massive ranges of public IPs for Port 23 and systematically attempt these default lists.

**The Risk:**
The Mirai botnet famously exploited this exact vector. It scanned the internet for IoT devices (like IP cameras and DVRs) running Telnet with hardcoded default passwords. It infected millions of devices, assembling them into a massive botnet used to launch unprecedented Distributed Denial of Service (DDoS) attacks.

**Exploitation via Hydra:**
```bash
hydra -l admin -P /usr/share/wordlists/mirai_passwords.txt telnet://192.168.1.1
```

## 6. Vulnerabilities in Telnet Server Implementations
Beyond the protocol's lack of encryption, specific Telnet server software has suffered from implementation bugs.

### 6.1 Buffer Overflows
Legacy Telnet daemons (like `telnetd` in older Unix systems) have historically been vulnerable to buffer overflows. By sending excessively long strings during option negotiation or login, an attacker could overwrite memory and achieve Remote Code Execution (RCE) with the privileges of the Telnet service (often root).

### 6.2 Environment Variable Manipulation
Some ancient Telnet implementations allowed clients to pass environment variables to the server during negotiation. By passing specifically crafted environment variables (like `LD_PRELOAD`), an attacker could force the server to load malicious libraries, bypassing authentication or executing code.

## 7. Defensive Strategies & Mitigation

### 7.1 Complete Deprecation (The Only True Fix)
The absolute best practice regarding Telnet is simple: **Do not use it.**
Telnet should be entirely disabled and uninstalled across the entire infrastructure. It must be replaced with Secure Shell (SSH), which provides encrypted communications, strong host verification, and robust authentication mechanisms.

### 7.2 Legacy System Containment
If Telnet *must* be used because legacy hardware cannot support SSH (e.g., ancient industrial control systems or vintage mainframes):
- **Strict Network Isolation:** Place the legacy system on a highly isolated, air-gapped VLAN.
- **VPN / IPSec Tunnels:** Force all administrative traffic to flow through an encrypted VPN or IPSec tunnel before reaching the isolated VLAN. This effectively wraps the cleartext Telnet traffic in an encrypted outer layer during transit.
- **Strict ACLs:** Implement rigorous Access Control Lists (ACLs) on routers and firewalls to ensure that only specific, designated administrative jump boxes can even attempt to connect to Port 23.

### 7.3 Securing Authentication on Legacy Systems
If Telnet is unavoidable:
- **Change Default Credentials:** Immediately change all default vendor passwords.
- **Implement Long, Complex Passwords:** Use exceptionally long passphrases to defend against brute-force attacks.
- **Enable Login Banners:** Ensure a legal warning banner is displayed before the login prompt to deter unauthorized access and satisfy legal compliance requirements.

## 8. Identifying Telnet in the Wild
Penetration testers frequently discover forgotten Telnet services during external and internal footprinting.

**Nmap Scanning for Telnet:**
```bash
nmap -sV -p 23 192.168.1.0/24
```
**Nmap Scripting Engine (NSE) Brute Force:**
```bash
nmap -p 23 --script telnet-brute --script-args userdb=users.txt,passdb=pass.txt 192.168.1.1
```

## 9. Chaining Opportunities
- **ARP Spoofing to Credential Capture:** Use Responder or Ettercap to MITM the network, sniff a network admin's Telnet session to a core router, and capture the 'enable' password. -> [[02 - Man-in-the-Middle Attacks]]
- **Default Credential Brute Force to Botnet Deployment:** Scan a subnet for Telnet, guess default IoT credentials, and deploy a custom payload to utilize the device for lateral movement. -> [[05 - IoT Security]]
- **Cleartext Password to Password Spraying:** Once a password is sniffed over Telnet, use that exact password to spray against the organization's Active Directory or VPN endpoints, assuming password reuse. -> [[12 - Password Cracking Strategies]]

## 10. Related Notes
- [[02 - SSH — Brute Force, Weak Keys, Version Vulns]]
- [[01 - FTP — Anonymous Login, Bounce Attack, Credential Brute Force]]
- [[02 - Man-in-the-Middle Attacks]]
- [[01 - Nmap Port Scanning Techniques]]

---
*End of Note*
