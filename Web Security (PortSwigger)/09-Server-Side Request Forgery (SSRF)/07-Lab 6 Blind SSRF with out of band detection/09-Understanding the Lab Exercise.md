---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Understanding the Lab Exercise

In the given lab exercise, we successfully exploited a blind SSRF vulnerability using Burp Suite Professional. A blind SSRF is one where the attacker does not receive direct feedback from the server about the success of the request. Instead, the attacker relies on indirect methods to confirm the success of the attack.

### What is Blind SSRF?

Blind SSRF is a variant of SSRF where the attacker cannot directly observe the result of the server's request. This makes the exploitation more challenging but also more stealthy. The attacker typically uses out-of-band techniques to confirm the success of the attack.

### Why is Blind SSRF Important?

Blind SSRF is important because it can be used to bypass simple input validation mechanisms. Since the attacker does not receive direct feedback, traditional methods of detecting SSRF may fail. This makes blind SSRF a powerful tool for attackers to gain unauthorized access to internal networks and sensitive data.

### How Does Blind SSRF Work?

To understand how blind SSRF works, let's break down the process:

1. **Induce the Server to Make a Request**: The attacker crafts a request that causes the server to make an HTTP request to a controlled endpoint.
2. **Monitor the Controlled Endpoint**: The attacker monitors the controlled endpoint to detect whether the server made the request.
3. **Confirm the Success of the Attack**: Based on the monitoring, the attacker confirms whether the SSRF was successful.

### Example Scenario

Consider a web application that allows users to specify a URL to fetch data from. An attacker can exploit this feature to make the server fetch data from internal resources or external services.

#### Vulnerable Code Example

```python
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.text

# User-provided URL
user_url = "http://internal-service:8080/data"
data = fetch_data(user_url)
```

In this example, the `fetch_data` function takes a user-provided URL and makes an HTTP GET request to that URL. If the user provides a URL pointing to an internal service, the server will make a request to that internal service, potentially exposing sensitive data.

### Real-World Examples

Recent real-world examples of SSRF vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the Jenkins plugin that allowed attackers to perform SSRF attacks.
- **CVE-2021-3156**: A vulnerability in the Kubernetes API server that allowed attackers to perform SSRF attacks.

These vulnerabilities highlight the importance of securing applications against SSRF attacks.

---
<!-- nav -->
[[08-Testing for SSRF Vulnerabilities|Testing for SSRF Vulnerabilities]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/07-Lab 6 Blind SSRF with out of band detection/00-Overview|Overview]] | [[10-Understanding the Vulnerability|Understanding the Vulnerability]]
