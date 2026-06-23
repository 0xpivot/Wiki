---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the difference between a stored XSS vulnerability and a reflected XSS vulnerability?**

Stored XSS occurs when the attacker's input is permanently stored in the server, such as in a database, and is later served to other users. Reflected XSS, on the other hand, involves the attacker's input being immediately reflected back to the user, typically via a URL or form submission. In the stored XSS scenario, any user who views the page with the injected script will execute the script, whereas in reflected XSS, the script executes only for the user who initially triggered it.

**Q2. How would you exploit a stored XSS vulnerability in the comment functionality of a blog post?**

To exploit a stored XSS vulnerability in the comment functionality of a blog post, you would need to inject a script into the comment field that gets stored on the server and is later rendered in the HTML context. For example, you could use a payload like `<script>alert('XSS');</script>` in the comment field. When another user views the blog post, the script will execute in their browser, triggering the alert box.

**Q3. Explain why encoding input data is crucial in preventing XSS attacks.**

Encoding input data is crucial because it ensures that any special characters used in an attack, such as `<`, `>`, and `/`, are treated as literal characters rather than as part of the HTML or JavaScript code. This prevents the browser from interpreting the input as executable code. For instance, if the input `<script>alert('XSS');</script>` is properly encoded, it might be transformed into `&lt;script&gt;alert('XSS');&lt;/script&gt;`, which the browser will display as plain text rather than executing it as a script.

**Q4. How can you verify if a web application is vulnerable to stored XSS through its comment functionality?**

To verify if a web application is vulnerable to stored XSS through its comment functionality, you can inject a simple payload like `<script>alert('XSS');</script>` into the comment field and submit it. Then, check if the payload is rendered as executable JavaScript when viewing the comment. If an alert box appears when viewing the comment, the application is likely vulnerable to stored XSS.

**Q5. Describe a recent real-world example of a stored XSS vulnerability and explain how it was exploited.**

A notable example is the stored XSS vulnerability found in the popular blogging platform WordPress. In 2019, a vulnerability was discovered in the WordPress REST API that allowed attackers to inject malicious scripts into comments. The vulnerability was exploited by injecting a script into the comment field, which was then stored and rendered on the blog posts. When other users viewed the blog, the script executed, potentially stealing cookies or redirecting users to malicious sites. This type of attack highlights the importance of proper input validation and encoding in web applications.

**Q6. What steps can developers take to prevent stored XSS vulnerabilities in web applications?**

Developers can take several steps to prevent stored XSS vulnerabilities:

1. **Input Validation:** Ensure that all user inputs are validated against expected formats and patterns.
2. **Output Encoding:** Encode all user inputs before rendering them in the HTML context. Use libraries like OWASP Java Encoder or ESAPI for encoding.
3. **Content Security Policy (CSP):** Implement CSP to restrict the sources from which scripts can be loaded, reducing the risk of XSS.
4. **Sanitization:** Use sanitization libraries to clean user inputs, especially for HTML content.
5. **Security Testing:** Regularly perform security testing, including automated scanning and manual penetration testing, to identify and fix XSS vulnerabilities.

By following these practices, developers can significantly reduce the risk of stored XSS vulnerabilities in their web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/02-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/00-Overview|Overview]]
