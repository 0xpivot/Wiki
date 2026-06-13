---
tags: [tools, vapt, utility, network]
difficulty: intermediate
module: "41 - Tools"
topic: "41.03 Nmap"
---

# Nmap: The De Facto Standard for Network Reconnaissance

## 1. Executive Summary & Overview
Nmap (Network Mapper) is arguably the most recognized and ubiquitous tool in the broader cybersecurity industry. Authored by Gordon Lyon (insecure.org), it is an open-source, highly versatile utility for network discovery, port scanning, and vulnerability enumeration. In the context of Vulnerability Assessment and Penetration Testing (VAPT), Nmap is almost universally the first tool utilized during the active reconnaissance phase. It provides the foundational map of the target's external or internal infrastructure upon which the rest of the engagement is built.

Nmap's primary function is to send specially crafted packets to target hosts and intricately analyze the responses to determine an extraordinary amount of information. It goes far beyond simply listing "open ports." Nmap is capable of determining what hosts are alive on a network, identifying the specific services (and their exact versions) running on those ports, fingerprinting the underlying Operating System (OS), identifying packet filters and firewalls, and executing complex, automated vulnerability checks via its embedded scripting engine.

Despite its age, Nmap remains relevant due to its constant updates, its unparalleled reliability, its massive user community, and its underlying architecture, which balances raw speed with meticulous, granular control over packet creation and timing.

## 2. Core Architecture & Operating Principles
Nmap operates at the transport and network layers (OSI Layers 3 and 4), requiring raw socket access for many of its advanced scanning techniques (which is why it often requires root/administrator privileges). It does not merely rely on standard operating system network APIs; instead, it crafts custom packets (TCP, UDP, ICMP, SCTP) from scratch. 

The core of Nmap's intelligence lies in its extensive databases (like `nmap-os-db` and `nmap-services`). When Nmap receives a response to a probe, it compares the subtle nuances of the packet (such as TCP sequence numbers, window sizes, options, and TTL values) against thousands of known signatures to accurately determine the OS or service version.

### ASCII Architecture Diagram: Nmap Scanning Methodology

```text
                                  Nmap Engine (Root Privilege)
    +-----------------------------------------------------------------------------------------+
    |                                                                                         |
    |  1. Host Discovery (Ping Sweep)   ------>   Target Alive?                               |
    |                                                | (Yes)                                  |
    |                                                v                                        |
    |  2. Port Scanning (SYN, Connect, UDP) -->   Identify Open/Closed/Filtered Ports         |
    |                                                |                                        |
    |                                                v                                        |
    |  3. Service & Version Detection   ------>   Send specific probes (HTTP, SSH, etc.)      |
    |     (-sV)                                   Analyze responses against signatures        |
    |                                                |                                        |
    |                                                v                                        |
    |  4. OS Fingerprinting             ------>   Analyze TCP/IP stack behavior nuances       |
    |     (-O)                                       |                                        |
    |                                                v                                        |
    |  5. Nmap Scripting Engine (NSE)   ------>   Execute Lua scripts against open services   |
    |     (-sC)                                   (Vulnerability checks, enumeration)         |
    |                                                |                                        |
    |                                                v                                        |
    |                                     Formatted Output (XML, Grepable, Normal)            |
    +-----------------------------------------------------------------------------------------+
```

## 3. Deep Dive into Primary Modules and Scan Types

### 3.1 Host Discovery (Ping Sweeps)
Before wasting time scanning thousands of ports, Nmap determines which IP addresses actually host active machines.
*   **`-sn` (No Port Scan)**: Previously `-sP`. Instructs Nmap to only perform host discovery and skip the port scan entirely.
*   **Discovery Techniques**: Nmap uses a combination of ICMP Echo Requests, TCP SYN to port 443, TCP ACK to port 80, and ICMP Timestamp requests. This multi-pronged approach is designed to bypass simple firewalls that might just block standard ICMP pings.

