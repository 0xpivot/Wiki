---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection (SQLi) is a type of cyber attack used to exploit vulnerabilities in web applications that interact with databases. Specifically, it involves inserting malicious SQL statements into input fields to manipulate the backend database. This technique can allow attackers to bypass authentication mechanisms, retrieve sensitive information, modify data, or even execute administrative operations on the database.

### Why SQL Injection Matters

SQL Injection attacks are significant because they can lead to severe consequences such as data theft, unauthorized access, and even complete system compromise. According to the Open Web Application Security Project (OWASP), SQL Injection is one of the most critical web application security risks.

### How SQL Injection Works

SQL Injection occurs when user input is not properly sanitized or validated before being included in an SQL query. This allows an attacker to inject arbitrary SQL code that can alter the intended behavior of the query. For instance, consider a simple login form where the user inputs their username and password. A typical SQL query might look like:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the input fields are not properly sanitized, an attacker could enter something like `'' OR '1'='1` for the username, which would result in the following query:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This modified query will return all rows from the `users` table, effectively bypassing authentication.

### Real-World Example: Recent Breaches

One notable example of a SQL Injection attack is the breach of the Equifax credit reporting agency in 2017. The attackers exploited a vulnerability in Apache Struts, which allowed them to inject SQL commands and gain access to sensitive personal data of millions of individuals. This breach highlights the severe consequences of SQL Injection attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/00-Overview|Overview]] | [[02-Blind-Based SQL Injection|Blind-Based SQL Injection]]
