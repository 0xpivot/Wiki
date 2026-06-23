---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## How to Prevent / Defend Against SSRF

### Detection

To detect SSRF vulnerabilities, organizations can use automated scanning tools like Burp Suite, OWASP ZAP, or commercial solutions like Veracode. These tools can help identify potential SSRF attack vectors.

### Prevention

#### Input Validation

Ensure that all user-provided inputs are validated and sanitized before being used to construct URLs. This includes checking for valid domain names and IP addresses.

```python
import re

def validate_url(url):
    pattern = re.compile(
        r'^https?://'  # scheme
        r'([A-Za-z0-9.-]+)'  # domain
        r'(:\d+)?'  # port
        r'(\/[^\s]*)?$'  # path
    )
    return bool(pattern.match(url))

url = "http://example.com"
if validate_url(url):
    print("Valid URL")
else:
    print("Invalid URL")
```

#### Whitelisting Domains

Restrict the server to only access whitelisted domains. This can be achieved by configuring the application to only accept URLs from a predefined list.

```json
{
  "allowedDomains": [
    "example.com",
    "subdomain.example.com"
  ]
}
```

#### Network Segmentation

Implement network segmentation to isolate internal resources from external access. This can be done using firewalls and network policies.

### Secure Coding Practices

Developers should follow secure coding practices to prevent SSRF vulnerabilities. This includes validating user input, restricting access to internal resources, and using secure libraries and frameworks.

### Hands-On Labs

To practice SSRF testing, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on SSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.
- **WebGoat**: An interactive training application designed to teach web security principles.

By thoroughly understanding SSRF vulnerabilities and implementing robust defenses, organizations can significantly reduce the risk of these attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/10-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[12-Port Scanning with SSRF|Port Scanning with SSRF]]
