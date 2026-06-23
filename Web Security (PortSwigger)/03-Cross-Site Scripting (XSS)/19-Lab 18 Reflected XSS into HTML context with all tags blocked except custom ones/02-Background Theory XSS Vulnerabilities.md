---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Background Theory: XSS Vulnerabilities

### What is XSS?

XSS vulnerabilities arise when a web application takes untrusted data and sends it to a web browser without proper validation or escaping. This allows an attacker to inject malicious scripts that can execute in the context of the victim's browser.

### Why Does XSS Matter?

XSS attacks can lead to severe consequences, including:

- **Data Theft**: Attackers can steal sensitive information like session tokens, cookies, and personal data.
- **Session Hijacking**: By stealing session tokens, attackers can impersonate legitimate users.
- **Defacement**: Attackers can alter the appearance of a website to spread misinformation.
- **Phishing**: Malicious scripts can redirect users to fake login pages to capture their credentials.

### How Does XSS Work?

XSS exploits occur when a web application fails to properly sanitize user inputs. For example, consider a simple search feature where the user input is directly embedded into the HTML response:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for: <?php echo $_GET['query']; ?></h1>
</body>
</html>
```

If an attacker inputs `<script>alert('XSS');</script>` into the search field, the resulting HTML would be:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for: <script>alert('XSS');</script></h1>
</body>
</html>
```

When this page is rendered, the script executes, displaying an alert box.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A stored XSS vulnerability was discovered in WordPress plugins, allowing attackers to inject malicious scripts into comments and posts.
- **Twitter Breach (2020)**: A series of XSS vulnerabilities were exploited to gain unauthorized access to high-profile accounts, including those of Barack Obama and Elon Musk.

These examples highlight the critical nature of securing web applications against XSS attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[03-Bypassing Tag Blocking|Bypassing Tag Blocking]]
