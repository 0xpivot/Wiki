---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.21 Packet Structure — Reading Raw Traffic"
---

# 01.21 — Packet Structure — Reading Raw Traffic

## What is it?

Every message on the internet is broken into **packets** — small chunks of data with headers that tell network devices where to send them, how to reassemble them, and how to handle errors. Understanding packet structure lets you read raw network captures and craft custom packets for testing.

---

## Ethernet Frame Structure (Layer 2)

```
ETHERNET FRAME:
┌──────────┬──────────┬──────────┬──────────────────────────┬─────┐
│ Dst MAC  │ Src MAC  │EtherType │        PAYLOAD           │ FCS │
│ (6 bytes)│ (6 bytes)│ (2 bytes)│     (up to 1500 bytes)   │ 4B  │
└──────────┴──────────┴──────────┴──────────────────────────┴─────┘

EtherType Values:
  0x0800 = IPv4 (most traffic)
  0x0806 = ARP
  0x86DD = IPv6
  0x8100 = 802.1Q VLAN tag

FCS = Frame Check Sequence (CRC error detection)

VAPT SIGNIFICANCE:
  Src MAC → identify device vendor
  Dst MAC = FF:FF:FF:FF:FF:FF → broadcast (ARP requests)
  EtherType 0x0806 → ARP packet (MitM candidate)
```

---

## IP Packet Structure (Layer 3)

```
IPv4 HEADER (20 bytes minimum):
┌─────┬─────┬──────────┬──────────────────┬────────────────────┐
│ Ver │ IHL │   DSCP   │   Total Length   │  Identification    │
│ (4) │ (4) │   (8)    │     (16 bits)    │     (16 bits)      │
├─────┴─────┴──────────┴──────────────────┴────────────────────┤
│  Flags  │    Fragment Offset    │   TTL    │    Protocol      │
│  (3 b)  │      (13 bits)        │  (8 b)  │     (8 bits)     │
├─────────┴───────────────────────┴──────────────────────────  │
│         Header Checksum (16 bits)                            │
├──────────────────────────────────────────────────────────────┤
│              Source IP Address (32 bits)                     │
├──────────────────────────────────────────────────────────────┤
│           Destination IP Address (32 bits)                   │
└──────────────────────────────────────────────────────────────┘
│                      OPTIONS (optional)                      │
│                    DATA / PAYLOAD                            │

KEY FIELDS:
  TTL (Time to Live): decremented by each router. 0 = packet dropped.
    → Different OS defaults: Linux=64, Windows=128, Cisco=255
    → TTL fingerprinting → OS detection!

  Protocol: what's in the payload
    6  = TCP
    17 = UDP
    1  = ICMP

  Flags:
    DF (Don't Fragment): if set, packet must not be fragmented
    MF (More Fragments): more fragments to follow
    Fragment Offset: where this fragment fits in original packet

  ID + Fragment Offset: used to reassemble fragmented packets
```

---

## TCP Segment Structure (Layer 4)

```
TCP HEADER (20 bytes minimum):
┌──────────────────────────────────────────────────────────────┐
│      Source Port (16 bits)  │    Destination Port (16 bits)  │
├──────────────────────────────────────────────────────────────┤
│                  Sequence Number (32 bits)                   │
├──────────────────────────────────────────────────────────────┤
│              Acknowledgment Number (32 bits)                 │
├──────┬─────┬───────────────────────┬────────────────────────┤
│Offset│Rsv'd│     Control Bits      │    Window Size (16b)   │
│ (4b) │ (3) │SYN ACK FIN RST PSH URG│                        │
├──────┴─────┴───────────────────────┴────────────────────────┤
│      Checksum (16 bits)     │    Urgent Pointer (16 bits)   │
├──────────────────────────────────────────────────────────────┤
│                OPTIONS (0-40 bytes)                          │
├──────────────────────────────────────────────────────────────┤
│                      DATA / PAYLOAD                          │
└──────────────────────────────────────────────────────────────┘

KEY FIELDS FOR VAPT:
  Flags (control bits):
    SYN  = Initiate connection
    ACK  = Acknowledge received data
    FIN  = Graceful close
    RST  = Immediate close (abort)
    PSH  = Push data to application immediately
    URG  = Urgent data

  Sequence + ACK numbers: used to track data and detect injection
  Window Size: flow control, can be used for OS fingerprinting

NMAP FLAG COMBINATIONS:
  SYN scan:   [SYN] → open: [SYN,ACK]   closed: [RST]
  NULL scan:  [] → open: no response     closed: [RST]
  FIN scan:   [FIN] → open: no response  closed: [RST]
  XMAS scan:  [FIN,PSH,URG] → same as FIN
```

---

## UDP Datagram Structure (Layer 4)

```
UDP HEADER (8 bytes — very simple):
┌──────────────────────────────────────────────────────────────┐
│    Source Port (16 bits)    │   Destination Port (16 bits)   │
├──────────────────────────────────────────────────────────────┤
│       Length (16 bits)      │       Checksum (16 bits)       │
├──────────────────────────────────────────────────────────────┤
│                      DATA                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Reading a Packet with tcpdump

```bash
# Capture HTTP traffic
sudo tcpdump -i eth0 -n tcp port 80 -A

