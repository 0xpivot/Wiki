---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.06 Wireshark Basics and Packet Capture Analysis"
---

# Wireshark Basics and Packet Capture Analysis

## Introduction to Wireshark
Wireshark is the undisputed industry standard when it comes to network protocol analyzers. For Penetration Testers, Security Analysts, and Network Engineers, it provides microscopic visibility into network traffic. It is an indispensable tool that operates in promiscuous mode (when capturing over a shared medium like a hub or when port mirroring is enabled) to intercept and log traffic passing over a digital network or part of a network.

At its core, Wireshark allows you to examine data from a live network or from a capture file on disk. You can interactively browse the capture data, delving down into just the level of packet detail you need. In the context of Vulnerability Assessment and Penetration Testing (VAPT), Wireshark is routinely used to:
- Identify plaintext credentials transmitted over insecure protocols (e.g., HTTP, FTP, Telnet, SMTP).
- Analyze the behavior of malware, ransomware, or Command and Control (C2) beaconing.
- Understand the exact mechanisms of network-based exploits or enumeration scans.
- Reconstruct file transfers and data exfiltration events.
- Debug custom exploitation scripts by verifying the structural integrity of the crafted packets.
- Perform forensic analysis on breached systems to determine the timeline of compromise.

## How Wireshark Works: The Core Components
Wireshark is essentially a GUI front-end that leverages the underlying packet capture library.
- On Unix-like systems, this is `libpcap`.
- On Windows systems, this traditionally was `WinPcap`, but modern installations use `Npcap` (which supports loopback capture, 802.11 WiFi monitor mode, and is generally more robust and actively maintained).

### Promiscuous Mode vs. Monitor Mode
Understanding the difference between promiscuous and monitor mode is fundamental for effective packet capture:
- **Promiscuous Mode:** In a wired network, a Network Interface Card (NIC) normally drops packets that are not destined for its specific MAC address or the broadcast address. When placed in promiscuous mode, the NIC passes *all* traffic it receives to the CPU, regardless of the destination MAC address. However, in modern switched environments, promiscuous mode on a standard switch port will only see broadcast traffic, multicast traffic, and traffic destined for that specific port. To see traffic for other devices, you must configure a SPAN (Switched Port Analyzer) or mirror port on the switch, or use a network tap.
- **Monitor Mode:** Specifically applicable to wireless networks (802.11). It allows a computer with a wireless NIC to monitor all traffic received from the wireless network, without associating with an access point or ad-hoc network first. This is critical for capturing wireless handshakes (like WPA2/WPA3 4-way handshakes) for offline cracking.

## Capturing Traffic: The Methodology
Before you click "Start Capture," you need to ensure you are listening on the correct interface and, ideally, applying capture filters to prevent overwhelming your system's resources or disk space.

### Interface Selection
Wireshark will list all available interfaces. This includes physical interfaces (e.g., `eth0`, `enp3s0`, `wlan0`), loopback interfaces (`lo`), and virtual interfaces created by hypervisors or VPNs (`tun0`, `docker0`, `vmnet8`). Selecting the right interface is step zero. For local exploit testing, `lo` is often used. For external attacks, `eth0` or `tun0` (if pivoting over a VPN) is typical.

### Capture Filters (BPF Syntax)
Capture filters are applied *before* the traffic is stored in memory or on disk. They are highly efficient because they run in the kernel (via BPF - Berkeley Packet Filter). If you know exactly what you are looking for, applying a capture filter saves vast amounts of processing power.

The BPF syntax is simple and powerful.
**Primitives:**
- `host`: Filters by IP address (e.g., `host 192.168.1.100`).
- `net`: Filters by subnet (e.g., `net 10.0.0.0/24` or `net 10.0.0.0 mask 255.255.255.0`).
- `port`: Filters by port number (e.g., `port 80`).
- `portrange`: Filters a range of ports (e.g., `portrange 1024-65535`).

**Qualifiers:**
- Directional: `src` (source) or `dst` (destination). (e.g., `src host 10.10.10.5`).
- Protocol: `tcp`, `udp`, `icmp`, `arp`.

**Logical Operators:**
- `and` (`&&`)
- `or` (`||`)
- `not` (`!`)

**Examples of Capture Filters:**
1. Capture all traffic going to or from a specific IP:
   `host 192.168.1.50`
2. Capture only HTTP traffic (assuming standard port):
   `tcp port 80`
3. Capture traffic originating from a specific subnet, but ignore SSH traffic:
   `src net 192.168.1.0/24 and not tcp port 22`
4. Capture ICMP (Ping) traffic only:
   `icmp`

