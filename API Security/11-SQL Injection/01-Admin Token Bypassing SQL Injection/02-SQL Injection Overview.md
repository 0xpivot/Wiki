---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## SQL Injection Overview

SQL Injection (SQLi) is a type of injection attack that exploits vulnerabilities in the way an application handles user input to execute arbitrary SQL commands. This can lead to unauthorized access to sensitive data, data manipulation, and even complete system compromise. SQLi attacks are particularly dangerous because they can be executed against a wide variety of databases and applications.

### How SQL Injection Works

At its core, SQL Injection occurs when an attacker is able to inject malicious SQL code into a query that is executed by the database. This typically happens when user input is not properly sanitized or validated before being used in a SQL query.

#### Example of SQL Injection

Consider a simple login form where a user enters their username and password. The application might construct a SQL query like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the user input is not properly sanitized, an attacker could enter something like `username=' OR '1'='1` and `password=' OR '1'='1`. This would result in the following query:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```

Since `'1'='1'` is always true, the query will return all rows from the `users` table, effectively bypassing authentication.

### Real-World Examples

One notable real-world example of SQL Injection is the breach of the popular website MySpace in 2006. Attackers exploited a SQL Injection vulnerability to steal user data, including usernames and passwords. Another example is the 2017 Equifax breach, where attackers exploited a vulnerability in Apache Struts to gain access to sensitive personal information of millions of customers.

### Blind SQL Injection

Blind SQL Injection is a variant of SQL Injection where the attacker does not receive direct feedback from the database. Instead, the attacker must infer the structure of the database and the success of their queries based on the behavior of the application.

#### Example of Blind SQL Injection

In a Blind SQL Injection scenario, an attacker might use time-based techniques to determine if a query was successful. For example, the attacker could inject a query that causes the database to wait for a certain amount of time before responding. If the application takes longer to respond, the attacker knows the query was successful.

```sql
SELECT * FROM users WHERE username = 'admin' AND IF(1=1, SLEEP(5), 0);
```

This query will cause the database to wait for 5 seconds if the condition `1=1` is true. By measuring the response time, the attacker can infer the success of the query.

### SQL Injection Prevention

To prevent SQL Injection, developers should follow these best practices:

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate and sanitize all user input to ensure it conforms to expected formats.
3. **Least Privilege Principle**: Ensure that the database user has the minimum privileges necessary to perform its tasks.
4. **Error Handling**: Avoid exposing detailed error messages to users, as they can provide valuable information to attackers.

#### Secure Code Example

Here is an example of using prepared statements in Python with the `sqlite3` library:

```python
import sqlite3

# Connect to the database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Prepare the statement
query = "SELECT * FROM users WHERE username = ? AND password = ?"
params = ('admin', 'password')

# Execute the query
cursor.execute(query, params)
results = cursor.fetchall()

# Close the connection
conn.close()
```

### SQL Injection Detection

Detecting SQL Injection vulnerabilities can be challenging, but there are several tools and techniques available:

1. **Static Analysis Tools**: Tools like SonarQube and Fortify can analyze code for potential SQL Injection vulnerabilities.
2. **Dynamic Analysis Tools**: Tools like Burp Suite and OWASP ZAP can simulate SQL Injection attacks and detect vulnerabilities in live applications.
3. **Database Auditing**: Regularly auditing database logs can help identify suspicious activity that may indicate a SQL Injection attack.

### Lab Exercises

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover various types of SQL Injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application that includes SQL Injection vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that intentionally contains numerous security vulnerabilities, including SQL Injection.

### Conclusion

SQL Injection remains a significant threat to web applications. Understanding how it works, recognizing its variants, and implementing robust preventive measures are crucial steps in securing applications against this type of attack. By following best practices and using appropriate tools, developers can significantly reduce the risk of SQL Injection vulnerabilities.

---
<!-- nav -->
[[API Security/11-SQL Injection/01-Admin Token Bypassing SQL Injection/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[API Security/11-SQL Injection/01-Admin Token Bypassing SQL Injection/00-Overview|Overview]] | [[03-Understanding SQL Injection in API Endpoints|Understanding SQL Injection in API Endpoints]]
