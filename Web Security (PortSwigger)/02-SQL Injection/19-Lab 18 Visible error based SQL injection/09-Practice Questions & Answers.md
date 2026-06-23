---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the purpose of the tracking ID cookie in the lab?**

The tracking ID cookie is used by the application for analytics purposes. It is a custom cookie that interacts with the backend database, making it a potential target for SQL injection attacks. By manipulating the value of this cookie, an attacker can inject malicious SQL code into the database queries.

**Q2. How does the SQL injection vulnerability manifest in the lab?**

The SQL injection vulnerability manifests when the application fails to properly sanitize the input from the tracking ID cookie. By injecting a single quote (`'`) into the cookie value, the attacker can cause the SQL query to break, resulting in an error message that reveals details about the underlying SQL query structure. This error message can provide insights into the database schema and allow further exploitation.

**Q3. Explain the process of leaking the administrator's password using SQL injection in this lab.**

To leak the administrator's password, the following steps are taken:

1. Identify the vulnerable parameter (tracking ID cookie).
2. Inject a single quote (`'`) to trigger an error and confirm the presence of SQL injection.
3. Use the `CAST` function to manipulate the SQL query and force errors that reveal information.
4. Construct a query to extract the `username` and `password` fields from the `users` table.
5. Limit the query to return only one result to avoid exceeding character limits.
6. Extract the password for the administrator user and use it to log in.

For example, the payload to extract the password might look like this:
```sql
' UNION SELECT password FROM users LIMIT 1 --
```

**Q4. Why is the error message considered "verbose" in this context?**

The error message is considered "verbose" because it provides detailed information about the SQL query that caused the error. This includes the exact SQL command being executed, which can reveal the structure of the database tables and the nature of the query. Such detailed error messages are extremely helpful for attackers as they provide clear insights into the database schema and can guide further exploitation efforts.

**Q5. How can you prevent SQL injection vulnerabilities like the one demonstrated in this lab?**

To prevent SQL injection vulnerabilities, developers should follow these best practices:

1. **Use Prepared Statements:** Prepared statements ensure that user inputs are treated as data rather than executable code.
2. **Input Validation:** Validate and sanitize all user inputs to ensure they conform to expected formats and lengths.
3. **Error Handling:** Avoid displaying detailed error messages to users. Instead, log errors securely and provide generic error messages to the user.
4. **Least Privilege Principle:** Ensure that the database user has the minimum privileges required to perform its tasks.
5. **Regular Audits:** Regularly audit and test applications for SQL injection vulnerabilities using both manual and automated tools.

**Q6. Reference a recent real-world example of SQL injection and explain how it relates to the lab exercise.**

A notable recent example of SQL injection is the breach of the Capital One data in 2019, where an attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive customer data. The attacker used SQL injection to bypass authentication mechanisms and extract data from the database.

In relation to the lab exercise, the Capital One breach demonstrates the critical importance of proper input validation and error handling. Just as the lab exercise showed how a simple tracking cookie could be exploited to leak sensitive information, the Capital One breach highlights the real-world consequences of such vulnerabilities. Both scenarios underscore the necessity of robust security measures to prevent SQL injection attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/08-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/00-Overview|Overview]]
