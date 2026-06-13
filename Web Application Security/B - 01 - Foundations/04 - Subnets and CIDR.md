---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.04 Subnets and CIDR Notation"
---

# 01.04 — Subnets and CIDR Notation

## What is it?

A **subnet** (subnetwork) is a smaller network carved out of a larger one. Instead of one big network where every device can talk to every other device, you split it into sections.

**Analogy:** A city (network) is divided into neighbourhoods (subnets). People in the same neighbourhood can talk directly. To reach another neighbourhood, you go through a post office (router).

**CIDR** (Classless Inter-Domain Routing) is the notation used to describe a subnet — written as `IP/prefix`.

---

## Why Subnets Exist

```
WITHOUT SUBNETTING (flat network):
┌─────────────────────────────────────────────────────┐
│  HR PCs ── Finance PCs ── Servers ── Guest Laptops  │
│  All on 192.168.1.0/24 — everyone talks to everyone │
│  One breach → attacker reaches everything            │
└─────────────────────────────────────────────────────┘

WITH SUBNETTING (segmented):
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  HR          │  │  Finance     │  │  Guest Wi-Fi │
│  10.0.1.0/24 │  │  10.0.2.0/24 │  │  10.0.3.0/24 │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       └─────────────────┴─────────────────┘
                         │
                    [Firewall/Router]
                    Rules control who
                    can talk to who
```

---

## CIDR Notation Explained

```
192.168.1.0/24
│           │
│           └── Prefix length: 24 bits are the network part
└── Network address

/24 means: first 24 bits = network, last 8 bits = hosts

In binary:
192    .168    .1      .0
11000000.10101000.00000001.00000000
└─────────────────────────┘└──────┘
        Network (24 bits)   Host (8 bits)
        Fixed               Can be 0–255
```

---

## CIDR Cheat Sheet

```
CIDR  Subnet Mask       Hosts    Example Range
/8    255.0.0.0         16M      10.0.0.0 – 10.255.255.255
/16   255.255.0.0       65534    172.16.0.0 – 172.16.255.255
/24   255.255.255.0     254      192.168.1.0 – 192.168.1.255
/25   255.255.255.128   126      192.168.1.0 – 192.168.1.127
/26   255.255.255.192   62       192.168.1.0 – 192.168.1.63
/27   255.255.255.224   30
/28   255.255.255.240   14
/29   255.255.255.248   6
/30   255.255.255.252   2        (point-to-point links)
/31   255.255.255.254   2        (no broadcast — RFC 3021)
/32   255.255.255.255   1        (single host)

Formula: hosts = 2^(32-prefix) - 2
         /24 → 2^8 - 2 = 254 usable hosts
         (minus 1 for network address, minus 1 for broadcast)
```

---

## Breaking Down a Subnet

For `192.168.1.0/24`:

```
Network address:   192.168.1.0    ← first address (identifies subnet)
First usable:      192.168.1.1    ← usually the gateway/router
Last usable:       192.168.1.254
Broadcast:         192.168.1.255  ← last address (sent to all hosts)

Total addresses:   256
Usable hosts:      254
```

---

## Splitting a Network (Subnetting)

You have `192.168.1.0/24` (254 hosts). You need 4 separate subnets.

Split `/24` into four `/26` subnets (each with 62 hosts):

```
Subnet 1: 192.168.1.0/26    → 192.168.1.0   – 192.168.1.63
Subnet 2: 192.168.1.64/26   → 192.168.1.64  – 192.168.1.127
Subnet 3: 192.168.1.128/26  → 192.168.1.128 – 192.168.1.191
Subnet 4: 192.168.1.192/26  → 192.168.1.192 – 192.168.1.255
```

---

## Hands-On: Subnet Tools

```bash
# ipcalc — instant subnet breakdown
ipcalc 192.168.1.0/24
ipcalc 10.0.0.0/8

# Sample output:
# Address:   192.168.1.0
# Netmask:   255.255.255.0 = 24
# Network:   192.168.1.0/24
# HostMin:   192.168.1.1
# HostMax:   192.168.1.254
# Broadcast: 192.168.1.255
# Hosts/Net: 254

# sipcalc — more detail
sipcalc 10.10.10.0/22

# Python quick calc
python3 -c "import ipaddress; n=ipaddress.ip_network('192.168.1.0/24'); print(list(n.hosts())[:5])"

# See your current subnet
ip addr show eth0
# inet 192.168.1.100/24 → you're on a /24 subnet
```

---

## Security Context — Subnets in VAPT

### 1. Internal Network Discovery via SSRF

```http
GET /fetch?url=http://10.0.1.1/ HTTP/1.1

Attacker iterates through subnets:
http://10.0.1.1/    → response? Internal server found
http://10.0.2.1/    → timeout? No host there
http://172.16.0.1/  → response? Another internal net
```

### 2. Post-Exploitation — Pivoting to New Subnets

```
You compromised: 10.0.1.50 (web server)
You discover:    it has two interfaces
                 eth0: 10.0.1.50  (DMZ)
                 eth1: 172.16.0.50 (internal network)

Now you can pivot to 172.16.0.0/24 through this host:
proxychains nmap -sn 172.16.0.0/24    ← discover internal hosts
```

### 3. Nmap Scanning Subnets

```bash
# Scan entire class C
nmap 192.168.1.0/24

# Scan multiple subnets
nmap 10.0.1.0/24 10.0.2.0/24

# Fast sweep (no port scan) to find live hosts
nmap -sn 10.0.0.0/8         ← entire class A (can be slow)
nmap -sn 192.168.1.0/24     ← quick local sweep
```

### 4. Subnet Misconfiguration

```
Bad practice: Putting DB servers in same subnet as web servers
192.168.1.10 → Web server (internet-facing)
192.168.1.20 → DB server  (should be isolated)

If web server is compromised → DB server directly reachable

Good practice: Separate subnets + firewall rules
10.0.1.0/24 → DMZ (web servers)
10.0.2.0/24 → DB servers
Firewall: only 10.0.1.0/24 can talk to 10.0.2.0/24 on port 3306
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Flat network — breach reaches everything | Segment into subnets by function (DMZ, DB, internal, guest) |
| No firewall between subnets | Add inter-VLAN firewall rules — deny by default |
| Overly large subnets | Use smaller subnets to limit blast radius |
| Internal subnets reachable via SSRF | Block RFC1918 in server-side URL fetchers |

---

## Related Notes
- [[02 - IP Addresses]] — IP addressing basics
- [[12 - Firewalls How They Work]] — controlling traffic between subnets
- [[13 - SSRF]] — abusing SSRF to reach internal subnets
- [[21 - Port Scanning with Nmap]] — scanning subnets
