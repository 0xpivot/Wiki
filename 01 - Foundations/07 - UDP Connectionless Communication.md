---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.07 UDP — Connectionless Communication"
---

# 01.07 — UDP — Connectionless Communication

## What is it?

**UDP (User Datagram Protocol)** is a transport protocol that sends data without establishing a connection first. Unlike TCP, it doesn't guarantee delivery, ordering, or error checking.

**Analogy:**
- TCP = Registered mail (you get a receipt, tracking, confirmation of delivery)
- UDP = Dropping a flyer in a letterbox (fast, no confirmation, may not arrive)

---

## TCP vs UDP — Side by Side

```
TCP                          UDP
─────────────────────────    ─────────────────────────
Connection-oriented          Connectionless
3-way handshake required     No handshake — just send
Guaranteed delivery          No guarantee
Ordered data                 May arrive out of order
Error checking               Minimal error checking
Slower (overhead)            Faster (no overhead)
Larger header (20 bytes)     Smaller header (8 bytes)
HTTP, SSH, FTP, SMTP         DNS, DHCP, VoIP, Gaming
```

---

## UDP Packet Structure

```
UDP Header (8 bytes — much simpler than TCP's 20 bytes):

 0      7 8     15 16    23 24    31
┌────────┬────────┬────────┬────────┐
│ Source │  Dest  │        │        │
│  Port  │  Port  │ Length │Checksum│
└────────┴────────┴────────┴────────┘
    2B       2B      2B       2B

Then: Data payload follows immediately
```

---

## Common UDP Services (Security Relevant)

```
PORT   SERVICE     ATTACK SURFACE
────────────────────────────────────────────────────────
53     DNS         Zone transfer, DNS rebinding, amplification DoS
67/68  DHCP        Rogue DHCP server → MITM all traffic
69     TFTP        No authentication — read/write files
123    NTP         Amplification DDoS, time spoofing
161    SNMP        Community string brute force, info leak
162    SNMP Trap   Monitoring events — information leakage
500    IKE/IPSec   VPN — aggressive mode identity leak
514    Syslog      Log injection, log forging
1194   OpenVPN     VPN attacks
1900   SSDP        UPnP amplification DDoS
4500   NAT-T       IPSec NAT traversal
5353   mDNS        Network discovery, poisoning
11211  Memcached   Amplification DDoS (massive — 50,000x factor!)
```

---

## Security Context — UDP in VAPT

### 1. UDP Scanning — Often Missed

Most pentesters only scan TCP. UDP services are frequently overlooked — and often misconfigured.

```bash
# UDP scan (slower than TCP — requires timeout)
nmap -sU target
nmap -sU -p 53,67,69,161,500 target

# Top UDP ports
nmap -sU --top-ports 100 target

# Combined TCP + UDP scan
nmap -sS -sU -p T:1-1000,U:53,67,69,161 target

# Nmap output for UDP:
# PORT    STATE         SERVICE
# 53/udp  open          domain
# 69/udp  open|filtered tftp   ← "open|filtered" = no response (common for UDP)
# 161/udp open          snmp
```

**Important:** UDP ports show `open|filtered` when there's no response — Nmap can't tell if filtered or just not responding. Use service-specific probes:
```bash
nmap -sU -p 161 --script snmp-info target    ← confirm SNMP
nmap -sU -p 53  --script dns-recursion target ← confirm DNS
```

### 2. SNMP — Information Goldmine

SNMP (Simple Network Management Protocol) uses UDP 161. With default community strings, it leaks everything about a device.

```bash
# Enumerate SNMP with community string "public" (default)
snmpwalk -v2c -c public target

# Common community strings to try:
# public, private, community, admin, manager, cisco, 0392a0, ILMI

# Get system info
snmpwalk -v2c -c public target 1.3.6.1.2.1.1

# Get running processes
snmpwalk -v2c -c public target 1.3.6.1.2.1.25.4.2

# Get installed software
snmpwalk -v2c -c public target 1.3.6.1.2.1.25.6.3

# Get network interfaces and IP addresses
snmpwalk -v2c -c public target 1.3.6.1.2.1.4.20

# Nmap SNMP scripts
nmap -sU -p 161 --script snmp-brute target        ← brute community strings
nmap -sU -p 161 --script snmp-sysdescr target     ← get system description
nmap -sU -p 161 --script snmp-processes target    ← running processes
```

### 3. TFTP — No Authentication File Access

TFTP (Trivial FTP) on UDP 69 has no authentication. Often used by network devices to store configs.

```bash
# Connect and try to download config files
tftp target
tftp> get startup-config
tftp> get running-config
tftp> get /etc/passwd

# Command line
tftp -g -r cisco-config target    ← download file
```

### 4. DNS Amplification DDoS

Attacker sends small DNS queries with spoofed source IP (victim's IP). DNS server sends large responses to victim.

```
Attacker ──→ DNS Server: "Give me ALL records for target.com"
             Source IP: 192.168.1.1 (victim — spoofed)
             Request: 60 bytes

DNS Server ──→ 192.168.1.1 (victim): Full DNS response
                                      3000 bytes  ← 50x amplification!

Amplification factor: up to 4096x with EDNS
```

### 5. DHCP Starvation + Rogue DHCP

```
Attack 1: DHCP Starvation
  Attacker sends thousands of DHCP Discover requests with fake MACs
  Legitimate DHCP server runs out of IP addresses to assign
  New devices can't get IPs → DoS

Attack 2: Rogue DHCP Server
  Attacker sets up own DHCP server
  Responds faster than legitimate server
  Assigns:
    Default Gateway: attacker's IP  ← all traffic goes through attacker
    DNS Server: attacker's IP       ← attacker controls DNS → phishing
  Result: Full MITM of all new connections
```

```bash
# Tool: Yersinia (DHCP attacks)
yersinia dhcp -attack 1    ← DHCP starvation
```

---

## Hands-On: UDP Tools

```bash
# Send UDP data manually
echo "test" | nc -u target 1234

# Listen on UDP port
nc -ul 1234           ← listen for UDP on port 1234

# Capture UDP traffic
tcpdump -i eth0 -n udp
tcpdump -i eth0 -n udp port 53    ← just DNS

# Test if UDP port is open (basic check)
nmap -sU -p 161 --open target
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Default SNMP community strings | Change to strong random strings, use SNMPv3 with auth |
| TFTP exposed with no auth | Disable TFTP or restrict to specific IPs |
| DNS amplification | Disable recursive DNS for external queries |
| Rogue DHCP | Enable DHCP snooping on managed switches |
| SNMP version 1/2 (cleartext) | Upgrade to SNMPv3 (supports encryption and auth) |

---

## Related Notes
- [[06 - TCP Three-Way Handshake]] — TCP's reliable counterpart
- [[08 - DNS How Domain Names Resolve]] — DNS protocol (UDP 53)
- [[Module 35 - Network Protocol Attacks]] — SNMP, DHCP, DNS attacks
