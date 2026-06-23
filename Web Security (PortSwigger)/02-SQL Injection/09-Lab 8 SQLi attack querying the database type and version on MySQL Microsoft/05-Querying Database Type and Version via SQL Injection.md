---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Querying Database Type and Version via SQL Injection

In this section, we will delve into the specifics of how an attacker can use SQL Injection to query the type and version of a database. This knowledge is crucial for both attackers and defenders to understand the full scope of what can be achieved through SQL Injection.

### Background Theory

#### Why Query Database Type and Version?

Knowing the type and version of a database can provide valuable information to an attacker. Different database systems have different features, vulnerabilities, and configurations. By identifying the database type and version, an attacker can tailor their attacks more effectively.

#### Common Database Types

- **MySQL**: Open-source relational database management system.
- **Microsoft SQL Server**: Relational database management system developed by Microsoft.
- **PostgreSQL**: Object-relational database management system.

### Example Scenario

Consider a web application that uses a vulnerable input field to query a database. An attacker can inject SQL code to retrieve the database type and version.

#### Vulnerable Code Example

```python
import mysql.connector

def query_data(user_input):
    conn = mysql.connector.connect(host="localhost", user="root", password="password", database="testdb")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_input}"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result
```

In this example, the `user_input` variable is directly concatenated into the SQL query string. An attacker could inject SQL code to retrieve the database version.

#### Injected SQL Code

An attacker might enter something like `1 UNION SELECT @@version, NULL`.

This would result in the following query:

```sql
SELECT * FROM users WHERE id = 1 UNION SELECT @@version, NULL
```

The `@@version` variable retrieves the version of the MySQL server.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2022-24718**: A SQL Injection vulnerability was found in the WordPress plugin WP Job Manager. Attackers could exploit this vulnerability to retrieve sensitive information, including the database version.

- **SolarWinds Data Breach (2020)**: Although not directly related to SQL Injection, the SolarWinds breach involved the compromise of a software update server, which could have been exploited to inject malicious SQL code.

### Prevention and Defense

#### Secure Coding Practices

To prevent SQL Injection, developers should follow secure coding practices such as:

1. **Use Prepared Statements**: Prepared statements separate the SQL logic from the data, ensuring that user inputs are treated as data rather than executable code.

2. **Input Validation**: Validate and sanitize all user inputs to ensure they conform to expected formats and lengths.

3. **Least Privilege Principle**: Ensure that database connections are made with the least privilege necessary to perform required tasks.

#### Example of Secure Code

Here’s how the previous vulnerable code can be rewritten using prepared statements:

```python
import mysql.connector

def query_data_secure(user_input):
    conn = mysql.connector.connect(host="localhost", user="user", password="password", database="testdb")
    cursor = conn.cursor(prepared=True)
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_input,))
    result = cursor.fetchall()
    conn.close()
    return result
```

In this secure version, the `execute` method uses placeholders (`%s`) for the inputs, which are then safely substituted by the `cursor.execute` method.

### Detecting SQL Injection

#### Tools and Techniques

- **Static Application Security Testing (SAST)**: Tools like SonarQube and Fortify can analyze source code to identify potential SQL Injection vulnerabilities.
  
- **Dynamic Application Security Testing (DAST)**: Tools like Burp Suite and OWASP ZAP can simulate attacks to detect runtime vulnerabilities.

### Hands-On Practice

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting SQL Injection vulnerabilities.
  
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques, including SQL Injection.

### Conclusion

Understanding how to query the type and version of a database via SQL Injection is crucial for both attackers and defenders. By following secure coding practices and using appropriate tools for detection and prevention, developers can significantly reduce the risk of SQL Injection attacks. Always validate and sanitize user inputs, and use prepared statements to ensure that SQL queries are executed safely.

---

---
<!-- nav -->
[[04-Identifying Vulnerable Queries|Identifying Vulnerable Queries]] | [[Web Security (PortSwigger)/02-SQL Injection/09-Lab 8 SQLi attack querying the database type and version on MySQL Microsoft/00-Overview|Overview]] | [[06-Scripting SQL Injection to Query Database Type and Version|Scripting SQL Injection to Query Database Type and Version]]
