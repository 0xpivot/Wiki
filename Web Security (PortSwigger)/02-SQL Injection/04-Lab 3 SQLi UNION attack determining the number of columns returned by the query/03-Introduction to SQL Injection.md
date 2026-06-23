---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection (SQLi) is a type of cyber attack used to exploit vulnerabilities in web applications that use SQL databases. An attacker can inject malicious SQL statements into input fields or other parts of the application to manipulate the database and gain unauthorized access to sensitive data. SQLi attacks can lead to data theft, data manipulation, and even complete system compromise.

### What is SQL Injection?

SQL Injection occurs when an attacker is able to insert or "inject" a SQL query through the input data from the client to the application. The attacker's injected SQL code is executed by the database engine, leading to unauthorized access to the database or manipulation of the data.

#### Why Does SQL Injection Matter?

SQL Injection is a critical security issue because it can lead to significant data breaches. For instance, in 2017, a SQLi vulnerability was exploited to steal personal data from Equifax, affecting approximately 147 million people. This breach resulted in financial losses and reputational damage for the company.

### How Does SQL Injection Work?

To understand how SQL Injection works, consider a simple login form where a user enters their username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'username' AND password = 'password';
```

If the application does not properly sanitize the input, an attacker could inject a malicious SQL statement. For example, if the attacker inputs `username' OR '1'='1` as the username, the resulting SQL query would be:

```sql
SELECT * FROM users WHERE username = 'username' OR '1'='1' AND password = 'password';
```

This query will return all rows from the `users` table because `'1'='1'` is always true, effectively bypassing authentication.

### Real-World Example: Equifax Data Breach

In 2017, Equifax suffered a massive data breach due to a SQL Injection vulnerability. The attackers exploited a flaw in the Apache Struts framework, which allowed them to execute arbitrary SQL commands. This led to the theft of sensitive personal information, including Social Security numbers, birth dates, and addresses.

### SQL Injection Union Attack

A SQL Injection Union attack is a specific type of SQLi where the attacker uses the `UNION` operator to combine the results of two or more SELECT statements. This technique allows the attacker to retrieve data from different tables within the same database.

### Lab Setup

For this lab, we will use the PortSwigger Web Security Academy, which provides a controlled environment to practice and learn about various web security vulnerabilities, including SQL Injection.

1. **Sign Up**: Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security) and sign up for an account.
2. **Access the Lab**: Once logged in, navigate to the Academy section, select the learning path for SQL Injection, and choose the lab titled "SQL Injection Union Attack, determining the number of columns returned by the query."

---
<!-- nav -->
[[02-Introduction to SQL Injection and Union Attacks|Introduction to SQL Injection and Union Attacks]] | [[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/00-Overview|Overview]] | [[04-Background Knowledge on SQL Injection and Union Operator|Background Knowledge on SQL Injection and Union Operator]]
