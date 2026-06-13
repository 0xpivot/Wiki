---
tags: [vapt, information-disclosure, reconnaissance, network, headers, beginner]
difficulty: beginner
module: "33 - Information Disclosure"
topic: "33.09 Internal IP Disclosure in Headers"
---

# 09 - Internal IP Disclosure in Headers

## Introduction

Internal IP Disclosure occurs when a web application, API, or its underlying infrastructure inadvertently leaks internal network IP addresses (e.g., `10.x.x.x`, `192.168.x.x`, `172.16.x.x`) or internal hostnames to external clients. 

While an internal IP address alone is not an immediate compromise, it is a highly valuable piece of reconnaissance telemetry. It provides attackers with a glimpse behind the firewall, revealing the topological structure of the backend network, the presence of load balancers, and the internal routing mechanisms. This information is critical when attempting to bypass Web Application Firewalls (WAFs), construct Server-Side Request Forgery (SSRF) payloads, or execute lateral movement post-exploitation.

## Core Mechanisms of Internal IP Leakage

Modern web architecture rarely exposes the application server directly to the internet. Instead, traffic routes through CDNs, WAFs, Load Balancers, and Reverse Proxies. Misconfigurations in how these intermediaries communicate, handle legacy HTTP protocols, or manage session persistence frequently lead to internal IP leakage.

### ASCII Diagram: Internal IP Leak via HTTP/1.0 Host Omission

```text
+---------------------+                                       +-------------------------+
|                     |     1. GET /images HTTP/1.0           |                         |
|   Attacker          |     (No Host Header)                  |    Reverse Proxy /      |
|                     |  -----------------------------------> |    Load Balancer        |
|                     |                                       |                         |
+---------------------+                                       +-------------------------+
         |                                                                |
         |                                                                | 2. Proxies request
         |                                                                v
         |                                                    +-------------------------+
         |                                                    |                         |
         |                  3. HTTP/1.1 301 Moved Permanently |    Backend Web Server   |
         |                     Location: http://10.0.5.22/    |    (IIS / Apache)       |
         |                     Content-Length: 0              |    Internal IP:         |
         |  <------------------------------------------------ |    10.0.5.22            |
         v                                                    +-------------------------+
+---------------------+
|   Internal IP       |
|   Extracted!        |
|   (10.0.5.22)       |
+---------------------+
```

## Specific Vectors and Exploitation Techniques

Internal IP disclosures are not always obvious. They often require specific protocol manipulations or deep inspection of seemingly random headers.

### Vector 1: The Missing Host Header (HTTP/1.0 Fallback)
In HTTP/1.1, the `Host` header is mandatory. However, in legacy HTTP/1.0 requests, it is optional. When a server receives an HTTP/1.0 request without a Host header for a directory that requires a trailing slash (e.g., requesting `/images` instead of `/images/`), the server issues a `301` or `302` redirect. 

Because the server has no `Host` header to construct the absolute URL for the `Location` header, older versions of IIS and Apache fall back to using their own internal, bound IP address.

**The Attack Request:**
```http
GET /assets HTTP/1.0
[Empty Line]
```

**The Vulnerable Response:**
```http
HTTP/1.1 301 Moved Permanently
Date: Tue, 09 Jun 2026 12:00:00 GMT
Server: Microsoft-IIS/8.5
Location: http://192.168.1.100/assets/
```

### Vector 2: Reverse Proxy and Load Balancer Headers
Load balancers often inject custom headers for debugging, routing, or maintaining session affinity (sticky sessions). If these headers are not stripped before the response is sent back to the client, they leak backend infrastructure details.

*   `X-Internal-IP: 10.0.0.4`
*   `X-Backend-Server: webnode-04.internal.local`
*   `X-Forwarded-Server: 172.16.5.12`

### Vector 3: F5 BIG-IP Cookie Decoding
F5 BIG-IP load balancers use specific cookies to maintain session persistence. By default, the value of this cookie is an encoded representation of the backend server's internal IP and port. 

