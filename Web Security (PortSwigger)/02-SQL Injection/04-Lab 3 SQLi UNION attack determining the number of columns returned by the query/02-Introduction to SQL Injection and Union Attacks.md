---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection and Union Attacks

SQL Injection (SQLi) is a type of cyberattack where an attacker manipulates a website's database queries to gain unauthorized access to sensitive information or execute malicious actions. One of the most common forms of SQLi is the **Union Attack**, which allows attackers to combine the results of two or more SELECT statements into a single result set. This can be used to extract data from other tables in the database, even if those tables are not directly accessible through the original query.

### What is SQL Injection?

SQL Injection occurs when an attacker injects malicious SQL code into input fields or parameters that are not properly sanitized. This can lead to unauthorized access to sensitive data, manipulation of data, or even complete control over the database.

#### Why Does SQL Injection Matter?

SQL Injection is a critical vulnerability because it can lead to significant data breaches. For example, in 2017, a SQL Injection attack was used to steal data from the Equifax credit reporting agency, affecting over 143 million people. This breach resulted in financial losses and reputational damage for Equifax.

### How Does SQL Injection Work?

To understand SQL Injection, let's consider a simple example. Suppose a web application has a search feature that allows users to search for products based on a category. The SQL query might look something like this:

```sql
SELECT * FROM products WHERE category = 'Electronics';
```

If the category parameter is not properly sanitized, an attacker could inject malicious SQL code. For instance, if the attacker inputs `Electronics' OR '1'='1`, the query becomes:

```sql
SELECT * FROM products WHERE category = 'Electronics' OR '1'='1';
```

This query will return all rows from the `products` table because the condition `'1'='1'` is always true.

### Union Attacks

A Union Attack is a specific type of SQL Injection where the attacker uses the `UNION` operator to combine the results of two or more SELECT statements. This can be used to extract data from other tables in the database.

#### Example of a Union Attack

Consider the following SQL query:

```sql
SELECT product_name, price FROM products WHERE category = 'Electronics';
```

An attacker could inject a `UNION` statement to retrieve data from another table, such as a `users` table:

```sql
SELECT product_name, price FROM products WHERE category = 'Electronics' UNION SELECT username, password FROM users;
```

This would return a result set that combines the product names and prices with the usernames and passwords from the `users` table.

### Determining the Number of Columns

Before performing a Union Attack, it is crucial to determine the number of columns returned by the original query. This ensures that the injected query matches the structure of the original query and does not cause a syntax error.

#### Steps to Determine the Number of Columns

1. **Identify the Vulnerable Parameter**: Find a parameter in the application that is vulnerable to SQL Injection.
2. **Inject Malformed SQL**: Inject a malformed SQL statement to cause an error and observe the number of columns in the error message.
3. **Use ORDER BY Clause**: Use the `ORDER BY` clause to determine the number of columns.

Let's go through these steps in detail.

### Identifying the Vulnerable Parameter

In our example, the `category` parameter is vulnerable to SQL Injection. We can test this by injecting a single quote (`'`) into the parameter:

```
http://example.com/products?category=Electronics'
```

This should cause a SQL syntax error, indicating that the parameter is vulnerable.

### Injecting Malformed SQL

Next, we can inject a malformed SQL statement to cause an error and observe the number of columns in the error message. For example, we can inject a single quote:

```
http://example.com/products?category=Electronics' AND '1'='1
```

This should cause an error message similar to:

```
Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''Electronics' AND '1'='1'' at line 1
```

By examining the error message, we can infer the number of columns in the result set.

### Using ORDER BY Clause

Another method to determine the number of columns is to use the `ORDER BY` clause. We can inject a `ORDER BY` statement with increasing column numbers until we get a syntax error.

For example, we can start with:

```
http://example.com/products?category=Electronics' ORDER BY 1--
```

If this does not cause an error, we can increment the column number:

```
http://example.com/products?category=Electronics' ORDER BY 2--
```

We continue this process until we get a syntax error, indicating that we have exceeded the number of columns in the result set.

### Example of Determining the Number of Columns

Let's assume we are testing the `category` parameter and we want to determine the number of columns in the result set.

1. **Inject Single Quote**:
    ```
    http://example.com/products?category=Electronics'
    ```

    This should cause a syntax error.

2. **Use ORDER BY Clause**:
    ```
    http://example.com/products?category=Electronics' ORDER BY 1--
    ```

    If this does not cause an error, we can try:

    ```
    http://example.com/products?category=Electronics' ORDER BY 2--
    ```

    We continue this process until we get a syntax error.

### Real-World Example: CVE-2019-11510

CVE-2019-11510 is a SQL Injection vulnerability in the WordPress plugin WP Event Manager. An attacker could exploit this vulnerability to inject malicious SQL code and potentially retrieve sensitive data from the database.

#### Exploitation Steps

1. **Identify Vulnerable Parameter**: The `event_id` parameter in the `wp-event-manager` plugin is vulnerable.
2. **Inject Malformed SQL**: Inject a single quote to cause a syntax error.
3. **Determine Number of Columns**: Use the `ORDER BY` clause to determine the number of columns.

### How to Prevent / Defend Against SQL Injection

#### Detection

To detect SQL Injection vulnerabilities, you can use automated tools such as:

- **SQLMap**: A powerful tool for detecting and exploiting SQL Injection vulnerabilities.
- **Burp Suite**: A comprehensive toolkit for web application security testing.

#### Prevention

To prevent SQL Injection attacks, follow these best practices:

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate and sanitize all user input to ensure it meets expected formats and constraints.
3. **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks.
4. **Web Application Firewalls (WAF)**: Use WAFs to detect and block suspicious SQL queries.

#### Secure Coding Fixes

Here is an example of a vulnerable SQL query and its secure counterpart using prepared statements:

**Vulnerable Code**:
```php
$category = $_GET['category'];
$query = "SELECT * FROM products WHERE category = '$category'";
$result = mysqli_query($conn, $query);
```

**Secure Code**:
```php
$category = $_GET['category'];
$stmt = $conn->prepare("SELECT * FROM products WHERE category = ?");
$stmt->bind_param("s", $category);
$stmt->execute();
$result = $stmt->get_result();
```

### Conclusion

Determining the number of columns returned by a query is a crucial step in performing a Union Attack. By identifying the vulnerable parameter, injecting malformed SQL, and using the `ORDER BY` clause, we can determine the number of columns and proceed with the attack. However, it is essential to implement proper defenses to prevent SQL Injection attacks and protect sensitive data.

### Practice Labs

For hands-on practice with SQL Injection and Union Attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on SQL Injection and Union Attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

These labs provide a safe environment to practice and understand the concepts of SQL Injection and Union Attacks in depth.

---
<!-- nav -->
[[01-Introduction to SQL Injection and UNION Attacks|Introduction to SQL Injection and UNION Attacks]] | [[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/03-Introduction to SQL Injection|Introduction to SQL Injection]]
