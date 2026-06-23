---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection: Union Attack Retrieving Multiple Values in a Single Column

### Introduction to SQL Injection

SQL Injection (SQLi) is a type of security vulnerability that allows an attacker to manipulate SQL queries executed by an application. This manipulation can lead to unauthorized access to sensitive data, data corruption, or even complete control of the database. SQLi occurs when user input is not properly sanitized and is directly incorporated into SQL queries.

### Understanding SQL Injection via UNION Attacks

A UNION attack is a specific type of SQL Injection where the attacker uses the `UNION` operator to combine the results of two or more SELECT statements. This technique is often employed to retrieve data from different tables within the same database.

#### Background Theory

The `UNION` operator is used to combine the result sets of two or more `SELECT` statements. Each `SELECT` statement within the `UNION` must have the same number of columns and compatible data types. The general syntax is:

```sql
SELECT column1, column2, ...
FROM table1
UNION
SELECT column1, column2, ...
FROM table2;
```

In the context of SQL Injection, an attacker might inject a `UNION` query to extract data from other tables in the database. For example, if an application constructs a SQL query based on user input, an attacker could inject a `UNION` query to retrieve additional data.

### Identifying the Number of Columns in a Query

To perform a successful UNION attack, the attacker first needs to determine the number of columns in the original query. This is crucial because the injected `UNION` query must match the number of columns in the original query.

#### Using ORDER BY Clause to Determine Column Count

One method to determine the number of columns is by using the `ORDER BY` clause. The idea is to iteratively order by each column until an internal server error is encountered. An internal server error indicates that the specified column does not exist.

Let's walk through the process step-by-step:

1. **Start with Column 1**:
    - Inject the following payload into the application:
      ```http
      GET /search?input=1' ORDER BY 1 --
      ```
    - If the application returns a valid response without an error, it means that column 1 exists.
    - However, if the column is not displayed on the page, it won't be useful for extracting data.

2. **Check Column 2**:
    - Inject the following payload:
      ```http
      GET /search?input=1' ORDER BY 2 --
      ```
    - If the application returns a valid response and the data is ordered, it means that column 2 exists and is displayed on the page.
    - This column can be used to extract data from other tables.

3. **Check Column 3**:
    - Inject the following payload:
      ```http
      GET /search?input=1' ORDER BY 3 --
      ```
    - If the application returns an internal server error, it means that column 3 does not exist.
    - Therefore, the number of columns in the original query is 2.

### Example of Determining Column Count

Consider the following scenario where an application constructs a SQL query based on user input:

```http
GET /search?input=1
```

The corresponding SQL query might look like this:

```sql
SELECT * FROM users WHERE id = '1';
```

To determine the number of columns, the attacker would inject payloads as follows:

1. **Order by Column 1**:
    ```http
    GET /search?input=1' ORDER BY 1 --
    ```

2. **Order by Column 2**:
    ```http
    GET /search?input=1' ORDER BY 2 --
    ```

3. **Order by Column 3**:
    ```http
    GET /search?input=1' ORDER BY 3 --
    ```

If the third payload results in an internal server error, the number of columns is 2.

### Real-World Examples of SQL Injection Vulnerabilities

Recent real-world examples of SQL Injection vulnerabilities include:

- **CVE-2021-21972**: A SQL Injection vulnerability was found in the WordPress plugin "WP Event Manager". This vulnerability allowed attackers to execute arbitrary SQL commands, potentially leading to data theft or manipulation.
- **CVE-2022-22965**: A SQL Injection vulnerability was discovered in the Joomla! CMS. This vulnerability allowed attackers to inject malicious SQL code, leading to unauthorized access to sensitive data.

### How to Perform a UNION Attack

Once the number of columns is determined, the attacker can craft a `UNION` query to extract data from other tables. The general structure of the `UNION` query is as follows:

```sql
SELECT column1, column2, ...
FROM table1
WHERE condition
UNION
SELECT column1, column2, ...
FROM table2
WHERE condition;
```

For example, if the original query has 2 columns, the attacker might inject the following payload:

