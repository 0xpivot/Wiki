---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.28 Wireshark tcpdump"
---

# Network Traffic Analysis: Wireshark & tcpdump

## 1. Introduction to Network Traffic Analysis

Network traffic analysis is the foundation of network-level penetration testing, incident response, and protocol debugging. It involves capturing, decoding, and interpreting the raw packets flowing across a network interface. Two of the most ubiquitous and powerful tools for this purpose are Wireshark and tcpdump.

While both tools ultimately perform the same core function—capturing packets via libpcap (or Npcap on Windows)—they serve different use cases. Wireshark is the undisputed king of deep, graphical protocol analysis, whereas tcpdump is the lightweight, CLI-native workhorse ideal for headless servers, quick captures, and pipeline integration. Understanding how to seamlessly pivot between these tools is a hallmark of a skilled network operator.

## 2. Packet Capture Architecture (ASCII Diagram)

```text
+-------------------+      +-------------------+      +-------------------+
|                   |      |                   |      |                   |
|  Network Medium   | ---> | Network Interface | ---> | Operating System  |
| (Ethernet, Wi-Fi) |      | (eth0, wlan0)     |      | Kernel Stack      |
|                   |      |                   |      |                   |
+-------------------+      +-------------------+      +-------------------+
                                                          |
+---------------------------------------------------------+
|
|   +-------------------+      +-----------------------------------------+
+-> | BPF (Berkeley     | ---> | libpcap / Npcap (Packet Capture Library)|
    | Packet Filter)    |      +-----------------------------------------+
    +-------------------+           |                             |
                                    v                             v
                       +-------------------+         +-------------------+
                       | tcpdump (CLI)     |         | Wireshark (GUI)   |
                       | - Fast, headless  |         | - Deep Dissection |
                       | - Scriptable      |         | - Stream Follow   |
                       +-------------------+         +-------------------+
                               |                             |
                               v                             v
                       +-------------------+         +-------------------+
                       | .pcap / .pcapng   | <------ | .pcap / .pcapng   |
                       | File Storage      |         | File Storage      |
                       +-------------------+         +-------------------+
```

## 3. tcpdump Deep Dive

### 3.1 Overview
tcpdump is a command-line packet analyzer. It prints out a description of the contents of packets on a network interface that match a boolean expression. It is essential for capturing traffic on remote, headless Linux servers where a GUI is unavailable. Because it relies heavily on terminal output, it requires the user to have a strong fundamental understanding of network protocols to interpret the raw hex and ASCII dumps.

### 3.2 BPF (Berkeley Packet Filter) Syntax
The true power of tcpdump lies in its filter expressions, based on the BPF syntax. BPF allows you to filter traffic in the kernel before it even reaches user space, making captures highly efficient and minimizing CPU overhead during high-bandwidth captures.

*   **Primitives:** `host`, `net`, `port`, `portrange`.
*   **Qualifiers:** `src`, `dst`.
*   **Protocols:** `tcp`, `udp`, `icmp`, `ip`, `ip6`.
*   **Operators:** `and` (`&&`), `or` (`||`), `not` (`!`).

### 3.3 Key Commands and Flags

```bash
# Capture on a specific interface
sudo tcpdump -i eth0

# Capture and write to a pcap file (Crucial for later Wireshark analysis)
sudo tcpdump -i eth0 -w capture.pcap

# Read from a pcap file
tcpdump -r capture.pcap

# Filter by IP address (source or destination)
sudo tcpdump host 192.168.1.100

# Filter by specific source IP and destination port
sudo tcpdump src 10.0.0.5 and dst port 80

# Capture raw packet data in HEX and ASCII (-X) and be verbose (-v)
sudo tcpdump -i eth0 -v -X port 80

# Do not resolve IP addresses to hostnames (-n) and ports to service names (-nn) (Speeds up capture)
sudo tcpdump -i eth0 -nn

# Capture only TCP SYN packets (useful for detecting port scans)
sudo tcpdump "tcp[tcpflags] & (tcp-syn) != 0"

# Capture HTTP GET requests only (Advanced byte offset filtering)
sudo tcpdump -s 0 -A 'tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420'
```

### 3.4 Use Cases in VAPT
- **Remote Packet Capture:** SSH into a compromised server, run `tcpdump -w out.pcap`, and exfiltrate the file to analyze locally in Wireshark.
- **Monitoring for Callbacks:** Set up a listener on an attacker-controlled VPS to monitor for specific reverse shell callbacks or DNS exfiltration.
- **Troubleshooting Exploits:** Verify if an exploit payload is actually leaving the attacker machine and reaching the target intact by monitoring the local network interface.

## 4. Wireshark Deep Dive

### 4.1 Overview
Wireshark is a graphical network protocol analyzer. It allows interactive browsing of packet data from a live network or a previously saved capture file. Its defining feature is its extensive library of protocol dissectors, which can decode almost any network protocol in existence, from standard HTTP to obscure SCADA protocols used in industrial control systems.

