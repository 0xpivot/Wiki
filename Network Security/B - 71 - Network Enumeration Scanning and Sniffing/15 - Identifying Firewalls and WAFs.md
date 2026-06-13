---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.15 Identifying Firewalls and WAFs"
---

# 15 - Identifying Firewalls and WAFs

## Introduction

During the active reconnaissance and enumeration phase of a Vulnerability Assessment and Penetration Testing (VAPT) engagement, an attacker rarely has an unimpeded path to the target server. Modern network architectures are fortified with layers of defensive appliances designed to inspect, filter, and block malicious traffic. The two most critical defensive layers encountered are **Network Firewalls** (which operate primarily at OSI Layers 3 and 4) and **Web Application Firewalls (WAFs)** (which operate at OSI Layer 7).

Before launching exploits, running noisy vulnerability scanners, or attempting SQL injection, a penetration tester *must* identify the presence, type, and rule sets of these defensive mechanisms. Failing to identify a WAF or Firewall will result in the attacker's IP being blacklisted automatically, halting the assessment.

This document explores the technical methodologies for detecting, fingerprinting, and mapping Firewalls and Web Application Firewalls.

---

## Deep Dive: Firewalls vs WAFs

### Network Firewalls (Stateful and Stateless)
Network firewalls inspect packet headers—specifically Source/Destination IP addresses, protocols (TCP/UDP/ICMP), and Source/Destination Ports. Modern Next-Generation Firewalls (NGFW) also possess deep packet inspection, but their primary function remains routing and port-level access control.

When a firewall blocks a packet, it typically does so in one of two ways:
1. **DROP:** The packet is silently discarded. No response is sent back to the sender. This results in the connection timing out.
2. **REJECT:** The packet is discarded, but the firewall sends an explicit message back to the sender. For TCP, this is a `RST` (Reset) packet. For UDP/ICMP, it is an `ICMP Type 3 (Destination Unreachable)` message.

### Web Application Firewalls (WAFs)
WAFs operate exclusively at the Application Layer (HTTP/HTTPS). They do not care about port numbers; they care about the *payload* of the HTTP requests. WAFs intercept web traffic and analyze headers, cookies, URL parameters, and POST bodies against a vast database of attack signatures (like Cross-Site Scripting or SQL Injection patterns). 

When a WAF detects malicious activity, it blocks the HTTP request and usually returns a specific HTTP status code (often `403 Forbidden` or `406 Not Acceptable`) along with a custom block page identifying the WAF vendor (e.g., Cloudflare, Imperva, F5 ASM).

---

## ASCII Diagram: Firewall and WAF Placement

