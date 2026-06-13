---
tags: [tools, vapt, utility, network, performance]
difficulty: intermediate
module: "41 - Tools"
topic: "41.05 Rustscan"
---

# Rustscan: The Modern, High-Velocity Port Scanner

## 1. Executive Summary & Overview
Rustscan is a relatively recent, highly impactful addition to the network reconnaissance landscape. Authored in the Rust programming language, it was designed specifically to solve a persistent frustration in Vulnerability Assessment and Penetration Testing (VAPT): the painful slowness of executing comprehensive, all-port (1-65535) Nmap scans.

Rustscan operates on a brilliant, synergistic philosophy: it uses the raw, multi-threaded speed of Rust to instantaneously identify open ports, and then seamlessly pipes those exact ports into Nmap to perform the complex, stateful version detection and scripting engine analysis that Nmap excels at. It acts as an incredibly fast, highly optimized wrapper and pre-processor for Nmap.

By segregating the tasks—giving the raw discovery phase to Rust and the analytical phase to Nmap—Rustscan drastically reduces the time required for complete infrastructure enumeration. An all-port scan that might take Nmap 30 minutes can often be completed by Rustscan in under 5 seconds, immediately feeding into a targeted 15-second Nmap scan. It has rapidly become the default first-strike network tool for modern penetration testers, CTF players, and bug bounty hunters.

## 2. Core Architecture & Operating Principles
Unlike Masscan, which bypasses the operating system entirely and requires root privileges and complex routing configurations, Rustscan utilizes the standard operating system socket APIs. However, it leverages the concurrency primitives inherent to the Rust language (specifically, asynchronous runtimes like Tokio) to open thousands of non-blocking TCP connections simultaneously.

Rustscan limits itself strictly to the TCP Connect (`-sT`) method (and limited UDP support). It does not craft raw packets. It attempts to open a standard TCP connection. If the connection succeeds, the port is open; if it fails or times out, it is closed or filtered. Once the hyper-fast Rust engine completes its scan, it automatically constructs a highly specific Nmap command string, injecting only the identified open ports, and executes Nmap as a child process.

### ASCII Architecture Diagram: The Rustscan Pipeline

```text
    +-----------------------------------------------------------------------------------+
    |                                    Rustscan                                       |
    |                                                                                   |
    |  1. Configuration Input (IP targets, port ranges, timeout, ulimit, Nmap flags)    |
    |                                      |                                            |
    |                                      v                                            |
    |  +-----------------------------------------------------------------------------+  |
    |  |                           Rust Async Engine                                 |  |
    |  |                                                                             |  |
    |  |  Spawns thousands of concurrent non-blocking TCP Connect() requests.        |  |
    |  |  Managed by high 'ulimit' (file descriptors).                               |  |
    |  +-----------------------------------------------------------------------------+  |
    |                                      |                                            |
    |                                      v                                            |
    |  2. Raw Open Port List Output (e.g., [22, 80, 443, 8080])                         |
    |                                      |                                            |
    |                                      v                                            |
    |  3. Dynamic Nmap Command Generation                                               |
    |     (e.g., nmap -vvV -p 22,80,443,8080 <target> -sC -sV)                          |
    |                                      |                                            |
    |                                      v                                            |
    |  +-----------------------------------------------------------------------------+  |
    |  |                          Nmap Child Process                                 |  |
    |  |                                                                             |  |
    |  |  Executes deep version scanning and NSE scripts ONLY on the open ports.     |  |
    |  +-----------------------------------------------------------------------------+  |
    +-----------------------------------------------------------------------------------+
```

## 3. Deep Dive into Primary Capabilities

### 3.1 Adaptive File Descriptor Limits (ulimit)
The absolute bottleneck for any standard socket-based scanner is the operating system's limit on open file descriptors. Every open TCP connection is a file descriptor.
*   **Automatic Scaling**: Rustscan intelligently detects the system's `ulimit -n` setting. If the limit is too low (e.g., the default 1024), Rustscan cannot scan fast.
*   **The `--ulimit` Flag**: Testers typically execute Rustscan with the `-b` (batch size) and `--ulimit` flags set very high (e.g., `ulimit -n 100000` on the host, and `-b 10000` in Rustscan) to allow the tool to open thousands of simultaneous connections without hitting kernel resource exhaustion errors.

### 3.2 Seamless Nmap Integration
The true magic of Rustscan is its handoff mechanism.
*   **Default Behavior**: By default, after finding open ports, Rustscan automatically runs `nmap -vvv -p <open_ports> <target>`.
*   **Custom Nmap Flags**: Testers can pass any standard Nmap flag to the underlying process by appending them after a `--` separator.
    `rustscan -a 192.168.1.100 -- -sC -sV -A -oA detailed_scan`
    This tells Rustscan: "Find the open ports fast, then run Nmap with default scripts, version detection, aggressive mode, and output all formats."

### 3.3 Grepable Output and Extensibility
While it excels as an Nmap wrapper, Rustscan can be used purely as a discovery tool.
*   **`-g` (Greppable)**: Outputs simply the IP and a comma-separated list of ports. Essential for piping output into other tools in a bash one-liner.
*   **Scripting Engine**: Rustscan features a rudimentary scripting engine allowing testers to define exactly what happens after open ports are found, enabling integrations with tools beyond just Nmap.

