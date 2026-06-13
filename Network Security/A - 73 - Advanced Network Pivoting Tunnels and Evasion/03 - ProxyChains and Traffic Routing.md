---
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
topic: "73.03 ProxyChains and Traffic Routing"
---

# 73.03 ProxyChains and Traffic Routing

## 1. Introduction to ProxyChains
Establishing a SOCKS proxy (via SSH, Chisel, or Metasploit) is only the first half of the pivoting battle. To actually utilize the proxy, offensive tools need to be instructed to route their traffic through it. While some GUI applications (like Firefox, Burp Suite, or FoxyProxy) have native proxy configuration settings, the vast majority of command-line tools (Nmap, Hydra, Netcat, CrackMapExec) do not natively support passing traffic through a SOCKS proxy.

**ProxyChains** (and its modern fork, **ProxyChains-NG**) is the industry-standard solution for this problem. It acts as a transparent intermediary, hooking network-related system calls in dynamically linked programs and forcing their outbound connections through a specified proxy or chain of proxies.

## 2. ASCII Architecture Diagram

```text
[Offensive Tool]             [Proxychains System Hook]              [Local SOCKS Proxy]
 Nmap / Hydra   ===========>   LD_PRELOAD Hooking      ===========>   127.0.0.1:9050
 (Executes as      Intercepts: connect()                      (SSH -D or Chisel)
  normal)                      gethostbyname()                        |
                               sendto()                               |
                                                                      V
                                                        [Compromised Pivot Machine]
                                                        (10.10.10.50 via Tunnel)
                                                                      |
                                                                      V
                                                            [Internal Target Server]
                                                            (192.168.100.25:445)
```

## 3. How ProxyChains Works: The LD_PRELOAD Mechanism
Proxychains operates by utilizing the `LD_PRELOAD` environment variable inherent to Linux operating systems. When a dynamically linked binary is executed with `LD_PRELOAD` set, the OS dynamic linker loads the specified shared library *before* any other libraries, including the standard C library (`libc`).

Proxychains injects a shared object (e.g., `libproxychains4.so`) into the process space of the tool being executed. This shared object intercepts fundamental networking functions. When the tool attempts to open a socket to a target IP using `connect()`, Proxychains hijacks the call. Instead of letting the connection hit the local network interface, Proxychains opens a connection to the configured SOCKS proxy and instructs the proxy to connect to the final destination on the tool's behalf.

### 3.1. Critical Limitations of LD_PRELOAD
Understanding the limitations of `LD_PRELOAD` is vital for Operational Security (OPSEC).
- **Statically Linked Binaries**: Tools compiled statically do not use dynamic linking to access `libc`. Because they handle system calls internally, `LD_PRELOAD` fails to inject the hooks. Consequently, statically compiled binaries (which includes many modern Golang tools like `ffuf` or `nuclei` if built statically) will **bypass Proxychains completely** and send traffic directly onto the local network, potentially triggering IDS alerts.
- **SUID/SGID Binaries**: For strict security reasons, the Linux kernel ignores the `LD_PRELOAD` variable when executing setuid root binaries (like `sudo nmap` or `ping`). Attempting to run `proxychains sudo nmap` will fail to proxy the traffic.
- **Go Binaries**: Even if dynamically linked, Go binaries often use their own internal networking stack rather than relying on `libc`, meaning proxychains frequently fails to hook them.

## 4. Configuring proxychains.conf
The configuration file is typically located at `/etc/proxychains.conf` or `/etc/proxychains4.conf`. Correct configuration is crucial for stability and evasion.

### 4.1. The Proxy List
At the bottom of the file, you define the proxies you wish to use. You can define multiple proxies to bounce traffic across several compromised hosts.
```text
[ProxyList]
# protocol  ip          port    [user]  [pass]
socks5      127.0.0.1   9050
socks4      127.0.0.1   1080
http        192.168.1.5 3128
```

### 4.2. Routing Modes
When multiple proxies are defined, ProxyChains can route traffic through them in different ways:
- **Strict Chain (`strict_chain`)**: Traffic goes through the proxies in the exact order they are listed. If a single proxy in the chain dies or becomes unresponsive, the entire chain fails and the connection drops.
- **Dynamic Chain (`dynamic_chain`)**: Traffic goes through the proxies in order, but intelligently skips dead proxies. This is the **most recommended** setting for engagement stability, as tunnels frequently drop or lag.
- **Random Chain (`random_chain`)**: Picks a random sequence of proxies from the list. This is extremely useful for evasion and obscuring the origin IP during heavy scanning, as each connection takes a different path.

