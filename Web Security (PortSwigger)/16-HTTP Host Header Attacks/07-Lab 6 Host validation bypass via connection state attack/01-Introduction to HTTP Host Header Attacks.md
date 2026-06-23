---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise due to improper handling or validation of the `Host` header in HTTP requests. The `Host` header is a crucial part of the HTTP protocol, used to identify the domain name of the server being contacted. This header is essential for virtual hosting, where multiple websites share the same IP address but are distinguished by their domain names.

### What is the `Host` Header?

The `Host` header is defined in the HTTP/1.1 specification (RFC 7230) and is required in all HTTP/1.1 requests. Its primary function is to specify the Internet host and port number of the resource being requested. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this example, the client is requesting the `/index.html` resource from the server identified by `www.example.com`.

### Why Does the `Host` Header Matter?

The `Host` header is critical because it allows servers to serve multiple domains from a single IP address. Without proper validation of the `Host` header, attackers can manipulate it to achieve various malicious objectives, such as Server-Side Request Forgery (SSRF), Cross-Site Scripting (XSS), and more.

### Real-World Example: CVE-2021-21972

One notable real-world example of a `Host` header vulnerability is CVE-2021-21972, which affected the Apache HTTP Server. This vulnerability allowed attackers to bypass certain security restrictions by manipulating the `Host` header. Specifically, the issue was related to how the server handled the `Host` header when processing requests.

### Lab Overview: Host Validation Bypass via Connection State Attack

In this lab, we will explore a specific type of `Host` header attack known as a "Connection State Attack." The lab is designed to demonstrate how an attacker can exploit the assumption made by the server about the `Host` header across multiple requests within the same connection.

### Lab Setup

To access the lab, follow these steps:

1. Visit the URL: `https://portswigger.net/web-security`.
2. Sign up for an account if you haven't already.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select "All Content" and then "All Labs."
6. Search for "host-based header attacks."
7. Click on "Lab Number Six: Host Validation Bypass via Connection State Attack."

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/02-Common Pitfalls and Mistakes|Common Pitfalls and Mistakes]]
