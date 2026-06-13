---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.04 Cryptography for Custom C2 AES RSA and Key Exchange"
---

# 98.04 Cryptography for Custom C2 AES RSA and Key Exchange

## Introduction

In modern Command and Control (C2) operations, sending plain text commands and receiving unencrypted output is a guaranteed method for immediate detection and compromise of the operation. Network Intrusion Detection Systems (NIDS) and Deep Packet Inspection (DPI) appliances will immediately flag anomalous strings (like `cmd.exe` or `whoami`), and incident responders can trivially reconstruct the entire attack narrative.

Therefore, robust cryptography is a foundational requirement for any custom C2 framework. This doesn't merely mean wrapping traffic in TLS (HTTPS), as corporate environments frequently utilize SSL/TLS Inspection (Man-in-the-Middle) to decrypt and analyze web traffic. A bespoke C2 must implement its own layer of end-to-end encryption to ensure confidentiality, integrity, and authenticity, completely independent of the transport layer. This ensures that even if defenders decrypt the outer TLS wrapper, the inner payload remains opaque.

## ASCII Diagram: End-to-End Encrypted Channel

```text
+-------------------------------------------------------------------------------------------------+
|                              C2 CRYPTOGRAPHIC ARCHITECTURE                                      |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   [ IMPLANT / AGENT ]                                                [ TEAM SERVER ]            |
|                                                                                                 |
|   1. Generate Session Key (AES-256)                                                             |
|      [ AES Key ]                                                                                |
|                                                                                                 |
|   2. Encrypt AES Key with Server's Public RSA Key                                               |
|      Encrypted_Key = RSA_Encrypt(Pub_Key, AES Key)                                              |
|                                                                                                 |
|   3. Send Initial Check-in Payload over Transport (HTTP/DNS)                                    |
|      -------------------- [ Encrypted_Key ] ----------------------->                            |
|                                                                      4. Decrypt with Private Key|
|                                                                         AES Key = RSA_Decrypt(  |
|                                                                                     Priv_Key,   |
|                                                                                     Encrypted_Key)|
|   5. Establish Symmetrical Encrypted Channel                                                    |
|                                                                                                 |
|      Command Request:                                                                           |
|      <-- [ AES_GCM_Encrypt(AES Key, "Task Request") ] --------------                            |
|                                                                                                 |
|                                                                      6. Process Task Request    |
|                                                                                                 |
|      Command Response:                                                                          |
|      --- [ AES_GCM_Encrypt(AES Key, "Execute: whoami") ] ---------->                            |
|                                                                                                 |
|   7. Decrypt, Execute, Return Results:                                                          |
|      <-- [ AES_GCM_Encrypt(AES Key, "Result: nt authority\system")]-                            |
|                                                                                                 |
|=================================================================================================|
|   NOTE: This entire exchange occurs INSIDE the standard TLS/HTTPS tunnel, rendering             |
|         corporate SSL Inspection useless against the actual payload content.                    |
+-------------------------------------------------------------------------------------------------+
```

## 1. Symmetric Encryption: The Workhorse

Symmetric encryption uses the same key for both encryption and decryption. It is incredibly fast and efficient, making it ideal for encrypting large volumes of data (like exfiltrated files or continuous command streams).

### 1.1 AES (Advanced Encryption Standard)
In a custom C2, AES-256 is the standard choice. However, the mode of operation is critical.
- **CBC (Cipher Block Chaining)**: Often used, but requires padding and is susceptible to padding oracle attacks if not implemented with a strong MAC (Message Authentication Code).
- **GCM (Galois/Counter Mode)**: The preferred mode for modern C2s. AES-GCM is an Authenticated Encryption with Associated Data (AEAD) cipher. It simultaneously provides confidentiality and data origin authenticity. If a network appliance or defender alters a single bit of the encrypted payload, the decryption process will fail, alerting the C2 that the payload was tampered with.

### 1.2 The Hardcoded Key Problem
A common, fatal mistake in amateur malware development is hardcoding the symmetric AES key directly into the agent's binary.
- **The Risk**: When incident responders recover the executable from disk or memory, reverse engineers can simply extract the key (e.g., using strings analysis or disassembling the binary) and subsequently decrypt all captured network traffic related to that operation, exposing the entire attack chain.

## 2. Asymmetric Encryption & Key Exchange

To solve the hardcoded key problem, custom C2s utilize asymmetric encryption (public/private key pairs) to facilitate a secure key exchange over an insecure channel.

### 2.1 RSA or Elliptic Curve (ECC)
The Team Server generates a key pair. The private key remains securely on the server; it never leaves. The public key is hardcoded into the agent.

### 2.2 The Key Exchange Flow
1. The agent generates a random, cryptographically secure symmetric key (e.g., a 32-byte AES-256 key) in memory at runtime.
2. The agent encrypts this session key using the server's hardcoded public key.
3. The agent sends the encrypted session key to the server during its first check-in (the initialization phase).
4. The server uses its private key to decrypt the payload and retrieve the session key.
5. Both sides now share the same symmetric key without it ever being transmitted in plaintext.

