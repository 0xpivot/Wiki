---
tags: [darkweb, tor, infrastructure, vapt]
difficulty: beginner
module: "83 - Dark Web Infrastructure and Tor Internals"
topic: "83.05 I2P Invisible Internet Project Architecture"
---

# I2P: Invisible Internet Project Architecture

## Introduction to I2P

While Tor is the most recognized anonymity network, the **Invisible Internet Project (I2P)** offers a radically different architectural approach to darknet communications. Tor was designed primarily as a proxy to anonymously access the Clearnet (outproxying), with Hidden Services added later. Conversely, I2P was designed from the ground up to be a completely self-contained, internal darknet. 

I2P is optimized for peer-to-peer (P2P) communication, hidden services (called **Eepsites**), and secure messaging. It eschews Tor's "Onion Routing" in favor of a concept known as **Garlic Routing**.

## Architectural Differences: Tor vs. I2P

To understand I2P, it is best contrasted with Tor:

| Feature | Tor (Onion Routing) | I2P (Garlic Routing) |
| :--- | :--- | :--- |
| **Circuit Type** | Bidirectional (Same path for up/down) | Unidirectional (Separate paths for up/down) |
| **Routing Algorithm** | Onion Routing | Garlic Routing (Message bundling) |
| **Directory Authority**| Centralized Directory Authorities | Decentralized Network Database (NetDB) |
| **Primary Focus** | Outproxy to Clearnet | Internal Darknet Services |
| **Client/Node Role** | Clients and Nodes are distinct | Every client is a routing node by default |
| **Transport Protocol** | TCP exclusively | TCP and UDP (NTCP2 and SSU2) |

## Core Mechanics of I2P

### 1. Garlic Routing
In Tor's Onion Routing, a single message is encrypted in layers and sent down a circuit. In I2P's **Garlic Routing**, multiple messages (often destined for different endpoints) are bundled together into a single encrypted payload—resembling the cloves of a garlic bulb. 
This bundling provides several advantages:
*   It obscures the number of actual communications taking place.
*   It complicates traffic analysis algorithms, as a single encrypted packet payload arriving at a router may splinter into multiple different directions on the next hop.

### 2. Unidirectional Tunnels
This is the most critical structural difference from Tor. 
*   **Tor:** A client builds a 3-hop circuit. Data flows *out* through hops 1 -> 2 -> 3, and the response flows *back* through hops 3 -> 2 -> 1.
*   **I2P:** A client builds separate **Inbound Tunnels** and **Outbound Tunnels**. 
    *   To send a message, Client A sends data down its *Outbound Tunnel*. The data exits the tunnel and is routed to Client B's *Inbound Tunnel*.
    *   When Client B replies, it does not send the data back along the same path. It sends it down its own *Outbound Tunnel*, which routes it to Client A's *Inbound Tunnel*.

Because the request and response take entirely different paths through the network, global traffic correlation attacks become exponentially more difficult. A passive adversary must monitor twice as many distinct tunnels to correlate a single conversation.

### 3. The Network Database (NetDB)
Tor relies on hardcoded Directory Authorities to tell clients which relays are active. This is a centralized point of failure and a target for censorship.
I2P utilizes a **Network Database (NetDB)** based on the Kademlia Distributed Hash Table (DHT) algorithm. 
*   Instead of downloading a consensus document, I2P routers constantly share routing information (RouterInfos) and service locations (LeaseSets) directly with their peers.
*   This makes I2P a true peer-to-peer network, highly resilient to takedowns, as there are no central servers to block.

## Eepsites and Destinations

Hidden services in I2P are called **Eepsites**. They are accessed via domains ending in `.i2p` (e.g., `identiguy.i2p` or long Base32 addresses like `[52-chars].b32.i2p`).

An I2P address does not represent an IP address; it represents a cryptographic **Destination**. A Destination is a set of public keys. When a user requests an `.i2p` address, their router queries the NetDB for the Destination's **LeaseSet**. The LeaseSet contains the current gateway routers (Inbound Tunnels) that the Eepsite is using to receive traffic.

## ASCII Architecture Diagram: Garlic Routing and Tunnels

```text
========================================================================================
                      I2P UNIDIRECTIONAL TUNNEL ARCHITECTURE
========================================================================================

    [ ALICE (Client) ]                                       [ BOB (Eepsite) ]
    Dest: Alice.b32.i2p                                      Dest: Bob.i2p
            |                                                        |
            | (Alice's Outbound Tunnel)               (Bob's Inbound Tunnel)
            V                                                        |
       [ Router A1 ]                                            [ Router B1 ]
            |                                                        ^
            V                                                        |
       [ Router A2 ] =========================================> [ Router B2 ]
       (Endpoint)             (Garlic Bundled Message)          (Gateway)

                                  --- RESPONSE PATH ---

    [ ALICE (Client) ]                                       [ BOB (Eepsite) ]
            ^                                                        |
            | (Alice's Inbound Tunnel)                (Bob's Outbound Tunnel)
            |                                                        V
       [ Router A3 ]                                            [ Router B3 ]
            ^                                                        |
            |                                                        V
       [ Router A4 ] <========================================= [ Router B4 ]
       (Gateway)              (Garlic Bundled Message)          (Endpoint)

========================================================================================
*Note: The Request and Response use completely different sets of routers.
```

