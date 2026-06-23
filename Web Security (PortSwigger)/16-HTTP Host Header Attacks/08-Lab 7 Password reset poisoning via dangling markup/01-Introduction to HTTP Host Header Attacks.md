---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks

HTTP Host Header attacks are a class of vulnerabilities that arise due to improper handling of the `Host` header in HTTP requests. The `Host` header is used by the server to determine which website or application to serve when multiple domains are hosted on the same IP address. This header is crucial for virtual hosting but can also be manipulated by attackers to exploit various vulnerabilities.

### What is the `Host` Header?

The `Host` header is a mandatory part of HTTP/1.1 requests. It specifies the domain name or IP address of the server being requested. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this request, the server will interpret the request as intended for `www.example.com`.

### Why Does the `Host` Header Matter?

Improper validation or sanitization of the `Host` header can lead to several types of attacks, including:

- **Virtual Host Hijacking**: An attacker can manipulate the `Host` header to make the server serve content from a different virtual host.
- **Cross-Site Scripting (XSS)**: By injecting malicious content through the `Host` header, an attacker can execute scripts in the context of the victim’s browser.
- **Password Reset Poisoning**: This specific attack vector involves manipulating the `Host` header to hijack password reset emails.

### Real-World Examples

One notable example of a `Host` header attack is the CVE-2020-14182, which affected Apache Tomcat servers. Attackers could exploit this vulnerability to bypass authentication mechanisms by manipulating the `Host` header.

Another example is the CVE-2021-21972, which affected Microsoft Exchange Server. This vulnerability allowed attackers to manipulate the `Host` header to gain unauthorized access to the server.

### Lab Setup

To practice these concepts, you can use the PortSwigger Web Security Academy. Here’s how to set up the lab:

1. Visit [PortSwigger.net/WebSecurity](https://portswigger.net/web-security).
2. Click on the "Sign Up" button to create an account.
3. Once logged in, navigate to the "Academy" section.
4. Select "All Content" and then "All Labs".
5. Search for "Host Header Attacks" and find Lab 7 titled "Password Reset Poisoning via Dangling Markup".

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/08-Lab 7 Password reset poisoning via dangling markup/00-Overview|Overview]] | [[02-How to Prevent  Defend Against Password Reset Poisoning|How to Prevent  Defend Against Password Reset Poisoning]]
