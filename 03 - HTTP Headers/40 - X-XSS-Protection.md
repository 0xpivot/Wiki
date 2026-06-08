---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.40 X-XSS-Protection — Legacy, Abusable"
---

# 03.40 — X-XSS-Protection

## What is it?

`X-XSS-Protection` is a legacy header that enabled the browser's built-in XSS filter (present in older IE, Chrome, and Safari). It was REMOVED from Chrome in 2019 and Edge in 2020 because the filter itself introduced new vulnerabilities (could be abused to leak page content). Modern browsers ignore this header.

**Key point for VAPT:** Setting `X-XSS-Protection: 1; mode=block` is NOT a meaningful security control in 2024+. The proper defense is CSP.

---

## Header Values (Legacy)

```
X-XSS-Protection: 0              → disable filter
X-XSS-Protection: 1              → enable filter (sanitize)
X-XSS-Protection: 1; mode=block  → enable, block page instead of sanitize
X-XSS-Protection: 1; report=https://example.com → report violations
```

---

## Attack: XSS-Protection Bypass (Historical)

```
The filter worked by detecting reflected XSS in responses.

BYPASS TECHNIQUES (worked in old browsers):
  1. Encoding variations:
     <scr<script>ipt>alert(1)</script>
     → Filter "fixed" the first part, which completed the second → XSS!
  
  2. Character set manipulation:
     Set Content-Type: charset=IBM037 (EBCDIC)
     → Filter didn't decode → missed XSS payloads!
  
  3. Using mode=block to detect content:
     Inject payload that blocks page if specific content present
     → If page blocked → content existed → information leak!
```

---

## Attack: Using X-XSS-Protection to Disable Filter (Historical)

```
ATTACKER SCENARIO (IE/Edge):
  App reflects attacker-controlled Header value:
  
  Request: X-XSS-Protection: 0
  → If server reflects this in response headers
  → XSS filter disabled in victim's browser!
  → All XSS now executes!
  
  (Only possible if server echoes request headers in response)
```

---

## Current State

```
BROWSER SUPPORT:
  Chrome: REMOVED (v78, 2019)
  Edge: REMOVED (v18)
  Firefox: NEVER supported
  Safari: REMOVED
  IE 11: Still has it (but IE is end-of-life)

MODERN RECOMMENDATION:
  DO NOT rely on X-XSS-Protection.
  Use Content-Security-Policy instead.
  
  If you set: X-XSS-Protection: 0
  → Explicitly disables (on IE) → worse than not setting!
  
  Best practice: omit the header entirely, OR set 0 to avoid old browser issues.
```

---

## Testing

```bash
# Check if X-XSS-Protection is set (informational):
curl -sI https://target.com | grep -i "x-xss-protection"

# If set to "0" → might indicate the developer was trying to work around it
# If set to "1; mode=block" → outdated but harmless in modern browsers
# If missing → fine, modern browsers don't use it
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Relying on X-XSS-Protection | Use Content-Security-Policy instead |
| Setting X-XSS-Protection: 0 | Evaluate if needed; generally don't set this header |

---

## Related Notes
- [[34 - Content-Security-Policy]] — the proper modern XSS defense
- [[Module 02 - XSS]] — XSS attacks and defenses