```http
GET /search?input=1' UNION SELECT username, password FROM users --
```

This payload combines the results of the original query with the results of the `SELECT` statement from the `users` table.

### Complete Example of UNION Attack

Consider the following scenario where an application constructs a SQL query based on user input:

```http
GET /search?input=1
```

The corresponding SQL query might look like this:

```sql
SELECT id, name FROM products WHERE id = '1';
```

To perform a UNION attack, the attacker would inject the following payload:

```http
GET /search?input=1' UNION SELECT username, password FROM users --
```

This payload combines the results of the original query with the results of the `SELECT` statement from the `users` table.

### How to Prevent / Defend Against SQL Injection

#### Detection

To detect SQL Injection vulnerabilities, organizations can use automated tools such as static application security testing (SAST) and dynamic application security testing (DAST). These tools can identify potential SQL Injection points in the code and during runtime.

#### Prevention

1. **Use Prepared Statements and Parameterized Queries**:
    - Prepared statements ensure that user input is treated as data rather than executable code.
    - Example in Python using SQLite:
      ```python
      import sqlite3

      conn = sqlite3.connect('example.db')
      cursor = conn.cursor()

      user_input = '1'
      cursor.execute("SELECT id, name FROM products WHERE id = ?", (user_input,))
      results = cursor.fetchall()
      ```

2. **Input Validation**:
    - Validate and sanitize user input to ensure it meets expected formats and constraints.
    - Example in PHP:
      ```php
      $user_input = filter_var($_GET['input'], FILTER_VALIDATE_INT);
      if ($user_input !== false) {
          // Proceed with query
      }
      ```

3. **Least Privilege Principle**:
    - Ensure that the database user account used by the application has the minimum necessary privileges.
    - Example in MySQL:
      ```sql
      GRANT SELECT ON database.products TO 'app_user'@'localhost';
      ```

4. **Error Handling**:
    - Avoid exposing detailed error messages to end-users, as they can provide valuable information to attackers.
    - Example in Node.js:
      ```javascript
      app.use((err, req, res, next) => {
          console.error(err.stack);
          res.status(500).send('Something broke!');
      });
      ```

### Secure Coding Practices

#### Vulnerable Code Example

```http
GET /search?input=1' UNION SELECT username, password FROM users --
```

#### Secure Code Example

```python
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

user_input = '1'
cursor.execute("SELECT id, name FROM products WHERE id = ?", (user_input,))
results = cursor.fetchall()
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Hardcoding SQL Queries**:
    - Hardcoding SQL queries without parameterization can lead to SQL Injection vulnerabilities.
2. **Ignoring Input Validation**:
    - Failing to validate and sanitize user input can expose the application to SQL Injection attacks.
3. **Exposing Detailed Error Messages**:
    - Exposing detailed error messages to end-users can provide valuable information to attackers.

#### Best Practices

1. **Use ORM Libraries**:
    - Object-relational mapping (ORM) libraries can help abstract away SQL queries and reduce the risk of SQL Injection.
2. **Regular Security Audits**:
    - Regularly conduct security audits and penetration tests to identify and mitigate SQL Injection vulnerabilities.
3. **Educate Developers**:
    - Educate developers about the risks of SQL Injection and best practices for preventing it.

### Hands-On Labs for Practice

For hands-on practice with SQL Injection and UNION attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice various types of SQL Injection attacks, including UNION attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable to common web application flaws, including SQL Injection.

### Conclusion

SQL Injection remains a significant threat to web applications. By understanding the techniques used by attackers, such as UNION attacks, and implementing robust security measures, organizations can protect their applications from these vulnerabilities. Regular security audits, input validation, and the use of prepared statements are essential steps in preventing SQL Injection attacks.

---
<!-- nav -->
[[02-SQL Injection UNION Attack|SQL Injection UNION Attack]] | [[Web Security (PortSwigger)/02-SQL Injection/07-Lab 6 SQL injection UNION attack retrieving multiple values in a single column/00-Overview|Overview]] | [[04-Understanding SQL Injection and UNION Attacks|Understanding SQL Injection and UNION Attacks]]
