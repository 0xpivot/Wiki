---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Understanding SQL Injection and UNION Attacks

### Introduction to SQL Injection

SQL Injection (SQLi) is a type of attack where an attacker manipulates a website's database queries to execute unauthorized commands. This can lead to unauthorized access to sensitive data, data corruption, or even complete system compromise. SQL Injection attacks typically occur due to poor input validation and sanitization practices.

### UNION-Based SQL Injection

One common form of SQL Injection is the **UNION-based SQL Injection**. This technique exploits the `UNION` operator in SQL, which is used to combine the result sets of two or more `SELECT` statements. By injecting malicious SQL code into a vulnerable query, an attacker can manipulate the output of the original query.

#### Example Scenario

Consider a simple login form where the backend SQL query looks like this:

```sql
SELECT username, password FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the input fields are not properly sanitized, an attacker might inject a `UNION` statement to retrieve additional information from the database.

### Rules of the UNION Operator

The `UNION` operator combines the results of two or more `SELECT` statements into a single result set. However, for the `UNION` to work correctly, the following rules must be satisfied:

1. **Number of Columns**: The number of columns selected in each `SELECT` statement must be the same.
2. **Data Types**: The data types of the corresponding columns in the `SELECT` statements must be compatible.

#### Example Query

Let's consider a query that selects four columns from a table:

```sql
SELECT columnA, columnB, columnC, columnD FROM some_table;
```

To successfully use the `UNION` operator, the injected query must also select four columns with compatible data types.

### Black Box Perspective

In a **black box** scenario, the attacker does not have prior knowledge of the structure of the database or the specific SQL queries being executed. Therefore, the attacker must determine the number of columns and their data types through trial and error.

#### Step-by-Step Process

1. **Determine the Number of Columns**:
    - Add `UNION SELECT NULL` to the original query and observe the response.
    - If the response is successful (HTTP 200), incrementally add more `NULL` values until an error occurs.
    - The number of `NULL` values that produce a successful response indicates the number of columns in the original query.

2. **Determine Data Types**:
    - Once the number of columns is known, the attacker can start guessing the data types.
    - Common data types include `INTEGER`, `VARCHAR`, `TEXT`, etc.
    - The attacker can test different data types by replacing `NULL` with values of different types.

### Example Attack Scenario

Let's assume an attacker is trying to exploit a vulnerable login form. The original query might look like this:

```sql
SELECT username, password FROM users WHERE username = 'input_username' AND password = 'input_password';
```

The attacker injects a `UNION` statement to determine the number of columns:

```sql
SELECT username, password FROM users WHERE username = 'input_username' AND password = 'input_password' UNION SELECT NULL, NULL;
```

If this query returns a successful response, the attacker knows that the original query has two columns. They can then try to determine the data types by injecting different values:

```sql
SELECT username, password FROM users WHERE username = 'input_username' AND password = 'input_password' UNION SELECT 1, 'test';
```

If this query returns an error, the data types are likely not compatible. The attacker continues to guess until they find the correct combination.

### Real-World Examples

#### CVE-2021-21972

This CVE describes a SQL Injection vulnerability in a popular CMS platform. An attacker could inject malicious SQL code into the search functionality, leading to unauthorized access to sensitive data.

#### Example Exploit

Consider a search functionality that constructs a query like this:

```sql
SELECT * FROM articles WHERE title LIKE '%input_search%';
```

An attacker could inject a `UNION` statement to retrieve additional information:

```sql
SELECT * FROM articles WHERE title LIKE '%input_search%' UNION SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10;
```

By carefully crafting the injected query, the attacker can bypass input validation and retrieve sensitive data.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Input Validation and Sanitization**:
    - Always validate and sanitize user inputs to ensure they do not contain malicious SQL code.
    - Use parameterized queries or prepared statements to prevent SQL Injection.

2. **Least Privilege Principle**:
    - Ensure that the application runs with the least privileges necessary to perform its tasks.
    - Limit the permissions of the database user to only the required operations.

#### Example Secure Code

Here is an example of a secure login function using parameterized queries:

```python
import sqlite3

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Parameterized query to prevent SQL Injection
    cursor.execute("SELECT username, password FROM users WHERE username = ? AND password = ?", (username, password))
    
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False
```

#### Detection and Monitoring

1. **Web Application Firewalls (WAF)**:
    - Implement WAFs to detect and block SQL Injection attempts.
    - Regularly update WAF rules to protect against new vulnerabilities.

2. **Logging and Monitoring**:
    - Enable detailed logging of database queries and monitor for suspicious activity.
    - Use intrusion detection systems (IDS) to identify potential SQL Injection attacks.

#### Example Secure Configuration

Here is an example of a secure configuration for a WAF:

```json
{
  "rules": [
    {
      "name": "SQL Injection",
      "description": "Detects SQL Injection attempts",
      "pattern": ".*\\b(SELECT|UPDATE|DELETE|INSERT|DROP)\\b.*",
      "action": "block"
    }
  ]
}
```

### Conclusion

Understanding and preventing SQL Injection attacks is crucial for maintaining the security of web applications. By adhering to secure coding practices, implementing proper input validation, and using tools like WAFs, developers can significantly reduce the risk of SQL Injection vulnerabilities.

### Practice Labs

For hands-on practice with SQL Injection attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on SQL Injection and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security attacks.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of vulnerable web applications for learning and testing security measures.

These labs provide real-world scenarios and practical experience in identifying and mitigating SQL Injection vulnerabilities.

---
<!-- nav -->
[[05-SQL Injection UNION Attack|SQL Injection UNION Attack]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/07-Practice Questions & Answers|Practice Questions & Answers]]
