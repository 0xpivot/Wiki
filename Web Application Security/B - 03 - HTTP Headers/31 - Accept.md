---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.31 Accept — Content Negotiation, MIME Sniffing"
---

# 03.31 — Accept

## What is it?

The `Accept` header tells the server which content types the client can handle. The server uses content negotiation to choose the response format. Manipulating `Accept` can trigger different code paths, cause parser confusion, and sometimes bypass WAF rules or access controls based on content type.

---

## Format

```
Accept: text/html                    → only HTML
Accept: application/json             → only JSON
Accept: application/xml              → only XML
Accept: */*                          → anything (browser default)
Accept: text/html, application/json  → prefer HTML, accept JSON
Accept: application/json;q=0.9, text/html;q=0.8  → quality factor
```

---

## Attack 1: Content Type Switching for Parser Confusion

```
API returns JSON normally:
  GET /api/user/1
  Accept: application/json
  → {"id":1,"username":"admin","role":"user"}

ATTACK: Request XML response → trigger XML parser → XXE:
  GET /api/user/1
  Accept: application/xml
  
  → If server returns XML:
  <?xml version="1.0"?>
  <user><id>1</id><username>admin</username></user>
  
  Now inject XXE in any field that becomes XML input!
  This is output format switching → sometimes source of XXE!
```

---

## Attack 2: WAF Bypass via Accept Header

```
WAF inspects request for attack signatures.

BYPASS:
  Some WAFs only deep-inspect specific content types.
  If WAF knows the response will be JSON (Accept: application/json):
  → WAF might skip HTML-specific payload checks!

  OR:
  Accept: application/x-malicious-custom-type
  → WAF may not recognize → falls through to backend!
```

---

## Attack 3: Different Response Behavior

```
Some apps serve different content per Accept:
  Accept: text/html    → full HTML page with CSRF token
  Accept: application/json → JSON response WITHOUT CSRF protection!
  
  ATTACK: Submit state-changing requests with JSON Accept header
  → Might bypass CSRF checks applied only to form-based (HTML) flows!

ALSO TEST:
  Accept: application/javascript  → might get JSONP response!
  JSONP bypasses CORS restrictions (legacy technique)
```

---

## Attack 4: Error Message Differences

```
Accept: application/json → JSON error: {"error":"not found","path":"/admin/users"}
Accept: text/html → HTML error with full stack trace!

→ Change Accept to trigger verbose errors on HTML endpoints!
```

---

## Testing

```bash
# Test XML response (potential XXE surface):
curl -H "Accept: application/xml" https://target.com/api/user/1

# Test for JSONP (old APIs):
curl -H "Accept: application/javascript" https://target.com/api/user?callback=evil

# Get different error format:
curl -H "Accept: text/html" https://target.com/api/notexist -v

# Burp Suite:
# Use Content Negotiation in Repeater:
# Change Accept header → compare responses
# Look for: different status codes, extra data in one format, stack traces
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Different auth per content type | Apply same authorization to all content type variants |
| XML format enabled unnecessarily | Disable XML output if not needed |
| Verbose errors in HTML mode | Standardize error format and verbosity |

---

## Related Notes
- [[19 - Content-Type]] — Content-Type of request body
- [[02.14 - MIME Types and Content-Type]] — MIME types
- [[Module 05 - XXE]] — XXE via content negotiation
