---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Overview

SQL Injection is a common web application security vulnerability that occurs when an attacker can inject malicious SQL code into a query executed by the application. This can lead to unauthorized access to sensitive data, manipulation of data, or even complete compromise of the database system. SQL Injection attacks are particularly dangerous because they can be used to bypass authentication mechanisms and gain administrative privileges.

### How SQL Injection Works

When a user inputs data into a web form, such as a login form, the application typically constructs an SQL query using the input data. If the input data is not properly sanitized or validated, an attacker can inject SQL code that will alter the intended behavior of the query. For example, consider the following SQL query:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If an attacker inputs `input_username` as `' OR '1'='1` and `input_password` as `anything`, the resulting SQL query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'anything';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true. Thus, the attacker can bypass authentication without knowing the actual username and password.

### Real-World Examples

One of the most notable real-world examples of SQL Injection is the breach of the popular website Adobe in 2013. Attackers exploited a SQL Injection vulnerability to steal over 150 million user records, including usernames, passwords, and credit card information. This breach highlights the severe consequences of not properly securing web applications against SQL Injection attacks.

Another example is the breach of the Equifax credit reporting agency in 2017, which was caused by a vulnerability in Apache Struts, leading to the exposure of sensitive personal information of approximately 143 million consumers.

### Prevention and Detection

To prevent SQL Injection attacks, developers should follow these best practices:

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code. This can be achieved using parameterized queries.

2. **Input Validation**: Validate all user inputs to ensure they conform to expected formats and ranges.

3. **Least Privilege Principle**: Ensure that the database user account used by the application has the minimum necessary permissions to perform its tasks.

4. **Security Testing**: Regularly test applications for SQL Injection vulnerabilities using tools like Burp Suite, SQLMap, and OWASP ZAP.

### Secure Coding Practices

Here is an example of a vulnerable and a secure version of a login function in Python:

#### Vulnerable Code

```python
import sqlite3

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
```

#### Secure Code

```python
import sqlite3

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result
```

In the secure version, the query uses placeholders (`?`) and the `execute` method takes a tuple of parameters, ensuring that user input is treated as data rather than executable code.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/08-Lab 7 SQL injection attack querying the database type and version on Oracle/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/08-Lab 7 SQL injection attack querying the database type and version on Oracle/00-Overview|Overview]] | [[03-Implementing SQL Injection Exploits|Implementing SQL Injection Exploits]]
