---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## How to Prevent / Defend Against SSRF

Preventing SSRF attacks requires a combination of input validation, network segmentation, and proper configuration of web applications. Here are some best practices:

### Input Validation

Validate and sanitize all user inputs to ensure they do not contain malicious URLs. Use a whitelist approach to allow only trusted domains.

#### Secure Code Example

```python
import requests
from urllib.parse import urlparse

def fetch_data(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        raise ValueError("Invalid scheme")
    if parsed_url.netloc not in ['trusted-domain.com']:
        raise ValueError("Invalid domain")
    response = requests.get(url)
    return response.text

# User-provided URL
user_url = "http://trusted-domain.com/data"
data = fetch_data(user_url)
```

In this example, the `fetch_data` function validates the URL to ensure it only contains trusted domains.

### Network Segmentation

Segment the network to limit the ability of the server to make requests to internal resources. Use firewalls and network policies to restrict outbound traffic.

### Proper Configuration

Properly configure web applications to prevent SSRF attacks. Disable features that are not needed, such as DNS resolution on the server.

### Detection

Detect SSRF attacks by monitoring network traffic and looking for unusual patterns. Use intrusion detection systems (IDS) to identify suspicious activity.

### Prevention

Prevent SSRF attacks by implementing the following measures:

- **Input Validation**: Validate all user inputs to ensure they do not contain malicious URLs.
- **Network Segmentation**: Segment the network to limit the ability of the server to make requests to internal resources.
- **Proper Configuration**: Properly configure web applications to prevent SSRF attacks.

### Secure Coding Practices

Implement secure coding practices to prevent SSRF attacks. Use libraries and frameworks that provide built-in protection against SSRF.

#### Example Secure Code

```python
import requests
from urllib.parse import urlparse

def fetch_data(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        raise ValueError("Invalid scheme")
    if parsed_url.netloc not in ['trusted-domain.com']:
        raise ValueError("Invalid domain")
    response = requests.get(url)
    return response.text

# User-provided URL
user_url = "http://trusted-domain.com/data"
data = fetch_data(user_url)
```

In this example, the `fetch_data` function validates the URL to ensure it only contains trusted domains.

### Conclusion

Server-Side Request Forgery (SSRF) is a serious web application vulnerability that can be exploited to gain unauthorized access to internal networks and sensitive data. By understanding the concepts, techniques, and best practices for preventing SSRF attacks, you can secure your web applications against these threats.

### Further Reading and Practice Labs

For further reading and practice, consider the following resources:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web security, including SSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: A deliberately insecure Java web application maintained by OWASP for learning web security.

By practicing with these resources, you can gain hands-on experience in identifying and mitigating SSRF vulnerabilities.

---

This chapter provides a comprehensive overview of Server-Side Request Forgery (SSRF), including detailed explanations, real-world examples, code snippets, and diagrams. It covers the concepts, techniques, and best practices for preventing SSRF attacks, ensuring a deep understanding of the topic.

---
<!-- nav -->
[[04-How to Prevent  Defend Against Blind SSRF|How to Prevent  Defend Against Blind SSRF]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[06-Lab Setup and Tools|Lab Setup and Tools]]
