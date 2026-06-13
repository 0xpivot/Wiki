---
tags: [darkweb, tor, infrastructure, vapt]
difficulty: beginner
module: "83 - Dark Web Infrastructure and Tor Internals"
topic: "83.02 The Onion Router Tor Architecture and Mechanics"
---

# The Onion Router: Tor Architecture and Mechanics

## Introduction to Onion Routing

The Tor (The Onion Router) network is the most widely used and extensively researched anonymity overlay network in existence. Originally conceptualized and funded by the United States Naval Research Laboratory (NRL) in the 1990s, the primary objective was to protect U.S. intelligence communications online. Today, it is an open-source project managed by the Tor Project, utilized by privacy advocates, journalists, whistleblowers, and cyber threat actors alike.

The foundational principle of Tor is **Onion Routing**. This technique involves encapsulating data in multiple layers of encryption—analogous to the layers of an onion. The data is then transmitted through a series of volunteer-operated network nodes (relays). Each node peels away a single layer of encryption to reveal the next destination, ensuring that no single node ever knows both the origin and the final destination of the data.

## Core Architectural Components

To understand Tor's mechanics, one must understand its constituent components:

1.  **Onion Proxy (OP):** The Tor client software running on the user's local machine (e.g., the Tor Browser). The OP is responsible for fetching directory information, constructing circuits, and encrypting data before it enters the network.
2.  **Onion Router (OR):** The relays that form the Tor network. These are volunteer-run servers. A standard Tor circuit consists of three ORs: the Guard (Entry) node, the Middle node, and the Exit node.
3.  **Directory Authorities (DirAuths):** A small, hardcoded group of highly trusted servers that maintain the state of the network. They vote on and publish the "Consensus" document, which lists all active, valid relays and their cryptographic keys.

### The Role of Directory Authorities
Directory Authorities are the anchor of trust in the Tor network. There are typically 9 or 10 Directory Authorities operated by trusted individuals and organizations globally.
*   Every hour, these authorities vote on the status of all known relays.
*   They compile the **Consensus Document**, a signed list of active relays, their bandwidth weights, and their flags (Guard, Exit, Fast, Stable).
*   If a relay is acting maliciously or returning bad data, the DirAuths vote to assign it the `BadExit` flag, effectively removing it from clients' path selection algorithms.

## The Circuit Creation Process

When a Tor client wishes to communicate with a destination server, it must first establish a cryptographic circuit. Tor does not send packets directly; it sends **Cells** through this predefined circuit.

### Step-by-Step Circuit Building

1.  **Directory Fetch:** The client (OP) connects to a Directory Authority to download the latest Consensus document and the corresponding **Microdescriptors** (which contain the public keys of the relays).
2.  **Path Selection:** The OP locally selects three relays:
    *   **Node 1 (Guard):** Selected from a list of stable, high-bandwidth nodes. The OP pins this node for a long duration (typically 2-3 months) to prevent profiling attacks.
    *   **Node 2 (Middle):** Selected randomly from the pool of available relays, weighted by consensus bandwidth.
    *   **Node 3 (Exit):** Selected randomly, but must have an Exit Policy that permits traffic to the requested destination IP and port (e.g., allowing TCP 443).
3.  **Circuit Extension (Telescoping):** The OP establishes the circuit sequentially, negotiating symmetric encryption keys (via Diffie-Hellman handshakes) with each node using the `CREATE/CREATED` and `EXTEND/EXTENDED` cell types.
    *   OP negotiates Key 1 ($K_1$) with the Guard.
    *   OP asks the Guard to extend the circuit to the Middle node, negotiating Key 2 ($K_2$) with the Middle node *through* the Guard.
    *   OP asks the Middle node to extend the circuit to the Exit node, negotiating Key 3 ($K_3$) with the Exit node *through* the Guard and Middle.

### Data Transmission (The Onion)

When the OP wants to send an HTTP GET request, it encrypts the payload three times:
1.  Encrypts payload with $K_3$ (Exit Key).
2.  Encrypts result with $K_2$ (Middle Key).
3.  Encrypts result with $K_1$ (Guard Key).

