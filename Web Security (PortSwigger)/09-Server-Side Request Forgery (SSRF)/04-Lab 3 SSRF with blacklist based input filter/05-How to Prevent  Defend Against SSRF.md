---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## How to Prevent / Defend Against SSRF

### Prevention Strategies

To prevent SSRF vulnerabilities, implement the following strategies:

- **Whitelist-Based Validation**: Use whitelists to allow only trusted domains and IP addresses.
- **Input Sanitization**: Sanitize user input to remove malicious patterns.
- **Rate Limiting**: Implement rate limiting to prevent abuse.
- **Network Segmentation**: Segment networks to limit access to internal systems.

### Secure Coding Fixes

Show both the vulnerable and secure versions of the code side by side.

#### Vulnerable Code

```python
def check_stock(url):
    response = requests.get(url)
    return response.text
```

#### Secure Code

```python
import requests

def check_stock(url):
    allowed_domains = ["example.com"]
    parsed_url = urlparse(url)
    if parsed_url.hostname not in allowed_domains:
        raise ValueError("Invalid domain")
    response = requests.get(url)
    return response.text
```

### Configuration Hardening

Harden configurations to prevent SSRF attacks:

#### Nginx Configuration

```nginx
location /stock-check {
    deny all;
}
```

#### Apache Configuration

```apache
<Directory "/path/to/stock-check">
    Order Deny,Allow
    Deny from all
</Directory>
```

### Mitigations

Implement additional mitigations to further protect against SSRF:

- **Firewall Rules**: Configure firewall rules to block outgoing requests to internal IP addresses.
- **Network Policies**: Implement network policies to restrict access to internal systems.

### Complete Example: Full HTTP Request and Response

#### HTTP Request

```http
GET /stock-check?url=http://localhost/admin HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Admin Interface</title>
</head>
<body>
    <!-- Admin interface content -->
</body>
</html>
```

### Practice Labs

For hands-on practice, use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of SSRF labs to practice and learn.
- **OWASP Juice Shop**: Provides a web application with numerous security vulnerabilities, including SSRF.
- **DVWA**: A deliberately insecure web application for practicing web security skills.

By thoroughly understanding SSRF vulnerabilities, their causes, and effective mitigation strategies, you can significantly enhance the security of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/04-Common Pitfalls and Detection|Common Pitfalls and Detection]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/00-Overview|Overview]] | [[06-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]]
