---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a common web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. The goal of SQL Injection attacks is to manipulate the logic of these queries to gain unauthorized access to sensitive data or to perform unauthorized actions within the database.

### What is SQL Injection?

SQL Injection occurs when user input is incorrectly filtered by a web application and is then passed into a SQL query. This can happen in various contexts, such as search fields, login forms, or any other form of user input. The attacker can inject malicious SQL statements into the input fields, which can alter the intended behavior of the SQL query.

#### Why Does SQL Injection Matter?

SQL Injection is significant because it can lead to severe security breaches. An attacker can use SQL Injection to:

- Retrieve sensitive data from the database.
- Modify or delete data in the database.
- Execute administrative operations on the database, such as shutting it down.
- Bypass authentication mechanisms.

### How Does SQL Injection Work?

To understand how SQL Injection works, consider a simple login form where a user enters their username and password. The application might construct a SQL query like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the application does not properly sanitize the user input, an attacker could inject a malicious SQL statement. For example, if the attacker inputs `'' OR '1'='1` as the username, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Real-World Example: CVE-2021-22205

A notable real-world example of SQL Injection is CVE-2021-22205, which affected the popular WordPress plugin WPForms. The vulnerability allowed attackers to inject malicious SQL code through the plugin’s form submissions, potentially leading to unauthorized access to the database.

### Lab Setup: Web Security Academy

For this lab, we will use the Web Security Academy provided by PortSwigger. To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Click on the "Sign Up" button to create an account.
3. Once logged in, navigate to the "Academy" section.
4. Select the "Learning Path" and then choose "SQL Injection".
5. Under "Examining the Database", find the lab titled "SQL Injection Attack, listing the database contents on non-Oracle databases".

### Lab Overview

The lab contains a SQL injection vulnerability in the product category filter. The application returns the results of the query in its response, allowing us to use a union-based SQL injection attack to retrieve data from other tables. The application also has a login function, and the database contains a table that holds usernames and passwords.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/02-SQL Injection Overview|SQL Injection Overview]]
