---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.19 OSI Model — 7 Layers"
---

# 01.19 — OSI Model — 7 Layers

## What is it?

The **OSI Model (Open Systems Interconnection)** is a conceptual framework that divides network communication into 7 distinct layers. Each layer has a specific role and only communicates with the layers directly above and below it.

**Why it matters for VAPT:** Every attack lives at a specific layer. Understanding the model helps you know WHICH layer a vulnerability is in and therefore WHAT kind of tools to use.

---

## The 7 Layers

```
LAYER 7 ┌─────────────────────────────────────────────────────┐
        │              APPLICATION LAYER                      │
        │  What the user/app sees. HTTP, FTP, DNS, SMTP.     │
        │  Vulnerabilities: SQLi, XSS, SSRF, XXE, etc.       │
LAYER 6 ├─────────────────────────────────────────────────────┤
        │              PRESENTATION LAYER                     │
        │  Data format: encryption, encoding, compression.    │
        │  SSL/TLS, ASCII→Unicode, JPEG/PNG parsing.          │
        │  Vulns: TLS downgrade, encoding bypass, CVEs.       │
LAYER 5 ├─────────────────────────────────────────────────────┤
        │                SESSION LAYER                        │
        │  Opens/closes sessions between apps.               │
        │  NetBIOS, RPC, SQL sessions, authentication.       │
        │  Vulns: session fixation, hijacking.               │
LAYER 4 ├─────────────────────────────────────────────────────┤
        │               TRANSPORT LAYER                       │
        │  End-to-end connection. TCP and UDP.               │
        │  Ports, reliability, flow control.                 │
        │  Vulns: SYN flood, port scanning, RST injection.   │
LAYER 3 ├─────────────────────────────────────────────────────┤
        │                NETWORK LAYER                        │
        │  Routing between networks. IP protocol.            │
        │  Routers operate here. IP addresses.               │
        │  Vulns: IP spoofing, ICMP attacks, routing attacks. │
LAYER 2 ├─────────────────────────────────────────────────────┤
        │               DATA LINK LAYER                       │
        │  Node-to-node on same LAN. MAC addresses.         │
        │  Ethernet, WiFi (802.11), VLANs, switches.        │
        │  Vulns: ARP spoofing, MAC flooding, VLAN hopping.  │
LAYER 1 └─────────────────────────────────────────────────────┘
                         PHYSICAL LAYER
           Cables, radio waves, fiber, electrical signals.
           Hubs, repeaters, physical media.
           Vulns: physical access, cable tapping, rogue APs.
```

---

## Memory Aid

```
Please Do Not Throw Sausage Pizza Away
Layer 1: Physical
Layer 2: Data Link
Layer 3: Network
Layer 4: Transport
Layer 5: Session
Layer 6: Presentation
Layer 7: Application

(Or from top to bottom: All People Seem To Need Data Processing)
```

---

## What Each Layer Does — Concrete Examples

```
DATA FLOW: You send a POST request to target.com

LAYER 7 (Application):
  You type: POST /login HTTP/1.1
            Host: target.com
            Content: username=alice&password=secret

LAYER 6 (Presentation):
  TLS encryption: the HTTP data is encrypted
  The data is now scrambled bytes

LAYER 5 (Session):
  TCP session established (connection to target.com:443 is open)

LAYER 4 (Transport):
  Data split into TCP segments
  Source port: 54321, Dest port: 443
  Sequence numbers added for reassembly

LAYER 3 (Network):
  IP packets created
  Source IP: 192.168.1.100, Dest IP: 142.250.182.46
  Router decides next hop

LAYER 2 (Data Link):
  Ethernet frames created
  Source MAC: your NIC MAC, Dest MAC: router MAC
  Travels to router

LAYER 1 (Physical):
  Bits: 01001010... sent as electrical signals/radio waves
  Physically travels to router
```

---

## Security Context — OSI Model in VAPT

### Layer-by-Layer Attack Map

