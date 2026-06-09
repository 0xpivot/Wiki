---
tags: [vapt, cache, infrastructure, intermediate]
difficulty: intermediate
module: "27 - Web Cache Poisoning and Deception"
topic: "27.05 Cache Poisoning via Unkeyed Headers"
---

# 27.05 — Cache Poisoning via Unkeyed Headers

## What is it?
While `X-Forwarded-Host` and `X-Forwarded-Scheme` are the most common vectors for Web Cache Poisoning, they are not the only ones. Many applications rely on other obscure or custom HTTP headers to alter the backend's response. If these headers are treated as **Unkeyed Inputs** by the caching layer, they can be used to poison the cache.

Some common unkeyed headers include:
- `X-Original-URL` or `X-Rewrite-URL`: Used to override the requested URL path.
- `User-Agent`: Sometimes unkeyed, but used by the backend to serve mobile vs. desktop specific HTML.
- `Cookie`: If the cache ignores the session cookie, but the backend reflects data from it.
- Custom headers like `X-Language`, `X-Theme`, or internal headers specific to the target company.

Think of it like a personalized license plate factory. The factory manager (Cache) sorts orders only by the state (The Key). You order a license plate for California and put a secret post-it note on the order saying "Actually, print 'HACKED' on all plates today." (Unkeyed Header). The factory manager doesn't read the post-it, but the guy stamping the metal (Backend) does. Because the manager grouped all California orders together, every driver in California receives a plate that says 'HACKED'.

## ASCII Diagram
```text
================================================================================
                    POISONING VIA UNKEYED HEADERS
================================================================================

[1. Attacker Discovers an Unkeyed Header]
GET / HTTP/1.1
Host: target.com
X-Original-URL: /admin               <-- Changes the backend route!

[2. Backend Processes X-Original-URL]
Backend says: "Even though the request is for '/', the X-Original-URL says '/admin'.
I will return the Admin login page."

[3. Cache Saves the Response]
Cache says: "I will save this response for the Key: GET / | target.com"
(The cache completely ignores the X-Original-URL header).

[4. Victim Requests the Homepage]
GET / HTTP/1.1
Host: target.com

[5. Cache Serves Poisoned Content]
Cache serves the Admin login page to the regular user trying to access the homepage!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Use Burp Suite's **Param Miner** extension.
  2. Right-click a request -> `Extensions` -> `Param Miner` -> `Guess headers`.
  3. Param Miner will automatically try thousands of common and obscure headers.
  4. Look for the "Unkeyed Header found" alert in the Issues tab.
  5. Once identified, manually test what the header actually *does* to the backend response. Does it change the HTML? Does it trigger an error? Does it cause a redirect?

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit the `X-Original-URL` header to cause a localized Denial of Service (DoS) or defacement.
  1. Target is a standard e-commerce site. You find that `X-Original-URL` is unkeyed.
  2. Send a request to a highly visited page with a cachebuster:
     `GET /products/shoes?cb=1 HTTP/1.1`
     `X-Original-URL: /does-not-exist-12345`
  3. The backend processes the `X-Original-URL` and returns a `404 Not Found` page containing an error message.
  4. The cache saves the `404` response under the key for `/products/shoes?cb=1`.
  5. **Poison the Live Cache:** Remove the cachebuster and send the payload against the live URL. Wait for the cache to expire.
  6. **Impact:** The cache saves the `404 Not Found` response for the main shoes page. Every customer who clicks on "Shoes" gets a 404 error instead of the product catalog.

- **Actual payloads:**
  **Injecting XSS via a custom unkeyed language header:**
  ```http
  GET / HTTP/1.1
  Host: vulnerable.com
  X-Custom-Language: en"><script>alert(1)</script>
  ```
  *(If the backend reflects this into `<html lang="en"><script>alert(1)</script>">` and the cache ignores the `X-Custom-Language` header, the cache is poisoned).*

## Real-World Example
A bug bounty hunter found that a major streaming service used an unkeyed `X-Country-Code` header to serve geographically restricted content. By sending `GET /movies/blockbuster` with `X-Country-Code: NORTH_KOREA`, the backend returned a custom "Content Not Available in Your Region" error page. Because the cache ignored this header, the hunter was able to poison the cache for the entire US region, causing millions of American users to receive the North Korean geo-block error message when trying to watch the movie.

## How to Fix It
- **Developer remediation:**
  1. **Strict Input Validation:** The backend should not implicitly trust obscure HTTP headers (like `X-Original-URL` or `X-Rewrite-URL`) unless they are required for internal routing. If they are not required, strip them at the Edge/WAF layer.
  2. **Add to Cache Key:** If a custom header (like `X-Custom-Language`) is genuinely needed to generate localized HTML, the backend must return the `Vary: X-Custom-Language` header in the response. This forces the cache server to include the language in the Cache Key, preventing users with different headers from receiving the same cached copy.

## Chaining Opportunities
- This vuln + [[27.08 Cache Poisoning to Redirect Users]] → Using unkeyed routing headers to force 301 Redirects.
- This vuln + [[27.07 Cache Poisoning to Deliver XSS]] → Finding obscure headers that reflect into the DOM without sanitization.

## Related Notes
- [[27.02 Cache Keys and Unkeyed Inputs]]
- [[27.06 Cache Poisoning via Fat GET]]
