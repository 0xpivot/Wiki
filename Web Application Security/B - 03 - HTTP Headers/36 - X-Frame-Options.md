---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.36 X-Frame-Options — Clickjacking"
portswigger_labs: ["Clickjacking — 5 labs"]
---

# 03.36 — X-Frame-Options

## What is it?

`X-Frame-Options` controls whether a page can be embedded in an `<iframe>`, `<frame>`, or `<object>`. Without it, attackers can embed your page in their site and trick users into clicking invisible buttons — this is clickjacking.

---

## Values

```
X-Frame-Options: DENY           → never allow embedding
X-Frame-Options: SAMEORIGIN     → only allow same-origin embedding
X-Frame-Options: ALLOW-FROM https://trusted.com  → allow specific origin
                 (ALLOW-FROM is deprecated and not widely supported!)

MODERN REPLACEMENT:
  Content-Security-Policy: frame-ancestors 'none'
  Content-Security-Policy: frame-ancestors 'self'
  Content-Security-Policy: frame-ancestors https://trusted.com
  
  CSP frame-ancestors supersedes X-Frame-Options in modern browsers.
  Set both for compatibility.
```

---

## Attack: Clickjacking

```
PRECONDITION: Target page has no X-Frame-Options or CSP frame-ancestors.

ATTACK SETUP (attacker's page):
  <html>
  <head>
  <style>
    iframe {
      width: 1000px; height: 700px;
      position: absolute;
      top: 0; left: 0;
      opacity: 0.001;    ← invisible!
      z-index: 2;        ← on top
    }
    div {
      position: absolute;
      top: 265px; left: 200px;    ← aligned with target's "Delete Account" button
      z-index: 1;
    }
  </style>
  </head>
  <body>
    <div>Click here to Win!</div>     ← decoy button (visible)
    <iframe src="https://target.com/account/settings"></iframe>  ← invisible victim page
  </body>
  </html>
  
WHAT HAPPENS:
  Victim sees: "Click here to Win!"
  Victim clicks: Actually clicks "Delete Account" on invisible target page!
  → Account deleted without victim's knowledge!
```

**PortSwigger Labs:** Clickjacking (5 labs)

---

## Attack: Drag-and-Drop Clickjacking

```
VARIANT: Instead of clicking, victim drags a "prize" to a drop zone.
  Invisible frame positioned so drop zone = file upload or sensitive input.
  
VARIANT: Multi-step clickjacking:
  Frame target page's confirmation dialog.
  Victim clicks through confirmation without seeing it.
```

---

## Advanced: Iframe Sandbox Bypass Attempts

```
<iframe sandbox="allow-forms allow-scripts" src="https://target.com">

sandbox attribute restricts many capabilities.
But sandboxed iframes can still:
  - Submit forms (allow-forms)
  - Run scripts (allow-scripts)
  → Sandboxed clickjacking still possible for form submissions!

Note: sandbox causes Origin: null → breaks some CSRF tokens.
```

---

## Testing for Clickjacking

```bash
# Check if X-Frame-Options is set:
curl -sI https://target.com | grep -i "x-frame-options\|frame-ancestors"

# Test embedding:
cat > frame-test.html << 'EOF'
<html>
<body>
<iframe src="https://TARGET.com" width="1000" height="700"></iframe>
<p>If you can see target.com above → clickjacking possible!</p>
</body>
</html>
EOF
# Open in browser → if iframe loads → vulnerable!

# Burp Suite:
# Clickjacking PoC generator: Target → Engagement Tools → Generate Clickjacking PoC
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| No X-Frame-Options | Add `X-Frame-Options: DENY` (or SAMEORIGIN) |
| No CSP frame-ancestors | Add `frame-ancestors 'none'` to CSP |
| ALLOW-FROM (deprecated) | Migrate to CSP frame-ancestors |
| Clickjacking on auth pages | Never allow auth pages (login, sensitive forms) to be framed |

**Quick fix (Nginx):**
```nginx
add_header X-Frame-Options "DENY" always;
add_header Content-Security-Policy "frame-ancestors 'none'" always;
```

---

## Related Notes
- [[34 - Content-Security-Policy]] — CSP frame-ancestors directive
- [[Module 13 - Clickjacking]] — full clickjacking exploitation
