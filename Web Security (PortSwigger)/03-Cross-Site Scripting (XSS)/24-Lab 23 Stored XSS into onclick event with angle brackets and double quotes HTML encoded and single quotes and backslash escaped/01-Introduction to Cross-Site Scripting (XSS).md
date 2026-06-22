---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications where an attacker can inject malicious scripts into web pages viewed by other users. XSS attacks can lead to various security issues such as session hijacking, data theft, and unauthorized actions performed on behalf of the victim.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, often in response to a user request, and then executed by the user's browser.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is later served to unsuspecting users.
3. **DOM-based XSS**: The vulnerability exists in the client-side JavaScript code rather than the server-side code. The script is executed based on the way the DOM is manipulated.

### Lab Overview

In this lab, we will focus on a **Stored XSS** vulnerability where the malicious script is stored in the database and then executed when a user clicks on a specific element. Specifically, the lab involves injecting a script into the `onclick` event of a comment author's name.

### Setup and Access

To access the lab, follow these steps:

1. Visit the Web Security Academy at [portswigger.net/web-security](https://portswigger.net/web-security).
2. Click on the "Sign up" button to create an account.
3. Once logged in, navigate to the "Academy" section.
4. Select "All Labs" and search for "cross-site scripting labs".
5. Locate and open lab number 23 titled "Stored XSS into OnClick event with angle brackets and double quotes, HTML encoded, and single quotes, and backslash escaped".

### Understanding the Vulnerability

The lab contains a stored XSS vulnerability in the comment functionality. The goal is to submit a comment that calls the `alert` function when the comment author's name is clicked.

#### Key Concepts

- **HTML Encoding**: Special characters like `<`, `>`, `"`, and `'` are encoded to prevent them from being interpreted as HTML tags.
- **Backslash Escaping**: Single quotes (`'`) are escaped using a backslash (`\`) to prevent them from being treated as string delimiters.

### Steps to Exploit the Vulnerability

1. **Identify the Input Field**: Find the input field where comments can be submitted.
2. **Craft the Malicious Payload**: Create a payload that includes the `alert` function within the `onclick` event.
3. **Submit the Comment**: Submit the crafted comment through the web interface.

#### Crafting the Payload

To craft the payload, we need to ensure that the `onclick` event is properly set up and that the payload bypasses the encoding and escaping mechanisms.

```html
<script>
function exploit() {
    var payload = "<script>alert('XSS');</script>";
    document.write(payload);
}
</script>
```

However, since the input is HTML-encoded and single quotes are backslash-escaped, we need to adjust our approach. We can use double quotes to define the `onclick` attribute and avoid issues with single quotes.

```html
<script>
function exploit() {
    var payload = '<img src="x" onerror="alert(\'XSS\');">';
    document.write(payload);
}
</script>
```

This payload uses an `img` tag with an `onerror` event to execute the `alert` function. The `onerror` event is triggered when the image source cannot be loaded, which is a common technique to bypass encoding and escaping.

### Submitting the Comment

Once the payload is crafted, submit it through the web interface. Ensure that the payload is correctly formatted and that the `onclick` event is properly set up.

#### Example Submission

```html
<img src="x" onerror="alert('XSS');">
```

When the comment is submitted, it will be stored in the database and displayed on the page. When a user clicks on the comment author's name, the `alert` function will be executed.

### Detection and Prevention

#### How to Detect XSS

1. **Automated Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, and Acunetix to scan for XSS vulnerabilities.
2. **Manual Testing**: Manually test input fields by injecting payloads and observing the behavior of the application.
3. **Code Review**: Perform a thorough code review to identify potential XSS vulnerabilities.

#### How to Prevent XSS

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
2. **Output Encoding**: Encode all user inputs before displaying them on the web page. Use libraries like `OWASP Java Encoder` or `Microsoft Anti-XSS Library`.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded.
4. **HTTP Headers**: Set appropriate HTTP headers such as `X-Content-Type-Options` and `X-Frame-Options` to mitigate certain types of XSS attacks.

### Secure Coding Practices

#### Vulnerable Code

```html
<!-- Vulnerable Code -->
<a href="#" onclick="alert('Clicked!')">Author Name</a>
```

#### Secure Code

```html
<!-- Secure Code -->
<a href="#" onclick="alert('Clicked!'); return false;">Author Name</a>
```

By adding `return false;` to the `onclick` event, we ensure that the default action of the link is prevented, reducing the risk of unintended behavior.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A stored XSS vulnerability was discovered in the WordPress plugin "WP GDPR Compliance". Attackers could inject malicious scripts into the plugin settings, leading to unauthorized actions.
- **CVE-2020-14182**: A reflected XSS vulnerability was found in the Atlassian Jira software. Attackers could inject malicious scripts into URLs, leading to session hijacking and data theft.

### Hands-On Practice

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs specifically designed to teach and test XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Understanding and preventing XSS vulnerabilities is crucial for maintaining the security of web applications. By following secure coding practices, implementing proper input validation and output encoding, and using automated scanning tools, developers can significantly reduce the risk of XSS attacks. Always stay updated with the latest security practices and regularly test your applications for vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/02-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]]
