---
tags: [cryptography, defense, mitigation, key-management, advanced]
difficulty: advanced
module: "32 - Cryptography Vulnerabilities"
topic: "32.15 Defense - Strong Algorithms, Key Management, TLS Best Practices"
---

# Defense: Strong Algorithms, Key Management, TLS Best Practices

## Introduction

Securing digital infrastructure against modern cryptographic attacks requires a holistic, defense-in-depth approach that spans across algorithm selection, robust key management lifecycles, and strict adherence to protocol-level best practices. As attacks like CRIME, BEAST, POODLE, and Logjam have demonstrated, relying on encryption alone is insufficient if the underlying protocols, parameters, or implementations contain structural weaknesses. Cryptography is uniquely unforgiving; a single conceptual flaw, a poorly configured cipher suite, or a mishandled private key can cascade into total system compromise, nullifying all other security controls in the process.

This document details the essential pillars of cryptographic defense: selecting modern, resilient algorithms; establishing secure key lifecycles; and locking down transport layer security (TLS) configurations.

## 1. Strong Algorithm Selection

Choosing the right cryptographic primitives is the foundation of any secure system. Algorithms that were considered highly secure a decade ago may now be vulnerable to rapid brute-forcing, precomputation attacks, or sophisticated mathematical breakthroughs.

### Symmetric Encryption (Data Confidentiality)
Symmetric algorithms use the same key for encryption and decryption.
- **Recommended**: **AES-256-GCM** and **ChaCha20-Poly1305**. 
  - **Why?** Both of these are Authenticated Encryption with Associated Data (AEAD) ciphers. They simultaneously guarantee both confidentiality (encryption) and integrity (authentication). This prevents devastating tampering attacks like Padding Oracles, which target non-authenticated cipher modes like AES-CBC. ChaCha20 is particularly useful on mobile or IoT devices lacking dedicated AES hardware acceleration.
- **Deprecated/Dangerous**: DES, 3DES, RC4, AES-CBC, AES-ECB.

### Asymmetric Encryption (Key Exchange & Signatures)
Asymmetric algorithms use a public key for encryption/verification and a private key for decryption/signing.
- **Recommended for Key Exchange**: **ECDHE** (Elliptic Curve Diffie-Hellman Ephemeral).
  - **Why?** Elliptic Curve cryptography requires significantly smaller key sizes for the same level of security compared to RSA or traditional Diffie-Hellman (e.g., a 256-bit ECC key is roughly equivalent to a 3072-bit RSA key). The 'Ephemeral' (E) aspect guarantees Perfect Forward Secrecy (PFS), meaning if the server's long-term private key is compromised in the future, past recorded traffic cannot be decrypted. Curves like `Curve25519` are highly recommended over legacy NIST curves due to concerns regarding potential backdoors and ease of secure implementation.
- **Recommended for Signatures**: **RSA-3072** (or higher), **Ed25519**, **ECDSA**.
- **Deprecated/Dangerous**: RSA < 2048-bit, static Diffie-Hellman, static RSA key exchange.

### Cryptographic Hashing
Hashing functions create fixed-size fingerprints of data, used for integrity verification and password storage.
- **Recommended for Data Integrity**: **SHA-256**, **SHA-384**, **SHA-3** family.
- **Recommended for Password Storage**: **Argon2id**, **bcrypt**, **PBKDF2** (with high iteration counts). These algorithms are intentionally slow and require high memory, neutralizing the speed advantage of attacker hardware (GPUs/ASICs) during brute-force attempts.
- **Deprecated/Dangerous**: MD5, SHA-1 (both vulnerable to collision attacks).

## 2. Secure Key Management Lifecycle

Even the strongest algorithms are useless if the underlying cryptographic keys are mishandled. A formal Key Management Lifecycle must govern how keys are handled from birth to death.

### Phases of Key Management
1. **Generation**: Keys must be generated using strong, cryptographically secure pseudorandom number generators (CSPRNG), such as `/dev/urandom` on Linux systems. Never use standard programming functions like `Math.random()`.
2. **Storage**: Keys must never be hardcoded into application source code or stored in plaintext in databases.
   - Use centralized Key Management Services (KMS) like AWS KMS, Azure Key Vault, or HashiCorp Vault.
   - For maximum security, utilize Hardware Security Modules (HSMs) which process cryptographic operations internally, meaning the raw private key never leaves the physical hardware boundary.
