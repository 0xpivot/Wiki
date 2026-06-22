---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary purpose of the `postMessage` function in the context of this lab?**

The `postMessage` function is used to send messages between different windows or iframes. In this lab, it is used to exploit a DOM-based XSS vulnerability by sending a crafted message that triggers the execution of malicious JavaScript code within the target application. Specifically, the payload is designed to call the `print` function when the message is received and processed by the target application.

**Q2. Explain why the use of `innerHTML` in the given JavaScript snippet makes the application vulnerable to DOM-based XSS.**

The use of `innerHTML` in the JavaScript snippet makes the application vulnerable to DOM-based XSS because it allows unfiltered client-supplied input to be directly injected into the DOM. When the `innerHTML` property is set with user-provided data, any embedded scripts within that data will be executed by the browser. This can lead to arbitrary code execution if an attacker can control the input, as demonstrated in this lab where the `innerHTML` property is used to insert a crafted message into the DOM.

**Q3. How would you modify the payload to include a more complex XSS attack, such as redirecting the user to a phishing site?**

To modify the payload for a more complex XSS attack, such as redirecting the user to a phishing site, you can change the payload to include a script that redirects the user. For example:

```html
<img src="nonexistent" onerror="location.href='http://phishing-site.com';">
```

This payload will attempt to load an image from a non-existent source. When the image fails to load, the `onerror` attribute will execute the JavaScript code, which redirects the user to a phishing site.

**Q4. Why is the `targetOrigin` parameter set to `"*"` in the `postMessage` function call?**

The `targetOrigin` parameter in the `postMessage` function call is set to `"*"` to allow the message to be sent to any domain. This is a wildcard value that indicates that the message can be sent to any origin, including the origin of the target application. Setting `targetOrigin` to `"*"` is often used in labs and testing environments but should be avoided in production code due to security risks. In a real-world scenario, `targetOrigin` should be set to the specific domain of the intended recipient to prevent unauthorized domains from receiving the message.

**Q5. How does the lack of input validation or sanitization contribute to the vulnerability exploited in this lab?**

The lack of input validation or sanitization contributes significantly to the vulnerability exploited in this lab. Without proper validation or sanitization, the application blindly accepts and processes any input provided by the user. This allows an attacker to inject malicious content, such as JavaScript code, directly into the DOM. In this lab, the application uses `innerHTML` to insert user-provided data into the DOM without any checks or sanitization, making it susceptible to DOM-based XSS attacks. Proper input validation and sanitization would help mitigate such vulnerabilities by ensuring that only safe and expected inputs are processed.

---
<!-- nav -->
[[02-DOM-Based Vulnerabilities and DOM-XSS Using Web Messages|DOM-Based Vulnerabilities and DOM-XSS Using Web Messages]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/01-Lab 1 DOM XSS using web messages/00-Overview|Overview]]
