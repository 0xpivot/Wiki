---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.15 VPNs IPsec and Tunneling Basics"
---

# 70.15 VPNs IPsec and Tunneling Basics

## 1. VPN Architecture
Extends a private network across a public network.
- **Site-to-Site:** Connects two static routers. Transparent to users.
- **Remote Access:** Connects roaming users to the corporate network via client software.

## 2. IPsec Suite
Operates at Layer 3.
- **AH (Authentication Header):** Protocol 51. Integrity and Authentication. No encryption. Breaks NAT.
- **ESP (Encapsulating Security Payload):** Protocol 50. Encryption, Integrity, Authentication.

### Modes
- **Transport Mode:** Encrypts payload only. Original IP header is kept.
- **Tunnel Mode:** Encrypts entire packet. Prepends new IP header.

## 3. IKE (Internet Key Exchange)
Establishes Security Associations (SAs) over UDP 500.
- **Phase 1:** Establishes secure channel. (Main Mode vs Aggressive Mode).
- **Phase 2:** Negotiates IPsec SAs to encrypt the actual data.

## 4. ASCII Diagram: IPsec Tunnel Mode Packet
```text
  [ New IP Header | ESP Header | Orig IP Header | TCP Header | Payload | ESP Trailer ]
  |-------------| |----------------------- ENCRYPTED -----------------------------|
  |--------------------------- AUTHENTICATED -------------------------------------|
```

## 5. SSL/TLS VPNs
Operates at Layer 4-7.
- Often easier to deploy than IPsec due to better NAT traversal (appears as standard HTTPS traffic).
- Clientless (Web Portal) or Full Tunnel (Virtual Interface).

## 6. VAPT Context and Exploitation
- **IKE Aggressive Mode:** Sends PSK hash in the clear. Can be captured and cracked offline (Hashcat).
- **Split Tunneling:** Allows an attacker to pivot through a compromised remote worker's laptop directly into the corporate network.
- **Device Vulnerabilities:** VPN edge appliances (Pulse, Fortinet) are prime targets for RCE exploits.

## Chaining Opportunities
- **Lateral Movement:** Pivot through compromised segments using [[11 - SSH Protocol Basics and Key Authentication]].
- **Payload Delivery:** Combine with [[12 - SMTP POP3 and IMAP Email Protocols]] for access.
- **Recon:** Findings feed into [[13 - SNMP Protocol Basics and Community Strings]].
- **Evasion:** Bypasses [[14 - Firewalls IDS IPS and NAT Explained]].
- **VPNs:** Compare with [[15 - VPNs IPsec and Tunneling Basics]].

## Related Notes
- [[11 - SSH Protocol Basics and Key Authentication]]
- [[12 - SMTP POP3 and IMAP Email Protocols]]
- [[13 - SNMP Protocol Basics and Community Strings]]
- [[14 - Firewalls IDS IPS and NAT Explained]]
- [[15 - VPNs IPsec and Tunneling Basics]]

## 7. Extended IPsec Configuration and Diagnostics

### 7.1 StrongSwan `ipsec.conf` Template (Site-to-Site)
Below is an example of a deeply hardened IPsec Site-to-Site configuration using IKEv2, completely avoiding Aggressive Mode and enforcing strong AES-GCM cryptography.

```text
# ipsec.conf - strongSwan IPsec configuration file

config setup
    # Enable strict CRL checking
    strictcrlpolicy=yes
    # Unique IDs allow multiple connections per peer
    uniqueids=yes
    # Verbose logging for ISAKMP and Kernel layers
    charondebug="ike 2, knl 2, cfg 2, net 1, esp 2"

# Default connection settings applied to all tunnels
conn %default
    # Enforce IKEv2 (disables IKEv1 Aggressive Mode entirely)
    keyexchange=ikev2
    
    # Phase 1: Authentication and Key Exchange Crypto
    # AES-256 in Galois/Counter Mode, SHA-384 for PRF, ECDP-384 for Diffie-Hellman
    ike=aes256gcm16-prfsha384-ecp384!
    
    # Phase 2: ESP Payload Crypto
    # AES-256-GCM inherently provides both encryption and integrity
    esp=aes256gcm16-ecp384!
    
    # Enable Dead Peer Detection (DPD)
    dpdaction=restart
    dpddelay=30s
    dpdtimeout=120s
    
    # Key lifetimes
    ikelifetime=3h
    lifetime=1h
    margintime=9m

# Specific Tunnel Configuration (HQ to Branch)
conn hq-to-branch
    # Local endpoint (HQ)
    left=203.0.113.10
    leftsubnet=10.0.0.0/16
    leftid=@hq.example.com
    leftauth=pubkey
    leftcert=hqCert.pem
    
    # Remote endpoint (Branch)
    right=198.51.100.20
    rightsubnet=192.168.10.0/24
    rightid=@branch.example.com
    rightauth=pubkey
    
    # Start automatically on boot
    auto=start
```

### 7.2 IKE Aggressive Mode Enumeration (VAPT Context)
If IKEv1 is still active, an attacker might probe it using `ike-scan`. Below is a diagnostic output showing a vulnerable Aggressive Mode configuration that leaks the PSK hash.

```text
$ ike-scan -M -A 203.0.113.10
Starting ike-scan 1.9 with 1 hosts
203.0.113.10  Aggressive Mode Handshake returned HDR, SA, KE, NONCE, ID, HASH
	SA=(Enc=3DES Hash=MD5 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800)
	ID=192.168.1.1
	HASH=a1b2c3d4e5f6071829304a5b6c7d8e9f

1 hosts scanned in 0.123 seconds (8.13 hosts/sec). 1 returned handshake.

# The HASH value above can now be taken offline and cracked.
$ hashcat -m 5300 ike_hash.txt rockyou.txt
```
