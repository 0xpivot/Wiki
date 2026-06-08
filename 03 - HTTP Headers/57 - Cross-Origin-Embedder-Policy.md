---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.57 Cross-Origin-Embedder-Policy (COEP)"
---

# 03.57 — Cross-Origin-Embedder-Policy (COEP)

## What is it?

`Cross-Origin-Embedder-Policy` (COEP) is a security header that prevents a document from loading cross-origin resources unless those resources explicitly opt in to being embedded (via CORS or CORP headers). COEP is required alongside COOP to enable powerful browser features like `SharedArrayBuffer` (used in Spectre-like attacks).

---

## Values

```
Cross-Origin-Embedder-Policy: unsafe-none     → default; any resource loadable
Cross-Origin-Embedder-Policy: require-corp    → all cross-origin resources must have CORP or CORS headers
Cross-Origin-Embedder-Policy: credentialless  → cross-origin requests made without credentials
```

---

## Why It Matters for Security

```
SPECTRE ATTACK (2018):
  Spectre exploits CPU speculative execution to read other processes' memory.
  SharedArrayBuffer enabled precise timing needed for Spectre.
  → Browsers disabled SharedArrayBuffer after Spectre!

RE-ENABLING SharedArrayBuffer (safely):
  Browser allows SharedArrayBuffer ONLY if page is "cross-origin isolated":
    Cross-Origin-Opener-Policy: same-origin    ← COOP
    Cross-Origin-Embedder-Policy: require-corp  ← COEP
  
  These together ensure page can't load attacker-controlled content
  that could be used in Spectre timing attacks.

ATTACK RELEVANCE:
  Apps that enable SharedArrayBuffer without COEP:
  → Attackers can use timing attacks to leak cross-origin data!
  → Spectre-style reading of sensitive memory!
```

---

## Attack: Missing COEP Enables Timing Attacks

```
SCENARIO: App uses SharedArrayBuffer (requires cross-origin isolation).
          But doesn't set COEP properly.
          Browser refuses SharedArrayBuffer → app broken.
          
          OR app circumvents via Web Workers without COEP.

IF COEP is missing:
  → High-resolution timer available (performance.now() less restricted)
  → Enables Spectre-like side-channel attacks on co-located content
  → Can leak information from cross-origin iframes loaded on same page
```

---

## Practical VAPT Check

```bash
# Check COEP:
curl -sI https://target.com | grep -i "cross-origin-embedder-policy"

# Also check for COOP (they work together):
curl -sI https://target.com | grep -i "cross-origin-opener-policy"

# Check for SharedArrayBuffer usage (browser DevTools):
# Console: typeof SharedArrayBuffer === 'undefined' → not available
# If available → app is cross-origin isolated → COEP + COOP set!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| SharedArrayBuffer without isolation | Set COEP: require-corp + COOP: same-origin |
| Cross-origin resource loading without consent | Ensure all resources have CORP or CORS headers |

---

## Related Notes
- [[58 - Cross-Origin-Opener-Policy]] — COOP (partner header)
- [[59 - Cross-Origin-Resource-Policy]] — CORP (required by COEP)
- [[Module 16 - Side-Channel Attacks]] — Spectre and timing
