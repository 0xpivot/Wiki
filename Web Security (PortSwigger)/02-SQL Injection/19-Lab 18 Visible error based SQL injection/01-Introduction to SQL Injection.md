---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection (SQLi) is a type of security vulnerability that allows an attacker to manipulate SQL queries executed by a web application. This manipulation can lead to unauthorized data access, data modification, or even complete system compromise. SQL Injection occurs when an attacker is able to inject malicious SQL code into a query that is executed by the application.

### What is SQL?

Structured Query Language (SQL) is a programming language used to manage relational databases. It allows users to perform various operations such as creating tables, inserting data, updating records, and querying data. SQL is widely used in web applications to interact with databases, making it a critical component of many systems.

### Why Does SQL Injection Matter?

SQL Injection is a significant threat because it can allow attackers to bypass authentication mechanisms, access sensitive data, and even execute commands on the underlying operating system. This can result in data breaches, financial losses, and reputational damage. Understanding SQL Injection is crucial for both developers and security professionals to ensure the integrity and confidentiality of data.

### How Does SQL Injection Work?

SQL Injection typically occurs when user input is improperly sanitized and directly included in SQL queries. An attacker can inject malicious SQL code into these queries, which can then be executed by the database server. The following steps illustrate the process:

1. **User Input**: The attacker provides input that includes SQL code.
2. **Query Construction**: The application constructs a SQL query using the user input.
3. **Execution**: The database executes the modified query, potentially leading to unintended actions.

### Example Scenario

Consider a simple login form where a user enters their username and password. The application might construct a SQL query like this:

```sql
SELECT * FROM users WHERE username = 'user_input' AND password = 'password_input';
```

If the user input is not properly sanitized, an attacker could inject SQL code to bypass authentication. For instance, if the attacker inputs `'' OR '1'='1` as the username, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'password_input';
```

This query will return all rows from the `users` table, effectively allowing the attacker to bypass authentication.

### Real-World Examples

#### CVE-2021-21972: Apache Struts 2

In 2021, a vulnerability was discovered in Apache Struts 2, a popular Java framework. The vulnerability allowed attackers to inject SQL code through the `redirectAction` parameter, leading to unauthorized data access. This CVE highlights the importance of proper input validation and sanitization in web applications.

#### Equifax Data Breach (2017)

The Equifax data breach, one of the largest in history, was partly due to an SQL Injection vulnerability. Attackers exploited a flaw in the Apache Struts framework, which allowed them to access sensitive personal information of millions of individuals. This breach underscores the severe consequences of SQL Injection attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/02-Exploiting the Vulnerability|Exploiting the Vulnerability]]
