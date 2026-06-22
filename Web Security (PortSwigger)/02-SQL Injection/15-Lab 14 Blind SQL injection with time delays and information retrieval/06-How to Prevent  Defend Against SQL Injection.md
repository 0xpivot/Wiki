---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

### Secure Coding Practices

1. **Parameterized Queries**: Use parameterized queries to ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate and sanitize user input to prevent malicious SQL code from being injected.
3. **Least Privilege Principle**: Ensure that the database user has the least privileges necessary to perform its tasks.

### Secure Configuration

1. **Disable Unnecessary Features**: Disable unnecessary features and functions in the database to reduce the attack surface.
2. **Use Prepared Statements**: Use prepared statements to separate SQL logic from user input.
3. **Enable Query Logging**: Enable query logging to monitor and detect suspicious activity.

### Secure-Coding Fixes

#### Vulnerable Code

```php
$name = $_GET['name'];
$query = "SELECT * FROM products WHERE name LIKE '%$name%'";
$result = mysqli_query($conn, $query);
```

#### Secure Code

```php
$name = $_GET['name'];
$stmt = $conn->prepare("SELECT * FROM products WHERE name LIKE ?");
$stmt->bind_param("s", "%$name%");
$stmt->execute();
$result = $stmt->get_result();
```

### Configuration Hardening

#### MySQL Configuration

```ini
[mysqld]
sql_mode=NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
```

#### PostgreSQL Configuration

```ini
# postgresql.conf
log_statement = 'all'
```

### Detection Tools

1. **OWASP ZAP**: OWASP ZAP is a free and open-source web application security scanner that can detect SQL Injection vulnerabilities.
2. **Burp Suite**: Burp Suite is a commercial web application security testing tool that includes features for detecting SQL Injection vulnerabilities.
3. **SQLMap**: SQLMap is an open-source penetration testing tool that automates the process of detecting and exploiting SQL Injection vulnerabilities.

### Hands-On Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice various types of SQL Injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/05-Common Pitfalls and Detection|Common Pitfalls and Detection]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/07-Conclusion|Conclusion]]
