---
tags: [vapt, websockets, infrastructure, beginner, protocol-deepdive]
difficulty: beginner
module: "29 - WebSockets Security"
topic: "29.01 WebSocket Protocol — How It Works"
---

# 29.01 — WebSocket Protocol: How It Works

## 1. Introduction: The Problem with HTTP
To understand the security vulnerabilities inherent in WebSockets, one must first understand the fundamental limitations of HTTP that WebSockets were designed to solve. 

The Hypertext Transfer Protocol (HTTP) is inherently a **stateless, half-duplex, client-driven protocol**. 
1. **Stateless:** Every single request is treated as completely independent. The server retains no memory of previous requests (this is why we use Cookies to simulate state).
2. **Half-Duplex:** Only one party can send data at a time over the TCP socket.
3. **Client-Driven:** The server cannot unilaterally push data to the client. The client *must* ask for it first.

Before WebSockets, developers used massive "hacks" to simulate real-time communication:
- **Short Polling:** The browser executes an AJAX request every 3 seconds asking, "Any new messages?" This crushes the server with thousands of empty HTTP requests, wasting bandwidth on HTTP headers for every single check.
- **Long Polling (Comet):** The browser asks, "Any new messages?" and the server *holds the connection open* without responding until a message arrives. Once a message arrives, the server responds, the connection closes, and the client immediately opens a new one. This causes immense connection thrashing on the server.
- **Server-Sent Events (SSE):** Allows the server to push data, but the client cannot push data back over the same channel. It is strictly unidirectional.

**The Solution:** The WebSocket protocol (RFC 6455). It provides a **stateful, full-duplex, persistent connection** over a single TCP socket. Both the client and the server can send data simultaneously, at any time, with practically zero overhead (a WebSocket frame header is as small as 2 bytes, compared to hundreds of bytes for HTTP headers).

## 2. The Architectural Shift
When a web application adopts WebSockets, the fundamental architecture of the application changes. This shift is what introduces the security flaws.
- In HTTP, the application relies heavily on the web server (Apache, Nginx) to parse requests, enforce CORS, check CSRF tokens, and route to specific API endpoints.
- In WebSockets, the web server simply acts as a dumb pipe. Once the connection is established, the application itself (Node.js, Spring Boot, Go) must manually parse the binary frames, maintain the state of the user, route the internal messages based on JSON payloads, and implement its own custom access control logic on a per-message basis.
- Because developers are reinventing routing and authorization inside their custom WebSocket handlers, they frequently make catastrophic mistakes.

## 3. Detailed ASCII Diagrams

### 3.1 The Communication Lifecycle
```text
================================================================================
                    THE WEBSOCKET COMMUNICATION LIFECYCLE
================================================================================

[Phase 1: The HTTP Handshake]
The communication starts as purely standard HTTP/1.1 over TCP port 443.

CLIENT (Browser)                                    SERVER (Node.js/Nginx)
  |                                                           |
  | GET /chat HTTP/1.1                                        |
  | Host: target.com                                          |
  | Upgrade: websocket                                        |
  | Connection: Upgrade                                       |
  | Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==               |
  | Sec-WebSocket-Version: 13                                 |
  | Origin: https://target.com                                |
  | Cookie: session_id=SECRET_TOKEN                           |
  |---------------------------------------------------------->|
  |                                                           |
  |                            HTTP/1.1 101 Switching Protocols
  |                                          Upgrade: websocket
  |                                         Connection: Upgrade
  |        Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo= |
  |<----------------------------------------------------------|

[Phase 2: The Protocol Switch]
The TCP connection REMAINS OPEN. However, HTTP is dead. The socket is now 
speaking the custom binary WebSocket protocol. WAFs that only parse HTTP 
will stop monitoring the traffic at this point.

[Phase 3: Full-Duplex Data Transfer]
Frames can be sent in both directions simultaneously. No headers required.

  |                                                           |
  | [WS Frame: Opcode=1 (Text)]                               |
  | {"action": "join", "room": "general"}                     |
  |---------------------------------------------------------->|
  |                                                           |
  |                               [WS Frame: Opcode=1 (Text)] |
  |                 {"sys": "Welcome to general, User123!"}   |
  |<----------------------------------------------------------|
  |                                                           |
  | [WS Frame: Opcode=1 (Text)]                               |
  | {"action": "send", "msg": "Hello everyone!"}              |
  |---------------------------------------------------------->|
  |                                                           |

[Phase 4: The Teardown]
  |                                                           |
  | [WS Frame: Opcode=8 (Close)]                              |
  |---------------------------------------------------------->|
  |                                                           |
  |                              [WS Frame: Opcode=8 (Close)] |
  |<----------------------------------------------------------|
  |                                                           |
  v                                                           v
  (TCP FIN/ACK - Connection Closed)
================================================================================
```

