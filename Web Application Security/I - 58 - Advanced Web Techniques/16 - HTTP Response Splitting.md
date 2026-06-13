---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.16 HTTP Response Splitting"
---

# HTTP Response Splitting

## Introduction to HTTP Response Splitting

HTTP Response Splitting is a critical web application vulnerability that arises when untrusted user input is embedded directly into an HTTP response header without proper sanitization or encoding. Because the HTTP protocol is text-based and relies on specific control characters—specifically Carriage Return (`CR`, `\r`, `%0d`) and Line Feed (`LF`, `\n`, `%0a`)—to delineate headers and separate the header block from the response body, failing to neutralize these characters can lead to devastating consequences.

When an attacker successfully injects a CRLF sequence into a response header (such as `Location` or `Set-Cookie`), they can trick the server, intermediate proxies, or the client's browser into interpreting the remainder of the injected payload as a completely separate HTTP response. This effectively "splits" the original response into two or more responses.

While many modern frameworks (like Django, Spring, Express) and application servers (like Tomcat, Nginx, Apache) automatically sanitize or block CRLF characters in outgoing headers, this vulnerability still frequently surfaces in legacy applications, custom embedded web servers (e.g., in IoT devices), or when custom routing logic is implemented by developers unaware of the risks. Furthermore, subtle variations of this attack have evolved into modern HTTP Request Smuggling, which targets the boundaries of HTTP messages between reverse proxies and back-end servers.

## Core Mechanics of CRLF Injection

To understand HTTP Response Splitting, one must first deeply understand how HTTP messages are structured according to RFC 7230. 

An HTTP response looks like this:
```http
HTTP/1.1 200 OK[CRLF]
Content-Type: text/html[CRLF]
Content-Length: 123[CRLF]
Set-Cookie: session=xyz[CRLF]
[CRLF]
<html><body>...</body></html>
```

The separation between individual headers is exactly one `[CRLF]` sequence. The separation between the final header and the body of the message is exactly two `[CRLF]` sequences (`\r\n\r\n`).

If an application takes a user-supplied parameter and reflects it in a header, such as a redirect:
```php
<?php
$lang = $_GET['lang'];
header("Location: /index.php?lang=" . $lang);
?>
```

An attacker can provide a payload for the `lang` parameter that includes URL-encoded CRLF characters:
`en%0d%0aSet-Cookie:%20admin=true`

The server decodes this and outputs:
```http
HTTP/1.1 302 Found
Location: /index.php?lang=en
Set-Cookie: admin=true
...
```
This is a standard CRLF injection (HTTP Header Injection). However, HTTP Response Splitting takes this a step further by completely terminating the HTTP response and injecting a full secondary response.

## ASCII Architecture Diagram

Below is a visual representation of how an injected payload is interpreted by the client or proxy, effectively splitting the intended response into two separate conceptual blocks.

```text
+-------------------------------------------------------------+
|                     ATTACKER PAYLOAD                        |
|   en%0d%0a%0d%0aHTTP/1.1 200 OK%0d%0a...%0d%0a%0d%0aBody    |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                VULNERABLE WEB APPLICATION                   |
|  header("Location: /lang=" . $input);                       |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|              GENERATED HTTP RESPONSE STREAM                 |
|                                                             |
|  HTTP/1.1 302 Found\r\n           <-- Start of Original     |
|  Location: /lang=en\r\n\r\n       <-- Splitting occurs here |
|  HTTP/1.1 200 OK\r\n              <-- Start of Split Resp   |
|  Content-Type: text/html\r\n                                |
|  Content-Length: 25\r\n                                     |
|  \r\n                                                       |
|  <script>alert(1)</script>                                  |
+-------------------------------------------------------------+
                              |
                              V
+-------------------------------------------------------------+
|                     PROXY / BROWSER                         |
|                                                             |
|  Response 1: 302 Found (Discarded or processed)             |
|  Response 2: 200 OK with Malicious XSS payload              |
+-------------------------------------------------------------+
```

## Attack Vector 1: Cross-Site Scripting (XSS)

The most direct and visually impactful result of HTTP Response Splitting is Cross-Site Scripting. Normally, XSS requires user input to be reflected within the HTML body. But what if the application only reflects input in the headers (like a 302 redirect), and the body is empty or non-existent?

By splitting the response, an attacker can artificially create an HTTP response body containing malicious JavaScript. 

### Exploitation Walkthrough
Consider the vulnerable PHP redirect code shown earlier. An attacker crafts the following payload:

`foobar%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0aContent-Type:%20text/html%0d%0aContent-Length:%2025%0d%0a%0d%0a%3Cscript%3Ealert(1)%3C/script%3E`

When decoded and processed by the server, the raw socket output becomes:

```http
HTTP/1.1 302 Found
Location: /index.php?lang=foobar

HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 25

<script>alert(1)</script>
```

When a browser receives this stream over a single TCP connection, it might parse it as two distinct responses if HTTP pipelining or specific keep-alive conditions are met. Alternatively, intermediate proxies might cache the second response and serve it to subsequent users, which leads us directly into Web Cache Poisoning.

## Attack Vector 2: Web Cache Poisoning

The true devastation of HTTP Response Splitting is unlocked when combined with a caching proxy (like Varnish, Squid, or a CDN) sitting in front of the vulnerable web application.

