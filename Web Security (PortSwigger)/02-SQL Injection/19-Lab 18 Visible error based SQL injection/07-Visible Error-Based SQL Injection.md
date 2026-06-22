---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Visible Error-Based SQL Injection

Visible Error-Based SQL Injection is a specific type of SQL Injection where the application returns detailed error messages to the user. These error messages often contain information about the structure of the database, which can be exploited by attackers to craft more sophisticated SQL Injection attacks.

### How It Works

In Visible Error-Based SQL Injection, the attacker injects SQL code that causes the application to generate an error. The error message returned by the application can reveal details about the database schema, such as table names, column names, and even data values. This information can be used to further exploit the vulnerability.

### Example Scenario

Consider a web application that uses a tracking cookie for analytics. The application constructs a SQL query using the value of the cookie:

```sql
SELECT * FROM analytics WHERE cookie = 'cookie_value';
```

If the attacker injects SQL code into the cookie value, such as `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM analytics WHERE cookie = '' OR '1'='1';
```

This query will cause an error if the injected code is not properly handled. The error message returned by the application might look something like this:

```
Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'OR '1'='1' at line 1
```

This error message reveals that the application is using MySQL and that the injected code caused a syntax error. The attacker can use this information to craft more sophisticated SQL Injection attacks.

### Real-World Example

#### CVE-2_2020-14882: WordPress REST API

In 2020, a vulnerability was discovered in the WordPress REST API that allowed attackers to inject SQL code through certain parameters. The application returned detailed error messages that revealed information about the database schema. This vulnerability highlights the importance of proper error handling and sanitization in web applications.

---
<!-- nav -->
[[06-Understanding Error-Based SQL Injection|Understanding Error-Based SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/08-Conclusion|Conclusion]]
