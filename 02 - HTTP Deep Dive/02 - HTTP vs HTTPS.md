---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.02 HTTP vs HTTPS"
---

# 02.02 — HTTP vs HTTPS

## What is it?

**HTTP** sends data in cleartext — anyone who can intercept the traffic can read it. **HTTPS** (HTTP Secure) wraps HTTP inside TLS encryption, making traffic unreadable to eavesdroppers.

HTTPS = HTTP + TLS. The HTTP protocol itself doesn't change — TLS encrypts it in transit.

---

## HTTP vs HTTPS Side by Side

```
HTTP (Port 80)                      HTTPS (Port 443)
──────────────────────────────────────────────────────
Cleartext — readable by anyone       Encrypted by TLS
No server identity verification      Server identity verified (cert)
Anyone on path can see data          Only client+server can read
Anyone on path can MODIFY data       Data integrity guaranteed
ISP sees full request/response       ISP only sees IP + SNI hostname
Man-in-middle reads credentials      Man-in-middle sees encrypted noise
Suitable for: nothing sensitive      Required for: all sites

NETWORK CAPTURE COMPARISON:

HTTP request on wire:
  50 72 6f 78 79 2d 43 6f  6e 6e 65 63 74 69 6f 6e  Proxy-Connection
  3a 20 6b 65 65 70 2d 61  6c 69 76 65 0d 0a 43 6f  : keep-alive..Co
  6e 74 65 6e 74 2d 54 79  70 65 3a 20 61 70 70 6c  ntent-Type: appl
  [READABLE — username=alice&password=secret visible!]

HTTPS traffic on wire:
  17 03 03 00 28 ab cd ef  12 34 56 78 9a bc de f0  ....(........4Vx
  34 56 78 9a bc de f0 12  [ENCRYPTED NOISE — unreadable!]
```

---

## What HTTPS Protects Against

```
THREAT: Passive Eavesdropping
  Network attacker, ISP, coffee shop WiFi operator
  Just reads traffic from the wire
  HTTP: ✗ Full request/response visible
  HTTPS: ✓ Only sees IP + port + SNI hostname

THREAT: Active Man-in-the-Middle
  Attacker intercepts and modifies traffic
  HTTP: ✗ Can read AND modify anything (inject scripts, change passwords)
  HTTPS: ✓ Modifications detected by MAC → connection rejected
  HTTPS: ✓ Only valid cert holder can terminate connection

THREAT: Session Hijacking from Sniffing
  Attacker captures your session cookie from wire
  HTTP: ✗ Cookie visible in cleartext
  HTTPS: ✓ Cookie encrypted, can't be captured via sniffing
  (still vulnerable to XSS-based cookie theft)
```

---

## What HTTPS Does NOT Protect Against

```
HTTPS ≠ SECURE APPLICATION

Things HTTPS doesn't protect:
  ✗ SQL injection (encrypted but malicious payload still executes)
  ✗ XSS (encrypted but JS still runs in browser)
  ✗ CSRF (encrypted but forged request still comes from victim's browser)
  ✗ Insecure direct object references (IDOR)
  ✗ Business logic flaws
  ✗ Server-side vulnerabilities
  ✗ Password stored in plaintext on server

HTTPS only protects traffic IN TRANSIT.
Application security is separate.
```

---

## Security Context — HTTP vs HTTPS in VAPT

### 1. HSTS — HTTP Strict Transport Security

HSTS forces browsers to always use HTTPS, even if a URL says HTTP.

```bash
# Check if HSTS is set
curl -I https://target.com | grep -i strict

# Good response:
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
#                          ↑1 year cache   ↑subdomains too   ↑in preload list

# Missing HSTS = SSL strip attack possible:
# Attacker downgrades HTTPS to HTTP via MITM
# Victim connects over HTTP → credentials exposed
```

### 2. Mixed Content — HTTP Resources in HTTPS Page

```html
<!-- HTTPS page loading HTTP resource: -->
<script src="http://cdn.target.com/jquery.js"></script>
<!-- ↑ VULNERABLE: attacker can MITM the HTTP resource and inject JS! -->
<!-- Even though the page itself is HTTPS! -->

<!-- Check for mixed content: -->
<!-- Browser console → Security → Mixed Content warnings -->

# Burp Suite: Check for HTTP in resources
curl -s https://target.com | grep -oP 'http://[^"]+' | grep -v "^https"
```

### 3. Testing HTTPS Downgrade

```bash
# Check if HTTP redirects to HTTPS:
curl -I http://target.com
# 301 Moved Permanently → Location: https://target.com ← good!
# 200 OK directly over HTTP ← bad! Site accessible over HTTP

# What if HSTS is missing?
# SSL strip:
sudo bettercap -iface eth0 -eval "set arp.spoof.targets 192.168.1.100; arp.spoof on; https.proxy on; net.sniff on"
```

### 4. SNI — What ISPs See on HTTPS

```
Even with HTTPS, the ISP/network observer sees:
  - Your IP address
  - Server's IP address
  - Port 443
  - SNI (Server Name Indication) = hostname in TLS ClientHello
    → ISP knows you're connecting to "bank.com" but not what you're doing

ESNI/ECH (Encrypted ClientHello):
  Newer TLS 1.3 extension that encrypts the SNI
  Cloudflare supports it
  Hides even the hostname from network observers
```

### 5. Certificate Warnings — Attacker MITM Indicator

```
When a MITM attacker intercepts HTTPS:
  They need to present THEIR certificate (can't forge the real one)
  Browser shows: "Your connection is not private" / NET::ERR_CERT_AUTHORITY_INVALID
  
  If victim clicks "Proceed anyway" → attacker sees all traffic
  
  Solution: HSTS preloading + HPKP (cert pinning) prevent clicking through
```

---

## Hands-On: HTTP vs HTTPS Testing

```bash
# Check if site forces HTTPS:
curl -I http://target.com | grep -i location
# Should redirect to https://

# Check TLS details:
openssl s_client -connect target.com:443
# Shows cert, cipher suite, TLS version

# Check HSTS:
curl -I https://target.com | grep -i strict-transport

# Test HTTP/HTTPS on all discovered hosts:
httpx -l hosts.txt -p 80,443 -title -status-code -tech-detect

# Check for HTTP site (common on internal networks):
nmap -p 80,443 --script http-title --open 192.168.1.0/24
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Site accessible over HTTP | Force redirect 301 HTTP → HTTPS |
| HSTS not set | Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` |
| Mixed content (HTTP resources on HTTPS page) | Change all resource URLs to HTTPS or `//` protocol-relative |
| Weak TLS configuration | Disable TLS 1.0/1.1, use only TLS 1.2/1.3 |
| Self-signed certificate | Replace with CA-signed certificate |

---

## Related Notes
- [[01 - What is HTTP]] — HTTP basics
- [[17 - TLS SSL How HTTPS Works]] — TLS in detail
- [[18 - Certificates and Certificate Authorities]] — certificate trust
- [[Module 03 - HTTP Headers Security]] — HSTS, security headers
