---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Introduction to Server-Side Request Forgery (SSRF)

Server-Side Request Forgery (SSRF) is a type of web application vulnerability that allows an attacker to induce the server into making HTTP requests to an arbitrary domain of the attacker’s choosing. This can lead to unauthorized access to internal systems, sensitive data exfiltration, and even remote code execution. SSRF vulnerabilities arise due to improper validation and sanitization of user input used in server-side requests.

### What is SSRF?

SSRF occurs when an application uses untrusted input to make a request to an external resource. The attacker can manipulate this input to point to internal resources, such as localhost or other internal IP addresses, which are typically not accessible from the outside. This can result in the attacker gaining access to internal services, databases, or other critical infrastructure.

### Why Does SSRF Matter?

SSRF is significant because it can bypass traditional network security measures like firewalls and intrusion detection systems. Since the requests originate from within the trusted environment, they often pass unnoticed. Additionally, SSRF can be used to perform reconnaissance, exfiltrate data, and even execute commands on internal systems.

### How Does SSRF Work Under the Hood?

To understand SSRF, consider a web application that allows users to check the stock levels of products by providing a URL to an external inventory system. If the application does not properly validate the URL provided by the user, an attacker could supply a URL pointing to an internal service, such as `http://localhost/admin`.

#### Example Scenario

Imagine a web application with a stock check feature:

```python
def check_stock(url):
    response = requests.get(url)
    return response.text
```

If an attacker provides `http://localhost/admin`, the server will make a request to the local admin interface, potentially exposing sensitive information.

### Real-World Examples of SSRF

Recent real-world examples of SSRF vulnerabilities include:

- **CVE-2020-14182**: A vulnerability in the Jenkins plugin allowed attackers to perform SSRF attacks, leading to unauthorized access to internal systems.
- **CVE-2021-21972**: A vulnerability in the GitLab API allowed attackers to perform SSRF attacks, enabling them to read internal files and exfiltrate sensitive data.

These examples highlight the severity and potential impact of SSRF vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/04-Lab 3 SSRF with blacklist based input filter/02-Lab Setup and Overview|Lab Setup and Overview]]
