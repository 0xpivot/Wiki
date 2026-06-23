---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Real-World Examples

### Recent CVEs and Breaches

One notable example of an SSRF vulnerability is CVE-2021-21972, which affected the Jenkins pipeline plugin. An attacker could exploit this vulnerability to perform SSRF attacks, leading to unauthorized access to internal networks and sensitive data.

Another example is the SSRF vulnerability in the Docker API, which allowed attackers to read arbitrary files from the host system. This vulnerability was exploited in several high-profile breaches, including the compromise of the Travis CI build system.

### How to Prevent / Defend

#### Detection

To detect SSRF vulnerabilities, you can use tools like Burp Suite, ZAP, and OWASP Dependency-Check. These tools can help identify potential SSRF vulnerabilities by analyzing HTTP requests and responses.

#### Prevention

1. **Input Validation**: Validate and sanitize all inputs that could be used to construct URLs. Ensure that only trusted domains are allowed.
2. **Whitelist Domains**: Maintain a whitelist of allowed domains and reject any requests to untrusted domains.
3. **Use Secure Headers**: Implement secure headers such as `Content-Security-Policy` to restrict the sources of content that can be loaded by the browser.
4. **Network Segmentation**: Segment the network to limit the exposure of internal services to the internet.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```python
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.text
```

**Secure Code**

```python
import requests

def fetch_data(url):
    allowed_domains = ['example.com', 'trusteddomain.com']
    if any(domain in url for domain in allowed_domains):
        response = requests.get(url)
        return response.text
    else:
        raise ValueError("Invalid domain")
```

### Configuration Hardening

Ensure that your web server and application configurations are hardened against SSRF attacks. For example, configure your web server to reject requests to internal IP addresses and use firewall rules to block unauthorized outbound traffic.

### Conclusion

Server-Side Request Forgery (SSRF) is a serious web application vulnerability that can lead to unauthorized access to internal networks and sensitive data. By understanding the different types of SSRF attacks and implementing proper detection and prevention measures, you can protect your applications from these vulnerabilities.

### Practice Labs

For hands-on practice with SSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive SSRF module with interactive challenges.
- **OWASP Juice Shop**: Contains several SSRF vulnerabilities that can be exploited and fixed.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including SSRF.

By completing these labs, you can gain practical experience in identifying and mitigating SSRF vulnerabilities.

---
<!-- nav -->
[[06-Lab Setup and Tools|Lab Setup and Tools]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[08-Testing for SSRF Vulnerabilities|Testing for SSRF Vulnerabilities]]
