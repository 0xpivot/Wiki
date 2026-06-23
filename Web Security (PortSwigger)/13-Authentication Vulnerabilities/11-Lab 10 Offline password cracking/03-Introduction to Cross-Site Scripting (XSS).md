---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. This vulnerability allows attackers to inject malicious scripts into web pages viewed by other users. XSS attacks can lead to various security issues, including session hijacking, defacement of websites, and theft of sensitive data.

### What is XSS?

XSS vulnerabilities occur when an application includes untrusted data in a web page without proper validation or escaping. This can allow an attacker to execute arbitrary scripts in the context of the victim's browser. There are three main types of XSS:

1. **Reflected XSS**: The injected script comes from the current HTTP request.
2. **Stored XSS**: The injected script is permanently stored on the server.
3. **DOM-based XSS**: The vulnerability exists in the client-side code rather than the server-side code.

### Why Does XSS Matter?

XSS attacks can have severe consequences, such as stealing cookies, session tokens, and other sensitive information. They can also be used to perform actions on behalf of the user, such as posting messages, changing settings, or even transferring funds.

### How Does XSS Work?

To understand XSS, consider the following scenario:

1. **Injection Point**: An attacker finds a place in the application where user input is reflected back to the user without proper sanitization.
2. **Script Injection**: The attacker injects a malicious script into the input field.
3. **Execution**: When the user views the page, the browser executes the injected script.

### Example: Reflected XSS

Let's take a closer look at the example provided in the lecture transcript. The application reflects user input in the comment field of a blog post. An attacker can inject a script into this field, which will be executed when the user views the post.

#### Code Example

Consider the following HTML form for posting comments:

```html
<form action="/post-comment" method="POST">
    <input type="text" name="name" placeholder="Name">
    <textarea name="comment" placeholder="Comment"></textarea>
    <input type="submit" value="Post Comment">
</form>
```

If the application does not properly sanitize the input, an attacker can inject a script like this:

```html
<script>alert(1)</script>
```

When the user views the post, the browser will execute the script, displaying an alert box with the number `1`.

### Real-World Examples

Recent real-world examples of XSS vulnerabilities include:

- **CVE-2021-21972**: A stored XSS vulnerability in WordPress plugins allowed attackers to inject malicious scripts into posts and comments.
- **CVE-2022-22965**: A reflected XSS vulnerability in Microsoft Exchange Server allowed attackers to inject scripts into email messages.

### Detection and Prevention

#### Detection

To detect XSS vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A popular tool for web application security testing.
- **OWASP ZAP**: Another widely-used tool for detecting security vulnerabilities.

#### Prevention

To prevent XSS attacks, follow these best practices:

1. **Input Validation**: Ensure that all user inputs are validated and sanitized.
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

### Secure Coding Fixes

Here is an example of how to securely handle user input in a web application:

#### Vulnerable Code

```python
def post_comment(name, comment):
    return f"<div><strong>{name}</strong>: {comment}</div>"
```

#### Secure Code

```python
import html

def post_comment(name, comment):
    safe_name = html.escape(name)
    safe_comment = html.escape(comment)
    return f"<div><strong>{safe_name}</strong>: {safe_comment}</div>"
```

### Content Security Policy (CSP)

Implementing a Content Security Policy (CSP) can further mitigate the risk of XSS attacks. Here is an example of a CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com;
```

This policy restricts the sources of scripts to the same origin and a trusted CDN.

### How to Prevent / Defend Against XSS

#### Detection

Use automated tools to scan your application for XSS vulnerabilities. Regularly review and update your security policies.

#### Prevention

1. **Input Validation**: Always validate and sanitize user inputs.
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code to understand the differences:

#### Vulnerable Code

```python
def post_comment(name, comment):
    return f"<div><strong>{name}</strong>: {comment}</div>"
```

#### Secure Code

```python
import html

def post_comment(name, comment):
    safe_name = html.escape(name)
    safe_comment = html.escape(comment)
    return f"<div><strong>{safe_name}</strong>: {safe_comment}</div>"
```

### Hands-On Labs

To practice and reinforce your understanding of XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about XSS and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

### Conclusion

Understanding and preventing XSS vulnerabilities is crucial for securing web applications. By following best practices and using secure coding techniques, you can significantly reduce the risk of XSS attacks.

---

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/11-Lab 10 Offline password cracking/02-Introduction to Authentication Vulnerabilities|Introduction to Authentication Vulnerabilities]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/11-Lab 10 Offline password cracking/00-Overview|Overview]] | [[04-Additional Depth on XSS Vulnerabilities|Additional Depth on XSS Vulnerabilities]]
