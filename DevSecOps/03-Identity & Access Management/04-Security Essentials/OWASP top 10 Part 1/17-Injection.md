---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Injection

### Definition

Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. The attacker’s hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data.

### Types of Injection

There are several types of injection attacks, including SQL injection, OS command injection, and LDAP injection. Each type exploits different interpreters and can lead to severe consequences.

#### SQL Injection

SQL injection is one of the most common and dangerous types of injection attacks. It occurs when an attacker manipulates a SQL query by inserting malicious SQL code into input fields.

**Example:**
Consider a login form where the username and password are submitted to a backend server. The server constructs a SQL query to validate the credentials:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```

If an attacker inputs `username=' OR '1'='1` and leaves the password field empty, the resulting SQL query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will return all rows from the `users` table, effectively bypassing authentication.

### Real-World Example

A notable example of SQL injection is the breach of the Heartland Payment Systems in 2008. Attackers used SQL injection to steal sensitive credit card information from millions of customers.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Parameterized Queries**: Use parameterized queries or prepared statements to ensure that user input is treated as data, not executable code.
   
   ```sql
   SELECT * FROM users WHERE username = ? AND password = ?;
   ```

2. **Input Validation**: Validate and sanitize user input to ensure it conforms to expected formats and does not contain malicious characters.

#### Detection

1. **Static Code Analysis**: Tools like SonarQube and Fortify can identify potential SQL injection vulnerabilities in code.
2. **Dynamic Testing**: Penetration testing tools like Burp Suite and OWASP ZAP can simulate SQL injection attacks to detect vulnerabilities.

#### Secure Configuration

1. **Least Privilege Principle**: Ensure database accounts have the minimum necessary privileges to perform their tasks.
2. **Database Hardening**: Disable unnecessary features and services in the database to reduce the attack surface.

### Conclusion

Injection flaws are among the most critical security risks in web applications. By understanding the nature of these vulnerabilities and implementing robust preventive measures, organizations can significantly reduce the risk of successful injection attacks.

---

### Next Section: Broken Authentication

In the next section, we will delve into the second category of the OWASP Top 10: Broken Authentication. This category covers vulnerabilities related to the authentication mechanisms used in web applications, including weak session management and improper credential handling. Stay tuned for a detailed exploration of this critical security issue.

---
<!-- nav -->
[[17-Encryption and Data Protection|Encryption and Data Protection]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/OWASP top 10 Part 1/00-Overview|Overview]] | [[19-Insecure Data Transmission and Cryptographic Failures|Insecure Data Transmission and Cryptographic Failures]]
