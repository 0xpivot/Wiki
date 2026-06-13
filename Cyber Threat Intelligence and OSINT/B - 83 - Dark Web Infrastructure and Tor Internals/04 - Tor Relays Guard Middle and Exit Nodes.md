---
tags: [darkweb, tor, infrastructure, vapt]
difficulty: beginner
module: "83 - Dark Web Infrastructure and Tor Internals"
topic: "83.04 Tor Relays Guard Middle and Exit Nodes"
---

# Tor Relays: Guard, Middle, and Exit Nodes

## Introduction to the Relay Topology

The Tor network's security and bandwidth are entirely dependent on a decentralized infrastructure of volunteer-operated servers known as Relays (or Nodes). Without these relays, Onion Routing is impossible. As of modern metrics, the network consists of roughly 7,000 to 8,000 active relays distributing traffic globally. 

Relays are categorized based on their position within a Tor circuit and their configured permissions. Understanding the specific roles, risks, and configurations of Guard, Middle, and Exit nodes is critical for both operating infrastructure and conducting threat intelligence.

## 1. Guard Nodes (Entry Relays)

The Guard node is the first point of contact between the Tor Client (Onion Proxy) and the Tor network. 

### Characteristics and Purpose
*   **Visibility:** The Guard node is the **only** entity in the Tor circuit that knows the true IP address of the user.
*   **Requirements:** To become a Guard, a relay must demonstrate high uptime, high bandwidth, and stability. The Directory Authorities automatically grant the "Guard" flag to relays meeting these criteria.
*   **Guard Pinning:** Historically, Tor clients chose a random entry node for every new circuit. This led to a high probability that, eventually, a user would choose a Guard controlled by a malicious actor. To mitigate this, Tor implemented **Entry Guards**. A Tor client selects a small set of Guard nodes and "pins" them, using the same Guard for all circuits for 2-3 months. This drastically reduces the statistical probability of an attacker profiling a user over time.

## 2. Middle Nodes

The Middle node serves as the vital cryptographic buffer between the Guard and the Exit node.

### Characteristics and Purpose
*   **Anonymity Buffer:** The Middle node knows the IP of the Guard node and the IP of the Exit node. It does **not** know the user's IP, nor does it know the final destination of the traffic. 
*   **Traffic Forwarding:** Its sole job is to receive encrypted cells, peel off one layer of encryption, and pass the cells to the next hop.
*   **Low Risk Operation:** Running a Middle relay is the safest way to contribute to the Tor network. Because traffic neither originates nor terminates at the Middle node, operators are entirely shielded from abuse complaints (DMCA, law enforcement inquiries).

## 3. Exit Nodes

The Exit node is the final hop in the Tor circuit. It is the bridge between the encrypted Tor overlay network and the unencrypted Clearnet.

### Characteristics and Purpose
*   **Visibility:** The Exit node removes the final layer of Tor encryption. It knows the IP address of the Middle node and the destination IP address of the web server the user is trying to reach. It can see the plaintext payload of the traffic (unless the traffic is independently encrypted via HTTPS/TLS).
*   **DNS Resolution:** The Exit node is responsible for performing DNS lookups on behalf of the user.
*   **High Risk Operation:** Because the traffic appears to originate from the Exit node's IP address, the operator will receive all abuse complaints associated with the traffic (hacking attempts, spam, illegal downloads). Operating an Exit node requires dedicated infrastructure, bulletproof hosting, and legal preparedness.

### Exit Policies
To manage risk, Exit nodes implement strict **Exit Policies** defined in their `torrc` configuration file. These policies dictate which IP ranges and ports the node is willing to bridge to the Clearnet.

```conf
# Example /etc/tor/torrc Exit Node Configuration

Nickname MyHighBandwidthExit
ContactInfo admin@example.com
ORPort 9001
DirPort 9030

# Bandwidth Rate Limiting
RelayBandwidthRate 100 MBytes
RelayBandwidthBurst 200 MBytes

# IPv6 Support
IPv6Exit 1

# The Exit Policy: Rejecting high-abuse ports and internal IPs
ExitPolicy reject *:25      # Block SMTP (Spam prevention)
ExitPolicy reject *:137-139 # Block SMB (Worm propagation)
ExitPolicy reject *:445     # Block SMB
ExitPolicy reject *:6881-6999 # Block BitTorrent default ports
ExitPolicy reject 192.168.0.0/16:* # Block internal routing
ExitPolicy reject 10.0.0.0/8:*
ExitPolicy reject 172.16.0.0/12:*

# Allow standard web and secure traffic
ExitPolicy accept *:80      # HTTP
ExitPolicy accept *:443     # HTTPS
ExitPolicy accept *:853     # DNS over TLS
ExitPolicy accept *:993     # IMAPS
ExitPolicy reject *:*       # Default deny all else
```

## 4. Bridge Relays and Pluggable Transports

