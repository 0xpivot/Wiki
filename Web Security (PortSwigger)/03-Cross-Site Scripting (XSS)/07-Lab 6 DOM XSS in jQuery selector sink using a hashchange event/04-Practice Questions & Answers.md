---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a DOM-based XSS vulnerability is and how it differs from traditional XSS vulnerabilities.**

DOM-based XSS occurs when a web application uses untrusted data within the JavaScript code without proper validation or sanitization. Unlike traditional XSS where the payload is stored on the server or reflected from the server, DOM-based XSS relies on the client-side JavaScript to execute the payload. This makes it harder to detect and mitigate as it operates entirely on the client side.

**Q2. How does the `hashchange` event contribute to the DOM-based XSS vulnerability in this lab?**

The `hashchange` event is triggered whenever the fragment identifier (the part of the URL after the `#`) changes. In this lab, the JavaScript code listens for changes to the `location.hash` and uses its content to scroll to a specific section on the page. If the content of `location.hash` is not properly sanitized, it can lead to a DOM-based XSS vulnerability. An attacker can inject malicious JavaScript into the `location.hash`, which gets executed when the `hashchange` event fires.

**Q3. Describe how you would exploit the DOM-based XSS vulnerability in this lab to call the `print()` function.**

To exploit the DOM-based XSS vulnerability in this lab, you need to inject a payload into the `location.hash`. The payload should be crafted to execute the `print()` function when the `hashchange` event is triggered. For example, you can use the following payload:

```
http://example.com/#<img src=1 onerror=print()>
```

When the user navigates to this URL, the `hashchange` event will fire, and the JavaScript inside the `onerror` attribute of the `<img>` tag will be executed, calling the `print()` function.

**Q4. Why is framing the application necessary to exploit the DOM-based XSS vulnerability in this lab?**

Framing the application is necessary because the `hashchange` event only triggers when the URL fragment changes. Simply sending a URL with the payload in the `location.hash` would not work if the user directly navigates to that URL, as the `hashchange` event would not be triggered. By framing the application and dynamically changing the `src` attribute of the iframe, you can ensure that the `hashchange` event is triggered, thereby executing the malicious payload.

**Q5. Provide a recent real-world example of a DOM-based XSS vulnerability and explain how it was exploited.**

One recent example of a DOM-based XSS vulnerability is CVE-2021-21972, which affected the popular web conferencing platform Zoom. The vulnerability allowed attackers to inject arbitrary JavaScript into the URL fragment, which would then be executed by the client-side JavaScript when the `hashchange` event was triggered. Attackers could craft URLs that, when clicked by users, would execute malicious scripts, potentially leading to session hijacking or other attacks. To exploit this vulnerability, attackers would send a specially crafted URL to victims, who upon clicking it, would unknowingly execute the injected JavaScript.

**Q6. How can developers prevent DOM-based XSS vulnerabilities in their applications?**

Developers can prevent DOM-based XSS vulnerabilities by ensuring that all untrusted data is properly validated and sanitized before being used in JavaScript code. Key practices include:

1. **Input Validation**: Validate all inputs to ensure they meet expected formats and constraints.
2. **Output Encoding**: Encode data appropriately depending on the context in which it is used (e.g., HTML, JavaScript, CSS).
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded, reducing the risk of XSS attacks.
4. **Use Libraries and Frameworks**: Utilize libraries and frameworks that provide built-in protections against XSS, such as AngularJS or React, which automatically escape user inputs.

By following these best practices, developers can significantly reduce the risk of introducing DOM-based XSS vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/07-Lab 6 DOM XSS in jQuery selector sink using a hashchange event/03-Understanding DOM-based XSS|Understanding DOM-based XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/07-Lab 6 DOM XSS in jQuery selector sink using a hashchange event/00-Overview|Overview]]
