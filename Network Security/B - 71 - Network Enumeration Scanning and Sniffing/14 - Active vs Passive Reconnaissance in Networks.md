---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.14 Active vs Passive Reconnaissance in Networks"
---

# 14 - Active vs Passive Reconnaissance in Networks

## Introduction

Reconnaissance is the foundational phase of any penetration test, red team engagement, or malicious cyber attack. It involves gathering intelligence about a target organization, its network topology, its employees, and its digital footprint. The quality of the reconnaissance directly dictates the success of subsequent exploitation phases. 

Reconnaissance is strictly categorized into two methodologies: **Passive Reconnaissance** and **Active Reconnaissance**. Understanding the operational, technical, and legal distinctions between the two is vital. Choosing the wrong method at the wrong time can result in burning your infrastructure, triggering a massive Incident Response (IR) from the target's Security Operations Center (SOC), or violating the Rules of Engagement (RoE).

This document explores the mechanics, tools, and strategic application of both active and passive network reconnaissance.

---

## Deep Dive: Passive vs Active Methodologies

### Passive Reconnaissance

Passive reconnaissance involves gathering information about a target *without directly interacting with the target's infrastructure*. From the target's perspective, passive reconnaissance is completely invisible. Because the attacker is querying third-party databases, public records, or listening to ambient network traffic without transmitting packets to the target, no logs are generated on the target's intrusion detection systems or firewalls.

**Key Characteristics:**
- Zero direct interaction with the target's servers or network.
- Completely stealthy; leaves no trace on target logs.
- Heavily reliant on Open Source Intelligence (OSINT).
- Often yields historical or slightly outdated data.

### Active Reconnaissance

Active reconnaissance involves direct, packet-level interaction with the target's systems. The attacker sends probes (TCP, UDP, ICMP packets) to the target's network and analyzes the responses. This phase maps exactly what is currently alive on the network, but it generates immense amounts of noise.

**Key Characteristics:**
- Direct interaction with target IP addresses and domains.
- Highly accurate and real-time.
- extremely noisy; easily detected by Firewalls, IDS/IPS, and SOC analysts.
- Carries legal implications if performed without authorization.

---

## ASCII Diagram: Passive vs Active Flow

```text
+-----------------------------------------------------------------------------------+
|                        PASSIVE VS ACTIVE RECONNAISSANCE                           |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [PASSIVE RECONNAISSANCE - Stealth Mode]                                          |
|                                                                                   |
|  +-------------+       (Queries)        +------------------+                      |
|  |             | ---------------------> | 3rd Party DBs    |                      |
|  |  Attacker   |                        | (Shodan, WHOIS,  |     +-------------+  |
|  |             | <--------------------- |  DNS, GitHub)    |     | Target Org  |  |
|  +-------------+       (Results)        +------------------+     +-------------+  |
|        |                                         |                      |         |
|        +-----------------------------------------+----------------------+         |
|         Attacker never touches the target. Target logs show NO activity.          |
|                                                                                   |
|===================================================================================|
|                                                                                   |
|  [ACTIVE RECONNAISSANCE - Direct Interaction]                                     |
|                                                                                   |
|  +-------------+     SYN / ICMP / HTTP Probes                +-------------+      |
|  |             | ------------------------------------------> |             |      |
|  |  Attacker   |                                             | Target Org  |      |
|  |             | <------------------------------------------ |   (Firewall/|      |
|  +-------------+       SYN-ACK / RST / 200 OK                |    Servers) |      |
|                                                              +-------------+      |
|        +----------------------------------------------------------------+         |
|         Attacker packets hit target. Target Firewall/IDS logs EVERYTHING.         |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Passive Reconnaissance Techniques and Tools

Passive reconnaissance builds the initial map of the target's external perimeter. 

### 1. WHOIS and DNS Enumeration
Querying domain registries to find ownership details, name servers, and IP ranges.
- **Tools:** `whois`, `nslookup`, `dig`.
- **Passive DNS:** Using services like SecurityTrails, VirusTotal, or DNSDumpster to view historical DNS records. This can reveal subdomains and development servers that are not currently linked on the main website.

### 2. Search Engine Dorking (Google Hacking)
Using advanced search operators to find exposed files, directory listings, or login portals that search engines have indexed.
- `site:target.com filetype:pdf "confidential"`
- `site:target.com intitle:"index of"`
- `site:target.com inurl:admin`

### 3. Deep Internet Scanning Databases (Shodan / Censys)
Instead of port-scanning the target (which is Active), we query Shodan. Shodan continuously port-scans the entire internet and indexes the banners. We query Shodan's database for the target's IP ranges.
- **Example:** Searching Shodan for `org:"Target Corporation" port:3389` reveals exposed Remote Desktop servers without ever sending a packet to the target.

### 4. Code Repositories and Data Leaks
Searching GitHub, GitLab, and Pastebin for hardcoded credentials, API keys, or infrastructure blueprints accidentally committed by developers.
- **Tools:** TruffleHog, Gitrob.

### 5. Social Media and Corporate OSINT
Mapping employee hierarchies via LinkedIn. Finding the IT department staff, their technical skills (which hint at the technology stack used internally), and generating target lists for phishing campaigns.

### 6. Passive Network Sniffing (Internal Only)
If the attacker already has a rogue device on the internal network, firing up Wireshark in promiscuous mode to simply *listen* to broadcast traffic (ARP, LLMNR, NBT-NS, DHCP) is passive reconnaissance. No packets are injected, but network architecture and live hosts are discovered.

---

## Active Reconnaissance Techniques and Tools

Once the passive phase defines the target space and Rules of Engagement permit, active reconnaissance begins to validate the findings.

### 1. Network Discovery and Ping Sweeps
Determining which IP addresses within a discovered CIDR range are actually online and responding.
- **Tools:** `nmap -sn 10.10.10.0/24`, `fping -a -g 10.10.10.0/24`, `netdiscover` (ARP sweeping).

### 2. Port Scanning and Service Enumeration
Interrogating the live IP addresses to see what TCP/UDP ports are open and what services are listening.
- **Tools:** Nmap (`nmap -sS -p- 10.10.10.5`), Masscan (for scanning massive internet ranges quickly), RustScan.
- Extracting banners (e.g., connecting via Netcat to port 22 to see `SSH-2.0-OpenSSH_8.2p1 Ubuntu`).

### 3. Web Application Directory Brute-Forcing
Sending thousands of HTTP GET requests to discover hidden administrative directories or backup files.
- **Tools:** Gobuster, Feroxbuster, ffuf.
- *Command:* `gobuster dir -u http://target.com -w common.txt`

