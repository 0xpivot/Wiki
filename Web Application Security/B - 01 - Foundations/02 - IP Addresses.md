---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.02 IP Addresses (IPv4 and IPv6)"
---

# 01.02 — IP Addresses (IPv4 and IPv6)

## What is it?

An **IP address** (Internet Protocol address) is a unique number assigned to every device on a network. It works like a home address — without it, data packets have nowhere to go.

**Analogy:** If the internet is a city, IP addresses are house numbers. You can't deliver a letter without knowing the house number.

---

## IPv4 — The Common One

IPv4 addresses are **32-bit numbers** written as 4 groups of numbers separated by dots.

```
192  .  168  .   1   .  100
 │         │    │       │
 └─────────┴────┴───────┘
   4 groups (octets), each 0–255
   Total: 256 × 256 × 256 × 256 = ~4.3 billion addresses
```

**Reading an IPv4 address:**
```
IP:   192.168.1.100
      ─────────────
      Decimal format
      Each number = 1 byte (8 bits)
      Range per group: 0 to 255
```

### Binary Representation (how machines actually see it)
```
192      168       1       100
11000000.10101000.00000001.01100100

Pentesters need this for subnet calculations.
```

---

## Classes and Private Ranges

Not all IPs are the same. Some are **public** (reachable from internet), some are **private** (only inside your network).

```
PRIVATE IP RANGES (used inside homes and offices):
┌──────────────────────────────────────────────────────┐
│  10.0.0.0    – 10.255.255.255      /8   Class A      │
│  172.16.0.0  – 172.31.255.255      /12  Class B      │
│  192.168.0.0 – 192.168.255.255     /16  Class C      │
└──────────────────────────────────────────────────────┘

SPECIAL ADDRESSES:
┌──────────────────────────────────────────────────────┐
│  127.0.0.1          Localhost (your own machine)      │
│  127.0.0.0/8        Loopback range                   │
│  0.0.0.0            All interfaces (bind address)    │
│  255.255.255.255    Broadcast (send to everyone)      │
│  169.254.0.0/16     APIPA (no DHCP found — auto IP)  │
│  169.254.169.254    AWS/GCP/Azure Metadata Server ←  │
│                     (Critical for SSRF attacks!)      │
└──────────────────────────────────────────────────────┘
```

---

## Subnet Masks and CIDR Notation

A subnet mask tells you which part of an IP is the **network** and which part is the **host**.

```
IP Address:    192.168.1.100
Subnet Mask:   255.255.255.0
               ─────────────
               255 = network part (fixed)
               0   = host part (can change)

This means: network is 192.168.1.x
            hosts are  192.168.1.1 to 192.168.1.254
```

**CIDR notation (shorthand for subnet mask):**
```
192.168.1.0/24

/24 = 24 bits are the network part
    = 255.255.255.0 in subnet mask
    = 254 usable hosts

Common CIDR values:
/8   → 255.0.0.0       → 16,777,214 hosts  (huge — Class A)
/16  → 255.255.0.0     → 65,534 hosts      (large — Class B)
/24  → 255.255.255.0   → 254 hosts         (small — Class C, home networks)
/25  → 255.255.255.128 → 126 hosts
/30  → 255.255.255.252 → 2 hosts           (point-to-point links)
/32  → 255.255.255.255 → 1 host            (single IP)
```

**CIDR cheat sheet:**
```
/24 → 256 IPs  (192.168.1.0   – 192.168.1.255)
/25 → 128 IPs  (192.168.1.0   – 192.168.1.127)
/26 → 64 IPs   (192.168.1.0   – 192.168.1.63)
/27 → 32 IPs
/28 → 16 IPs
/29 → 8 IPs
/30 → 4 IPs    (2 usable)
```

---

## How Nmap Uses CIDR (VAPT Context)

```bash
# Scan a single host
nmap 192.168.1.100

# Scan entire /24 subnet (254 hosts)
nmap 192.168.1.0/24

# Scan a range
nmap 192.168.1.1-50

# Useful in internal pentest: discover all live hosts
nmap -sn 10.10.10.0/24    ← ping sweep, no port scan
```

---

## IPv6 — The New Version

IPv4 is running out of addresses (~4.3 billion used up). IPv6 uses **128-bit addresses** — enough for every grain of sand on Earth.

```
IPv6 format:
2001:0db8:85a3:0000:0000:8a2e:0370:7334

Written as 8 groups of 4 hex digits, separated by colons.

Shorthand rules:
- Leading zeros in a group can be removed
- Consecutive all-zero groups replaced with ::

Full:      2001:0db8:0000:0000:0000:0000:0000:0001
Short:     2001:db8::1
```

