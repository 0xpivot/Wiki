---
tags: [vapt, cache, data-exfiltration, critical]
difficulty: advanced
module: "27 - Web Cache Poisoning and Deception"
topic: "27.09 Web Cache Deception Attack"
---

# 27.09 — Web Cache Deception Attack

## What is it?
While Web Cache *Poisoning* tricks the cache into saving the *attacker's* malicious payload, **Web Cache Deception** tricks the cache into saving the *victim's* highly sensitive personal data.

This attack relies on a discrepancy between how the Cache Server and the Backend Server parse URL extensions. 
- The **Cache Server** is usually configured to aggressively cache static assets by looking at the file extension (e.g., "Always cache `.css`, `.js`, and `.png` files for 24 hours").
- The **Backend Server** (often a modern framework like Django or Spring) is configured with flexible routing. If a user requests `/profile/settings.png`, the Backend might say, "I don't know what `.png` is, I'll just ignore it and route the user to `/profile/settings`."

**The Attack:** The attacker sends the victim a link: `https://target.com/profile/settings/nonexistent.js`.
The victim clicks the link. Their browser sends their session cookies to the server.
The Backend ignores the `/nonexistent.js` part, processes the request as `/profile/settings`, and generates HTML containing the victim's API keys, email, and credit card data.
The Cache Server sees the response from the Backend. It looks at the URL: `/profile/settings/nonexistent.js`. It says: "Oh, a `.js` file! I am configured to cache `.js` files for everyone!" It saves the victim's private HTML under that public URL.
The attacker immediately navigates to `https://target.com/profile/settings/nonexistent.js` and downloads the victim's cached data.

Think of it like a bank teller (Backend) and a security guard (Cache). You want to see someone else's bank statement. You hand your friend an empty folder labeled "Public Newsletter" and say, "Go ask the teller to put your bank statement in here." Your friend does. As your friend walks out, the security guard sees the folder labeled "Public Newsletter", takes a photocopy of it, and pins it to the public bulletin board. You walk up to the bulletin board and read their bank statement.

## ASCII Diagram
```text
================================================================================
                    WEB CACHE DECEPTION ATTACK
================================================================================

[1. The Setup]
Attacker sends a malicious link to the Victim:
`https://bank.com/api/account_details/fake.css`

[2. Victim Clicks the Link]
Victim's Browser sends:
GET /api/account_details/fake.css HTTP/1.1
Cookie: session=VICTIMS_SECRET_TOKEN

[3. Backend Routing (Flexible)]
Backend: "I don't care about /fake.css. The route is /api/account_details."
Backend generates the JSON containing the Victim's SSN and Balance.

[4. Cache Evaluation (Extension-Based)]
Cache sees the response. It checks the URL: `/api/account_details/fake.css`.
Cache: "This is a .css file! CSS is public and static. I will cache this!"
Cache saves the Victim's JSON data under the key: `/api/account_details/fake.css`.

[5. The Exfiltration]
Attacker navigates to `https://bank.com/api/account_details/fake.css`.
The Cache serves the Victim's JSON data to the Attacker!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify endpoints that return sensitive, authenticated user data (e.g., `/api/user`, `/profile`, `/settings`).
  2. Append a static file extension to the URL (e.g., `/api/user/test.css`, `/api/user.js`, `/profile;test.png`).
  3. Send the request (while logged in as User A).
  4. Did the backend return the sensitive data anyway, ignoring the extension? If it returned a 404, the routing is strict, and the attack fails. If it returned the data, proceed.
  5. Check the HTTP response headers. Look for `X-Cache: hit` or `Cache-Control: max-age=...`. If the response was cached, you have a Web Cache Deception vulnerability.
  6. Confirm by logging in as User B (or an unauthenticated browser) and visiting that exact same URL with the extension. If you see User A's data, the vulnerability is verified.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Find the URL structure that triggers the deception (e.g., path parameters like `/profile/id=1.css`, matrix parameters like `/profile;x.png`, or simple appends like `/profile/anything.js`).
  2. Craft the deceptive URL.
  3. Force the victim to visit the URL. You can do this by embedding an invisible image tag on a site you control: `<img src="https://target.com/profile/keys.png">`.
  4. As soon as the victim's browser attempts to load the image, their data is cached on the target server.
  5. You (the attacker) run a script that constantly polls `https://target.com/profile/keys.png`. Once the victim triggers the cache, your script downloads their API keys.

## Real-World Example
In 2017, Omer Gil published the original research on Web Cache Deception, demonstrating it against PayPal. If a user navigated to `https://www.paypal.com/myaccount/home/attack.css`, the PayPal backend completely ignored the `attack.css` string and returned the user's main dashboard HTML (containing their full name, email, and transaction history). The Akamai CDN sitting in front of PayPal saw the `.css` extension and cached the HTML. Gil demonstrated that by sending this link to a victim, he could read their entire PayPal dashboard.

## How to Fix It
- **Developer remediation:**
  1. **Strict Routing:** The backend framework should return a `404 Not Found` or `400 Bad Request` if a URL contains an unrecognized or invalid file extension. Do not gracefully ignore `/fake.css`.
  2. **Cache Configuration:** The caching layer should not base its caching decisions purely on the URL string extension. It should also respect the `Content-Type` header returned by the backend (e.g., "Do not cache this `.css` URL because the backend returned `Content-Type: application/json`").
  3. **Cache-Control Headers:** Ensure that all endpoints returning sensitive data explicitly set `Cache-Control: no-store, private` in the HTTP response headers. The CDN must be configured to strictly obey backend `Cache-Control` directives.

## Chaining Opportunities
- This vuln + Phishing/Social Engineering → To force the victim to request the URL.
- This vuln + CSRF (Cross-Site Request Forgery) → Using `<img>` or `<script>` tags to force the victim's browser to make the request silently.

## Related Notes
- [[27.01 What is Web Caching?]]
- [[27.02 Cache Keys and Unkeyed Inputs]]
