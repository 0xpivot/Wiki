---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Blind SQL Injection with Conditional Errors

Blind SQL Injection is a type of SQL Injection where the attacker cannot see the results of the injected SQL query directly. Instead, the attacker must infer the structure of the database by observing the behavior of the application.

### What is Blind SQL Injection?

Blind SQL Injection occurs when the application does not return the results of the SQL query directly. Instead, the attacker must use indirect methods to determine the success or failure of the injected SQL query. There are two main types of Blind SQL Injection:

- **Blind SQL Injection with Conditional Responses**: The attacker observes changes in the application's behavior based on the success or failure of the injected SQL query.
- **Blind SQL Injection with Conditional Errors**: The attacker triggers error messages that provide information about the success or failure of the injected SQL query.

### Conditional Errors in SQL Injection

Conditional errors occur when the injected SQL query causes the database to generate an error message. These error messages can provide valuable information to the attacker, such as the structure of the database or the presence of certain data.

#### Example Scenario

Consider a web application that uses a tracking cookie for analytics. The application performs a SQL query containing the value of the submitted cookie. The results of the SQL query are not returned, and the application does not respond any differently based on whether the query returns any rows.

The vulnerable parameter is the tracking cookie. Because the results of the SQL query are not returned, we cannot use Union-based SQL injection. Additionally, because the application does not respond any differently based on whether the query returns any rows, we cannot use blind-based SQL injection based on conditional responses.

### Exploiting Blind SQL Injection with Conditional Errors

To exploit Blind SQL Injection with conditional errors, the attacker must trigger error messages that provide information about the success or failure of the injected SQL query. This can be done by injecting SQL queries that cause the database to generate error messages.

#### Step-by-Step Exploitation

1. **Identify the Vulnerable Parameter**: Identify the parameter that is vulnerable to SQL Injection. In this case, it is the tracking cookie.
2. **Inject Malicious SQL Queries**: Inject SQL queries that cause the database to generate error messages. For example, you can inject a query that attempts to divide by zero, which will cause an error.

Here is an example of how to inject a malicious SQL query:

```http
GET /page?trackingCookie=1' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 1 END)='1 HTTP/1.1
Host: vulnerable-app.com
Cookie: trackingCookie=1' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 1 END)='1
```

This query will cause the database to generate an error if the condition `(1=1)` is true. By observing whether the application returns an error message, the attacker can infer the success or failure of the injected SQL query.

### Detection and Prevention

#### How to Detect SQL Injection Vulnerabilities

To detect SQL Injection vulnerabilities, you can use automated tools such as SQLMap, Burp Suite, or OWASP ZAP. These tools can automatically test for SQL Injection vulnerabilities and provide detailed reports.

Additionally, you can manually test for SQL Injection vulnerabilities by injecting various SQL payloads into the vulnerable parameters and observing the behavior of the application.

#### How to Prevent SQL Injection

To prevent SQL Injection, follow these best practices:

1. **Use Prepared Statements and Parameterized Queries**: Prepared statements and parameterized queries ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate all user input to ensure that it conforms to expected formats and ranges.
3. **Least Privilege Principle**: Ensure that the database user has the least privilege necessary to perform its tasks.
4. **Error Handling**: Implement proper error handling to prevent error messages from revealing sensitive information about the database structure.

#### Secure Coding Practices

Here is an example of how to securely handle user input using prepared statements in Python:

```python
import sqlite3

# Connect to the database
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Prepare the SQL statement
query = "SELECT * FROM users WHERE username = ? AND password = ?"

# Execute the query with user input
username = 'user'
password = 'pass'
cursor.execute(query, (username, password))

# Fetch the results
results = cursor.fetchall()
print(results)

# Close the connection
conn.close()
```

In this example, the user input is passed as a parameter to the `execute` method, ensuring that it is treated as data rather than executable code.

### Real-World Examples

#### CVE-2019-14287: WP Event Booking Plugin

A SQL Injection vulnerability was found in the WordPress plugin "WP Event Booking". This allowed attackers to execute arbitrary SQL commands, potentially leading to data theft or manipulation.

#### CVE-2020-1938: Joomla! CMS

A SQL Injection vulnerability was discovered in the Joomla! CMS. This vulnerability allowed attackers to inject malicious SQL code, leading to unauthorized access to sensitive data.

### Conclusion

Blind SQL Injection with conditional errors is a powerful technique that allows attackers to infer the structure of a database by observing the behavior of the application. To prevent SQL Injection, it is essential to use prepared statements and parameterized queries, validate all user input, implement the least privilege principle, and handle errors properly.

By following these best practices and using secure coding techniques, you can significantly reduce the risk of SQL Injection attacks and protect your web applications from unauthorized access and data theft.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of SQL Injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several SQL Injection vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable to common web application attacks, including SQL Injection.

These labs provide a safe environment to practice and learn about SQL Injection attacks and how to defend against them.

---

This chapter provides a comprehensive overview of SQL Injection, focusing on Blind SQL Injection with conditional errors. It covers the theory, practical examples, and secure coding practices to help you understand and prevent SQL Injection attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/13-Lab 12 Blind SQL injection with conditional errors/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/13-Lab 12 Blind SQL injection with conditional errors/00-Overview|Overview]] | [[03-Real-World Examples|Real-World Examples]]