## Display Filters: The Art of Finding the Needle
While capture filters dictate what gets recorded, display filters dictate what is currently visible on the screen. Display filters are much more granular than capture filters. They understand the intricacies of hundreds of protocols. Because they are applied *after* capture, they are computationally more expensive but infinitely more flexible.

Wireshark's display filter engine allows you to filter on almost any field of any protocol.

### Syntax and Operators
Display filters use a dot-notation for protocol fields.
- `==` or `eq`: Equal
- `!=` or `ne`: Not equal
- `>` or `gt`: Greater than
- `<` or `lt`: Less than
- `>=` or `ge`: Greater than or equal to
- `<=` or `le`: Less than or equal to
- `contains`: Checks if a protocol, field, or byte sequence contains a value.
- `matches`: Uses Perl Compatible Regular Expressions (PCRE).

### Common Display Filters for VAPT
1. **Filtering by IP:**
   - `ip.addr == 192.168.1.50` (Source or Destination)
   - `ip.src == 10.0.0.5`
   - `ip.dst == 10.0.0.10`

2. **Filtering by Protocol:**
   - `tcp`
   - `udp`
   - `http`
   - `dns`
   - `smb2`
   - `tls`

3. **Filtering by Port:**
   - `tcp.port == 443`
   - `udp.dstport == 53`

4. **Hunting for Cleartext Credentials:**
   - `http.request.method == "POST"` (Often used for login forms)
   - `ftp.request.command == "USER" or ftp.request.command == "PASS"`
   - `telnet` (Inspect the raw data stream)
   - `pop.request.command == "USER" or pop.request.command == "PASS"`

5. **Analyzing HTTP Traffic:**
   - `http.request.uri contains "admin"`
   - `http.response.code == 200`
   - `http.response.code >= 400` (Find errors, potentially indicative of scanning or exploitation attempts like directory traversal)
   - `http.host matches "\.onion$"` (Detecting Tor hidden service traffic if unencrypted proxies are used)

6. **Analyzing DNS Traffic:**
   - `dns.qry.name contains "maliciousdomain.com"`
   - `dns.flags.response == 0` (DNS Queries)
   - `dns.flags.response == 1` (DNS Responses)
   - `dns.qry.type == 252` (AXFR - Zone Transfer attempts)
   - `dns.flags.rcode != 0` (Find DNS errors like NXDOMAIN, useful for identifying DGA activity)

7. **Identifying Network Scans:**
   - TCP SYN Scan (Stealth): `tcp.flags.syn == 1 and tcp.flags.ack == 0`
   - TCP Connect Scan: `tcp.flags.syn == 1 and tcp.flags.ack == 1` (Looking at the response)
   - Null Scan: `tcp.flags == 0x000`
   - XMAS Scan: `tcp.flags.fin == 1 and tcp.flags.push == 1 and tcp.flags.urg == 1`
   - UDP Scan: `icmp.type == 3 and icmp.code == 3` (Destination Unreachable, Port Unreachable - indicates a closed UDP port being scanned)

## Advanced Analysis Techniques

### Following the Stream
One of the most powerful features in Wireshark is the ability to "Follow Stream." When you identify a packet of interest, right-clicking it and selecting "Follow -> TCP Stream" (or UDP, HTTP, TLS) will reassemble the entire session payload into a readable format.
This is incredibly useful for:
- Reading the full HTTP request and response, including headers and body data (like JSON payloads or uploaded files).
- Viewing the back-and-forth communication of a Telnet or FTP session, easily spotting commands entered by a user or an attacker.
- Inspecting reverse shell traffic to see exactly what commands were executed by an adversary.
- De-chunking chunked HTTP responses automatically to read the underlying text.

### Exporting Objects
If files were transferred over unencrypted protocols (HTTP, FTP, SMB, TFTP), Wireshark can carve them out of the packet capture and save them to disk.
Go to `File -> Export Objects -> HTTP...` (for example). Wireshark will present a list of all files seen in the capture. You can save them locally to analyze them further. This is critical for incident response (e.g., extracting dropped malware) or data exfiltration analysis.

### Decrypting TLS/SSL Traffic
Modern networks are heavily encrypted. By default, you cannot see the contents of HTTPS traffic. However, if you possess the server's private RSA key (and Diffie-Hellman ephemeral keys are not strictly used, which is rare nowadays) or, more commonly, if you have the client's symmetric session keys, you can decrypt the traffic within Wireshark.

**Using SSLKEYLOGFILE:**
Browsers like Chrome and Firefox can log symmetric TLS session keys to a file if the `SSLKEYLOGFILE` environment variable is set.
1. Set the environment variable: `export SSLKEYLOGFILE=/path/to/sslkeys.log`
2. Start the browser from that same terminal.
3. In Wireshark, go to `Edit -> Preferences -> Protocols -> TLS`.
4. In the "(Pre)-Master-Secret log filename" field, browse to your `sslkeys.log` file.
Wireshark will automatically decrypt the captured TLS traffic, turning it back into visible HTTP (or other underlying protocols) traffic.

