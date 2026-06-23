---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of DOM-based XSS and how it differs from traditional XSS.**

DOM-based Cross-Site Scripting (XSS) occurs when a web application reflects user-supplied data into the DOM without proper sanitization. Unlike traditional XSS, where the server directly injects user input into the response, DOM-based XSS involves client-side scripts that manipulate the DOM based on user input. This means the vulnerability lies within the client-side JavaScript rather than the server-side code.

**Q2. How would you exploit a DOM-based XSS vulnerability using the `document.write` method? Provide an example payload.**

To exploit a DOM-based XSS vulnerability using the `document.write` method, you need to inject a payload that will execute JavaScript code within the context of the page. For example, if the application uses `document.write` to write user input into the page, you can inject a script tag to execute arbitrary JavaScript. Here’s an example payload:

```
<script>alert('XSS');</script>
```

If the application writes this payload into the page using `document.write`, the script will execute, triggering an alert box.

**Q3. Why is the `location.search` property often used as a source for DOM-based XSS attacks?**

The `location.search` property represents the part of the URL that follows the question mark (`?`). This property is often used to pass parameters to the page via the URL. Since this data can be controlled by the user, it is a common source for DOM-based XSS attacks. Attackers can manipulate the URL to inject malicious content that gets processed by the client-side script.

**Q4. How would you mitigate a DOM-based XSS vulnerability in a web application that uses `document.write` and `location.search`?**

To mitigate a DOM-based XSS vulnerability in a web application that uses `document.write` and `location.search`, you should ensure that user input is properly sanitized before being written to the DOM. This can be achieved by:

1. **Sanitizing Input:** Use a library or framework that provides input sanitization functions to escape special characters in user input.
2. **Content Security Policy (CSP):** Implement a Content Security Policy to restrict the sources from which scripts can be loaded, reducing the risk of XSS.
3. **Avoid Using `document.write`:** Refrain from using `document.write` as it can overwrite the entire document and is generally considered a bad practice. Instead, use DOM manipulation methods such as `innerHTML`, `textContent`, or `createElement`.

Example of sanitizing input using a library like DOMPurify:

```javascript
const userInput = decodeURIComponent(location.search.substring(1));
const safeInput = DOMPurify.sanitize(userInput);
document.write(safeInput);
```

**Q5. Reference a recent real-world example of a DOM-based XSS vulnerability and explain how it was exploited.**

One notable example is the DOM-based XSS vulnerability found in the popular web analytics tool Google Tag Manager (GTM). In 2021, researchers discovered that GTM could be exploited to execute arbitrary JavaScript if an attacker could control the `dataLayer` variable.

Attackers could inject malicious code into the `dataLayer` variable, which GTM processes and writes to the DOM. This allowed the execution of arbitrary JavaScript, leading to potential data exfiltration or other malicious activities.

To exploit this vulnerability, attackers would craft a URL or use other methods to inject malicious code into the `dataLayer` variable. Once the code was executed, it could perform actions such as stealing cookies or redirecting users to malicious sites.

This example highlights the importance of proper input validation and sanitization in client-side scripts to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/06-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/00-Overview|Overview]]
