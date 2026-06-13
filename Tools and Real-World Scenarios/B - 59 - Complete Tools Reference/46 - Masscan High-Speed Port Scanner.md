---
tags: [tools, network, exploit, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.46 Masscan High-Speed Port Scanner"
---

# Masscan High-Speed Port Scanner

## 1. Introduction to Masscan

Masscan is an internet-scale port scanner capable of scanning the entire IPv4 address space in under six minutes, provided the executing system and network infrastructure can handle the immense packet rates (approximately 10 million packets per second). Created by Robert Graham, Masscan achieves this blistering speed by relying on a custom asynchronous TCP/IP stack and utilizing zero-copy techniques via PF_RING or similar kernel bypass technologies where available.

Unlike Nmap, which maintains complex state tracking for each connection and performs extensive probing for service identification and OS fingerprinting, Masscan operates almost entirely amnesiac. It fires SYN packets at the target and independently listens for SYN-ACK responses, immediately sending RST packets to tear down the connection to prevent the underlying operating system's TCP stack from becoming exhausted or interfering.

Understanding Masscan is critical for Red Teams, Penetration Testers, and Bug Bounty Hunters who need to identify attack surfaces across massive Class A subnets or entire corporate infrastructures without waiting days for conventional scanners to finish. It is the premier tool for external footprinting at scale.

## 2. Core Architecture and Asynchronous Transmission

Masscan's architecture fundamentally diverges from traditional socket-based scanners. To achieve wire-speed transmission, it discards the POSIX socket paradigm entirely.

### Custom TCP/IP Stack
Traditional scanners use the OS's socket API (`connect()`, `send()`, `recv()`). This introduces significant overhead due to context switches between user-space and kernel-space, state tracking (TCP state machine), and file descriptor limits. Every connection requires memory allocation in the kernel.
Masscan bypasses the OS socket API. It constructs raw Ethernet/IP/TCP frames in user-space and injects them directly into the network interface using libpcap or kernel-bypass methods.

### Independent Transmit and Receive Threads
Masscan separates transmission and reception into distinct, independent threads:
- **Transmit Thread:** Rapidly generates and spews SYN packets based on a randomized target list (to avoid overwhelming any single target router). It does not wait for a response before sending the next packet.
- **Receive Thread:** Actively sniffs the network interface for SYN-ACK or RST responses using a BPF (Berkeley Packet Filter). When a SYN-ACK is received, Masscan logs the open port and immediately fires a RST packet to prevent the host OS from attempting to complete the three-way handshake (since the OS didn't initiate the connection, it would normally send a RST anyway, but Masscan beats it to the punch to maintain control and reduce latency).

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                          Masscan Architecture                           |
+-------------------------------------------------------------------------+
|                                                                         |
|  +--------------------+                     +------------------------+  |
|  | Target/Port Output |                     |   Target Randomizer    |  |
|  |     Formatter      |                     | (BlackRock Algorithm)  |  |
|  +--------^-----------+                     +----------+-------------+  |
|           |                                            |                |
|           | Logs Open Ports                            | IP/Port Pairs  |
|           |                                            |                |
|  +--------+-----------+                     +----------v-------------+  |
|  |                    |                     |                        |  |
|  |   Receive Thread   | <--- Independent -> |    Transmit Thread     |  |
|  |   (PCAP/PF_RING)   |                     |     (Raw Sockets)      |  |
|  |                    |                     |                        |  |
|  +--------^-----------+                     +----------+-------------+  |
|           |                                            |                |
|       SYN-ACK / RST                                   SYN               |
|           |                                            |                |
+-----------|--------------------------------------------|----------------+
            |                                            |                 
      +-----|--------------------------------------------|----+            
      |     |               Host OS Kernel               |    |            
      |  +--+-------+                              +-----v-+  |            
      |  | BPF/PCAP |                              | NDISC |  |            
      |  +--^-------+                              +-----+-+  |            
      +-----|--------------------------------------------|----+            
            |                                            |                 
      +-----|--------------------------------------------v----+            
      |                      Network Card                     |            
      +-------------------------------------------------------+            
```

## 3. The BlackRock Randomization Algorithm

A critical component of Masscan's architecture is how it selects the next IP/Port combination to scan. If you scan a /8 subnet, scanning sequentially (10.0.0.1, 10.0.0.2...) would instantly trigger broadcast storms and overwhelm the target network's edge routers, leading to dropped packets and inaccurate results.

Masscan utilizes a custom cryptographic algorithm called **BlackRock** (a modified version of DES tailored for arbitrary domain sizes). 
Instead of maintaining a list of IPs in memory—which would consume gigabytes of RAM for a large scan—Masscan generates a random sequence mathematically. The index counter increments, passes through the BlackRock cipher, and produces a mathematically guaranteed unique IP/Port combination within the target range. This ensures complete coverage while looking like random background noise to routers, preventing localized congestion.

## 4. High-Speed Scanning Considerations and Network Exhaustion

Achieving maximum speed with Masscan requires tuning both the tool and the host environment. However, extreme caution must be exercised to avoid self-inflicted Denial of Service.

### Rate Limiting (`--rate`)
The `--rate` parameter defines the packets per second (pps) Masscan will attempt to transmit.
- `--rate 10000`: Safe for most home/office broadband connections.
- `--rate 100000`: Suitable for Gigabit Ethernet connections on corporate networks.
- `--rate 10000000`: Requires 10-Gigabit Ethernet and kernel bypass (PF_RING).

**Warning on Router State Table Exhaustion:**
Even though Masscan does not maintain state, the routers, NAT gateways, and stateful firewalls between you and the target *do*. If you push 100,000 pps through a standard SOHO router or a low-tier cloud VPN, you will exhaust its NAT translation table in seconds. The router will stop forwarding packets entirely, dropping your internet connection and invalidating the scan. Always scan from a public IP without NAT, or explicitly configure your firewall to bypass state tracking for the scan traffic.

### Kernel Bypass (PF_RING / DPDK)
For rates exceeding 1-2 million pps, standard Linux networking stacks become the primary bottleneck. Masscan heavily integrates with PF_RING, a high-speed packet capture library that bypasses the kernel's networking stack, allowing user-space applications to read/write directly to the network interface card (NIC). This eliminates the costly kernel-to-user-space context switches.

## 5. Advanced Usage and Command Syntax

### Basic Wide-Area Scan
Scanning an entire Class B subnet for standard web ports:
```bash
sudo masscan 10.10.0.0/16 -p80,443,8080,8443 --rate 10000
```
*Note: `sudo` is unconditionally required because Masscan injects raw frames.*

### Reading Targets from a File
For bug bounties or large enterprise engagements, targets are often compiled in comprehensive lists:
```bash
sudo masscan -iL targets.txt -p1-65535 --rate 50000 -oL masscan_out.txt
```

### Excluding IP Ranges
Always exclude critical infrastructure, Department of Defense ranges, or non-target subnets using an exclude file. Masscan respects the standard format used by Nmap:
```bash
sudo masscan 10.0.0.0/8 -p80 --excludefile exclude.txt
```

### Banner Grabbing: Breaking the Amnesia
Masscan *can* perform basic banner grabbing, though this fundamentally breaks its purely asynchronous, stateless nature. To grab a banner, Masscan must establish a full TCP connection, send a payload (or wait for the server to speak), and read the response.
```bash
sudo masscan 10.10.0.0/16 -p21,22,80 --banners --source-ip 192.168.1.100
```
**CRITICAL:** When using `--banners`, you MUST assign a dedicated IP address (`--source-ip`) to Masscan that the host OS does not use. Otherwise, the host OS will receive the SYN-ACK, realize it never initiated the connection, and send a RST packet to the target, destroying the connection before Masscan's user-space thread can grab the banner.

### Sharding for Distributed Scanning
For truly massive scans (e.g., the entire internet), you can easily distribute the workload across multiple VPS instances using the `--shard` parameter without needing a centralized controller. The BlackRock algorithm guarantees that shards are perfectly mutually exclusive.
- Machine 1: `masscan 0.0.0.0/0 -p80 --shard 1/3`
- Machine 2: `masscan 0.0.0.0/0 -p80 --shard 2/3`
- Machine 3: `masscan 0.0.0.0/0 -p80 --shard 3/3`

## 6. Output Formats and Pipeline Integration

Masscan supports multiple output formats, which is crucial for piping results into secondary analysis tools.

- **List format (`-oL`)**: Simple, greppable text format.
- **JSON format (`-oJ`)**: Ideal for programmatic parsing.
- **XML format (`-oX`)**: Compatible with Nmap's XML format (mostly), allowing integration with tools that parse Nmap output (like Searchsploit, Metasploit, or raw ingestion into databases).
- **Grepable format (`-oG`)**: Similar to Nmap's grepable format.

### Parsing Masscan for Nmap
A standard Red Team workflow is to use Masscan to find open ports rapidly across a massive scope, then feed those specific IP:Port combinations into Nmap for detailed service enumeration, version detection, and scripting.

```bash
# 1. Run Masscan and output to JSON
sudo masscan 10.10.0.0/16 -p1-65535 --rate 50000 -oJ masscan.json

# 2. Parse JSON using jq to extract IPs and Ports into a list
cat masscan.json | jq -r '.[] | "\(.ip):\(.ports[0].port)"' > open_ports.txt

# 3. Using a bash one-liner to pass results to Nmap
# Note: Complex formatting may be required if you want to group multiple ports per IP
awk -F: '{ports[$1] = ports[$1] "," $2} END {for (ip in ports) print ip, substr(ports[ip], 2)}' open_ports.txt | while read ip portlist; do nmap -sV -p "$portlist" "$ip"; done
```

## 7. Tuning and Troubleshooting Considerations

- **No Results / Mass Dropped Packets**: If your rate is too high, your local router's ARP table might overflow, or the ISP might drop packets entirely. Always test on a known-open port first. If it fails, reduce the `--rate`.
- **Inaccurate Results**: Scanning through NAT or VPNs heavily impacts Masscan. It is highly recommended to run Masscan directly on a public IP or a network without restrictive stateful firewalls.
- **Source Port Interference**: Use `--source-port 60000` to bind Masscan to a specific source port. This makes it easier to configure `iptables` rules to silently drop the host OS's RST packets if you are sharing an IP address and want to prevent the OS from tearing down connections during banner grabbing.
  ```bash
  iptables -A INPUT -p tcp --dport 60000 -j DROP
  ```

## 8. Extreme Scale Engagements: The 10-Gigabit Limit

When pushing beyond standard Gigabit Ethernet into the 10-Gigabit space, hardware bottlenecks become immediately apparent. The primary issue is PCIe bus saturation and CPU interrupt handling.
Even with PF_RING or DPDK (Data Plane Development Kit), moving 14 million 64-byte packets per second requires careful NUMA (Non-Uniform Memory Access) pinning.
If Masscan's transmit thread is running on a CPU core in NUMA node 0, but the NIC is attached to the PCIe lanes of NUMA node 1, the packets must traverse the QPI (QuickPath Interconnect), adding microseconds of latency per packet and halving the maximum transmit rate.
Advanced users must use `taskset` to bind Masscan to the precise core affinity closest to the NIC.

Additionally, when scanning the entire IPv4 space at 10-GigE speeds, you must randomize your source IP address (using the `--source-ip 1.1.1.1-1.1.1.255` format) assuming you control an entire /24 block. If you transmit 10 million pps from a single IP address, the return traffic (SYN-ACKs, RSTs, ICMP Unreachables) will converge into a micro-burst that will overwhelm the Top-of-Rack (ToR) switch buffers, leading to devastating tail-drops and network collapse.

## 9. Operational Security (OPSEC)

Masscan is exceptionally loud. A default high-speed scan will instantly trigger virtually any properly configured IDS/IPS (Suricata, Snort, Zeek). It is not designed for stealth; it is designed for scale.

If stealth is required, Masscan is the wrong tool. Nmap with slow timing (`-T2` or `-T1`), randomized hosts, and packet fragmentation is heavily preferred. Masscan is the tool of choice exclusively when speed and coverage are prioritized over discretion.

### Circumventing Threat Intelligence Feeds
In modern Red Teaming, scanning from a known static VPS (like DigitalOcean, Linode, or AWS) is often ineffective because corporate firewalls subscribe to Threat Intelligence feeds (like GreyNoise or CrowdStrike) that categorize these ASNs as "Scanner/Malicious."
To maintain effectiveness while using Masscan, operators must route traffic through residential proxy networks or rapidly rotate cloud infrastructure using Terraform, acquiring and discarding ephemeral IP addresses before the Threat Intel feeds can classify them.

## 10. Threat Hunting and Blue Team Defense Against Masscan

From a defensive perspective, identifying and mitigating Masscan activity is relatively straightforward compared to low-and-slow Nmap scans.
Because Masscan sends packets sequentially across its randomized target array, the ingress firewall will see a massive spike of incoming SYN packets originating from a single IP (or small block of IPs) destined for the same port across hundreds of internal hosts.
- **Zeek/Bro Signatures**: Zeek can be configured to flag and automatically shun IP addresses that initiate more than 100 connection attempts to disparate internal IP addresses within a 1-second window.
- **TCP Timestamp Anomalies**: By default, Masscan might lack the complex TCP option padding that typical OS stacks include. Packet inspection can reveal structural anomalies in the SYN packet itself, identifying it as synthetic rather than organic traffic.

To respond to an active Masscan sweep:
1. Implement edge-layer Rate Limiting on SYN packets per source IP.
2. Null-route the offending ASN at the BGP level if the scan is part of a larger DDoS or aggressive credential-stuffing precursor.

## 11. Chaining Opportunities
- **Rustscan Integration:** Use Masscan output to feed target lists into [[47 - Rustscan Fast Pre-Scanner for Nmap]] if you want Rustscan's automatic Nmap execution features but Masscan's wide-area speed.
- **Vulnerability Scanning:** Feed HTTP ports identified by Masscan directly into [[08 - FFuF Directory Fuzzing]] or [[14 - Nuclei Vulnerability Scanner]] for immediate exploitation at scale.
- **Brute Forcing:** Pass open SSH/FTP/Telnet ports to [[50 - Hydra All Protocols Reference]] for mass credential stuffing across an enterprise environment.
- **Metasploit Auto-Exploitation:** Parse Masscan XML into Metasploit workspaces using `db_import` and leverage [[48 - Metasploit Auxiliary Exploits Post Modules]] for automated testing.

## 12. Related Notes
- [[02 - Nmap Port Scanning Techniques]]
- [[47 - Rustscan Fast Pre-Scanner for Nmap]]
- [[14 - Nuclei Vulnerability Scanner]]
- [[50 - Hydra All Protocols Reference]]
- [[08 - FFuF Directory Fuzzing]]
