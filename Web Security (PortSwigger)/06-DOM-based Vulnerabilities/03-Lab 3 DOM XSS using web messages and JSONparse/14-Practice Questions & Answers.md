---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how DOM-based XSS vulnerabilities arise in web applications.**

DOM-based XSS occurs when a web application reflects user-supplied data into the document object model (DOM) without proper validation or sanitization. This can happen when JavaScript code reads data from sources such as URL fragments, cookies, or web storage, and then writes that data to the DOM. If an attacker can control the input, they can inject malicious scripts that will execute in the context of the victim’s browser.

**Q2. How can you exploit a DOM-based XSS vulnerability using web messages and JSON.parse?**

To exploit a DOM-based XSS vulnerability using web messages and JSON.parse, you can craft a payload that is sent via `window.postMessage` to the target application. The payload should be structured as valid JSON and designed to trigger a specific condition within the application's JavaScript logic. For example, if the application expects a message with a certain type (e.g., "load channel") and uses the message content to set a URL or other DOM elements, you can create a JSON payload that includes a script tag or other executable content. Here's an example payload:

```javascript
var payload = {
    "type": "load channel",
    "url": "<script>alert('XSS');</script>"
};
window.postMessage(JSON.stringify(payload), "*");
```

This payload would cause the application to insert the script into the DOM, leading to the execution of the injected script.

**Q3. What steps should be taken to prevent DOM-based XSS vulnerabilities in web applications?**

To prevent DOM-based XSS vulnerabilities, developers should follow these best practices:

1. **Input Validation**: Ensure that all user-supplied data is validated against a strict set of rules before being used in the application.
2. **Output Encoding**: Use appropriate encoding techniques to ensure that user-supplied data is safely rendered in the DOM. For example, use HTML entity encoding for text content, and URL encoding for URLs.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded, thereby mitigating the risk of XSS attacks.
4. **Sanitize Inputs**: Use libraries or functions that sanitize user inputs to remove potentially dangerous characters or patterns.
5. **Avoid Untrusted Data in DOM**: Avoid directly inserting untrusted data into the DOM. Instead, use safe methods like setting attributes or properties through JavaScript APIs.

**Q4. How can you detect DOM-based XSS vulnerabilities during a security assessment?**

To detect DOM-based XSS vulnerabilities during a security assessment, you can perform the following steps:

1. **Review Source Code**: Examine the JavaScript code for any instances where user-supplied data is read and written to the DOM without proper validation or encoding.
2. **Test with Fuzzing Tools**: Use automated tools to fuzz the application with various payloads to see if any of them result in the execution of arbitrary scripts.
3. **Manual Testing**: Manually test the application by injecting different types of payloads into various input fields and observing the behavior of the application.
4. **Use Developer Tools**: Utilize browser developer tools to inspect the DOM and network traffic to identify potential vulnerabilities.
5. **Check for Web Messaging Vulnerabilities**: Specifically test for vulnerabilities related to `window.postMessage` by sending crafted messages and observing the application's response.

**Q5. Provide a recent real-world example of a DOM-based XSS vulnerability and explain how it was exploited.**

One recent example of a DOM-based XSS vulnerability is the case of a vulnerability found in the popular web analytics tool, Matomo (formerly Piwik). In 2021, a researcher discovered a DOM-based XSS vulnerability in Matomo's dashboard. The vulnerability arose due to improper handling of user-supplied data in the URL fragment, which was reflected in the DOM without proper sanitization.

The researcher exploited this vulnerability by crafting a URL that included a script tag in the URL fragment. When a user clicked on this URL, the script tag was inserted into the DOM, leading to the execution of arbitrary JavaScript code in the context of the user's browser. This allowed the attacker to steal sensitive information such as session tokens or perform other malicious actions.

To exploit this vulnerability, the researcher might have used a payload similar to the following:

```
https://example.com/matomo/#<script>alert(document.cookie)</script>
```

When a user navigated to this URL, the script tag was executed, revealing the user's cookies. This demonstrates the importance of proper input validation and output encoding to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/13-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]]
