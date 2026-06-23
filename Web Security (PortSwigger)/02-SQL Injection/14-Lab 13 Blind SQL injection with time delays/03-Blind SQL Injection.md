---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Blind SQL Injection

Blind SQL Injection is a variant of SQL Injection where the attacker cannot see the output of the injected SQL query directly. Instead, the attacker must infer the results based on the application's behavior. This makes the exploitation process more challenging but also more stealthy.

### What is Blind SQL Injection?

In Blind SQL Injection, the application does not return any data from the SQL query directly. Instead, the attacker must deduce the results based on the application's response times, error messages, or other indirect indicators. This type of injection is often used when the application sanitizes or filters the output of SQL queries.

### Why Does Blind SQL Injection Matter?

Blind SQL Injection is significant because it can be used to bypass basic security measures that prevent direct data exfiltration. Attackers can still extract sensitive information by making educated guesses about the database structure and contents.

### How Does Blind SQL Injection Work?

To understand Blind SQL Injection, consider a scenario where an application uses a tracking cookie for analytics. The application constructs an SQL query using the value of the submitted cookie. If the application does not properly validate the cookie value, an attacker can inject SQL code to manipulate the query.

For example, suppose the application constructs an SQL query like this:

```sql
SELECT * FROM analytics WHERE cookie = 'cookie_value';
```

An attacker can inject SQL code to delay the query execution, thereby inferring the result based on the response time. For instance, the attacker might inject `'; WAITFOR DELAY '0:0:5'--` as the cookie value, resulting in the following SQL query:

```sql
SELECT * FROM analytics WHERE cookie = ''; WAITFOR DELAY '0:0:5'--';
```

This query will wait for 5 seconds before returning, indicating that the injected SQL code was executed successfully.

### Real-World Example: CVE-2020-14882

A notable real-world example of Blind SQL Injection is CVE-2020-14882, which affected the Joomla CMS. The vulnerability allowed attackers to inject SQL code through the search functionality, leading to unauthorized access to sensitive data. This highlights the importance of proper input validation and sanitization in web applications.

---
<!-- nav -->
[[02-Lab 13 Blind SQL Injection with Time Delays|Lab 13 Blind SQL Injection with Time Delays]] | [[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/00-Overview|Overview]] | [[04-Exploiting the Vulnerability|Exploiting the Vulnerability]]
