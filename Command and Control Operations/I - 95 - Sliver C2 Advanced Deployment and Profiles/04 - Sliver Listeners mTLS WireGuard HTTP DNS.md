---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.04 Sliver Listeners mTLS WireGuard HTTP DNS"
---

# 95.04 Sliver Listeners: mTLS, WireGuard, HTTP, and DNS

## Overview

A critical component of adversary infrastructure is the mechanism by which implants communicate back to the Team Server. Sliver supports multiple egress protocols, known as listeners. Each protocol offers unique advantages, evasion capabilities, and OPSEC trade-offs.

Understanding how these listeners encapsulate and encrypt data, and how they interact with enterprise network boundaries, is essential for Red Teams engineering egress pathways and for Threat Hunters designing robust network traffic analysis (NTA) capabilities.

---

## The Four Primary Listeners

Sliver supports four main communication protocols: **mTLS**, **WireGuard (WG)**, **HTTP/S**, and **DNS**.

### 1. mTLS (Mutual TLS)
mTLS is the default and most robust protocol in Sliver. Unlike standard TLS where only the server proves its identity to the client, mTLS requires the client (implant) to also present an X.509 certificate to authenticate itself to the server.
- **Mechanism**: When generated, the implant embeds a client certificate signed by the Team Server's CA. During the TLS handshake, both parties verify each other.
- **Advantages**: Extremely secure against active probing or replay attacks. Blue teams cannot easily interact with the listener without the implant's certificate.
- **Disadvantages**: TCP over a non-standard web port (if not proxied) can stand out.

### 2. WireGuard (WG)
WireGuard is a modern, high-performance VPN protocol that uses state-of-the-art cryptography (Noise protocol framework, ChaCha20, Poly1305).
- **Mechanism**: Sliver creates a user-space WireGuard TUN/TAP interface. The implant encapsulates the gRPC traffic inside WireGuard UDP packets.
- **Advantages**: Because it is connectionless (UDP), it is highly resilient to network drops and IP changes. It is extremely fast.
- **Disadvantages**: Corporate firewalls often block outbound UDP traffic on non-standard ports (like the default WG port 51820).

### 3. HTTP / HTTPS
HTTP/S listeners camouflage C2 traffic within standard web traffic.
- **Mechanism**: The gRPC protobuf data is base64 encoded or encrypted and chunked into HTTP POST/GET requests. HTTPS wraps this in standard TLS.
- **Advantages**: Blends seamlessly into normal user web browsing. Almost universally permitted outbound through corporate firewalls. Supports Layer 7 proxies and redirectors.
- **Disadvantages**: Requires careful profile customization to avoid generic framework signatures (e.g., default User-Agents or URIs). High overhead due to HTTP headers.

### 4. DNS (Domain Name System)
DNS C2 relies on the fact that DNS resolution is permitted in almost every environment.
- **Mechanism**: The implant encodes data, chunking it into subdomains of a domain controlled by the attacker (e.g., `1a2b3c.data.evil.com`). The internal DNS server recursively resolves this, eventually hitting the Team Server's DNS listener. Responses from the server are encoded in DNS records (TXT, CNAME, or NULL).
- **Advantages**: Can bypass strict outbound firewall rules (e.g., restricted subnets with zero internet access but internal DNS resolution).
- **Disadvantages**: Extremely slow. Generates massive amounts of DNS traffic, making it highly conspicuous to network defenders.

---

## ASCII Diagram: Listener Encapsulation

```text
                  HOW DATA IS ENCAPSULATED PER LISTENER

[ Original Command Data: "whoami" (Protobuf) ]

  +-----------------------+   +-----------------------+   +-----------------------+
  |        mTLS           |   |       HTTP/S          |   |         DNS           |
  +-----------------------+   +-----------------------+   +-----------------------+
  | TCP Header (Port 8888)|   | TCP Header (Port 443) |   | UDP Header (Port 53)  |
  +-----------------------+   +-----------------------+   +-----------------------+
  | TLS 1.3 Record        |   | TLS 1.3 Record        |   | DNS Query Header      |
  | (Mutual Auth Handshake|   | (Standard Auth)       |   +-----------------------+
  +-----------------------+   +-----------------------+   | QNAME:                |
  | Encrypted Payload:    |   | HTTP POST /api/sync   |   | base32(data).evil.com |
  | [ gRPC Message ]      |   | User-Agent: Mozilla.. |   +-----------------------+
  +-----------------------+   +-----------------------+   | DNS Response (TXT)    |
                              | Encrypted Payload:    |   | base32(server_reply)  |
                              | [ gRPC Message ]      |   +-----------------------+
                              +-----------------------+
```