### 3.2 Port Scanning Techniques
This is Nmap's bread and butter. Nmap categorizes ports into six states: open, closed, filtered (blocked by a firewall), unfiltered, open|filtered, or closed|filtered.
*   **`-sS` (TCP SYN "Stealth" Scan)**: The default and most popular scan. It sends a SYN packet. If the port is open, the target replies with SYN/ACK. Nmap immediately sends an RST (Reset) to tear down the connection before it is fully established. This prevents the connection from being logged by many basic applications, hence "stealth."
*   **`-sT` (TCP Connect Scan)**: Uses the operating system's standard `connect()` system call to complete the full 3-way TCP handshake. Slower and more likely to be logged by target applications, but useful when root privileges are unavailable.
*   **`-sU` (UDP Scan)**: Scans for UDP services (like DNS, SNMP, DHCP). UDP scanning is notoriously slow and unreliable because open UDP ports often do not respond to empty probes. Nmap uses service-specific payloads to elicit responses.
*   **`-sA` (TCP ACK Scan)**: Used strictly for mapping firewall rulesets. It sends an ACK packet. If a firewall is stateful, it drops the packet (Filtered). If there is no firewall, the target responds with an RST (Unfiltered). It does not determine if a port is open or closed.

### 3.3 Service and OS Enumeration
*   **`-sV` (Version Detection)**: Crucial for VAPT. Once a port is found open, Nmap interrogates the service running behind it. It sends a series of complex probes (HTTP GET requests, SSL hellos) and analyzes the banners and error messages to pinpoint the exact software and version (e.g., Apache httpd 2.4.41).
*   **`-O` (OS Fingerprinting)**: Nmap sends a battery of malformed and standard packets to the target and analyzes the responses. Since different OS implementations of the TCP/IP stack handle anomalies differently, Nmap can determine the underlying OS (e.g., Windows Server 2019, Linux kernel 5.4) with high probability.

### 3.4 Nmap Scripting Engine (NSE)
The NSE elevates Nmap from a simple scanner to an automated vulnerability assessment framework. Scripts are written in Lua and categorized by functionality (e.g., `default`, `vuln`, `exploit`, `auth`, `discovery`).
*   **`-sC`**: Runs the `default` set of scripts (safe, non-intrusive enumeration).
*   **`--script=vuln`**: Runs scripts designed to actively check for known, specific vulnerabilities (like Heartbleed, MS17-010 EternalBlue) without necessarily exploiting them.
*   **Customization**: Testers can write their own Lua scripts to check for proprietary vulnerabilities or automate complex enumeration tasks against specific services.

## 4. Advanced Configuration & Optimization

### 4.1 Timing and Performance Tuning
Nmap's execution speed can be heavily customized to balance speed against accuracy and network stability.
*   **Timing Templates (`-T0` through `-T5`)**:
    *   `-T0` (Paranoid) and `-T1` (Sneaky): Extremely slow, used to evade Intrusion Detection Systems (IDS) by sending packets agonizingly slowly.
    *   `-T3` (Normal): The default.
    *   `-T4` (Aggressive): The standard for VAPT on reliable, modern networks. Speeds up timeouts and parallelizes scanning.
    *   `-T5` (Insane): Sacrifices accuracy for absolute raw speed. Often drops packets and misses open ports on congested networks.
*   **Granular Controls**: `--min-rate`, `--max-retries`, `--host-timeout` allow testers to meticulously define exactly how fast packets are sent, crucial for navigating unstable VPNs or bypassing rate-limiting firewalls.

### 4.2 Firewall Evasion and Spoofing
Nmap possesses advanced features designed to circumvent network defenses.
*   **`-f` (Fragment Packets)**: Splits TCP headers over multiple tiny IP fragments, attempting to confuse older packet-filtering firewalls or poorly configured IDS systems that do not properly reassemble fragments.
*   **`-D` (Decoy Scan)**: Spoofs the source IP address. Nmap sends scans appearing to come from multiple arbitrary IP addresses (decoys) alongside the tester's actual IP address, hiding the true source of the scan in a sea of noise.
*   **`--source-port` (or `-g`)**: Some firewalls blindly allow traffic originating from specific ports (like DNS port 53 or HTTP port 80). Nmap can spoof the source port of its probes to bypass these simplistic rules.

### 4.3 Output Formats
Properly logging Nmap results is essential.
*   **`-oN`**: Standard human-readable output.
*   **`-oX`**: XML output, essential for importing results into databases, reporting tools, or other frameworks like Metasploit.
*   **`-oG`**: Grepable output, designed for quick command-line parsing using `awk`, `grep`, and `cut`.
*   **`-oA <basename>`**: Outputs all three major formats simultaneously, which is the best practice during professional engagements.

## 5. Real-World Attack Scenarios / Case Studies

