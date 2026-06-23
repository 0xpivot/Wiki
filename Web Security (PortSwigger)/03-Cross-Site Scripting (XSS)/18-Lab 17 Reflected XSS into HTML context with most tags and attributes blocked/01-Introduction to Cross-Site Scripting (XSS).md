---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into web pages viewed by other users. XSS attacks can lead to various security issues such as stealing cookies, session tokens, and other sensitive information. There are three main types of XSS vulnerabilities:

1. **Reflected XSS**: The injected script is reflected off the web server, usually in response to a user's request. The script is then executed in the user's browser.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is later served to unsuspecting users.
3. **DOM-based XSS**: The vulnerability exists in the client-side code rather than the server-side code. The script is executed based on the way the DOM is manipulated.

### Lab Overview: Reflected XSS into HTML Context with Most Tags and Attributes Blocked

In this lab, we will explore a scenario where a web application is vulnerable to Reflected XSS, but the application uses a Web Application Firewall (WAF) to block common XSS vectors. The goal is to craft an XSS payload that bypasses the WAF and executes a JavaScript `print` function without requiring any user interaction.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Search for "cross-site scripting labs".
6. Locate and open lab number 17 titled "Reflected XSS into HTML Context with most tags and attributes blocked".

### Understanding the Vulnerability

The vulnerability in this lab is a Reflected XSS where the input is reflected in the HTML context. However, the application employs a WAF that blocks many common XSS vectors, including most HTML tags and attributes. This makes the task more challenging as we need to find a way to execute JavaScript without using typical tags like `<script>` or attributes like `onload`.

#### Background Theory

HTML context refers to the situation where user input is placed within an HTML document. The browser interprets this input as part of the HTML structure. For example, if a user input is inserted into an HTML element like `<div>`, the browser will parse this input as HTML.

### Crafting the Payload

Given the constraints of the WAF, we need to find a way to inject JavaScript that bypasses the WAF's filtering mechanisms. One approach is to use event handlers that are less commonly blocked by WAFs. For instance, the `href` attribute of an anchor tag (`<a>`) can be used to execute JavaScript.

#### Example Payload

Let's consider the following payload:

```html
<a href="javascript:print()">Click</a>
```

This payload attempts to execute the `print` function when the link is clicked. However, since the lab specifies that the solution must not require any user interaction, we need to find a way to automatically execute the script.

#### Using Event Handlers

One effective method is to use the `href` attribute combined with an event handler that triggers automatically. For example, the `onerror` event handler can be used to execute JavaScript when an error occurs.

Here is a refined payload:

```html
<img src="x" onerror="print()">
```

This payload uses an image tag with an invalid `src` attribute. When the browser fails to load the image, the `onerror` event handler is triggered, executing the `print` function.

### Testing the Payload

To test the payload, we need to send a request to the web application with our crafted input. The full HTTP request might look like this:

```http
GET /search?q=<img%20src=%22x%22%20onerror=%22print()%22> HTTP/1.1
Host: vulnerable-website.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Connection: close
```

The corresponding HTTP response should reflect the payload in the HTML context:

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <p>Your search for "<img src="x" onerror="print()">" returned no results.</p>
</body>
</html>
```

### How to Prevent / Defend Against XSS

#### Detection

To detect XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.

These tools can help identify potential XSS vulnerabilities by analyzing the application's responses to various inputs.

#### Prevention

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being processed by the application.
2. **Output Encoding**: Encode user inputs appropriately based on the context in which they are used. For example, use HTML entity encoding for HTML contexts.
3. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources from which scripts can be loaded. This helps mitigate the impact of XSS attacks.

#### Secure Coding Practices

Here is an example of insecure code:

```python
# Insecure code
def search(query):
    return f"<p>Your search for \"{query}\" returned no results.</p>"
```

And here is the secure version:

```python
# Secure code
import html

def search(query):
    safe_query = html.escape(query)
    return f"<p>Your search for \"{safe_query}\" returned no results.</p>"
```

By using `html.escape`, we ensure that any special characters in the user input are properly encoded, preventing them from being interpreted as HTML.

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-21972**: A critical vulnerability in Microsoft Exchange Server allowed attackers to inject arbitrary JavaScript code, leading to a full compromise of the server.
- **CVE-2020-14882**: A vulnerability in the WordPress REST API allowed attackers to inject malicious scripts, leading to a wide range of attacks including XSS.

### Hands-On Practice

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs specifically designed to teach and test XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and testing web security vulnerabilities.

### Conclusion

Understanding and mitigating XSS vulnerabilities is crucial for securing web applications. By carefully crafting payloads and implementing robust security measures, developers can significantly reduce the risk of XSS attacks. Always remember to validate and encode user inputs, and consider using tools like CSP to enhance security.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/18-Lab 17 Reflected XSS into HTML context with most tags and attributes blocked/00-Overview|Overview]] | [[02-Exploiting Reflected XSS|Exploiting Reflected XSS]]
