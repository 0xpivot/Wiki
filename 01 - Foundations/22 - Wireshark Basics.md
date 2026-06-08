---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.22 Wireshark Basics"
---

# 01.22 — Wireshark Basics

## What is it?

**Wireshark** is the world's most popular network protocol analyzer (packet sniffer). It captures network traffic and lets you inspect every byte of every packet — in real time or from saved capture files. Essential for debugging, VAPT, CTF challenges, and incident response.

**tshark** = Wireshark's command-line version (same engine, no GUI).

---

## Wireshark Interface

```
┌──────────────────────────────────────────────────────────────┐
│  Menu: File | Edit | View | Go | Capture | Analyze | ...    │
├──────────────────────────────────────────────────────────────┤
│  Display Filter Bar:  [ip.addr == 192.168.1.100         ] ▶ │
├──────────────────────────────────────────────────────────────┤
│  PACKET LIST PANE:                                           │
│  # │ Time   │ Src         │ Dst         │ Proto │ Info       │
│  1 │ 0.000  │ 192.168.1.1 │ 8.8.8.8     │ DNS   │ Std query  │
│  2 │ 0.002  │ 8.8.8.8     │ 192.168.1.1 │ DNS   │ Std resp   │
│  3 │ 0.004  │ 192.168.1.1 │ 93.184.x.x  │ TCP   │ SYN        │
├──────────────────────────────────────────────────────────────┤
│  PACKET DETAILS PANE (click a packet to expand):            │
│  ▼ Frame 3: 74 bytes on wire                                │
│  ▼ Ethernet II: 00:aa:bb... → 00:cc:dd...                  │
│  ▼ Internet Protocol Version 4: 192.168.1.1 → 93.184.x.x   │
│  ▼ Transmission Control Protocol: 54321 → 80 [SYN]         │
├──────────────────────────────────────────────────────────────┤
│  PACKET BYTES PANE (raw hex + ASCII):                       │
│  0000  ff ff ff ff ff ff 00 aa  ....... hex dump .......    │
└──────────────────────────────────────────────────────────────┘
```

---

## Essential Display Filters

```
BASIC FILTERS:
ip.addr == 192.168.1.100       # any traffic to/from this IP
ip.src == 192.168.1.100        # only traffic FROM this IP
ip.dst == 192.168.1.100        # only traffic TO this IP
ip.addr == 192.168.1.0/24      # entire subnet

PROTOCOL FILTERS:
tcp                            # all TCP traffic
udp                            # all UDP traffic
http                           # HTTP traffic (Layer 7 decoded)
https                          # same as ssl / tls
dns                            # DNS queries and responses
arp                            # ARP traffic
icmp                           # ping traffic
smtp                           # email
ftp                            # FTP
ssh                            # SSH (encrypted, but metadata visible)

PORT FILTERS:
tcp.port == 80                 # TCP port 80 (HTTP)
tcp.port == 443                # HTTPS
tcp.dstport == 8080            # destination port 8080
udp.port == 53                 # DNS

TCP FLAG FILTERS:
tcp.flags.syn == 1             # SYN packets (connection starts)
tcp.flags.ack == 1             # ACK packets
tcp.flags.reset == 1           # RST packets (connection reset)
tcp.flags == 0x002             # pure SYN (no ACK) = new connections
tcp.flags == 0x012             # SYN-ACK
tcp.flags == 0x011             # FIN-ACK

CONTENT FILTERS:
http.request.method == "POST"  # POST requests
http.request.uri contains "admin"  # URLs containing "admin"
http.response.code == 200      # successful responses
http.response.code == 401      # unauthorized
http.cookie contains "session" # packets with session cookie
frame contains "password"      # any packet with "password" in payload

COMBINATION FILTERS (use && and ||):
ip.addr == 192.168.1.100 && tcp.port == 80
http && ip.dst == 10.0.0.1
!(arp || icmp || dns)          # exclude noise
```

---

## Key Wireshark Features for VAPT

### 1. Follow Stream

Right-click a packet → Follow → TCP Stream (or HTTP Stream, TLS Stream)

```
Shows full conversation between client and server:

→ GET /login HTTP/1.1
→ Host: target.com
→ Cookie: session=abc123

← HTTP/1.1 200 OK
← Set-Cookie: session=newtoken
← <html>Welcome admin!</html>

Use this to:
- Reconstruct full HTTP sessions
- Find credentials in cleartext
- Understand application logic
- Extract uploaded files
```

### 2. Statistics Menu

```
Statistics → Protocol Hierarchy
→ Shows breakdown: what % of traffic is DNS vs HTTP vs TCP
→ Identify unusual protocols or dominant protocols

Statistics → Conversations
→ See all unique IP pairs that communicated
→ Find most active talkers
→ Identify C2 communication (one IP talking to many others)

Statistics → IO Graph
→ Visualize traffic over time
→ Identify bursts (DDoS), consistent beaconing (C2 implant)

Statistics → DNS
→ All DNS queries in one view
→ Find suspicious domain resolutions (DGA domains)

Statistics → HTTP
→ All HTTP requests/responses
→ Find error codes, specific URIs
```

### 3. Export Objects