### Scenario A: Comprehensive External Infrastructure Mapping
1.  **Scope Acquisition**: The tester is provided a `/24` external CIDR block.
2.  **Host Discovery**: They execute a fast ping sweep to identify live assets: `nmap -sn -PE -PP -PS443,80 192.168.1.0/24 -oG live_hosts.txt`.
3.  **Targeted Scanning**: After extracting the live IP addresses, the tester initiates a thorough, aggressive scan for service versions and basic vulnerabilities: `nmap -iL live_hosts.txt -sS -sV -sC -O -T4 -p- -oA external_scan`.
4.  **Analysis**: The tester reviews the XML output. They discover a web server running an outdated version of Apache Tomcat on an obscure port (8080) and an exposed SSH service running an old version of OpenSSH. This sets the stage for targeted exploitation.

### Scenario B: Internal Network SMB Vulnerability Hunting
1.  **Objective**: An internal red team needs to quickly identify servers vulnerable to the MS17-010 (EternalBlue) exploit across a massive internal corporate network.
2.  **Targeted NSE Execution**: Instead of a full port scan, the team targets only the SMB port (445) and executes a specific NSE vulnerability script: `nmap -p 445 --script smb-vuln-ms17-010 10.0.0.0/8 -T4 -oA eternalblue_check`.
3.  **Rapid Exploitation**: Nmap rapidly queries port 445 across the entire Class A network. The output highlights the exact IP addresses of unpatched Windows servers, allowing the team to move laterally almost immediately.

## 6. Defensive Posture & Evasion Techniques
Defending against Nmap requires a multi-layered approach.
*   **Strict Egress and Ingress Filtering**: Firewalls should default to deny all traffic, only allowing explicitly required ports.
*   **Intrusion Prevention Systems (IPS)**: Modern IPS appliances are highly adept at signature-matching Nmap's default scanning behavior (especially aggressive timing templates and SYN scans). They can automatically block the source IP address upon detecting a port sweep.
*   **Port Knocking / Single Packet Authorization (SPA)**: Hides sensitive services (like SSH) entirely until a specific, cryptographically sound sequence of packets is received, rendering the service completely invisible to standard Nmap scans.
*   **Deception Technology**: Deploying honeypots that intentionally open thousands of fake ports to slow down Nmap scans (`Tarpitting`) and generate immediate high-fidelity alerts when touched.

## 7. Automation, API, & CI/CD Integrations
Nmap is highly amenable to scripting and automation.
*   **Bash/Python Wrappers**: Testers frequently write Python scripts (using the `python-nmap` module) to parse Nmap's XML output and automatically launch subsequent tools based on the findings (e.g., if port 80 is open, automatically launch Gobuster).
*   **Continuous Monitoring**: Organizations use scheduled cron jobs running Nmap diff scans (`ndiff`) to monitor their external perimeter for unexpected state changes (e.g., a developer accidentally exposing a database port to the internet).
*   **Metasploit Integration**: Nmap is natively integrated into the Metasploit Framework. The `db_nmap` command runs Nmap and automatically populates the Metasploit database with hosts, services, and vulnerabilities for streamlined exploitation.

## 8. Chaining Opportunities
*   **Nmap + Searchsploit**: The XML output of Nmap's version detection (`-sV`) can be fed into tools like Searchsploit to automatically query the Exploit Database for known public exploits matching the identified software versions.
*   **Nmap + Masscan/Rustscan**: For unimaginably large networks (like the entire internet or massive `/8` internal ranges), Masscan or Rustscan is used first to rapidly identify open ports in minutes. Those specific open ports and IP pairs are then fed into Nmap for detailed, slower version and script scanning.
*   **Nmap + Eyewitness/Aquatone**: Nmap identifies all IP addresses with HTTP/HTTPS ports open (80, 443, 8080, 8443). This list is passed to Aquatone, which automatically visits every web server, takes a screenshot of the application, and gathers server headers, providing a visual attack surface map.

## 9. Related Notes
*   [[04 - Masscan]] - The asynchronous, high-speed alternative for massive network ranges.
*   [[05 - Rustscan]] - The modern, insanely fast port scanner that seamlessly integrates with Nmap.
*   [[14 - Network Reconnaissance]] - The broader methodology where Nmap is the foundational tool.
*   [[08 - Metasploit Framework]] - A framework that heavily relies on Nmap data for exploitation.
