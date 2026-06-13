---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.14 User-Agent — Fingerprinting, WAF Bypass"
---

# 03.14 — User-Agent

## What is it?

The `User-Agent` header identifies the client software making the request (browser name, version, OS). It was designed for servers to serve compatible content to different clients. In VAPT, it's useful for fingerprinting, bypassing WAFs, and triggering different application behaviors.

---

## Common User-Agent Values

```
Chrome browser (Windows):
  Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36

Firefox:
  Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0

Safari (Mac):
  Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15

Curl (tool fingerprint!):
  curl/7.81.0

Python requests:
  python-requests/2.31.0

Sqlmap:
  sqlmap/1.7.8 (https://sqlmap.org)   ← red flag to WAFs!

Googlebot:
  Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
```

---

## Attack 1: WAF Bypass via User-Agent

```
WAFs may behave differently based on User-Agent:

SCENARIO 1: WAF allows known search engine bots:
  User-Agent: Googlebot   → WAF allows without inspection!
  User-Agent: Bingbot
  
SCENARIO 2: WAF checks for scanner signatures and blocks:
  User-Agent: sqlmap → WAF blocks immediately
  
  But change to:
  User-Agent: Mozilla/5.0 (...)
  → WAF thinks it's a normal browser → allows!

SCENARIO 3: App has different code paths for mobile:
  User-Agent: (mobile browser string)
  → Different (potentially less-tested) code path → different vulnerabilities
```

---

## Attack 2: Application Behavior Changes

```
Many apps serve different content based on User-Agent:

MOBILE DETECTION:
  Normal UA → desktop HTML (with CSRF protection, complex JS)
  Mobile UA → simpler API calls → might lack some security features
  
  Try: User-Agent: Mozilla/5.0 (Android 13; Mobile; rv:109.0)
  Observe: does app behave differently? Different API endpoint?

DEBUG MODE TRIGGER:
  Some apps enable debug output for specific UAs:
  User-Agent: Python/Debug
  User-Agent: developer-internal-tool
  
  Try common internal tool names → might get debug info!

BOT DETECTION BYPASS:
  App blocks automated tools (scrapers, fuzzers) via UA check:
  User-Agent: curl → blocked
  User-Agent: [browser string] → allowed
```

---

## Attack 3: User-Agent Injection

```
If UA is stored/displayed (server logs, admin panels):

SQLi via User-Agent:
  User-Agent: Mozilla/5.0' OR SLEEP(5)--
  → If stored in DB → time-based blind SQLi!

XSS via User-Agent:
  User-Agent: <script>alert(1)</script>
  → If admin dashboard displays "Recent visitors" with UA → stored XSS!

Log Injection:
  User-Agent: legitimate\n[FAKE LOG] Admin logged in successfully
  → Poisoned log entry
```

---

## Hands-On: UA Testing

```bash
# Mimic Googlebot
curl -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  https://target.com/

# Mobile UA
curl -A "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/109.0" \
  https://target.com/

# Empty UA
curl -A "" https://target.com/

# SQLi in UA (test for stored injection)
curl -A "Mozilla' OR SLEEP(5)-- " https://target.com/

# UA XSS test
curl -A "<script>alert(1)</script>" https://target.com/

# Different UAs and compare responses:
diff <(curl -s -A "Mozilla/5.0" https://target.com/) \
     <(curl -s -A "curl/7.81" https://target.com/)
# Differences reveal UA-based behavior changes
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| WAF bypass via bot UA | Don't whitelist bots entirely; still inspect requests |
| SQLi/XSS via User-Agent | Sanitize UA before storing or displaying |
| Debug mode via UA | Never trigger debug based on client-supplied headers |

---

## Related Notes
- [[02 - X-Forwarded-For]] — another client-supplied header
- [[Module 36 - WAF Bypass]] — WAF evasion techniques
- [[Module 01 - SQL Injection]] — SQLi via stored User-Agent
- [[Module 02 - XSS]] — stored XSS via User-Agent in logs
