---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into a webpage viewed by other users. This can lead to various attacks, such as stealing cookies, session tokens, and other sensitive data. XSS vulnerabilities can be categorized into three main types: Stored XSS, Reflected XSS, and DOM-based XSS.

### Stored XSS

Stored XSS, also known as Persistent XSS, occurs when the injected script is permanently stored on the server, such as in a database, and is later served to unsuspecting users. This type of XSS is particularly dangerous because the malicious script can affect multiple users over time.

#### Example Scenario

Consider a blog application where users can leave comments. If the application does not properly sanitize user input, an attacker can inject a malicious script into a comment. When other users view the blog post, their browsers execute the injected script, potentially compromising their sessions or stealing sensitive information.

### Lab 23: Stored XSS into `onclick` Event

In this lab, we will explore a scenario where the application stores user input in a comment section and renders it within an `onclick` event handler. The goal is to craft a payload that bypasses encoding and escaping mechanisms to trigger an alert box when the comment is clicked.

#### Understanding the Vulnerability

The application encodes angle brackets (`<`, `>`) and double quotes (`"`), and escapes single quotes (`'`) and backslashes (`\`). This means that direct injection of `<script>` tags or unescaped quotes will not work. We need to find a way to close the string context and execute JavaScript code.

#### Crafting the Payload

To craft the payload, we need to understand how the application processes and renders the input. The input is enclosed in single quotes and used within an `onclick` event handler. Our goal is to close the string context and execute a JavaScript function, such as `alert`.

1. **Initial Attempt:**
   - Close the string context using a single quote.
   - Inject the `alert` function.
   - Close the string context again.

```plaintext
' + alert(1) +
```

However, the application escapes single quotes, so this approach will not work. The input `' + alert(1) +` will be rendered as `\' + alert(1) +`, which is invalid JavaScript.

2. **Using HTML Entities:**
   - Instead of using single quotes, we can use their HTML entity equivalent (`&#39;`).
   - This bypasses the escaping mechanism and allows us to close the string context.

```plaintext
&#39; + alert(1) + &#39;
```

This payload will be rendered as:

```html
onclick="alert('test') + alert(1) + alert('test')"
```

When the comment is clicked, the `alert` function will be executed, displaying the message "1".

#### Full Example

Let's walk through the full process of crafting and testing the payload.

1. **Input the Payload:**
   - Navigate to the comment section of the blog post.
   - Enter the crafted payload: `&#39; + alert(1) + &#39;`.
   - Submit the comment.

2. **Inspect the Rendered Output:**
   - View the blog post and locate the submitted comment.
   - Inspect the HTML to ensure the payload is correctly rendered within the `onclick` event handler.

```html
<a href="#" onclick="alert('test') + alert(1) + alert('test')">Click me</a>
```

3. **Trigger the Alert:**
   - Click the comment to trigger the `alert` function.
   - Verify that the alert box appears with the message "1".

### Real-World Examples

#### Recent CVEs and Breaches

1. **CVE-2021-21972:**
   - A Stored XSS vulnerability was discovered in the WordPress plugin "WP GDPR Compliance." Attackers could inject malicious scripts into the plugin settings, affecting all users who viewed the settings page.
   
2. **CVE-2022-22965:**
   - A Stored XSS vulnerability was found in the Joomla component "JCE Editor." Attackers could inject malicious scripts into the editor settings, affecting all users who accessed the editor.

These real-world examples highlight the importance of proper input sanitization and validation to prevent XSS attacks.

### How to Prevent / Defend

#### Detection

1. **Automated Scanning Tools:**
   - Use tools like Burp Suite, OWASP ZAP, or commercial scanners to detect potential XSS vulnerabilities.
   - Regularly scan your web applications for known vulnerabilities.

2. **Manual Testing:**
   - Perform manual penetration testing to identify and validate XSS vulnerabilities.
   - Use payloads like `"><script>alert(1)</script>` to test for reflected XSS and `"><script>alert(document.cookie)</script>` to test for stored XSS.

#### Prevention

1. **Input Sanitization:**
   - Ensure all user inputs are properly sanitized before being stored or rendered.
   - Use libraries like OWASP Java Encoder or ESAPI for encoding user inputs.

2. **Content Security Policy (CSP):**
   - Implement a strict Content Security Policy (CSP) to restrict the sources of executable scripts.
   - Example CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com
```

3. **HTTP Headers:**
   - Set the `X-XSS-Protection` header to enable browser-based XSS protection:

```http
X-XSS-Protection: 1; mode=block
```

4. **Secure Coding Practices:**
   - Avoid directly embedding user inputs in JavaScript contexts.
   - Use template engines that automatically escape user inputs.

#### Secure Code Fix

Here is an example of how to securely handle user inputs in a web application:

**Vulnerable Code:**

```php
<?php
$comment = $_POST['comment'];
echo "<a href='#' onclick='alert('$comment')'>Click me</a>";
?>
```

**Fixed Code:**

```php
<?php
$comment = htmlspecialchars($_POST['comment'], ENT_QUOTES, 'UTF-8');
echo "<a href='#' onclick='alert(\"$comment\")'>Click me</a>";
?>
```

In the fixed code, `htmlspecialchars` is used to encode special characters, preventing XSS attacks.

### Practice Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs to practice detecting and exploiting XSS vulnerabilities.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application with numerous security vulnerabilities, including XSS.

By thoroughly understanding and practicing the concepts covered in this chapter, you will be better equipped to identify and mitigate XSS vulnerabilities in web applications.

### Conclusion

Cross-Site Scripting (XSS) is a critical security vulnerability that can have severe consequences if left unmitigated. By understanding the different types of XSS, crafting effective payloads, and implementing robust defenses, you can significantly reduce the risk of XSS attacks in your web applications. Always stay vigilant and keep your applications up-to-date with the latest security practices.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/24-Lab 23 Stored XSS into onclick event with angle brackets and double quotes HTML encoded and single quotes and backslash escaped/03-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]]
