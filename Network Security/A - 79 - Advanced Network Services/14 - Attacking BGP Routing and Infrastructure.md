---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.14 Attacking BGP Routing and Infrastructure"
---

# 79.14 Attacking BGP Routing and Infrastructure

## 1. Introduction to BGP (Border Gateway Protocol)

The Border Gateway Protocol (BGP) is the foundational routing protocol of the internet. It is a path-vector protocol responsible for making core routing decisions across the global internet and within massive enterprise WANs. 

Unlike internal routing protocols like OSPF or EIGRP which calculate the fastest technical path based on link bandwidth, BGP routes traffic based on network policies, Autonomous System (AS) paths, and organizational relationships. 
- **Autonomous System (AS)**: A collection of connected IP routing prefixes under the control of a single administrative entity (e.g., an ISP, a large corporation, or a cloud provider). Each AS is assigned a unique AS Number (ASN).
- **eBGP vs iBGP**: eBGP connects entirely different ASes. iBGP is used to route internal traffic within a single AS.

The critical vulnerability in BGP is its legacy design: it was built in an era of absolute trust. By default, if an AS announces that it is the best path to a specific IP block (prefix), the global routing table inherently believes it, lacking intrinsic cryptographic validation of the claim.

---

## 2. Mechanics of Route Propagation

BGP operates over TCP port `179`. When two routers form a BGP session, they exchange full routing tables. Subsequent updates are sent via `UPDATE` messages.
An `UPDATE` message contains:
- **NLRI (Network Layer Reachability Information)**: The IP prefix being announced (e.g., `104.20.0.0/16`).
- **Path Attributes**: Various metrics including the `AS_PATH` (the list of ASNs the route has traversed).

**The Golden Rule of BGP Routing:** The most specific route (longest prefix match) always wins. For example, a `/24` advertisement will ALWAYS override a `/16` advertisement for those specific 256 IPs, regardless of the AS Path length.

---

## 3. BGP Threat Landscape

### 3.1 Route Hijacking (Prefix Hijacking)
Route hijacking occurs when a malicious or misconfigured AS announces an IP prefix that it does not own. 
**Scenario:**
1. A bank owns and legitimately advertises `200.200.200.0/24`.
2. A malicious AS (Attacker) intentionally advertises the more specific prefix `200.200.200.0/25` and `200.200.200.128/25`.
3. Because the global routing table prefers the longest match (`/25` over `/24`), all internet traffic bound for the bank is immediately redirected to the Attacker's AS.
4. The attacker can blackhole the traffic (DoS), or worse, perform Man-in-the-Middle (MitM) attacks by stripping SSL/TLS or serving phishing pages, before proxying the traffic back to the legitimate bank.

### 3.2 BGP Route Leaks
A route leak is typically an accidental but catastrophic propagation of routing information beyond its intended scope, violating peering agreements.
For example, a small corporate network connected to two different Tier-1 ISPs might accidentally advertise routes learned from ISP A over to ISP B. ISP B now thinks the small corporate network is a transit provider to ISP A and dumps massive amounts of internet backbone traffic onto the small corporate network, causing immediate saturation and massive outages.

### 3.3 AS Path Spoofing
Attackers can manually craft the `AS_PATH` attribute in their BGP updates. By prepending a target's ASN to the path, the attacker can manipulate loop-prevention mechanisms. If the target AS sees its own ASN in a received path, it will drop the route (thinking a routing loop occurred), effectively isolating the target from that specific path.

### 3.4 BGP Session Reset and DoS Attacks
Because BGP relies on TCP `179`, it is susceptible to standard TCP attacks.
- **TCP RST Spoofing**: If an attacker can guess the TCP sequence numbers between two peering BGP routers, they can spoof a TCP RST packet, tearing down the BGP session.
- **Resource Exhaustion**: Sending massive numbers of fake prefix updates can overwhelm the RAM and CPU of a routing engine, crashing the router.

---

## 4. Real-world Scenarios and Case Studies
- **Pakistan Telecom / YouTube (2008)**: Pakistan Telecom attempted to censor YouTube internally by hijacking its `/24` block. However, they accidentally leaked this route to their upstream provider. The global internet accepted the route, effectively blackholing YouTube traffic globally for hours.
- **Amazon Route 53 Hijack (2018)**: Attackers hijacked Amazon DNS IP prefixes. Traffic bound for AWS Route 53 was redirected to Russian servers, where the attackers responded to DNS queries for `myetherwallet.com`, directing victims to a malicious site and stealing millions in cryptocurrency.

---

## 5. Securing BGP Routing

### 5.1 RPKI and ROA (Resource Public Key Infrastructure)
RPKI is the modern defense against prefix hijacking. It uses a cryptographic hierarchy to link IP prefixes to ASNs.
- **ROA (Route Origin Authorization)**: A cryptographically signed object stating which ASN is legally authorized to originate a specific IP prefix, and what the maximum prefix length (e.g., `/24`) is allowed.
- When BGP routers receive a route update, they validate the origin ASN against the global RPKI cache. If the route is "Invalid", it is dropped.

### 5.2 BGPsec (BGP Security)
While RPKI validates the *origin* of a route, BGPsec uses cryptography to validate the entire *AS Path*. Each AS signs the update as it passes through, preventing Path Spoofing. However, adoption is extremely slow due to high computational overhead on routers.

### 5.3 MD5/TCP-AO Authentication
To prevent TCP RST spoofing and rogue session establishment, neighboring BGP routers should authenticate BGP sessions using TCP MD5 signatures or the newer TCP Authentication Option (TCP-AO).

---

## 6. ASCII Diagram: BGP Hijacking Vector

```text
       Normal Traffic Flow:
       [User] ----> [ISP A] ----> [ISP B] ----> [Bank AS] (Advertises 200.200.0.0/16)
       
       Hijack Attack Flow:
                                             (Advertises more specific 200.200.0.0/24)
                                             +-----------------------------------+
                                             |                                   v
       [User] ----> [ISP A] ----> [ISP B] ---+--> [Attacker AS] (Malicious Routing)
                                             |
                                             |  (Attacker sniffs traffic, then proxies to Bank)
                                             +-----------------------------------> [Bank AS]
```

---

## 7. Chaining Opportunities
- **BGP Hijacking to Let's Encrypt MitM**: Hijacking a target's IP prefix to intercept ACME HTTP-01 challenges, allowing the attacker to issue valid SSL/TLS certificates for the victim's domain. This enables perfect, warning-free HTTPS interception.
- **Router Exploitation to BGP injection**: Using default SNMP community strings to gain write access to an edge router, then injecting rogue BGP configurations to silently siphon traffic or create routing blackholes inside the enterprise WAN.

---

## 8. Related Notes
- [[11 - IoT Protocols MQTT and CoAP Exploitation]]
- [[12 - CAN Bus and Automotive Network Exploitation]]
- [[13 - VoIP and SIP Protocol Attacks]]
- [[04 - VLAN Hopping and Layer 2 Attacks]]
