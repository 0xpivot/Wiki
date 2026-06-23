---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples and Recent Breaches

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a reflected XSS vulnerability found in the WordPress plugin "WP GDPR Compliance". The plugin did not properly sanitize user input, allowing attackers to inject malicious scripts.

**Vulnerable Code:**

```php
echo "<script>var name = '" . $_GET['name'] . "';</script>";
```

**Exploit:**

An attacker could inject a payload like `', alert('XSS'), '` to break out of the string context and execute arbitrary JavaScript code.

### Real-World Example: CVE-2022-22965

CVE-2022-22965 is a reflected XSS vulnerability found in the Atlassian Jira application. The application did not properly encode user input in certain contexts, leading to potential XSS attacks.

**Vulnerable Code:**

```java
response.getWriter().write("<script>var input = '" + request.getParameter("input") + "';</script>");
```

**Exploit:**

An attacker could inject a payload like `", alert("XSS"), "` to break out of the string context and execute arbitrary JavaScript code.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/03-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/05-Understanding the Lab Scenario|Understanding the Lab Scenario]]
