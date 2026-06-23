---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding DOM-based XSS

DOM-based XSS vulnerabilities occur when a web application uses untrusted data to update the Document Object Model (DOM) without proper validation or sanitization. The key difference between DOM-based XSS and other forms of XSS is that the injection happens entirely on the client side, making it harder to detect with traditional server-side protections.

### Example Scenario: DOM XSS in jQuery Selector Sink Using Hash Change Event

Let's delve into a specific example of DOM-based XSS involving a jQuery selector sink and a hash change event. We'll explore the mechanics, potential risks, and how to mitigate such vulnerabilities.

#### Background Theory

The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a document as a tree of nodes, allowing scripts to dynamically access and manipulate the content, structure, and style of a document.

In this scenario, the application uses the `hashchange` event to update the DOM based on the URL fragment identifier. The fragment identifier is the part of the URL that comes after the `#` symbol. When the fragment identifier changes, the `hashchange` event is triggered, and the application updates the DOM accordingly.

#### Code Example

Consider the following HTML and JavaScript code:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DOM XSS Example</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        $(window).on('hashchange', function() {
            var fragment = window.location.hash.substring(1);
            $('#content').html(fragment);
        });
    </script>
</body>
</html>
```

In this example, the `hashchange` event listener updates the content of the `#content` div with the value of the URL fragment identifier. If an attacker can control the fragment identifier, they can inject malicious scripts.

#### Potential Attack Vector

An attacker can craft a URL with a malicious script in the fragment identifier, such as:

```
http://example.com/#<script>alert('XSS')</script>
```

When a user clicks on this link, the `hashchange` event is triggered, and the malicious script is injected into the `#content` div and executed by the browser.

### Real-World Examples and Recent Breaches

Recent real-world examples of DOM-based XSS include:

- **CVE-2021-21972**: A DOM-based XSS vulnerability was discovered in the WordPress plugin "WPML Multilingual CMS". The plugin used untrusted data from the URL fragment identifier to update the DOM, leading to potential script injection.
  
- **CVE-2022-22965**: Another DOM-based XSS vulnerability was found in the "Yoast SEO" plugin for WordPress. The plugin used untrusted data from the URL fragment identifier to update the DOM, allowing attackers to inject malicious scripts.

These vulnerabilities highlight the importance of properly validating and sanitizing user inputs, especially when they are used to update the DOM.

### How to Prevent / Defend Against DOM-based XSS

To prevent DOM-based XSS vulnerabilities, follow these best practices:

1. **Input Validation and Sanitization**: Always validate and sanitize user inputs before using them to update the DOM. Use libraries like DOMPurify to sanitize HTML content.

2. **Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) to restrict the sources of executable scripts. This can help mitigate the impact of XSS attacks.

3. **Use Safe Methods**: Instead of using methods like `.html()` or `.innerHTML`, use safer methods like `.text()` or `.textContent` to set the content of elements.

4. **Escape User Inputs**: Escape user inputs to ensure they are treated as plain text rather than executable code.

#### Secure Code Example

Here is a secure version of the previous code example:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Secure DOM XSS Example</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/dompurify@2.3.0/dist/purify.min.js"></script>
</head>
<body>
    <div id="content"></div>
    <script>
        $(window).on('hashchange', function() {
            var fragment = window.location.hash.substring(1);
            var safeFragment = DOMPurify.sanitize(fragment);
            $('#content').text(safeFragment);
        });
    </script>
</body>
</html>
```

In this secure version, the `DOMPurify` library is used to sanitize the fragment identifier before setting it as the content of the `#content` div. Additionally, the `.text()` method is used instead of `.html()` to ensure that the content is treated as plain text.

### Detection and Mitigation Tools

Several tools can help detect and mitigate DOM-based XSS vulnerabilities:

- **Burp Suite**: A comprehensive toolkit for web application security testing that includes features for detecting and exploiting XSS vulnerabilities.
  
- **OWASP ZAP**: An open-source web application security scanner that can detect various types of vulnerabilities, including XSS.

- **DOMPurify**: A library for sanitizing HTML content to prevent XSS attacks.

### Practice Labs

For hands-on practice with DOM-based XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs specifically designed to teach and test web security concepts, including XSS.
  
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including XSS.

- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.

By thoroughly understanding the mechanics of DOM-based XSS and implementing robust security measures, developers can significantly reduce the risk of such vulnerabilities in their web applications.

### Conclusion

DOM-based XSS is a critical security issue that requires careful attention to input validation, sanitization, and the use of safe methods when updating the DOM. By following best practices and using appropriate tools and libraries, developers can effectively prevent and mitigate these vulnerabilities, ensuring the security and integrity of their web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/07-Lab 6 DOM XSS in jQuery selector sink using a hashchange event/02-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/07-Lab 6 DOM XSS in jQuery selector sink using a hashchange event/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/07-Lab 6 DOM XSS in jQuery selector sink using a hashchange event/04-Practice Questions & Answers|Practice Questions & Answers]]
