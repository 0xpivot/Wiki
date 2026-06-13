---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.01 Ping Sweeps and Host Discovery"
---

# Ping Sweeps and Host Discovery

## Introduction

Host discovery is the critical first phase in any network penetration test or vulnerability assessment. Before an attacker or penetration tester can identify vulnerable services, they must first identify which IP addresses are actually active and responding on the network. This process, commonly known as ping sweeping or host discovery, involves sending various types of probes to a target IP range and analyzing the responses to determine if a host is "up" (active).

Host discovery must be approached methodically, as different network environments (e.g., local LANs vs. routed WANs) and security controls (e.g., firewalls, Intrusion Detection Systems) dictate the effectiveness of different probing techniques. The goal is to accurately map the attack surface while minimizing noise if stealth is required, or maximizing thoroughness if comprehensive assessment is the objective.

## The Theory of Host Discovery

At its core, host discovery relies on the expected behavior of networking protocols as defined by RFCs. When a device receives a specific packet, the protocol dictates how it should respond. By sending packets that elicit a response from active hosts but are ignored or explicitly rejected by inactive or filtered addresses, we can infer the state of the target.

### The OSI Model Context
Host discovery primarily operates at Layer 2 (Data Link), Layer 3 (Network), and Layer 4 (Transport) of the OSI model:
- **Layer 2 (ARP/NDP):** Extremely effective on local network segments where routing is not involved.
- **Layer 3 (ICMP):** The traditional protocol used for ping, relying on Echo Requests and other ICMP message types.
- **Layer 4 (TCP/UDP):** Involves sending TCP SYN, ACK, or UDP packets to specific ports to determine if a host responds, bypassing Layer 3 ICMP restrictions.

## Layer 2 Discovery: Address Resolution Protocol (ARP)

When performing host discovery on an Ethernet Local Area Network (LAN), Layer 2 discovery is the most reliable and fastest method. This is because hosts on the same physical or logical subnet must resolve IP addresses to MAC addresses using ARP (IPv4) or Neighbor Discovery Protocol (NDP for IPv6) to communicate.

### How ARP Discovery Works
1. The scanning machine broadcasts an ARP Request: "Who has IP address X.X.X.X? Tell Y.Y.Y.Y."
2. All devices on the local segment receive this broadcast.
3. If a device has the IP address X.X.X.X, it responds with an ARP Reply containing its MAC address.
4. The scanner receives the ARP Reply, confirming the host is up.

### Advantages of Layer 2 Discovery
- **Extremely Accurate:** Firewalls and local host-based firewalls (like Windows Defender Firewall) generally do not block ARP requests, as doing so would break local network communication.
- **Fast:** Layer 2 broadcasts are handled rapidly by switches.
- **No Routing Overhead:** Packets do not traverse routers, reducing latency.

### Tools for ARP Discovery
- **arp-scan:** A fast, command-line tool specifically designed for ARP sweeping.
  ```bash
  arp-scan --localnet
  arp-scan -I eth0 192.168.1.0/24
  ```
- **Nmap ARP Discovery:** Nmap defaults to ARP discovery when scanning local subnets (unless run without root privileges).
  ```bash
  nmap -sn -PR 192.168.1.0/24
  ```

## Layer 3 Discovery: Internet Control Message Protocol (ICMP)

When scanning across routed boundaries (WANs or distinct subnets), Layer 2 discovery is impossible because ARP broadcasts are not forwarded by routers. In these scenarios, Layer 3 protocols like ICMP are utilized.

### ICMP Echo Request/Reply (Standard Ping)
The most common host discovery method is the ICMP Echo Request (Type 8). If the host is alive and not filtering ICMP, it replies with an ICMP Echo Reply (Type 0).

```bash
ping -c 4 10.10.10.5
nmap -sn -PE 10.10.10.0/24
```

### Advanced ICMP Discovery Techniques
Modern firewalls frequently block ICMP Echo Requests. To bypass these restrictions, other ICMP types can be used:

1. **ICMP Timestamp Request (Type 13):** Historically used for time synchronization. Some hosts that block Echo Requests might still respond to Timestamp Requests with a Timestamp Reply (Type 14).
   ```bash
   nmap -sn -PP 10.10.10.0/24
   ```

2. **ICMP Address Mask Request (Type 17):** Used to request the subnet mask of the target network. Responded to with an Address Mask Reply (Type 18). While largely deprecated, some legacy or misconfigured systems still respond.
   ```bash
   nmap -sn -PM 10.10.10.0/24
   ```

## Layer 4 Discovery: TCP and UDP Probes

When ICMP is entirely blocked by perimeter firewalls, attackers fall back to Layer 4 protocols. By probing common ports, one can determine host liveness based on transport layer responses.

