---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a reflected cross-site scripting (XSS) vulnerability is and how it differs from other types of XSS vulnerabilities.**

Reflected XSS occurs when an attacker injects malicious scripts into a web page via user input, such as a search query. The injected script is then reflected back to the user in the response, executed in the user's browser, and can perform actions like stealing cookies or session tokens. It differs from stored XSS, where the malicious script is permanently stored on the server and served to multiple users, and from DOM-based XSS, which relies on client-side code to reflect the script rather than server-side code.

**Q2. How would you exploit a reflected XSS vulnerability in a search functionality where the input is reflected back in the HTML context without encoding? Provide an example payload.**

To exploit a reflected XSS vulnerability in a search functionality, you would craft a payload that includes a script tag with a function call. For example, the payload `"<script>alert('XSS');</script>"` can be inserted into the search field. When the server reflects this input back in the HTML, the script will execute in the user's browser, triggering an alert box with the message 'XSS'. This confirms that the input was interpreted as executable JavaScript.

**Q3. Why is it important to check if characters like `<` and `>` are encoded in the output when testing for XSS vulnerabilities?**

It is crucial to check if characters like `<` and `>` are encoded because these characters are used to define HTML tags. If they are not encoded, an attacker can inject HTML tags and JavaScript code into the page. By testing with these characters, you can determine whether the application properly sanitizes or encodes user inputs, thus preventing potential XSS attacks. If these characters are not encoded, it indicates that the application is vulnerable to XSS.

**Q4. What recent real-world examples or CVEs highlight the importance of protecting against reflected XSS vulnerabilities?**

One notable example is the CVE-2021-21972, which affected several versions of Microsoft Exchange Server. This vulnerability allowed attackers to inject arbitrary JavaScript code through specially crafted HTTP requests, leading to reflected XSS attacks. Attackers could exploit this to steal session cookies or perform actions as the authenticated user. This highlights the critical importance of proper input validation and encoding to prevent such vulnerabilities.

**Q5. How can developers mitigate the risk of reflected XSS vulnerabilities in their applications?**

Developers can mitigate the risk of reflected XSS vulnerabilities by implementing the following practices:
1. **Input Validation**: Ensure that all user inputs are validated and sanitized to remove or encode potentially harmful characters.
2. **Output Encoding**: Encode user inputs before reflecting them back in the HTML context to ensure that they are treated as plain text and not executable code.
3. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded, reducing the impact of XSS attacks.
4. **Use of Libraries and Frameworks**: Utilize security-focused libraries and frameworks that automatically handle input validation and output encoding.

By adhering to these best practices, developers can significantly reduce the likelihood of introducing reflected XSS vulnerabilities into their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/02-Lab 1 Reflected XSS into HTML context with nothing encoded/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/02-Lab 1 Reflected XSS into HTML context with nothing encoded/00-Overview|Overview]]
