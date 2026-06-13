---
tags: [tools, network, exploit, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.47 Rustscan Fast Pre-Scanner for Nmap"
---

# Rustscan Fast Pre-Scanner for Nmap

## 1. Introduction to Rustscan

Rustscan is a modern, hyper-fast port scanner written in Rust. It was designed to solve a specific, pervasive problem in penetration testing: Nmap is incredibly accurate and feature-rich, but when tasked with scanning all 65,535 ports on a host, it is painfully slow. Rustscan operates as a "pre-scanner"—it rapidly identifies open ports using Rust's asynchronous I/O capabilities and then automatically pipes those discovered ports directly into Nmap for detailed service enumeration and scripting.

By leveraging the speed of compiled Rust and asynchronous networking libraries, Rustscan can scan all 65k ports on a local network in less than 3 seconds. It effectively transforms a 20-minute Nmap full-port scan into a sub-10-second operation without sacrificing Nmap's unparalleled capability to accurately fingerprint services and execute Nmap Scripting Engine (NSE) scripts.

Understanding Rustscan is crucial for maximizing efficiency during time-boxed engagements, OSCP exams, and CTF competitions.

## 2. Core Architecture and Asynchronous I/O

Rustscan's speed is derived not from bypassing the kernel (like Masscan) but from highly optimized asynchronous socket handling within user-space.

### Asynchronous Concurrency Model
Traditional Nmap (without heavy tuning) uses synchronous, blocking sockets for connection attempts, or complex select/poll loops that struggle at massive scale. Rustscan utilizes the `tokio` asynchronous runtime. When Rustscan attempts a TCP connect, it does not block the thread waiting for the SYN-ACK. Instead, it yields execution back to the runtime, allowing thousands of other socket connection attempts to be initiated concurrently on the same thread.

### Ulimit Dependency
Because Rustscan relies on the host OS's standard socket API (`connect()`), it is entirely bound by the operating system's file descriptor limit (the `ulimit`). Every open connection requires a file descriptor. If Rustscan attempts to scan 10,000 ports concurrently, it needs 10,000 available file descriptors.

If the `ulimit -n` is set to the default 1024, Rustscan will bottleneck, error out, or dramatically slow down. Properly configuring the `ulimit` is the single most critical factor in optimizing Rustscan.

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                          Rustscan Workflow                              |
+-------------------------------------------------------------------------+
|                                                                         |
|  +--------------------+                                                 |
|  |    Target List     |                                                 |
|  |  (IPs / CIDR)      |                                                 |
|  +--------+-----------+                                                 |
|           |                                                             |
|           v                                                             |
|  +--------------------+      Tokio Async Runtime                        |
|  | Rustscan Engine    | <---------------------------+                   |
|  | - Batch Generation |                             |                   |
|  | - Async Sockets    | ======= SYN packets =====>  |                   |
|  | - Ulimit scaling   | <====== SYN-ACK ============|                   |
|  +--------+-----------+                             |                   |
|           |                                       Target                |
|           | Rapidly outputs Open Ports            Network               |
|           v                                                             |
|  +--------------------+                                                 |
|  | Port Aggregator    |                                                 |
|  | (e.g., 22,80,443)  |                                                 |
|  +--------+-----------+                                                 |
|           |                                                             |
|           | Pipes strictly open ports to Nmap                           |
|           v                                                             |
|  +--------------------+                                                 |
|  | Nmap Subprocess    | ----> Nmap Scripting Engine (NSE)               |
|  | nmap -p22,80,443   | ----> OS Fingerprinting (-O)                    |
|  | -sV -sC <target>   | ----> Version Detection (-sV)                   |
|  +--------------------+                                                 |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 3. Installation and Deployment Nuances

Rustscan can be installed via Cargo, compiled from source, or run via Docker.

### Native Installation (Debian/Ubuntu)
Downloading the `.deb` release is highly recommended for standard Kali Linux or Parrot OS environments as it avoids Docker networking overhead.
```bash
wget https://github.com/RustScan/RustScan/releases/download/2.0.1/rustscan_2.0.1_amd64.deb
sudo dpkg -i rustscan_2.0.1_amd64.deb
```

### Docker Deployment
While Docker is convenient, running network scanners through Docker's bridge network introduces latency and state-tracking overhead that can artificially throttle the scan. If you must use Docker, always use host networking.
```bash
# Optimal Docker Usage
docker run -it --rm --network host rustscan/rustscan:2.x.x -a 10.10.10.1 -- -A -sC
```
*Note: Using `--network host` allows the container to bypass the Docker proxy bridge and directly utilize the host's networking stack, essential for high-speed scanning.*

## 4. Tuning: The Ulimit and Batch Size

To unlock Rustscan's true potential, you must understand the interplay between the host's `ulimit` and Rustscan's `--batch-size`.

### The Batch Size Parameter (`-b`)
The batch size dictates how many concurrent connections Rustscan attempts at any given microsecond. The default is usually around 4500.

### The Ulimit Parameter (`-u`)
The `-u` parameter tells Rustscan what it should automatically configure the system ulimit to be before running.
If your system restricts you from altering the ulimit, you must lower the batch size.

**The Golden Rule of Rustscan Optimization:**
`Batch Size + 100 < Ulimit`
If you want to scan extremely fast on a powerful box:
1. Increase the system file descriptor limit: `ulimit -n 100000`
2. Run Rustscan with a massive batch size: `rustscan -b 65535 -a 10.10.10.1`
This will scan all 65k ports literally instantaneously.

## 5. Advanced Usage and Command Syntax

### Basic Full Port Scan
Scanning a single target, finding open ports, and automatically passing them to Nmap for default scripts and version detection.
```bash
rustscan -a 10.10.10.10 -- -sC -sV
```
*Notice the `--` syntax. Everything *after* the double dash is passed directly to the Nmap subprocess.*

### Subnet Scanning
Scanning a /24 subnet rapidly:
```bash
rustscan -a 10.10.10.0/24 -t 1500 --batch-size 5000
```
*(The `-t` parameter sets the timeout in milliseconds. Lowering it increases speed but risks missing ports on high-latency networks).*

### Skipping Nmap Execution
Sometimes you only want the raw port list without triggering Nmap. This is useful for piping into other tools.
```bash
rustscan -a 10.10.10.10 -g
```
The `-g` (greppable) flag outputs a clean string: `10.10.10.10 -> [22,80,443]`.

### Modifying the Nmap Command
By default, Rustscan runs `nmap -vvv -p <ports> <ip>`. If you pass arguments after `--`, it appends them.
To completely customize the Nmap command, you can use the `--command` flag, or modify the configuration file.

```bash
rustscan -a 10.10.10.10 --command "nmap -Pn -sV -p {port} {ip} -oA full_scan"
```
*Here, `{port}` and `{ip}` are placeholders that Rustscan dynamically populates.*

## 6. Adaptive Learning and Heuristics

Modern versions of Rustscan incorporate adaptive learning. If it detects that a network is highly unstable or dropping packets (often caused by rate-limiting firewalls or an overly aggressive batch size), it can dynamically adjust its internal timeout and concurrency settings to ensure accuracy.

If you are scanning a CTF box locally, you want max aggression. If you are scanning over a sluggish VPN, you should manually raise the timeout (`-t 2000`) and lower the batch size (`-b 2000`) to prevent false negatives.

## 7. Operational Security (OPSEC) Considerations

Rustscan is explicitly designed for speed, making it the opposite of stealthy.
- It initiates full TCP connect scans by default (unless run as root, where it can utilize SYN scans, though Nmap integration still dictates the final traffic profile).
- The extreme concurrency will flood the target network with packets, triggering alerts in Splunk, QRadar, or any standard EDR/IDS system instantly.
- In professional Red Teaming where stealth is paramount, Rustscan is generally avoided in favor of highly fragmented, throttled Nmap SYN scans or entirely passive reconnaissance.

## 8. Deep Dive: Memory Allocation and File Descriptor Limits

A common issue encountered when scaling Rustscan across a `/16` or `/8` is sudden, unceremonious crashing. This often stems from exhaustion of secondary kernel resources beyond just file descriptors.
When you attempt 65,535 simultaneous connections, the kernel must allocate TCP control blocks (TCBs), send buffers, and receive buffers for each socket. Even if the sockets are non-blocking, memory allocation can spike dramatically.
On resource-constrained jump boxes or cheap Virtual Private Servers, this can trigger the Linux Out-Of-Memory (OOM) Killer, which will mercilessly terminate the Rustscan process.
To mitigate this in high-density environments:
1. Ensure the kernel parameter `net.ipv4.tcp_max_syn_backlog` is elevated.
2. Consider lowering the TCP connection timeout globally in the kernel `net.ipv4.tcp_fin_timeout` to reclaim stale sockets faster.
3. If memory is tight, strictly throttle Rustscan's batch size (`-b 1000`) and accept a longer scan duration rather than a crashed process.

## 9. Custom Configuration and Extensibility

Rustscan supports a TOML configuration file (usually located at `~/.rustscan.toml` or `/etc/rustscan/config.toml`). This allows operators to define custom pre-scan scripts or post-scan integrations.
You can redefine the default execution flow entirely. For instance, instead of piping to Nmap, you could pipe directly to a custom Python parser or a centralized database ingestor.

```toml
# Example ~/.rustscan.toml
[rustscan]
batch_size = 5000
timeout = 2000
ports = ["22", "80", "443", "8080"] # Scan only these if not scanning all 65k
```

## 10. Troubleshooting VPN Routing and State Tracking

When executing Rustscan over OpenVPN or WireGuard—common in environments like HackTheBox or TryHackMe—the tun0 interface MTU (Maximum Transmission Unit) and stateful packet inspection can severely degrade performance.
Because Rustscan fires packets asynchronously, the VPN daemon must encrypt and encapsulate them at wire speed. A massive batch size will saturate the CPU core handling the VPN encryption, causing the VPN interface to drop packets silently. The scanner will assume the ports are closed, resulting in massive false negatives.
**Rule of Thumb over VPNs:** Never exceed a batch size of 2000 over a standard OpenVPN connection. Increase the timeout to compensate for the encryption/decryption latency.

## 11. Chaining Opportunities
- **Vulnerability Scanning:** Use `rustscan -g` to quickly extract ports, format them, and pipe directly into [[14 - Nuclei Vulnerability Scanner]].
- **Web Enumeration:** Pass identified HTTP/HTTPS ports to [[08 - FFuF Directory Fuzzing]] or [[17 - Gobuster Directory and DNS Enumeration]].
- **Mass Exploitation:** Output open ports to a file, parse the services, and feed into [[48 - Metasploit Auxiliary Exploits Post Modules]] for automated targeting.
- **Brute Forcing:** Instantly identify management ports (RDP, SSH, WinRM) and pipe target lists into [[50 - Hydra All Protocols Reference]].

## 12. Related Notes
- [[02 - Nmap Port Scanning Techniques]]
- [[46 - Masscan High-Speed Port Scanner]]
- [[14 - Nuclei Vulnerability Scanner]]
- [[08 - FFuF Directory Fuzzing]]
- [[50 - Hydra All Protocols Reference]]
