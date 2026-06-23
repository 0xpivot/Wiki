---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what SQL injection is and how it can occur in API endpoints.**

SQL injection is a type of security vulnerability that allows an attacker to insert malicious SQL statements into an application's input fields, which are then executed by the backend database. In the context of API endpoints, SQL injection can occur when user inputs are not properly sanitized or validated before being used in SQL queries. For example, if an API endpoint accepts a user ID as a parameter and uses it directly in a SQL query without proper validation, an attacker could inject a crafted input that alters the intended SQL query, potentially leading to unauthorized access or data manipulation.

**Q2. How can you detect SQL injection vulnerabilities in an API endpoint using tools like SQLMap?**

To detect SQL injection vulnerabilities in an API endpoint using SQLMap, you can follow these steps:

1. Capture the HTTP request to the API endpoint using a tool like Burp Suite or similar.
2. Save the captured request to a file, e.g., `request.txt`.
3. Use SQLMap to analyze the request and check for SQL injection vulnerabilities. The basic command structure is:

```bash
sqlmap -r request.txt --batch --level=5 --risk=3
```

This command tells SQLMap to read the request from `request.txt`, run in batch mode, and set the detection level and risk to high to ensure comprehensive analysis.

**Q3. Describe how to exploit a SQL injection vulnerability in an API endpoint using a UNION-based attack.**

A UNION-based SQL injection attack involves combining the results of two or more SELECT statements to manipulate the output of the original query. Here’s how you might exploit such a vulnerability:

1. Identify the number of columns in the original query. This can often be done by incrementally increasing the number of columns until the query returns successfully.
   
   ```sql
   ' UNION SELECT 1,2,3,4,5,6 -- 
   ```

2. Once the number of columns is known, craft a UNION query to retrieve additional data. For example, to extract the names of tables in the database:

   ```sql
   ' UNION SELECT table_name, NULL, NULL, NULL, NULL, NULL FROM information_schema.tables --
   ```

3. Send the crafted payload to the vulnerable API endpoint and observe the response to confirm successful exploitation.

**Q4. What are some common defenses against SQL injection attacks in API endpoints?**

Common defenses against SQL injection attacks include:

1. **Parameterized Queries**: Use prepared statements or parameterized queries to ensure that user inputs are treated as data rather than executable code.
   
   Example in Python using SQLite:
   
   ```python
   cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
   ```

2. **Input Validation**: Validate and sanitize all user inputs to ensure they conform to expected formats and ranges.
   
3. **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks, reducing the potential impact of a successful SQL injection attack.
   
4. **Web Application Firewalls (WAF)**: Deploy WAFs to filter out malicious SQL injection attempts before they reach the application.

**Q5. Discuss recent real-world examples of SQL injection attacks and their impacts.**

One notable recent example is the SQL injection attack on the Capital One breach in 2019. An attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive customer data. The breach affected over 100 million customers, leading to significant financial and reputational damage for Capital One.

Another example is the SQL injection attack on the Equifax breach in 2017, where attackers exploited a vulnerability in Apache Struts to steal personal information of approximately 143 million consumers. These breaches highlight the critical importance of securing applications against SQL injection and other vulnerabilities.

---
<!-- nav -->
[[API Security/11-SQL Injection/04-SQL Injection/05-Conclusion|Conclusion]] | [[API Security/11-SQL Injection/04-SQL Injection/00-Overview|Overview]]