## 4. Advanced Configuration & Optimization

### 4.1 Batch Size and Timeout Tuning
Rustscan's speed is dictated by how many connections it attempts simultaneously and how long it waits for a response.
*   **`-b` (Batch Size)**: Determines how many ports are scanned concurrently. A batch size of 5000 means 5000 SYN packets are sent before checking the queue. Too high, and the local network interface drops packets; too low, and the tool is slow.
*   **`-t` (Timeout)**: The time in milliseconds to wait for a response. The default is usually fine for local networks, but when scanning over unstable VPNs or the internet, increasing the timeout (e.g., `-t 2000`) prevents false negatives (marking a port closed just because of high latency).

### 4.2 Handling Firewalls and Rate Limiting
Rustscan is explicitly *not* a stealth tool. Its philosophy is noise and speed.
*   **Drawback**: Because it opens thousands of full TCP connections in seconds, it is immediately flagged by almost any Intrusion Prevention System (IPS) or basic firewall rate-limiting rule.
*   **Mitigation**: If a target environment utilizes strict rate limiting, Rustscan is the wrong tool. Testers must revert to Nmap's `-T2` timing templates. Rustscan is designed for CTF environments, internal networks without east-west firewalling, or initial massive-scope external bug bounty reconnaissance where noise is less relevant than discovery speed.

### 4.3 IPv6 Support
Unlike some older, highly optimized scanners, Rustscan fully supports IPv6 target ranges, maintaining its extreme speed advantages across modern network architectures.

## 5. Real-World Attack Scenarios / Case Studies

### Scenario A: Penetration Testing Lab / CTF Domination
1.  **Objective**: In a time-restricted environment like an OSCP exam or HackTheBox scenario, a tester needs to find all non-standard open ports on a target IP (`10.10.10.50`) instantly.
2.  **Execution**: Instead of waiting 15 minutes for `nmap -p-`, the tester runs:
    `rustscan -a 10.10.10.50 --ulimit 5000 -- -sC -sV -oA target`
3.  **Result**: Rustscan scans 65,535 ports in 2 seconds, finding ports 22, 80, and a hidden service on 33060. It immediately launches Nmap against *only* those three ports. The full script and version enumeration completes in 30 seconds.

### Scenario B: Internal Subnet Discovery
1.  **Objective**: A red team has landed on a pivot machine in a corporate `/24` subnet and needs to map all available web servers quickly before the Blue Team notices the compromised pivot point.
2.  **Execution**: The tester uses Rustscan to scan specifically for common web ports across the entire subnet:
    `rustscan -a 192.168.50.0/24 -p 80,443,8080,8443 -b 1000 -g > web_ports.txt`
3.  **Result**: Rustscan rapidly identifies all alive web services. The grepable output is then fed into a tool like EyeWitness for immediate screenshotting of the internal applications.

## 6. Defensive Posture & Evasion Techniques
Defending against Rustscan is primarily about detecting anomalous volumetric traffic.
*   **Connection Rate Limiting**: Firewalls configured to track the `state` of connections can easily detect Rustscan. A rule that blocks an IP address attempting more than 100 new TCP connections per second will instantly neutralize Rustscan.
*   **IDS Signatures**: While Rustscan uses standard TCP Connects, the sheer velocity and sequential (or predictably batched) nature of the port queries are highly recognizable to tools like Snort or Suricata.
*   **Lack of Stealth**: As stated, Rustscan provides zero evasion capabilities. It does not perform SYN stealth scans, fragment packets, or spoof source IPs. It trades all subtlety for unparalleled execution speed.

## 7. Automation, API, & CI/CD Integrations
Rustscan is frequently utilized in bash scripting and automation pipelines due to its speed and predictable output.
*   **Automated Bug Bounty Workflows**: Bug bounty hunters use subfinder to get a list of subdomains, resolve them to IP addresses, and pipe the entire list into Rustscan.
*   **Integration with Vulnerability Scanners**: Rustscan's ability to act as a discovery layer means its output can be formatted (using `awk` or custom parsers) to feed target lists to Nessus or OpenVAS via API, ensuring the heavy vulnerability scanners only spend time on verified open ports.

## 8. Chaining Opportunities
*   **Rustscan -> Nmap**: The primary, built-in chain. This is the entire reason the tool exists.
*   **Rustscan -> ffuf**: After using Rustscan to quickly identify anomalous HTTP ports across a subnet, the resulting `http://ip:port` list is fed into ffuf to commence high-speed directory brute-forcing.
*   **Rustscan -> Searchsploit**: The Nmap child process output (containing version data) is fed into Searchsploit for rapid exploit discovery.

## 9. Related Notes
*   [[03 - Nmap]] - The analytical engine that Rustscan relies upon for deep enumeration.
*   [[04 - Masscan]] - The internet-scale alternative, useful when bypassing the OS kernel is required.
*   [[14 - Network Reconnaissance]] - The operational phase where Rustscan significantly reduces time expenditure.
*   [[06 - ffuf]] - Often the next logical step after Rustscan identifies web services.
