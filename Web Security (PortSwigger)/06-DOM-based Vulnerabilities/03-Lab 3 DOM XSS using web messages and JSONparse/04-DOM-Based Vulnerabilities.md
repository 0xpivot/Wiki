---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## DOM-Based Vulnerabilities

### Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when a web application uses untrusted input to dynamically modify the Document Object Model (DOM) in a way that can execute arbitrary JavaScript code. This type of vulnerability is particularly dangerous because it can bypass many traditional security mechanisms, such as Content Security Policy (CSP) and Same-Origin Policy (SOP).

#### What is the Document Object Model (DOM)?

The Document Object Model (DOM) is an API for HTML and XML documents. It represents the document as a tree structure, where each node is an object representing parts of the document, such as elements, attributes, and text content. The DOM allows scripts to dynamically access and manipulate these nodes, enabling interactive web applications.

#### Why Are DOM-Based Vulnerabilities Dangerous?

DOM-based vulnerabilities are dangerous because they can lead to Cross-Site Scripting (XSS) attacks. Unlike traditional XSS attacks, which inject malicious scripts into the server-side response, DOM-based XSS attacks inject scripts directly into the client-side DOM. This makes them harder to detect and mitigate using standard server-side security measures.

### Understanding the Lab Exercise

In the given lab exercise, we are dealing with a DOM-based XSS vulnerability that involves the use of web messages and `JSON.parse`. Let's break down the steps involved in this exercise:

1. **Setting Up the Exploit**:
    - We create a JavaScript snippet that calls a `print` function.
    - This snippet is then copied and pasted into the exploit server.
    - We verify that the script loads correctly in our browser.

2. **Delivering the Exploit**:
    - The exploit is delivered to the victim user.
    - Upon successful exploitation, we receive a confirmation message.

### Detailed Explanation of the Exploit

Let's dive deeper into the specifics of the exploit and how it works.

#### Step 1: Setting Up the Exploit

First, we need to create a JavaScript snippet that will be used to exploit the DOM-based vulnerability. Here’s an example of what the JavaScript might look like:

```javascript
// JavaScript snippet to call the print function
(function() {
    var source = "javascript:print();";
    // Additional logic to inject the script into the DOM
})();
```

This snippet creates a string `source` that contains the JavaScript code to call the `print` function. The `print` function is typically used to open the print dialog in the browser.

#### Step 2: Copying and Verifying the Snippet

Next, we copy this JavaScript snippet and paste it into the exploit server. We then verify that the script loads correctly in our browser. This ensures that the script is functioning as intended before we proceed with the actual exploitation.

```html
<!-- Example of the exploit server page -->
<!DOCTYPE html>
<html>
<head>
    <title>Exploit Server</title>
</head>
<body>
    <script>
        // Paste the JavaScript snippet here
        (function() {
            var source = "javascript:print();";
            // Additional logic to inject the script into the DOM
        })();
    </script>
</body>
</html>
```

#### Step 3: Delivering the Exploit

Once the script is verified, we deliver the exploit to the victim user. This can be done through various methods, such as embedding the script in a link or injecting it into a web page that the victim visits.

```html
<!-- Example of delivering the exploit via a link -->
<a href="javascript:(function(){var source='javascript:print();';})();">Click here</a>
```

Upon clicking the link, the victim's browser will execute the JavaScript code, leading to the successful exploitation of the DOM-based vulnerability.

### Real-World Examples of DOM-Based XSS

DOM-based XSS vulnerabilities have been exploited in numerous real-world scenarios. Here are some recent examples:

1. **CVE-2021-3197**: A DOM-based XSS vulnerability was found in the WordPress plugin "WP GDPR Compliance". The vulnerability allowed attackers to inject malicious scripts into the DOM, leading to potential data theft and other malicious activities.

2. **CVE-2022-22965**: Another DOM-based XSS vulnerability was discovered in the popular web framework Angular. The vulnerability allowed attackers to inject malicious scripts into the DOM, bypassing the framework's built-in security mechanisms.

### How to Prevent / Defend Against DOM-Based XSS

Preventing DOM-based XSS requires a combination of secure coding practices, proper validation and sanitization of user inputs, and the use of security mechanisms like Content Security Policy (CSP).

#### Secure Coding Practices

1. **Avoid Directly Using Untrusted Input**: Ensure that any user-provided input is not directly used to modify the DOM. Instead, use safe methods to handle user input.

2. **Use Safe Methods**: Use methods like `textContent` instead of `innerHTML` to set the content of DOM elements. This prevents the execution of arbitrary scripts.

#### Validation and Sanitization

1. **Input Validation**: Validate all user inputs to ensure they meet the expected format and constraints. This helps prevent malicious inputs from being processed.

2. **Sanitization**: Sanitize user inputs to remove any potentially harmful characters or patterns. Libraries like DOMPurify can be used to sanitize HTML content.

#### Content Security Policy (CSP)

Content Security Policy (CSP) is a security mechanism that helps prevent XSS attacks by defining a set of rules for the browser to follow when loading resources. By implementing CSP, you can restrict the sources from which scripts can be loaded, thereby reducing the risk of XSS attacks.

Here’s an example of how to implement CSP in your web application:

```http
HTTP/1.1 200 OK
Content-Type: text/html
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-source.com

<!DOCTYPE html>
<html>
<head>
    <title>Secure Page</title>
</head>
<body>
    <script src="https://trusted-source.com/script.js"></script>
</body>
</html>
```

In this example, the `default-src` directive specifies that resources should only be loaded from the same origin (`'self'`). The `script-src` directive further restricts the sources from which scripts can be loaded, allowing only trusted sources.

### Common Pitfalls and Detection

#### Common Pitfalls

1. **Improper Input Handling**: Failing to properly validate and sanitize user inputs can lead to DOM-based XSS vulnerabilities.

2. **Over-reliance on Client-Side Security**: Relying solely on client-side security mechanisms without implementing server-side validation and sanitization can leave your application vulnerable.

#### Detection

Detecting DOM-based XSS vulnerabilities can be challenging, but there are several tools and techniques that can help:

1. **Static Analysis Tools**: Tools like ESLint and SonarQube can help identify potential security issues in your codebase.

2. **Dynamic Analysis Tools**: Tools like Burp Suite and OWASP ZAP can be used to test your application for vulnerabilities by simulating attacks.

3. **Manual Testing**: Manual testing is essential to ensure that your application is secure. Techniques like fuzzing and manual penetration testing can help identify vulnerabilities that automated tools may miss.

### Hands-On Practice Labs

To gain practical experience with DOM-based XSS vulnerabilities, you can use the following labs:

1. **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including modules on DOM-based XSS.
2. **OWASP Juice Shop**: A deliberately insecure web application that includes various security vulnerabilities, including DOM-based XSS.
3. **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, providing a platform to practice exploiting and defending against various web vulnerabilities.

### Conclusion

DOM-based vulnerabilities are a significant threat to web applications, but with proper understanding and implementation of secure coding practices, validation, sanitization, and security mechanisms like CSP, they can be effectively prevented. By staying vigilant and continuously testing your applications, you can ensure that they remain secure against these types of attacks.

---
<!-- nav -->
[[03-DOM-Based Vulnerabilities and DOM XSS Using Web Messages and JSON.parse|DOM-Based Vulnerabilities and DOM XSS Using Web Messages and JSON.parse]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[05-Exploiting DOM-Based XSS Using `window.postMessage`|Exploiting DOM-Based XSS Using `window.postMessage`]]
