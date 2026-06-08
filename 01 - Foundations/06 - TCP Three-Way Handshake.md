---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.06 TCP — Three-Way Handshake"
---

# 01.06 — TCP — Three-Way Handshake

## What is it?

**TCP (Transmission Control Protocol)** is the protocol that guarantees reliable, ordered delivery of data between two devices. Before any data is sent, TCP performs a **three-way handshake** to establish a connection.

**Analogy:** Before a phone call, both sides confirm they can hear each other:
- You: "Hello, can you hear me?" (SYN)
- Them: "Yes I can, can you hear me?" (SYN-ACK)
- You: "Yes!" (ACK)
- Now you both talk (data transfer)

---

## The Three-Way Handshake

```
CLIENT                              SERVER
  │                                   │
  │──── SYN (seq=100) ───────────────→│
  │     "I want to connect,           │
  │      my sequence number is 100"   │
  │                                   │
  │←─── SYN-ACK (seq=300, ack=101) ──│
  │     "OK, acknowledged your 100,   │
  │      my sequence number is 300"   │
  │                                   │
  │──── ACK (ack=301) ───────────────→│
  │     "Acknowledged your 300,       │
  │      connection established!"     │
  │                                   │
  │══════ DATA TRANSFER ══════════════│
  │                                   │
```

**The flags:**
```
SYN     = Synchronize — "I want to start a connection"
ACK     = Acknowledge — "I received your data"
SYN-ACK = Both flags set — "I accept and also want to sync"
FIN     = Finish — "I want to close the connection"
RST     = Reset — "Something went wrong, closing immediately"
PSH     = Push — "Send this data immediately, don't buffer"
URG     = Urgent — "This data is urgent"
```

---

## Connection Termination (4-Way)

Closing a TCP connection requires 4 steps (FIN handshake):

```
CLIENT                              SERVER
  │                                   │
  │──── FIN ─────────────────────────→│  "I'm done sending"
  │                                   │
  │←─── ACK ──────────────────────────│  "Got it"
  │                                   │
  │←─── FIN ──────────────────────────│  "I'm done too"
  │                                   │
  │──── ACK ─────────────────────────→│  "Got it, bye"
  │                                   │
       Connection fully closed
```

---

## TCP States

```
LISTEN      ← Server waiting for connections (port is open)
SYN_SENT    ← Client sent SYN, waiting for SYN-ACK
SYN_RCVD    ← Server received SYN, sent SYN-ACK
ESTABLISHED ← Connection active, data flowing
FIN_WAIT_1  ← Sent FIN, waiting
FIN_WAIT_2  ← Received ACK of FIN
CLOSE_WAIT  ← Received FIN, waiting to close
TIME_WAIT   ← Waiting to ensure remote received final ACK
CLOSED      ← No connection
```

```bash
# See all TCP connections and their states
ss -tn
netstat -tn

# Sample output:
# ESTAB  0  0  192.168.1.100:54231  8.8.8.8:443      ← active HTTPS
# LISTEN 0  0  0.0.0.0:22                             ← SSH waiting
# TIME_WAIT 0  0  192.168.1.100:54200  1.1.1.1:80     ← closing
```

---

## Sequence Numbers — How TCP Tracks Data

Each byte of data gets a sequence number. This is how TCP:
- Detects missing data (requests retransmit)
- Reassembles data in the right order
- Prevents replay attacks

```
Client sends: "Hello World" (11 bytes)
  Seq=100: H
  Seq=101: e
  Seq=102: l
  ...
  Seq=110: d

Server acknowledges: ACK=111  ← "I received up to byte 110, send me 111 next"
```

---

## Security Context — TCP in VAPT

### 1. Nmap Port Scanning — Uses TCP Handshake

```bash
# TCP Connect Scan — completes full handshake (noisy, logged)
nmap -sT target

# SYN Scan (Half-open) — sends SYN, reads SYN-ACK, sends RST
# Never completes handshake → stealthier, less likely to be logged
nmap -sS target       ← default when run as root

# How SYN scan works:
Client ──SYN──→ Server
Client ←SYN-ACK── Server  ← port is OPEN
Client ──RST──→ Server    ← reset instead of completing

Client ──SYN──→ Server
Client ←RST── Server      ← port is CLOSED

Client ──SYN──→ Server
(no response / ICMP unreachable) ← port is FILTERED (firewall)
```

### 2. TCP Session Hijacking

If an attacker can predict or sniff sequence numbers, they can inject data into an existing TCP session.

```
[Client] ══════════════════════════════ [Server]
         seq=1000 ──────────────────→
         ←────────────── ack=1001

[Attacker sniffs seq=1000, ack=1001]
[Attacker injects]
         seq=1001, fake data ────────→ [Server accepts it!]
```

**Modern mitigation:** Sequence numbers are randomized (ISN — Initial Sequence Number randomization). TLS also prevents injection even if sequence numbers are known.

### 3. SYN Flood — DoS Attack

Attacker sends thousands of SYN packets with spoofed source IPs. Server allocates resources for each, fills up the SYN backlog, legitimate connections fail.

```
Attacker (spoofed IPs) ──SYN──→ Server × 100,000
Server allocates half-open connections × 100,000
Server runs out of resources
Legitimate users ──SYN──→ Server (no response — DoS)
```

**Mitigation:** SYN cookies — server doesn't allocate resources until ACK received.

### 4. RST Injection — Killing Connections

If an attacker can inject a RST packet with the right sequence number, they can terminate any TCP connection.

```
[Great Firewall of China uses this to kill "blocked" connections]
User ──SYN──→ Blocked Site
User ←SYN-ACK──
GFW injects RST ──→ User   ← kills the connection
```

### 5. Wireshark — Capturing the Handshake

```bash
# Capture TCP handshake to google.com
tcpdump -i eth0 -n 'host 142.250.182.46 and tcp'

# Filter for just handshake packets
tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn|tcp-ack) != 0'
```

**Wireshark display filter for handshakes:**
```
tcp.flags.syn == 1              ← all SYN packets
tcp.flags.syn == 1 && tcp.flags.ack == 0  ← only initial SYN
tcp.flags.fin == 1              ← all FIN packets
tcp.flags.rst == 1              ← all RST packets (connection resets)
```

---

## Hands-On: Watching a TCP Handshake

```bash
# Terminal 1: capture traffic
sudo tcpdump -i eth0 -n port 80 -S

# Terminal 2: make a request
curl http://example.com

# You'll see:
# 12:01:01 IP 192.168.1.100.54321 > 93.184.216.34.80: Flags [S],  seq 1234567
# 12:01:01 IP 93.184.216.34.80 > 192.168.1.100.54321: Flags [S.], seq 8765432, ack 1234568
# 12:01:01 IP 192.168.1.100.54321 > 93.184.216.34.80: Flags [.],  ack 8765433
# ↑ S = SYN   S. = SYN-ACK   . = ACK
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| SYN flood DoS | Enable SYN cookies, rate-limit SYN packets |
| Port scanning via SYN scan | Deploy IDS/IPS, log half-open connections |
| TCP session hijacking | Use TLS (encrypts and authenticates data) |
| RST injection | Use TLS (RST injection on encrypted stream has no effect) |
| Half-open connections clogging server | Tune SYN backlog, set timeout values |

---

## Related Notes
- [[05 - Ports and Protocols]] — what ports are
- [[07 - UDP Connectionless Communication]] — TCP's counterpart
- [[17 - TLS SSL How HTTPS Works]] — TCP + encryption
- [[21 - Port Scanning with Nmap]] — SYN scanning in VAPT
