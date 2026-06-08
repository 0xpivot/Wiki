---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.20 TCP/IP Model"
---

# 01.20 — TCP/IP Model

## What is it?

The **TCP/IP Model** (also called the Internet Model or DoD Model) is the practical, real-world framework that the internet actually uses. Unlike the OSI model (7 layers, conceptual), the TCP/IP model has 4 layers and maps directly to real protocols and implementations.

**OSI is the theory. TCP/IP is the reality.**

---

## TCP/IP vs OSI — Side by Side

```
OSI MODEL (7 layers)          TCP/IP MODEL (4 layers)     PROTOCOLS
─────────────────────────────────────────────────────────────────────
7 Application                 ┐
6 Presentation                ├─ Application Layer        HTTP, HTTPS, FTP, DNS,
5 Session                     ┘                           SSH, SMTP, IMAP, RDP
                                                          SNMP, NTP, Telnet

4 Transport                   ── Transport Layer           TCP, UDP

3 Network                     ── Internet Layer            IP, ICMP, ARP (some
                                                          put ARP here)

2 Data Link                   ┐
1 Physical                    ┘─ Network Access Layer      Ethernet, WiFi (802.11)
                                 (Link Layer)              ARP, MAC addresses
```

---

## TCP/IP Layer Detail

```
┌─────────────────────────────────────────────────────────┐
│            APPLICATION LAYER (Layer 4)                  │
│  Your app talks here. HTTP, DNS, SSH, FTP.              │
│  This is where your data lives before any networking.   │
│  PDU (Protocol Data Unit): MESSAGE or DATA              │
├─────────────────────────────────────────────────────────┤
│             TRANSPORT LAYER (Layer 3)                   │
│  TCP or UDP. Source port + Dest port.                   │
│  TCP: reliable, ordered, connection-based.              │
│  UDP: fast, no guarantee, connectionless.               │
│  PDU: SEGMENT (TCP) or DATAGRAM (UDP)                   │
├─────────────────────────────────────────────────────────┤
│             INTERNET LAYER (Layer 2)                    │
│  IP protocol. Routing between networks.                 │
│  Source IP + Dest IP. IP addressing, routing tables.    │
│  ICMP (ping, traceroute) lives here.                    │
│  PDU: PACKET                                            │
├─────────────────────────────────────────────────────────┤
│          NETWORK ACCESS LAYER (Layer 1)                 │
│  Physical transmission. Ethernet, WiFi.                 │
│  MAC addresses for local delivery.                      │
│  NIC, switches, cables, radio waves.                    │
│  PDU: FRAME                                             │
└─────────────────────────────────────────────────────────┘
```

---

## Encapsulation — How Data Travels Down the Stack

```
APPLICATION LAYER:
  [HTTP DATA: "GET /index.html HTTP/1.1"]

TRANSPORT LAYER adds TCP header:
  [TCP: SrcPort=54321, DstPort=443, Seq=1000] | [HTTP DATA]
  ↑ This becomes a SEGMENT

INTERNET LAYER adds IP header:
  [IP: Src=192.168.1.100, Dst=142.250.182.46] | [TCP SEGMENT]
  ↑ This becomes a PACKET

NETWORK ACCESS LAYER adds Ethernet header+footer:
  [ETH: SrcMAC=AA:BB..., DstMAC=CC:DD..] | [IP PACKET] | [FCS]
  ↑ This becomes a FRAME

Physical: 01001010... (bits on the wire/air)

RECEIVING END — De-encapsulation:
  Frame → remove Ethernet header → Packet
  Packet → remove IP header → Segment
  Segment → remove TCP header → HTTP Data
```

---

## Security Context — TCP/IP Model in VAPT

### Sniffing at Each Layer

```bash
# Capture all layers with Wireshark or tcpdump:
sudo tcpdump -i eth0 -w capture.pcap
# Open in Wireshark — you see ALL layers:
# Frame (Layer 1/2): Ethernet header, source/dest MAC
# Internet Protocol (Layer 3): source/dest IP
# TCP (Layer 4): ports, seq numbers, flags
# HTTP (Layer 7): actual request/response

# Capture only specific layers:
tcpdump -i eth0 arp          # Layer 2 ARP
tcpdump -i eth0 icmp         # Layer 3 ICMP
tcpdump -i eth0 tcp port 80  # Layer 4 + 7 HTTP
```

