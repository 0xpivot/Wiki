---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.01 What is a Network"
---

# 01.01 — What is a Network?

## What is it?

A **network** is two or more devices connected together so they can share information.

Think of it like a postal system:
- Your house = a computer
- The road = the cable or Wi-Fi signal
- The post office = a router
- The letter = data (files, web pages, messages)

When you open Google, your computer sends a "letter" through the network asking for Google's webpage. Google sends a "letter" back with the page. All of this happens in milliseconds.

---

## Types of Networks

```
┌─────────────────────────────────────────────────────────┐
│  LAN — Local Area Network                               │
│  Small area: your home, office, school                  │
│                                                         │
│  [PC] ──── [Switch] ──── [Router] ──── Internet        │
│  [Laptop] ─┘             └─── [Printer]                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  WAN — Wide Area Network                                │
│  Large area: cities, countries, the Internet itself     │
│                                                         │
│  [Office A LAN] ──── [ISP] ──── [Office B LAN]         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  WLAN — Wireless LAN (Wi-Fi)                            │
│  Same as LAN but without cables                         │
│                                                         │
│  [PC] )))  (((  [Wi-Fi Router] ──── Internet           │
│  [Phone] )))                                            │
└─────────────────────────────────────────────────────────┘
```

| Type | Full Name | Example |
|------|-----------|---------|
| LAN | Local Area Network | Your home Wi-Fi |
| WAN | Wide Area Network | The Internet |
| MAN | Metropolitan Area Network | City-wide fibre |
| WLAN | Wireless LAN | Coffee shop Wi-Fi |
| VPN | Virtual Private Network | Secure tunnel over Internet |

---

## How Data Travels — The Journey of a Web Request

When you type `google.com` in your browser:

```
Step 1: Your browser asks "What is google.com's address?"
        [Your PC] ──→ DNS Query ──→ [DNS Server]
        [DNS Server] ──→ "It's 142.250.182.46" ──→ [Your PC]

Step 2: Your PC connects to Google's server
        [Your PC] ──→ TCP Connection ──→ [Google Server 142.250.182.46]

Step 3: Your browser asks for the webpage
        [Your PC] ──→ "GET / HTTP/1.1" ──→ [Google Server]

Step 4: Google sends back the webpage
        [Google Server] ──→ HTML/CSS/JS ──→ [Your PC]

Step 5: Your browser renders the page
        [Your PC] displays Google homepage
```

---

## Network Devices — What Each One Does

```
Internet
   │
   ▼
[Modem]          ← Converts ISP signal to digital signal
   │
   ▼
[Router]         ← Directs traffic between networks (assigns IP addresses)
   │
   ├──────────────────────┐
   ▼                      ▼
[Switch]              [Wi-Fi AP]    ← Access Point (wireless)
   │
   ├── [PC 1]
   ├── [PC 2]
   └── [Printer]
```

| Device | Job |
|--------|-----|
| Modem | Connects your home to your ISP |
| Router | Directs traffic, assigns local IP addresses (192.168.x.x) |
| Switch | Connects multiple wired devices in a LAN |
| Access Point | Provides Wi-Fi |
| Firewall | Blocks unwanted traffic |
| Hub | Old, dumb switch — broadcasts to everyone (rarely used now) |

---

## IP Addresses — Every Device has an Address

Just like every house has a postal address, every device on a network has an **IP address**.

```
Public IP (given by your ISP — visible to the internet):
  203.0.113.42

Private IP (given by your router — only visible inside your home):
  192.168.1.100   ← your PC
  192.168.1.101   ← your phone
  192.168.1.1     ← your router
```

