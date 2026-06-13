---
tags: [tools, vapt, utility, network, performance]
difficulty: intermediate
module: "41 - Tools"
topic: "41.04 Masscan"
---

# Masscan: Asynchronous, High-Speed Internet-Scale Port Scanning

## 1. Executive Summary & Overview
Masscan, authored by Robert David Graham, is a specialized network reconnaissance tool designed for one singular, overriding purpose: absolute, unadulterated speed. It is heralded as the fastest internet-scale port scanner in existence, capable of transmitting up to 10 million packets per second. At its theoretical maximum (given appropriate hardware, typically a dedicated 10Gbps network interface, and a custom network driver like PF_RING), Masscan can scan the entire IPv4 internet (roughly 3.7 billion routable addresses) for a single open port in under six minutes.

In the context of Vulnerability Assessment and Penetration Testing (VAPT), Masscan fills a very specific niche. It is not a replacement for the granular, stateful analysis provided by Nmap. Instead, it is the premier tool for massive-scope external engagements, bug bounty hunting across vast corporate infrastructures, or internal red team operations where an attacker needs to identify the open attack surface of an immense `/8` internal network instantaneously before defensive teams can react.

Masscan achieves this extreme performance by abandoning the traditional socket-based TCP/IP stack of the operating system. It operates asynchronously, building its own raw packets and managing state entirely in user-space, ignoring the operating system's connection tracking.

## 2. Core Architecture & Operating Principles
The fundamental reason traditional scanners like Nmap are bottlenecked at high speeds is the operating system's TCP/IP stack. When Nmap sends a SYN packet and receives a SYN/ACK, the OS kernel (which Nmap must interface with) tries to track that connection, consuming memory and CPU cycles.

Masscan bypasses the kernel entirely. It uses a custom asynchronous transmit engine. It blasts out TCP SYN packets as fast as the network interface card (NIC) can handle them. It does not wait for a response before sending the next packet. 

To handle incoming responses, Masscan has a completely separate receive thread. When a SYN/ACK packet is received, Masscan identifies it, logs the open port, and (crucially) generates a raw RST (Reset) packet to close the connection, satisfying the remote host without ever informing the local operating system that a connection was attempted.

### ASCII Architecture Diagram: Masscan Asynchronous Engine

```text
    Local Operating System (Linux Kernel)              |        Target Network (e.g., The Internet)
                                                       |
    +---------------------------------------+          |
    |               User Space              |          |
    |  +---------------------------------+  |          |
    |  |             Masscan             |  |          |
    |  |                                 |  |          |
    |  |  [ Transmit Thread ]            |  |          |       1. Massive wave of Raw TCP SYN packets
    |  |  (Builds raw SYN packets)       |===============|========================================>
    |  |                                 |  |          |
    |  |                                 |  |          |       2. Interleaved SYN/ACK responses
    |  |  [ Receive Thread  ]            |<==============|=========================================
    |  |  (Parses incoming packets,      |  |          |
    |  |   logs state, sends raw RST)    |  |          |
    |  +---------------------------------+  |          |
    +---------------------------------------+          |
       |  (Bypasses standard TCP/IP stack)             |
       |                                               |
       v                                               |
    [ Raw Network Interface (e.g., eth0) ]             |
    (Ideally utilizing PF_RING / DPDK for speed)       |
```

## 3. Deep Dive into Primary Capabilities

### 3.1 Unprecedented Scanning Speed
The defining feature of Masscan is the `--rate` parameter, which specifies the exact number of packets per second (pps) the tool will attempt to transmit.
*   **Low Rates**: `masscan -p80 10.0.0.0/8 --rate 1000`. Scans a Class A network at a modest 1000 pps, safe for most standard routers.
*   **High Rates**: `masscan -p443 0.0.0.0/0 --rate 100000`. Scans the entire internet at 100,000 pps. This requires significant bandwidth and will overwhelm consumer-grade routers, essentially functioning as a localized Denial of Service (DoS) attack against the tester's own infrastructure if not provisioned correctly.

### 3.2 Stateless Architecture and Randomization
*   **Statelessness**: Because Masscan does not maintain connection state, it is immune to SYN floods and does not run out of memory when tracking millions of probes.
*   **Target Randomization**: Unlike Nmap, which typically scans IPs sequentially (which looks very obvious to Intrusion Detection Systems), Masscan pseudo-randomly hashes the target IP list. It hits `1.1.1.1`, then `200.10.5.2`, then `8.8.8.8`. This spreads the load across the internet, preventing targeted overwhelming of a single destination subnet and often slipping under the radar of simplistic rate-limiting firewalls.

### 3.3 Banner Grabbing
While primarily a port scanner, Masscan has limited banner grabbing capabilities to identify the service running behind the open port.
*   **`--banners`**: This flag forces Masscan to complete the TCP handshake (sending an ACK after receiving the SYN/ACK) and wait for the remote service to transmit its initial banner string (like an SSH or FTP server banner).
*   **Limitation**: Masscan's banner grabbing is primitive compared to Nmap's `-sV`. It simply reads the first few bytes sent by the server; it does not send complex probes or analyze the responses against a sophisticated database.

### 3.4 Sharding for Distributed Scanning
For massive bug bounty operations, a single machine, even with a fast connection, might not be enough. Masscan supports sharding, allowing the workload to be split perfectly across multiple servers without overlap.
*   **`--shard 1/3`**: Instructs the first server to scan its specific third of the mathematical target space. Server 2 uses `--shard 2/3`, and so on.

## 4. Advanced Configuration & Optimization

