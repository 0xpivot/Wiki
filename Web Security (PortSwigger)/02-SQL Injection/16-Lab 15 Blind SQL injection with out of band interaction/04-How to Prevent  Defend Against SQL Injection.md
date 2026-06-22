---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

### Secure Coding Practices

1. **Use Parameterized Queries**: Ensure that all SQL queries use parameterized inputs to prevent attackers from injecting malicious SQL code.
   
   ```sql
   SELECT * FROM products WHERE name = ?;
   ```

2. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.

### Database Hardening

1. **Least Privilege Principle**: Ensure that the application database user has the minimum necessary privileges to perform its tasks.
   
   ```sql
   GRANT SELECT, INSERT ON products TO app_user;
   ```

2. **Disable Unnecessary Functions**: Disable or remove unnecessary functions and procedures that can be exploited, such as `UTL_INADDR` in Oracle.

### Detection and Monitoring

1. **Database Auditing**: Enable auditing features in the database to log and monitor suspicious activities.
   
   ```sql
   AUDIT SELECT TABLE BY app_user;
   ```

2. **IDS/IPS Systems**: Deploy Intrusion Detection and Prevention Systems to detect and block SQL injection attempts.

### Real-World Examples

#### CVE-2021-21972

This vulnerability affected several web applications that used a vulnerable version of the `mysql_real_escape_string()` function. Attackers could bypass input validation and inject malicious SQL code.

#### Example Exploit

```sql
SELECT * FROM users WHERE username = 'admin' OR 1=1 --';
```

### Secure Code Fix

#### Vulnerable Code

```php
$query = "SELECT * FROM users WHERE username = '" . $_GET['username'] . "'";
```

#### Secure Code

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
$stmt->execute([$_GET['username']]);
```

### Conclusion

Blind SQL Injection with out-of-band interaction is a sophisticated attack vector that requires careful handling. By understanding the underlying mechanisms and implementing robust security measures, organizations can significantly reduce the risk of such attacks. Always stay updated with the latest security practices and tools to protect against evolving threats.

### Practice Labs

For hands-on experience with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various types of SQL Injection, including blind SQL Injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of SQL Injection attacks.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing skills, including SQL Injection.

By engaging with these labs, you can gain practical experience in identifying and mitigating SQL Injection vulnerabilities.

---
<!-- nav -->
[[03-Database-Specific Payloads|Database-Specific Payloads]] | [[Web Security (PortSwigger)/02-SQL Injection/16-Lab 15 Blind SQL injection with out of band interaction/00-Overview|Overview]] | [[05-Understanding SQL Injection|Understanding SQL Injection]]
