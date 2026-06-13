---
tags: [c2, red-team, infrastructure, vapt]
difficulty: intermediate
module: "94 - Command and Control Foundations and Architectures"
topic: "94.10 C2 Network Signatures and TLS Fingerprinting"
---

# C2 Network Signatures and TLS Fingerprinting

## Introduction to TLS Fingerprinting

Historically, Red Teams focused their network evasion efforts on modifying HTTP headers, changing URIs, and obfuscating payloads (Malleable C2). However, as HTTPS became ubiquitous, Blue Teams and security vendors shifted their focus to the one part of the network connection that remains unencrypted and highly structured: **The TLS Handshake**.

Before application data (HTTP) is transmitted, the client and server must negotiate encryption parameters. The specific combination of TLS versions, cipher suites, elliptic curves, and extensions offered by a client (the implant) acts as a unique cryptographic fingerprint. If an implant uses a custom Golang binary or the Python `requests` library to communicate, its TLS fingerprint will look completely different from a standard Chrome or Edge browser on a corporate workstation. 

Security researchers formalized this detection methodology into standards like **JA3** (Client Fingerprinting) and **JARM** (Server Fingerprinting).

## JA3: Fingerprinting the Client (The Implant)

JA3 collects the decimal values of specific fields in the `ClientHello` packet and concatenates them into a string, which is then MD5 hashed to produce the final JA3 fingerprint.

The fields used are:
`TLSVersion,CipherSuites,Extensions,EllipticCurves,EllipticCurveFormats`

Example JA3 String:
`771,4866-4867-4865-255,0-11-10-16-22-23-43-13-45-51,29-23-30,0`
Example JA3 Hash (MD5):
`cd08e31494f9531f560d64c695473da9` (Often maps to specific Go binaries or malware families).

If a defender sees a JA3 hash associated with Metasploit, Cobalt Strike's default Java client, or a raw Python script crossing their firewall, they can immediately flag or drop the traffic—regardless of what domain the traffic is destined for or what the HTTP `Host` header says.

### Defeating JA3: TLS Spoofing
To bypass JA3 fingerprinting, Red Teams must manipulate the underlying networking libraries of their implants:
1. **Using Native APIs**: On Windows, implants should use `WinINet` or `WinHTTP` APIs rather than custom sockets or embedded libraries. This forces the OS to handle the TLS handshake, making the implant's JA3 hash perfectly match a legitimate Windows process (like Internet Explorer or Edge).
2. **Modifying the Crypto Library**: If using cross-platform languages like Golang, operators can use packages like `utls` (uTLS by Refraction Networking) which allows the binary to explicitly spoof the `ClientHello` fingerprint of specific browsers (e.g., Firefox, Chrome, iOS).

## JARM: Fingerprinting the Server (The C2 Infrastructure)

While JA3 fingerprints the client, **JARM** is an active scanning technique used to fingerprint the C2 Server (the redirector or Team Server). 

JARM works by sending 10 specifically crafted `ClientHello` packets to the target server and recording the specific `ServerHello` responses (which ciphers it accepts, what order it returns extensions, how it handles TLS 1.2 vs TLS 1.3). These responses are hashed together to create the JARM fingerprint.

### The ASCII Anatomy of TLS Fingerprinting

```text
  [ Compromised Endpoint ]                            [ C2 Team Server ]
        (Implant)                                        (Redirector)
            |                                                 |
            | === ClientHello (TLS Version, Ciphers, Ext) ==> |
            |      [ Captured by Firewall -> JA3 Hash ]       |
            |                                                 |
            | <==== ServerHello (Chosen Cipher, Certs) ====== |
            |      [ Scanned by Shodan -> JARM Hash ]         |
            |                                                 |
            | ======== Key Exchange & Change Cipher ========> |
            | <======= Key Exchange & Change Cipher ========= |
            |                                                 |
            | <======== Encrypted Application Data =========> |
            |             (HTTP / Malleable C2)               |
```

Default installations of Cobalt Strike, Mythic, or sliver team servers have known, widely published JARM signatures. Internet scanners (Censys, Shodan) constantly scan the IPv4 space. If they find an IP matching a Cobalt Strike JARM, that IP is immediately added to global threat intelligence blocklists.

### Defeating JARM: Server-Side Evasion
To protect infrastructure from JARM scanning:
1. **Smart Reverse Proxies**: Place a highly configurable Nginx or HAProxy server in front of the Team Server. The TLS connection terminates at Nginx. By explicitly defining allowed Ciphers and TLS parameters in the Nginx config, you change the server's response behavior, thereby altering the JARM hash to look like a generic web server.
2. **Cloud CDNs**: Fronting the C2 with Cloudflare or AWS CloudFront completely replaces the server's JARM hash with the CDN's JARM hash.
3. **Conditional Dropping**: As discussed in redirectors, drop incoming traffic that doesn't match the exact JA3 hash or User-Agent of your implant. If the JARM scanner cannot complete the handshake, it cannot fingerprint the server.

## Certificate Anomalies

Beyond JA3 and JARM, the X.509 TLS certificate itself is a massive signature point. 
- **Default Certificates**: Never use default framework certificates (e.g., Cobalt Strike's `cobaltstrike.store`).
- **Let's Encrypt Transparency**: Let's Encrypt certs are highly scrutinized. Because of Certificate Transparency (CT) logs, the moment you issue a certificate for `malware-c2-update.com`, Blue Teams can see it. Red Teams often purchase legitimate, age-validated domains and use commercial CA certificates, or generate self-signed certificates that flawlessly mimic default Microsoft or Google certificates for internal pivoting.

## Real-World Attack Scenario

### The JARM Hunt and Evasion
A proactive threat hunting team uses Shodan to search for IPs presenting the JARM fingerprint `07d14d16d21d21d07c42d41d00041d24a458a375eef0c576d23a7bab9a9fb1` (a known default Cobalt Strike signature). They identify 400 active C2 servers globally and feed these IPs into their firewall blocklist.

**The Red Team Countermeasure**:
The Red Team anticipates this. They do not expose their Team Server. Instead, they deploy an Nginx redirector and modify the `ssl_ciphers` and `ssl_protocols` directives to match the exact configuration of an out-of-the-box Apache web server running on Ubuntu. 
When Shodan scans the Red Team's infrastructure, the resulting JARM hash is benign. Furthermore, the Red Team compiled their Golang implant using `uTLS`, instructing it to spoof the JA3 signature of Google Chrome `91.0`. When the implant beacons out, the firewall inspects the JA3, sees Chrome, and permits the traffic.

## Chaining Opportunities

TLS Fingerprinting evasion is closely tied to how you construct your perimeter infrastructure:
- **Redirectors**: Nginx configuration is the primary tool for manipulating JARM. (See [[07 - Redirectors Socat Iptables Nginx]])
- **CDN Usage**: CDNs neutralize JARM scanning by terminating the TLS connection at the edge. (See [[06 - Domain Fronting and CDN Abuse]])

## Related Notes
- [[06 - Domain Fronting and CDN Abuse]]
- [[07 - Redirectors Socat Iptables Nginx]]
- [[08 - Cloud Infrastructure for C2 AWS Azure DigitalOcean]]
- [[09 - C2 Obfuscation and Jitter]]
