---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.10 SOCKS Proxies and Pivoting with Mythic"
---

# SOCKS Proxies and Pivoting with Mythic

## Introduction
Lateral movement in modern networks rarely involves direct internet access from internal subnets. Once an initial foothold is established, Red Team operators must route their attacking tools through the compromised host to access segmented internal networks. 

Mythic natively supports proxying traffic via the SOCKS5 protocol. By leveraging agents like Apollo, Poseidon, or Athena, operators can expose a local SOCKS port on their Mythic server that dynamically tunnels TCP (and sometimes UDP) traffic through the C2 channel and out of the compromised endpoint.

## Core Capabilities
- **SOCKS5 Protocol**: Standard proxy protocol supported by almost all offensive tooling (Nmap, Impacket, CrackMapExec, Metasploit).
- **Reverse Port Forwarding**: Exposing internal network services back to the operator.
- **Chained Proxies**: Routing traffic through multiple compromised hosts (e.g., Host A -> Host B -> Target C) to bypass strict network segmentation.
- **Protocol Encapsulation**: All proxy traffic is wrapped inside the existing C2 communication channel (HTTP/S, WebSockets), maintaining OPSEC and bypassing basic firewalls.

## Architecture and Execution Flow

Understanding how traffic flows through Mythic's proxy architecture is critical for troubleshooting latency and connection drops.

```text
+-------------------+        +-------------------+       +-----------------------+
| Operator Machine  |        |   Mythic Server   |       | Compromised Endpoint  |
|                   |        |                   |       |      (Agent)          |
| +---------------+ |        | +---------------+ |       | +-------------------+ |
| |  Proxychains  | |        | |  SOCKS Port   | |       | | Mythic Agent      | |
| |  / Nmap       | | =====> | |  (e.g., 9050) | | ====> | | (SOCKS Thread)    | |
| +---------------+ | TCP    | +---------------+ | HTTP/S| +-------------------+ |
|                   |        |                   |       |          |            |
+-------------------+        +-------------------+       +----------|------------+
                                                                    |
                                                                    v
                                                         +-----------------------+
                                                         | Internal Target (DC)  |
                                                         | Port 445 (SMB)        |
                                                         +-----------------------+
```

## Configuration & Usage

### 1. Initiating the Proxy
To start a proxy, operators issue a command to a supported agent.
For example, in Poseidon:
`socks 9050`
This tells the Mythic server to open port 9050 locally, and binds that stream to the specific agent's callback ID.

### 2. Configuring Proxychains
On the operator's local Linux machine, configure `/etc/proxychains4.conf`:
```text
strict_chain
proxy_dns 
[ProxyList]
socks5  127.0.0.1 9050
```
*Note: Ensure `proxy_dns` is enabled to prevent DNS leaks where your attacking machine attempts to resolve internal domain names against external DNS servers.*

### 3. Executing Tooling
Once configured, prefix standard tools with `proxychains`:
```bash
proxychains impacket-secretsdump DOMAIN.LOCAL/Admin:'Password123'@10.10.5.50
proxychains nmap -sT -Pn -p 445,3389 10.10.5.0/24
```

## Limitations and Caveats

- **TCP Connect Scans Only**: SOCKS5 does not support raw sockets or ICMP. Tools like Nmap *must* use `-sT` (TCP Connect) and `-Pn` (skip ping). SYN scans (`-sS`) will fail.
- **Latency and Callbacks**: If your agent is configured to sleep for 60 seconds (`sleep 60`), every single packet through the proxy will wait up to 60 seconds. Proxies require agents to be in an "interactive" mode (sleep 0) to be usable.
- **Bandwidth Bottlenecks**: Heavy data transfers (like massive BloodHound ingestions or large SMB file copies) can crash the agent or trigger network anomaly detection.

## Operational Security (OPSEC)

Tunneling traffic over C2 is highly noisy. 

### Traffic Analysis Detections
When an agent goes interactive (`sleep 0`) to support a SOCKS proxy, the beaconing pattern changes from periodic, jittered callbacks to a continuous, high-volume stream of data. EDRs and Network Intrusion Detection Systems (NIDS) like Zeek/Suricata easily flag this as "C2 Data Exfiltration" or "Interactive Beaconing".

**Mitigation**:
- Use WebSocket C2 profiles for SOCKS proxying. WebSockets maintain a persistent TCP connection, preventing the overhead and noise of thousands of individual HTTP GET/POST requests.
- Limit concurrent connections in your tooling (e.g., `nmap --max-parallelism 10`).

### The Double-Agent Tactic
To maintain the stealth of your primary initial access payload, spawn a *secondary* agent strictly for proxying. 
1. Primary Agent: HTTP, Sleep 1 hour, Jitter 20%. (Maintains persistence).
2. Secondary Agent: WebSocket, Sleep 0. (Used for pivoting, expendable if caught).

## Real-World Attack Scenario

### The Setup
An operator compromises a DMZ web server (Linux) via a CVE. They deploy a Poseidon agent. The goal is to compromise the internal Windows Domain Controller, which is inaccessible from the internet.

### The Pivot
1. The operator issues `socks 1080` to the Poseidon agent on the web server.
2. The operator uses `proxychains` with `CrackMapExec` to spray local administrator credentials across the internal `10.10.10.0/24` subnet.
3. They find a successful hit on an internal engineering workstation (`10.10.10.55`).
4. Still using the SOCKS proxy, the operator uses Impacket's `wmiexec.py` to execute a PowerShell one-liner on the engineering workstation.
5. The PowerShell one-liner downloads and executes an Apollo agent. 
6. The Apollo agent uses a SMB named-pipe C2 profile, connecting *back* to the DMZ web server, which routes the traffic out to Mythic. 

The operator has successfully established a multi-tier proxy chain, controlling a heavily segmented internal Windows host entirely through the initial Linux beachhead.

## Detection Engineering & Blue Team Notes

Blue Teams should hunt for:
- Large spikes in outbound HTTP/S traffic volume from processes that normally send small, periodic pulses.
- Unexpected internal SMB (445) or WMI (135) connections originating from DMZ or web-facing servers.
- Long-lived WebSocket connections bypassing standard corporate proxy teardown policies.

## Chaining Opportunities
- Understand internal protocols over proxies: [[11 - Impacket and Python Lateral Movement]]
- Deploy agents deep into networks via SMB: [[04 - Named Pipes and SMB P2P C2 Channels]]

## Related Notes
- [[06 - Poseidon Agent macOS and Linux C2]]
- [[08 - Customizing Mythic Agent Builds and OPSEC]]
