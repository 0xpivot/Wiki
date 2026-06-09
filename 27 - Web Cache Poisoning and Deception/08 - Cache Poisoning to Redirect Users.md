---
tags: [vapt, cache, infrastructure, advanced]
difficulty: advanced
module: "27 - Web Cache Poisoning and Deception"
topic: "27.08 Cache Poisoning to Redirect Users"
---

# 27.08 — Cache Poisoning to Redirect Users

## What is it?
**Cache Poisoning to Redirect Users** is an attack where an attacker manipulates unkeyed HTTP headers to trick the backend server into generating an HTTP `301 Moved Permanently` or `302 Found` redirect to a malicious external site. 

Because the cache saves this redirect response, the cache becomes a permanent trap. Any legitimate user who navigates to the poisoned URL (like the homepage of a bank) will not see the bank's website; instead, their browser will instantly hit the cache, receive the 301 Redirect, and seamlessly forward them to the attacker's phishing site.

This is highly effective because it requires zero interaction from the victim other than visiting a website they already trust. 

Think of it like changing the street signs on a highway. The Department of Transportation (Backend) normally has a sign pointing to "Downtown." You sneak out at night and paint over it to point to "Bandit Country" (Unkeyed Input). The Highway Patrol (Cache) takes a photo of the new sign and prints it in every GPS map update. Now, every driver (Victims) who tries to go Downtown is automatically routed straight into Bandit Country.

## ASCII Diagram
```text
================================================================================
                    POISONING TO REDIRECT USERS
================================================================================

[1. Attacker Discovers Redirect Logic]
The application redirects HTTP traffic to HTTPS, but builds the HTTPS URL
using the unkeyed `X-Forwarded-Host` header.

[2. Attacker Sends Payload]
GET /login HTTP/1.1
Host: mybank.com
X-Forwarded-Proto: http
X-Forwarded-Host: mybanc.com/phishing   <-- EVIL DOMAIN!

[3. Backend Generates Redirect]
Backend sees HTTP, so it generates a redirect. It uses the XFH header.
Response:
HTTP/1.1 301 Moved Permanently
Location: https://mybanc.com/phishing/login

[4. Cache Stores the Redirect]
Cache Key: GET /login | mybank.com
(Cache saves the 301 response).

[5. The Mass Redirection Event]
Legitimate users type `mybank.com/login` into their browsers.
The Cache instantly serves the 301 Redirect.
Users are seamlessly taken to the phishing site!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify application features that generate redirects. Common locations include:
     - Root directory redirects (e.g., `/` redirects to `/en/home`).
     - HTTP to HTTPS forced redirects.
     - Login page redirects (e.g., `/login?next=/dashboard`).
     - "Trailing slash" redirects (e.g., `/about` redirects to `/about/`).
  2. Send requests to these endpoints with unkeyed headers (`X-Forwarded-Host`, `X-Original-URL`, `X-Rewrite-URL`, `Host` if the secondary Host header is unkeyed).
  3. Observe the `Location` header in the response. If your injected domain appears in the `Location` header, the redirect logic is vulnerable.
  4. Ensure the HTTP status code is cacheable (301s are usually cached by default, 302s might require specific `Cache-Control` headers from the backend).

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a "trailing slash" redirect.
  1. You notice that navigating to `GET /dashboard` (no slash) causes the backend to redirect to `GET /dashboard/` (with slash).
  2. Send the request with an unkeyed host header:
     ```http
     GET /dashboard HTTP/1.1
     Host: target.com
     X-Forwarded-Host: evil.com
     ```
  3. The backend responds:
     ```http
     HTTP/1.1 301 Moved Permanently
     Location: https://evil.com/dashboard/
     ```
  4. Strip your cachebuster, time the cache expiration, and send the payload to the live `/dashboard` URL.
  5. The cache saves the 301 Redirect. Every user clicking a link to `/dashboard` is now sent to `evil.com`.

- **Actual payloads:**
  **Exploiting Double Host Headers:**
  Sometimes, edge proxies take the first Host header, but the internal routing takes the second.
  ```http
  GET / HTTP/1.1
  Host: target.com
  Host: evil.com
  ```
  *(If the proxy uses `target.com` as the Cache Key, but the backend uses `evil.com` to generate the 301 HTTP->HTTPS redirect, the cache is poisoned).*

## Real-World Example
A security researcher found a severe vulnerability in a default configuration of the Symfony PHP framework. Symfony used the `X-Forwarded-Host` header to generate absolute URLs for routing. The researcher targeted a company's main marketing page `/promo`. The page had logic that redirected users to `/promo/2024`. By sending `X-Forwarded-Host: attacker.com`, the researcher caused the backend to generate `Location: https://attacker.com/promo/2024`. Cloudflare cached this 301 redirect. The attacker successfully hijacked the entire promotional campaign, redirecting all marketing traffic to their own server.

## How to Fix It
- **Developer remediation:**
  1. **Hardcoded Base URLs:** Never use client-provided headers to construct the domain portion of a `Location` redirect header. Use a relative redirect (`Location: /dashboard/`) or an absolute URL built from a trusted environment variable (`Location: https://www.target.com/dashboard/`).
  2. **Vary Headers:** If the application requires multi-tenant routing based on `X-Forwarded-Host`, it MUST return `Vary: X-Forwarded-Host` so the cache maintains separate keys for separate domains.
  3. **Strip Headers at Edge:** The CDN or WAF should be configured to strip `X-Forwarded-Host` and `X-Forwarded-Scheme` if they originate from the public internet.

## Chaining Opportunities
- This vuln + Phishing → The ultimate goal of redirecting traffic is to harvest credentials on a look-alike domain.
- This vuln + [[16.03 OAuth Misconfigurations (Implicit Flow)]] → Redirecting the OAuth callback URL to steal the victim's access token.

## Related Notes
- [[27.03 Cache Poisoning via X-Forwarded-Host]]
- [[27.04 Cache Poisoning via X-Forwarded-Scheme]]
