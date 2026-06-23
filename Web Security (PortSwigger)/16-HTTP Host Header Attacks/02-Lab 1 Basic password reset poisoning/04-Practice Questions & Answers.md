---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "password reset poisoning" and how it can be exploited.**

Password reset poisoning is a technique where an attacker manipulates a vulnerable website into generating a password reset link that points to a domain controlled by the attacker. This is typically achieved through host header injection, where the attacker modifies the `Host` header in the HTTP request to redirect the password reset link to their own server. When the victim clicks on the poisoned link, the attacker can intercept the temporary password reset token and use it to reset the victim’s password.

**Q2. How can you detect if a web application is vulnerable to host header injection?**

To detect if a web application is vulnerable to host header injection, you can perform the following steps:

1. Identify functionalities that generate URLs, such as password reset links.
2. Send a request to the server with a modified `Host` header pointing to a domain you control.
3. Check if the generated URL contains the domain specified in the `Host` header.

For example, if you send a request to the password reset functionality with a `Host` header set to `attacker.com`, and the generated password reset link includes `attacker.com`, then the application is likely vulnerable to host header injection.

**Q3. Why is it important to validate the `Host` header in web applications?**

Validating the `Host` header is crucial because attackers can manipulate it to perform various types of attacks, including host header injection. By validating the `Host` header against a list of trusted domains, developers can prevent attackers from injecting arbitrary values that could redirect users to malicious sites or intercept sensitive information like password reset tokens.

**Q4. How would you fix a web application that is vulnerable to host header injection?**

To fix a web application vulnerable to host header injection, follow these steps:

1. Ensure that the `Host` header is validated against a whitelist of trusted domains.
2. Use a secure method to generate URLs that do not rely on the `Host` header, such as using a configuration setting or environment variable for the base URL.
3. Implement proper input validation and sanitization for all headers and inputs to prevent injection attacks.

Here is an example of how you might implement this in a Python Flask application:

```python
from flask import Flask, request

app = Flask(__name__)

trusted_domains = ['example.com', 'subdomain.example.com']

@app.before_request
def validate_host_header():
    host = request.headers.get('Host')
    if host not in trusted_domains:
        return "Invalid Host header", 400

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    # Generate password reset link using a trusted domain
    reset_link = f"https://example.com/forgot-password/{generate_token()}"
    return {"reset_link": reset_link}

def generate_token():
    # Function to generate a unique token
    pass

if __name__ == '__main__':
    app.run()
```

**Q5. Describe a recent real-world example where host header injection led to a security breach.**

A notable example of a host header injection leading to a security breach is the case of the popular blogging platform Ghost. In 2019, a vulnerability (CVE-2019-19764) was discovered in Ghost versions prior to 2.33.0. An attacker could exploit this vulnerability by manipulating the `Host` header to inject malicious content into the blog posts, effectively bypassing the content security policies.

In this scenario, the attacker could craft a request with a modified `Host` header to trick the server into serving content from a different domain, leading to Cross-Site Scripting (XSS) attacks. This allowed the attacker to execute arbitrary JavaScript code within the context of the victim's browser, potentially stealing session cookies or other sensitive data.

To mitigate such vulnerabilities, it is essential to validate the `Host` header and ensure that all URLs are generated securely, without relying on untrusted input.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/03-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/00-Overview|Overview]]
