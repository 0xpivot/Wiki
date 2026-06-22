---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a Stored DOM-based XSS vulnerability is and how it differs from a Reflected XSS.**

A Stored DOM-based XSS vulnerability occurs when an attacker can inject malicious scripts into a persistent storage mechanism (like a database) that is later retrieved and executed by other users' browsers. The key difference from a Reflected XSS is that in a Reflected XSS, the payload is immediately reflected back to the user who submitted it, whereas in a Stored XSS, the payload is stored and then served to multiple users over time.

**Q2. How would you identify potential points of injection for a Stored DOM-based XSS vulnerability?**

To identify potential points of injection for a Stored DOM-based XSS vulnerability, you should:

1. Map the application to understand where user inputs are stored and later rendered.
2. Look for areas where user-supplied data is displayed back to the user, such as comments, usernames, or posts.
3. Check if the application properly sanitizes or escapes user input before rendering it in the DOM.

For example, in the lab described, the comment and name fields were identified as potential points of injection since they were displayed back to the user without proper escaping.

**Q3. What is the role of the `escapeHtml` function in the context of preventing XSS attacks, and why was it ineffective in this lab?**

The `escapeHtml` function is intended to prevent XSS attacks by replacing potentially harmful characters (such as `<` and `>`), which could be used to inject scripts, with their URL-encoded equivalents. However, in this lab, the `escapeHtml` function was ineffective because it only replaced the first instance of the angle brackets in the input string. This allowed subsequent angle brackets to remain unescaped, enabling an attacker to inject a script tag.

**Q4. How would you exploit the Stored DOM-based XSS vulnerability demonstrated in the lab to execute a simple alert box?**

To exploit the Stored DOM-based XSS vulnerability demonstrated in the lab, you would inject a payload that includes a script tag. Since the `escapeHtml` function only escapes the first instance of angle brackets, you can bypass this by including multiple angle brackets. Here’s an example payload:

```
<<img src="x" onerror="alert('1')">
```

When this payload is injected and later rendered in the DOM, the first set of angle brackets will be escaped, but the second set will remain intact, allowing the `onerror` event handler to execute the `alert` function.

**Q5. Referencing recent real-world examples, explain how a Stored DOM-based XSS vulnerability can be exploited in a real-world scenario.**

One recent example of a Stored DOM-based XSS vulnerability is the CVE-2021-21972, which affected several popular WordPress plugins. Attackers could inject malicious scripts into comments or other user-submitted content, which would then be stored and executed by other users' browsers when they visited the affected pages.

In such scenarios, attackers might use the vulnerability to steal cookies, session tokens, or other sensitive information, leading to unauthorized access to user accounts. They could also redirect users to malicious sites or display misleading content, causing reputational damage to the affected organization.

**Q6. How would you fix the vulnerability in the `escapeHtml` function to prevent Stored DOM-based XSS attacks?**

To fix the vulnerability in the `escapeHtml` function, you should ensure that all instances of potentially harmful characters are properly escaped. This can be achieved by using a regular expression to replace all occurrences of the characters, rather than just the first one. Here’s an improved version of the `escapeHtml` function:

```javascript
function escapeHtml(str) {
    return str.replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');
}
```

This function uses the global flag (`/g`) in the regular expressions to replace all occurrences of `<` and `>` with their respective HTML entities, ensuring that no script tags can be injected.

**Q7. What are some best practices to prevent Stored DOM-based XSS vulnerabilities in web applications?**

Some best practices to prevent Stored DOM-based XSS vulnerabilities include:

1. **Input Validation**: Validate all user inputs to ensure they conform to expected formats.
2. **Output Encoding**: Always encode user inputs before inserting them into the DOM. Use context-sensitive encoding (e.g., HTML entity encoding for HTML contexts).
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded.
4. **Sanitization Libraries**: Use well-tested libraries for sanitizing user inputs, such as DOMPurify for JavaScript.
5. **Security Testing**: Regularly perform security testing, including automated scans and manual penetration testing, to identify and mitigate vulnerabilities.

By following these practices, developers can significantly reduce the risk of Stored DOM-based XSS vulnerabilities in their web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/14-Lab 13 Stored DOM XSS/04-Understanding the Vulnerability|Understanding the Vulnerability]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/14-Lab 13 Stored DOM XSS/00-Overview|Overview]]
