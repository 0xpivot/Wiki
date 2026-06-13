---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.10 HTTP 2 Specific Attacks"
---

# HTTP/2 Specific Attacks

## 1. Introduction to HTTP/2 Attacks
HTTP/2 was introduced to solve the performance bottlenecks of HTTP/1.1 by introducing a binary framing layer, multiplexing, header compression (HPACK), and stream prioritization. While these features vastly improve web performance, they also introduce complex new attack vectors.

HTTP/2 Specific Attacks target the structural and protocol-level differences between HTTP/1.1 and HTTP/2. Because many modern architectures deploy HTTP/2 at the edge (CDN/Load Balancer) but downgrade to HTTP/1.1 for backend communication, discrepancies in how these two protocols translate data create severe vulnerabilities, most notably HTTP/2-to-HTTP/1.1 Request Smuggling (H2.TE / H2.CL). Furthermore, native HTTP/2 features like HPACK and stream multiplexing open doors to novel Denial of Service (DoS) attacks.

## 2. The Mechanics of HTTP/2
Unlike HTTP/1.1, which is plain text, HTTP/2 is a binary protocol.
- **Connections:** A single TCP connection is used per origin.
- **Streams:** Independent, bidirectional sequences of frames exchanged within the connection.
- **Frames:** The smallest unit of communication (e.g., HEADERS frame, DATA frame).
- **Pseudo-headers:** HTTP/2 replaces the request line (e.g., `GET /index HTTP/1.1`) with pseudo-headers that begin with a colon: `:method`, `:path`, `:authority` (replaces Host header), and `:scheme`.
- **HPACK:** A stateful compression algorithm for headers to reduce overhead.

## 3. ASCII Architecture Diagram: HTTP/2 Downgrade Smuggling
```text
[ Attacker (HTTP/2 Client) ]
     |
     | Frame 1 (HEADERS):
     | :method: POST
     | :path: /
     | :authority: target.com
     | transfer-encoding: chunked
     | 
     | Frame 2 (DATA):
     | 0\r\n\r\nGET /admin HTTP/1.1\r\nHost: target.com\r\n\r\n
     v
[ Edge Proxy (HTTP/2 to HTTP/1.1 Downgrade) ]
     |
     | Translates HTTP/2 frames into a plaintext HTTP/1.1 request.
     | Fails to sanitize the injected 'transfer-encoding' header.
     v
[ Backend Server (HTTP/1.1) ]
     |
     | POST / HTTP/1.1
     | Host: target.com
     | Transfer-Encoding: chunked
     |
     | 0
     | 
     | GET /admin HTTP/1.1
     | Host: target.com
     |
     | Backend sees the '0' chunk, finishes the first request, and treats
     | the smuggled "GET /admin" as the start of the NEXT request in the pipeline!
     v
[ Smuggled Request Execution (Cache Poisoning, Auth Bypass) ]
```

## 4. Vulnerability Mechanics in Detail

### 4.1 HTTP/2 Request Smuggling (H2.TE / H2.CL)
When a reverse proxy accepts HTTP/2 and translates it to HTTP/1.1 for the backend, it must synthesize an HTTP/1.1 request. In HTTP/2, the length of the body is determined intrinsically by the DATA frames and the `END_STREAM` flag. Headers like `Content-Length` (CL) or `Transfer-Encoding` (TE) are technically unnecessary for routing HTTP/2.
However, attackers can explicitly inject `content-length` or `transfer-encoding` headers into the HTTP/2 HEADERS frame.
- If the proxy blindly forwards these headers into the HTTP/1.1 request, the backend HTTP/1.1 server will interpret the body boundaries based on those headers.
- By providing conflicting information (e.g., injecting `transfer-encoding: chunked` inside an HTTP/2 request, known as H2.TE), the attacker causes a desynchronization between the proxy's understanding of the request boundaries and the backend's understanding, resulting in Request Smuggling.

### 4.2 Pseudo-Header Manipulation
HTTP/2 enforces strict syntax via pseudo-headers. However, downgrade mechanisms sometimes mishandle them.
- **Carriage Return / Line Feed (CRLF) Injection:** HTTP/2 allows characters in header values that HTTP/1.1 strictly forbids (like `\r\n`). If an attacker injects `\r\n` into an HTTP/2 header, and the proxy translates it to HTTP/1.1 without validation, it results in HTTP Request Splitting.
- **Ambiguous Authority:** If an attacker sends both an `:authority` pseudo-header and a standard `Host` header with conflicting values, the proxy might route based on one, while the backend uses the other, leading to Host header attacks or SSRF.

