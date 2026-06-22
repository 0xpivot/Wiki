---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into web pages viewed by other users. XSS attacks can lead to various harmful outcomes, including stealing sensitive data, session hijacking, and even spreading malware. There are three main types of XSS: Stored XSS, Reflected XSS, and DOM-based XSS. In this chapter, we will focus on Stored XSS and DOM-based XSS, providing detailed explanations, real-world examples, and comprehensive defense strategies.

### Stored Cross-Site Scripting (XSS)

Stored XSS, also known as Persistent XSS, is a type of XSS where the malicious script is permanently stored on the target server. When a user visits the affected page, the script is executed in their browser. This can lead to widespread damage, especially if the script is designed to propagate itself.

#### Example: MySpace Worm

One of the most famous examples of a Stored XSS attack is the MySpace worm. In 2005, Samy Kamkar exploited a Stored XSS vulnerability on MySpace to create a worm that spread across the platform. Here’s how it worked:

1. **Injection**: Samy injected a script into his profile that would execute whenever someone visited his profile.
2. **Propagation**: The script automatically added Samy as a friend and copied the malicious script into the victim’s profile.
3. **Spread**: When others visited the victim’s profile, the same process repeated, leading to exponential propagation.

This worm eventually caused MySpace to go offline temporarily as they had to manually remove the malicious scripts from all affected profiles.

#### How Stored XSS Works

To understand Stored XSS, let’s break down the steps involved:

1. **Injection Point**: An attacker finds a place in the web application where user input is stored and later displayed to other users.
2. **Malicious Input**: The attacker injects a script into this input field.
3. **Storage**: The web application stores the malicious input in its database.
4. **Display**: When another user views the page containing the malicious input, the script is executed in their browser.

#### Real-World Example: CVE-2018-1337

A notable real-world example of Stored XSS is CVE-2018-1337, which affected WordPress plugins. The vulnerability allowed attackers to inject malicious scripts into comments or posts, which were then stored and displayed to other users.

```http
POST /wp-comments-post.php HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

comment=<script>alert('XSS');</script>&submit=Submit
```

In this example, the attacker injects a simple `alert` script into a comment form. When another user views the post, the script executes, potentially leading to more serious attacks.

#### How to Prevent / Defend Against Stored XSS

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being stored in the database.
2. **Output Encoding**: Encode all user-generated content before displaying it to other users. This prevents scripts from executing.
3. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded.
4. **Secure Coding Practices**: Follow secure coding practices such as using parameterized queries and avoiding direct insertion of user input into SQL queries.

**Vulnerable Code Example**:
```php
<?php
$comment = $_POST['comment'];
// Vulnerable: Directly inserting user input into the database
$query = "INSERT INTO comments (content) VALUES ('$comment')";
mysqli_query($conn, $query);
?>
```

**Fixed Code Example**:
```php
<?php
$comment = $_POST['comment'];
// Fixed: Sanitize and encode user input
$safeComment = htmlspecialchars($comment, ENT_QUOTES, 'UTF-8');
$query = "INSERT INTO comments (content) VALUES (?)";
$stmt = mysqli_prepare($conn, $query);
mysqli_stmt_bind_param($stmt, "s", $safeComment);
mysqli_stmt_execute($stmt);
?>
```

### DOM-Based Cross-Site Scripting (XSS)

DOM-based XSS is a type of XSS where the attack payload is executed as a result of modifying the Document Object Model (DOM) of the victim user. Unlike Stored and Reflected XSS, DOM-based XSS does not involve the server; the attack is purely client-side.

#### Understanding the DOM

The Document Object Model (DOM) is a programming interface for HTML and XML documents. It represents the structure of a document as a tree of objects, allowing JavaScript to interact with and modify the document dynamically.

When a web page is loaded into a browser, the browser parses the HTML and constructs the DOM tree. JavaScript can then access and manipulate this tree to change the content of the page.

#### Example: DOM-Based XSS Attack

Consider a web application that uses JavaScript to display a user’s name from the URL hash:

```javascript
var userName = window.location.hash.substring(1);
document.getElementById("greeting").innerHTML = "Hello, " + userName;
```

An attacker could exploit this by crafting a URL like `https://example.com/#<script>alert('XSS')</script>`. When a user clicks this link, the script is executed in their browser.

#### How DOM-Based XSS Works

1. **Attack Vector**: The attacker crafts a URL or other input that contains a script.
2. **Execution**: The script is executed in the context of the current page due to the way the DOM is manipulated.
3. **Impact**: The script can perform actions such as stealing cookies, redirecting the user, or displaying alerts.

#### Real-World Example: CVE-2019-11358

CVE-2019-11358 is a DOM-based XSS vulnerability found in the jQuery library. The vulnerability allowed attackers to inject malicious scripts through the `$.parseHTML()` function.

```javascript
var html = "<img src=x onerror=alert('XSS')>";
$.parseHTML(html);
```

In this example, the `$.parseHTML()` function parses the HTML string and creates DOM nodes, which can then execute the `onerror` event handler.

#### How to Prevent / Defend Against DOM-Based XSS

1. **Sanitize Inputs**: Ensure that all user inputs are properly sanitized before being used to modify the DOM.
2. **Use Safe Methods**: Use safe methods for manipulating the DOM, such as setting text content instead of HTML content.
3. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded.
4. **Secure Coding Practices**: Follow secure coding practices such as validating and encoding user inputs.

**Vulnerable Code Example**:
```javascript
var userName = window.location.hash.substring(1);
document.getElementById("greeting").innerHTML = "Hello, " + userName;
```

**Fixed Code Example**:
```javascript
var userName = window.location.hash.substring(1);
// Fixed: Sanitize user input
var safeUserName = decodeURIComponent(userName).replace(/</g, '&lt;').replace(/>/g, '&gt;');
document.getElementById("greeting").textContent = "Hello, " + safeUserName;
```

### Conclusion

Cross-Site Scripting (XSS) is a critical security vulnerability that can have severe consequences if not properly mitigated. Both Stored XSS and DOM-based XSS require careful attention to input validation, output encoding, and secure coding practices. By understanding the mechanisms behind these attacks and implementing robust defenses, developers can significantly reduce the risk of XSS vulnerabilities in their web applications.

### Practice Labs

For hands-on experience with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive challenges and tutorials on various web security topics, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including XSS.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including XSS.
- **WebGoat**: An interactive, gamified training application for learning about web security vulnerabilities and exploits.

By engaging with these labs, you can gain practical experience in identifying, exploiting, and defending against XSS vulnerabilities.

---
<!-- nav -->
[[04-Content Security Policy Cheat Sheet|Content Security Policy Cheat Sheet]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[06-Detailed Explanation of XSS Contexts and Payloads|Detailed Explanation of XSS Contexts and Payloads]]
