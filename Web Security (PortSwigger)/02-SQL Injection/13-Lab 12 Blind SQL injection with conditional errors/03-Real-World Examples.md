---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Real-World Examples

### Recent CVEs and Breaches

One notable example of a SQLi attack is the breach of the Equifax credit reporting agency in 2017. The attackers exploited a vulnerability in the Apache Struts framework, which allowed them to inject SQL commands and steal sensitive data.

Another example is the breach of the Panera Bread company in 2017, where attackers used SQLi to access customer data.

### How to Prevent / Defend

#### Detection

To detect SQLi attacks, organizations should implement the following measures:

1. **Web Application Firewalls (WAF)**: Use WAFs to monitor and block suspicious SQL queries.
2. **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns in SQL queries.
3. **Security Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, and Nessus to scan for vulnerabilities.

#### Prevention

To prevent SQLi attacks, organizations should follow these best practices:

1. **Parameterized Queries**: Use parameterized queries to ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate all user input to ensure it meets expected formats and lengths.
3. **Least Privilege Principle**: Ensure that database accounts used by applications have the least privileges necessary to perform their tasks.

#### Secure Coding Fixes

Here’s an example of a vulnerable SQL query and its secure counterpart:

##### Vulnerable Code

```php
$username = $_POST['username'];
$password = $_POST['password'];

$sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($conn, $sql);
```

##### Secure Code

```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
```

### Configuration Hardening

Organizations should also harden their database configurations to minimize the risk of SQLi attacks:

1. **Disable Unnecessary Features**: Disable unnecessary features and services in the database.
2. **Use Strong Passwords**: Ensure that all database accounts use strong, unique passwords.
3. **Regular Audits**: Perform regular audits of database configurations and permissions.

### Hands-On Labs

To practice and understand SQLi attacks better, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on SQLi and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various security attacks.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.

By thoroughly understanding the mechanics of SQLi attacks and implementing robust preventive measures, organizations can significantly reduce the risk of such attacks.

---
<!-- nav -->
[[02-Blind SQL Injection with Conditional Errors|Blind SQL Injection with Conditional Errors]] | [[Web Security (PortSwigger)/02-SQL Injection/13-Lab 12 Blind SQL injection with conditional errors/00-Overview|Overview]] | [[04-Types of SQL Injection|Types of SQL Injection]]
