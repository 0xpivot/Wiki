---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Blind SQL Injection

Blind SQL Injection is a variant of SQL Injection where the attacker cannot see the results of their injected SQL code directly. Instead, the attacker must infer the success or failure of their injection based on the behavior of the application.

### What is Blind SQL Injection?

In Blind SQL Injection, the application does not return the results of the SQL query directly. Instead, the attacker must deduce the success or failure of their injection by observing changes in the application's behavior. This makes the attack more challenging but also more stealthy.

#### Why Does Blind SQL Injection Matter?

Blind SQL Injection is significant because it can be used to extract data from a database even when the application does not return the results of the SQL query. This makes it a powerful technique for attackers to bypass basic security measures.

### How Does Blind SQL Injection Work?

To perform a Blind SQL Injection attack, the attacker must carefully craft SQL queries that cause the application to behave differently based on the results of the query. This can be done using various techniques, including time delays and conditional errors.

#### Example: Time-Based Blind SQL Injection

Consider a scenario where an application uses a tracking cookie for analytics and performs an SQL query containing the value of the submitted cookie. The results of the SQL query are not returned, and the application does not respond differently based on whether the query returns any rows or causes any error.

The attacker can inject a time delay into the SQL query to determine if the query was successful. For example, the attacker might submit the following cookie value:

```
' OR IF(SUBSTRING(@@version,1,1)='5', SLEEP(5), 0) -- 
```

This query checks if the first character of the MySQL version is '5'. If it is, the query will cause a 5-second delay. The attacker can observe the delay to infer the success of the injection.

### Real-World Example: CVE-2020-14882

One recent example of Blind SQL Injection is CVE-2020-14882, which affected the Joomla CMS. The vulnerability allowed attackers to inject SQL code through the search functionality, leading to unauthorized data access. This demonstrates the importance of proper input validation and sanitization in web applications.

---
<!-- nav -->
[[03-Blind SQL Injection with Time Delays|Blind SQL Injection with Time Delays]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/05-Common Pitfalls and Detection|Common Pitfalls and Detection]]
