---
tags: [vapt, smuggling, http, advanced]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.01 What is HTTP Request Smuggling?"
---

# 26.01 — What is HTTP Request Smuggling?

## What is it?
**HTTP Request Smuggling** (HRS) is an advanced, critical web vulnerability that arises when the front-end server (like a load balancer, reverse proxy, or API Gateway) and the back-end server disagree about where a single HTTP request ends and the next one begins.

In modern infrastructure, users don't talk directly to the backend application server (like Node.js or Python). They talk to a front-end server (like Nginx, HAProxy, or Cloudflare). To save CPU and network overhead, the front-end server bundles multiple HTTP requests from different users and streams them over a single, long-lived TCP connection to the backend.

To tell the backend where one request stops and another begins, HTTP uses two headers:
1. `Content-Length (CL)`: Specifies the size of the request body in bytes.
2. `Transfer-Encoding (TE)`: If set to `chunked`, it means the body is sent in "chunks," each preceded by its size in hexadecimal, ending with a chunk of size `0`.

The vulnerability occurs when an attacker sends an ambiguous request containing *both* headers, or malformed headers. If the front-end relies on the `Content-Length` but the back-end relies on the `Transfer-Encoding` (or vice-versa), they will parse the exact same stream of bytes differently. 

The attacker crafts a payload where the front-end thinks it's forwarding 1 request, but the back-end reads it as 1.5 requests. That remaining "0.5" (the smuggled request) sits dead in the backend's TCP buffer. When the *next legitimate user* sends their request, the backend attaches it to the dead 0.5 request. The attacker has successfully "smuggled" a hidden request into the pipeline, poisoning the next user's interaction.

Think of it like a shipping container. The front-end is the harbor master who checks the manifest (Content-Length) and says "Okay, 1 container." The backend is the warehouse worker who unloads it by looking at the specific boxes inside (Transfer-Encoding). If the attacker puts a false bottom in the container, the harbor master sees 1 container and lets it through. The warehouse worker unpacks it, finds the false bottom, and realizes there's a hidden, second, highly dangerous package inside that the harbor master never saw.

## ASCII Diagram
```text
================================================================================
                        THE MECHANICS OF SMUGGLING
================================================================================

[Attacker's Malicious HTTP Request]
POST / HTTP/1.1
Host: vulnerable.com
Content-Length: 13
Transfer-Encoding: chunked

0
SMUGGLED

[Front-End Server (Parses Content-Length: 13)]
"I see 13 bytes in the body. I will forward exactly 13 bytes."
(Forwards: "0\r\n\r\nSMUGGLED")
       │
       ▼
[Back-End Server (Parses Transfer-Encoding: chunked)]
"I see chunked encoding. I read '0'. That means the request is OVER!"
"Wait, what is this 'SMUGGLED' text left over in the TCP buffer? I'll 
leave it there and prepend it to the next request that comes in."
       │
[Next Legitimate User sends their request over the same connection]
GET /profile HTTP/1.1
Host: vulnerable.com
       │
       ▼
[Back-End Server combines them!]
SMUGGLEDGET /profile HTTP/1.1
Host: vulnerable.com

[Result: The Back-End throws an error because "SMUGGLEDGET" is not a 
valid HTTP method. The legitimate user receives the error!]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. You need a deep understanding of HTTP RFCs and protocol specifications.
  2. Send requests with both `Content-Length` and `Transfer-Encoding: chunked` headers.
  3. Send requests with malformed headers: `Transfer-Encoding: xchunked`, `Transfer-Encoding : chunked` (with a space), `Transfer-Encoding: chunked\r\n`.
  4. Use a Time-Delay technique (See [[26.11 Detecting Smuggling]]) to observe if the backend hangs while waiting for data.
  5. If the front-end and back-end handle the malformed headers differently, you have the necessary conditions for a smuggling attack.

- **Tool commands with flags explained:**
  **HTTP Request Smuggler (Burp Suite Extension by James Kettle):**
  This is the industry-standard tool for detecting HRS.
  1. Install "HTTP Request Smuggler" from the BApp Store.
  2. Right-click any request -> `Extensions` -> `HTTP Request Smuggler` -> `Smuggle Probe`.
  3. The extension will automatically test dozens of permutations and report if a timeout/discrepancy was found.

## How to Exploit It
- **Step-by-step walkthrough:**
  (Exploitation depends on the specific type of smuggling, covered in subsequent notes. The goal is always the same):
  1. **Identify the Discrepancy:** Figure out if the front-end prefers CL and backend prefers TE (CL.TE) or vice-versa (TE.CL).
  2. **Craft the Prefix:** Write a malicious HTTP request (e.g., `POST /admin/delete_user`).
  3. **Hide the Prefix:** Embed this malicious request inside the body of your carrier request, formatted so that the front-end sees it as "just data", but the backend sees it as "the start of the next HTTP request".
  4. **Fire the Carrier:** Send the request.
  5. **Wait for a Victim:** The next user who uses the application will have their request appended to your prefix. If your prefix was `POST /admin/delete_user HTTP/1.1\r\nHost: target\r\n\r\n`, the backend executes that action using the victim's session cookies!

## Real-World Example
In 2019, James Kettle (albinowax) released groundbreaking research on HTTP Request Smuggling. He demonstrated how this vulnerability affected major corporations like PayPal, Apple, and Slack. In one example, by smuggling a request to a server that handled static images, he was able to poison the response queue. When the next user (a victim) requested their own profile picture, the server responded with the attacker's smuggled request, effectively serving malicious JavaScript instead of a PNG, resulting in a persistent, cache-poisoned Cross-Site Scripting (XSS) attack that compromised thousands of users.

## How to Fix It
- **Developer remediation:**
  1. **HTTP/2 End-to-End:** HTTP/2 completely redesigns how requests are framed. It doesn't use `Content-Length` or `Transfer-Encoding` strings; it uses binary frames with explicit lengths. If you use HTTP/2 from the user all the way to the backend (not just to the load balancer), HRS is impossible.
  2. **Reject Ambiguity:** Configure the front-end server to aggressively reject (400 Bad Request) any HTTP request that contains both a `Content-Length` and a `Transfer-Encoding` header.
  3. **Disable Connection Reuse:** (Not recommended for performance) If the front-end closes the TCP connection to the backend after every single request, smuggled data cannot poison the next user.

## Chaining Opportunities
- This vuln + [[25.13 Function-Level Access Control Bypass]] → Smuggle a request to an admin endpoint. When an actual Admin uses the site, their session cookies are appended to your smuggled request, executing the admin action on your behalf.
- This vuln + [[26.06 Response Queue Poisoning]] → Steal the sensitive data intended for the next user.

## Related Notes
- [[26.02 CL.TE Smuggling]]
- [[26.03 TE.CL Smuggling]]