### 3.2 The Cryptographic Handshake (`Sec-WebSocket-Key`)
You might wonder what the `Sec-WebSocket-Key` and `Sec-WebSocket-Accept` headers are doing. This is NOT encryption, and it is NOT authentication. 

It is a basic mathematical handshake designed solely to prove that the server actually understands the WebSocket protocol and isn't just a misconfigured HTTP server that accidentally returned a 200 OK. 

1. The client generates a random 16-byte value and Base64 encodes it (e.g., `dGhlIHNhbXBsZSBub25jZQ==`).
2. The server reads this key and concatenates it with a globally defined "Magic String" from the RFC: `258EAFA5-E914-47DA-95CA-C5AB0DC85B11`.
3. The server takes the SHA-1 hash of the concatenated string.
4. The server Base64 encodes that hash and returns it as `Sec-WebSocket-Accept`.

If the client's browser verifies the hash, the connection proceeds. If the hash is wrong, the browser drops the connection. This is a purely structural mechanism to prevent accidental HTTP proxy caching, but many junior developers mistakenly believe it provides cryptographic security.

### 3.3 The WebSocket Binary Frame Structure
Unlike HTTP, which sends text-based headers parsed by looking for `\r\n\r\n`, WebSockets send data in highly structured binary frames. This structure is what breaks legacy WAFs and intrusion detection systems.

```text
================================================================================
                    WEBSOCKET BINARY FRAME STRUCTURE (RFC 6455)
================================================================================

      0                   1                   2                   3
      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
     +-+-+-+-+-------+-+-------------+-------------------------------+
     |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
     |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
     |N|V|V|V|       |S|             |   (if payload len==126/127)   |
     | |1|2|3|       |K|             |                               |
     +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
     |     Extended payload length continued, if payload len == 127  |
     + - - - - - - - - - - - - - - - +-------------------------------+
     |                               |Masking-key, if MASK set to 1  |
     +-------------------------------+-------------------------------+
     | Masking-key (continued)       |          Payload Data         |
     +-------------------------------- - - - - - - - - - - - - - - - +
     :                     Payload Data continued ...                :
     + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
     |                     Payload Data continued ...                |
     +---------------------------------------------------------------+

[Key Components]
- FIN (1 bit): Indicates if this is the final fragment in a message.
- RSV1, RSV2, RSV3: Reserved bits, usually 0 unless an extension is negotiated.
- Opcode (4 bits): Defines the interpretation of the payload data.
    - 0x1: Text frame (Usually UTF-8 JSON)
    - 0x2: Binary frame (e.g., ArrayBuffer, images)
    - 0x8: Connection close
    - 0x9: Ping (Heartbeat)
    - 0xA: Pong (Heartbeat reply)
- MASK (1 bit): Defines whether the payload data is masked. (ALWAYS 1 for Client->Server).
- Payload length (7 bits): If 0-125, that's the length. If 126, the next 2 bytes are the length. If 127, the next 8 bytes are the length.
- Masking-key (32 bits): A 4-byte random key used to XOR the payload.
================================================================================
```