# Sample output:
# 14:23:45.123456 IP 192.168.1.100.54321 > 93.184.216.34.80: Flags [S] ...
# ^timestamp       ^proto ^src.srcport   ^dst.dstport      ^TCP flags
#
# Decoded:
# 192.168.1.100 = source IP
# 54321 = source port (ephemeral)
# 93.184.216.34 = destination IP (example.com)
# 80 = destination port (HTTP)
# Flags [S] = SYN (starting connection)

# Flags key:
# [S] = SYN    [.] = ACK    [S.] = SYN-ACK
# [F] = FIN    [R] = RST    [P.] = PSH-ACK (data)

# Show packet contents (-A = ASCII, -X = hex+ASCII):
sudo tcpdump -i eth0 -n -X tcp port 80
```

---

## Security Context — Reading Packets in VAPT

### 1. Extracting HTTP from a Capture

```bash
# Capture HTTP and show payload
sudo tcpdump -i eth0 -A -s 0 tcp port 80 | grep -E "GET|POST|Cookie|Set-Cookie|Authorization"

# Extract HTTP from pcap file
tcpdump -r capture.pcap -A tcp port 80

# Better: use Wireshark "Follow TCP Stream"
# Select a packet → Right-click → Follow → TCP Stream
# Shows full HTTP request + response as text
```

### 2. TTL Fingerprinting

```bash
# Ping a target — check TTL in response
ping target.com
# 64 bytes from 142.250.182.46: ttl=116 time=12.5 ms
# TTL=116 → started at 128 (Windows) → 12 hops away

# Nmap OS detection (uses TTL + TCP fingerprint)
nmap -O target
```

### 3. Custom Packet Crafting for Firewall Bypass

```python
from scapy.all import *

# Craft fragmented packet (evade basic packet-filter firewalls)
# Firewall sees fragment 1 with no flags → allows
# Firewall sees fragment 2 → allows (no context)
# Reassembled = attack payload

pkt = IP(dst="target.com", flags="MF")/TCP(dport=80, flags="S")
send(pkt)

# NULL scan (no flags — some firewalls only block SYN)
pkt = IP(dst="target.com")/TCP(dport=80, flags=0)
sr1(pkt, timeout=1)

# XMAS scan (FIN + PSH + URG)
pkt = IP(dst="target.com")/TCP(dport=80, flags="FPU")
sr1(pkt, timeout=1)
```

### 4. PCAP Analysis — CTF / Incident Response

```bash
# Open pcap in Wireshark
wireshark capture.pcap

# Key Wireshark features:
# Statistics → Protocol Hierarchy  → see what protocols in the capture
# Statistics → Conversations       → see who talked to whom
# File → Export Objects → HTTP     → extract files from HTTP traffic
# File → Export Objects → SMB      → extract files from SMB traffic

# tcpdump one-liners for pcap analysis:
# Show unique IPs:
tcpdump -r capture.pcap -n | awk '{print $3}' | cut -d. -f1-4 | sort -u

# Show all DNS queries:
tcpdump -r capture.pcap -n port 53 | grep -oP 'A\? \K[^ ]+'

# Show all HTTP requests:
tcpdump -r capture.pcap -A port 80 | grep "GET\|POST\|Host:"

# tshark (Wireshark CLI):
tshark -r capture.pcap -Y "http" -T fields -e ip.src -e http.request.method -e http.request.uri
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | sort -u
```

---

## Hands-On: Packet Commands

```bash
# Capture 100 packets to file
sudo tcpdump -i eth0 -c 100 -w capture.pcap

# Read pcap file
tcpdump -r capture.pcap -n -A

# Show hex dump of packets
sudo tcpdump -i eth0 -XX -n

# Watch for specific content
sudo tcpdump -i eth0 -A -n tcp port 80 | grep -i password

# Craft and send ping with custom TTL
ping -t 50 target.com  # Windows: set TTL=50
ping -m 50 target.com  # Linux: set TTL=50 (MULTICAST_TTL)

# Python Scapy interactive
sudo python3 -c "from scapy.all import *; sniff(prn=lambda x: x.summary(), count=10)"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Cleartext protocol (HTTP, FTP, Telnet) | Move to encrypted version (HTTPS, SFTP/SCP, SSH) |
| Packet injection possible on LAN | Use encryption, 802.1X authentication, switch port security |
| Fragmentation-based IDS evasion | Configure IDS to reassemble fragments before inspecting |
| TTL-based firewall bypass | Stateful firewall (reassembles context across packets) |

---

## Related Notes
- [[20 - TCP IP Model]] — where packets fit in the model
- [[06 - TCP Three-Way Handshake]] — TCP flags in detail
- [[22 - Wireshark Basics]] — graphical packet analysis
- [[Module 35 - Network Protocol Attacks]] — crafting malicious packets
