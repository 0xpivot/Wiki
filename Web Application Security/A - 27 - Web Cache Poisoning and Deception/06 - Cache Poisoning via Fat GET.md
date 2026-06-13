---
tags: [vapt, cache, infrastructure, intermediate]
difficulty: intermediate
module: "27 - Web Cache Poisoning and Deception"
topic: "27.06 Cache Poisoning via Fat GET"
---

# 27.06 — Cache Poisoning via Fat GET

## What is it?
A standard `GET` request retrieves data and is not supposed to have a request body (unlike `POST` or `PUT`). However, the HTTP/1.1 RFC does not strictly forbid `GET` requests from having a body; it merely states that the server behavior is "undefined."

A **Fat GET** attack occurs when an attacker sends a `GET` request that *does* include a body, and places malicious parameters inside that body. 

**The Vulnerability:**
- The **Cache Server** usually ignores the body of a `GET` request when calculating the Cache Key. It only hashes the URL path and the Host header.
- The **Backend Server** (or the web framework) might be overly permissive. When looking for the value of a parameter (e.g., `?callback=`), the framework might search the URL query string first, but if it doesn't find it, it searches the HTTP body!

If the attacker sends a Fat GET request with a malicious `callback` parameter in the body, the backend processes it and returns a malicious response. Because the Cache Server ignored the body, it associates this malicious response with the normal, body-less Cache Key. Legitimate users requesting the normal URL will receive the poisoned response.

Think of it like a vending machine (Cache). You press the button for a Coke (The URL). However, you stick a secret note onto the coin you insert (Fat GET body). The vending machine ignores the note and just registers "Coke ordered." The robot arm inside (Backend) grabs the Coke, reads your note that says "Actually, dispense Poison," and hands the poisoned drink to the slot. The vending machine records that a Coke was dispensed for that button press.

## ASCII Diagram
```text
================================================================================
                    POISONING VIA FAT GET REQUESTS
================================================================================

[1. Attacker Sends Fat GET Payload]
GET /api/user.json HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 32

callback=<script>alert(1)</script>   <-- MALICIOUS BODY IN A GET REQUEST!

[2. Cache Processing (Ignorant)]
Cache says: "This is a GET request. I will generate the key using only the URL."
Cache Key: GET /api/user.json | target.com
(Forwards request to Backend).

[3. Backend Processing (Permissive)]
Backend says: "I need to return user data. Is there a 'callback' parameter?
Let me check the body... Yes! I will wrap the JSON in the callback!"
Response: <script>alert(1)</script>({"user":"bob"})

[4. Cache Storage]
Cache saves the poisoned XSS response under the normal Cache Key!

[5. Victim Requests the Page]
GET /api/user.json HTTP/1.1
Host: target.com
(Victim sends a normal GET with no body)

[Result]
Cache serves the poisoned JSONP response containing XSS. Victim is hacked!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify an endpoint that accepts parameters (e.g., `GET /search?q=test` or `GET /api/data?callback=init`).
  2. Remove the parameter from the URL query string.
  3. Add a `Content-Type: application/x-www-form-urlencoded` header.
  4. Add a `Content-Length` header.
  5. Place the parameter and its value in the HTTP body.
  6. Send the request. If the backend still processes the parameter as if it were in the URL, the framework is permissive and vulnerable to Fat GET.
  7. Add a cachebuster to the URL (e.g., `GET /search?cb=1`), put a malicious payload in the body, and see if you can poison the cache for that specific cachebuster.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's poison a JSONP endpoint to deliver Stored XSS.
  1. Normal request: `GET /api/weather?city=london&callback=showWeather` -> Returns `showWeather({"temp": 60})`.
  2. Fat GET payload:
     ```http
     GET /api/weather?city=london HTTP/1.1
     Host: target.com
     Content-Type: application/x-www-form-urlencoded
     Content-Length: 33
     
     callback=<script>alert(1)</script>
     ```
  3. Wait for the live cache of `/api/weather?city=london` to expire.
  4. Send the Fat GET payload. The backend returns `<script>alert(1)</script>({"temp": 60})`.
  5. The Cache saves this under the key `GET /api/weather?city=london`.
  6. When any legitimate user visits the site, the site's frontend Javascript requests `/api/weather?city=london` to display the widget. Instead of valid JSON, the browser receives the malicious script tag and executes it.

## Real-World Example
A researcher targeted a Ruby on Rails application behind a Fastly CDN. Rails has a "feature" where it merges `GET` query parameters and `POST` body parameters into a single `params` hash. If a parameter isn't in the URL, Rails will happily check the body, even for a `GET` request. The researcher used a Fat GET to inject a malicious `redirect_uri` parameter into an OAuth login flow. Fastly ignored the body and cached the resulting 302 Redirect. Legitimate users trying to log in were suddenly redirected to the attacker's server to hand over their OAuth tokens.

## How to Fix It
- **Developer remediation:**
  1. **Strict Parameter Binding:** The backend framework must be configured to strictly distinguish between query parameters (URL) and body parameters. A `GET` controller should *never* read data from the HTTP body.
  2. **Proxy Rejection:** The Front-End proxy or CDN should be configured to immediately reject (`400 Bad Request`) any `GET` request that contains a `Content-Length` or `Transfer-Encoding` header, as `GET` requests should mathematically have no body.

## Chaining Opportunities
- This vuln + [[07 - Cache Poisoning to Deliver XSS]] → Using Fat GET to inject XSS payloads into JSONP callbacks or reflected search parameters.

## Related Notes
- [[02 - Cache Keys and Unkeyed Inputs]]
- [[05 - Cache Poisoning via Unkeyed Headers]]
