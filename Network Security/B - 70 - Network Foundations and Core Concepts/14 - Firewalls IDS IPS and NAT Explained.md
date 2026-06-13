---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.14 Firewalls IDS IPS and NAT Explained"
---

# 70.14 Firewalls IDS IPS and NAT Explained

## 1. Firewalls Overview
- **Stateless:** Filters by IP/Port. No memory of connection.
- **Stateful:** Tracks TCP 3-way handshake and connection state.
- **NGFW:** Deep Packet Inspection, Application awareness (Layer 7).
- **WAF:** Web Application Firewall for HTTP payloads.

## 2. NAT (Network Address Translation)
Solves IPv4 exhaustion and hides internal topologies.
- **Static NAT:** 1-to-1 mapping.
- **Dynamic NAT:** Many-to-Pool mapping.
- **PAT (NAT Overload):** Many-to-1 mapping using source ports.

## 3. IDS vs IPS
- **IDS (Intrusion Detection System):** Passive, receives copied traffic via SPAN/Mirror port. Generates alerts.
- **IPS (Intrusion Prevention System):** Inline, actively drops malicious packets or resets connections.
- Detection types: Signature-based vs. Anomaly-based.

## 4. ASCII Diagram: Network Topology
```text
       [ Internet ]
            |
            v
     [ External Router ]
            |
      (NAT Translation)
            |
            v
       [ NGFW / IPS ] (Inline Blocking)
            |
    +-------+-------+
    |               |
    v               v
 [ DMZ ]       [ Internal LAN ]
(Web/Mail)     (Workstations)
```

## 5. VAPT Context: Evasion Techniques
- **Fragmentation:** Splitting packets to evade IDS signature matching.
- **Decoys:** Obscuring scan origin with spoofed IP addresses.
- **Encryption:** Tunneling malware C2 through HTTPS or SSH to bypass DPI.
- **Timing:** Slow-rate scanning to avoid threshold-based anomaly detection.

## Chaining Opportunities
- **Lateral Movement:** Pivot through compromised segments using [[11 - SSH Protocol Basics and Key Authentication]].
- **Payload Delivery:** Combine with [[12 - SMTP POP3 and IMAP Email Protocols]] for access.
- **Recon:** Findings feed into [[13 - SNMP Protocol Basics and Community Strings]].
- **Evasion:** Bypasses [[14 - Firewalls IDS IPS and NAT Explained]].
- **VPNs:** Compare with [[15 - VPNs IPsec and Tunneling Basics]].

## Related Notes
- [[11 - SSH Protocol Basics and Key Authentication]]
- [[12 - SMTP POP3 and IMAP Email Protocols]]
- [[13 - SNMP Protocol Basics and Community Strings]]
- [[14 - Firewalls IDS IPS and NAT Explained]]
- [[15 - VPNs IPsec and Tunneling Basics]]

## 6. Comprehensive Rulesets (IPTables and Snort)

### 6.1 Advanced IPTables Stateful Ruleset
Below is an example of a hardened, stateful IPTables configuration for a Linux-based edge firewall.
```bash
#!/bin/bash
# Flush all existing rules
iptables -F
iptables -X
iptables -t nat -F

# Set default drop policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback interface
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Stateful inspection: Allow return traffic for established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# Drop invalid packets
iptables -A INPUT -m state --state INVALID -j DROP
iptables -A FORWARD -m state --state INVALID -j DROP

# Anti-Spoofing: Drop traffic claiming to be from localhost on external interface
iptables -A INPUT -i eth0 -s 127.0.0.0/8 -j DROP

# Allow inbound SSH on specific port from specific IP
iptables -A INPUT -p tcp --dport 2222 -s 203.0.113.50 -m state --state NEW -j ACCEPT

# Allow inbound HTTP/HTTPS to DMZ (Forwarding)
iptables -A FORWARD -i eth0 -o eth1 -p tcp --dport 80 -m state --state NEW -j ACCEPT
iptables -A FORWARD -i eth0 -o eth1 -p tcp --dport 443 -m state --state NEW -j ACCEPT

# Prevent SYN Floods (Rate Limiting)
iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# ICMP Rate Limiting (Prevent Ping Floods)
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# NAT Overload (PAT) configuration for internal subnet accessing the internet
iptables -t nat -A POSTROUTING -o eth0 -s 192.168.1.0/24 -j MASQUERADE
```

### 6.2 Snort IDS Signature Examples
```text
# Alert on any external attempts to access the SSH port
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 (msg:"Suspicious SSH Access Attempt"; flags:S; classtype:attempted-recon; sid:1000001; rev:1;)

# Detect Nmap XMAS Scan
alert tcp $EXTERNAL_NET any -> $HOME_NET any (msg:"Nmap XMAS Scan Detected"; flags:FPU; classtype:attempted-recon; sid:1000002; rev:1;)

# Detect potential SQL Injection in URI
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS 80 (msg:"SQL Injection Attempt - UNION SELECT"; flow:to_server,established; content:"UNION"; nocase; http_uri; content:"SELECT"; nocase; http_uri; classtype:web-application-attack; sid:1000003; rev:1;)

# Detect large ICMP Packets (Ping of Death / Tunneling)
alert icmp $EXTERNAL_NET any -> $HOME_NET any (msg:"Oversized ICMP Packet - Possible Tunneling"; dsize:>800; itype:8; classtype:misc-activity; sid:1000004; rev:1;)
```
