---
tags: [vapt, cache, infrastructure, intermediate]
difficulty: intermediate
module: "27 - Web Cache Poisoning and Deception"
topic: "27.01 What is Web Caching?"
---

# 27.01 — What is Web Caching?

## What is it?
**Web Caching** is a performance optimization technique used to reduce server load, decrease latency, and improve the user experience. Instead of the back-end application server generating the exact same response for thousands of users requesting the same page, a cache server (usually a CDN like Cloudflare, Fastly, or a reverse proxy like Varnish) sits in front of the application.

When the first user requests a page (e.g., `GET /index.html`), the cache forwards the request to the backend. The backend generates the HTML and sends it back. The cache saves a copy of this HTML (it "caches" it) and sends it to the user. When the *next* 10,000 users request `GET /index.html`, the cache immediately serves the saved HTML copy. The backend server doesn't even know those 10,000 users exist.

This is highly efficient, but it introduces a massive security risk. If an attacker can somehow trick the backend server into generating a *malicious* response (like a page containing Cross-Site Scripting), and the cache saves that malicious response, the cache will now serve the attacker's payload to the next 10,000 legitimate users. 

This act of tricking the cache into saving a malicious payload is called **Web Cache Poisoning**.

Think of a web cache like a printing press for a newspaper. The journalist (Back-End) writes an article. The printing press (Cache) prints 100,000 copies and hands them to the delivery boys. If a malicious intern breaks into the journalist's office and changes the headline to a scam link right before the press starts, the printing press will faithfully print 100,000 copies of the scam and deliver them to every house in the city. Web Cache Poisoning is the act of poisoning the master copy.

## ASCII Diagram
```text
================================================================================
                        THE WEB CACHING LIFECYCLE
================================================================================

[Normal Operation]
User A ──> GET /image.png ──> [ CACHE SERVER ] ──(MISS)──> [ BACK-END SERVER ]
                                    │                           │
User A <── [Returns image.png] <──(SAVES COPY)<── [Returns image.png]
                                    
User B ──> GET /image.png ──> [ CACHE SERVER ] ──(HIT!)
                                    │
User B <── [Returns image.png] <────┘

[Cache Poisoning Operation]
Hacker ──> GET /index ──> [ CACHE SERVER ] ──(MISS)──> [ BACK-END SERVER ]
           + Evil Header                                 (Processes Evil Header)
                                    │                           │
Hacker <── [Returns Evil HTML] <──(SAVES COPY)<── [Returns Evil HTML]

Victim ──> GET /index ──> [ CACHE SERVER ] ──(HIT!)
                                    │
Victim <── [Returns Evil HTML] <────┘   <-- VICTIM IS HACKED!
================================================================================
```

## How to Find It
- **Manual steps:**
  You don't "exploit" caching itself; you exploit the interaction between caching and other vulnerabilities. To know if caching is happening, look at the HTTP response headers.
  - `X-Cache: hit` (The response came from the cache)
  - `X-Cache: miss` (The cache didn't have it, so it fetched it from the backend)
  - `Cache-Control: max-age=3600` (The cache will hold this file for 3600 seconds)
  - `Age: 45` (This cached copy is 45 seconds old)
  - `CF-Cache-Status: HIT` (Cloudflare specific)

- **Tool commands with flags explained:**
  **Param Miner (Burp Suite Extension):**
  This tool is essential for finding the "unkeyed inputs" (hidden headers) needed to execute a cache poisoning attack.
  - Right-click a request -> `Extensions` -> `Param Miner` -> `Guess headers`. 
  - Param Miner will silently brute-force thousands of HTTP headers in the background to see if the backend server reacts to any of them.

## How to Exploit It
- **Step-by-step walkthrough:**
  (Exploitation details are covered in subsequent notes. The general flow is:)
  1. **Identify the Cache:** Confirm the target uses a cache (look for `X-Cache` headers).
  2. **Find an Unkeyed Input:** Find an HTTP header or parameter that changes the backend's response but is *ignored* by the cache.
  3. **Elicit a Malicious Response:** Use the unkeyed input to make the backend generate an XSS payload or an open redirect.
  4. **Poison the Cache:** Send the payload repeatedly until the cache expires its old copy and saves your new, malicious copy.
  5. **Verify:** Load the page in a clean browser (no attacker headers). If the malicious payload executes, the cache is poisoned.

## Real-World Example
A classic example is a website that dynamically generates a "Back to Top" link based on the HTTP `Host` header. A user sends `Host: target.com`, and the page generates `<a href="https://target.com/top">`. If an attacker sends `Host: evil.com`, the page generates `<a href="https://evil.com/top">`. If the cache server is configured to *ignore* the `Host` header when deciding what to cache, the attacker's `evil.com` link gets saved as the master copy for the homepage. When legitimate users visited the site, they click "Back to Top" and are redirected to a phishing page.

## How to Fix It
- **Developer remediation:**
  1. **Don't Trust Unkeyed Inputs:** The backend application must never use HTTP headers (like `X-Forwarded-Host`, `X-Original-URL`, or arbitrary headers) to generate content if those headers are not part of the Cache Key.
  2. **Disable Caching for Dynamic Content:** If a page's content changes based on who is asking or what headers they send, that page should not be cached. Return `Cache-Control: no-store, no-cache`.

## Chaining Opportunities
- This vuln + [[24.01 What is Open Redirect?]] → Poison the cache to redirect all users on the homepage to a phishing site.
- This vuln + [[26.06 Response Queue Poisoning]] → Use HTTP Request Smuggling to trick the cache into saving the wrong response entirely.

## Related Notes
- [[27.02 Cache Keys and Unkeyed Inputs]]
- [[27.07 Cache Poisoning to Deliver XSS]]
