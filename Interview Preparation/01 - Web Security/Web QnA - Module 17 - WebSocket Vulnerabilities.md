---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 17"
---

# Web QnA - Module 17 - WebSocket Vulnerabilities

## Architectural Overview: Cross-Site WebSocket Hijacking (CSWSH)

```text
    [Attacker Site]                            [Target Web Server]
    evil.com                                   victim.com
       |                                            |
       | 1. Victim visits evil.com                  |
       |<--------------------------------           |
       |                                            |
       | 2. JS executes:                            |
       |    new WebSocket('wss://victim.com/ws')    |
       |------------------------------------------->|
       |    GET /ws HTTP/1.1                        |
       |    Host: victim.com                        |
       |    Origin: https://evil.com   <---- [!]    |
       |    Cookie: session=VictimAuthCookie        |
       |    Connection: Upgrade                     |
       |                                            |
       |<-------------------------------------------|
       |    HTTP/1.1 101 Switching Protocols        |
       |    Upgrade: websocket                      |
       |                                            |
       | 3. CSWSH Established! Attacker JS can now  |
       |    send/receive raw socket frames as victim|
```

## Formal Technical Questions

**Q1: Explain the mechanism of Cross-Site WebSocket Hijacking (CSWSH). Why does the Same-Origin Policy (SOP) not prevent this by default?**
**A1:** 
Cross-Site WebSocket Hijacking (CSWSH) is functionally identical to Cross-Site Request Forgery (CSRF), but instead of executing a single HTTP request, it establishes a persistent, two-way communication channel. When a user authenticates to a web application, their session cookie is stored in the browser. If the user visits an attacker-controlled website, the attacker's JavaScript can initiate a WebSocket connection (`wss://victim.com`) to the vulnerable application.
The browser automatically attaches the victim's session cookies to the initial HTTP Upgrade request. 
SOP does *not* apply to WebSockets. The WebSocket standard explicitly allows cross-origin connections. It is entirely up to the server-side implementation to read the `Origin` header during the HTTP handshake and reject connections from untrusted origins. If the server ignores the `Origin` header, the connection succeeds, and the attacker gains full read/write access to the socket.

