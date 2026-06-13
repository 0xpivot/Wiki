---
tags: [tools, web-testing, exploiter, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.39 smuggler HTTP Request Smuggling Detector"
---

# smuggler HTTP Request Smuggling Detector

## 1. Introduction to HTTP Request Smuggling

HTTP Request Smuggling (HRS) is a highly critical, intricate attack technique that exploits discrepancies in how different components of a web infrastructure (like frontend proxies, load balancers, and backend servers) parse HTTP request boundaries. When these servers desynchronize, an attacker can "smuggle" a hidden HTTP request inside a legitimate one. This smuggled request is then interpreted by the backend server as the beginning of the *next* request, potentially bypassing security controls, poisoning web caches, or hijacking other users' sessions.

**Smuggler** is a specialized, open-source tool developed to automate the detection of HTTP Request Smuggling vulnerabilities. It tests the infrastructure for desynchronization conditions primarily caused by conflicting `Content-Length` (CL) and `Transfer-Encoding` (TE) headers.

## 2. Under the Hood: The Mechanics of Smuggler

Smuggler operates by sending meticulously crafted payloads designed to induce a measurable timeout or an anomalous response code when the frontend and backend servers disagree on where a request ends.

### 2.1 The Core Vulnerability Types

The tool tests for the following primary desynchronization scenarios:
- **CL.TE (Content-Length / Transfer-Encoding):** The frontend server uses the `Content-Length` header, but the backend server prioritizes the `Transfer-Encoding` header.
- **TE.CL (Transfer-Encoding / Content-Length):** The frontend server uses the `Transfer-Encoding` header, but the backend server uses the `Content-Length` header.
- **TE.TE (Transfer-Encoding / Transfer-Encoding):** Both servers support `Transfer-Encoding`, but one can be induced to ignore it by obfuscating the header (e.g., `Transfer-Encoding: chunked\r`, `Transfer-Encoding : chunked`).

### 2.2 Detection Methodology

Smuggler uses timing-based inference to detect vulnerabilities. For example, in a CL.TE scenario, Smuggler might send a payload where the `Content-Length` includes the entire payload, but the `Transfer-Encoding: chunked` structure terminates early (using a `0\r\n\r\n` chunk).

If the backend server relies on TE, it processes the request up to the `0` chunk and stops. However, the frontend sent more data (based on the CL). This leftover data is "poisoned" in the socket. If Smuggler intentionally leaves an incomplete request in the pipeline, the backend will wait for the rest of it. This results in a time delay. By measuring this delay, Smuggler can accurately infer a vulnerability without causing destructive cache poisoning.

## 3. Architecture and Attack Flow Diagram

```ascii
                      [Attacker Running Smuggler]
                                   |
                    (Crafts CL.TE Ambiguous Request)
                                   |
+-------------------------------------------------------------------------+
| POST / HTTP/1.1                                                         |
| Host: target.com                                                        |
| Content-Length: 44       <-- Frontend uses this (Reads all 44 bytes)    |
| Transfer-Encoding: chunked <-- Backend uses this (Reads chunk logic)    |
|                                                                         |
| 0                        <-- Backend sees end of chunked body here.     |
|                                                                         |
| GET /admin HTTP/1.1      <-- Smuggled request (Left in backend buffer)  |
| Host: target.com                                                        |
+-------------------------------------------------------------------------+
                                   |
                      ============================
                         FRONTEND LOAD BALANCER
                      ============================
                                   |
             (Forwards entire payload based on Content-Length)
                                   |
                      ============================
                         BACKEND WEB SERVER
                      ============================
                                   |
        (Parses via TE. Stops at '0'. Leaves 'GET /admin...' in buffer)
                                   |
                      ============================
                           VICTIM'S REQUEST
                      ============================
             (Victim sends: GET /profile HTTP/1.1)
                                   |
        Backend appends Victim's request to the smuggled data:
        GET /admin HTTP/1.1
        Host: target.com
        GET /profile HTTP/1.1   <-- Evaluated as arbitrary headers/body
```

## 4. Usage and Syntax

Smuggler is typically executed from the command line and can be provided a single URL, a file containing raw HTTP requests, or a list of domains.

### 4.1 Basic Commands

**Testing a single URL:**
```bash
python3 smuggler.py -u https://www.target.com/
```

**Testing a list of URLs:**
```bash
python3 smuggler.py -l urls.txt
```

### 4.2 Advanced Configuration

- **Custom Configurations and Payloads:** Smuggler allows testing of specific mutation techniques to bypass WAFs or specific frontend load balancers. You can define custom payloads in the tool's payload directory.
- **Method Modification:** Sometimes, smuggling only works on `POST` requests. Smuggler defaults to POST but can be configured otherwise.
- **Timeout Adjustments:** Because it relies on time-delays, adjusting the timeout is critical on slow networks to avoid false positives.
  ```bash
  python3 smuggler.py -u https://target.com/ -t 10
  ```

## 5. Confirming and Exploiting the Vulnerability

When Smuggler reports a vulnerability (e.g., `[+] CL.TE vulnerability found!`), the next step is manual verification and exploitation.

### 5.1 Bypassing Frontend Security Controls

Many frontends act as reverse proxies that block access to administrative interfaces (e.g., blocking `/admin`). If a CL.TE vulnerability exists, the attacker sends an innocuous request to `/` but smuggles a request to `/admin`. The frontend inspects the `/` request and permits it. The backend processes the smuggled `/admin` request, effectively bypassing the ACL.

### 5.2 Request Smuggling to XSS

If the application is vulnerable to Reflected XSS but it is unexploitable (e.g., requires a POST request or is hidden behind a WAF), an attacker can smuggle a request containing the XSS payload. When the next victim connects to the server, their legitimate request is appended to the smuggled XSS request, forcing the victim's browser to execute the attacker's JavaScript.

### 5.3 Web Cache Poisoning

This is the most devastating impact of request smuggling. An attacker smuggles a request targeting a static file (like `/app.js`). However, the smuggled request includes malicious headers that trick the backend into returning attacker-controlled content. The frontend cache then associates this malicious response with the URI `/app.js`. Every subsequent user requesting `/app.js` will receive the attacker's payload.

## 6. Advanced Payload Obfuscation (TE.TE)

Sometimes both the frontend and backend technically support Transfer-Encoding, but an attacker can trick one into ignoring it by obfuscating the header. Smuggler supports automated mutations.
Examples of TE mutations:
- `Transfer-Encoding: xchunked`
- `Transfer-Encoding : chunked` (Space before colon)
- `Transfer-Encoding: chunked\r` (Carriage return before newline)
- `Transfer-Encoding: chunked\0` (Null byte injection)
If the frontend proxy normalizes these and processes it as `chunked`, but the backend fails and falls back to `Content-Length`, a TE.CL condition is achieved.

## 7. Defensive Considerations and Mitigation

Resolving HTTP Request Smuggling requires architectural and configurational changes:
- **Use HTTP/2 Extensively:** HTTP/2 uses a binary framing mechanism rather than plain-text parsing for request boundaries, making classic TE/CL smuggling impossible (though HTTP/2 to HTTP/1.1 downgrades introduce new risks, see [[40 - h2csmuggler HTTP 2 Cleartext Smuggling]]).
- **Disable Connection Reuse:** If the frontend closes the TCP connection after every request, smuggled data cannot affect subsequent requests. (Note: High performance impact).
- **Normalize Ambiguous Requests:** Configure the frontend proxy to normalize ambiguous requests or reject requests that contain both `Content-Length` and `Transfer-Encoding` headers.
- **Strict Header Validation:** Ensure the backend server strictly complies with RFC specifications. If a request contains both CL and TE headers, the CL header MUST be ignored, and any obfuscated TE headers should result in a `400 Bad Request`.

## 8. Chaining Opportunities

- **Web Cache Poisoning:** HRS is the premier method for achieving mass web cache poisoning. See [[29 - Web Cache Poisoning and Deception]].
- **Session Hijacking:** By smuggling a request that captures the victim's request headers (including their session cookie), an attacker can extract those cookies and take over the account. See [[04 - Account Takeover Methodologies]].
- **SSRF:** HRS can be used to smuggle requests to internal infrastructure that the backend can reach but the frontend blocks. See [[15 - Server-Side Request Forgery (SSRF)]].

## 9. Appendix: Comprehensive Smuggling Payloads and Scenarios

### A.1 Raw CL.TE Payload Example
```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```
*Breakdown:*
The frontend processes `Content-Length: 13`. It reads `0\r\n\r\nSMUGGLED` (which is exactly 13 bytes). The backend uses `Transfer-Encoding`, sees the `0`, and stops processing. The `SMUGGLED` string is left in the buffer.

### A.2 Raw TE.CL Payload Example
```http
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```
*Breakdown:*
The frontend processes `Transfer-Encoding`. It reads the chunk size `8`, the data `SMUGGLED`, and the terminating `0` chunk. It forwards the whole request. The backend processes `Content-Length: 3`. It reads `8\r\n` (3 bytes) and stops. The `SMUGGLED\r\n0\r\n\r\n` string is left in the backend buffer.

### A.3 Advanced Exploit: Capturing Victim Requests
If the application has an endpoint that reflects user input (like a search function or a comment form), you can smuggle a request to that endpoint and use the `Content-Length` header in the smuggled request to force the backend to append the *victim's* request into the body of your smuggled request.

*Smuggled Request:*
```http
POST /search HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 300

query=
```
When the victim's request arrives, it is appended to `query=`. The backend processes the search, and the attacker checks the search history to see the victim's raw HTTP request, including their session cookies.

### A.4 WAF Bypass via Obfuscation
Often, a WAF will block requests containing both `Content-Length` and `Transfer-Encoding`. Smuggler automates the obfuscation of the TE header to slip past the WAF:
- `X-Ignore: X\r\nTransfer-Encoding: chunked`
- `Transfer-Encoding: xchunked`
- `Transfer-Encoding : chunked`
- `Transfer-Encoding\n: chunked`

### A.5 Debugging Smuggler Output
If Smuggler reports a timeout but manual exploitation fails, it may be a "Blind" request smuggling vulnerability. This occurs when the smuggled request triggers an error on the backend (e.g., 400 Bad Request) and the backend immediately closes the connection, discarding the poisoned buffer. In these cases, exploitation requires extremely precise timing to send the victim's request before the backend closes the connection.

## 10. Related Notes

- [[09 - HTTP Protocol Weaknesses]]
- [[40 - h2csmuggler HTTP 2 Cleartext Smuggling]]
- [[45 - Web Application Firewalls and Bypasses]]
- [[24 - Advanced Proxy Configurations]]
- [[53 - Cache Deception Vulnerabilities]]
- [[17 - Advanced Load Balancer Exploits]]