### Endpoint and Conversation Analysis
To get a high-level overview of who is talking to whom, use:
- `Statistics -> Endpoints`: Shows all unique MAC, IPv4, IPv6, and UDP/TCP endpoints. Useful for spotting top talkers or rogue devices.
- `Statistics -> Conversations`: Shows the traffic between specific pairs of endpoints. You can quickly see which two IPs transferred the most data.
- `Statistics -> I/O Graphs`: Visual representation of throughput over time, which can visually reveal traffic spikes associated with denial of service or data exfiltration.

## Command-Line Alternative: TShark
TShark is the command-line equivalent of Wireshark. It utilizes the same display filter engine and can read/write the same PCAP/PCAPNG files. TShark is invaluable when working over SSH, integrating into automated scripts, or parsing massive capture files that would cause the GUI to crash due to memory constraints.
Example: Extracting HTTP hostnames from a pcap:
`tshark -r capture.pcap -Y "http.request" -T fields -e http.host`

---

## ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                       Network Packet Flow & Wireshark Capture               |
+-----------------------------------------------------------------------------+

      [Attacker] 10.0.0.5                              [Target Web Server]
          |                                                 10.0.0.50
          | (1) Malicious Payload (HTTP POST)                   |
          |---------------------------------------------------->|
          |                                                     |
          |                                                     |
  ===========================================================================
  [ Shared Network Segment / Switch with SPAN port ]
  ===========================================================================
                                |
                                | (2) Mirrored Traffic
                                v
                +-------------------------------+
                |      Sniffing Workstation     |
                |        (Promiscuous NIC)      |
                |                               |
                |  +-------------------------+  |
                |  |    Capture Filter       |  | <-- (3) Drops irrelevant traffic
                |  |  (BPF: tcp port 80)     |  |         e.g., SSH, ARP
                |  +-------------------------+  |
                |               |               |
                |               v               |
                |  +-------------------------+  |
                |  |       PCAP Engine       |  | <-- (4) Writes to capture.pcapng
                |  |  (libpcap / npcap)      |  |
                |  +-------------------------+  |
                |               |               |
                |               v               |
                |  +-------------------------+  |
                |  |   Wireshark GUI / CLI   |  | <-- (5) Analysts apply Display
                |  |     Display Filters     |  |         Filters (http.request.method=="POST")
                |  |                         |  |         and Follow TCP Stream.
                |  +-------------------------+  |
                +-------------------------------+
```

## Defensive Perspective
While attackers use Wireshark to find vulnerabilities and cleartext data, defenders use it for Incident Response and Threat Hunting.
- **Baseline Creation:** Understanding what "normal" traffic looks like on your network is essential. If you don't know normal, you can't spot abnormal.
- **Malware Analysis:** Detonating malware in a sandbox and capturing the PCAP allows defenders to extract C2 IPs, domain names, and identify the communication protocols used by the adversary.
- **Data Loss Prevention (DLP):** Analyzing large outbound flows to determine if sensitive files were exfiltrated.
- **Network Segmentation Verification:** Ensuring that VLANs and firewalls are properly configured by verifying that traffic from an untrusted zone cannot reach a trusted zone.

## Chaining Opportunities
- **ARP Spoofing/Poisoning:** Sniffing on a switched network requires intercepting traffic. Tools like `arpspoof` or `ettercap` can redirect a target's traffic through your machine, allowing Wireshark to capture it. See [[03 - ARP Spoofing and MITM Attacks]].
- **WiFi Deauthentication & Capture:** Before cracking wireless networks, you use monitor mode to capture the 4-way WPA handshake. Wireshark is used to verify the handshake was successfully captured. See [[22 - Wireless Network Cracking WPA2]].
- **Credential Harvesting to Lateral Movement:** Extracting cleartext HTTP/FTP/Telnet credentials via Wireshark directly leads to lateral movement or privilege escalation. See [[14 - Lateral Movement Techniques]].
- **Exploit Verification:** After firing an exploit payload via Metasploit, you use Wireshark to ensure the payload reached the target and to analyze the exact response. See [[05 - Metasploit Framework Basics]].

## Related Notes
- [[07 - tcpdump Basics and Command Line Sniffing]]
- [[01 - Introduction to Network Protocols]]
- [[12 - Analyzing PCAPs with Zeek and Suricata]]
- [[04 - Man-in-the-Middle MITM Concepts]]
- [[18 - Advanced Protocol Evasion]]
