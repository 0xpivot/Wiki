---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.65 Public-Key-Pins (HPKP) — Deprecated, History"
---

# 03.65 — Public-Key-Pins (HPKP)

## What is it?

HTTP Public Key Pinning (HPKP) was a security header that told browsers to remember specific public keys for a site and reject any other certificate — even from a trusted CA. It was deprecated in 2019 after causing widespread outages and being weaponized for attacks. Understanding it helps explain why certain security mechanisms fail.

---

## What HPKP Did

```
Server sends:
  Public-Key-Pins: pin-sha256="base64hash1"; pin-sha256="base64hash2"; 
                   max-age=5184000; includeSubDomains

MEANING:
  "Only accept my cert if its public key matches one of these hashes."
  "Remember this for 60 days."
  "Apply to all subdomains."
  
  Even if a rogue CA issues a new cert for your domain:
  → Browser has pinned keys → rejects the rogue cert!
  → MITM prevention!
```

---

## Why HPKP Was Dangerous (and Deprecated)

```
PROBLEM 1: Self-inflicted DoS
  If you pinned a key and then:
  - Lost the private key
  - Changed CAs
  - Cert expired and new cert has different key
  
  → ALL your users couldn't access your site for max-age duration!
  → No way to undo (browser has cached the pin)!
  → "HPKP suicide" — very real risk!

PROBLEM 2: HPKP Ransom Attack
  Attacker gets XSS or brief access → injects malicious HPKP header:
  Public-Key-Pins: pin-sha256="attackerKey"; max-age=31536000
  
  → Browser pins attacker's key!
  → Site owner changes cert (real cert) → doesn't match attacker's pinned key!
  → Users can't access site for 1 YEAR!
  → Site owner pays ransom to stop!
  
  This attack was documented in 2016.

RESULT:
  Chrome 72 (2019): HPKP removed
  Firefox: deprecated
  All browsers: deprecated
```

---

## Current Status

```
HPKP:       DEPRECATED - do not use
Expect-CT:  DEPRECATED - CT enforced natively
HSTS:       ACTIVE - still use this!
CSP:        ACTIVE - critical header
SRI:        ACTIVE - use for third-party resources

REPLACEMENT FOR HPKP GOAL:
  Certificate Transparency (CT) achieves similar goal:
  → Unauthorized certs appear in public logs → detectable!
  → No risk of self-DoS!
  
  CAA DNS records:
  → Restrict which CAs can issue certs for your domain!
  → Server-side, not browser-side → no risk to end users!
```

---

## If You See HPKP in the Wild

```
Finding HPKP on a target:
  Public-Key-Pins: ...
  
  IMPLICATIONS:
  - Old server configuration!
  - IT team may not have updated security headers in years!
  - Look for other outdated practices:
    → Old TLS versions (TLS 1.0/1.1)
    → Weak cipher suites
    → X-XSS-Protection (another deprecated header)
    → Missing CSP
  
  REPORT: "Remove HPKP (deprecated, creates availability risk)"
          "Review and update all security headers"
```

---

## Testing

```bash
# Check for HPKP (should not be present):
curl -sI https://target.com | grep -i "public-key-pins"
# If present → informational: deprecated and should be removed

# Check overall security header status:
curl -sI https://target.com | grep -iE "hsts|csp|x-frame|x-content-type|referrer-policy|permissions-policy"
# Compare against recommended set
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| HPKP still enabled | Remove it immediately; prevent outage risk |
| Cert pinning need | Use CAA DNS records instead |
| Unauthorized cert concern | Monitor Certificate Transparency logs |

---

## Related Notes
- [[37 - Strict-Transport-Security]] — HSTS (the active equivalent)
- [[60 - Expect-CT]] — CT monitoring (also deprecated)
- [[01.18 - Certificates and Certificate Authorities]] — cert pinning concepts
