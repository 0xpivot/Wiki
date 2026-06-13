---
tags: [bgp, routing, hijacking, mitm, infrastructure]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.35 BGP"
---

# BGP — Route Hijacking

## 1. Executive Summary
The Border Gateway Protocol (BGP) is the fundamental exterior gateway routing protocol that binds the global internet together. It facilitates the exchange of routing and reachability information among Autonomous Systems (AS)—the massive networks operated by ISPs, tech giants, and universities. 

Unlike internal routing protocols (like OSPF or EIGRP) that calculate paths based on link speed or metrics, BGP calculates paths based on organizational network policies and rules. The most critical security flaw in the original design of BGP is its reliance on **implicit trust**. When a BGP router announces that it owns a specific block of IP addresses (an IP prefix), neighboring routers inherently trust that announcement. 

This lack of built-in cryptographic authentication leads to **BGP Route Hijacking**. By maliciously or accidentally announcing ownership of a victim's IP prefix, an attacker can manipulate the global routing table. This allows the attacker to silently redirect all internet traffic destined for the victim through their own infrastructure, facilitating massive-scale Man-in-the-Middle (MitM) attacks, cryptocurrency theft, or devastating Denial of Service (DoS) conditions.

## 2. Technical Architecture: BGP Protocol
- **Autonomous Systems (AS):** Each major network on the internet is assigned an Autonomous System Number (ASN). BGP operates by announcing which IP prefixes belong to which ASN.
- **TCP Transport:** BGP operates over **TCP port 179**. It requires a reliable transport mechanism to exchange potentially massive routing tables.
- **Path Vector:** BGP is a path-vector protocol. As an announcement propagates across the internet, each AS prepends its own ASN to the `AS_PATH` attribute. Routers use this path to prevent routing loops and to choose the shortest path to a destination.
- **Rule of Specificity:** The most critical rule in IP routing is that the **most specific prefix always wins**. A `/24` route will always be chosen over a `/23` route, regardless of the `AS_PATH` length.

## 3. ASCII Architecture Diagram: BGP Sub-Prefix Hijacking

```text
    [Attacker AS 666]
   Announces: 192.0.2.0/25 (Fake, More Specific)
        |
        v
    [ISP Router C]  <---- Malicious route is accepted (No filtering)
       /      \
      /        \
[ISP Router A]  [ISP Router B]
      \        /
       \      /
     [Victim AS 100]
   Legitimate Owner: 192.0.2.0/24

*Traffic from the internet destined for 192.0.2.10 will route to AS 666, because the attacker announced a /25, which is more specific than the legitimate /24.*
```

## 4. Attack Vectors and Vulnerabilities
### 4.1 BGP Route Hijacking (Exact Prefix Hijacking)
An attacker configures their BGP router to announce an exact match of a prefix they do not own. If the announcement is accepted by their upstream ISP, it propagates. The internet routing table will now have two paths to the same destination. Traffic will split; routers physically closer (in terms of network topology) to the attacker will route traffic to the attacker, while others route to the victim.

### 4.2 Sub-Prefix Hijacking (More Specific Prefix)
This is the most devastating and effective form of BGP hijacking. The attacker announces a more specific prefix than the legitimate owner. For example, if the victim announces `192.0.2.0/24`, the attacker announces two `/25` blocks (`192.0.2.0/25` and `192.0.2.128/25`). Because routers always prefer the most specific route, **100% of global traffic** destined for that block will immediately reroute to the attacker.

### 4.3 BGP Route Leaks
Often accidental, a route leak occurs when an AS propagates routing information it learned from one provider to another provider, violating routing policies. This effectively makes the leaking AS an unintended transit network for global traffic, almost always resulting in massive traffic congestion and localized internet outages.

### 4.4 TCP Session Reset (DoS)
Because BGP peering sessions rely on long-lived TCP connections on port 179, an attacker capable of spoofing a TCP RST packet with the correct sequence numbers can sever the peering session. When the session drops, the router withdraws all routes learned from that neighbor, causing severe routing instability (route flapping).

## 5. Enumeration Methodology
Unlike local network attacks, BGP reconnaissance requires global vantage points.
### 5.1 Public Looking Glasses
Network engineers use public Looking Glass servers to view the global routing table from the perspective of different ISPs around the world.
- Tools: Hurricane Electric BGP Toolkit (`bgp.he.net`), RIPE stat, `bgpq3`.