### TCP SYN Ping (-PS)
The scanner sends an empty TCP packet with the SYN flag set to a specific port (e.g., 80, 443, 22).
- If the port is **open**, the target responds with a SYN/ACK. The scanner then sends an RST to tear down the connection.
- If the port is **closed**, the target responds with an RST.
- In both cases, receiving a response confirms the host is up.

```bash
nmap -sn -PS22,80,443 10.10.10.0/24
```

### TCP ACK Ping (-PA)
The scanner sends a TCP packet with the ACK flag set. Because there is no existing connection state, the target RFC dictates it must respond with an RST packet. This technique is particularly effective at bypassing stateless firewalls that only block incoming SYN packets.

```bash
nmap -sn -PA80,443 10.10.10.0/24
```

### UDP Ping (-PU)
The scanner sends an empty UDP packet to a target port. This method is slower and less reliable due to the connectionless nature of UDP.
- If the port is **closed**, the target typically sends back an ICMP Port Unreachable message, confirming the host is up.
- If the port is **open** or **filtered**, usually no response is returned. Therefore, UDP pings are best targeted at obscure, likely closed ports.

```bash
nmap -sn -PU40125 10.10.10.0/24
```

## IP Protocol Ping (-PO)

This advanced technique sends IP packets with specified protocol numbers (e.g., IGMP, IP-in-IP). If the protocol is supported, the host may respond. If unsupported, the host typically replies with an ICMP Protocol Unreachable message, thereby confirming the host is up.

```bash
nmap -sn -PO1,2,4 10.10.10.0/24
```

## SCTP INIT Ping (-PY)

Stream Control Transmission Protocol (SCTP) is a reliable transport layer protocol. Sending an SCTP INIT chunk acts similarly to a TCP SYN. If the host is up and supports SCTP on the targeted port, it responds with an INIT-ACK (open) or an ABORT (closed).

```bash
nmap -sn -PY80,443 10.10.10.0/24
```

## Scripting a Custom Ping Sweep

Sometimes, Nmap might not be available on a compromised pivot host. Knowing how to script a basic ping sweep using native tools is a critical skill.

### Bash One-Liner (Linux)
```bash
for ip in $(seq 1 254); do ping -c 1 -W 1 192.168.1.$ip | grep "bytes from" | cut -d " " -f 4 | tr -d ":" & done; wait
```
This script loops through 1-254, sends exactly 1 ping (`-c 1`) with a 1-second timeout (`-W 1`), and runs them in parallel (`&`) to drastically reduce the time needed. The output is filtered to show only responding IP addresses.

### PowerShell One-Liner (Windows)
```powershell
1..254 | ForEach-Object { Test-Connection -ComputerName 192.168.1.$_ -Count 1 -ErrorAction SilentlyContinue | Select-Object IPV4Address }
```

## Wireshark Perspective

When running a comprehensive Nmap host discovery, viewing the traffic in Wireshark is highly educational. 

1. **Filter for ICMP:** `icmp` - You will see the standard Type 8 requests.
2. **Filter for TCP SYN Ping:** `tcp.flags.syn==1 and tcp.flags.ack==0`
3. **Filter for ARP:** `arp` - Observe the massive broadcast storm if running a local scan.

Understanding the packet-level interactions allows testers to troubleshoot why a scan is failing or generating false positives.

## Visualizing the Host Discovery Process

```ascii
+-----------------------+                            +-----------------------+
|   Attacker / Scanner  |                            |    Target Network     |
|     192.168.1.100     |                            |     10.10.10.0/24     |
+-----------------------+                            +-----------------------+
          |                                                      |
          |       1. Is target on local LAN?                     |
          |-------------------------------------[Yes]----------->| Layer 2 ARP Request
          |                                                      | "Who has 192.168.1.X?"
          |<-----------------------------------------------------| Layer 2 ARP Reply
          |                                                      |
          |                                                      |
          |       2. Is target routed? (WAN)                     |
          |-------------------------------------[No ARP]-------->| Router forwards traffic
          |                                                      |
          |       --- Layer 3 ICMP Probes ---                    |
          |--------> ICMP Echo Request (Type 8) ---------------->| (Often Blocked)
          |<-------- ICMP Echo Reply (Type 0)   -----------------| (If allowed)
          |                                                      |
          |--------> ICMP Timestamp Req (Type 13) -------------->|
          |<-------- ICMP Timestamp Reply (Type 14) -------------|
          |                                                      |
          |       --- Layer 4 TCP/UDP Probes ---                 |
          |--------> TCP SYN to Port 80 ------------------------>|
          |<-------- TCP SYN/ACK (Port Open) --------------------| Host is UP
          |                                                      |
          |--------> TCP ACK to Port 443 ----------------------->|
          |<-------- TCP RST (Out of state) ---------------------| Host is UP
          |                                                      |
          |--------> UDP Packet to Port 53 --------------------->|
          |<-------- ICMP Port Unreachable (Type 3 Code 3) ------| Host is UP
          |                                                      |
+-----------------------+                            +-----------------------+
```

