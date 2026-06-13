---
tags: [darkweb, tor, infrastructure, vapt]
difficulty: beginner
module: "83 - Dark Web Infrastructure and Tor Internals"
topic: "83.03 Tor Hidden Services v3 Cryptography"
---

# Tor Hidden Services v3 Cryptography

## Introduction to Onion Services

While Tor is primarily known as a proxy network to access the Clearnet anonymously (via Exit nodes), its most secure and defining feature is its ability to host services *inside* the network. These are known as **Onion Services** (formerly Hidden Services). 

When a client connects to an Onion Service, the traffic never leaves the Tor network. There is no Exit node involved. Instead, both the client and the server build independent Tor circuits that meet in the middle, ensuring end-to-end encryption, bidirectional anonymity, and complete obfuscation of both the client's and the server's physical IP addresses.

## The Transition from v2 to v3

In 2021, the Tor Project officially deprecated Hidden Services v2 in favor of v3. The transition was necessary due to critical cryptographic weaknesses in the v2 protocol.

### Key Upgrades in v3
1.  **Cryptography:** v2 relied on RSA-1024 and SHA-1, which are vulnerable to modern cryptanalysis and compute power. v3 upgraded to **Ed25519** for elliptic curve cryptography and **SHA-3** for hashing.
2.  **Address Length:** v2 addresses were 16 characters long, derived from a truncated hash of the RSA public key. v3 addresses are 56 characters long, encompassing the entire Ed25519 public key, a checksum, and a version byte.
    *   *v2 Example:* `exp10re.onion`
    *   *v3 Example:* `vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd.onion`
3.  **Directory Anonymity:** v3 implemented "Hidden Service Directory (HSDir) blinding." In v2, malicious HSDir nodes could harvest `.onion` addresses. In v3, the addresses are shielded via blinded keys that rotate daily, preventing directory enumeration.
4.  **Improved Client Authorization:** v3 uses x25519 for secure, scalable client authorization.

## The 6-Step Rendezvous Protocol

Connecting to an Onion Service is a complex cryptographic dance. It requires six distinct steps to ensure that neither party discovers the other's identity.

### 1. Setup (Server Side)
The server operating the Onion Service creates several Tor circuits and picks random relays to act as **Introduction Points (IPs)**. It provides these IPs with its public key.

### 2. Publication (Server Side)
The server constructs a **Hidden Service Descriptor**. This descriptor contains the list of chosen Introduction Points and their authentication keys. The server signs this descriptor with its Ed25519 private key and uploads it to a distributed hash table hosted on specialized Tor relays called **Hidden Service Directories (HSDirs)**.

### 3. Fetching (Client Side)
The client receives the `.onion` address out-of-band (e.g., from a forum). The `.onion` address *is* the public key. The client queries an HSDir using the `.onion` address to download the Hidden Service Descriptor. The client verifies the signature on the descriptor using the public key embedded in the `.onion` address.

### 4. Rendezvous Point Selection (Client Side)
The client selects a random relay to act as the **Rendezvous Point (RP)**. The client builds a circuit to the RP and gives it a one-time cryptographic secret (the Rendezvous Cookie).

### 5. Introduction (Client Side to Server)
The client builds a circuit to one of the Introduction Points listed in the fetched descriptor. The client sends an `INTRODUCE1` cell containing:
*   The address of the chosen Rendezvous Point.
*   The Rendezvous Cookie.
*   The first half of a Diffie-Hellman handshake.
This payload is encrypted with the Onion Service's public key, so the Introduction Point cannot read it. The IP passes this to the server.

### 6. Rendezvous and Connection (Server to Client)
The server decrypts the introduction message. It builds a circuit to the specified Rendezvous Point and sends the Rendezvous Cookie along with the second half of the Diffie-Hellman handshake. 
The Rendezvous Point pairs the client and server based on the matching cookie. They establish an end-to-end encrypted connection. At no point does the RP know the identity of the client or the server.

## ASCII Architecture Diagram: Rendezvous Protocol

```text
========================================================================================
                      ONION SERVICE v3 RENDEZVOUS ARCHITECTURE
========================================================================================

                                  [ HIDDEN SERVICE DIRECTORY (HSDir) ]
                                   (Stores Signed Service Descriptor)
                                     ^                     ^
                 (3. Fetch Descriptor) |                     | (2. Publish Descriptor)
                                     |                     |
[ CLIENT ] --------------------------+                     +----------------------- [ SERVER ]
   |                                                                                    |
   |                                                                                    |
   | (5. Send INTRODUCE1 via Circuit)             (1. Establish Intro Points)           |
   +---------------------> [ INTRODUCTION POINT ] <-------------------------------------+
                                     |
                                     | (Forwards Intro Payload to Server)
                                     V
                           [ SERVER RECEIVES INTRO ]
                                     |
   +---------------------------------+--------------------------------------------------+
   | (4. Establish RP & Send Cookie) |                                                  |
   |                                 | (6. Connect to RP & Send Cookie + DH Part 2)     |
   V                                 V                                                  V
[ TOR CIRCUIT 1 ]            [ RENDEZVOUS POINT ]                           [ TOR CIRCUIT 2 ]
(3 Hops to RP)               (Pairs Connections)                            (3 Hops to RP)
   |                                 |                                                  |
   +=================================O==================================================+
                                     |
             [ END-TO-END ENCRYPTED BIDIRECTIONAL COMMUNICATION ESTABLISHED ]
             (Client IP hidden by Circuit 1 | Server IP hidden by Circuit 2)

```

