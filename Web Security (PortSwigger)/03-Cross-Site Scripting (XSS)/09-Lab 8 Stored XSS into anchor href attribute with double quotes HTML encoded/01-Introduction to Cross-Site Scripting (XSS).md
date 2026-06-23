---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. This can lead to various attacks such as stealing sensitive data, session hijacking, and defacement of websites. XSS vulnerabilities arise due to the lack of proper input validation and output encoding on web applications.

### Types of XSS Vulnerabilities

There are three main types of XSS vulnerabilities:

1. **Stored XSS**: The malicious script is permanently stored on the server and served to users whenever they visit the affected page.
2. **Reflected XSS**: The malicious script is included in the URL or form data and is immediately reflected back to the user.
3. **DOM-based XSS**: The vulnerability exists within the client-side JavaScript code rather than the server-side code.

In this lab, we will focus on a **Stored XSS** vulnerability where the malicious script is stored in the database and then rendered in the HTML response.

### Lab Overview

The lab we are working on is titled "Stored XSS into Anchor `href` attribute with double quotes HTML encoded." This means that the application stores user input in a comment section, which is later rendered in an HTML anchor (`<a>`) tag. The input is enclosed in double quotes and is subject to HTML encoding.

### Setting Up the Lab Environment

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the "Sign up" button to create an account.
3. Once logged in, navigate to the "Academy" section.
4. Select "All Labs" and search for "cross-site scripting labs."
5. Find and open Lab No. 8 titled "Stored XSS into Anchor `href` attribute with double quotes HTML encoded."

### Understanding the Vulnerability

#### Background Theory

When a user submits a comment, the application stores the input in the database. Later, when the comment is displayed, it is rendered within an HTML anchor tag. If the input is not properly sanitized, an attacker can inject a malicious script that will execute when the comment is viewed.

#### Example Scenario

Consider the following HTML snippet:

```html
<a href="javascript:alert('XSS')">Click me</a>
```

If an attacker can inject this script into the `href` attribute, clicking the link will trigger the `alert` function, displaying "XSS" to the user.

### Identifying the Vulnerability

To identify the vulnerability, we need to understand how the application handles user input. Specifically, we need to determine if the input is properly sanitized and encoded before being rendered in the HTML response.

#### Steps to Identify the Vulnerability

1. **Access the Comment Section**: Navigate to the comment section of the post.
2. **Submit a Test Input**: Submit a comment with a simple test string, such as `<script>alert('test')</script>`.
3. **Inspect the Response**: Use Burp Suite to inspect the HTTP response and see how the input is rendered in the HTML.

### Exploiting the Vulnerability

To exploit the vulnerability, we need to craft a payload that will execute a script when the comment is viewed. Since the input is enclosed in double quotes and is subject to HTML encoding, we need to ensure our payload is correctly formatted.

#### Crafting the Payload

Given that the input is enclosed in double quotes and is subject to HTML encoding, we can use the following payload:

```html
<a href="javascript:alert('XSS')">Click me</a>
```

However, since the input is enclosed in double quotes, we need to ensure that the double quotes in our payload are properly escaped. We can achieve this by using the following payload:

```html
<a href="javascript:alert('XSS')">Click me</a>
```

This payload will be rendered as:

```html
<a href="javascript:alert(&quot;XSS&quot;)">Click me</a>
```

When the comment is viewed, clicking the link will trigger the `alert` function, displaying "XSS" to the user.

### Full HTTP Request and Response

Here is the complete HTTP request and response for submitting the comment:

#### HTTP Request

```http
POST /post/comment HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 42

comment=<a%20href=%22javascript:alert(%27XSS%27)%22>Click%20me</a>
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Post Comments</title>
</head>
<body>
    <h1>Comments</h1>
    <div id="comments">
        <div class="comment">
            <a href="javascript:alert(&quot;XSS&quot;)">Click me</a>
        </div>
    </div>
</body>
</html>
```

### How to Prevent / Defend Against XSS

#### Detection

To detect XSS vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A popular web application security testing tool that includes features for detecting and exploiting XSS vulnerabilities.
- **OWASP ZAP**: An open-source web application security scanner that can help identify XSS vulnerabilities.

#### Prevention

To prevent XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being processed.
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML response. Use context-sensitive encoding techniques such as HTML encoding, URL encoding, and JavaScript encoding.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources of executable scripts and prevent inline scripts from executing.
4. **Secure Coding Practices**: Follow secure coding practices such as using parameterized queries and avoiding direct inclusion of user inputs in HTML templates.

#### Secure Code Fix

Here is an example of how to securely handle user inputs in a web application:

##### Vulnerable Code

```python
# Vulnerable code
comment = request.form['comment']
response = f'<div><a href="{comment}">Click me</a></div>'
```

##### Secure Code

```python
# Secure code
from markupsafe import Markup

comment = request.form['comment']
encoded_comment = Markup.escape(comment)
response = f'<div><a href="{encoded_comment}">Click me</a></div>'
```

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-21972**: A stored XSS vulnerability was found in the WordPress plugin "WP User Avatar." Attackers could inject malicious scripts into user profiles, leading to potential session hijacking and data theft.
- **CVE-2022-22965**: A reflected XSS vulnerability was discovered in the Atlassian Jira software. Attackers could inject malicious scripts into URLs, leading to unauthorized access and data exfiltration.

### Hands-On Practice

To practice and reinforce your understanding of XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice different types of XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several XSS challenges.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that includes various security vulnerabilities, including XSS.

### Conclusion

Understanding and preventing XSS vulnerabilities is crucial for securing web applications. By following best practices such as input validation, output encoding, and implementing a Content Security Policy, you can significantly reduce the risk of XSS attacks. Always stay updated with the latest security practices and regularly test your applications for vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/09-Lab 8 Stored XSS into anchor href attribute with double quotes HTML encoded/00-Overview|Overview]] | [[02-Stored XSS into Anchor `href` Attribute with Double Quotes HTML Encoded|Stored XSS into Anchor `href` Attribute with Double Quotes HTML Encoded]]