### 4.3 Rapid Reset Attack (CVE-2023-44487)
A critical Denial of Service (DoS) vulnerability leveraging HTTP/2 stream multiplexing.
An attacker opens a large number of streams simultaneously (sending HEADERS frames), but immediately sends an `RST_STREAM` (Reset Stream) frame for each one.
- The server allocates resources to handle the new stream (parsing headers, initiating backend connections).
- The `RST_STREAM` immediately cancels it, bypassing the server's concurrent stream limit.
- By repeating this in a tight loop, the attacker consumes immense server CPU and memory with minimal bandwidth, taking down massive infrastructure.

### 4.4 HPACK Bomb (Decompression Bomb)
HPACK uses dynamic tables to compress headers. An attacker can craft a highly compressed HPACK payload that expands massively when decompressed by the server. This causes memory exhaustion (OOM) or high CPU usage, functioning similarly to a traditional zip bomb but at the protocol parsing layer.

## 5. Exploitation Scenarios

### 5.1 Cache Poisoning via H2.TE
By smuggling a request for a static resource (like `/style.css`) while attaching a malicious payload, an attacker can poison the proxy's cache. Legitimate users fetching the CSS will receive the attacker's smuggled response.

### 5.2 Bypassing WAFs and Frontend Controls
WAFs analyzing HTTP/2 traffic might look at the apparent structure of the request. However, due to downgrade translation quirks, the WAF might miss a smuggled request entirely, allowing malicious payloads to reach the backend unimpeded.

## 6. Tooling for HTTP/2 Attacks
Testing HTTP/2 vulnerabilities requires specialized tools, as standard HTTP/1.1 tools (like older versions of curl) cannot manipulate HTTP/2 frames directly.
- **Burp Suite Professional:** Includes the HTTP/2 Request Smuggling scanner and allows manual modification of pseudo-headers via the Inspector.
- **h2csmuggler:** A specialized tool for identifying and exploiting HTTP/2 Cleartext (h2c) smuggling.
- **Custom Scripts:** Utilizing libraries like Python's `h2` or Go's `golang.org/x/net/http2` to manually craft malicious frames.

## 7. Mitigation Strategies

### 7.1 End-to-End HTTP/2
The most robust defense against downgrade attacks is to eliminate the downgrade entirely. Configure the backend application servers to natively support and accept HTTP/2, maintaining the binary framing all the way through the stack.

### 7.2 Strict Protocol Translation Validation
If downgrading is unavoidable, the reverse proxy MUST strictly validate and sanitize the HTTP/2 request before translating it:
- Strip any `transfer-encoding` or `content-length` headers provided in the HTTP/2 HEADERS frame. The proxy must compute the actual `Content-Length` based on the HTTP/2 DATA frames and generate the HTTP/1.1 header itself.
- Reject any headers containing forbidden characters (CRLF).

### 7.3 Rate Limiting and Stream Management
To protect against Rapid Reset and DoS attacks, configure strict limits on the number of active streams, the rate of new streams, and aggressively close connections that exhibit abusive `RST_STREAM` behavior.
Apply patches for known CVEs (like CVE-2023-44487) on all load balancers and web servers.

## 8. Summary
HTTP/2 provides massive performance benefits but shifts complexity into the proxy layer. Security practitioners must look beyond HTTP/1.1 boundaries to properly identify modern protocol-level attacks.

## Chaining Opportunities
- **[[10 - HTTP Request Smuggling]]**: HTTP/2 is an advanced delivery mechanism for classic request smuggling payloads.
- **[[15 - Web Cache Poisoning]]**: Exploiting smuggled requests to overwrite cache entries.
- **[[09 - Host Override via Forwarded Headers]]**: Combining pseudo-header manipulation with host overrides for complex routing bypasses.

## Related Notes
- [[01 - Architecture and Proxies]]
- [[03 - HTTP Header Injection]]
- [[18 - Denial of Service DoS]]