If a defender recovers the agent, they only find the public key. The public key cannot be used to decrypt the network traffic; it can only encrypt data. Without the server's private key, historical traffic analysis is impossible.

### 2.3 Forward Secrecy
For elite operations, even this is not enough. If the Team Server is ever seized or compromised by defenders, the private key is exposed, allowing all past traffic (if captured and stored in PCAPs) to be decrypted.
- **Implementation**: Advanced C2s implement Ephemeral Diffie-Hellman (ECDHE) key exchanges. A new session key is negotiated for every interaction (or periodically). Even if the long-term keys are compromised, past session keys remain secure because they were discarded.

## 3. Data Integrity and Authentication

Encryption hides the data, but it doesn't prove who sent it.

### 3.1 HMAC (Hash-based Message Authentication Code)
If AES-CBC is used instead of GCM, an HMAC (e.g., HMAC-SHA256) MUST be appended to every packet. The server calculates the HMAC of the received payload and compares it to the transmitted HMAC. If they differ, the packet is dropped. This prevents replay attacks and packet manipulation by active network defenders or IPS appliances.

### 3.2 Implantation Authentication
How does the server know it's talking to a legitimate agent and not a blue teamer probing the infrastructure?
- Agents often generate a unique UUID based on hardware hashes (MAC address, CPU ID, Volume Serial Number). This UUID is encrypted and sent with check-ins, allowing the server to authenticate the specific endpoint and ensure rogue researchers aren't flooding the task queue.

## Real-World Attack Scenario

### Scenario: Bypassing Advanced SSL Inspection

**Context**: A Red Team is engaged against a mature financial institution. The target uses highly restrictive Palo Alto firewalls configured with SSL Decryption. All outbound HTTPS traffic is decrypted, analyzed by the IPS engine for malicious patterns, re-encrypted, and sent to the internet.

**The Attack**:
1. The Red Team deploys their custom C2 agent. The agent uses HTTP/HTTPS for transport.
2. The agent generates data: `Execute Command: net user administrator /domain`
3. If they relied only on HTTPS, the Palo Alto firewall would decrypt the TLS tunnel, see the plaintext command, flag it as suspicious enumeration, and block the connection.
4. **The Custom Crypto Layer**: Before handing the payload to the HTTPS transport layer, the agent encrypts the string using AES-256-GCM with a dynamically negotiated session key. The payload becomes unreadable bytes: `0x7a8b9c...`
5. The agent encodes this encrypted blob and places it into the body of an HTTPS POST request, disguised within a JSON structure that looks like legitimate application telemetry or analytics data.
6. **The Result**: The Palo Alto firewall decrypts the TLS tunnel. It inspects the JSON payload. It sees what appears to be random alphanumeric data within a legitimate-looking JSON field. Lacking signatures for this specific bespoke encryption format, and unable to read the underlying command, the firewall passes the traffic, allowing the C2 channel to operate undetected through the inspection layer.

## Detection Engineering & Threat Hunting

Cryptography is designed to defeat analysis, but the implementation often leaves traces that defenders can hunt for.

1. **Entropy Analysis**: Encrypted data is indistinguishable from highly random data. NTA tools monitor for high-entropy payloads leaving the network. While TLS is high-entropy, the data *inside* the TLS tunnel (visible via SSL inspection) should be structured (like HTML or JSON). Finding high-entropy blobs inside HTTP POST bodies during SSL inspection is a massive indicator of custom encryption.
2. **Memory Forensics**: The ultimate weakness of cryptography in C2 is that the keys must exist in plaintext in the agent's memory to perform the encryption/decryption routines. Defenders taking memory dumps of suspected infected machines can use tools like Volatility or specific YARA rules to scan for cryptographic constants, AES S-boxes, or key schedules in memory.
3. **Cryptographic API Hooking**: EDRs often hook OS-level cryptographic APIs (e.g., Windows BCrypt / Cryptography API: Next Generation). If an unknown process suddenly requests the generation of AES keys and performs bulk encryption operations before initiating network connections, the EDR may flag this behavior. Custom C2 developers bypass this by statically compiling open-source crypto libraries (like mbedTLS or libsodium) directly into their agent, avoiding the OS APIs entirely.

## Chaining Opportunities

- **Steganography**: Cryptography obscures meaning; steganography obscures existence. Chaining custom encryption with steganography (e.g., hiding the AES-encrypted blob within the least significant bits of an image file) adds an additional layer of evasion against DPI (see [[XX - Steganography in C2 Channels]]).
- **Domain Generation Algorithms (DGA)**: Combining encrypted payloads with DGAs ensures that even if a defender identifies the traffic, they cannot simply block a single static IP or Domain, as the agent will continuously calculate new infrastructure points to contact (see [[XX - Implementing DGAs and Fast Flux]]).

## Related Notes

- [[98.02 Core Components Server Agent and Protocol]]
- [[98.05 Developing the Team Server Python Flask FastAPI]]
- [[XX - Memory Forensics and Key Extraction]]
- [[XX - Evading Network Intrusion Detection Systems]]