### Crafting Custom Packets (Scapy)

Scapy lets you build packets layer by layer for attacks/testing:

```python
# Python Scapy — build packets at any layer

from scapy.all import *

# Layer 3+4+7: Custom HTTP packet
pkt = IP(dst="target.com")/TCP(dport=80, flags="S")/Raw(b"GET / HTTP/1.1\r\nHost: target.com\r\n\r\n")
send(pkt)

# SYN flood (Layer 4 DoS)
for i in range(1000):
    pkt = IP(src=RandIP(), dst="target.com")/TCP(dport=80, flags="S")
    send(pkt, verbose=False)

# ARP spoof (Layer 2)
pkt = ARP(pdst="192.168.1.100", psrc="192.168.1.1", op=2)
send(pkt, count=10)

# ICMP ping (Layer 3)
ans = sr1(IP(dst="target.com")/ICMP())
print(ans[IP].src)
```

### Protocol Identification in Capture

```
When analyzing a pcap file, identify layers:

Wireshark filter examples:
  eth.addr == aa:bb:cc:dd:ee:ff    ← Layer 2 (MAC)
  ip.addr == 192.168.1.100         ← Layer 3 (IP)
  tcp.port == 443                  ← Layer 4 (TCP)
  http.request.method == "POST"    ← Layer 7 (HTTP)
  dns.qry.name == "target.com"     ← Layer 7 (DNS)

tcpdump filters:
  tcpdump arp                      ← Layer 2
  tcpdump icmp                     ← Layer 3
  tcpdump tcp                      ← Layer 4
  tcpdump host 192.168.1.100       ← Layer 3
  tcpdump port 80                  ← Layer 4
  tcpdump 'tcp[tcpflags] == tcp-syn' ← SYN packets
```

### Traceroute — Seeing Layer 3 Hops

```bash
# Traceroute shows the IP path through the internet
traceroute target.com

# Output:
# 1  192.168.1.1 (gateway)   1ms
# 2  100.64.0.1  (ISP)       5ms
# 3  203.0.113.1 (ISP core)  10ms
# 4  162.158.x.x (Cloudflare) 15ms
# 5  target.com              20ms

# Each hop = one router = one Layer 3 device
# Time shows latency to each router

# TCP traceroute (bypass ICMP blocks)
traceroute -T target.com    # use TCP SYN
```

---

## Hands-On: Protocol Tools by Layer

```bash
# Layer 2 tools
arp -a                    # ARP cache
arp-scan -l               # scan LAN
ifconfig eth0             # NIC info including MAC

# Layer 3 tools
ip route show             # routing table
ping target.com           # ICMP echo (Layer 3)
traceroute target.com     # Layer 3 path
nmap -sn 192.168.1.0/24   # ICMP host discovery

# Layer 4 tools
nmap -sS target           # TCP SYN scan
nmap -sU target           # UDP scan
nc -lvnp 4444             # TCP listener
ss -tulnp                 # show listening TCP/UDP ports

# Layer 7 tools
curl https://target.com   # HTTP
dig target.com            # DNS
ssh user@target.com       # SSH
```

---

## How to Fix / Secure

| Layer | Attack Type | Defense |
|-------|-------------|---------|
| Application | Injection, auth bypass | SAST, DAST, WAF, code review |
| Transport | SYN flood, port scan | Firewall, rate limiting, SYN cookies |
| Internet | IP spoofing, routing attacks | BCP38 filtering, RPKI |
| Network Access | ARP spoofing, MAC flood | Dynamic ARP Inspection, 802.1X |

---

## Related Notes
- [[19 - OSI Model 7 Layers]] — the 7-layer conceptual model
- [[06 - TCP Three-Way Handshake]] — TCP at transport layer
- [[21 - Packet Structure Reading Raw Traffic]] — reading each layer in a packet
- [[22 - Wireshark Basics]] — visualize all layers in captures
