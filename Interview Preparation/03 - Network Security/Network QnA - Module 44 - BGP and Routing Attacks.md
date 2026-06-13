---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 44"
---

# Network QnA - Module 44 - BGP and Routing Attacks

```text
       Border Gateway Protocol (BGP) Hijacking Architecture
+------------------+                   +------------------+
|   Legitimate AS  |                   |   Attacker AS    |
|   AS Number: 100 |                   |   AS Number: 666 |
| Announces:       |                   | Announces:       |
| 203.0.113.0/24   |                   | 203.0.113.0/25   |
| (Shorter Prefix) |                   | (Longer Prefix)  |
+--------+---------+                   +--------+---------+
         |                                      |
         +-----------------+  +-----------------+
                           |  |
                 +---------+--+---------+
                 |    Internet Transit  |
                 |      Routers         |
                 |  Route selected: /25 |
                 +----------------------+
```

## Formal Technical Questions

**Q1: Explain the fundamental mechanism of a BGP Prefix Hijack. Why does the internet infrastructure inherently trust these malicious route announcements?**
**Answer:**
BGP (Border Gateway Protocol) is the routing protocol of the internet, exchanging routing and reachability information among Autonomous Systems (AS).
- **Mechanism:** A BGP Hijack occurs when a malicious or misconfigured AS announces a route to IP prefixes that it does not own. BGP routers process routes based on two primary metrics:
  1. **Longest Prefix Match:** A more specific subnet announcement (e.g., a `/24` or `/25`) will always be preferred over a less specific one (e.g., a `/16`), regardless of the path length.
  2. **Shortest AS Path:** If the prefix lengths are identical, BGP prefers the route with the fewest AS hops.
- **Trust Model:** BGP was designed in the 1980s with an implicit trust model. Originally, there was no built-in cryptographic validation to verify that an AS actually owned the IP prefix it was announcing. Consequently, when an attacker announces a `/25` route for a target's `/24` block, upstream transit routers accept and propagate the route, diverting global traffic to the attacker.

**Q2: Differentiate between a BGP Prefix Hijack and a BGP Route Leak.**
**Answer:**
- **Prefix Hijack:** Intentional or accidental announcement of IP space not owned by the announcer. The origin AS in the BGP update is falsified or maliciously claimed. The goal is to steal or blackhole traffic.
- **Route Leak:** Usually an accidental misconfiguration. It occurs when an AS propagates routing information learned from one provider/peer to another provider/peer in violation of intended routing policies. For example, a customer AS multi-homed to two Tier-1 ISPs might accidentally advertise routes learned from ISP A to ISP B. ISP B then sends traffic for ISP A through the customer's low-bandwidth network, causing massive congestion and DoS, though the prefix ownership remains legitimate.

**Q3: Explain how an attacker can manipulate the AS_PATH attribute, and why they would do it.**
**Answer:**
The `AS_PATH` is a mandatory BGP attribute that lists all the Autonomous Systems a route has traversed. It is used to prevent routing loops and for path selection.
- **Manipulation:** An attacker can forge the `AS_PATH` by appending fake AS numbers, or more maliciously, appending the AS number of the target they are trying to attack.
- **Why:** If an attacker wants to stealthily hijack traffic from specific regions without tipping off the victim AS, they will append the Victim's AS number to the `AS_PATH`. When the BGP update propagates and reaches the Victim AS (or its immediate peers), the Victim's routers see their own AS number in the path and drop the update (due to built-in loop prevention). This prevents the victim from seeing the hijacked route, while the rest of the internet routes traffic to the attacker.

## Scenario-Based Questions

**Q4: You are performing a Red Team assessment on an internal corporate network running OSPF (Open Shortest Path First) for dynamic routing. Authentication is disabled. How do you exploit this to intercept traffic destined for the domain controllers?**
**Answer:**
Without authentication, OSPF is highly vulnerable to rogue route injection.
1. **Adjacency Establishment:** I would connect to the network and use a tool like `Quagga`, `FRRouting`, or Python's `Scapy` to listen for OSPF Hello packets. I configure my machine to match the OSPF Area ID and timers, successfully forming adjacency with the legitimate internal routers.
2. **LSA Injection:** OSPF routers use Link-State Advertisements (LSAs) to build the topology map. I would generate and flood malicious Type 1 or Type 5 LSAs.
3. **Traffic Diversion:** To intercept traffic bound for the Domain Controller (e.g., `10.10.10.5`), I would advertise a highly specific route (`10.10.10.5/32`) with a metric of 1, pointing to my attacker machine's IP as the next-hop.
4. **MITM Execution:** Internal routers update their routing tables. Traffic destined for the DC flows to me. I enable IP forwarding, log/intercept the traffic (e.g., capturing NTLM hashes or DNS queries), and route it back to the real DC using a secondary interface or static route to maintain connectivity.