3. **Distribution**: Keys must be transmitted to endpoints securely, usually wrapped (encrypted) by another transport key, avoiding transmission in the clear.
4. **Rotation**: Keys must have a defined cryptoperiod. Regular key rotation limits the blast radius if a key is compromised. If a key is stolen, it is only useful for the duration of its active lifespan.
5. **Revocation & Destruction**: When a key expires or is compromised, it must be formally revoked (e.g., via Certificate Revocation Lists (CRL) or OCSP). Upon retirement, the key material must be securely destroyed (crypto-shredding) to prevent forensic recovery.

## 3. TLS Best Practices and Configurations

Securing data in transit requires locking down the TLS protocol to eliminate downgrade attacks and side-channel vulnerabilities.

### Protocol Versions
- **Mandatory**: **TLS 1.2** and **TLS 1.3**.
- **Why?** TLS 1.3 represents a massive overhaul. It removes support for weak legacy ciphers (RC4, DES, CBC modes), enforces Perfect Forward Secrecy by completely removing static RSA key exchanges, reduces the handshake process to a single round trip (1-RTT) for performance, and encrypts more of the handshake itself (including the server certificate).
- **Deprecated**: SSLv2, SSLv3, TLS 1.0, TLS 1.1. These must be explicitly disabled on web servers, load balancers, and API gateways.

### Server Configuration Directives
Web servers (Nginx, Apache) must be explicitly configured to enforce strong cryptography:
- **Cipher Suites Priority**: Ensure the server enforces its own preferred cipher suite order, prioritizing strong AEAD ciphers over older ones.
  ```nginx
  # Nginx Example
  ssl_prefer_server_ciphers on;
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
  ```
- **HSTS (HTTP Strict Transport Security)**: A security header that forces browsers to only interact with the application over HTTPS, preventing MitM attacks like SSL Stripping.
  ```http
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  ```
- **Disable Compression**: Explicitly disable TLS compression to completely neutralize the CRIME attack.
- **Secure Renegotiation**: Ensure secure renegotiation is patched, or disable client-initiated renegotiation to prevent Denial of Service (DoS) attacks where clients force the server to perform expensive asymmetric crypto calculations repeatedly.

### ASCII Diagram of Secure Architecture

```text
+---------------------------------------------------------------------------------+
|                       SECURE CRYPTOGRAPHIC ARCHITECTURE                         |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  +--------------------+       +--------------------+       +-----------------+  |
|  |   Application      |       |  Key Management    |       |   Storage/DB    |  |
|  |   Logic Layer      |<----->|  Service (KMS)     |<----->|   Data at Rest  |  |
|  +---------+----------+       +---------+----------+       +-----------------+  |
|            |                            |                                       |
|            v                            v                                       |
|  +--------------------+       +--------------------+                            |
|  |  TLS 1.3 Endpoint  |       | Hardware Security  |                            |
|  |  (Nginx/HAProxy)   |       | Module (HSM)       |                            |
|  +---------+----------+       +--------------------+                            |
|            |                                                                    |
|            | (Perfect Forward Secrecy, AEAD Ciphers, HSTS Enforced)             |
|            v                                                                    |
|  +--------------------+                                                         |
|  |   Public Internet  |                                                         |
|  +--------------------+                                                         |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

## Advanced Operational Security

Beyond configuration, maintaining a strong cryptographic posture requires operational vigilance.
- **Certificate Transparency (CT)**: An open framework where all issued SSL certificates are logged publicly. Administrators should monitor CT logs for their domains to detect rogue or misissued certificates.
- **Automated Issuance**: Utilizing protocols like ACME (used by Let's Encrypt) to automate short-lived certificate renewals. Short-lived certificates (e.g., 90 days) fundamentally limit the window of opportunity for stolen keys and reduce reliance on fragile revocation mechanisms like CRLs.

## Chaining Opportunities
Failure to implement these defenses directly leads to:
- **Session Hijacking**: Via downgraded or broken ciphers.
- **Data Breaches**: Through compromised static keys that decrypt years of captured historical traffic.
- **Authentication Bypasses**: Weak hashing algorithms allowing rapid offline cracking of password databases.

## Related Notes
- [[13 - CRIME Attack (compression of cookies over TLS)]] - Why TLS compression must be disabled.
- [[14 - Diffie-Hellman Weak Parameters (Logjam)]] - Why strong key exchange and minimum bit lengths matter.
- [[11 - Padding Oracle Attacks]] - Why AEAD ciphers are required over CBC modes.
- [[12 - POODLE Attack]] - Why legacy protocols like SSLv3 must be eradicated.
- [[05 - MitM and Downgrade Attacks]] - General theory on how protocols are forced into insecure states.