## Technical Configuration: I2P Tunnels

I2P configuration is handled via the `i2ptunnel.config` file or the web console. Below is a conceptual configuration for exposing a local SSH server as an I2P service, and an IRC client tunnel.

```ini
# /var/lib/i2p/i2ptunnel.config (Snippet)

# ----------------------------------------------------
# Define a standard server tunnel (Eepsite hosting)
# ----------------------------------------------------
tunnel.0.name=Hidden_SSH
tunnel.0.description=SSH Access over I2P
tunnel.0.type=server

# The target local port to bind the I2P tunnel to
tunnel.0.targetHost=127.0.0.1
tunnel.0.targetPort=22

# Cryptographic profile
tunnel.0.privKeyFile=ssh_privkey.dat
tunnel.0.inbound.length=3  # 3 hops for inbound anonymity
tunnel.0.outbound.length=3 # 3 hops for outbound anonymity
tunnel.0.inbound.lengthVariance=1 # Add random +/- 1 hop variance

# ----------------------------------------------------
# Define a client tunnel (Accessing a specific service)
# ----------------------------------------------------
tunnel.1.name=I2P_IRC
tunnel.1.description=IRC Client Tunnel
tunnel.1.type=client
tunnel.1.interface=127.0.0.1
tunnel.1.listenPort=6668
tunnel.1.targetDestination=irc.postman.i2p
```

## Real-World Attack Scenario

### Scenario: Eclipse Attack on the NetDB

**Context:** Because I2P is entirely decentralized and relies on a DHT (NetDB) for peer discovery, it is theoretically vulnerable to attacks targeting the routing table itself, rather than the cryptographic payloads.

1.  **The Setup:** A well-resourced attacker (State Actor) wishes to de-anonymize a specific Eepsite.
2.  **Sybil Node Injection:** The attacker spins up thousands of malicious I2P routers (a Sybil attack). They engineer the cryptographic IDs of these routers to mathematically surround the target Eepsite's ID within the Kademlia DHT space.
3.  **The Eclipse:** When the target Eepsite attempts to publish its `LeaseSet` (its location data) to the NetDB, the DHT algorithm routes the publication to the nodes mathematically closest to the Eepsite's ID. Because the attacker controls all the surrounding nodes, the target publishes its data directly to the attacker.
4.  **Isolation and De-anonymization:** The attacker's nodes refuse to propagate the target's `LeaseSet` to the rest of the legitimate network. The Eepsite is "eclipsed." Furthermore, because the attacker controls the nodes directly interacting with the Eepsite's inbound/outbound tunnel creation requests, they can conduct intense traffic analysis to trace the Eepsite's physical IP address.
5.  **Mitigation:** I2P developers continuously refine the network's floodfill algorithms and Sybil detection heuristics to make Eclipse attacks prohibitively expensive and difficult to execute.

## I2P Routing Logs

A typical I2P node startup involves bootstrapping to the NetDB and building tunnels:

```log
INFO: Start I2P Router
INFO: Loading NetDB from local cache...
INFO: Bootstrapping to seed nodes (reseeding)...
INFO: Building Outbound Tunnel: [Router A] -> [Router B] -> [Router C]
INFO: Building Inbound Tunnel: [Router X] -> [Router Y] -> [Router Z]
INFO: Successfully published LeaseSet to Floodfill router.
INFO: Accepting participating traffic (acting as a routing node).
```

## Conclusion

I2P provides a highly resilient, internal-focused darknet. While it lacks the sheer user base and Clearnet proxy capabilities of Tor, its unidirectional tunnels and decentralized database make it exceptionally robust against the global traffic correlation attacks that threaten Onion Routing networks.

## Chaining Opportunities
*   Contrasting I2P's architecture directly with Tor's circuit model provides a comprehensive understanding of overlay networks. Refer back to [[02 - The Onion Router Tor Architecture and Mechanics]].
*   Understanding how Eepsites function builds upon the hidden service concepts established in [[03 - Tor Hidden Services v3 Cryptography]].

## Related Notes
*   [[01 - Clearnet vs Deep Web vs Dark Web]]
*   [[02 - The Onion Router Tor Architecture and Mechanics]]
*   [[03 - Tor Hidden Services v3 Cryptography]]
*   [[04 - Tor Relays Guard Middle and Exit Nodes]]
