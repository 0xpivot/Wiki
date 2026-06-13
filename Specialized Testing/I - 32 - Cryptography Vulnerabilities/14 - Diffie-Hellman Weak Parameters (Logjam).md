---
tags: [cryptography, tls, diffie-hellman, logjam, advanced]
difficulty: advanced
module: "32 - Cryptography Vulnerabilities"
topic: "32.14 Diffie-Hellman Weak Parameters (Logjam)"
---

# Diffie-Hellman Weak Parameters (Logjam)

## Introduction

The Logjam attack, identified by CVE-2015-4000, is a devastating cryptographic flaw that affects the Diffie-Hellman (DH) key exchange protocol as it was widely implemented in TLS, IPsec, and SSH. Published by a team of security researchers in 2015, the vulnerability arises from a combination of deliberate historical cryptography weakening (US export controls from the 1990s) and a fundamental misunderstanding of the computational effort required to solve the Discrete Logarithm Problem (DLP) for specific, widely shared prime numbers. 

Logjam allows a Man-in-the-Middle (MitM) attacker to downgrade a seemingly secure TLS connection to use 512-bit "export-grade" cryptography. Once downgraded, the attacker can solve the mathematics underlying the 512-bit key exchange in near real-time, compute the master secret, and subsequently decrypt and manipulate the entire secure session.

## Mathematical Foundation: Diffie-Hellman

The Diffie-Hellman Key Exchange allows two parties (Client and Server) to establish a shared secret over an insecure channel. It relies on the computational difficulty of the Discrete Logarithm Problem.

1. Both parties agree on a large prime number `p` and a generator `g`.
2. The Client picks a secret random number `a` and computes `A = g^a mod p`.
3. The Server picks a secret random number `b` and computes `B = g^b mod p`.
4. They exchange `A` and `B` over the public network.
5. The Client computes the shared secret `S = B^a mod p`.
6. The Server computes the shared secret `S = A^b mod p`.
7. Due to modular arithmetic, `B^a mod p` is equal to `A^b mod p`. Both parties now share the secret `S`.

An eavesdropper sees `p`, `g`, `A`, and `B`. To find the secret `S`, the eavesdropper must determine the secret `a` or `b`. Computing `a` given `A`, `g`, and `p` is the Discrete Logarithm Problem: `a = log_g(A) mod p`. For sufficiently large primes (e.g., 2048-bit), this is computationally infeasible for modern supercomputers. However, for small primes (e.g., 512-bit), it is highly achievable.

## The Flaw: Export-Grade Cryptography and Precomputation

### The Legacy of DHE_EXPORT
In the 1990s, the United States enforced export controls on strong cryptography. Software exported overseas was legally required to support weakened "export cipher suites" that limited the Diffie-Hellman prime `p` to 512 bits (`DHE_EXPORT`). While these restrictions were eventually lifted, the legacy support for these weak ciphers remained deeply embedded in TLS protocols and server configurations for decades to ensure backward compatibility.

### The Number Field Sieve (NFS) and the Precomputation Trap
The algorithm used to break Diffie-Hellman is the General Number Field Sieve (GNFS). The GNFS process consists of several steps. The most critical aspect is that the most computationally intensive phase depends *only on the prime `p`*, not on the individual keys (`A` or `B`) generated for a specific connection.

This creates a massive vulnerability known as the **precomputation trap**:
1. An attacker spends a massive amount of computational power (e.g., a week on a supercomputing cluster) to precompute the data for a specific 512-bit prime `p`.
2. Once this precomputation is done, breaking *any* specific key exchange that uses that exact same prime `p` takes only a fraction of a second.

The researchers who published Logjam discovered that an overwhelming majority of internet servers (up to 8% of the Top 1 Million domains) were using the *exact same hardcoded 512-bit prime* (typically the default prime packaged with Apache or OpenSSL). By precomputing the data for this one prime, the researchers could break the connections of millions of servers instantly.

### The Threat of State-Level Adversaries (1024-bit Primes)
The Logjam paper further hypothesized that state-level actors (like intelligence agencies) possess the resources to perform the precomputation phase for **1024-bit primes**. Because many servers also shared default 1024-bit primes (such as the Oakley Group 2), precomputing just one or two common 1024-bit primes could allow an adversary to passively decrypt a massive percentage of global VPN (IPsec), SSH, and HTTPS traffic without executing an active downgrade attack.

## The Downgrade Attack Execution

For the attack to work against modern clients, the MitM attacker must trick the server and client into agreeing on the weak `DHE_EXPORT` cipher suite.

