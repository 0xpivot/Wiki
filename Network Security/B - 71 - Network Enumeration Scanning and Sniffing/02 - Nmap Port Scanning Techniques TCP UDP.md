---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.02 Nmap Port Scanning Techniques TCP UDP"
---

# Nmap Port Scanning Techniques (TCP & UDP)

## Introduction

Once host discovery is complete, the next logical step in network enumeration is port scanning. Port scanning is the process of probing a target host to determine which TCP and UDP ports are "open" (listening), "closed" (not listening), or "filtered" (blocked by a firewall). This critical phase maps the attack surface of the target, revealing what services, applications, and operating systems are exposed to the network.

Nmap (Network Mapper) is the undisputed industry standard for port scanning. It offers a vast array of scanning techniques designed to operate accurately across different network environments, bypass firewalls, and evade Intrusion Detection Systems (IDS). Understanding the underlying mechanics of TCP and UDP protocols is essential to leverage Nmap effectively and interpret its output correctly.

## Port States in Nmap

Before diving into techniques, it is crucial to understand the six port states recognized by Nmap:

1. **Open:** An application is actively accepting TCP connections, UDP datagrams, or SCTP associations on this port. This is the primary goal of port scanning.
2. **Closed:** A closed port is accessible (it receives and responds to Nmap probe packets), but there is no application listening on it. These can be useful for OS detection.
3. **Filtered:** Nmap cannot determine whether the port is open because packet filtering prevents its probes from reaching the port. The filtering could be from a dedicated firewall device, router rules, or host-based firewall software.
4. **Unfiltered:** The port is accessible, but Nmap is unable to determine whether it is open or closed. This state is mostly seen with the TCP ACK scan.
5. **Open|Filtered:** Nmap places ports in this state when it is unable to determine whether a port is open or filtered. This occurs for scan types in which open ports give no response.
6. **Closed|Filtered:** This state is used when Nmap is unable to determine whether a port is closed or filtered. It is only used for the IP ID idle scan.

## TCP Scanning Techniques

Transmission Control Protocol (TCP) is a connection-oriented protocol that relies on the three-way handshake (SYN, SYN/ACK, ACK) to establish reliable communication. Nmap manipulates this process to determine port states.

### 1. TCP Connect Scan (`-sT`)

The TCP Connect scan is the default scanning technique when a user does not have raw packet privileges (e.g., not running as root). It utilizes the underlying operating system's `connect()` system call to attempt to open a connection to every target port.

- **How it works:**
  - If the port is open, the OS completes the full three-way handshake: SYN -> SYN/ACK -> ACK.
  - If the port is closed, the target responds with an RST/ACK.
- **Pros:** Does not require root privileges. Highly reliable on local networks.
- **Cons:** Extremely noisy. Because a full connection is established, the target service will almost certainly log the connection attempt in its application logs (e.g., Apache or IIS access logs). It is also slower than other methods due to the overhead of the full handshake.

### 2. TCP SYN Scan (`-sS`)

Also known as "half-open" or "stealth" scanning, this is the default scan when running as root. It is the most popular scan type because it is fast, relatively stealthy, and accurate.

- **How it works:**
  - Nmap sends a SYN packet (requesting a connection).
  - If the target responds with a SYN/ACK, the port is **open**. Nmap immediately sends an RST (Reset) to tear down the connection before it is fully established.
  - If the target responds with an RST, the port is **closed**.
  - If there is no response after several retransmissions, or an ICMP unreachable error is received, the port is marked as **filtered**.
- **Pros:** Stealthier than a Connect scan because it never completes the three-way handshake, meaning many applications will not log the connection. Extremely fast.
- **Cons:** Requires root/administrator privileges to craft raw packets. Modern IDSs easily detect sequential SYN scans.

### 3. TCP ACK Scan (`-sA`)

Unlike other scans, the ACK scan never determines if a port is "open" or "closed." Its sole purpose is to map out firewall rulesets to determine if ports are **filtered** or **unfiltered**.

- **How it works:**
  - Nmap sends an ACK packet with a random sequence number.
  - According to RFC 793, an unexpected ACK packet should be responded to with an RST packet.
  - If Nmap receives an RST packet, it knows the port is reachable (i.e., **unfiltered**).
  - If there is no response, or an ICMP error is returned, the port is **filtered**.
