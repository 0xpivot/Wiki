---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Bypassing XSS Filters

One common method to bypass XSS filters is by using whitespace characters. Browsers are generally lenient with whitespace in HTML and JavaScript, allowing attackers to insert spaces, tabs, or newlines to evade simple keyword-based filters.

### Example: Using Whitespace to Bypass Filters

Consider a scenario where the application filters out the string `JavaScript`. An attacker can bypass this filter by inserting a tab character between the letters:

```html
<script>
Ja vaScript:alert('XSS');
</script>
```

In this example, the browser will still interpret the script correctly despite the inserted tab.

#### Encoded Version of Whitespace

Attackers can also use the encoded version of whitespace characters. For instance, the tab character (`\t`) can be represented as `%09` in URL encoding:

```html
<script>
Ja%09vaScript:alert('XSS');
</script>
```

This encoded version will still be interpreted as valid JavaScript by the browser.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example where an XSS vulnerability was exploited in a popular web application. The vulnerability was due to insufficient input validation and sanitization, allowing attackers to inject malicious scripts. The attackers used whitespace evasion techniques to bypass the application's filters.

#### Full HTTP Request and Response

Here is a sample HTTP request and response demonstrating the exploitation:

```http
POST /search HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded

query=Ja%09vaScript:alert('XSS')
```

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <script>
        Ja%09vaScript:alert('XSS');
    </script>
</body>
</html>
```

### Detection and Prevention

To prevent XSS attacks, it is essential to implement robust input validation and output encoding. Here are some steps to defend against XSS:

1. **Input Validation**: Ensure that all user inputs are validated against a strict set of rules. Reject any input that does not conform to these rules.
2. **Output Encoding**: Encode all user inputs before rendering them in the HTML document. This ensures that any malicious scripts are rendered harmless.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This helps mitigate the risk of XSS attacks.

#### Secure Coding Practices

Here is an example of insecure code and its secure counterpart:

**Insecure Code:**

```php
<?php
$user_input = $_GET['query'];
echo "<script>$user_input</script>";
?>
```

**Secure Code:**

```php
<?php
$user_input = htmlspecialchars($_GET['query'], ENT_QUOTES, 'UTF-8');
echo "<script>$user_input</script>";
?>
```

### How to Prevent / Defend

1. **Detection**: Regularly scan your web application for XSS vulnerabilities using tools like Burp Suite, OWASP ZAP, or automated scanners.
2. **Prevention**: Implement input validation and output encoding as described above.
3. **Hardening**: Configure your web server and application to enforce strict security policies. Use tools like ModSecurity to enhance your defenses.

### Hands-On Practice

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive challenges and tutorials on XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

---
<!-- nav -->
[[02-What is Cross-Site Scripting (XSS)|What is Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[04-Content Security Policy Cheat Sheet|Content Security Policy Cheat Sheet]]
