---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection (SQLi) is a type of security vulnerability that allows an attacker to manipulate SQL queries executed by a web application. This manipulation can lead to unauthorized data access, data modification, or even complete system compromise. SQL Injection vulnerabilities arise due to improper input validation and sanitization, allowing attackers to inject malicious SQL code into user inputs.

### What is SQL Injection?

SQL Injection occurs when an attacker can insert or "inject" SQL code into a web application's input fields, which are then executed by the database. This can happen through various input points such as form fields, URL parameters, cookies, and more. The injected SQL code can alter the intended behavior of the SQL query, leading to unintended actions.

### Why Does SQL Injection Matter?

SQL Injection is significant because it can lead to severe consequences, including:

- **Data Theft**: Attackers can extract sensitive information like usernames, passwords, credit card details, etc.
- **Data Manipulation**: Attackers can modify or delete data within the database.
- **Unauthorized Access**: Attackers can gain administrative privileges and control over the entire database.
- **Denial of Service**: By injecting malicious SQL code, attackers can cause the application to crash or become unresponsive.

### How Does SQL Injection Work?

To understand SQL Injection, consider a simple login form where a user enters their username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'user_input' AND password = 'password_input';
```

If the application does not properly sanitize the `user_input` and `password_input`, an attacker could inject malicious SQL code. For example, if the attacker inputs `'' OR '1'='1` as the username, the resulting SQL query would look like this:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'password_input';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Real-World Example: CVE-2021-21972

A notable real-world example of SQL Injection is CVE-2021-21972, which affected the WordPress plugin WP eCommerce. The vulnerability allowed attackers to inject SQL code through the search functionality, leading to unauthorized access to sensitive data. This highlights the importance of proper input validation and sanitization in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/00-Overview|Overview]] | [[02-Lab 13 Blind SQL Injection with Time Delays|Lab 13 Blind SQL Injection with Time Delays]]
