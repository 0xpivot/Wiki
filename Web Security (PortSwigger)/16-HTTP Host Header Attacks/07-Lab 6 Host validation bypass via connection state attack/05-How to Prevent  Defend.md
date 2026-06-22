---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## How to Prevent / Defend

### Detection

To detect `Host` header manipulation attacks, implement logging and monitoring of HTTP requests. Look for unusual `Host` header values that do not match the expected domain names.

### Prevention

To prevent `Host` header manipulation attacks, ensure proper validation of the `Host` header. Here are some steps to take:

1. **Whitelist Trusted Domains**: Only allow requests with `Host` headers that match a predefined list of trusted domains.
2. **Strict Validation**: Implement strict validation of the `Host` header to ensure it matches the expected format and domain.
3. **Use HTTPS**: Enforce HTTPS to prevent man-in-the-middle attacks that could manipulate the `Host` header.

### Secure Coding Fixes

Here is an example of how to securely validate the `Host` header in a web application:

```python
def validate_host_header(request):
    trusted_domains = ["example.com", "subdomain.example.com"]
    host_header = request.headers.get("Host")
    
    if host_header not in trusted_domains:
        raise ValueError("Invalid Host header")

# Example usage
try:
    validate_host_header(request)
except ValueError as e:
    print(e)
```

### Configuration Hardening

Ensure that your web server configuration is hardened to prevent `Host` header manipulation attacks. Here is an example of how to configure Nginx to enforce strict validation of the `Host` header:

```nginx
server {
    listen 80;
    server_name example.com subdomain.example.com;

    location / {
        if ($host !~* ^(example\.com|subdomain\.example\.com)$ ) {
            return 444;
        }
        # Other configurations
    }
}
```

### Mitigations

Implement the following mitigations to further protect against `Host` header manipulation attacks:

1. **Use Content Security Policy (CSP)**: Implement CSP to restrict the sources of content that can be loaded by the browser.
2. **Enable HSTS**: Enable HTTP Strict Transport Security (HSTS) to enforce HTTPS connections.
3. **Regular Audits**: Conduct regular security audits to identify and mitigate potential vulnerabilities.

---
<!-- nav -->
[[04-HTTP Host Header Attacks|HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/07-Lab 6 Host validation bypass via connection state attack/06-Practice Labs|Practice Labs]]
