---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a common type of security vulnerability that allows an attacker to manipulate the backend database through user input. This can lead to unauthorized data access, data manipulation, and even complete system compromise. In this chapter, we will focus on a specific type of SQL Injection known as **Blind SQL Injection**, particularly using conditional responses to extract information from a database.

### What is SQL Injection?

SQL Injection occurs when an attacker is able to inject malicious SQL code into a query that is executed by the database. This can happen when user input is not properly sanitized or validated before being used in a SQL query. The injected SQL code can alter the intended behavior of the query, potentially allowing the attacker to read, modify, or delete sensitive data.

### Why Does SQL Injection Matter?

SQL Injection is a critical security issue because it can lead to significant data breaches and financial losses. According to the Open Web Application Security Project (OWASP), SQL Injection is one of the most dangerous vulnerabilities in web applications. Real-world examples include:

- **CVE-2019-14587**: A SQL Injection vulnerability was found in the WordPress plugin "WP Event Manager". This allowed attackers to execute arbitrary SQL commands, leading to potential data theft.
- **Equifax Breach (2017)**: One of the largest data breaches in history involved SQL Injection. Attackers exploited a vulnerability in Apache Struts, which led to the exposure of sensitive personal information of millions of users.

### How Does SQL Injection Work?

To understand SQL Injection, let's consider a simple example. Suppose we have a login form where a user enters their username and password. The backend code might look something like this:

```sql
SELECT * FROM users WHERE username = 'user_input' AND password = 'password_input';
```

If the user input is not properly sanitized, an attacker could enter a username such as `' OR '1'='1` and a password such as `' OR '1'='1`. This would change the SQL query to:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```

Since `1=1` is always true, the query would return all rows from the `users` table, effectively bypassing authentication.

### Types of SQL Injection

There are two main types of SQL Injection:

1. **Error-Based SQL Injection**: The attacker receives error messages from the database, which can provide useful information about the structure of the database.
2. **Blind SQL Injection**: The attacker does not receive any direct feedback from the database. Instead, they must infer information based on the application's behavior.

In this chapter, we will focus on **Blind SQL Injection** using conditional responses.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/12-Lab 11 Blind SQL injection with conditional responses/00-Overview|Overview]] | [[02-Blind SQL Injection with Conditional Responses|Blind SQL Injection with Conditional Responses]]
