---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.03 Nmap Service and OS Detection"
---

# Nmap Service and OS Detection

## Introduction

Discovering an open port (e.g., port 80) is only the beginning of network enumeration. While port 80 typically hosts an HTTP web server, it could theoretically be hosting SSH, a custom malware C2 channel, or a database, as administrators can bind any service to any port. To accurately identify vulnerabilities, an attacker or penetration tester must determine precisely *what* application is running on an open port and what Operating System (OS) is powering the underlying host.

Nmap provides incredibly robust capabilities for Service Version Detection (`-sV`) and Operating System Detection (`-O`). These features transform a simple list of open ports into a detailed map of the target's technological stack, enabling targeted exploitation.

## Service Version Detection (`-sV`)

The service version detection module in Nmap queries open ports and analyzes the responses to determine the application name and version. This is achieved through a complex process of protocol interaction and signature matching against the `nmap-service-probes` database.

### How Service Detection Works

1. **Null Probe:** Nmap initially connects to the open port. Some services (like FTP, SSH, or SMTP) are "chatty" and immediately send a banner upon connection (e.g., `220 ProFTPD 1.3.5 Server`). Nmap captures this banner and attempts to match it against its signature database.
2. **Probing Sequence:** If the Null Probe yields no banner or an inconclusive one, Nmap begins sending a series of protocol-specific probes (HTTP GET requests, SSL client hellos, SMB negotiate requests, custom binary payloads) defined in the `nmap-service-probes` file.
3. **Response Analysis:** The target's response to these probes is collected and compared against thousands of regular expression signatures.
4. **Fallback:** If a service cannot be identified, Nmap prints the raw fingerprint and invites the user to submit it to the Nmap project to improve the database.

### Intensity Levels

Service detection can take time, especially against non-standard or heavily filtered services. Nmap allows you to control the thoroughness using the `--version-intensity` flag, which accepts a value from 0 to 9 (default is 7).

- **Intensity 0 (Light):** Only sends the Null Probe and a few highly specific probes. Very fast, but less accurate. Equivalent to `--version-light`.
- **Intensity 9 (All):** Sends every single probe in the database to every open port. Very slow, but highest chance of identifying obscure services. Equivalent to `--version-all`.

### Example Command
```bash
# Standard service detection with default intensity
nmap -sV -p 22,80,443 10.10.10.5

# High intensity service detection for obscure ports
nmap -sV --version-all -p 8080,8443,9000 10.10.10.5
```

### The `nmap-service-probes` File
Understanding this file is critical for advanced users. It dictates exactly how Nmap interacts with unknown ports. A typical entry looks like this:
```
Probe TCP GetRequest q|GET / HTTP/1.0\r\n\r\n|
match http m|^HTTP/1\.[01] \d\d\d .*\r\nServer: Apache/([\d.]+)| p/Apache httpd/ v/$1/
```
This tells Nmap to send a specific HTTP GET request and provides a regex to match the Server header, extracting the version number for the output.

## Operating System (OS) Detection (`-O`)

OS Detection attempts to identify the target's operating system (e.g., Windows 10, Linux Kernel 5.4, Cisco IOS) by sending a series of crafted TCP, UDP, and ICMP packets and analyzing the subtle differences in how the target's TCP/IP stack responds. This technique is known as **TCP/IP stack fingerprinting**.

### The Mechanics of Stack Fingerprinting

RFCs define how protocols *should* behave, but different developers implement these protocols slightly differently in their operating systems. Nmap exploits these implementation variations. Key metrics analyzed include:

- **Initial Sequence Number (ISN) Generation:** How random are the sequence numbers? (e.g., completely random, tied to time, sequential). Older systems had highly predictable ISNs, whereas modern systems use complex PRNGs.
- **TCP Options:** Which options (MSS, Window Scale, SACK Permitted, Timestamps) are supported and in what order are they arranged in the packet header? The ordering is often uniquely distinct across OS families.
- **Window Size:** The default TCP window size specified in the initial SYN/ACK.
- **IP ID Field:** How the IP Identification field increments (incremental, random, all zeros). This is critical for Idle Scanning.
- **ICMP Handling:** How the OS responds to malformed ICMP requests, quotes back original IP headers in error messages, or rate limits ICMP errors.
- **DF Bit:** Whether the "Don't Fragment" bit is set by default on generated packets.

Nmap aggregates these responses into a massive fingerprint and compares it against the `nmap-os-db`, a database containing thousands of OS fingerprints.

### Requirements for Accurate OS Detection
For the highest accuracy, Nmap OS detection requires at least:
1. One **open** TCP port.
2. One **closed** TCP port.
If these conditions are not met, Nmap will still attempt to guess the OS, but it will display a lower confidence score (e.g., "Aggressive OS guesses").

