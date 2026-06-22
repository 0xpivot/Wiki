---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against Blind SQL Injection

### Secure Coding Practices

1. **Parameterized Queries**: Use parameterized queries to ensure that user input is treated as data rather than executable code.
   
   ```sql
   SELECT * FROM users WHERE id = ?
   ```

2. **Input Validation**: Validate and sanitize all user inputs to prevent malicious SQL code from being injected.

### Configuration Hardening

1. **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks.
   
   ```sql
   GRANT SELECT ON users TO webapp_user;
   ```

2. **Database Security Settings**: Enable security features such as SQL injection detection and prevention mechanisms provided by the database management system.

### Detection and Monitoring

1. **Intrusion Detection Systems (IDS)**: Implement IDS to monitor and detect suspicious SQL queries.
   
   ```mermaid
sequenceDiagram
       participant IDS
       participant WebApp
       participant Database

       WebApp->>Database: Execute Query
       Database-->>IDS: Log Query
       IDS-->>Administrator: Alert on Suspicious Activity
```

2. **Logging and Auditing**: Maintain detailed logs of all database activities to help identify and investigate potential SQL Injection attempts.

### Secure Code Examples

#### Vulnerable Code

```php
$query = "SELECT * FROM users WHERE id = '" . $_GET['id'] . "'";
$result = mysqli_query($conn, $query);
```

#### Secure Code

```php
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $_GET['id']);
$stmt->execute();
$result = $stmt->get_result();
```

### Hands-On Labs

For practical experience with Blind SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on SQL Injection, including time-based Blind SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including SQL Injection, for educational purposes.

---
<!-- nav -->
[[05-Extracting Data Using Time-Based Blind SQL Injection|Extracting Data Using Time-Based Blind SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/00-Overview|Overview]] | [[07-Lab Setup and Initial Analysis|Lab Setup and Initial Analysis]]