```
File → Export Objects → HTTP
→ Extracts ALL files transferred via HTTP
→ Can recover: HTML, images, executables, documents, passwords

File → Export Objects → SMB
→ Extracts files from Windows file share traffic
→ Can recover documents, malware, configurations

Use case: CTF pcap challenge — extract the hidden file
Use case: Incident response — recover malware dropped via HTTP
```

### 4. Decrypting TLS (HTTPS)

```
If you have the server's private key (or session keys from browser):

Method 1: Pre-master secret from browser (best, works for ECDHE):
  - Set env: SSLKEYLOGFILE=/tmp/ssl_keys.log
  - Browse → keys captured automatically
  - Wireshark: Edit → Preferences → Protocols → TLS
    → Set (Pre)-Master-Secret log filename
  - HTTPS is now decrypted!

Method 2: RSA private key (only works if NO forward secrecy):
  Edit → Preferences → Protocols → TLS → RSA Keys
  Add: IP, port, protocol=http, key file=server.key

CAPTURE SETUP:
  SSLKEYLOGFILE=/tmp/ssl.log firefox &
  wireshark -i lo -k -o "tls.keylog_file:/tmp/ssl.log"
```

### 5. Coloring Rules

```
Wireshark colors packets by default:
  Green   = TCP traffic
  Blue    = DNS/UDP
  Black   = TCP errors (retransmissions, RST)
  Light blue = ICMP

Custom coloring for VAPT:
View → Coloring Rules → New
  Name: Login Attempt
  Filter: http.request.uri contains "login"
  Color: Red background
```

---

## tshark — Command Line Wireshark

```bash
# Live capture
sudo tshark -i eth0

# Capture to file
sudo tshark -i eth0 -w capture.pcap

# Read pcap
tshark -r capture.pcap

# Apply display filter
tshark -r capture.pcap -Y "http"
tshark -r capture.pcap -Y "dns"
tshark -r capture.pcap -Y "tcp.flags.syn == 1"

# Extract specific fields
tshark -r capture.pcap -Y "http.request" \
  -T fields -e ip.src -e http.request.method -e http.request.full_uri

# Extract DNS queries
tshark -r capture.pcap -Y "dns.qry.type == 1" \
  -T fields -e dns.qry.name | sort -u

# Extract all HTTP POST bodies
tshark -r capture.pcap -Y "http.request.method == POST" \
  -T fields -e http.file_data

# Statistics
tshark -r capture.pcap -q -z conv,tcp    # TCP conversations
tshark -r capture.pcap -q -z io,phs      # protocol hierarchy

# Follow stream
tshark -r capture.pcap -Y "tcp.stream eq 0" -z follow,tcp,ascii,0
```

---

## VAPT Workflow with Wireshark

### Scenario 1: Capture Credentials from HTTP

```bash
# On same network (after ARP spoof), capture credentials
sudo wireshark -i eth0 &

# Or with tshark:
sudo tshark -i eth0 -Y "http.request.method == POST" \
  -T fields -e http.request.full_uri -e http.file_data

# Look for login POST data containing username/password
```

### Scenario 2: Analyze CTF pcap

```bash
# 1. Open in Wireshark
# 2. Check Statistics → Protocol Hierarchy → what protocols?
# 3. Follow interesting TCP streams
# 4. Export Objects → HTTP → check for files
# 5. Filter for credentials: frame contains "password"
# 6. Check DNS queries for DGA/C2 domains
# 7. Decode any base64 or encoded data
```

### Scenario 3: Detect Anomalies (Blue Team)

```bash
# Find beaconing (regular intervals = C2 implant)
tshark -r capture.pcap -T fields -e frame.time -e ip.dst \
  | sort | uniq -c | sort -rn | head -20

# Find DNS tunneling (very long queries)
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name \
  | awk 'length>50'  # suspicious if > 50 chars

# Find port scans (many SYNs, mostly RST responses)
tshark -r capture.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
  -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn
```

---

## Hands-On: Quick Start

```bash
# Install
sudo apt install wireshark tshark

# Add user to wireshark group (capture without sudo)
sudo usermod -a -G wireshark $USER
newgrp wireshark

# Launch GUI
wireshark

# Quick CLI capture and filter
sudo tshark -i eth0 -Y "not arp and not icmp" -a duration:60 -w lab.pcap
# Capture 60 seconds, exclude ARP and ICMP noise

# Quick analysis on saved file
tshark -r lab.pcap -Y http -T fields -e ip.src -e ip.dst -e http.request.uri 2>/dev/null
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Credentials captured in cleartext | Use TLS/HTTPS for all services |
| MITM enables Wireshark capture | Prevent ARP spoofing (DAI), use encrypted protocols |
| Attacker runs Wireshark on compromised host | Monitor for promiscuous mode NICs, use network segmentation |

---

## Related Notes
- [[21 - Packet Structure Reading Raw Traffic]] — packet structure explained
- [[10 - ARP Address Resolution Protocol]] — ARP spoofing enables capture
- [[06 - TCP Three-Way Handshake]] — TCP flags in Wireshark
- [[Module 35 - Network Protocol Attacks]] — what to look for in captures
- [[Module 53 - Digital Forensics]] — pcap analysis for incident response