## Combining Techniques for Comprehensive Sweeps

In a real-world VAPT engagement, relying on a single discovery method will likely result in false negatives. Hosts may block ICMP but allow TCP to port 443, or they might block TCP 443 but allow ICMP Timestamp requests.

Nmap allows combining these techniques into a single, comprehensive host discovery scan:

```bash
nmap -sn -PE -PP -PS21,22,23,25,80,113,31339 -PA80,113,443,10042 --source-port 53 10.10.10.0/24
```

### Breakdown of the Command:
- `-sn`: Disable port scanning (perform host discovery only).
- `-PE`: ICMP Echo Request.
- `-PP`: ICMP Timestamp Request.
- `-PS21,22...`: TCP SYN ping to specified common ports.
- `-PA80,113...`: TCP ACK ping to specified ports.
- `--source-port 53`: Spoofs the source port to 53 (DNS) to bypass poorly configured firewalls that trust traffic originating from port 53.

## Evading Intrusion Detection Systems (IDS)

Loud ping sweeps generate significant network noise, often triggering IDS/IPS alerts (e.g., Snort rules detecting ICMP sweeps or rapid TCP SYN connections across multiple IPs).

### Strategies for Evasion:
1. **Timing Adjustments:** Use Nmap's timing templates (`-T2` or `-T1`) to slow down the scan, sending packets infrequently enough to stay under IDS rate-limiting thresholds.
2. **Decoys:** Use the `-D` flag to spoof other IP addresses. The target sees scans coming from your IP and several decoys, obfuscating the true source.
   ```bash
   nmap -sn -D 192.168.1.5,192.168.1.6,ME 10.10.10.0/24
   ```
3. **Fragmentation:** While more applicable to port scanning, fragmenting packets can sometimes evade basic packet inspection.
4. **Targeting Specific Services:** Instead of scanning all IPs, focus on identifying specific services (e.g., DNS servers) that might leak internal IP ranges or trust specific sources.

## Defensive Strategies against Host Discovery

As a network defender, completely preventing host discovery is difficult without negatively impacting legitimate traffic. However, several steps can be taken:
- **Filter ICMP:** Configure perimeter firewalls to drop inbound ICMP Echo Requests. Note that RFCs recommend allowing certain ICMP types (like Fragmentation Needed) to avoid breaking MTU path discovery.
- **Strict Ingress Filtering:** Ensure firewalls only allow traffic to specific exposed services (e.g., TCP 443) and drop all other unsolicited traffic implicitly.
- **Implement IDS/IPS:** Deploy systems like Suricata or Snort to detect and temporarily ban IPs performing broad horizontal sweeps across multiple ports or IPs in a short timeframe.

## Dealing with False Positives and Negatives

- **False Negatives:** A host is active but does not respond to any of your probes due to strict firewall rules. Mitigation: Broaden your Layer 4 probes to include more ports, or use alternative discovery methods like DNS zone transfers or active directory enumeration if applicable.
- **False Positives:** A firewall or IDS intercepts the probes and responds on behalf of all IP addresses in the range (e.g., responding with SYN/ACK for all SYN requests). Mitigation: Analyze the TTL and IP ID fields of the responses. If all responses have identical characteristics regardless of the target IP, it's likely an intervening security device.

## Advanced Customization with Hping3

While Nmap is the industry standard, `hping3` allows for ultimate flexibility in crafting custom ICMP/TCP/UDP packets for host discovery. This is useful when Nmap's predefined structures are fingerprinted by an IDS.

```bash
# Custom TCP SYN ping to port 80
hping3 -S -p 80 -c 1 10.10.10.5

# Custom ICMP Echo Request with specific data payload to evade simple length-based filtering
hping3 -1 -d 100 -E payload.txt 10.10.10.5
```

## Chaining Opportunities
- **Port Scanning:** Once active hosts are discovered, the list of IPs is fed into comprehensive port scanners to identify listening services. See [[02 - Nmap Port Scanning Techniques TCP UDP]].
- **Vulnerability Scanning:** Host discovery feeds directly into vulnerability assessment tools (e.g., Nessus, OpenVAS) which require a target list.
- **Active Directory Enumeration:** Discovered hosts might include Domain Controllers or DNS servers, which can be further queried for more internal network information.

## Related Notes
- [[02 - Nmap Port Scanning Techniques TCP UDP]]
- [[05 - Masscan and RustScan for Fast Discovery]]
- [[03 - Nmap Service and OS Detection]]
