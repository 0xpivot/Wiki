---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Server-Side Request Forgery (SSRF)

### Introduction to SSRF

Server-Side Request Forgery (SSRF) is a type of web security vulnerability that allows an attacker to induce the server-side application to make HTTP requests to an arbitrary domain of the attacker’s choosing. This can lead to unauthorized data exfiltration, internal network reconnaissance, and even remote code execution. SSRF vulnerabilities arise due to improper input validation and lack of proper security controls when the server makes requests to other systems.

### Understanding Internal IP Address Blacklisting

One common defense mechanism against SSRF is to blacklist internal IP addresses. This means that the server will reject any requests that target IP addresses within a specific range, typically reserved for internal networks (e.g., `127.0.0.1`, `192.168.x.x`, etc.). However, attackers can bypass these blacklists using various techniques.

#### Decimal Encoding of Localhost

One such technique involves using the decimal encoding of the localhost IP address (`127.0.0.1`). Instead of using the standard format, attackers can represent the IP address as a large integer. For example, `127.0.0.1` can be represented as `2130706433`.

```http
GET http://2130706433/
```

When the server processes this request, it resolves the integer back to `127.0.0.1`. This bypasses the blacklist because the server does not recognize the integer as an internal IP address.

#### Partial IP Address Representation

Another technique involves using partial IP addresses. For instance, instead of using the full `127.0.0.1`, an attacker might use `127.1`. The server will automatically fill in the missing octets with zeros, resolving to `127.0.0.1`.

```http
GET http://127.1/
```

This method also bypasses the blacklist since the server does not match the partial IP address against the full list of internal IP addresses.

#### Octal Representation

Yet another technique involves using the octal representation of the localhost IP address. The octal form of `127.0.0.1` is `0177.0.0.1`.

```http
GET http://0177.0.0.1/
```

The server will interpret this octal representation and resolve it to `127.0.0.1`, effectively bypassing the blacklist.

### Real-World Examples and Recent Breaches

Recent real-world examples of SSRF vulnerabilities include:

- **CVE-2021-21972**: A SSRF vulnerability was found in the Jenkins plugin for GitLab. An attacker could exploit this vulnerability to read sensitive files from the server.
- **CVE-2021-3504**: A SSRF vulnerability in the Kubernetes API server allowed attackers to read secrets stored in etcd.

These vulnerabilities highlight the importance of implementing robust defenses against SSRF attacks.

### How to Prevent / Defend Against SSRF

#### Detection

To detect SSRF vulnerabilities, organizations should implement logging and monitoring mechanisms to track HTTP requests made by the server. Any unexpected requests to internal IP addresses or unusual patterns should be flagged for further investigation.

#### Prevention

Preventing SSRF requires a combination of input validation, proper security controls, and network segmentation.

##### Input Validation

Ensure that user inputs are properly validated and sanitized. For example, if the server expects a URL, validate that the URL is external and not internal.

```python
import re

def validate_url(url):
    pattern = r'^https?://(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

url = "http://example.com"
if validate_url(url):
    print("Valid URL")
else:
    print("Invalid URL")
```

##### Network Segmentation

Implement network segmentation to isolate internal services from external access. This ensures that even if an SSRF vulnerability is exploited, the attacker cannot access critical internal resources.

##### Secure Coding Practices

Use secure coding practices to ensure that the server does not make requests to untrusted sources. For example, avoid using user-provided input directly in HTTP requests.

```python
import requests

def fetch_data(url):
    if validate_url(url):
        response = requests.get(url)
        return response.text
    else:
        return "Invalid URL"

url = "http://example.com"
print(fetch_data(url))
```

### Complete Example of Vulnerable and Secure Code

#### Vulnerable Code

```python
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.text

url = "http://127.0.0.1"
print(fetch_data(url))
```

#### Secure Code

```python
import requests
import re

def validate_url(url):
    pattern = r'^https?://(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))

def fetch_data(url):
    if validate_url(url):
        response = requests.get(url)
        return response.text
    else:
        return "Invalid URL"

url = "http://example.com"
print(fetch_data(url))
```

### Hands-On Labs

For hands-on practice with SSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive SSRF module with interactive challenges.
- **OWASP Juice Shop**: Contains several SSRF-related challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including SSRF.

### Conclusion

Server-Side Request Forgery (SSRF) is a serious web security vulnerability that can have severe consequences if not properly mitigated. By understanding the techniques used to bypass blacklists and implementing robust defenses, organizations can significantly reduce the risk of SSRF attacks. Regularly testing and validating inputs, along with proper network segmentation and secure coding practices, are essential steps in preventing SSRF vulnerabilities.

---
<!-- nav -->
[[15-Sanitization and Validation of Client-Supplied Input Data|Sanitization and Validation of Client-Supplied Input Data]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[17-Testing for SSRF Vulnerabilities|Testing for SSRF Vulnerabilities]]