When an attacker sends two requests over a single connection, the proxy expects two responses from the backend server. However, by sending ONE malicious request that causes the backend to generate a SPLIT response (which looks like TWO responses to the proxy), the proxy's request-response queue falls out of sync.

### The Desync Execution
1. **Attacker Connection**: The attacker opens a TCP connection to the proxy.
2. **Request 1**: The attacker sends a request targeting the vulnerable endpoint with a Response Splitting payload.
3. **Request 2**: The attacker immediately pipelines a second request for a highly trafficked, static resource (e.g., `/scripts/main.js`).
4. **Backend Processing**: The backend server processes Request 1. Due to the splitting vulnerability, it outputs what looks like TWO responses.
5. **Proxy Interpretation**: 
   - The proxy receives "Response 1A" (the first half) and matches it to Request 1.
   - The proxy receives "Response 1B" (the maliciously crafted second half containing the attacker's payload) and incorrectly matches it to Request 2 (`/scripts/main.js`).
6. **Cache Poisoning**: The proxy aggressively caches "Response 1B" under the cache key for `/scripts/main.js`.
7. **Victim Impact**: Every legitimate user who visits the site and requests `/scripts/main.js` will receive the attacker's malicious payload from the cache.

This leads to a complete compromise of the web application for all users, as the core JavaScript files are essentially backdoored via the cache.

## Attack Vector 3: Cache Defacement and Hijacking

Similar to Cache Poisoning, an attacker can use Response Splitting to perform Cache Defacement. If the attacker wants to deface the homepage (`/index.html`), they follow the exact same desync pipeline technique. 

Additionally, an attacker could inject `Set-Cookie` headers into the second split response, forcing a specific session ID onto a victim. If the proxy caches this and serves it to a user, the user is unknowingly logged into an attacker-controlled account, or their session is fixated, leading to Session Fixation or Account Hijacking scenarios.

## Modern Day Context and HTTP Request Smuggling

While classic HTTP Response Splitting is rare today due to built-in CRLF protections in frameworks like Express.js (`res.setHeader` throws an error if it detects CRLF) or modern Java Servlet APIs, the underlying concept has evolved. 

HTTP Request Smuggling (HRS) is the modern successor. Instead of injecting into response headers to confuse the proxy about the *response* stream, HRS abuses discrepancies in how the proxy and backend parse `Content-Length` and `Transfer-Encoding` headers to confuse them about the *request* stream. Both vulnerabilities fundamentally exploit boundary desynchronization in HTTP message streams.

## Detailed Remediation and Defense Strategies

Fixing HTTP Response Splitting is conceptually simple but requires strict adherence to secure coding practices across all layers of the application stack.

### 1. Upgrade Frameworks and Servers
Rely on modern application frameworks. Frameworks like ASP.NET, Spring Boot, Django, and modern Node.js web servers inherently sanitize or throw exceptions if they detect `\r` or `\n` in header values. Ensure that you are not using outdated server software (e.g., ancient versions of Apache or Tomcat that lacked these checks).

### 2. Strict Input Validation
Never trust user input. If a header value must be dynamically generated based on user input, strictly validate the input against an allowlist of permitted characters. 
For example, if setting a language cookie based on input, ensure the input matches `^[a-zA-Z]{2,3}$`. This completely eliminates the possibility of CRLF characters entering the header.

### 3. Output Encoding
If you are writing a custom server or using a low-level language (like C or raw socket programming in Python) where you construct HTTP headers manually, you MUST URL-encode or strip any `\r` and `\n` characters before appending the string to the response stream.

### 4. Architectural Defenses
- Disable HTTP Pipelining on proxies if it is not strictly necessary.
- Transition to HTTP/2 or HTTP/3. These protocols use binary framing rather than text-based delimiters (CRLF). Because headers and bodies are transmitted in separate binary frames, classic CRLF injection and HTTP Response Splitting are structurally impossible at the protocol layer (though the proxy might still translate them back to vulnerable HTTP/1.1 requests for the backend, which requires care).

## Debugging and Detection

During a VAPT engagement, detection relies on fuzzing header-reflected parameters. 

**Payloads to test:**
- `%0d%0aInjected-Header:%20true`
- `%0d%0a%0d%0a<script>alert(1)</script>`
- `\r\nSet-Cookie: test=123`

Tools like Burp Suite Active Scanner automatically test for CRLF injection by appending `%0d%0a` followed by a unique header, and then observing if the response parses that unique header properly. If `Injected-Header: true` appears as an actual parsed header in the HTTP response tab, the vulnerability is confirmed.

## Chaining Opportunities

- **[[14 - HTTP Request Smuggling]]**: Response Splitting concepts apply heavily to Request Smuggling, where boundary confusion is weaponized.
- **[[08 - Web Cache Poisoning]]**: Response Splitting is a primary vector for achieving unauthenticated, persistent cache poisoning.
- **[[03 - Cross-Site Scripting (XSS)]]**: Provides an alternative vector for XSS when conventional body-reflection is impossible but header-reflection is present.
- **[[09 - Session Fixation]]**: Injecting a `Set-Cookie` header via response splitting to fixate a victim's session ID.

## Related Notes

- [[02 - Input Validation and Sanitization]]
- [[24 - Proxy and WAF Evasion]]
- [[12 - HTTP Protocol Fundamentals]]
- [[21 - Advanced CRLF Injection Techniques]]

---
*End of Document*