### 5.2 RIPE stat API Enumeration
You can query the current routing state of an IP prefix using `curl`:
```bash
curl "https://stat.ripe.net/data/bgp-state/data.json?resource=192.0.2.0/24"
```
This returns the ASNs currently announcing the prefix and the accepted AS paths.

## 6. Exploitation Techniques (Lab Environment)
*Warning: Executing BGP hijacks on the public internet is a federal crime and an attack on critical infrastructure. This methodology is strictly for closed lab environments.*

### 6.1 Announcing a Hijacked Route (Using FRRouting)
If an attacker compromises an edge router or peers with an ISP that lacks strict ingress filtering, they can inject malicious routes via the BGP daemon (e.g., Quagga or FRRouting).
```bash
# Enter the FRR routing shell
vtysh

# Enter global configuration mode
conf t

# Select the attacker's BGP process
router bgp 666

# Inject the victim's prefix as a more specific route (/25)
network 192.0.2.0/25
network 192.0.2.128/25
exit
```
The router instantly sends `BGP UPDATE` messages to its peers. If the ISP accepts the route, it propagates globally within minutes.

### 6.2 Traffic Interception and Forwarding
If the attacker simply drops the traffic (a blackhole), the attack acts as a DoS. To perform a MitM attack, the attacker must route the traffic back to the legitimate AS after interception. This is usually accomplished by establishing a GRE tunnel to a router physically close to the legitimate AS, or by manipulating internal routing policies to ensure outbound traffic ignores the hijacked BGP route.

## 7. Post-Exploitation
- **TLS Interception:** Once traffic is hijacked, attackers will often use tools to intercept DNS requests (responding with their own IPs) and attempt to issue fraudulent TLS certificates or strip TLS entirely to steal credentials.
- **Cryptocurrency Theft:** In the famous 2018 Amazon Route 53 hijack, attackers hijacked the BGP routes for Amazon's DNS servers. When users tried to resolve `myetherwallet.com`, the hijacked DNS servers returned the attacker's IP, leading users to a phishing site where their crypto wallets were drained.

## 8. Defensive Evasion
Sophisticated attackers utilize **AS_PATH Prepending** to spoof the origin of the route. Instead of announcing the route originating from their own ASN, they forge the `AS_PATH` so it appears as though the legitimate ASN is announcing it through the attacker's ASN, evading simple origin-validation scripts.

## 9. Incident Response & Detection
Organizations must utilize external monitoring services (e.g., Cisco ThousandEyes, Kentik, RouteViews) to detect BGP hijacks.
- **Detection Logic:** Alert immediately if a new, unauthorized ASN begins announcing the organization's IP prefix, or if an unexpected, more specific sub-prefix (e.g., `/25`) suddenly appears in the global routing table.

## 10. Remediation & Hardening Guide
Securing BGP requires a cooperative effort from all ISPs and network operators.
- **RPKI (Resource Public Key Infrastructure):** The ultimate solution to BGP hijacking. RPKI uses cryptographic certificates to bind IP prefixes to specific ASNs (Route Origin Authorizations - ROAs). Routers are configured to perform Route Origin Validation (ROV), dropping any BGP announcements where the cryptographic signature is invalid or missing.
- **Strict Route Filtering (BCP38 / BCP84):** ISPs must implement strict ingress filtering (Prefix Lists) on customer links. The ISP must only accept BGP announcements for IP prefixes that the customer provably owns.
- **BGP TTL Security Mechanism (GTSM):** To prevent remote TCP reset attacks, routers configure the peering session to expect an IP Time-to-Live (TTL) of 255. Because remote attackers must traverse multiple routers (decrementing the TTL), their spoofed reset packets arrive with a TTL lower than 255 and are dropped.
- **TCP-AO / MD5 Authentication:** All BGP peering sessions should be secured with password authentication to prevent unauthorized routers from establishing sessions.

## 11. Chaining Opportunities
- **[[38 - Man-in-the-Middle (MitM) Attacks]]:** BGP hijacking is the most powerful, nation-state level MitM technique available.
- **[[43 - TLS Downgrade Attacks]]:** Used in conjunction with BGP hijacks to strip encryption from intercepted web traffic.
- **[[11 - DNS Spoofing and Cache Poisoning]]:** BGP hijacking is frequently used to hijack authoritative DNS server IP space, allowing complete control over domain resolution.

## 12. Related Notes
- [[18 - Network Architecture and Topologies]]
- [[66 - Network Denial of Service (DoS)]]
- [[70 - Advanced Persistent Threats (APT)]]