### 4.2 The Interface
- **Packet List Pane:** Displays a summary of each packet captured, color-coded by protocol.
- **Packet Details Pane:** Shows the selected packet dissected into its OSI model layers (Frame, Ethernet, IPv4, TCP, HTTP, etc.). Expanding these trees reveals individual flags and header values.
- **Packet Bytes Pane:** Shows the raw hex and ASCII dump of the selected packet.

### 4.3 Display Filters vs. Capture Filters
*   **Capture Filters (BPF):** Applied *during* capture. Traffic not matching the filter is discarded. Syntax is the same as tcpdump.
*   **Display Filters:** Applied *after* capture or during a live capture to change what is visible on screen. They do not delete data. The syntax is specific to Wireshark (e.g., `ip.addr == 192.168.1.1`, `http.request.method == "POST"`).

### 4.4 Advanced Features
- **Follow TCP/UDP/TLS Stream:** This is arguably Wireshark's most powerful feature for VAPT. Right-clicking a packet and selecting "Follow TCP Stream" reassembles the entire conversation between the client and server, displaying the raw payload (e.g., an entire HTTP request/response cycle, or a plaintext FTP login).
- **Export Objects:** Wireshark can extract files (HTTP, DICOM, SMB, etc.) directly from the captured traffic. If an executable is downloaded over HTTP during a capture, Wireshark can save that `.exe` to your disk for reverse engineering.
- **Statistics and Graphing:** Tools for analyzing endpoints, conversations, I/O graphs, and protocol hierarchy to quickly identify anomalous traffic patterns.

### 4.5 Display Filter Examples

```text
# Show only HTTP traffic
http

# Show HTTP GET requests
http.request.method == "GET"

# Show traffic to or from a specific IP
ip.addr == 10.10.10.50

# Show DNS queries for a specific domain
dns.qry.name == "example.com"

# Show TCP traffic containing a specific string (useful for finding plaintext passwords)
tcp contains "password"
```

### 4.6 Decrypting WPA/WPA2 Wi-Fi Traffic
Wireshark isn't limited to wired networks; it is a powerhouse for wireless analysis. When performing a wireless penetration test, raw 802.11 frames are often captured. If the network uses WPA/WPA2 Personal (PSK), the traffic is encrypted.
To decrypt it in Wireshark:
1. Ensure you have captured the 4-Way EAPOL Handshake (which occurs when a client authenticates to the AP).
2. Go to `Edit` -> `Preferences` -> `Protocols` -> `IEEE 802.11`.
3. Check `Enable decryption`.
4. Click `Edit...` next to Decryption Keys.
5. Add a key of type `wpa-pwd` and input the key in the format `password:SSID`.
Once entered, Wireshark will dynamically decrypt the payload of the 802.11 frames, exposing the underlying IP, TCP, and HTTP traffic just as if you were plugged into an Ethernet port.

## 5. Comparison: tcpdump vs. Wireshark

| Feature | tcpdump | Wireshark |
| :--- | :--- | :--- |
| **Interface** | CLI | GUI (TShark for CLI) |
| **Primary Use** | Fast capture, headless environments | Deep analysis, protocol dissection |
| **Filtering** | BPF Capture Filters | BPF Capture + Advanced Display Filters |
| **Resource Usage** | Extremely low | High (can consume massive RAM for large pcaps) |
| **Stream Reassembly** | Difficult (requires external tools) | Built-in, excellent |

## 6. Workflow Example: The Perfect Pair

The most common workflow in penetration testing involves using both tools in tandem to leverage their respective strengths:

1.  **The Capture (tcpdump):** A penetration tester gains a shell on an internal pivot machine. To map the internal network without active, noisy port scanning, they run tcpdump silently to capture background broadcast, multicast, and routine unicast traffic.
    `tcpdump -i eth1 -w pivot_capture.pcap`
2.  **Exfiltration:** The `pivot_capture.pcap` file is transferred back to the tester's local Kali machine via SCP or an established tunnel.
3.  **The Analysis (Wireshark):** The tester opens `pivot_capture.pcap` in Wireshark. They use display filters and the "Protocol Hierarchy" statistics to identify internal domain controllers, database servers, and plaintext protocols (like Telnet or FTP) in use.

## 7. Conclusion

tcpdump and Wireshark are complementary, indispensable tools. tcpdump is the scalpel—precise, lightweight, scriptable, and perfect for surgical packet capture in restricted environments. Wireshark is the microscope—providing unparalleled visibility, graphical stream reassembly, and deep analytical capabilities for dissecting complex protocol interactions and extracting actionable intelligence from raw data.

## 8. Chaining Opportunities
- Use to analyze the network behavior of exploits developed in [[08 - Exploit Development Basics]].
- Capture authentication handshakes to feed into [[39 - Hashcat John The Ripper]].
- Monitor Out-of-Band (OAST) interactions using [[29 - Interactsh Burp Collaborator]].
- Utilize packet captures to perform man-in-the-middle analysis alongside [[22 - Sniffing and Spoofing]].

## 9. Related Notes
- [[05 - OSI Model and Networking Protocols]]
- [[22 - Sniffing and Spoofing]]
- [[46 - Network Pivoting and Tunneling]]
- [[23 - Post Exploitation Fundamentals]]
