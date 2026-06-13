---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.05 Browser Cache Attacks"
---

# Browser Cache Attacks

## 1. Executive Summary

Browser Cache Attacks represent a highly impactful class of vulnerabilities that exploit the complex, often misunderstood interactions between web applications and intermediate caching infrastructure (such as Content Delivery Networks [CDNs], Reverse Proxies like Varnish or Nginx, and the user's internal browser cache). 

Caching is fundamentally designed to optimize web performance by temporarily storing and serving HTTP responses without repeatedly querying the backend server. However, when caching logic becomes desynchronized with the backend application's routing logic, attackers can manipulate these mechanisms. This discrepancy facilitates two primary attack paradigms: **Web Cache Deception (WCD)**, which results in the massive exfiltration of sensitive user data, and **Web Cache Poisoning (WCP)**, which allows an attacker to store malicious payloads (like XSS) on the CDN, infecting all subsequent legitimate users.

## 2. Conceptual Foundation: The Cache Key and Unkeyed Inputs

To master cache attacks, one must deeply understand how a cache decides whether to serve a stored response (a "Cache Hit") or fetch fresh data from the server (a "Cache Miss").

**The Cache Key:**
Caches identify distinct resources using a "Cache Key." Typically, this key comprises the request line and the `Host` header:
`Cache Key = [Method] + [Scheme] + [Host] + [URI Path] + [Query String]`

**Unkeyed Inputs:**
Any component of the HTTP request that is *not* included in the Cache Key is considered an "Unkeyed Input." 
Common unkeyed inputs include:
- HTTP Headers (`X-Forwarded-Host`, `X-Forwarded-Scheme`, `User-Agent`, `Origin`)
- Certain query parameters (e.g., UTM tracking codes are often explicitly unkeyed by CDNs to improve cache hit rates).

If an application alters its HTTP response based on an *unkeyed input*, the cache will store that altered response and serve it to everyone requesting the same Cache Key, regardless of whether they sent the unkeyed input. This is the genesis of Cache Poisoning.

## 3. Web Cache Deception (WCD)

Web Cache Deception relies on tricking a victim into authenticated navigation to a URL that forces the cache to store their private, dynamic data as if it were a public, static asset.

### The Path Confusion Mechanism
WCD exploits routing discrepancies between the CDN and the Backend.
Many web frameworks (like Django, Ruby on Rails, or custom PHP) implement flexible routing. If a user requests `/api/profile/unknown.css`, the backend might ignore the `.css` extension, match the `/api/profile` route, and return the user's highly sensitive JSON data.

However, the CDN edge server sees the `.css` extension. CDNs are heavily optimized to cache static file extensions aggressively. The CDN observes the response from the backend, caches the private profile data, and associates it with the public `/api/profile/unknown.css` Cache Key.

### Execution Flow (WCD)
1. **Attacker:** Sends a malicious link to the victim: `https://bank.com/dashboard/style.css`.
2. **Victim:** Clicks the link. Their browser includes their authenticated session cookie.
3. **CDN:** Sees a request for `.css`. It's a Cache Miss. Forwards to the backend.
4. **Backend:** Ignores `style.css`, processes the `/dashboard` route, and returns the victim's private account details.
5. **CDN:** Receives the response, caches it under the key `/dashboard/style.css`, and serves it to the victim.
6. **Attacker:** Anonymously requests `https://bank.com/dashboard/style.css`. The CDN serves the cached victim's data.

## 4. Web Cache Poisoning (WCP)

While WCD steals data from a specific victim, Web Cache Poisoning (WCP) is an infrastructure-wide attack. The attacker manipulates an HTTP request to generate a malicious response from the backend, forcing the cache to save it and serve it to all users.

### Manipulating Unkeyed Headers
Consider an application that dynamically builds URLs using the `X-Forwarded-Host` header.
```html
<script src="https://[X-Forwarded-Host_Value]/assets/main.js"></script>
```
If this header is *unkeyed* by the CDN, the attacker can execute the following attack:

### Execution Flow (WCP)
1. **Attacker:** Sends a request to the target homepage.
   ```http
   GET / HTTP/1.1
   Host: target.com
   X-Forwarded-Host: evil-server.com
   ```
2. **Backend:** Generates the HTML, reflecting the malicious host: `<script src="https://evil-server.com/assets/main.js"></script>`.
3. **CDN:** Caches this malicious HTML under the key `target.com/`.
4. **Legitimate User:** Visits `target.com/` normally.
5. **CDN:** Serves the poisoned cache. The user's browser executes the attacker's JavaScript, resulting in mass Cross-Site Scripting (XSS).

## 5. ASCII Diagram: Cache Deception vs. Cache Poisoning

```text
========================================================================
[ ATTACK 1: WEB CACHE DECEPTION (Data Exfiltration) ]
========================================================================
   [ Attacker ] --- Sends link: /profile/fake.js ---> [ Victim ]
                                                           |
                                                      (Clicks Link)
                                                           |
   [ CDN Cache ] <-----------------------------------------+
        |  (Miss: Forwards request to Backend)
        v
   [ Backend ] --> Routes to /profile, returns Victim Data (JSON)
        |
   [ CDN Cache ] --> Caches Victim Data as "fake.js" (Publicly Accessible!)
        |
   [ Attacker ] ---> Requests /profile/fake.js ---> Gets Victim's Data!


========================================================================
[ ATTACK 2: WEB CACHE POISONING (Mass Payload Delivery) ]
========================================================================
   [ Attacker ]
   GET /home
   X-Forwarded-Host: evil.com
        |
   [ CDN Cache ] <--- (Unkeyed Header Ignored in Cache Key)
        |
   [ Backend ] -----> Returns <script src="http://evil.com/xss.js">
        |
   [ CDN Cache ] ---> Saves malicious HTML for the key "/home"
        |
   [ Normal User A, B, C ] ---> GET /home (No malicious headers)
        |
   [ CDN Cache ] ---> Serves Poisoned HTML ---> MASS XSS EXECUTED!
```

## 6. Advanced Poisoning Techniques

### Parameter Cloaking (DOM-Based Cache Poisoning)
Sometimes, parameters are unkeyed to improve cache ratios (e.g., `?utm_campaign=sale`). If the application reflects this unkeyed parameter into the DOM, an attacker can achieve DOM-XSS.
`GET /page?utm_campaign="><script>alert(1)</script>`
The CDN caches the page at `/page`. When users visit `/page`, the cached payload executes.

### Cache Poisoned Denial of Service (CPDoS)
Instead of injecting XSS, the attacker forces the backend to return an error (e.g., a 400 Bad Request) by sending an oversized header or an invalid method override. The cache stores the error page. Legitimate users requesting the homepage are subsequently locked out, receiving the cached error page until the cache Time-To-Live (TTL) expires.

## 7. Caching Server Behaviors & Tooling

Different caching layers behave differently:
- **Cloudflare:** Aggressively caches specific file extensions by default. Highly susceptible to Web Cache Deception if backend routing is loose.
- **Varnish:** Extremely customizable via Varnish Configuration Language (VCL). Vulnerabilities often stem from custom VCL scripts that improperly strip headers before cache key generation.
- **Tooling:** **Param Miner** (a Burp Suite extension) is the industry standard for discovering unkeyed inputs. It systematically injects thousands of headers and query parameters, analyzing cache hits/misses and response reflections to identify poisonable inputs.

## 8. Defensive Posture and Remediation

1. **Align Cache and Backend Configurations (The Golden Rule):** The CDN and the application must treat routes identically. If the backend serves a dynamic page, the CDN must never treat it as a static asset, regardless of the file extension.
2. **Strict Cache-Control Headers:** The backend application must explicitly dictate caching behavior using HTTP headers. Sensitive endpoints must return:
   `Cache-Control: private, no-cache, no-store, must-revalidate`
3. **Normalize Inbound Requests:** The edge proxy or WAF should strip or strictly validate all unnecessary headers (such as `X-Forwarded-Host`, `X-Original-URL`, `X-Rewrite-URL`) before they reach the backend application.
4. **Key All Influential Inputs:** If the application alters its response based on a specific header (e.g., `Accept-Language` or `User-Agent`), that header must be included in the Cache Key (often achieved using the `Vary` header).
5. **Disable Caching by Extension:** Configure CDNs to cache based on content-type or specific, explicit directory paths (e.g., `/static/*`), rather than relying on regex matching of file extensions across the entire application map.

## 9. Chaining Opportunities

- **Web Cache Poisoning + Cross-Site Scripting (XSS):** Elevating reflected XSS to a stored-like mass exploitation vector without requiring database write access.
- **Web Cache Poisoning + Open Redirect:** Poisoning the cache to redirect all traffic destined for a legitimate endpoint to an attacker-controlled phishing domain.
- **Web Cache Deception + BOLA/IDOR:** Exfiltrating sensitive object data by forcing the cache to store it under an attacker-accessible URI, circumventing standard authorization checks on subsequent requests.

## 10. Related Notes

- [[07 - Cross-Site Scripting (XSS)]]
- [[01 - HTTP Parameter Pollution HPP]]
- [[15 - Host Header Injection]]
- [[20 - Server-Side Request Forgery (SSRF)]]
- [[09 - HTTP Request Smuggling]]
