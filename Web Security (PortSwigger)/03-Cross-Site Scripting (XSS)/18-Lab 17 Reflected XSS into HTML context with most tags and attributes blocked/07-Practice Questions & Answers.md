---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the Web Application Firewall (WAF) in the context of the lab?**

The Web Application Firewall (WAF) in the lab is designed to protect against common XSS vectors by filtering out certain HTML tags and attributes. Its purpose is to prevent attackers from injecting malicious scripts into the application. In this specific lab, the WAF blocks the `<script>` tag, among others, to mitigate XSS attacks.

**Q2. How can you determine which HTML tags are allowed by the WAF?**

To determine which HTML tags are allowed by the WAF, you can use Burp Suite's Intruder feature. By sending a large set of payloads containing various HTML tags through Intruder, you can observe which tags result in a successful response (HTTP 200) and which result in errors (e.g., HTTP 400). Tags that return a 200 status indicate they are allowed by the WAF.

**Q3. Explain how you can exploit the allowed `<body>` tag to perform an XSS attack.**

Once you identify that the `<body>` tag is allowed by the WAF, you can exploit it by attaching event handlers to it. For example, the `onresize` event can be used to execute JavaScript when the browser window is resized. By embedding this event handler within the `<body>` tag, you can inject a script that triggers the desired action, such as calling the `print()` function.

```html
<body onresize="print()">
```

This script will automatically execute when the browser window is resized, thus triggering the print functionality without requiring any user interaction beyond visiting the link.

**Q4. Why is the iframe technique necessary in this lab?**

The iframe technique is necessary because the initial XSS payload requires the user to resize the browser window to trigger the print functionality. Since the lab specifies that the user will not perform any actions, the iframe technique automates this process. By embedding the vulnerable page within an iframe on an attacker-controlled server, the attacker can programmatically resize the iframe, thereby triggering the print functionality without any user interaction.

**Q5. How would you configure the iframe to automatically resize and trigger the XSS payload?**

To configure the iframe to automatically resize and trigger the XSS payload, you can create an HTML page on the attacker-controlled server that includes the iframe and a script to resize it. Here’s an example:

```html
<!DOCTYPE html>
<html>
<head>
    <title>XSS Exploit</title>
</head>
<body>
    <iframe src="http://vulnerable-app.com/search?q=<body%20onresize='print()'>"></iframe>
    <script>
        var iframe = document.querySelector('iframe');
        iframe.style.width = '100px';
        setTimeout(function() {
            iframe.style.width = '900px';
        }, 1000);
    </script>
</body>
</html>
```

In this example, the iframe loads the vulnerable page with the XSS payload embedded. The script then resizes the iframe, which triggers the `onresize` event and executes the `print()` function.

**Q6. How does this lab relate to recent real-world examples of XSS vulnerabilities?**

Recent real-world examples of XSS vulnerabilities include cases where attackers exploited flaws in web applications to inject malicious scripts. For instance, in 2021, several popular websites were affected by XSS vulnerabilities that allowed attackers to steal session cookies or redirect users to phishing sites. These incidents highlight the importance of properly sanitizing user inputs and using security measures like WAFs to filter out potentially harmful content. The techniques learned in this lab, such as identifying allowed tags and exploiting them, are directly applicable to understanding and mitigating such vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/06-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/00-Overview|Overview]]
