---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.03 MAC Addresses"
---

# 01.03 — MAC Addresses

## What is it?

A **MAC address** (Media Access Control address) is a unique hardware identifier burned into every network interface card (NIC) — your Wi-Fi card, ethernet port, etc.

**Analogy:**
- IP address = your current address (can change when you move)
- MAC address = your fingerprint (permanent, tied to the hardware)

MAC addresses work at **Layer 2** (Data Link layer) of the OSI model — they handle communication within the same local network. IP addresses handle communication across networks.

---

## MAC Address Format

```
MAC address: AA:BB:CC:DD:EE:FF

Written as 6 groups of 2 hex digits:
AA:BB:CC : DD:EE:FF
└───────┘   └──────┘
OUI         Device ID
(Vendor)    (Unique per device)

Total: 48 bits = 281 trillion possible addresses
```

**Real examples:**
```
00:50:56:XX:XX:XX    → VMware virtual machine
08:00:27:XX:XX:XX    → VirtualBox virtual machine
00:0C:29:XX:XX:XX    → VMware (another range)
AC:BC:32:XX:XX:XX    → Apple device
FC:FB:FB:XX:XX:XX    → Dell device
```

The first 3 bytes = **OUI (Organizationally Unique Identifier)** — tells you the manufacturer.

---

## How MAC Addresses Work

MAC addresses are used for communication **within the same LAN**. When data crosses a router to another network, MAC addresses change at each hop.

```
SAME NETWORK (Layer 2 — MAC addresses used):

[PC: IP 192.168.1.100, MAC AA:AA:AA:AA:AA:AA]
          │
          │ Ethernet frame:
          │ Src MAC: AA:AA:AA:AA:AA:AA
          │ Dst MAC: BB:BB:BB:BB:BB:BB
          ▼
[Printer: IP 192.168.1.200, MAC BB:BB:BB:BB:BB:BB]


ACROSS NETWORKS (Layer 3 — IP addresses used, MAC changes at each hop):

[Your PC]  ──→  [Router]  ──→  [ISP Router]  ──→  [Google]
MAC: AA:AA      MAC: CC:CC      MAC: DD:DD          MAC: FF:FF
IP: 192.168.1.100              IP: 203.0.113.42     IP: 142.250.x.x
                ↑ MAC changes here. IP stays the same end-to-end.
```

---

## ARP — How MAC Addresses are Found

When your PC wants to talk to `192.168.1.200` on the same network, it doesn't know the MAC address. It uses **ARP (Address Resolution Protocol)**:

```
Step 1: Broadcast to everyone on the network
        [PC] → "Who has 192.168.1.200? Tell 192.168.1.100"
        (Sent to FF:FF:FF:FF:FF:FF — the broadcast MAC)

Step 2: The target responds
        [Printer] → "192.168.1.200 is at BB:BB:BB:BB:BB:BB"

Step 3: PC stores this in its ARP cache
        [PC] → ARP table updated:
               192.168.1.200 → BB:BB:BB:BB:BB:BB

Step 4: PC sends data directly using MAC address
```

**View your ARP cache:**
```bash
arp -a              # Linux and Windows
ip neigh show       # Linux modern command
```

**Sample output:**
```
192.168.1.1    ether   c8:3a:35:xx:xx:xx   C   eth0   ← router
192.168.1.101  ether   ac:bc:32:xx:xx:xx   C   eth0   ← phone
```

---

## Security Context — MAC Addresses in VAPT

### 1. ARP Spoofing / ARP Poisoning (MITM Attack)

An attacker sends fake ARP replies to poison the ARP cache of victims.

```
NORMAL:
[PC] asks "Who is 192.168.1.1 (router)?"
[Router] replies "I am at CC:CC:CC:CC:CC:CC"

AFTER ARP SPOOFING:
[Attacker] sends fake ARP: "192.168.1.1 is at AA:AA:AA:AA:AA:AA (attacker's MAC)"
[Attacker] sends fake ARP to router: "192.168.1.100 is at AA:AA:AA:AA:AA:AA"

Result:
[PC] ──→ [Attacker] ──→ [Router]   ← Attacker sees ALL traffic!
         (Man in the Middle)
```

