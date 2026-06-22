---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the difference between stored XSS and reflected XSS.**

Stored XSS occurs when an attacker injects malicious scripts into a database or persistent storage that is later served to users. Reflected XSS, on the other hand, involves injecting malicious scripts into a web page that is immediately reflected back to the user, often via a query string or form submission. In stored XSS, the payload is stored and delivered to multiple users, whereas in reflected XSS, the payload is typically targeted at a single user.

**Q2. How would you exploit a stored XSS vulnerability in a comment system?**

To exploit a stored XSS vulnerability in a comment system, an attacker could insert a malicious script into a comment field. For example, the attacker might submit a comment containing a script tag such as `<script>alert('XSS');</script>`. When another user views the comment, the script executes in their browser, potentially allowing the attacker to steal cookies, session tokens, or other sensitive information.

**Q3. How can you mitigate stored XSS vulnerabilities in a web application?**

Mitigating stored XSS vulnerabilities involves several steps:

1. **Input Validation:** Ensure that all user inputs are validated against a strict set of rules before being stored or displayed.
2. **Output Encoding:** Encode user inputs appropriately when displaying them in different contexts (HTML, JavaScript, CSS, etc.). Use libraries like OWASP Java Encoder or Microsoft Anti-XSS library.
3. **Content Security Policy (CSP):** Implement CSP to restrict the sources from which scripts can be loaded, thereby reducing the risk of XSS attacks.
4. **Sanitization:** Use sanitization techniques to remove or escape potentially dangerous characters from user inputs.

**Q4. Describe a recent real-world example of a stored XSS vulnerability and explain how it was exploited.**

A notable example is the stored XSS vulnerability found in the popular social media platform Twitter in 2021 (CVE-2021-29467). Attackers were able to inject malicious scripts into tweets, which were then stored in the database and served to other users. This allowed the attackers to execute arbitrary JavaScript code in the context of the victim's browser, potentially stealing sensitive data or performing actions on behalf of the user.

**Q5. How would you configure a web server to prevent stored XSS attacks?**

To configure a web server to prevent stored XSS attacks, consider the following steps:

1. **Enable Content Security Policy (CSP):** Set up CSP headers to restrict the sources from which scripts can be loaded. For example:
   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
   ```

2. **Set HTTP Headers:** Use headers like `X-XSS-Protection` to enable browser-based XSS filters:
   ```http
   X-XSS-Protection: 1; mode=block
   ```

3. **Use Strict Transport Security (HSTS):** Force the use of HTTPS to prevent man-in-the-middle attacks:
   ```http
   Strict-Transport-Security: max-age=31536000; includeSubDomains
   ```

4. **Implement Input Validation and Sanitization:** Ensure that all user inputs are properly validated and sanitized before being stored or displayed.

**Q6. What is the role of JSON and XML in the context of stored XSS vulnerabilities?**

JSON and XML are data formats used for storing and transmitting data. In the context of stored XSS vulnerabilities, if these formats are not properly encoded or sanitized before being rendered in a browser, they can be used to inject malicious scripts. For instance, if a JSON object contains a user-submitted comment with a script tag, and this JSON is rendered as HTML, the script can execute in the browser. Similarly, XML can be used to inject scripts if it is improperly handled.

**Q7. How does HTML encoding help prevent stored XSS attacks?**

HTML encoding converts special characters into their corresponding HTML entities, preventing them from being interpreted as part of the HTML document. For example, the less-than sign (`<`) is converted to `&lt;`, and the greater-than sign (`>`) is converted to `&gt;`. By encoding user inputs before rendering them in a browser, the risk of executing malicious scripts is significantly reduced. This ensures that even if an attacker attempts to inject a script, it will be rendered as plain text rather than executable code.

---
<!-- nav -->
[[02-Introduction to Stored Cross-Site Scripting (XSS)|Introduction to Stored Cross-Site Scripting (XSS)]] | [[API Security/12-Cross Site Scripting/05-Stored Cross Site Scripting hide01ir/00-Overview|Overview]]