```text
+-----------------------------------------------------------------------------------+
|                        DEFENSIVE ARCHITECTURE TOPOLOGY                            |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                                                                                   |
|  +----------+         [OSI Layer 3/4]             [OSI Layer 7]                   |
|  |          |           +---------+               +-----------+                   |
|  | Attacker | ---->     | Network |      ---->    | Web App   |     +-----------+ |
|  |  (Nmap,  | (TCP 80)  | Firewall|    (HTTP GET) | Firewall  | --> | Web       | |
|  |  Burp)   |           | (Cisco/ |               | (WAF - F5/|     | Server    | |
|  +----------+           |  Palo)  |               | Cloudflare|     +-----------+ |
|                         +---------+               +-----------+                   |
|                              |                          |                         |
|   <--- SILENT DROP --------- +                          |                         |
|   (If port 22 is scanned)                               |                         |
|                                                         |                         |
|   <--- 403 FORBIDDEN & BLOCK PAGE ----------------------+                         |
|   (If payload contains "' OR 1=1--")                                              |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Identifying Network Firewalls

The goal of firewall identification is to map out the ACLs (Access Control Lists) and determine the rules governing inbound traffic.

### 1. TCP ACK Scans (Stateful Firewall Detection)
Standard Nmap SYN scans (`-sS`) determine if a port is open or closed. An ACK scan (`-sA`) is used specifically to determine if a port is *filtered* by a firewall.
Because an ACK packet implies an established connection, a stateful firewall will check its state table. If no prior connection exists, it drops the packet. Nmap uses this to map out the firewall ruleset without actually opening connections.

```bash
nmap -sA 10.10.10.50
```
- **Unfiltered:** Target returns an RST. The port is reachable, but we don't know if it's open/closed.
- **Filtered:** No response, or an ICMP Unreachable. A firewall is blocking the traffic.

### 2. Fragmentation and Evasion Techniques
If a firewall is aggressively blocking scans, attackers can test its robustness by altering packet structures.
- **Fragmenting Packets:** Breaking TCP headers over multiple packets to evade basic intrusion detection rules.
  ```bash
  nmap -f 10.10.10.50
  ```
- **Decoy Scans:** Spoofing the source IP to make the firewall think the scan is coming from dozens of random addresses, masking the true attacker's IP.
  ```bash
  nmap -D RND:10 10.10.10.50
  ```
- **Source Port Manipulation:** Some poorly configured firewalls explicitly trust traffic originating from specific ports, like DNS (53) or HTTP (80).
  ```bash
  nmap --source-port 53 10.10.10.50
  ```

### 3. Firewalk Tool
Firewalk is an active reconnaissance technique that uses TTL (Time To Live) expiration techniques (similar to traceroute) to determine the firewall rules of a gateway. It sends packets with a TTL one greater than the targeted gateway. If the gateway allows the traffic, the packet proceeds, the TTL expires at the next hop, and an "ICMP Time Exceeded" is returned. If the firewall blocks it, no response is seen.

---

## Identifying Web Application Firewalls (WAFs)

Identifying a WAF requires interacting with the web server and deliberately sending payloads designed to trigger defensive mechanisms. 

### 1. Passive WAF Fingerprinting
Sometimes, WAFs announce their presence via HTTP response headers or custom cookies.
- **Headers:** Inspect HTTP responses for headers like `Server: cloudflare`, `X-Powered-By: AWS WAF`, or `X-Sucuri-ID`.
- **Cookies:** WAFs often inject session tracking cookies. For instance, F5 BIG-IP injects cookies starting with `TS` or `BIGipServer`. Incapsula injects `incap_ses`.

You can observe these easily using `curl`:
```bash
curl -I http://target.com
```

### 2. Active WAF Triggering
The most definitive way to test for a WAF is to send a blatant, highly recognizable attack payload and observe the response.

**Normal Request:**
```bash
curl http://target.com/index.php?id=1
# Returns HTTP 200 OK
```

**Malicious Request (SQLi payload):**
```bash
curl "http://target.com/index.php?id=1%20UNION%20SELECT%201,2,3--"
# Returns HTTP 403 Forbidden
# Response Body: "The request has been blocked by Cloudflare"
```

### 3. Automated WAF Identification Tools

**WAFW00F:**
The industry-standard tool for identifying and fingerprinting WAFs. It sends a series of normal and malicious requests and analyzes the headers and block pages to identify the specific vendor.
```bash
wafw00f http://target.com
```
*Output Example:*
```text
[*] Checking http://target.com
[+] The site http://target.com is behind Cloudflare (Cloudflare Inc.) WAF.
```

**Nmap WAF Scripts:**
Nmap includes scripts specifically designed to detect web application firewalls.
```bash
nmap -p 80,443 --script http-waf-detect --script-args="http-waf-detect.detectBodyChanges" target.com
nmap -p 80,443 --script http-waf-fingerprint target.com
```

**WhatWeb:**
While primarily a web technology fingerprinting tool, WhatWeb contains dozens of plugins for WAF detection based on headers and cookies.
```bash
whatweb http://target.com
```

---

## Implications for Penetration Testing

Once a Firewall or WAF is identified, the methodology must adapt:
1. **Throttle Scanning:** Noisy scans (like Nessus or fast Nmap sweeps) will result in an IP ban. Scans must be slowed down drastically, or distributed across multiple source IP proxies.
2. **Payload Encoding:** If a WAF blocks `' OR 1=1--`, attackers must attempt to bypass it using encoding (URL encoding, Hex encoding, Unicode) or by exploiting parser differentials (e.g., HTTP Parameter Pollution).
3. **Bypassing Proxies:** Often, a WAF like Cloudflare operates as a reverse proxy. If the penetration tester can discover the *true origin IP* of the backend server (via passive DNS history, email headers, or Shodan), they can point their attacks directly at the origin IP, completely bypassing the WAF entirely.

---

## Chaining Opportunities
- Firewall evasion techniques (like fragmentation and source-port manipulation) are directly utilized during the port scanning phases discussed in [[14 - Active vs Passive Reconnaissance in Networks]].
- Discovering an origin IP to bypass a WAF allows an attacker to run unrestricted vulnerability scans directly against the host, tying into [[13 - Vulnerability Scanning with Nessus and OpenVAS]].
- Successfully bypassing a WAF using encoded payloads is a prerequisite for executing web application attacks, leading directly into [[45 - Uploading and Executing Web Shells]] or SQL Injection.

## Related Notes
- [[13 - Vulnerability Scanning with Nessus and OpenVAS]]
- [[14 - Active vs Passive Reconnaissance in Networks]]
- [[11 - Enumerating FTP and TFTP]]
- [[12 - Enumerating SMTP VRFY EXPN]]