**Q2: How does HTTP Request Smuggling manifest over WebSocket connections, and what makes it dangerous?**
**A2:** 
WebSocket Smuggling occurs in complex architectures involving reverse proxies and backend servers. The attack abuses discrepancies in how the proxy and the backend interpret the `Connection: Upgrade` and `Upgrade: websocket` headers.
If an attacker sends a malformed HTTP request that tricks the proxy into believing a WebSocket connection has been established, the proxy stops parsing HTTP semantics and switches to raw TCP tunneling. However, if the backend server rejected the upgrade (or wasn't even asked, due to smuggling), it still expects standard HTTP requests. 
The attacker can now send arbitrary HTTP requests directly through the proxy's "blind" TCP tunnel. This allows the attacker to bypass proxy-level WAFs, routing rules, and access internal administrative endpoints, effectively smuggling secondary HTTP requests inside the body of the "upgraded" connection.

**Q3: Describe the concept of "Blind WebSocket Attacks" and how you would exploit a message-injection vulnerability without seeing the response.**
**A3:** 
A Blind WebSocket attack happens when an attacker can inject messages into a WebSocket stream (perhaps through an exposed internal service or an SSRF) but cannot view the returning frames. It is also common when exploiting CSWSH where the application uses unpredictable frame IDs, or when triggering backend actions via unauthenticated WebSockets.
To exploit this, I rely on Out-of-Band (OOB) techniques or side channels:
1. **Time-Based:** Injecting payloads that cause backend processing delays (e.g., `{"command": "search", "query": "a' WAITFOR DELAY '0:0:5'--"}`).
2. **OOB Interaction:** Forcing the backend to reach out to an external server I control via SSRF payloads inside the WebSocket frame (`{"avatar": "http://collaborator.id/image.jpg"}`).
3. **State Change Observation:** Injecting a mutation payload via the blind socket, then checking a separate, standard HTTP endpoint to see if the target data changed.

## Scenario-Based Questions

**Q4: You are auditing a financial trading application. The application uses WebSockets to push live stock prices. Authentication is handled via a Bearer token in the LocalStorage (not cookies). The server perfectly validates the `Origin` header. Can you still hijack the WebSocket stream? If so, how?**
**A4:** 
Yes, it is possible, but not via traditional CSWSH (since cookies aren't used and the Origin is validated). I must find a way to execute code within the trusted origin.
1. **Cross-Site Scripting (XSS):** If I find an XSS vulnerability anywhere on the target domain or its subdomains, I can execute JavaScript in the victim's browser.
2. **Token Extraction:** The XSS payload extracts the Bearer token from LocalStorage.
3. **Socket Instantiation:** My XSS payload manually opens a new WebSocket connection. Since the JS is running on the legitimate domain, the `Origin` header will be valid.
4. **Token Transmission:** The payload sends the extracted Bearer token in the first WebSocket frame to authenticate the session (since it's not sent automatically like cookies). 
From there, the XSS payload acts as a relay, forwarding all intercepted financial data to my external C2 server.

**Q5: A chat application uses WebSockets. When you capture the traffic in Burp Suite, the HTTP Upgrade request succeeds, but all subsequent WebSocket frames look like random binary gibberish instead of JSON. What is going on, and how do you analyze the traffic?**
**A5:** 
The data is likely serialized using a binary format or is end-to-end encrypted.
1. **Binary Protocols:** The application might be using Protobuf, MessagePack, or custom binary serialization instead of plain text JSON. I can inspect the client-side JavaScript to find the schema or the parsing libraries (like `protobuf.js`). I can then write a custom Burp extension using the extracted schema to deserialize the frames in real-time.
2. **Per-Message Deflate:** It could be standard WebSocket compression (`Sec-WebSocket-Extensions: permessage-deflate`). Burp Suite usually handles this natively, but if misconfigured, it appears as binary.
3. **Application-Layer Encryption:** The JS might be encrypting the JSON payload before sending it through the socket (e.g., using WebCrypto API). To analyze this, I would use browser DevTools to place a breakpoint right before the encryption function `encrypt(payload)`, read the plaintext, or hook the function using an extension like Tampermonkey to dump plaintext traffic to the console.

**Q6: You find an endpoint `wss://app.victim.com/terminal` that provides a diagnostic CLI. It strictly checks the `Origin` header against a whitelist. You notice the whitelist is implemented as a regex: `^https://app\.victim\.com`. How do you bypass this to perform CSWSH?**
**A6:** 
The regex is improperly anchored or lacks strict domain boundary checks.
Since it doesn't end with `$`, it allows any domain that *starts* with the string. I can register a malicious domain:
`https://app.victim.com.attacker.com`
When a victim visits my malicious domain, the browser sets the Origin header to `https://app.victim.com.attacker.com`. The server's regex matches the beginning of the string and allows the connection. I now have CSWSH and can execute terminal commands on the victim's behalf via the hijacked socket.

## Deep-Dive Defensive Questions

**Q7: How should a defense-in-depth architecture properly secure WebSocket authentication to prevent both CSWSH and unauthenticated access?**
**A7:** 
A robust defense requires multiple layers:
1. **Strict Origin Validation:** The server must rigorously check the `Origin` header against an exact-match whitelist of trusted domains. No weak regexes.
2. **Ticket-Based Authentication:** Do not rely solely on cookies for WebSocket authentication. The client should make an authenticated HTTP request to an API endpoint (e.g., `/api/ws-ticket`) which returns a short-lived, cryptographically secure one-time-use ticket. The client then passes this ticket either in the URL (`wss://app.com/ws?ticket=XYZ`) or in the first frame. 
3. **CSRF Tokens:** If cookies are used, the initial HTTP Upgrade request must include a standard CSRF token, either in the URL or as a custom header, validating the request's intent.

**Q8: Explain the security implications of WSS (WebSocket Secure) vs WS. Does WSS protect the application from application-layer attacks?**
**A8:** 
WSS is simply WebSockets tunneled over TLS (just as HTTPS is HTTP over TLS). 
WSS guarantees data confidentiality and integrity *in transit* between the client and the server, preventing Man-in-the-Middle (MitM) attacks from sniffing or tampering with the frames on the network level.
However, **WSS provides zero protection against application-layer attacks**. It does not prevent CSWSH, frame injection, XSS via returned frames, or backend SQL injection. The server still receives the exact same malicious payloads; they are just securely encrypted during transit. Application-layer validation of every incoming frame is absolutely mandatory, regardless of WSS.

## Real-World Attack Scenario

**The Silent Auction Takeover**
An online auction house implemented a real-time bidding system using WebSockets. 
1. **Reconnaissance:** The attacker realized the application used standard session cookies for authentication. Upon analyzing the WebSocket handshake (`wss://auction.com/bidding`), they noticed the server completely ignored the `Origin` header.
2. **Exploitation:** The attacker crafted a malicious webpage (`https://evil-hacker.com/free-money`). The page contained JavaScript that initiated a WebSocket connection to the auction house. 
3. **Execution:** When high-roller victims visited the attacker's site (lured via a phishing email), their browsers silently opened the WebSocket connection in the background. The cookies were automatically sent.
4. **Impact:** The attacker's JavaScript listened for incoming broadcast messages detailing current bids. When a valuable item appeared, the malicious JS silently forged a bid on behalf of the victim for an astronomical amount, using the hijacked socket. The victims unknowingly placed winning bids on items they didn't want, draining their accounts.

## Chaining Opportunities

- **Stored XSS -> WebSocket Relay:** Injecting an XSS payload that connects back to the attacker's server via WebSockets, creating a persistent, full-duplex C2 channel directly from the victim's browser, bypassing inbound firewall rules.
- **WebSocket -> Internal SSRF:** If a WebSocket server accepts URLs to fetch preview images (e.g., in a chat app), injecting AWS metadata IP `169.254.169.254` into the socket frame can yield cloud credentials.
- **Host Header Injection -> WSS Cache Poisoning:** Tricking an intermediary proxy into caching a malicious WebSocket upgrade response by injecting a rogue Host header during the handshake.

## Related Notes
- [[11 - Cross-Site Request Forgery (CSRF)]]
- [[04 - Session Management Vulnerabilities]]
- [[21 - Advanced Cross-Site Scripting (XSS)]]
- [[14 - Server-Side Request Forgery (SSRF)]]
