---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.08 HTTP HTTPS and TLS Handshake Explained"
---

# HTTP, HTTPS, and the TLS Handshake Explained

## 1. The Foundation: HTTP Basics
The Hypertext Transfer Protocol (HTTP) is the foundational application-layer protocol for the World Wide Web. It operates natively over TCP port 80. HTTP is fundamentally a **stateless, client-server, request-response** protocol. 
*   **Stateless:** The server retains no memory of past requests from the same client. Every request must contain all necessary information to be understood. To maintain state (like a logged-in session), applications must build logic on top of HTTP using mechanisms like Cookies or Tokens (e.g., JWT).
*   **Client-Server:** The client (e.g., a web browser or API tool) initiates the connection and sends a request; the server processes it and returns a response.

## 2. HTTP Protocol Evolution
*   **HTTP/1.0:** Established the basic request/response structure and headers. A major drawback was that every single request required a brand new, expensive TCP connection.
*   **HTTP/1.1:** Introduced persistent connections (`Connection: keep-alive`), allowing multiple requests to use the same TCP socket. It also added the mandatory `Host` header (crucial for virtual hosting), chunked transfer encoding, and caching improvements.
*   **HTTP/2:** A massive overhaul aimed at performance. It introduced binary framing (instead of plain text), multiplexing (sending multiple requests concurrently over a single TCP connection without head-of-line blocking), header compression (HPACK), and server push.
*   **HTTP/3:** Replaces the underlying transport layer entirely. Instead of TCP, HTTP/3 uses **QUIC**, a protocol built on top of UDP. QUIC eliminates the TCP handshake latency and solves TCP-level head-of-line blocking while maintaining reliable, encrypted delivery.

## 3. HTTP Methods (Verbs)
Methods indicate the desired action to be performed on the identified resource.
*   **GET:** Retrieve data. Should be idempotent and safe (no state changes on the server).
*   **POST:** Submit data to the server to process or store. Often used for form submissions and API data creation. Non-idempotent.
*   **PUT:** Replace an existing resource entirely or create it if it doesn't exist. Idempotent.
*   **DELETE:** Remove a specified resource.
*   **PATCH:** Apply partial modifications to a resource.
*   **OPTIONS:** Describe the communication options/methods available for the target resource (critical for CORS preflight requests).
*   **TRACE:** Perform a message loop-back test. Highly dangerous in production due to Cross-Site Tracing (XST) vulnerabilities, as it echoes back sensitive headers like Cookies.
*   **CONNECT:** Converts the request connection to a transparent TCP/IP tunnel, primarily used to establish SSL/TLS connections through an HTTP proxy.

## 4. HTTP Status Codes
Responses indicate the result of the request via a 3-digit code:
*   **1xx (Informational):** Request received, continuing process. (e.g., 101 Switching Protocols for WebSockets).
*   **2xx (Success):** The action was successfully received, understood, and accepted. (e.g., 200 OK, 201 Created, 204 No Content).
*   **3xx (Redirection):** Further action must be taken to complete the request. (e.g., 301 Moved Permanently, 302 Found/Temporary Redirect).
*   **4xx (Client Error):** The request contains bad syntax or cannot be fulfilled. (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed).
*   **5xx (Server Error):** The server failed to fulfill an apparently valid request. (e.g., 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable).

## 5. Important HTTP Headers
Headers provide metadata about the request or response.
*   **Host:** Specifies the domain name of the server (mandatory in HTTP/1.1).
*   **User-Agent:** Identifies the client software (browser, OS).
*   **Accept:** What content types the client understands.
*   **Content-Type:** The MIME type of the payload (e.g., `application/json`, `application/x-www-form-urlencoded`).
*   **Authorization:** Contains credentials for authenticating the client with the server (e.g., Bearer tokens, Basic auth).
*   **Cookie / Set-Cookie:** Used for state management and session tracking.

## 6. HTTPS and Cryptographic Foundations
HTTPS is simply HTTP encapsulated within a secure TLS (Transport Layer Security) tunnel, operating over TCP port 443. It provides:
1.  **Confidentiality:** Symmetrical encryption ensures data cannot be read by eavesdroppers.
2.  **Integrity:** Message Authentication Codes (MACs) ensure data isn't altered in transit.
3.  **Authentication:** Public Key Infrastructure (PKI) and digital certificates prove the server is who it claims to be.

## 7. The TLS 1.2 Handshake Step-by-Step
Before any HTTP data is sent, the client and server must establish the secure tunnel. The TLS 1.2 handshake involves multiple round trips:

1.  **ClientHello:** The client sends a message proposing the TLS version, a random byte string (Client Random), a list of supported Cipher Suites (encryption algorithms), and extensions. **Crucial Extension:** SNI (Server Name Indication) allows the client to specify which hostname it wants to connect to, allowing a single IP to host multiple HTTPS domains.
2.  **ServerHello:** The server responds, selecting the highest mutually supported TLS version and Cipher Suite. It also generates its own random byte string (Server Random).
3.  **Certificate:** The server sends its Digital Certificate (containing its Public Key), signed by a trusted Certificate Authority (CA). The client verifies this signature against its local root trust store.
4.  **ServerKeyExchange:** (Depending on the cipher suite). If Forward Secrecy is used (like ECDHE), the server sends parameters required to generate the shared secret.
5.  **ServerHelloDone:** Server indicates it is finished with its part of the negotiation.
6.  **ClientKeyExchange:** The client sends its portion of the cryptographic parameters.
7.  **ChangeCipherSpec & Finished (Client):** The client signals that all future messages will be symmetrically encrypted using the newly derived shared secret (Master Secret). It sends an encrypted hash of the entire handshake to prove integrity.
8.  **ChangeCipherSpec & Finished (Server):** The server decrypts and verifies the client's finish message, then switches to symmetric encryption and sends its own encrypted handshake summary.
*Once complete, secure HTTP application data can flow.*

## 8. TLS 1.3 Improvements
TLS 1.3, the modern standard, brought massive enhancements:
*   **Speed (1-RTT and 0-RTT):** It reduced the handshake from two round trips down to one round trip (1-RTT). It also introduced 0-RTT for resumed connections, allowing the client to send encrypted HTTP data in the very first packet.
*   **Security:** Removed obsolete and insecure cryptographic primitives like MD5, SHA-1, RC4, DES, and static RSA key exchange. Perfect Forward Secrecy (PFS) is now mandatory.
*   **Privacy:** Encrypts more of the handshake earlier in the process, including the server certificate.

## 9. Security Vulnerabilities and Attack Vectors
*   **SSL Stripping (Downgrade Attack):** An attacker in a MITM position intercepts the initial unencrypted `http://` request and proxies it to the server via `https://`. The attacker serves the client the plain-text HTTP version, successfully reading all traffic. Mitigated by HSTS (HTTP Strict Transport Security).
*   **HTTP Request Smuggling (CL.TE / TE.CL):** A highly critical attack where a discrepancy in how front-end proxies and back-end servers parse the `Content-Length` (CL) and `Transfer-Encoding` (TE) headers allows an attacker to "smuggle" a second, hidden HTTP request within the body of a first request. This can bypass WAFs, poison caches, and hijack other users' sessions.
*   **Host Header Injection & SSRF:** Manipulating the `Host` header can cause the server to generate password reset links pointing to an attacker's domain, or force internal proxies to route requests to internal-only systems (Server-Side Request Forgery).

## 10. ASCII Diagram: TLS 1.2 Handshake Flow

```text
  [Client Browser]                                        [Web Server]
         |                                                     |
         | --------- (1) ClientHello ------------------------> |
         |               (Cipher Suites, Client Random, SNI)   |
         |                                                     |
         | <-------- (2) ServerHello ------------------------- |
         |               (Chosen Cipher, Server Random)        |
         | <-------- (3) Certificate ------------------------- |
         |               (Server's Public Key inside)          |
         | <-------- (4) ServerKeyExchange (Optional) -------- |
         |               (Diffie-Hellman Parameters)           |
         | <-------- (5) ServerHelloDone --------------------- |
         |                                                     |
  [Client verifies Certificate                                 |
   against Root CA Store]                                      |
         |                                                     |
         | --------- (6) ClientKeyExchange ------------------> |
         |               (Client's DH Parameters)              |
         |                                                     |
  [Both independently calculate                                |
   the Symmetric Master Secret]                                |
         |                                                     |
         | --------- (7) ChangeCipherSpec -------------------> |
         | --------- (8) Finished (Encrypted Handshake Hash)-> |
         |                                                     |
         | <-------- (9) ChangeCipherSpec -------------------- |
         | <-------- (10) Finished (Encrypted Handshake Hash)- |
         |                                                     |
         | =================================================== |
         | <======== Secure, Encrypted HTTP Data ============> |
         | =================================================== |
```

## 11. Chaining Opportunities
*   **HTTP Request Smuggling to Web Cache Poisoning:** A smuggled request can poison an intermediate caching proxy with malicious JavaScript, affecting all subsequent users who request that resource.
*   **SSL Stripping to Credential Harvesting:** If HSTS is not enabled, stripping the TLS layer allows tools like Bettercap to capture plaintext POST bodies containing usernames and passwords.
*   **TRACE enabled to XSS token theft:** If the TRACE method is enabled and an XSS vulnerability exists, an attacker can use XHR to send a TRACE request, causing the server to echo back the `HttpOnly` cookies, bypassing standard client-side protections.

## 12. Related Notes
*   [[06 - DNS Protocol Basics and Name Resolution]]
*   [[10 - FTP TFTP and Telnet Protocols]]
*   [[01 - Introduction to Web Application Security]]
