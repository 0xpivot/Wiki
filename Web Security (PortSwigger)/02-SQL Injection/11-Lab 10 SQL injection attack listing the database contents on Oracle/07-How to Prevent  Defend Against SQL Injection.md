---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

Preventing SQL Injection requires a combination of secure coding practices, input validation, and proper configuration of the database and web application.

### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
2. **Parameterized Queries**: Parameterized queries separate the SQL logic from the user input, preventing SQL Injection.
3. **Input Validation**: Validate and sanitize all user input to ensure it meets expected formats and constraints.

#### Example: Prepared Statement

Here is an example of using prepared statements in PHP:

```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $pdo->prepare("SELECT * FROM users WHERE username = :username AND password = :password");
$stmt->execute(['username' => $username, 'password' => $password]);
$user = $stmt->fetch();
```

### Input Validation

Validate and sanitize all user input to ensure it meets expected formats and constraints. For example, use regular expressions to validate email addresses, phone numbers, etc.

#### Example: Input Validation

Here is an example of input validation in PHP:

```php
function validateInput($input) {
    // Add your validation logic here
    return preg_match("/^[a-zA-Z0-9_]+$/", $input);
}

$username = $_POST['username'];
if (!validateInput($username)) {
    die("Invalid username");
}
```

### Proper Configuration

Configure the database and web application to minimize the risk of SQL Injection.

1. **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks.
2. **Error Handling**: Disable detailed error messages that can reveal sensitive information about the database schema.
3. **Web Application Firewall (WAF)**: Use a WAF to filter out malicious SQL Injection attempts.

#### Example: Least Privilege Principle

Ensure that the database user has the minimum necessary privileges to perform its tasks:

```sql
GRANT SELECT, INSERT, UPDATE ON users TO webapp_user;
```

### Detection and Prevention Tools

Use automated tools to detect and prevent SQL Injection vulnerabilities.

1. **SQLMap**: Automate the process of detecting and exploiting SQL Injection vulnerabilities.
2. **Static Code Analysis Tools**: Use static code analysis tools to identify potential SQL Injection vulnerabilities in the codebase.

#### Example: Static Code Analysis Tool

Use a static code analysis tool like SonarQube to identify potential SQL Injection vulnerabilities in the codebase:

```bash
sonar-scanner
```

### Conclusion

SQL Injection is a serious security vulnerability that can lead to severe consequences. By understanding how SQL Injection works and taking appropriate measures to prevent it, we can protect our web applications from this type of attack.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice SQL Injection and other web security techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application with multiple security vulnerabilities for educational purposes.

By completing these labs, you can gain practical experience in identifying and exploiting SQL Injection vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/06-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/00-Overview|Overview]] | [[08-Identifying Vulnerable Input Fields|Identifying Vulnerable Input Fields]]