### 4.1 Routing and Source IP Bypassing
Because Masscan bypasses the OS kernel, it often bypasses the OS routing tables.
*   **`--router-mac <mac>`**: Crucial on complex networks or VPNs. The tester must manually specify the MAC address of the default gateway router, otherwise, Masscan's raw packets will not know where to go on the local Ethernet segment.
*   **`--source-ip <ip>`**: Allows the tester to arbitrarily spoof the source IP address of the scan. If the tester specifies a source IP they do not control, they will not receive the responses (making it a blind scan or a SYN flood), but this is useful for evasion or testing firewall ingress filtering.

### 4.2 Handling the "Kernel RST" Problem
Because Masscan operates outside the OS, when a SYN/ACK arrives, the local OS kernel *also* sees it. Since the kernel has no record of initiating this connection (Masscan did it secretly), the kernel will automatically send an RST packet to the remote server, immediately killing the connection. This prevents Masscan's `--banners` feature from working.
*   **The Fix (iptables)**: Testers must configure their local firewall to block the kernel from seeing the incoming traffic on the specific port Masscan is using to receive data.
    `iptables -A INPUT -p tcp --dport 60000 -j DROP`
    Masscan is then configured to use that specific source port (`--source-port 60000`). Masscan, sniffing the raw interface, sees the packet before iptables drops it, but the kernel is shielded from it.

### 4.3 Output Formats and Resumption
*   **`-oJ` (JSON), `-oG` (Grepable)**: Masscan supports structured output for integration into data pipelines.
*   **`--resume <file.conf>`**: If a massive internet-wide scan crashes or is interrupted, Masscan can resume exactly where it left off by reading its dynamically generated paused configuration file.

## 5. Real-World Attack Scenarios / Case Studies

### Scenario A: Corporate Acquisition Asset Discovery
1.  **Objective**: A company acquires a massive legacy enterprise and needs to immediately discover all externally facing SSH servers across a sprawling `/16` and several `/8` legacy subnets to enforce password rotation.
2.  **Execution**: The tester deploys a Masscan instance on a high-bandwidth cloud VPS.
    `masscan 10.0.0.0/8 172.16.0.0/16 -p22 --rate 50000 -oJ ssh_hosts.json`
3.  **Result**: Within minutes, Masscan parses millions of IP addresses and outputs a JSON file containing only the IPs with port 22 open. This file is immediately handed to Nmap for deep version scanning.

### Scenario B: Exploiting the "Leftover" Attack Surface (Bug Bounty)
1.  **Objective**: A bug bounty hunter wants to find obscure, forgotten services (like unauthenticated Redis or Memcached databases) hosted on high-numbered ports across a target's massive AWS IP space.
2.  **Execution**: The hunter uses Masscan to scan all 65,535 ports across the target's `/16` block. Doing this with Nmap would take days. With Masscan, it takes less than an hour.
    `masscan -p1-65535 54.200.0.0/16 --rate 100000 --banners -oG high_ports.txt`
3.  **Exploitation**: The scan reveals a Memcached instance exposed on port 11211, leading directly to a high-impact data exfiltration finding.

## 6. Defensive Posture & Evasion Techniques
Defending against Masscan requires understanding its volume-based nature.
*   **Rate Limiting and Blackholing**: Standard firewalls will be immediately overwhelmed by a high-rate Masscan. Defense relies on edge routers and specialized DDoS mitigation appliances (like Arbor Networks) that detect the massive SYN anomaly and BGP blackhole the source IP.
*   **Stateful Inspection Failure**: Because Masscan randomizes targets, a stateful firewall might not realize it's a port scan if the firewall only looks at traffic directed at a *single* host. Network-wide anomaly detection is required.
*   **Evasion**: Masscan inherently evades sequential detection through IP randomization. However, it is highly "noisy." A tester cannot use Masscan "stealthily" if they are utilizing its primary feature (speed).

## 7. Automation, API, & CI/CD Integrations
Masscan is a foundational tool in continuous external attack surface management (EASM) pipelines.
*   **Cron/Airflow Jobs**: Security teams schedule weekly Masscan runs across their entire known IP space, outputting to JSON.
*   **Diffing Pipelines**: The JSON output is parsed by Python scripts and compared against the previous week's baseline. Any new IP/Port combination generates an immediate Slack alert to the SOC.
*   **Feeding the Pipeline**: Masscan is almost never the final tool. Its output is exclusively used to generate the target lists for Nmap (for version detection), Nuclei (for vulnerability scanning), or Eyewitness (for visual inspection).

## 8. Chaining Opportunities
*   **Masscan -> Nmap**: The classic workflow. Masscan acts as the wide-angle lens, finding the open ports across a `/8`. Nmap acts as the microscope, analyzing the specific ports Masscan found for vulnerabilities.
*   **Masscan -> Nuclei**: A bug bounty favorite. Masscan finds all open port 80/443 instances across an ASN. The list of `http://ip:port` is piped directly into Nuclei to immediately blast thousands of known CVE templates against the newly discovered attack surface.
*   **Masscan -> Zmap**: While similar, Zmap is often chained or compared. Masscan is preferred for scanning multiple ports across a range, whereas Zmap is highly optimized for scanning a single port across the entire IPv4 internet.

## 9. Related Notes
*   [[03 - Nmap]] - The tool used immediately following a Masscan run for deep service enumeration.
*   [[05 - Rustscan]] - A modern, faster, and more user-friendly alternative to the Masscan->Nmap chain.
*   [[08 - Nuclei]] - The template-based scanner fed by Masscan's output.
*   [[14 - Network Reconnaissance]] - The phase of testing where Masscan is deployed for large scopes.
