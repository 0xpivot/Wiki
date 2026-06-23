---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise due to improper handling of the `Host` header in web applications. The `Host` header is a critical component of HTTP requests, specifying the domain name of the server to which the request is being sent. This header is essential for virtual hosting, where multiple websites share the same IP address but serve different content based on the requested domain.

### What is the `Host` Header?

The `Host` header is defined in the HTTP/1.1 specification (RFC 7230) and is required in all HTTP/1.1 requests. Its primary function is to identify the host and port number of the resource being requested. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this example, the `Host` header specifies that the request is intended for `www.example.com`.

### Why Does the `Host` Header Matter?

The `Host` header is crucial because it allows servers to differentiate between multiple domains hosted on the same IP address. Without the `Host` header, a server would not know which website to serve when receiving a request. However, this flexibility can also introduce security risks if the server does not properly validate or sanitize the `Host` header.

### How Does the `Host` Header Work Under the Hood?

When a client sends an HTTP request, the `Host` header is included as part of the request headers. The server uses this information to determine which virtual host should handle the request. If the server is configured to support virtual hosting, it will route the request to the appropriate site based on the `Host` header value.

### Common Pitfalls Without Proper Handling

Improper handling of the `Host` header can lead to several security issues, including:

- **Routing-Based SSRF (Server-Side Request Forgery)**: An attacker can manipulate the `Host` header to make the server send requests to unintended destinations.
- **DNS Rebinding**: An attacker can use the `Host` header to bypass Same-Origin Policy restrictions by changing the IP address associated with a domain.
- **Virtual Host Poisoning**: An attacker can trick the server into serving content from a different virtual host than intended.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A vulnerability in Apache Tomcat allowed attackers to bypass virtual host restrictions by manipulating the `Host` header.
- **CVE-2020-14882**: A vulnerability in Nginx allowed attackers to bypass virtual host restrictions and access sensitive resources.

These examples highlight the importance of proper handling of the `Host` header to prevent such attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/05-Lab 4 Routing based SSRF/00-Overview|Overview]] | [[02-Lab 4 Routing-Based SSRF|Lab 4 Routing-Based SSRF]]
