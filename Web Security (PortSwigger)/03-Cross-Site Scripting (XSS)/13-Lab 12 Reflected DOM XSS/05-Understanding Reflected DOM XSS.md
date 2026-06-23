---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding Reflected DOM XSS

### What is Reflected DOM XSS?

Reflected DOM XSS occurs when a web application reflects user input in the response without proper validation or sanitization. The reflected input is then processed by a script on the page, leading to the execution of arbitrary JavaScript code.

#### Example Scenario

Consider a web application that takes a parameter from the URL and displays it on the page. If the application does not properly sanitize the input, an attacker can inject a script that will be executed when the page is loaded.

### How Does Reflected DOM XSS Work?

Let's break down the steps involved in a Reflected DOM XSS attack:

1. **User Input**: The attacker crafts a URL that includes malicious JavaScript code.
2. **Server Response**: The server reflects the user input in the response.
3. **Client Execution**: The client-side script processes the reflected input and executes the injected JavaScript code.

#### Example Code

Suppose we have a web application with the following HTML structure:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Reflected DOM XSS</title>
</head>
<body>
    <script>
        var param = window.location.search.substring(1);
        document.getElementById("output").innerHTML = param;
    </script>
    <div id="output"></div>
</body>
</html>
```

If an attacker crafts a URL like `http://example.com/?param=<script>alert('XSS')</script>`, the server will reflect this input in the response, and the client-side script will execute the `alert` function.

### Real-World Examples

Recent real-world examples of Reflected DOM XSS include:

- **CVE-2021-21972**: A vulnerability in the WordPress plugin "WPML Multilingual CMS" allowed attackers to inject malicious scripts via the `lang` parameter.
- **CVE-2020-14882**: A vulnerability in the "WordPress Gutenberg" editor allowed attackers to inject malicious scripts via the `post_id` parameter.

These examples highlight the importance of proper input validation and sanitization to prevent XSS attacks.

---
<!-- nav -->
[[04-How to Prevent  Defend Against Reflected DOM XSS|How to Prevent  Defend Against Reflected DOM XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/06-Conclusion|Conclusion]]