### 4. Vulnerability Scanning
Actively probing identified services for known CVEs using tools like Nessus or OpenVAS, as detailed in [[13 - Vulnerability Scanning with Nessus and OpenVAS]].

### 5. DNS Zone Transfers (AXFR)
Attempting to force the target's DNS server to dump its entire zone file. While DNS querying is generally passive, attempting an AXFR transfer is a direct, active attack against the server's configuration.
- *Command:* `dig axfr @ns1.target.com target.com`

---

## Blurring the Lines: Semi-Passive and Stealth Active

In modern engagements, attackers use techniques that blur these definitions.

- **Web Crawling:** Is visiting a website passive or active? Technically it's active (you are sending HTTP requests), but visiting standard public pages looks like normal traffic. Running an automated spider (like Burp Suite Spider) rapidly becomes active reconnaissance as it generates 404 errors and noise.
- **Stealth Scans:** Using Nmap Decoys (`-D`) or extremely slow timing templates (`-T 1` or "Sneaky") is active reconnaissance designed to evade detection by blending into background noise or spoofing source IPs.

---

## Defense and Mitigation Strategies

Defending against reconnaissance requires different strategies depending on the type:

**Defending against Passive Reconnaissance:**
- **Data Minimization:** Ensure WHOIS privacy is enabled. Utilize reverse-proxies (like Cloudflare) to hide origin server IP addresses.
- **Code Audits:** Strictly audit GitHub repositories to ensure no API keys or credentials are leaked.
- **Metadata Stripping:** Strip metadata (Exif data, author names, software versions) from public PDF and Word documents before publishing them to the website.

**Defending against Active Reconnaissance:**
- **Perimeter Firewalls:** Implement strict Default-Drop rules on edge firewalls. Only expose explicitly required ports (e.g., 443).
- **Intrusion Prevention Systems (IPS):** Configure IPS to automatically block IP addresses that trigger port scan signatures or generate excessive 404 errors in a short timeframe.
- **Honeypots:** Deploy honeypots or honey-ports. If an internal port scan hits a known decoy service, immediately isolate the source machine.

---

## Chaining Opportunities
- The domains and subdomains discovered during Passive DNS enumeration are immediately fed into Active Reconnaissance tools like Nmap to discover open ports.
- Passive discovery of employee names via LinkedIn translates directly into username generation for SMTP enumeration detailed in [[12 - Enumerating SMTP VRFY EXPN]].
- Active port scanning identifies infrastructure that must be categorized and assessed for Firewalls/WAFs, bridging into [[15 - Identifying Firewalls and WAFs]].

## Related Notes
- [[12 - Enumerating SMTP VRFY EXPN]]
- [[13 - Vulnerability Scanning with Nessus and OpenVAS]]
- [[15 - Identifying Firewalls and WAFs]]
- [[11 - Enumerating FTP and TFTP]]