```
LAYER 7 — Application Attacks:
─────────────────────────────
  SQLi, XSS, SSRF, XXE, IDOR, CSRF, Command Injection
  HTTP Request Smuggling, Cache Poisoning, Business Logic
  Authentication Bypass, JWT attacks, OAuth attacks
  Tools: Burp Suite, sqlmap, gobuster, nikto

LAYER 6 — Presentation/Crypto Attacks:
──────────────────────────────────────
  SSL stripping (downgrade HTTPS → HTTP)
  Heartbleed (TLS memory disclosure)
  POODLE (SSLv3 padding oracle)
  BEAST (CBC IV prediction)
  Tools: testssl.sh, sslyze, openssl

LAYER 5 — Session Attacks:
──────────────────────────
  Session fixation (force known session ID on victim)
  Session hijacking (steal session cookie)
  Pass-the-Hash, Pass-the-Ticket (Kerberos)
  Tools: Burp Suite, impacket, mimikatz

LAYER 4 — Transport Attacks:
────────────────────────────
  TCP SYN flood (DoS)
  Port scanning (Nmap)
  RST injection (TCP session reset)
  UDP flood (DoS)
  Tools: Nmap, hping3, scapy

LAYER 3 — Network Attacks:
──────────────────────────
  IP spoofing (fake source IP)
  ICMP redirect attacks
  Smurf attack (ICMP amplification)
  BGP hijacking (route table manipulation)
  Tools: hping3, scapy, Nmap

LAYER 2 — Data Link Attacks:
────────────────────────────
  ARP spoofing/poisoning (MITM on LAN)
  MAC flooding (fill switch CAM table → switch becomes hub)
  VLAN hopping (bypass VLAN segmentation)
  STP attacks (spanning tree manipulation)
  Tools: arpspoof, bettercap, yersinia

LAYER 1 — Physical Attacks:
───────────────────────────
  Rogue WiFi access point
  Physical access to server room
  USB drop attack (malicious USB in parking lot)
  Cable tapping, signal interception
  Evil Twin WiFi attack
```

### Common OSI Layer Confusion in Questions

```
Question: "ARP spoofing operates at which layer?"
Answer: Layer 2 (Data Link) — ARP works with MAC addresses

Question: "SSL/TLS operates at which layer?"
Answer: Layer 5/6 (Session/Presentation) — depends on model used
Note: TCP/IP model puts it at Transport. Don't overthink this.

Question: "SQL injection operates at which layer?"
Answer: Layer 7 (Application) — it's an HTTP/app-level attack

Question: "Port scanning — which layer?"
Answer: Layer 4 (Transport) — scanning TCP/UDP ports

Question: "IP spoofing — which layer?"
Answer: Layer 3 (Network) — manipulating IP headers
```

---

## Hands-On: Identifying Attack Layers

```bash
# Layer 7 attack — HTTP request tampering (Burp Suite)
curl -X POST https://target.com/login -d "admin' OR '1'='1"

# Layer 6 — test TLS version
openssl s_client -connect target.com:443 -ssl3  # should fail if patched

# Layer 4 — port scan
nmap -sS -p 1-65535 target   # TCP SYN scan

# Layer 3 — ICMP ping (network reachability)
ping target.com
traceroute target.com    # shows Layer 3 routing hops

# Layer 2 — ARP attack (local network only)
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
sudo arp-scan -l    # Layer 2 discovery

# Layer 1 — rogue AP (physical proximity needed)
# hostapd-wpe setup (requires physical WiFi adapter in monitor mode)
```

---

## How to Fix / Secure (Layer by Layer)

| Layer | Common Attack | Defense |
|-------|---------------|---------|
| 7 Application | SQLi, XSS, CSRF | Input validation, WAF, CSP |
| 6 Presentation | SSL downgrade, Heartbleed | Patch TLS, disable old versions |
| 5 Session | Session hijacking | HttpOnly/Secure cookies, short TTL |
| 4 Transport | SYN flood | SYN cookies, rate limiting |
| 3 Network | IP spoofing | BCP38 ingress filtering |
| 2 Data Link | ARP spoofing | DAI, 802.1X authentication |
| 1 Physical | Physical access | Access control, camera, USB blocking |

---

## Related Notes
- [[20 - TCP IP Model]] — the 4-layer practical model
- [[06 - TCP Three-Way Handshake]] — Layer 4 detail
- [[10 - ARP Address Resolution Protocol]] — Layer 2 detail
- [[17 - TLS SSL How HTTPS Works]] — Layer 6 detail
- [[Module 35 - Network Protocol Attacks]] — Layer 2-4 attacks
