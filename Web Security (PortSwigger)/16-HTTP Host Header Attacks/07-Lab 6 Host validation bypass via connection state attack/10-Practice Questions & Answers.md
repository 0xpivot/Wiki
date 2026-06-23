---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a connection state attack in the context of host validation bypass.**

A connection state attack exploits the assumption made by some servers that all requests within the same connection share the same host header. Typically, the server performs host header validation only on the first request of a connection. Subsequent requests are assumed to be for the same host, thus bypassing further validation checks. This allows attackers to inject malicious host headers in later requests to access internal resources or perform SSRF attacks.

**Q2. How would you exploit a connection state attack to perform an SSRF attack?**

To exploit a connection state attack for an SSRF attack, follow these steps:

1. **Initial Valid Request**: Send a request with a valid host header to establish a connection.
2. **Subsequent Malicious Request**: In the same connection, send a second request with a modified host header pointing to an internal server or resource.
3. **Exploit**: Since the server assumes all requests in the same connection are for the same host, the second request bypasses the host validation and allows access to the internal resource.

For example, using Burp Suite:
```plaintext
# Initial request with valid host header
GET / HTTP/1.1
Host: example.com

# Second request with modified host header
GET /admin HTTP/1.1
Host: 192.168.1.1
```

**Q3. Why is it important to ensure that host header validation is performed on every request rather than just the first request in a connection?**

Performing host header validation on every request ensures that each request is independently verified against potential security threats. Relying solely on the first request's validation can lead to vulnerabilities like connection state attacks, where an attacker can exploit the assumption that all requests in the same connection are for the same host. This can result in unauthorized access to internal resources or SSRF attacks.

**Q4. How does the presence of intermediary systems like load balancers or reverse proxies affect the vulnerability to connection state attacks?**

Intermediary systems like load balancers or reverse proxies often rely on the host header to route requests to the appropriate backend server. If these systems assume that all requests in the same connection are intended for the same host and only validate the host header for the first request, they become susceptible to connection state attacks. An attacker can exploit this behavior by sending a valid initial request followed by a malicious request with a different host header, bypassing the validation mechanism.

**Q5. What recent real-world examples or CVEs demonstrate the impact of connection state attacks?**

One notable example is CVE-2021-21972, which affected several versions of the Apache HTTP Server. This vulnerability allowed attackers to bypass host header validation by exploiting the assumption that all requests in the same connection share the same host. By sending a valid initial request followed by a malicious request, attackers could access internal resources or perform SSRF attacks, leading to unauthorized data exposure or service disruption.

**Q6. How would you configure a server to mitigate the risk of connection state attacks?**

To mitigate the risk of connection state attacks, configure the server to perform host header validation on every request, not just the first request in a connection. This can be achieved by:

1. **Disabling Persistent Connections**: Disable persistent connections (HTTP keep-alive) to ensure each request is treated independently.
2. **Strict Validation**: Implement strict validation logic that checks the host header for each incoming request.
3. **Middleware Configuration**: Use middleware or plugins that enforce host header validation for every request, regardless of the connection state.

Example configuration in Nginx:
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        if ($host != 'example.com') {
            return 403;
        }
        # Other configurations
    }
}
```

This ensures that the host header is validated for each request, preventing attackers from exploiting connection state assumptions.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/00-Overview|Overview]]
