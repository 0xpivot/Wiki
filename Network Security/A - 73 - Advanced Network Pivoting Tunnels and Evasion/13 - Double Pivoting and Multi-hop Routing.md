---
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
topic: "73.13 Double Pivoting and Multi-hop Routing"
---

# 73.13 Double Pivoting and Multi-hop Routing

## Introduction to Multi-hop Pivoting
During an advanced network penetration test or Red Team engagement, breaching the perimeter is only the first step. Modern enterprise networks are highly segmented, heavily utilizing VLANs, internal firewalls, and zero-trust principles. An attacker will often compromise an initial beachhead in a DMZ, only to find that the target data resides deep within an isolated management VLAN or a highly restricted database subnet.

Pivoting is the technique of using a compromised system to attack other systems on the same network to avoid restrictions such as firewall configurations. **Double pivoting** or **multi-hop routing** involves chaining these compromised systems together. Traffic originates from the attacker's infrastructure, routes through the initial beachhead (Hop 1), forwards through a secondary compromised internal host (Hop 2), and finally strikes the target in the restricted zone.

## The Theory of Multi-hop Tunnels
To establish a multi-hop route, an attacker must encapsulate network traffic multiple times. This usually involves creating SOCKS proxies or dynamic port forwarding rules on the compromised hosts and instructing the attacker's local operating system or exploitation framework to route traffic sequentially through these proxies.

### Challenges in Double Pivoting
1. **TCP over TCP Meltdown**: When wrapping a reliable protocol (TCP) inside another reliable protocol (TCP SOCKS tunnel), packet loss on the underlying network can cause cascading retransmissions. The outer TCP layer detects a dropped packet and retransmits it, while the inner TCP layer also detects the timeout and retransmits. This exponential backoff can cause the tunnel to collapse entirely, dropping performance to zero.
2. **Latency and Jitter**: Each hop introduces processing overhead and latency. Highly interactive tools or latency-sensitive exploits (like some SMB relay attacks) may fail over deep pivot chains.
3. **UDP Support**: SOCKS4 does not support UDP. SOCKS5 technically supports UDP via the `UDP ASSOCIATE` command, but many pivoting tools fail to implement it correctly. This restricts tools like Nmap (which relies heavily on UDP for DNS resolution and certain scans) unless specifically engineered solutions like Ligolo-ng or advanced VPNs are used.

## Essential Tools and Protocols

### 1. ProxyChains
`ProxyChains` is a UNIX tool that hooks into dynamically linked network functions (like `connect()`) and forces the connection through user-defined proxy servers.
- **Strict Chain**: Routes traffic exactly in the order specified in `proxychains.conf` (e.g., Attacker -> Proxy1 -> Proxy2 -> Target).
- **Dynamic Chain**: Skips dead proxies in the chain but maintains the route, adding resilience.
By setting up local SSH dynamic port forwards mapping to different compromised hosts, an attacker can define a multi-hop route in `proxychains.conf`.

### 2. SSH (Secure Shell) Dynamic Forwarding
SSH is ubiquitous in enterprise environments, making it the ultimate living-off-the-land (LotL) pivoting tool. 
- **Hop 1**: The attacker establishes a dynamic port forward (`ssh -D 1080 user@hop1.com`).
- **Hop 2**: The attacker leverages ProxyChains to route their *next* SSH connection through Hop 1 to reach Hop 2 (`proxychains ssh -D 1081 user@hop2.internal`).
This creates a nested tunnel. Traffic sent to local port 1081 goes into the local SSH client, is routed via SOCKS through Hop 1, and terminates at Hop 2, breaking into the deep internal network.

### 3. Chisel
Chisel is a fast TCP/UDP tunnel over HTTP secured via SSH. It is highly effective for pivoting because it operates over a single port and bypasses many HTTP proxies. Chisel can be run in reverse mode, allowing a compromised internal host (which cannot accept inbound connections) to dial out to the attacker, establishing a SOCKS5 proxy on the attacker's machine.

### 4. Ligolo-ng
Ligolo-ng is an advanced, modern pivoting tool designed specifically for Red Teaming. Unlike proxychains (which relies on user-space hooking), Ligolo-ng utilizes a TUN interface on the attacker's Linux machine. This routes traffic at the network layer (Layer 3), natively supporting ICMP, full UDP, and TCP without the limitations of SOCKS proxies. Multi-hop routing with Ligolo-ng involves establishing multiple agents and dynamically manipulating the routing table on the attacker's machine.

## Architecture: The Nested SSH Double Pivot

Below is an ASCII representation of a classic double pivot using SSH and ProxyChains, demonstrating how an attacker reaches an isolated Database Server.

