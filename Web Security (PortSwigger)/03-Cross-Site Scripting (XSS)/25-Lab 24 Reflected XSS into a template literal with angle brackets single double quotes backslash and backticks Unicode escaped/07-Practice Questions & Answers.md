---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how the reflected XSS vulnerability works in the context of this lab.**

The reflected XSS vulnerability in this lab occurs when user input is directly included in a JavaScript template literal without proper sanitization or encoding. When a user inputs a string into the search field, the server reflects this input back to the client within a template literal. If the input contains malicious JavaScript code, such as an `alert` function, it will execute in the context of the victim's browser, leading to a successful XSS attack.

**Q2. How would you exploit the reflected XSS vulnerability described in the lab? Provide an example payload.**

To exploit the reflected XSS vulnerability, you need to inject a payload that executes JavaScript code within the template literal. An example payload could be:

```javascript
${alert(1)}
```

This payload uses the `${}` syntax to execute the `alert(1)` function within the template literal. When the server reflects this input back to the client, the injected JavaScript code will run, triggering an alert box.

**Q3. Why is the use of backticks significant in this lab's XSS vulnerability?**

Backticks (`) are used in JavaScript to denote template literals. Template literals allow for embedded expressions using the `${expression}` syntax, which can evaluate and insert the result of the expression into the string. In the context of this lab, the use of backticks indicates that the input is being processed as part of a template literal, making it possible to execute arbitrary JavaScript code if the input is not properly sanitized.

**Q4. What recent real-world examples or CVEs demonstrate the risk of reflected XSS vulnerabilities similar to those in this lab?**

One notable example is the CVE-2021-21972, which affected the popular web analytics tool Matomo (formerly Piwik). This vulnerability allowed attackers to inject arbitrary JavaScript code via a reflected XSS vector. By manipulating certain parameters in the URL, an attacker could execute JavaScript in the context of the victim's browser, potentially stealing sensitive data or performing actions on behalf of the user.

**Q5. How can developers prevent reflected XSS vulnerabilities like the one in this lab?**

Developers can prevent reflected XSS vulnerabilities by ensuring that all user input is properly sanitized and encoded before being included in the response. Specifically, for JavaScript contexts, developers should:

1. Use content security policies (CSP) to restrict the sources from which scripts can be loaded.
2. Sanitize and encode user input to ensure that it does not contain executable script code.
3. Avoid using template literals or other dynamic evaluation mechanisms unless absolutely necessary, and ensure that any such usage is properly secured.
4. Employ a framework or library that provides automatic escaping for user inputs in templates.

By following these best practices, developers can significantly reduce the risk of reflected XSS vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/06-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/00-Overview|Overview]]
