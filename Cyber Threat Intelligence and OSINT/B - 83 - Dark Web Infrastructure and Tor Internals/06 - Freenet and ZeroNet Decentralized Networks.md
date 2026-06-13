---
tags: [darkweb, tor, infrastructure, vapt]
difficulty: beginner
module: "83 - Dark Web Infrastructure and Tor Internals"
topic: "83.06 Freenet and ZeroNet Decentralized Networks"
---

# Freenet and ZeroNet Decentralized Networks

## Introduction
While the Tor network remains the most popular dark web infrastructure for deep web exploration, alternative decentralized networks like Freenet and ZeroNet provide unique architectures that completely bypass the standard client-server model. Understanding these networks is critical for Cyber Threat Intelligence (CTI) analysts and penetration testers targeting obscure threat actor communications, child exploitation material distribution rings, or decentralized botnet command and control (C2) structures.

Unlike Tor, which provides anonymity for accessing distinct, centrally hosted hidden services, Freenet and ZeroNet distribute the hosting of content across the network participants themselves. This fundamentally alters the operational security (OPSEC) landscape, threat models, and deanonymization vectors for both researchers and adversaries.

## Freenet: The Censorship-Resistant Data Store
Freenet is a peer-to-peer platform for censorship-resistant communication and publishing. It operates as a massive distributed data store, pooling the bandwidth and storage of its member nodes.

### Core Architectural Concepts
1.  **Distributed Hash Table (DHT) Architecture**: Freenet uses a specialized routing algorithm reminiscent of a DHT, but strictly designed for plausible deniability. Nodes do not know what data they are storing, nor do they know the origin of the data traversing their connections.
2.  **Small World Network**: Freenet routing relies on the "small world" phenomenon (similar to six degrees of separation). Connections are optimized to cluster nodes mathematically, drastically reducing the number of hops required to find a specific piece of data.
3.  **Darknet vs. Opennet**:
    *   *Opennet*: Nodes connect to any other Freenet node discovered organically.
    *   *Darknet*: Nodes ONLY connect to manually verified friends. A pure Darknet topology is virtually impossible to map, disrupt, or infiltrate globally, making it a haven for highly paranoid threat actors.

### Freenet Key Types
Data in Freenet is addressed via specific key structures, critical for CTI tracking:
*   **CHK (Content Hash Key)**: Used for static files. The key is derived directly from the hash of the file's contents. If the file changes, the key changes.
*   **SSK (Signed Subspace Key)**: Used for dynamic sites (Freesites). It relies on public-key cryptography. A user generates a key pair; the public key forms the SSK, allowing them to continuously update the site without changing the base address.
*   **USK (Updatable Subspace Key)**: A wrapper around SSK that automatically polls for the highest sequence number, effectively functioning as a continually updating domain name.

### Freenet Data Insertion and Retrieval
When a user requests a file, the request is passed from node to node. Each node checks its local datastore. If it doesn't have the file, it routes the request to the peer it mathematically calculates is most likely to have it. When the file is found, it is passed back along the exact same path, and *each node along the path caches a copy of the file*. This means popular content naturally propagates closer to requesting users, dramatically improving resilience against DDoS.

## ZeroNet: Real-Time Decentralized Web
ZeroNet uses Bitcoin cryptography and the BitTorrent network to build a decentralized web. It is distinctly different from Freenet in that it is not natively designed for extreme anonymity, but rather for absolute resistance to takedowns.

### Core Architectural Concepts
1.  **Site Addressing (BIP32)**: ZeroNet sites are identified by a Bitcoin address (e.g., `1HeLLo4uzjaLetFx6NH3PMwFP3qbRbTf3D`). The site owner holds the private key.
2.  **BitTorrent Synchronization**: When a user visits a ZeroNet site, they connect to the tracker infrastructure (often integrated or federated) and download the site's files from peers currently seeding it, exactly like a BitTorrent swarm.
3.  **Real-Time Updates**: If the site owner updates the content, they sign the new `content.json` file with their Bitcoin private key and push it to connected peers. Peers verify the signature and immediately download the differential updates.

### Namecoin Integration
ZeroNet integrates `Namecoin` (a decentralized DNS system based on blockchain) to allow users to register `.bit` domains. This translates complex Bitcoin addresses into human-readable URLs without relying on ICANN or centralized DNS authorities.

## Architecture Diagram