In regions with oppressive state-level censorship (e.g., China's Great Firewall, Iran), ISPs perform Deep Packet Inspection (DPI) to identify and block Tor traffic. Because the list of standard Guard nodes is public (published in the Consensus), censors simply block all IPs listed as Guards.

To circumvent this, Tor utilizes **Bridges**.
*   **Bridges:** These are unlisted Guard nodes. Their IP addresses are not published publicly. Users must request bridge IPs via email or CAPTCHA-protected websites.
*   **Pluggable Transports (PTs):** Merely hiding the IP is insufficient if the censor uses DPI to identify the cryptographic signature of a Tor handshake. Pluggable Transports alter the visual structure of Tor traffic to look like benign protocols.
    *   **obfs4:** The most common PT. It obfuscates the Tor traffic to look completely random, lacking any recognizable protocol signature.
    *   **meek:** Uses domain fronting. It encapsulates Tor traffic inside HTTPS requests directed at a major cloud provider (e.g., Azure or AWS). The censor only sees an HTTPS connection to `ajax.microsoft.com`. To block it, the censor must block the entire cloud provider, causing massive collateral damage.
    *   **Snowflake:** Uses WebRTC to turn volunteers' web browsers into temporary proxies.

## ASCII Architecture Diagram: Relays and Bridges

```text
=============================================================================================
                      TOR RELAY TOPOLOGY AND CENSORSHIP CIRCUMVENTION
=============================================================================================

[CENSORED REGION] | [STATE FIREWALL] |                   [FREE INTERNET / OVERLAY]
                  |                  |
                  |     (BLOCKED)    |
[STANDARD CLIENT]-+-------- X -------+-> [ PUBLIC GUARD ] -> [ MIDDLE ] -> [ EXIT ] -> [WEB]
                  |  (IP Blacklist)  |   (Listed in Consensus)
                  |                  |
                  |                  |
[CENSORED CLIENT]-+=== (obfs4) ======+-> [ UNLISTED BRIDGE ] -> [ MIDDLE ] -> [ EXIT ] -> [WEB]
(Uses Pluggable   | (Traffic looks   |   (IP not in consensus)
 Transport)       |  like noise)     |
                  |                  |
```

## Real-World Attack Scenario

### Scenario: Malicious Exit Node SSL Stripping Attack

**Context:** The Tor network guarantees anonymity, but it does not guarantee end-to-end data integrity if the user is communicating with a Clearnet site over unencrypted HTTP. A malicious actor can operate a cluster of high-bandwidth Exit nodes to intercept traffic.

1.  **The Setup:** An APT group spins up 50 high-bandwidth Tor Exit nodes. Due to their high bandwidth, the Tor path selection algorithm frequently chooses them as the final hop for users' circuits.
2.  **The Interception:** A user attempts to log into a cryptocurrency exchange. They type `http://crypto-exchange.com` into the Tor Browser.
3.  **SSL Stripping (Active Attack):** The traffic hits the malicious Exit node. The Exit node acts as a Man-in-the-Middle (MitM). When the exchange server attempts to upgrade the connection to HTTPS (via an HTTP 301 Redirect or HSTS), the malicious Exit node strips the redirect. It maintains an HTTPS connection with the server, but forces an unencrypted HTTP connection with the Tor client.
4.  **Payload Modification:** The user's Tor Browser displays an HTTP page. When the user submits their credentials, the malicious Exit node logs the plaintext username, password, and 2FA tokens.
5.  **Execution:** The Exit node forwards the traffic to the server, logging the user in to avoid suspicion, while the APT group simultaneously uses the stolen credentials to drain the victim's wallet.

*Defense:* The Tor Browser enforces "HTTPS-Only Mode" by default to explicitly prevent Exit nodes from performing SSL stripping attacks. However, if a user overrides this or uses older software, the risk remains absolute.

## Relay Logs and Diagnostics

Operating a relay requires constant monitoring. A healthy relay will log its inclusion in the consensus:

```log
[notice] Tor 0.4.7.13 running on Linux...
[notice] Your Tor server's identity key fingerprint is 'MyHighBandwidthExit A1B2C3D4...'
[notice] Bootstrapped 100% (done): Done
[notice] Now checking whether ORPort 192.168.1.10:9001 is reachable... (this may take up to 20 minutes)
[notice] Self-testing indicates your ORPort is reachable from the outside. Excellent.
[notice] Performing bandwidth self-test...done.
```

## Chaining Opportunities
*   The fundamental cryptography utilized by these relays to strip layers of the onion is detailed in [[02 - The Onion Router Tor Architecture and Mechanics]].
*   Understanding how Exit nodes interface with the Clearnet highlights the vulnerability gap that is completely bypassed by utilizing Onion Services, as covered in [[03 - Tor Hidden Services v3 Cryptography]].

## Related Notes
*   [[01 - Clearnet vs Deep Web vs Dark Web]]
*   [[02 - The Onion Router Tor Architecture and Mechanics]]
*   [[03 - Tor Hidden Services v3 Cryptography]]
*   [[05 - I2P Invisible Internet Project Architecture]]
