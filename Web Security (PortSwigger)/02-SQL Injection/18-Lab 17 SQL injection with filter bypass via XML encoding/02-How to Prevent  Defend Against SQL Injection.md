---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

### Detection

Detecting SQL Injection attempts can be done through various methods:

- **Logging and Monitoring**: Monitor logs for suspicious SQL queries.
- **Intrusion Detection Systems (IDS)**: Use IDS to detect and alert on potential SQL Injection attempts.

### Prevention

Preventing SQL Injection requires a multi-layered approach:

- **Input Validation**: Validate and sanitize all user inputs.
- **Parameterized Queries**: Use parameterized queries to separate SQL logic from user inputs.
- **Stored Procedures**: Use stored procedures to encapsulate SQL logic.
- **Least Privilege Principle**: Ensure database users have the least privilege necessary.

### Secure Coding Fixes

#### Vulnerable Code

```php
<?php
$username = $_GET['username'];
$password = $_GET['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($conn, $query);
?>
```

#### Secure Code

```php
<?php
$username = $_GET['username'];
$password = $_GET['password'];

$stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
?>
```

### Configuration Hardening

- **Disable Unnecessary Features**: Disable unnecessary features in the database that could be exploited.
- **Regular Updates**: Keep the database and WAF software up to date with the latest security patches.

### Real-World Example: Equifax Data Breach

The Equifax breach was caused by a vulnerability in the Apache Struts framework, which allowed SQL Injection. By implementing proper input validation and using parameterized queries, such vulnerabilities can be mitigated.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice SQL Injection techniques.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice various security attacks, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing.

By thoroughly understanding and practicing the concepts covered in this chapter, you can significantly enhance your ability to defend against SQL Injection attacks and ensure the security of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/18-Lab 17 SQL injection with filter bypass via XML encoding/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/18-Lab 17 SQL injection with filter bypass via XML encoding/00-Overview|Overview]] | [[03-Techniques to Bypass Web Application Firewalls|Techniques to Bypass Web Application Firewalls]]
