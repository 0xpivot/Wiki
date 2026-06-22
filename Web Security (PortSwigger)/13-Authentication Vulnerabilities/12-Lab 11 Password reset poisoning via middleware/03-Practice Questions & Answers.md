---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the password reset poisoning attack works in the context of the lab.**

The password reset poisoning attack exploits a vulnerability in the password reset functionality of a web application. In this lab, the application accepts an `X-Forwarded-Host` header, which allows an attacker to manipulate the host part of the URL in the password reset link. By setting the `X-Forwarded-Host` header to point to an exploit server, the attacker can generate a password reset link that redirects to the exploit server instead of the legitimate application domain. When the victim (Carlos) clicks on this poisoned link, the request is made to the exploit server, allowing the attacker to intercept the temporary password reset token and reset the victim's password.

**Q2. How would you exploit the password reset poisoning vulnerability in this lab?**

To exploit the password reset poisoning vulnerability in this lab, follow these steps:

1. **Identify the Vulnerability**: Use Burp Suite to intercept the HTTP requests related to the password reset functionality.
2. **Inject Headers**: Modify the intercepted request to include an `X-Forwarded-Host` header pointing to the exploit server.
3. **Generate Poisoned Link**: Send the modified request to trigger the generation of a password reset link that points to the exploit server.
4. **Intercept Token**: When the victim (Carlos) clicks on the poisoned link, the request will be made to the exploit server, and the temporary password reset token will be captured.
5. **Reset Password**: Use the captured token to reset the victim's password by sending a request to the application with the new password.

Here is an example payload for injecting the `X-Forwarded-Host` header:

```http
POST /forgot-password HTTP/1.1
Host: vulnerable-app.com
X-Forwarded-Host: exploit-server.com
Content-Type: application/x-www-form-urlencoded

username=carlos
```

**Q3. Why is the `X-Forwarded-Host` header vulnerable to manipulation in this scenario?**

The `X-Forwarded-Host` header is vulnerable to manipulation because the web application trusts the value of this header without proper validation. In a typical setup, this header is used by reverse proxies to pass along the original host header from the client request. However, if the application directly uses this header to construct URLs without verifying its authenticity, an attacker can manipulate it to redirect requests to a different domain, such as an exploit server.

**Q4. What recent real-world examples demonstrate the exploitation of similar vulnerabilities?**

One notable example is the exploitation of the `X-Forwarded-Host` header in the Equifax data breach in 2017. Hackers exploited a vulnerability in Apache Struts, which allowed them to inject malicious content into the `X-Forwarded-Host` header. This led to unauthorized access to sensitive data. Another example is CVE-2020-5902, where an attacker could manipulate the `X-Forwarded-Host` header to bypass security controls in certain applications, leading to unauthorized access.

In both cases, the lack of proper validation and sanitization of headers like `X-Forwarded-Host` allowed attackers to manipulate the application's behavior and gain unauthorized access to sensitive information.

**Q5. How can you prevent password reset poisoning attacks in web applications?**

To prevent password reset poisoning attacks, implement the following best practices:

1. **Validate Host Headers**: Ensure that the application validates the `X-Forwarded-Host` header against a list of trusted domains before using it to construct URLs.
2. **Use Secure Tokens**: Generate secure, unique tokens for password reset links and validate them on the server side.
3. **Limit Token Lifetime**: Set a short expiration time for password reset tokens to minimize the window of opportunity for attackers.
4. **Monitor and Log Requests**: Implement logging and monitoring to detect unusual patterns or suspicious activities related to password reset requests.
5. **Educate Users**: Inform users about the risks of clicking on unsolicited links and encourage them to verify the legitimacy of any password reset requests.

By implementing these measures, you can significantly reduce the risk of password reset poisoning attacks in web applications.

---
<!-- nav -->
[[02-Authentication Vulnerabilities Password Reset Poisoning via Middleware|Authentication Vulnerabilities Password Reset Poisoning via Middleware]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/12-Lab 11 Password reset poisoning via middleware/00-Overview|Overview]]