**Private IP ranges (you'll see these everywhere):**
```
10.0.0.0    – 10.255.255.255     (Class A — large networks)
172.16.0.0  – 172.31.255.255     (Class B — medium networks)
192.168.0.0 – 192.168.255.255    (Class C — home/small office)
```

---

## Ports — The Door Numbers

An IP address tells you which house to go to. A **port** tells you which door to knock on.

```
[Your PC] ──→ 142.250.182.46:443 ──→ [Google HTTPS Server]
              └── IP address  └── Port number

[Your PC] ──→ 142.250.182.46:80  ──→ [Google HTTP Server]
```

**Common ports to memorise:**
```
Port 21   → FTP       (File Transfer)
Port 22   → SSH       (Secure Shell — remote login)
Port 23   → Telnet    (Insecure remote login — avoid)
Port 25   → SMTP      (Email sending)
Port 53   → DNS       (Domain Name System)
Port 80   → HTTP      (Web — unencrypted)
Port 110  → POP3      (Email receiving)
Port 143  → IMAP      (Email receiving)
Port 443  → HTTPS     (Web — encrypted)
Port 445  → SMB       (Windows file sharing)
Port 3306 → MySQL     (Database)
Port 3389 → RDP       (Windows Remote Desktop)
Port 5432 → PostgreSQL (Database)
Port 8080 → HTTP Alt  (Web dev, proxy)
Port 8443 → HTTPS Alt (Web dev)
```

---

## Protocols — The Rules of Communication

A **protocol** is a set of rules for how devices talk to each other.

```
HTTP  → Rules for web browsing
HTTPS → HTTP + encryption (TLS)
TCP   → Rules for reliable data delivery (checks all packets arrived)
UDP   → Rules for fast data delivery (no checks — used for video, games)
DNS   → Rules for domain name lookups
ICMP  → Rules for network diagnostics (ping uses this)
ARP   → Rules for finding MAC addresses from IP addresses
```

---

## Security Context — Why This Matters for VAPT

Understanding networks is the foundation of everything in VAPT:

```
ATTACK SURFACE OF A NETWORK:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Attacker                                               │
│     │                                                   │
│     ▼                                                   │
│  [Open Port] ← Port scanning finds these               │
│  [Service]   ← Service version reveals CVEs            │
│  [Protocol]  ← Weak protocols (Telnet, FTP) = cleartext│
│  [Firewall]  ← Misconfigured = bypassed                │
│  [Network]   ← Sniffing, MITM, pivoting                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**What attackers look for:**
- Open ports with vulnerable services
- Unencrypted protocols (Telnet, FTP, HTTP)
- Devices on the same network (for pivoting)
- Misconfigured firewalls
- Default credentials on routers and switches

---

## Hands-On: See Your Own Network

```bash
# See your IP address (Linux/Mac)
ip addr
ifconfig

# See your IP address (Windows)
ipconfig

# See all devices on your network
arp -a

# Check if a host is reachable
ping 8.8.8.8          # Google's DNS server
ping google.com

# See the path packets take to a destination
traceroute google.com        # Linux/Mac
tracert google.com           # Windows

# Check what ports are open on your own machine
ss -tulnp             # Linux
netstat -ano          # Windows
```

**Sample output of `ip addr`:**
```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0
         └── Your IP  └── Subnet mask
```

---

## How to Fix / Secure a Network

| Risk | Fix |
|------|-----|
| Open unnecessary ports | Close unused ports with firewall rules |
| Cleartext protocols (Telnet, FTP) | Replace with SSH, SFTP |
| Default router credentials | Change default admin password |
| No network segmentation | Use VLANs to separate sensitive systems |
| No monitoring | Deploy IDS/IPS, log all traffic |
| Flat network (all devices trust each other) | Segment — guest Wi-Fi separate from corporate |

---

## Related Notes
- [[02 - IP Addresses]] — IPv4 and IPv6 deep dive
- [[06 - TCP Three-Way Handshake]] — how connections are established
- [[08 - DNS How Domain Names Resolve]] — how google.com becomes an IP
- [[21 - Port Scanning with Nmap]] — finding open ports in VAPT
- [[12 - Firewalls How They Work]] — the network's first line of defense