**Tool: arpspoof**
```bash
# Enable IP forwarding (so traffic actually passes through)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Poison victim's ARP cache
arpspoof -i eth0 -t 192.168.1.100 192.168.1.1

# Poison router's ARP cache
arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# Now capture traffic with Wireshark or tcpdump
```

**Tool: bettercap (modern)**
```bash
bettercap -iface eth0
# Inside bettercap:
net.probe on
arp.spoof.targets 192.168.1.100
arp.spoof on
net.sniff on
```

### 2. MAC Address Spoofing

Change your MAC address to impersonate another device or bypass MAC filtering.

```bash
# Linux — change MAC address
ip link set eth0 down
ip link set eth0 address AA:BB:CC:DD:EE:FF
ip link set eth0 up

# Or with macchanger
macchanger -r eth0              # random MAC
macchanger -m AA:BB:CC:11:22:33 eth0   # specific MAC

# Windows
# Device Manager → Network Adapter → Properties → Network Address
```

**Use cases:**
- Bypass Wi-Fi MAC filtering (the filter is easily defeated)
- Impersonate a trusted device on the network
- Avoid tracking across Wi-Fi networks (phone randomization)

### 3. Discovering Devices on LAN

```bash
# ARP scan — fast way to find all devices on LAN
arp-scan -l                      # scan local network
arp-scan 192.168.1.0/24

# Nmap ARP scan (requires root)
nmap -sn 192.168.1.0/24          # sends ARP requests on local network

# Sample output:
# Nmap scan report for 192.168.1.1
# Host is up (0.0010s latency).
# MAC Address: C8:3A:35:XX:XX:XX (Tenda)
#                                ↑ Vendor identified from OUI
```

### 4. OUI Lookup — Identifying Device Vendors

From a MAC address you can identify the vendor, which tells you what kind of device it is.

```
00:50:56 → VMware (target is a VM — may be easier to exploit)
00:0C:29 → VMware
AC:BC:32 → Apple (likely a Mac or iPhone)
00:1A:A0 → Dell (server or workstation)
B0:BE:76 → Samsung
```

**Lookup:** Use `macvendors.com` or the `arp-scan --localnet` output.

---

## MAC Filtering — A Weak Defense

Some Wi-Fi networks use MAC filtering to only allow known devices.

```
Router config: Only allow these MACs:
  AA:BB:CC:DD:EE:FF  (boss's laptop)
  11:22:33:44:55:66  (reception PC)

Bypass:
1. Sniff the network with Wireshark
2. See a whitelisted MAC in the traffic
3. Change your MAC to match it
4. Connect freely

This is why MAC filtering is not real security.
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| ARP Spoofing | Enable Dynamic ARP Inspection (DAI) on managed switches |
| ARP Spoofing | Use static ARP entries for critical devices |
| ARP Spoofing | Encrypt traffic (TLS/HTTPS — even if intercepted, data is encrypted) |
| MAC Filtering as sole auth | Use 802.1X (certificate-based network authentication) instead |
| MITM via ARP | Use VPN for sensitive communications on LAN |

---

## Hands-On: MAC Commands

```bash
# View your MAC address
ip link show eth0
ifconfig eth0

# View ARP table
arp -a
ip neigh

# Flush ARP cache
ip neigh flush all      # Linux
arp -d 192.168.1.1      # delete specific entry

# Sniff ARP traffic
tcpdump -i eth0 arp
```

---

## Related Notes
- [[01 - What is a Network]] — networking basics
- [[02 - IP Addresses]] — IP addressing
- [[10 - ARP Address Resolution Protocol]] — ARP deep dive
- [[Module 35 - Network Protocol Attacks]] — ARP spoofing attacks