The packet is sent to the Guard. The Guard decrypts the outer layer using $K_1$, revealing the instruction to forward it to the Middle node. The Middle node decrypts the next layer using $K_2$, forwarding it to the Exit. The Exit decrypts the innermost layer using $K_3$, revealing the plaintext HTTP GET request and the actual destination IP, which it then sends to the Clearnet.

## ASCII Architecture Diagram: The Tor Circuit

```text
========================================================================================
                              THE ONION ROUTING CIRCUIT
========================================================================================

   CLIENT (Onion Proxy)
   IP: 192.168.1.5 (Hidden)
   |
   | [Payload Encrypted 3x: E_K1( E_K2( E_K3( DATA ) ) ) ]
   V
+---------------------+
|    GUARD NODE       | <--- Knows: Client IP, Middle IP
|    (Entry Relay)    |      Does NOT know: Exit IP, Destination, Payload
|    IP: 82.x.x.x     |
+---------------------+
   |
   | Peels Layer 1 (K1)
   | [Payload Encrypted 2x: E_K2( E_K3( DATA ) ) ]
   V
+---------------------+
|    MIDDLE NODE      | <--- Knows: Guard IP, Exit IP
|    (Relay)          |      Does NOT know: Client IP, Destination, Payload
|    IP: 45.x.x.x     |
+---------------------+
   |
   | Peels Layer 2 (K2)
   | [Payload Encrypted 1x: E_K3( DATA ) ]
   V
+---------------------+
|    EXIT NODE        | <--- Knows: Middle IP, Destination IP, Plaintext Payload*
|    (Gateway)        |      Does NOT know: Client IP, Guard IP
|    IP: 104.x.x.x    |      *Unless payload is HTTPS/TLS encrypted end-to-end.
+---------------------+
   |
   | Peels Layer 3 (K3) -> Plaintext TCP Traffic exits the Tor Network
   | [Unencrypted HTTP GET or HTTPS Encrypted Traffic]
   V
+---------------------+
|  DESTINATION SERVER | <--- Knows: Exit Node IP, Payload
|  (Clearnet Server)  |      Does NOT know: Client IP, Tor Circuit Path
|  IP: 93.184.216.34  |
+---------------------+
```

## Tor Cell Structure and Byte-Level Analysis

Tor multiplexes multiple TCP streams (e.g., multiple browser tabs) over a single cryptographic circuit. Data is broken down into fixed-size 514-byte blocks called **Cells**. This fixed size prevents traffic analysis based on packet length.

### Fixed-Length Cells
*   **Header (3 bytes):** Contains a Circuit ID (CircID) (2 bytes) and a Command (1 byte).
*   **Payload (509 bytes):** The encrypted data payload.

### Common Cell Commands
*   `CREATE2` / `CREATED2`: Used for establishing the initial handshake.
*   `EXTEND2` / `EXTENDED2`: Used to tell a node to extend the circuit to the next node.
*   `RELAY`: Used to send end-to-end encrypted data through the circuit.
*   `DESTROY`: Tears down the circuit.

When a cell is a `RELAY` cell, it contains an additional internal header that includes a StreamID, allowing the Exit node to route the payload to the correct TCP socket.

## Tor Client Bootstrap Log Analysis

Analyzing the bootstrapping process is essential for understanding how the OP connects to the network. Below is a sample log from a Tor client initializing:

```log
Nov 10 14:00:00.000 [notice] Tor 0.4.7.13 running on Linux with Libevent 2.1.12-stable...
Nov 10 14:00:00.000 [notice] Read configuration file "/etc/tor/torrc".
Nov 10 14:00:00.000 [notice] Opening Socks listener on 127.0.0.1:9050
Nov 10 14:00:00.000 [notice] Bootstrapped 0% (starting): Starting
Nov 10 14:00:01.000 [notice] Starting with guard context "default"
Nov 10 14:00:01.000 [notice] Bootstrapped 5% (conn): Connecting to a relay
Nov 10 14:00:01.000 [notice] Bootstrapped 10% (conn_done): Connected to a relay
Nov 10 14:00:01.000 [notice] Bootstrapped 14% (handshake): Handshaking with a relay
Nov 10 14:00:02.000 [notice] Bootstrapped 15% (handshake_done): Handshake with a relay done
Nov 10 14:00:02.000 [notice] Bootstrapped 75% (enough_dirinfo): Loaded enough directory info to build circuits
Nov 10 14:00:02.000 [notice] Bootstrapped 90% (ap_handshake_done): Handshake finished with a relay to build circuits
Nov 10 14:00:02.000 [notice] Bootstrapped 95% (circuit_create): Establishing a Tor circuit
Nov 10 14:00:03.000 [notice] Bootstrapped 100% (done): Done
```
*Note: The OP contacts a DirAuth, downloads the consensus, selects its Guard, negotiates TLS, and establishes the primary circuit.*