*Example Cookie:* `Set-Cookie: BIGipServerpool_app=1677787402.36895.0000; path=/`

Attackers can reverse engineer this cookie using a known algorithmic decoding process:
1.  Extract the first segment: `1677787402`
2.  Convert to Hex: `0x6400000A`
3.  Reverse the byte order (Little Endian to Big Endian): `0x0A000064`
4.  Convert bytes to decimal IP format: `10.0.0.100`

### Vector 4: NTLM / Windows Integrated Authentication
When encountering a web application utilizing NTLM authentication (returning `WWW-Authenticate: NTLM`), attackers can initiate the handshake to force the server to disclose internal naming schemas.

By sending an empty NTLM Type 1 message, the server responds with a Type 2 message containing internal Active Directory domain names, internal NetBIOS names, and occasionally the internal IP.

**Request:**
```http
GET /admin HTTP/1.1
Host: target.com
Authorization: NTLM TlRMTVNTUAABAAAAB4IIAAAAAAAAAAAAAAAAAAAAAAA=
```

**Response:**
```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: NTLM TlRMTVNTUAACAAAABgBGADgAAAAF...[Base64 Data]...
```
Decoding the Base64 Type 2 message frequently reveals information like `CORP-DC01.internal.corp.com`.

## Weaponizing Internal IPs

Why do penetration testers care about internal IPs?

1.  **SSRF Exploitation:** If an application is vulnerable to Server-Side Request Forgery (`[[02 - SSRF]]`), the attacker now knows exactly which IP subnets to target to hit internal administrative panels, databases, or cloud metadata endpoints.
2.  **WAF Bypassing:** Some misconfigured Web Application Firewalls trust requests originating from "internal" networks. An attacker might spoof the `X-Forwarded-For` header using the discovered internal IP to bypass rate limits or access controls.
    `X-Forwarded-For: 10.0.5.22`
3.  **Post-Exploitation Network Pivoting:** If an attacker achieves Remote Code Execution (RCE), they do not need to blindly scan the network; they already know the layout of the DMZ and backend subnets.

## Defense and Remediation

Fixing internal IP leaks requires configuring front-end proxies to scrub outbound responses and ensuring backend servers utilize appropriate routing headers.

1.  **Configure IIS to use Hostnames:** In IIS, ensure that the "Use Host name for redirects" option is enabled. Alternately, use URL Rewrite rules to strip internal IPs from the `Location` header.
2.  **Scrub Debug Headers:** Configure Nginx or HAProxy to explicitly remove sensitive backend headers before sending the response to the client.
    ```nginx
    # Nginx snippet
    proxy_hide_header X-Internal-IP;
    proxy_hide_header X-Backend-Server;
    ```
3.  **Encrypt Load Balancer Cookies:** For F5 BIG-IP, administrators must configure the persistence profile to encrypt the session cookies rather than using the default Base10 encoding.
4.  **Enforce HTTP/1.1 Host Headers:** Configure the web server to reject HTTP/1.0 requests that lack a proper `Host` header, forcing a `400 Bad Request` instead of executing a redirect.

## Chaining Opportunities

Internal IP Disclosure acts as a powerful reconnaissance enabler for more critical vulnerabilities.
*   **[[02 - Server-Side Request Forgery SSRF]]:** The primary exploitation path for leveraging internal IP knowledge.
*   **[[04 - Host Header Injection]]:** Knowing the internal network architecture assists in crafting malicious Host headers for cache poisoning or password reset poisoning.
*   **[[08 - Version Disclosure]]:** Combining internal hostnames and version disclosures paints a complete picture of the target's infrastructure.

## Related Notes
*   [[01 - Introduction to Information Disclosure]]
*   [[02 - Infrastructure Reconnaissance]]
*   [[07 - Backup Files Exposed]]

---
*End of Note*