1. **ClientHello interception**: The client sends a standard ClientHello offering strong cipher suites (e.g., `TLS_DHE_RSA_WITH_AES_128_CBC_SHA`).
2. **Attacker Modification**: The MitM attacker intercepts the ClientHello and alters it, forcing it to offer *only* the weak export cipher (e.g., `TLS_DHE_RSA_EXPORT_WITH_DES40_CBC_SHA`).
3. **Server Response**: The server, supporting legacy clients, agrees to the export cipher suite and sends a ServerHello along with its signed 512-bit Diffie-Hellman parameters (the weak prime `p`).
4. **Attacker Forwarding**: The attacker forwards the ServerHello to the client. *Crucially, in TLS versions prior to 1.3, the server's signature does not cover the cipher suite chosen, only the DH parameters*. Thus, the client does not realize the server intentionally chose a weak cipher; the client thinks the server simply only supports 512-bit DH.
5. **Real-time Cracking**: The attacker receives the client's public key `A` and the server's public key `B`. Using the precomputed tables for the 512-bit prime `p`, the attacker solves the discrete logarithm in real-time to find the secret `a` or `b`.
6. **Master Secret Derivation**: The attacker calculates the shared Master Secret.
7. **Session Hijacking**: When the client sends its "Finished" message, the attacker decrypts it, modifies the handshake hashes to hide the downgrade, re-encrypts it, and forwards it to the server. The TLS connection is now completely compromised.

### ASCII Diagram of the Logjam Downgrade Attack

```text
+----------------+                +-----------------+                +----------------+
|     Client     |                | Attacker (MitM) |                |     Server     |
+-------+--------+                +--------+--------+                +-------+--------+
        |                                  |                                 |
        | 1. ClientHello (Strong DHE)      |                                 |
        |--------------------------------->| 2. ClientHello modified         |
        |                                  |    (Forces DHE_EXPORT)          |
        |                                  |-------------------------------->|
        |                                  |                                 |
        |                                  | 3. ServerHello (DHE_EXPORT)     |
        |                                  |    Server sends 512-bit prime   |
        |                                  |<--------------------------------|
        | 4. ServerHello forwarded         |                                 |
        |<---------------------------------|                                 |
        |                                  | 5. Attacker computes Discrete   |
        |                                  |    Logarithm of 512-bit key in  |
        |                                  |    real-time (NFS precomputed)  |
        |                                  |                                 |
        | 6. Client Computes Master Secret |                                 |
        |    using 512-bit DH key          |                                 |
        |                                  | 7. Attacker derives Master Sec. |
        |                                  |                                 |
        | 8. Client Finished (Encrypted)   |                                 |
        |--------------------------------->| 9. Attacker decrypts, modifies, |
        |                                  |    and re-encrypts hashes       |
        |                                  |-------------------------------->|
        |                                  |                                 |
+-------+--------+                +--------+--------+                +-------+--------+
```

## Mitigation and Remediation

Defending against Logjam requires eliminating support for weak cryptography and ensuring unique, sufficiently large prime groups.

1. **Disable Export Cipher Suites**: Servers must be configured to completely disable all `EXPORT` cipher suites. This prevents the MitM from downgrading the connection in the first place.
2. **Increase Minimum DH Size**: Servers and clients must enforce a minimum DH prime size of 2048 bits. Modern browsers implement hard limits, refusing to connect if the server provides a DH prime smaller than 1024 or 2048 bits.
3. **Generate Unique DH Groups**: Administrators must never use the default DH parameters shipped with their server software. Unique groups must be generated.
   *Example using OpenSSL:*
   ```bash
   # Generate a unique 2048-bit prime group
   openssl dhparam -out dhparams.pem 2048
   ```
   This file is then referenced in the server's TLS configuration (e.g., `ssl_dhparam /etc/nginx/dhparams.pem;` in Nginx).
4. **Transition to Elliptic Curve Diffie-Hellman (ECDHE)**: The ultimate defense is moving away from finite-field Diffie-Hellman (DHE) entirely and adopting Elliptic Curve cryptography (ECDHE). Elliptic curves do not suffer from the same precomputation vulnerabilities associated with the Number Field Sieve. ECDHE is faster, more secure, and is the standard for modern TLS (including mandatory usage in TLS 1.3).

## Chaining Opportunities
Logjam is fundamentally an enabler. By breaking the encryption layer, the attacker exposes the plaintext HTTP traffic, opening the door for:
- **Credential Harvesting**: Sniffing plaintext passwords, API keys, and authorization tokens.
- **Payload Injection**: Modifying server responses to inject malicious JavaScript, malware, or exploit kits directly into the victim's browser session.
- **Complete Session Takeover**: Capturing session cookies to impersonate the victim long after the initial MitM attack has concluded.

## Related Notes
- [[13 - CRIME Attack (compression of cookies over TLS)]] - Another protocol-level attack on TLS.
- [[15 - Defense - Strong Algorithms, Key Management, TLS Best Practices]] - How to configure TLS to avoid these downgrade attacks.
- [[05 - MitM and Downgrade Attacks]] - General overview of downgrade strategies.
- [[12 - POODLE Attack]] - A downgrade attack targeting SSLv3 fallback.