### IPv6 OS Detection
With the `-6` flag, Nmap performs IPv6 OS detection. Because IPv6 handles fragmentation and ICMP differently than IPv4, a completely separate set of probes and a different database (`nmap-os-db-ipv6`) are used. IPv6 fingerprinting leverages advanced features like IPv6 extension headers.

### Advanced OS Detection Options
- `--osscan-guess` or `--fuzzy`: Instructs Nmap to guess the OS more aggressively if an exact match is not found.
- `--osscan-limit`: Limits OS detection to targets where at least one open and one closed TCP port are found, saving time on heavily filtered hosts.
- `--max-os-tries`: Sets the maximum number of times Nmap tries to determine the OS against a difficult target.

### Example Command
```bash
# Run OS detection, requiring root privileges
sudo nmap -O 10.10.10.5
```

## The "Aggressive" Scan (`-A`)

For convenience, Nmap provides the `-A` flag, often referred to as an "Aggressive" scan. This single flag enables a comprehensive suite of enumeration techniques simultaneously:

1. Service Version Detection (`-sV`)
2. Operating System Detection (`-O`)
3. Script Scanning (`-sC` / Default NSE scripts)
4. Traceroute (`--traceroute`)

```bash
nmap -A -T4 -p- 10.10.10.5
```
*Note: While powerful, `-A` is extremely noisy and easily detected by any competent IDS/IPS. It should be used cautiously in stealth-oriented red team engagements.*

## Visualizing Service Detection Flow

```ascii
+-------------------+                                  +-------------------+
|      Scanner      |                                  |   Target System   |
|     (Nmap -sV)    |                                  |    (Port 80)      |
+-------------------+                                  +-------------------+
          |                                                      |
          |       1. TCP Connection Established                  |
          |----------------------------------------------------->| (3-way handshake)
          |                                                      |
          |       2. Null Probe (Wait for banner)                |
          |<-----------------------------------------------------| (Timeout or Banner)
          |                                                      |
          |       3. Send HTTP GET Request Probe                 |
          |-------- "GET / HTTP/1.0\r\n\r\n" ------------------->|
          |<------- "HTTP/1.1 200 OK\r\nServer: Apache/2.4" -----|
          |                                                      |
          |       4. Signature Matching                          |
          |  [Matches regex for Apache 2.4 in nmap-service-probes]
          |                                                      |
+-------------------+                                  +-------------------+
```

## Practical Considerations and Pitfalls

- **SSL/TLS Wrappers:** Many services are wrapped in SSL/TLS. Nmap automatically detects SSL and will negotiate a connection to extract the SSL certificate (revealing hostnames and dates) before attempting service detection on the underlying encrypted protocol (e.g., identifying HTTP running over SSL as HTTPS).
- **Deception and Banners:** Administrators can easily alter service banners (e.g., making Apache claim to be IIS) to confuse attackers. Nmap's deeper protocol probes often bypass simple banner manipulation, but advanced honeypots can spoof complete TCP/IP stacks to trick Nmap's OS detection.
- **Firewall Interference:** Stateful firewalls may drop malformed packets used in OS fingerprinting, skewing the results and lowering Nmap's confidence score.
- **Load Balancers & Proxies:** Scanning through a load balancer or reverse proxy will result in the OS and Service fingerprints of the *proxy*, not the backend server. The proxy terminates the TCP connection and establishes a new one, masking the true target's stack.
- **Virtualization:** Nmap can often determine if an OS is running as a virtual machine (e.g., detecting VMware or VirtualBox network adapter MAC OUIs, or slight timing differences).

## Defending Against OS and Service Detection

- **Banner Grabbing Defense:** Strip unnecessary banners from services (e.g., configuring `ServerTokens Prod` in Apache).
- **TCP/IP Obfuscation:** Tools like `IP Personality` or advanced `iptables` rules can alter the TCP/IP stack behavior, forcing the system to return an ISN sequence or TTL values that mimic a different operating system, thereby sending attackers down a false path.

## Chaining Opportunities
- **Vulnerability Searching:** Once specific software versions are identified (e.g., `Apache 2.4.49`), this information is fed directly into vulnerability databases like SearchSploit or the NVD to find relevant CVEs and exploits.
- **Targeted NSE Scripts:** Knowing the exact service allows testers to run highly targeted Nmap scripts. For example, if SMB version 1 is detected, the tester will immediately chain this with `smb-vuln-ms17-010` to check for EternalBlue. See [[04 - Nmap Scripting Engine NSE Basics]].

## Related Notes
- [[02 - Nmap Port Scanning Techniques TCP UDP]]
- [[04 - Nmap Scripting Engine NSE Basics]]