```text
    FREENET DATAS TORE & ROUTING               ZERONET BITTORRENT HYBRID
    ============================               =========================

      [User A] -> Request SSK                  [User B] -> Visit 1Site...
         |                                        |
         v                                        v
    +---------+       +---------+            +---------+       +---------+
    | Node 1  | ----> | Node 2  |            | Tracker | <---> | Peer 1  |
    | (Cache) |       | (Cache) |            +---------+       +---------+
    +---------+       +---------+                 ^                 |
         |                 |                      | (Peers)         | (Seed)
         v                 v                      v                 v
    +---------+       +---------+            +---------+       +---------+
    | Node 3  | <---> | Node 4  |            | Peer 2  | <---> | Peer 3  |
    +---------+       +---------+            +---------+       +---------+
         |
    (Data Found) -> Propagates back, caching on all nodes.
```

## Threat Modeling for Investigators
Investigating decentralized networks requires distinct OPSEC protocols:
*   **Freenet Threat Model**: Because your node stores encrypted pieces of the entire network's data, you technically possess illicit material. Freenet relies on plausible deniability—the encryption keys are held by the requester, not the host. However, in oppressive regimes, simply running a Freenet node can flag an IP address.
*   **ZeroNet Threat Model**: ZeroNet operates in the clear by default. Your IP address is broadcast to the BitTorrent swarm as a seeder of the site you are visiting. To achieve anonymity, ZeroNet *must* be routed through the Tor network. ZeroNet officially supports Tor integration natively via the `torrc` control port.

## Real-World Attack Scenario

### Scenario: Deanonymizing a ZeroNet Admin via Swarm Leakage
**The Target**: A threat actor running an illegal dark web marketplace exclusively on ZeroNet, assuming that decentralized hosting provides immunity from LEA takedowns.
**The Vulnerability**: The threat actor relies on Tor for anonymity but misconfigures their local ZeroNet client, allowing it to occasionally leak packets outside the Tor tunnel, or they accidentally connect to the swarm via the clearnet during a node reboot.

**The Attack Execution**:
1.  **Swarm Monitoring**: A CTI analyst or LEA deploys hundreds of tracking nodes into the specific BitTorrent swarm associated with the target's ZeroNet site (`1Market...`).
2.  **Traffic Analysis**: The tracking nodes log all incoming connections, aggressively attempting to map IP addresses to node IDs.
3.  **Update Correlation**: The attacker waits for the site admin to push a live update (`content.json` modification). The nodes immediately connected to the originating source of the update are analyzed.
4.  **Clearnet Leak**: Due to a split-routing vulnerability on the target's machine, a single UDP packet destined for a tracker escapes the Tor network.
5.  **Attribution**: The tracking nodes log the true IP address of the target. Although the site cannot be "taken down" (as it lives forever on seeded peers), the admin is identified, raided, and arrested.

## Defensive Strategies & Mitigation
For researchers conducting CTI on these networks, strict OPSEC must be maintained:
1.  **Strict Isolation**: Never run Freenet or ZeroNet on a host OS. Always utilize dedicated VMs (like Whonix) where the network is force-routed through Tor or a VPN, physically preventing clearnet leaks.
2.  **Storage Ephemerality**: Use amnesic systems (Tails) or encrypted virtual disks that are wiped after each investigation session to prevent accumulation of cached illicit data (especially relevant for Freenet).
3.  **Tor Integration**: Ensure ZeroNet's `[tor]` configuration is strictly enforced (`tor = always`), disabling direct clearnet peer connections.

## Advanced Topics
### Freenet Plausible Deniability Mathematics
Freenet's plausible deniability relies on the fact that an observer cannot distinguish whether a node is requesting data for its own user or merely routing a request for another node. The probability of the local node being the actual requester approaches zero as the network size increases, assuming standard Opennet topology.

### ZeroNet and Smart Contracts
Future iterations of decentralized hosting are moving towards integrating smart contracts (e.g., Ethereum-based decentralized storage like IPFS + Filecoin or Swarm), which introduce financial incentives for seeders. Tracking the blockchain transactions associated with these hosting contracts provides a novel vector for OSINT tracking of infrastructure funding.

## Chaining Opportunities
Understanding decentralized protocols enables researchers to track threat actors as they migrate infrastructure. If a traditional Tor Hidden Service is taken offline, actors frequently establish fallback points on ZeroNet. Cross-referencing PGP keys or Bitcoin addresses found on Tor with ZeroNet directories is a primary chaining technique.

## Related Notes
* [[07 - OPSEC for Dark Web Researchers]] - Critical guidelines before accessing these networks.
* [[08 - Setting up a Secure Investigation VM Whonix Tails]] - Setting up the environment safely.
* [[01 - Introduction to Tor and Hidden Services]] - Comparing decentralized networks with Tor.
* [[10 - Cryptocurrencies in the Dark Web Bitcoin Privacy]] - Analyzing the BIP32 addresses used in ZeroNet.