```ascii
+-------------------+
|   Attacker Kali   |
|   (Local Host)    |
|                   |
| ssh -D 1080 hop1  |
| proxychains ssh \ |
|   -D 1081 hop2    |
| proxychains nmap \|
|   target_DB       |
+---------+---------+
          |
    (Internet / VPN)
          |
+---------V---------+       +-------------------+       +-------------------+
|     Hop 1 (DMZ)   |       |  Hop 2 (App Tier) |       |   Database Tier   |
|   Web Server      |======>|  Internal Server  |======>|  Isolated Target  |
|  (Public IP)      | SSH   | (No Internet Acc.)|  TCP  |  (No Internet Acc.|
| Port 1080 Proxy   | SOCKS | Port 1081 Proxy   | Conn. |  No access from   |
| termination       | Tunnel| termination       |       |  the DMZ)         |
+-------------------+       +-------------------+       +-------------------+
```

## Deep Dive: Setting up the Chain

### Step 1: Compromise and Tunnel to Hop 1
The attacker compromises `198.51.100.10` (Web Server).
They execute:
`ssh -N -D 127.0.0.1:1080 user@198.51.100.10`
*Result: Local port 1080 is now a SOCKS5 proxy terminating at Hop 1.*

### Step 2: Configure ProxyChains for the Second Hop
The attacker updates `/etc/proxychains4.conf`:
```text
strict_chain
proxy_dns
[ProxyList]
socks5  127.0.0.1 1080
```

### Step 3: Establish the Second Tunnel
The attacker discovers `10.0.1.50` (App Server) from Hop 1. They compromise it.
They use ProxyChains to SSH from their Kali box, *through* Hop 1, into Hop 2:
`proxychains4 ssh -N -D 127.0.0.1:1081 admin@10.0.1.50`
*Result: Traffic to local port 1081 is encapsulated in SSH, sent to port 1080, decapsulated at Hop 1, forwarded to Hop 2, and decapsulated there. Local port 1081 is now a SOCKS5 proxy terminating at Hop 2.*

### Step 4: Attack the Deep Internal Target
The attacker updates `/etc/proxychains4.conf` again:
```text
strict_chain
proxy_dns
[ProxyList]
socks5  127.0.0.1 1081
```
Now, commands like `proxychains4 nmap -sT -Pn 10.0.2.100` (The isolated DB) will route through both hops successfully.

## Command and Control (C2) Multi-hop Routing
Modern C2 frameworks like Cobalt Strike natively support multi-hop routing via SMB or TCP Beacons. 
- The initial HTTP/HTTPS beacon calls out to the attacker.
- The attacker deploys an SMB beacon on an internal host.
- The internal SMB beacon connects over port 445 back to the HTTP beacon.
- The HTTP beacon encapsulates the SMB beacon's traffic and sends it out to the Team Server.
This creates a peer-to-peer overlay network entirely within the target environment, making internal routing seamless and bypassing the need for manual SSH tunnels.

## Operational Constraints and OPSEC
- **Bandwidth Consumption**: Multi-hop tunnels consume bandwidth on intermediate nodes. Large file transfers or aggressive Nmap scans can cause noticeable CPU and network spikes, triggering monitoring alerts.
- **Timeout Management**: Long-running TCP connections across multiple nodes are prone to idle timeouts enforced by intermediate firewalls. SSH `ServerAliveInterval` and `ClientAliveInterval` must be aggressively tuned.
- **Log Artifacts**: Establishing SSH connections leaves massive artifacts (`/var/log/auth.log`, `wtmp`, `btmp`). Attackers utilizing SSH for LotL pivoting must heavily sanitize logs or utilize memory-resident proxy tools (like Chisel or C2 SOCKS) to avoid forensic detection.

## Conclusion
Mastering double pivoting and multi-hop routing allows an attacker to operate deep within a compromised network with the same capabilities as if they were physically plugged into the internal switch. It transforms an external threat into a pervasive internal presence.

## Chaining Opportunities
- **[[11 - Bypassing Deep Packet Inspection DPI]]**: Often, the connection to Hop 1 requires DPI evasion.
- **[[14 - VPN Exploitation and Compromise]]**: Compromising a VPN gateway serves as the ultimate Hop 1, providing native routing into the internal network.
- **[[15 - C2 Infrastructure Traffic Obfuscation]]**: C2 frameworks handle multi-hop natively, relying on obfuscation to hide the egress traffic of the primary beacon.

## Related Notes
- [[09 - Proxies and Forwarding in Post-Exploitation]]
- [[21 - Active Directory Lateral Movement]]
- [[33 - Network Segmentation Bypass]]