**IPv6 Special Addresses:**
```
::1              → Localhost (same as 127.0.0.1)
::               → All zeros (unspecified)
fe80::/10        → Link-local (auto-assigned, not routed)
fc00::/7         → Unique local (private, like RFC1918)
2001:db8::/32    → Documentation range (examples only)
ff02::1          → All nodes multicast
```

---

## NAT — Network Address Translation

Your home has one public IP, but multiple devices. **NAT** is how your router makes this work.

```
INTERNET
   │
   │  Public IP: 203.0.113.42  (your ISP gives you this)
   ▼
[HOME ROUTER]
   │
   ├── 192.168.1.100  (your PC)
   ├── 192.168.1.101  (your phone)
   └── 192.168.1.102  (your TV)

When your PC sends a request to Google:
  PC            → Router: "I'm 192.168.1.100, going to 8.8.8.8"
  Router        → Internet: "I'm 203.0.113.42, going to 8.8.8.8"  ← NAT replaces private IP
  Google        → Router: "Reply to 203.0.113.42"
  Router        → PC: "Here's your reply, 192.168.1.100"         ← NAT reverses it
```

**Why this matters for VAPT:**
- You can't directly reach internal IPs (192.168.x.x) from the internet
- Once inside a network (via SSRF, LFI, etc.), you CAN reach internal IPs
- Cloud metadata server `169.254.169.254` is only reachable from inside the cloud instance

---

## Hands-On: IP Address Commands

```bash
# Show your IP addresses (Linux)
ip addr show
ip addr show eth0       ← specific interface

# Older command (still works)
ifconfig

# Windows
ipconfig
ipconfig /all           ← includes MAC, DNS, DHCP info

# Find public IP
curl ifconfig.me
curl ipinfo.io

# Ping by IP
ping 8.8.8.8

# Find IP of a domain
nslookup google.com
dig google.com          ← more detail

# Resolve an IP back to hostname
nslookup 8.8.8.8
dig -x 8.8.8.8
```

**Sample `ip addr` output:**
```
1: lo: <LOOPBACK,UP,LOWER_UP>
    inet 127.0.0.1/8 scope host lo       ← loopback

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.100/24                 ← your LAN IP
    inet6 fe80::a00:27ff:fe4e:66a1/64    ← IPv6 link-local
```

---

## Security Context — Why IP Addresses Matter in VAPT

```
1. RECON — Finding the attack surface
   ─────────────────────────────────
   nmap -sn 10.0.0.0/8        ← find all live hosts in internal network
   nmap 192.168.1.0/24        ← scan local subnet

2. SSRF — Server-Side Request Forgery
   ───────────────────────────────────
   Target: http://target.com/fetch?url=http://192.168.1.1/admin
   If server makes this request → attacker accesses internal IP

   Cloud SSRF target:
   http://169.254.169.254/latest/meta-data/iam/security-credentials/
   ← AWS metadata server, gives you IAM credentials!

3. IP SPOOFING — Bypassing IP-Based Access Controls
   ──────────────────────────────────────────────────
   X-Forwarded-For: 127.0.0.1    ← pretend to be localhost
   X-Forwarded-For: 10.0.0.1     ← pretend to be internal IP
   
   Many apps trust these headers → bypass IP allowlists

4. LOCALHOST BYPASS — SSRF Filter Evasion
   ─────────────────────────────────────────
   127.0.0.1       ← standard localhost
   127.1           ← short form (works in Linux)
   2130706433      ← decimal form of 127.0.0.1
   0x7f000001      ← hex form
   0177.0.0.1      ← octal form
   [::1]           ← IPv6 localhost
   [0:0:0:0:0:0:0:1]  ← full IPv6 localhost
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Internal IPs exposed via SSRF | Block requests to RFC1918 ranges server-side |
| IP-based auth bypass via headers | Never trust X-Forwarded-For from untrusted sources |
| Metadata server accessible | Use IMDSv2 on AWS (requires token), firewall 169.254.169.254 |
| Flat network (all IPs reachable) | Network segmentation with VLANs and firewall rules |

---

## Related Notes
- [[01 - What is a Network]] — networking foundations
- [[03 - MAC Addresses]] — layer 2 addressing
- [[04 - Subnets and CIDR]] — subnetting deep dive
- [[13 - SSRF]] — abusing 169.254.169.254 and internal IPs
- [[21 - Port Scanning with Nmap]] — scanning IP ranges