- **Use Case:** Mapping stateful firewalls. A stateful firewall tracks connection states and drops unsolicited ACK packets (marking them filtered). A stateless router ACL might allow the ACK packet through, revealing that the port is unfiltered.

### 4. TCP Null, FIN, and Xmas Scans (`-sN`, `-sF`, `-sX`)

These scans exploit a subtle loophole in the TCP RFC (RFC 793) regarding how systems should handle malformed TCP segments.

- **Null Scan (`-sN`):** Does not set any bits (TCP flag header is 0).
- **FIN Scan (`-sF`):** Sets just the TCP FIN bit.
- **Xmas Scan (`-sX`):** Sets the FIN, PSH, and URG flags, "lighting the packet up like a Christmas tree."
- **How it works (RFC compliant systems like Linux/Unix):**
  - If the port is **closed**, the target responds with an RST.
  - If the port is **open**, the target ignores the malformed packet (no response).
- **Pros:** Can bypass some stateless firewalls and older IDSs that only look for SYN packets.
- **Cons:** Does not work against Windows systems. Windows TCP stacks violate the RFC by sending an RST regardless of whether the port is open or closed, making all ports appear closed. Also results in ambiguous "open|filtered" states when no response is received.

### 5. TCP Window Scan (`-sW`) and Maimon Scan (`-sM`)

- **Window Scan:** Similar to the ACK scan, but it actually tries to distinguish between open and closed ports by examining the TCP Window field of the RST packet returned. On some systems, open ports yield a positive window size, while closed ports have a zero window.
- **Maimon Scan:** Named after Uriel Maimon. It sends a FIN/ACK probe. According to RFC 793, a RST should be generated in response to such a packet whether the port is open or closed. However, many BSD-derived systems simply drop the packet if the port is open.

### 6. The Idle Scan (`-sI`)

The Idle Scan is the ultimate stealth scan. It allows an attacker to scan a target without sending a single packet to the target from their own IP address. Instead, it utilizes a "zombie" host.

**How it works:**
1. The attacker finds an idle "zombie" host on the network with a predictable IP ID sequence generation mechanism.
2. The attacker probes the zombie to determine its current IP ID.
3. The attacker sends a forged SYN packet to the target, spoofing the source IP address to be that of the zombie.
4. If the target port is open, it sends a SYN/ACK to the zombie. The zombie, receiving an unexpected SYN/ACK, sends an RST to the target and increments its IP ID.
5. If the target port is closed, it sends an RST to the zombie. The zombie ignores the RST and its IP ID remains unchanged.
6. The attacker probes the zombie again. If the IP ID incremented by 2, the target port was open. If it incremented by 1, the port was closed.

```bash
nmap -sI zombie_ip target_ip
```

## UDP Scanning Techniques

User Datagram Protocol (UDP) is a connectionless protocol. UDP scanning is inherently more difficult, slower, and less reliable than TCP scanning because there is no standardized acknowledgment mechanism like the TCP three-way handshake.

### UDP Scan (`-sU`)

UDP scanning works by sending an empty UDP packet to the target port.

- **How it works:**
  - If an ICMP Port Unreachable error (Type 3, Code 3) is returned, the port is **closed**.
  - If the target responds with a UDP packet (rare, but happens for services like DNS or NTP), the port is **open**.
  - If no response is received (which is common, as open services often drop empty UDP packets, and firewalls drop UDP entirely), the port is marked as **open|filtered**.
- **Challenges:** UDP scanning is brutally slow because many systems (especially Linux) enforce rate limits on ICMP error messages (e.g., 1 error per second). Scanning all 65,535 UDP ports on a rate-limited host can take many hours.
- **Optimization:** To speed up UDP scans, combine them with version detection (`-sV`) so Nmap sends service-specific payloads instead of empty packets, increasing the chance of an active response. Also, limit the scan to top ports (`--top-ports 100`).

```bash
# Optimized UDP Scan example
nmap -sU -sV --top-ports 100 10.10.10.5
```

## Bypassing Firewalls and IDS

Nmap offers several options to circumvent packet filtering devices:

- **Fragmentation (`-f`):** Fragments the TCP header over several packets. This makes it harder for packet filters, IDSs, and other annoyances to understand what is happening.
- **Specify MTU (`--mtu`):** Allows specifying a custom Maximum Transmission Unit to enforce specific fragmentation sizes.
- **Decoys (`-D`):** Cloaks a scan with decoys, making it appear that the scan is coming from multiple IP addresses simultaneously.
- **Source Port Spoofing (`--source-port` or `-g`):** Many firewalls are misconfigured to implicitly trust traffic originating from port 53 (DNS) or port 20 (FTP data). This flag spoofs the source port of the scan.
- **MAC Address Spoofing (`--spoof-mac`):** Changes the source MAC address, which can help bypass MAC-based ACLs on local networks.

## Visualizing TCP Scan Mechanisms

```ascii
+-------------------+                                  +-------------------+
|      Scanner      |                                  |   Target System   |
|   (Nmap -sS / -sT)|                                  |    (Port 80)      |
+-------------------+                                  +-------------------+
          |                                                      |
          |               --- TCP Connect Scan (-sT) ---         |
          |-------- SYN ---------------------------------------->|
          |<------- SYN/ACK -------------------------------------|
          |-------- ACK ---------------------------------------->| (Connection Est.)
          |-------- RST/ACK (Nmap closes connection) ----------->|
          |                                                      |
          |               --- TCP SYN Scan (-sS) ---             |
          |-------- SYN ---------------------------------------->|
          |<------- SYN/ACK (Port is OPEN) ----------------------|
          |-------- RST (Nmap tears down early) ---------------->|
          |                                                      |
          |               --- TCP Null/FIN/Xmas Scan ---         |
          |-------- FIN/URG/PSH -------------------------------->|
          |             (No Response)                            | (Port is OPEN)
          |                                                      |
          |-------- FIN/URG/PSH -------------------------------->|
          |<------- RST -----------------------------------------| (Port is CLOSED)
          |                                                      |
+-------------------+                                  +-------------------+
```

## Scan Optimization and Timing

Port scanning can be resource-intensive and time-consuming. Nmap provides timing templates (`-T0` through `-T5`) to control aggressiveness:

- **T0 (Paranoid) & T1 (Sneaky):** Extremely slow, used for IDS evasion.
- **T2 (Polite):** Slows down to consume less bandwidth.
- **T3 (Normal):** Default behavior.
- **T4 (Aggressive):** Assumes a fast, reliable network. Significantly speeds up scans. Often the preferred setting for internal VAPT.
- **T5 (Insane):** Very fast, but prone to missing open ports due to packet loss or target rate limiting.

### Specific Timing Flags:
- `--min-rate <number>`: Send packets no slower than the specified rate.
- `--max-retries <number>`: Cap the number of port scan probe retransmissions.
- `--host-timeout <time>`: Give up on a target after this long.

## Port Specification

By default, Nmap scans the top 1,000 most common TCP ports. To customize this:
- `-p 22,80,443`: Scan specific ports.
- `-p 1-1024`: Scan a range.
- `-p-`: Scan all 65,535 ports (critical for thorough assessments, as malware or backdoors often hide on high ports).
- `--top-ports 2000`: Scan the top 2000 most common ports.

## Output Formats

Saving scan results is vital for documentation and feeding into other tools. Nmap supports multiple output formats:
- `-oN <file>`: Normal output (human-readable text).
- `-oX <file>`: XML output (essential for parsing with scripts or importing into tools like Metasploit or Nessus).
- `-oG <file>`: Grepable output (deprecated, but useful for basic `grep`/`awk` command-line parsing).
- `-oA <basename>`: Outputs in all three formats simultaneously.

## Chaining Opportunities
- **Service Enumeration:** Once open ports are identified, the next step is to determine the exact service and version running on them using Nmap's `-sV` flag. See [[03 - Nmap Service and OS Detection]].
- **Vulnerability Scanning:** Port lists are fed into vulnerability scanners or specific NSE scripts. See [[04 - Nmap Scripting Engine NSE Basics]].
- **Rapid Discovery:** If scanning massive networks, tools like Masscan or Rustscan are used first to find open ports rapidly, then Nmap is aimed specifically at those discovered ports. See [[05 - Masscan and RustScan for Fast Discovery]].

## Related Notes
- [[01 - Ping Sweeps and Host Discovery]]
- [[03 - Nmap Service and OS Detection]]
- [[05 - Masscan and RustScan for Fast Discovery]]