## Detailed Cryptographic Flow

The Diffie-Hellman handshake executed during circuit extension uses **ntor**, an advanced cryptographic handshake protocol designed to be secure against active adversaries. 

1.  The client generates an ephemeral x25519 keypair.
2.  It sends its public key to the router in an `EXTEND2` cell, alongside the router's identity fingerprint.
3.  The router generates its own ephemeral x25519 keypair, derives the shared secret using the client's public key and its own private keys (both ephemeral and long-term), and replies with a `CREATED2` cell.
4.  The client performs the inverse derivation.
5.  Both sides run the shared secret through HKDF (HMAC-based Key Derivation Function) to derive the symmetric encryption and authentication keys (usually AES-128 or AES-256 in CTR mode, with SHA-256 MACs).

## Real-World Attack Scenario

### Scenario: End-to-End Traffic Correlation Attack (Global Passive Adversary)

**Context:** The Tor network is explicitly designed to defeat local passive adversaries (e.g., your ISP) and local active adversaries (e.g., a malicious relay). However, it is fundamentally vulnerable to a Global Passive Adversary (GPA)—an entity that can observe both ends of the communication simultaneously.

1.  **The Setup:** A state-sponsored intelligence agency (acting as a GPA) suspects a target within their country is communicating with a specific dissident server hosted in another country.
2.  **Observation Point A (Client Side):** The agency taps the fiber optic line of the target's ISP. They observe encrypted Tor traffic flowing from the target's IP address to a known Tor Guard node.
3.  **Observation Point B (Server Side):** The agency also taps the upstream provider of the destination server. They observe Tor Exit nodes connecting to the destination server.
4.  **Traffic Correlation:** The agency records the exact timestamp, volume, and timing patterns of the packets leaving the client (Point A). Although the payload is encrypted and routed through three nodes, the *pattern* of data bursts (timing and volume) remains relatively constant.
5.  **Deanonymization:** By running statistical correlation algorithms (like Pearson correlation) against the traffic entering the Tor network at Point A and exiting the network at Point B, the agency matches the unique traffic signatures.
6.  **Result:** The agency definitively proves that Client IP $X$ is communicating with Server IP $Y$, entirely bypassing the cryptographic protections of the Tor circuit.

## Limitations and Mitigations

To mitigate traffic correlation, advanced implementations (often experimental) introduce artificial delays or dummy packets (padding) to obfuscate timing signatures. However, Tor explicitly rejects high-latency mixing (like Mixnets) because it would make interactive protocols like web browsing unacceptably slow. Tor sacrifices some anonymity against global adversaries to maintain low-latency usability.

### Website Fingerprinting
Even if an adversary cannot observe the destination, they can perform **Website Fingerprinting**. By loading thousands of websites over Tor and recording the size and timing of the encrypted packets that return, they build a profile for each website. If they monitor a user's connection to the Guard node and see a traffic pattern matching "Wikipedia," they can deduce the user's activity without breaking encryption.

## Chaining Opportunities
*   Understanding circuit creation is mandatory before delving into how Tor routes traffic entirely internally, without an Exit node, as detailed in [[03 - Tor Hidden Services v3 Cryptography]].
*   The selection criteria and risks associated with each specific hop in the circuit are expanded upon in [[04 - Tor Relays Guard Middle and Exit Nodes]].

## Related Notes
*   [[01 - Clearnet vs Deep Web vs Dark Web]]
*   [[03 - Tor Hidden Services v3 Cryptography]]
*   [[04 - Tor Relays Guard Middle and Exit Nodes]]
*   [[05 - I2P Invisible Internet Project Architecture]]