## Technical Configuration: Hosting an Onion Service

Hosting a v3 service is remarkably simple from a configuration standpoint. It requires modifying the `torrc` file on a server already running a web server (like Nginx) on localhost.

```conf
# /etc/tor/torrc snippet for Onion Service v3

# Define the directory where Tor will store the Ed25519 private key and hostname
HiddenServiceDir /var/lib/tor/hidden_service/

# Map Tor's virtual port (80) to the local application port (8080)
# Note: The web server should ONLY listen on 127.0.0.1 to prevent Clearnet leakage.
HiddenServicePort 80 127.0.0.1:8080

# Map Port 443 if you are serving HTTPS (though generally redundant inside Tor)
HiddenServicePort 443 127.0.0.1:8443

# Optional: Enable V3 client authorization for private networks
# HiddenServiceAuthorizeClient client-name

# Limit maximum number of streams per circuit to defend against DoS
HiddenServiceMaxStreams 0

# Limit maximum number of introduction points
HiddenServiceNumIntroductionPoints 3
```
Upon restarting Tor, it automatically generates the `hostname` (the `.onion` address) and the `hs_ed25519_secret_key` in the specified directory. The `hostname` file contains the 56-character string that serves as the public locator for the service.

## Python Snippet: Decoding a v3 Address

To understand the cryptography, one must understand how a v3 address is formed. The `.onion` address is not just a random string; it is a meticulously calculated cryptographic identifier.

```python
#!/usr/bin/env python3
# Conceptual logic for Tor v3 Address Construction
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519

# 1. Generate Ed25519 Keypair
private_key = ed25519.Ed25519PrivateKey.generate()
public_key_bytes = private_key.public_key().public_bytes_raw() # 32 bytes

# 2. Define Version Byte (0x03 for v3)
version_byte = b'\x03'

# 3. Calculate Checksum
# SHA3-256(".onion checksum" || PUBKEY || VERSION)
prefix = b".onion checksum"
checksum_data = prefix + public_key_bytes + version_byte
checksum = hashlib.sha3_256(checksum_data).digest()[:2] # First 2 bytes

# 4. Construct Final Data Block
# Address Data = PUBKEY (32 bytes) + CHECKSUM (2 bytes) + VERSION (1 byte)
address_data = public_key_bytes + checksum + version_byte

# 5. Base32 Encode and append .onion
onion_address = base64.b32encode(address_data).decode('utf-8').lower() + ".onion"
print(f"Generated v3 Address: {onion_address}")
```

## Real-World Attack Scenario

### Scenario: Application-Layer Deanonymization via Server-Status Leak

**Context:** The Tor protocol provides network-layer anonymity. It guarantees that the IP packets routing the traffic cannot be traced. However, Tor cannot protect against operational security (OpSec) failures at the application layer.

1.  **The Target:** An illicit marketplace operating as a Tor v3 Onion Service. The underlying web server is an improperly configured Apache instance.
2.  **The Vulnerability:** The administrator accidentally leaves the Apache `mod_status` module enabled and accessible at `/server-status`.
3.  **The Attack:** A CTI researcher browses to `http://[marketplace-v3-address].onion/server-status`. 
4.  **The Leak:** The `server-status` page dynamically generates a status report of the Apache server. Crucially, the page outputs the server's internal hostname, internal IP configurations, and sometimes the *Clearnet IP address* if the server is dual-homed or misconfigured to bind to `0.0.0.0` instead of strictly `127.0.0.1`.
5.  **The Deanonymization:** The researcher captures the true Clearnet IP address of the server hosting the marketplace from the status page. 
6.  **The Takedown:** The researcher correlates the Clearnet IP to a specific hosting provider (e.g., OVH or a bulletproof host), bypassing the entire 6-step cryptographic Tor Rendezvous protocol purely through an application misconfiguration.

## Defense and VAPT for Onion Services

When conducting VAPT against an Onion Service (often termed a "Dark Web audit"), testers look for:
*   **Application Leaks:** Examining metadata in images, error logs, and HTTP headers (e.g., `Server:` banners exposing the OS).
*   **DNS Leaks:** Forcing the application to resolve a Clearnet URL, causing the underlying server's DNS resolver to make a public request, thereby leaking the IP.
*   **Time-Based Attacks:** Sending large payloads and measuring response times to estimate geographical location based on latency.

## Chaining Opportunities
*   Hosting an Onion Service requires a deep understanding of the network perimeter boundaries discussed in [[01 - Clearnet vs Deep Web vs Dark Web]].
*   The Introduction and Rendezvous points are simply standard Tor Relays fulfilling temporary roles. Their core functions are detailed in [[04 - Tor Relays Guard Middle and Exit Nodes]].

## Related Notes
*   [[01 - Clearnet vs Deep Web vs Dark Web]]
*   [[02 - The Onion Router Tor Architecture and Mechanics]]
*   [[04 - Tor Relays Guard Middle and Exit Nodes]]
*   [[05 - I2P Invisible Internet Project Architecture]]