**Q5: A telecommunications client is worried about external attackers injecting routes into their external-facing BGP routers. They have implemented TCP MD5 authentication for all BGP peers. Is their BGP infrastructure fully secure against session attacks? What vulnerability still exists?**
**Answer:**
No, they are not fully secure. While TCP MD5 (RFC 2385) prevents unauthenticated session hijacking and blind RST injection, it suffers from severe limitations:
1. **Replay Attacks:** TCP MD5 lacks cryptographic nonces or anti-replay mechanisms. An attacker with a Man-In-The-Middle position can capture MD5-signed BGP packets and replay them later.
2. **Weak Cryptography:** MD5 is cryptographically broken. While practically difficult to crack the TCP MD5 signature quickly enough to hijack an active stream, it is sub-optimal.
3. **BGP TTL Security Hack (GTSM):** The client might be vulnerable to remote DoS. If an attacker spoofs the source IP of a legitimate peer, they can send hundreds of SYN packets to port 179. Even though the MD5 hash fails, the router CPU must expend resources calculating the MD5 hash for every spoofed packet, leading to CPU exhaustion. 
**Recommendation:** Upgrade to TCP-AO (Authentication Option) or IPsec, and implement the Generalized TTL Security Mechanism (GTSM), which ensures incoming BGP packets have a TTL of 255 (meaning they originated from a directly connected peer) dropping spoofed remote packets in hardware.

## Deep-Dive Defensive Questions

**Q6: Describe the Resource Public Key Infrastructure (RPKI) and Route Origin Authorization (ROA). How do they solve BGP prefix hijacking?**
**Answer:**
RPKI provides a cryptographic framework to secure internet routing.
- **ROA (Route Origin Authorization):** A ROA is a cryptographically signed object in the RPKI database. It states which Autonomous System (AS) is explicitly authorized to originate a specific IP prefix, and specifies the maximum prefix length (e.g., max `/24`) allowed.
- **Route Validation:** When a BGP router receives a route announcement, it checks the RPKI database. 
  - If the announcement matches the ROA (correct AS, correct length), the route is `Valid`.
  - If the AS is wrong or the prefix is too specific, the route is `Invalid`.
  - If no ROA exists, it is `Unknown`.
- **Solution:** By configuring routers to drop `Invalid` routes, RPKI strictly prevents origin hijacking. If an attacker AS announces a victim's prefix, the upstream ISP's router validates it against RPKI, sees the AS numbers don't match, and silently drops the malicious update.

**Q7: What is VRF (Virtual Routing and Forwarding) leaking, and how does it compromise network segmentation?**
**Answer:**
VRF allows multiple instances of routing tables to co-exist within the same router simultaneously. It is the Layer 3 equivalent of VLANs, providing deep network segmentation (often used in MPLS networks to separate tenant data).
- **Route Leaking:** VRF leaking is the intentional or accidental configuration that allows routes from one VRF (e.g., `VRF-Guest`) to be imported into another VRF (e.g., `VRF-Corporate`). This is controlled via Route Targets (RTs).
- **Compromise:** If an administrator misconfigures the Route Target import/export policies, an attacker in the `Guest` VRF could gain routing reachability to the `Corporate` VRF. This entirely breaks the Layer 3 segmentation, allowing the attacker to scan, communicate with, and exploit servers in the restricted zone without passing through a firewall.

## Real-World Attack Scenario

**Scenario: BGP Hijacking to Steal Cryptocurrency**
An advanced threat actor aims to steal cryptocurrency by compromising a Web3 service's DNS resolution.
1. **Target Identification:** The Web3 service relies on Amazon Route 53 for DNS (`205.251.192.0/21`).
2. **The Hijack:** The attacker compromises a small, poorly secured ISP in Eastern Europe (the Attacker AS). The attacker configures their BGP router to announce a more specific `/24` subnet corresponding to the exact IP addresses of the Route 53 DNS servers.
3. **Propagation:** Because the attacker announces a `/24`, which is more specific than Amazon's legitimate `/21`, upstream transit providers accept the route. Traffic destined for the DNS servers from significant portions of the internet is diverted to the attacker's AS.
4. **MITM & Phishing:** The attacker sets up rogue DNS servers that intercept queries for the Web3 service's domain. The rogue DNS responds with the IP address of an attacker-controlled phishing server.
5. **Execution:** Users attempting to access the Web3 platform are transparently routed to the look-alike phishing site. They enter their wallet seed phrases, and the attacker drains their cryptocurrency before withdrawing the malicious BGP announcement, leaving little trace.

## Chaining Opportunities
- **Physical/Infrastructure Penetration:** Compromising a core router via default SSH credentials instantly leads to OSPF/BGP manipulation to pivot traffic.
- **DNS Exploitation:** Routing attacks are frequently chained with DNS poisoning to capture Let's Encrypt TLS certificates and serve legitimate-looking phishing pages.
- **Denial of Service:** Route leaks are actively chained with DDoS campaigns to overwhelm mitigation scrubbing centers by misrouting clean traffic.

## Related Notes
- [[11 - MPLS Architecture and Security Vulnerabilities]]
- [[22 - DNS Over HTTPS (DoH) and Infrastructure Security]]
- [[38 - Cryptographic Trust Models in Network Protocols]]
- [[41 - TCP IP Internals]]
- [[59 - Defending Against Advanced Persistent Threats in Telecoms]]
