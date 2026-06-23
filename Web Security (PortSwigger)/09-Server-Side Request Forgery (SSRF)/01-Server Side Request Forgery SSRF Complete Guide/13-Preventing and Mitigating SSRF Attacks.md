---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Preventing and Mitigating SSRF Attacks

Now that you understand how to identify and exploit SSRF vulnerabilities, the final step is to learn how to prevent and mitigate these attacks. This section covers various techniques and best practices for securing your applications against SSRF attacks.

### Best Practices for Preventing SSRF

To prevent SSRF attacks, you should follow these best practices:

1. **Input Validation**: Validate and sanitize all user inputs to ensure they meet expected formats and constraints.
2. **Whitelist External Domains**: Only allow requests to a predefined list of trusted domains.
3. **Use HTTP Proxies**: Configure HTTP proxies to restrict outgoing requests to specific domains.
4. **Network Segmentation**: Ensure that internal resources are not accessible from the internet.
5. **Secure Coding Practices**: Follow secure coding guidelines to avoid common pitfalls.

#### Example: Input Validation

Here is an example of how to implement input validation in Python:

```python
import requests
from urllib.parse import urlparse

def fetch_data(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme in ['http', 'https'] and parsed_url.hostname == 'trusted-domain.com':
        response = requests.get(url)
        return response.text
    else:
        raise ValueError("Invalid URL")
```

In this code, the `fetch_data` function validates the `url` parameter to ensure it only points to a trusted domain.

### Mitigation Techniques

Even if you cannot completely prevent SSRF attacks, you can mitigate their impact by implementing the following techniques:

1. **Rate Limiting**: Implement rate limiting to prevent attackers from overwhelming internal services with requests.
2. **Logging and Monitoring**: Log and monitor all external requests to detect and respond to potential SSRF attacks.
3. **Firewall Rules**: Configure firewall rules to block requests to internal IP addresses and services.
4. **Security Audits**: Regularly perform security audits to identify and fix potential SSRF vulnerabilities.

#### Example: Rate Limiting

Here is an example of how to implement rate limiting in Python using the `ratelimiter` library:

```python
from ratelimiter import RateLimiter

@RateLimiter(max_calls=100, period=60)
def fetch_data(url):
    response = requests.get(url)
    return response.text
```

In this code, the `fetch_data` function is rate-limited to 100 calls per minute, preventing attackers from overwhelming internal services with requests.

### Conclusion

Preventing and mitigating SSRF attacks requires a combination of input validation, network segmentation, and secure coding practices. By following these best practices and implementing mitigation techniques, you can significantly reduce the risk of SSRF attacks.

---
<!-- nav -->
[[12-Port Scanning with SSRF|Port Scanning with SSRF]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[14-Real-World Examples|Real-World Examples]]