### 4.3. Preventing DNS Leaks
A "DNS Leak" occurs when your traffic is proxied, but your DNS resolution queries are sent out of your primary local network interface in the clear. This alerts network defenders to the domains you are investigating.
Ensure the following directive is uncommented in `proxychains.conf`:
```text
proxy_dns
```
This forces all DNS requests to be encapsulated and sent through the SOCKS5 proxy, resolving them on the target network. Note: SOCKS4 does not support remote DNS.

## 5. Using ProxyChains with Nmap
Scanning through a SOCKS proxy is vastly different from local scanning. SOCKS proxies only support full TCP connections; they cannot transport raw packets.

```bash
proxychains nmap -sT -Pn -n -p 21,22,80,443,445 10.10.10.0/24
```
**Mandatory Flags Explanation:**
- `-sT`: Forces a TCP Connect scan. SYN scans (`-sS`) require raw sockets, which ProxyChains cannot hook.
- `-Pn`: Disables ICMP ping discovery. SOCKS proxies drop ICMP traffic. Without this, Nmap will assume all hosts are down before even attempting port connections.
- `-n`: Disables reverse DNS lookup by Nmap. Let ProxyChains handle DNS resolution if needed, avoiding local DNS leaks and speeding up the scan.

*Warning: Running full port scans over proxychains is extremely slow due to the TCP handshakes required for every single port across the tunnel latency.*

## 6. Alternative Routing: Sshuttle and Iptables
When `LD_PRELOAD` hooking fails (e.g., when using Golang tools), transparent proxying must be achieved at the kernel routing level.

### 6.1. Sshuttle (The "Poor Man's VPN")
`sshuttle` is a Python tool that creates a transparent proxy over SSH. It automatically modifies local `iptables` rules to intercept traffic destined for specific subnets, wrapping it seamlessly over an SSH session.

```bash
# Route all traffic destined for the 10.10.10.0/24 subnet through the pivot
sshuttle -r user@192.168.1.50 10.10.10.0/24
```
**Benefits:**
- Does not rely on `LD_PRELOAD`. It works flawlessly with statically linked binaries, Golang tools, and SUID binaries.
- No need to prepend commands with `proxychains`.
- It mitigates the "TCP Meltdown" problem by intercepting traffic locally before it becomes a full TCP packet, multiplexing the payload over SSH, and reassembling it on the pivot.

### 6.2. RedSocks Transparent SOCKS
When `sshuttle` is unavailable, `redsocks` can be utilized. Redsocks listens on a local port and redirects intercepted TCP connections to an existing SOCKS/HTTPS proxy. By configuring local Linux `iptables` rules with the `PREROUTING` and `OUTPUT` chains, an attacker can force all local traffic into the redsocks daemon, which then forwards it to the SSH SOCKS proxy. This simulates a full OS-level VPN experience for TCP traffic.

## 7. Troubleshooting
- **"ProxyChains-3.1: connection refused"**: This usually indicates that the local proxy specified in the `.conf` file is dead, listening on the wrong port, or refusing connections. Check your SSH/Chisel tunnels.
- **Massive Timeouts**: The target might be dropping traffic from the pivot, or the proxy chain is too long and latency is causing the TCP connection to time out before the handshake completes. Increase Nmap's timing templates cautiously, or modify `tcp_read_time_out` and `tcp_connect_time_out` in `proxychains.conf`.

## 8. Chaining Opportunities
- ProxyChains is the primary consumer framework for tunnels generated in [[01 - Port Forwarding Local Remote and Dynamic]] and [[02 - SSH Tunneling and SOCKS Proxies]].
- For UDP and ICMP traffic support, attackers must abandon ProxyChains and migrate to Layer 3 tunnels via [[05 - Ligolo-ng Advanced TUN Interface Pivoting]].
- ProxyChains can be used to route subsequent C2 staging traffic over initial SOCKS channels established via [[04 - Chisel for TCP UDP Tunneling]].

## 9. Related Notes
- [[01 - Port Forwarding Local Remote and Dynamic]]
- [[02 - SSH Tunneling and SOCKS Proxies]]
- [[04 - Chisel for TCP UDP Tunneling]]
- [[05 - Ligolo-ng Advanced TUN Interface Pivoting]]
