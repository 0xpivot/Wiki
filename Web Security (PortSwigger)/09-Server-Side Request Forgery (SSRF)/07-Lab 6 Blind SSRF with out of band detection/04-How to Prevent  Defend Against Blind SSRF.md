---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## How to Prevent / Defend Against Blind SSRF

### Secure Coding Practices

1. **Validate Input**: Ensure that any user-provided input is validated and sanitized before being used to construct HTTP requests.
2. **Whitelist Domains**: Only allow requests to a predefined list of trusted domains.
3. **Use HTTPS**: Ensure that all requests are made over HTTPS to prevent man-in-the-middle attacks.

### Configuration Hardening

1. **Firewall Rules**: Implement strict firewall rules to block outgoing requests to untrusted domains.
2. **Network Segmentation**: Segment the network to limit the scope of potential damage from SSRF attacks.

### Secure Code Examples

#### Vulnerable Code

```python
import requests

def fetch_product_details(referer):
    response = requests.get('http://internal-api.com', headers={'Referer': referer})
    return response.text
```

#### Secure Code

```python
import requests

def fetch_product_details(referer):
    if not referer.startswith('http://trusted-domain.com'):
        raise ValueError("Invalid Referer header")
    response = requests.get('http://internal-api.com', headers={'Referer': referer})
    return response.text
```

### Detection and Prevention Tools

1. **Static Analysis Tools**: Use static analysis tools like SonarQube or Fortify to identify potential SSRF vulnerabilities in code.
2. **Dynamic Analysis Tools**: Use dynamic analysis tools like Burp Suite or ZAP to test for SSRF vulnerabilities during runtime.
3. **Web Application Firewalls (WAF)**: Deploy WAFs to monitor and block suspicious outgoing requests.

### Practice Labs

To practice and gain hands-on experience with SSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on different types of SSRF attacks.
- **OWASP Juice Shop**: A deliberately insecure web application that includes SSRF vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice SSRF exploitation.

By thoroughly understanding the concepts, techniques, and defenses related to SSRF, you can better protect web applications from these types of attacks.

---
<!-- nav -->
[[03-Exploiting Blind SSRF Using Burp Suite Professional|Exploiting Blind SSRF Using Burp Suite Professional]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/05-How to Prevent  Defend Against SSRF|How to Prevent  Defend Against SSRF]]
