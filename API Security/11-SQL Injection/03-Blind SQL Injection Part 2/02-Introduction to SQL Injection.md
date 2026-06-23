---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Introduction to SQL Injection

SQL Injection is a common type of attack used to exploit vulnerabilities in web applications that use SQL databases. In a SQL Injection attack, an attacker manipulates input data to execute arbitrary SQL commands on the database. This can lead to unauthorized access to sensitive data, data manipulation, or even complete control of the database.

### What is SQL Injection?

SQL Injection occurs when an attacker injects malicious SQL statements through input fields in a web application. These inputs are typically passed to the backend database, which executes them. If the input is not properly sanitized or validated, the attacker can manipulate the SQL queries to perform unintended actions.

#### Why Does SQL Injection Matter?

SQL Injection attacks are significant because they can lead to severe consequences such as:

- **Data Theft**: Attackers can extract sensitive information from the database.
- **Data Manipulation**: Attackers can modify or delete data within the database.
- **Unauthorized Access**: Attackers can gain elevated privileges and access to the system.
- **Denial of Service**: Attackers can cause the database to crash or become unresponsive.

### How Does SQL Injection Work?

To understand SQL Injection, consider a simple login form that takes a username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the input is not properly sanitized, an attacker could enter a username like `admin' --` which would change the query to:

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything';
```

The `--` comments out the rest of the query, effectively logging in as the admin user without needing the correct password.

### Types of SQL Injection

There are several types of SQL Injection attacks, including:

- **Classic SQL Injection**: Directly injecting SQL code into input fields.
- **Blind SQL Injection**: Injecting SQL code without seeing the results directly.
- **Union-Based SQL Injection**: Using the UNION operator to combine results from multiple queries.
- **Time-Based SQL Injection**: Using time delays to infer the success of injected SQL code.

### Real-World Examples

One notable example of SQL Injection is the breach of the popular website MySpace in 2006. Attackers exploited a SQL Injection vulnerability to steal millions of user passwords. Another example is the SQL Injection attack on the Heartland Payment Systems in 2008, which resulted in the theft of over 130 million credit card numbers.

---
<!-- nav -->
[[API Security/11-SQL Injection/03-Blind SQL Injection Part 2/01-Introduction to Blind SQL Injection|Introduction to Blind SQL Injection]] | [[API Security/11-SQL Injection/03-Blind SQL Injection Part 2/00-Overview|Overview]] | [[API Security/11-SQL Injection/03-Blind SQL Injection Part 2/03-Blind SQL Injection|Blind SQL Injection]]