### 3.4 Client-to-Server Masking
One of the most bizarre security features of WebSockets is **Masking**. According to the RFC, *every single frame sent from the Client to the Server must be masked (XORed) with a random 32-bit key*.

**Why? Cache Poisoning Prevention.**
Early in the development of WebSockets, researchers realized that if a browser sent unmasked text over port 80, a misconfigured transparent HTTP proxy sitting in the middle of the network might misinterpret the WebSocket frame as a completely new HTTP GET request. An attacker could craft a WebSocket payload that looked exactly like an HTTP request, tricking the proxy into executing an HTTP Request Smuggling attack or Cache Poisoning attack against the backend infrastructure.

By forcing the browser to XOR the payload with a random, rotating 4-byte key, the attacker can no longer guarantee what bytes actually traverse the network wire. The sequence `GET /admin HTTP/1.1` becomes garbled binary nonsense on the wire, which the server unmasks upon receipt. This completely neutralizes proxy poisoning. 

**Note for Hackers:** You do not need to worry about manually masking payloads. Burp Suite and browser native APIs handle the masking and unmasking completely transparently. When you view traffic in Burp, you see the unmasked plaintext.

## 4. The Expanding Attack Surface
When you approach a target that uses WebSockets, your threat modeling must immediately shift from a traditional HTTP mindset to a socket-based mindset.

1. **The Origin Check:** Because WebSockets don't respect the Same-Origin Policy, the server's single greatest responsibility is verifying where the connection request came from during the initial HTTP handshake. If this fails, the entire application is susceptible to Cross-Site WebSocket Hijacking.
2. **State Desynchronization:** In HTTP, authentication is checked on every single request via cookies or headers. In WebSockets, authentication is usually checked *once* during the initial handshake. If a user's account is suspended, or their password is changed, or their role is downgraded, does the server aggressively terminate all their active WebSocket connections? Often, it does not. An attacker can keep a highly privileged WebSocket connection open for weeks after their account has been supposedly revoked.
3. **Data Framing & Amplification:** Because WebSockets don't have the overhead of HTTP, they are often used to send hundreds of small messages per second. This makes them a prime target for Denial of Service. If an attacker can inject a massive payload (e.g., a 10MB text frame), the server's Node.js event loop will block entirely while parsing it, crashing the application.
4. **Multiplexing Logic Flaws:** Modern applications often route multiple different channels (e.g., `chat`, `notifications`, `live_prices`) over a single WebSocket connection. The backend uses a massive `switch` statement to route the JSON message based on an `action` or `channel` parameter. This internal routing layer is notoriously prone to Insecure Direct Object References (IDOR) and authorization bypasses, as developers forget to re-verify permissions for every single sub-channel inside the socket.

## 5. Tooling and Visibility
As a penetration tester, gaining visibility into the WebSocket stream is paramount.
- **Burp Suite:** Burp natively intercepts the HTTP upgrade request and maintains the tunnel. Traffic is viewed in `Proxy -> WebSockets history`. You can intercept live frames or send them to Repeater.
- **WSS to WS Stripping:** If you are testing a mobile application or a thick client that uses TLS-encrypted WebSockets (`wss://`), you must configure your device to trust Burp's CA certificate. The upgrade request will happen over HTTPS, and Burp will decrypt the tunnel, allowing you to see the plaintext frames.
- **Custom Scripts:** Often, Burp Repeater is too slow for complex race conditions or fuzzing over WebSockets. Penetration testers frequently write custom Python scripts using the `websocket-client` library. To authenticate the script, you must manually pass the victim's session cookies in the header of the `create_connection` call.

## 6. Next Steps in the Module
In the following notes, we will break down exactly how to exploit the flaws mentioned in this architectural overview. We will start by attacking the HTTP Handshake (CSWSH), and then move into attacking the persistent binary frames (Message Manipulation, XSS, SQLi, and Command Injection).

## Related Notes
- [[02 - WebSocket Upgrade Security Implications]]
- [[03 - Cross-Site WebSocket Hijacking (CSWSH)]]
- [[04 - WebSocket Message Manipulation]]