---

## Threat Hunting & Detection Engineering

Each protocol leaves distinct forensic artifacts on the network.

### Hunting mTLS and WireGuard
- **mTLS Fingerprinting**: Threat hunters can utilize JA3 (client) and JA3S (server) TLS fingerprinting. Since Sliver uses Golang's `crypto/tls` library, its JA3 hash differs significantly from standard browsers (Chrome/Edge). Searching for unexpected JA3 hashes combined with long connection durations is a strong indicator.
- **WireGuard Heuristics**: Look for sustained UDP streams on arbitrary high ports with uniform packet sizes, which is characteristic of VPN encapsulation.

### Hunting HTTP/S
- **Header Anomalies**: Look for HTTP requests missing typical headers (like `Accept-Language` or `Referer`) or containing default Go user agents if profiles are misconfigured.
- **Beaconing Rhythms**: Use Zeek or Suricata to monitor standard deviation in request intervals.
- **Certificate Transparency (CT) Logs**: Monitor for newly registered domains resolving to unknown cloud VPS providers hosting Let's Encrypt certificates generated just days prior to the communication.

### Hunting DNS C2
- **DNS Volume Analysis**: DNS C2 generates massive anomalies in query volume. A single host performing thousands of TXT or NULL record queries to a single root domain within minutes is highly anomalous.
- **Payload Length**: Legitimate DNS queries are short. Queries containing long, high-entropy subdomains (e.g., `ajd812jdasd912jdasda.malicious.com`) are indicative of data encapsulation.
- **Record Types**: Hunt for an unusual frequency of `TXT` or `NULL` records, which are rarely queried in high volume during normal operations.

---

## Real-World Attack Scenario

### Bypassing an Air-Gapped/Restricted Subnet
An adversary gains access to a highly secure database server subnet. This subnet has strict egress filtering applied at the firewall: all TCP and UDP outbound traffic to the internet is explicitly denied.

However, the database server is configured to resolve internal hostnames via the corporate Active Directory Domain Controller.

### Execution
The adversary drops a Sliver Beacon configured exclusively with a **DNS listener**. 

### The C2 Pathway
1. The implant encodes its check-in data into a long subdomain string: `gRPC-data-chunk1.c2.attacker-domain.com`.
2. The database server sends this query to the internal Domain Controller via standard UDP port 53.
3. The Domain Controller, acting as a recursive resolver, forwards the query to the external internet to resolve `attacker-domain.com`.
4. The query reaches the Sliver Team Server acting as the authoritative Name Server for the domain.
5. The Team Server processes the chunk and replies with the next command embedded in a `TXT` record.
6. The DC passes the TXT record back to the database server.

The firewall rules are successfully bypassed because the traffic appears to be legitimate internal DNS resolution, and the actual connection to the internet is made by the trusted Domain Controller.

---

## Chaining Opportunities

- **Protocol Rotation**: Modern implants can be configured to attempt egress over multiple listeners sequentially. E.g., Attempt mTLS -> Fallback to HTTP -> Fallback to DNS.
- **Domain Fronting**: Combining the HTTP listener with Cloudflare or Fastly infrastructure to obfuscate the true destination IP, relying on the `Host` header to route traffic to the backend team server.

---

## Related Notes

- [[95.01 Introduction to Sliver C2 Architecture]]
- [[95.05 Customizing Sliver Profiles for OPSEC]]
- [[42.11 Advanced DNS Tunneling and Exfiltration]]
- [[55.04 JA3 and JA3S TLS Fingerprinting Strategies]]
- [[38.07 Egress Filtering and Firewall Bypass Techniques]]

---
*Note: This material is intended for Threat Hunting, Detection Engineering, and authorized Red Team emulation purposes only.*
