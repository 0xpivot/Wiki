---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a type of security vulnerability that allows an attacker to manipulate SQL queries executed by an application. This manipulation can lead to unauthorized data access, data modification, or even complete system compromise. SQL Injection vulnerabilities arise due to improper input validation and sanitization, allowing attackers to inject malicious SQL code into user inputs.

### What is SQL Injection?

SQL Injection occurs when an attacker is able to insert or "inject" SQL commands into an application's SQL query, which the application then executes. This can happen when user input is not properly sanitized or validated before being used in a SQL query.

#### Why Does SQL Injection Matter?

SQL Injection is significant because it can lead to severe consequences such as:

- **Data Leakage**: Attackers can extract sensitive data from the database.
- **Data Manipulation**: Attackers can modify or delete data in the database.
- **Privilege Escalation**: Attackers can gain elevated privileges within the database.
- **Denial of Service**: Attackers can cause the application to crash or become unresponsive.

### How Does SQL Injection Work?

To understand how SQL Injection works, consider a simple login form where the username and password are submitted to the server. The server might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'username' AND password = 'password';
```

If the application does not properly sanitize the input, an attacker could submit a specially crafted input to alter the SQL query. For example, an attacker might submit the following username:

```
' OR '1'='1
```

This would result in the following SQL query:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'password';
```

Since `'1'='1'` is always true, the query will return all rows from the `users` table, effectively bypassing authentication.

### Real-World Example: CVE-2021-21972

One recent example of SQL Injection is CVE-2021-21972, which affected the WordPress plugin WP Event Manager. The vulnerability allowed attackers to inject SQL code through the search functionality, leading to unauthorized data access. This demonstrates the importance of proper input validation and sanitization in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]] | [[02-Lab 14 Blind SQL Injection with Time Delays and Information Retrieval|Lab 14 Blind SQL Injection with Time Delays and Information Retrieval]]
