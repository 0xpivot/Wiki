---
tags: [vapt, business-logic, rate-limiting, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.12 Rate Limit Bypass for Votes / Likes"
---

# 25.12 — Rate Limit Bypass for Votes / Likes

## What is it?
Applications frequently implement **Rate Limiting** or action limits to prevent spam, abuse, or the rigging of public systems. Examples include:
- "You can only vote once per poll."
- "You can only 'like' a post once."
- "You can only submit 5 comments per minute."

**Rate Limit Bypass** occurs when the mechanisms used to track who performed an action (or how many times they performed it) are flawed. Developers often rely on easily spoofed identifiers like IP addresses, Cookies, or predictable Device IDs, rather than rigidly authenticated user sessions. 

If an attacker wants to rig an online poll, they don't need to hack the database directly. They just need to figure out how the server knows they already voted, and change that identifier.

Think of it like voting in a local election. The rule is "One vote per person." To enforce this, the polling station dips your index finger in purple ink. If you come back, they see the ink and turn you away. A Rate Limit Bypass is realizing that if you wear a glove, or wash the ink off with a specific solvent (deleting your cookies), or send 50 friends to vote for the exact same candidate (IP rotation), you can cast infinite votes because the enforcement mechanism is superficial.

## ASCII Diagram
```text
================================================================================
                        THE RATE LIMIT BYPASS
================================================================================

[The Weak Enforcement Mechanism]
Server uses IP Address to track votes.

[Attacker's Goal: Give Post #42 a million likes]

1. Attacker sends POST /like {"post": 42}
   Server reads IP: 198.51.100.1. Adds Like. Logs IP.

2. Attacker sends POST /like {"post": 42}
   Server reads IP: 198.51.100.1. Sees IP in log. Blocks.

[The Bypass via HTTP Headers]
3. Attacker sends POST /like {"post": 42}
   Header: X-Forwarded-For: 12.34.56.78  <-- Spoofed!
   Server reads X-Forwarded-For. Thinks it's a new user. Adds Like!

4. Attacker writes a script to rotate the X-Forwarded-For header
   from 0.0.0.0 to 255.255.255.255.
   
[Result: Post #42 receives 4.2 Billion Likes in 10 minutes.]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Find a feature that restricts repeated actions (voting, liking, applying coupon codes, submitting contact forms).
  2. Perform the action until you are blocked.
  3. Analyze what changed to figure out how you are being tracked:
     - **Session Tracking:** Log out and log back in. If you can vote again, the limit is tied to the temporary session, not the permanent user ID.
     - **Cookie Tracking:** Delete your cookies. If you can vote again, the tracking is purely client-side.
     - **IP Tracking:** Disconnect from Wi-Fi and use your cellular data (changing your IP). If you can vote again, it's IP-based.
  4. Test Header Spoofing (if it's IP based): Send the request with headers like `X-Forwarded-For`, `True-Client-IP`, or `X-Real-IP`.

- **Tool commands with flags explained:**
  Using Burp Intruder to rapidly spoof IPs:
  Set the `X-Forwarded-For` header to `127.0.0.§1§`. Set the payload type to Numbers (1 to 255).
  *(This forces the backend to see 255 different IP addresses).*

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's bypass an IP-based poll using HTTP headers.
  1. You vote on a poll: `POST /poll/vote {"option": "A"}`.
  2. You receive: `{"error": "You already voted from this IP."}`
  3. You send the request to Burp Repeater.
  4. You add the header: `X-Forwarded-For: 8.8.8.8`.
  5. The server responds: `{"success": "Vote counted!"}`
  6. You change the header: `X-Forwarded-For: 8.8.4.4`.
  7. The server responds: `{"success": "Vote counted!"}`
  8. You write a python script to generate random IP addresses and send POST requests in an infinite loop, completely rigging the poll.

- **Actual payloads:**
  **Common Spoofing Headers for IP Bypasses:**
  ```http
  X-Forwarded-For: 192.168.1.100
  X-Forwarded-Host: 127.0.0.1
  X-Client-IP: 10.0.0.1
  True-Client-IP: 172.16.0.5
  X-Real-IP: 1.1.1.1
  X-Originating-IP: 8.8.8.8
  ```

- **Real HTTP request/response examples:**
  **Bypassing Rate Limits via URL Null Bytes:**
  Sometimes the rate limit is tied to the specific URL path requested.
  ```http
  GET /api/send_sms?phone=1234567890 HTTP/1.1
  ```
  *(Blocked: Limit 1 per minute).*
  ```http
  GET /api/send_sms?phone=1234567890%00 HTTP/1.1
  ```
  *(Success! The WAF rate-limiting engine sees a different string because of the null byte, but the backend strips it and sends the SMS).*

## Real-World Example
A Bug Bounty hunter targeted a social media platform that paid content creators based on how many "Likes" their videos received. To prevent abuse, the platform limited "Likes" to 1 per registered user per video. However, the hunter discovered that the backend database tracked likes using a composite key of `(video_id, user_id)`. The hunter found an endpoint intended for mobile devices that accepted arrays of video IDs to bulk-like videos: `POST /bulk_like {"videos": [1, 2, 3]}`. The hunter modified the array to include the *same* video ID multiple times: `{"videos": [42, 42, 42, 42]}`. Because the backend processed the array sequentially and updated the "Total Likes" counter for the video before inserting the composite key into the database, it incremented the "Total Likes" by 4, but only inserted one row into the database (ignoring the other 3 as duplicates). The hunter rigged their own videos to have millions of likes, generating massive fraudulent revenue.

## How to Fix It
- **Developer remediation:**
  1. **Strong Identity Tracking:** Action limits must be tied to a verified, authenticated User ID, never to an IP address, Cookie, or Session ID.
  2. **Do Not Trust Headers:** Never use `X-Forwarded-For` or `True-Client-IP` for security boundaries or rate limiting unless you implicitly trust the reverse proxy injecting them, and you configure your web server to explicitly strip out any user-provided values for those headers.
  3. **Idempotency / Unique Constraints:** If a user can only vote once, the database must have a `UNIQUE` constraint on the `(user_id, poll_id)` columns. Even if the application logic fails, the database will throw an exception and prevent the duplicate action.

## Chaining Opportunities
- This vuln + [[09 - Race Conditions in Financial Transactions]] → Race conditions are the ultimate rate-limit bypass. Send 50 requests before the rate-limit counter hits 1.
- This vuln + [[02 - Bruteforce and Wordlists]] → Bypassing rate limits on login pages allows for infinite credential stuffing and brute-forcing.

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[10 - Double Submit _ Double Spend]]
