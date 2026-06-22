---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection (SQLi) is a type of cyber attack used to exploit vulnerabilities in web applications that use SQL databases. This attack allows an attacker to insert malicious SQL statements into input fields, which can then be executed by the database. SQL Injection attacks can lead to unauthorized data access, data manipulation, and even complete system compromise.

### What is SQL Injection?

SQL Injection occurs when user input is incorrectly filtered by a web application and is then passed to an SQL query. This can result in the execution of arbitrary SQL code by the server. The attacker can manipulate the SQL query to retrieve sensitive information, modify existing data, or perform other actions that could compromise the integrity and confidentiality of the database.

### Why Does SQL Injection Matter?

SQL Injection is one of the most common and dangerous types of web application vulnerabilities. According to the Open Web Application Security Project (OWASP), SQL Injection is listed as one of the top ten web application security risks. Real-world examples of SQL Injection attacks include:

- **CVE-2019-14287**: A SQL Injection vulnerability was found in the WordPress plugin "WP Event Booking". This allowed attackers to execute arbitrary SQL commands, potentially leading to data theft or manipulation.
- **CVE-2020-1938**: A SQL Injection vulnerability was discovered in the Joomla! CMS. This vulnerability allowed attackers to inject malicious SQL code, leading to unauthorized access to sensitive data.

### How Does SQL Injection Work?

To understand how SQL Injection works, consider a simple login form where a user enters their username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'username' AND password = 'password';
```

If the application does not properly sanitize the input, an attacker could enter something like `username' OR '1'='1` as the username. This would change the SQL query to:

```sql
SELECT * FROM users WHERE username = 'username' OR '1'='1' AND password = 'password';
```

Since `'1'='1'` is always true, the query will return all rows from the `users` table, effectively bypassing authentication.

### Types of SQL Injection

There are several types of SQL Injection attacks, including:

- **Error-Based SQL Injection**: The attacker uses error messages to gather information about the database structure.
- **Union-Based SQL Injection**: The attacker combines the results of two or more SELECT statements using the UNION operator.
- **Blind SQL Injection**: The attacker infers the structure of the database by observing the behavior of the application.

In this chapter, we will focus on **Blind SQL Injection with Conditional Errors**.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/13-Lab 12 Blind SQL injection with conditional errors/00-Overview|Overview]] | [[02-Blind SQL Injection with Conditional Errors|Blind SQL Injection with Conditional Errors]]
