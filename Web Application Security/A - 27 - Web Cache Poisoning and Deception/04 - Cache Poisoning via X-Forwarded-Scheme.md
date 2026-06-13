---
tags: [vapt, cache, infrastructure, intermediate]
difficulty: intermediate
module: "27 - Web Cache Poisoning and Deception"
topic: "27.04 Cache Poisoning via X-Forwarded-Scheme"
---

# 27.04 — Cache Poisoning via X-Forwarded-Scheme

## What is it?
`X-Forwarded-Scheme` (or `X-Forwarded-Proto`) is an HTTP header used by load balancers and reverse proxies to tell the backend server what protocol the user originally connected with (HTTP or HTTPS). 

Because the load balancer often terminates the SSL/TLS connection, the traffic between the load balancer and the internal backend server is usually unencrypted plain HTTP. Without the `X-Forwarded-Scheme` header, the backend server would assume *every* request is plain HTTP.

**The Vulnerability:** Many web frameworks are configured to enforce HTTPS. If they receive an HTTP request, they immediately respond with a `301` or `302` redirect, telling the user to go to the `https://` version of the same URL.

If a caching layer is present and treats `X-Forwarded-Scheme` as an **Unkeyed Input**, an attacker can exploit this redirect logic. The attacker sends a request over a secure HTTPS connection, but manually injects `X-Forwarded-Scheme: http`. 

The Backend sees the `http` scheme, assumes the user is on an insecure connection, and generates a 301 Redirect to the HTTPS URL. The Cache Server sees the 301 Redirect, saves it, and associates it with the normal Cache Key. Now, every legitimate user who visits the site (even if they are already using HTTPS!) is served the 301 Redirect back to the exact same HTTPS URL, resulting in an **infinite redirect loop** that effectively takes the website offline (Denial of Service).

## ASCII Diagram
```text
================================================================================
                    POISONING VIA X-FORWARDED-SCHEME (DoS)
================================================================================

[1. Attacker Sends Payload over HTTPS]
GET / HTTP/1.1
Host: target.com
X-Forwarded-Scheme: http               <-- THE LIE

[2. Backend Logic (Enforcing HTTPS)]
Backend says: "Wait, the scheme is HTTP! I must redirect them to HTTPS!"
Response: 
HTTP/1.1 301 Moved Permanently
Location: https://target.com/

[3. Cache Storage]
Cache saves the 301 Redirect under the Cache Key: GET / | target.com

[4. Victim Requests the Page over HTTPS]
GET / HTTP/1.1
Host: target.com

[5. The Infinite Loop]
Cache serves the poisoned 301 Redirect.
Victim's browser goes to: https://target.com/
Victim hits the Cache again.
Cache serves the 301 Redirect again.
Victim's browser goes to: https://target.com/
(ERR_TOO_MANY_REDIRECTS)
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Pick a target endpoint, usually the homepage or a static asset: `GET /style.css?cb=1`.
  2. The connection must be HTTPS.
  3. Inject the header `X-Forwarded-Scheme: http`.
  4. Check the response. If you receive a `301 Moved Permanently` or `302 Found` with a `Location: https://target.com/style.css?cb=1`, the backend is vulnerable.
  5. Remove the `X-Forwarded-Scheme` header, keep the cachebuster, and send it again.
  6. If you *still* receive the 301 Redirect, you have successfully poisoned the cache for that cachebuster.

- **Other Scheme Variations:**
  If `X-Forwarded-Scheme` doesn't trigger the redirect, try:
  - `X-Forwarded-Proto: http`
  - `Front-End-Https: off`
  - `X-Scheme: http`

## How to Exploit It
- **Step-by-step walkthrough:**
  While causing an infinite redirect loop (DoS) is disruptive, a more advanced exploit involves chaining the Scheme header with the Host header to create a **Malicious Redirect**.
  
  Some frameworks build the 301 Redirect URL by combining the `X-Forwarded-Scheme` and the `Host` header (or `X-Forwarded-Host`).
  
  1. Send:
     ```http
     GET / HTTP/1.1
     Host: target.com
     X-Forwarded-Scheme: http
     X-Forwarded-Host: evil.com
     ```
  2. The backend sees `http` and decides to redirect. It builds the HTTPS URL using the `X-Forwarded-Host` value.
  3. The response becomes:
     ```http
     HTTP/1.1 301 Moved Permanently
     Location: https://evil.com/
     ```
  4. The Cache saves this. Now, anyone who visits the homepage is instantly redirected to the attacker's phishing site.

## Real-World Example
A researcher targeted a popular blogging platform. The platform used Varnish Cache and Ruby on Rails. Rails was configured with `force_ssl`. The researcher sent a request to a popular blog post with `X-Forwarded-Proto: http`. Rails immediately generated a 301 redirect back to the HTTPS version of the post. Varnish cached this 301 redirect. For the next 24 hours, anyone who tried to read that blog post received an `ERR_TOO_MANY_REDIRECTS` error in Chrome, completely denying access to the content. 

## How to Fix It
- **Developer remediation:**
  1. **Do not cache Redirects:** Configure the caching layer (CDN/Varnish) to *never* cache 301 or 302 responses that redirect to the exact same domain. 
  2. **Vary Header:** If the backend generates different responses based on the `X-Forwarded-Proto` header, the backend must return `Vary: X-Forwarded-Proto`. This tells the cache to keep HTTP responses and HTTPS responses completely separate.
  3. **Trust Configuration:** Only accept `X-Forwarded-` headers from trusted internal proxy IP addresses. If a request arrives from the public internet containing these headers, the edge proxy should strip them before forwarding to the backend.

## Chaining Opportunities
- This vuln + [[03 - Cache Poisoning via X-Forwarded-Host]] → Combine both headers to turn a DoS attack into an Open Redirect attack.

## Related Notes
- [[01 - What is Web Caching?]]
- [[08 - Cache Poisoning to Redirect Users]]
