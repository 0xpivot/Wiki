---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.08 Regex Bypass (evil.com matching .com)"
---

# 12.08 — Regex Bypass

## The Problem with Regex for CORS Validation

```
DEVELOPERS OFTEN WRITE REGEX INSTEAD OF WHITELISTS:
  Reason: "We have multiple subdomains, a list is too hard to maintain"
  
  COMMON WEAK PATTERNS:
  
  1. endsWith('.target.com'):
     evil.target.com → matches! (if subdomain takeover possible)
     
  2. includes('target.com'):
     attacktarget.com → matches!
     target.com.evil.com → matches!
     
  3. Regex /target\.com/:
     attackertarget.com → matches!
     target.com.evil.com → matches!
     
  4. Regex /^https:\/\/target\.com/:
     Does NOT match subdomains... but developer also meant to allow those
     → Adds: /^https:\/\/(.*\.)?target\.com$/
     → Now subdomain attack works!
```

---

## Bypass Pattern 1 — endsWith / suffix match

```
VULNERABLE CODE:
  // JavaScript:
  if (origin.endsWith('.target.com') || origin === 'https://target.com') {
    allow();
  }
  
  // Python:
  if origin.endswith('.target.com') or origin == 'https://target.com':
      allow()

BYPASS:
  Origin: https://evil.target.com    ← subdomain (if takeover possible)
  Origin: https://evil-target.com    ← NOT bypass (doesn't end in .target.com)
  
  But if check is just endsWith('target.com'):
  Origin: https://attackertarget.com → matches!

TEST:
  curl -H "Origin: https://evil.target.com" https://target.com/api
  curl -H "Origin: https://attackertarget.com" https://target.com/api
  (try both!)
```

---

## Bypass Pattern 2 — includes / substring match

```
VULNERABLE CODE:
  if 'target.com' in origin:  allow()

BYPASS:
  Origin: https://target.com.evil.com  → 'target.com' in this → MATCHES!
  Origin: https://attacktarget.com     → 'target.com' NOT in this
  Origin: https://evil.com/target.com  → 'target.com' in this → MATCHES!
  (URL path doesn't affect Origin header, but server code might check full string)

ATTACK:
  Register domain: target.com.evil.com
  OR host page at: https://evil.com/?ref=target.com (not helpful here)
  
  Host attack on target.com.evil.com!
```

---

## Bypass Pattern 3 — Weak Regex

```
VULNERABLE REGEX PATTERNS:

Pattern: /target\.com/
  Matches: https://attackertarget.com  ✓ bypass!
  Matches: https://target.com.evil.com ✓ bypass!

Pattern: /^https?:\/\/target\.com/
  Matches: https://target.com → correct
  Matches: https://target.com.evil.com → YES! (no anchor at end!)
  Fix: /^https:\/\/target\.com$/ (add $ anchor)

Pattern: /^https:\/\/(.*\.)?target\.com$/
  Matches: https://target.com → correct
  Matches: https://sub.target.com → correct
  Matches: https://evil.target.com → BYPASS if subdomain takeover!
  
PROPER REGEX:
  ^https:\/\/([a-zA-Z0-9-]+\.)?target\.com$
  Still allows subdomain attacks if any subdomain is vulnerable!
  Better: explicit whitelist!

TEST YOUR REGEX:
  Test inputs in order:
  https://target.com         → should allow
  https://sub.target.com     → should allow (if intended)
  https://evil.com           → must block
  https://evil.target.com    → depends on intent
  https://target.com.evil.com → must block!
  https://attackertarget.com → must block!
  http://target.com          → should block (insecure protocol)
```

---

## Real-World Bypass Examples

```
EXAMPLE 1 — Missing end anchor:
  Server regex: /^https:\/\/target\.com/
  Attacker domain: https://target.com.attacker.com
  → starts with https://target.com → MATCH!

EXAMPLE 2 — Unescaped dot:
  Server regex: /target.com/   (dot not escaped!)
  Dot matches any character!
  Attacker domain: https://targetXcom.evil.com
  → 'targetXcom' matches 'target.com' because . = any char!

EXAMPLE 3 — Case insensitive check:
  Server: if origin.lower().endswith('target.com')
  Attacker: https://TARGET.COM.evil.com (less common, browsers lowercase origins)

EXAMPLE 4 — Protocol not checked:
  Server: if 'target.com' in origin
  Attacker: Origin: http://target.com  (HTTP not HTTPS)
  → HTTP subdomains can be MITM'd!
```

---

## Testing for Regex Bypass

```bash
# GENERATE TEST ORIGINS:
origins=(
  "https://target.com"                   # legitimate
  "https://sub.target.com"               # subdomain
  "https://evil.target.com"              # subdomain (attack)
  "https://target.com.evil.com"          # domain confusion
  "https://attackertarget.com"           # suffix attack
  "https://notarget.com"                 # partial match
  "http://target.com"                    # HTTP version
  "https://evil.com/target.com"          # path confusion (unlikely but test)
  "null"                                 # null origin
)

for origin in "${origins[@]}"; do
  result=$(curl -s -I \
    -H "Origin: $origin" \
    -H "Cookie: session=YOURS" \
    "https://target.com/api/account" | grep -i "access-control-allow-origin")
  echo "$origin → $result"
done
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — reflection attack
- [[05 - Null Origin Misconfiguration]] — null attack
- [[07 - Subdomain Trust]] — using trusted subdomains
- [[12 - Defense Strict Origin Whitelisting]] — correct implementation (whitelist, not regex)
