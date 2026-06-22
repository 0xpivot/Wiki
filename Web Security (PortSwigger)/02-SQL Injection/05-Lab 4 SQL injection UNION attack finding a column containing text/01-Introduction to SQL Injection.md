---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a common web application security vulnerability that allows an attacker to manipulate database queries by injecting malicious SQL code through user input fields. This can lead to unauthorized access to sensitive data, data manipulation, or even complete control over the database server. Understanding and preventing SQL Injection is crucial for securing web applications.

### What is SQL Injection?

SQL Injection occurs when an attacker manipulates a web application's input fields to inject SQL code into the application's backend database. This can happen when the application constructs SQL queries using unvalidated or unsanitized user input. The injected SQL code can alter the intended behavior of the query, leading to unintended actions such as retrieving sensitive data or executing arbitrary commands.

### Why Does SQL Injection Matter?

SQL Injection is significant because it can compromise the integrity and confidentiality of a web application's data. An attacker can use SQL Injection to:

- Retrieve sensitive information such as passwords, credit card details, and personal data.
- Modify or delete data within the database.
- Gain administrative privileges over the database server.
- Execute arbitrary commands on the server.

### How Does SQL Injection Work?

To understand SQL Injection, let's consider a simple example. Suppose a web application has a login form that takes a username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the application does not properly sanitize the user input, an attacker could inject SQL code into the `username` field. For instance, if the attacker inputs `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'input_password';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true. Thus, the attacker bypasses authentication.

### Real-World Examples of SQL Injection

SQL Injection attacks have been responsible for numerous high-profile breaches. Here are a few recent examples:

- **CVE-2021-21972**: A SQL Injection vulnerability was found in the WordPress plugin WP Travel Engine. This allowed attackers to execute arbitrary SQL commands, potentially leading to data theft or manipulation.
- **CVE-2020-14882**: A SQL Injection vulnerability in the Joomla! CMS allowed attackers to execute arbitrary SQL commands, leading to unauthorized access to sensitive data.

### Lab Setup

For this lab, we will be using the Web Security Academy provided by PortSwigger. You can access the exercises by visiting [PortSwigger Web Security Academy](https://portswigger.net/web-security/sql-injection/lab-union-find-column-containing-text).

### Step-by-Step Guide to the Lab

#### Step 1: Access the Lab

1. Log in to your PortSwigger Web Security Academy account.
2. Navigate to the Academy section.
3. Select the learning path for SQL Injection.
4. Choose the lab titled "SQL Injection UNION Attack, finding a column containing text."

#### Step 2: Understanding the Union Operator

The `UNION` operator in SQL is used to combine the result sets of two or more `SELECT` statements. Each `SELECT` statement within the `UNION` must have the same number of columns and compatible data types.

For example, consider the following SQL query:

```sql
SELECT column1, column2 FROM table1
UNION
SELECT column1, column2 FROM table2;
```

This query combines the results of two `SELECT` statements, ensuring that both have the same number of columns and compatible data types.

### Step 3: Identifying Columns Containing Text

In this lab, we will use a union-based SQL injection to identify columns that contain text. This is step two in the union-based SQL injection attack.

#### Theory Behind the Attack

To identify columns containing text, we can inject a `UNION` query that returns a known string in each column. By observing which columns display the known string, we can determine which columns contain text.

For example, consider the following vulnerable query:

```sql
SELECT id, name FROM products WHERE id = 'input_id';
```

We can inject a `UNION` query to test each column:

```sql
SELECT id, name FROM products WHERE id = '1' UNION SELECT 'text', 'text';
```

This query will return two rows: one from the original query and one from the injected `UNION` query. By examining the output, we can determine which columns contain text.

### Step 4: Injecting the Query

Let's walk through the process of injecting the query and identifying columns containing text.

1. Open the lab in a new tab.
2. Identify the input field where the SQL injection can be performed.
3. Inject the `UNION` query to test each column.

For example, if the input field is a search box, you might inject the following:

```
1' UNION SELECT 'text', 'text'--
```

This will modify the query to:

```sql
SELECT id, name FROM products WHERE id = '1' UNION SELECT 'text', 'text';
```

### Step 5: Analyzing the Output

After injecting the query, observe the output to determine which columns contain text. For example, if the output shows:

```
id | name
---|------
1  | Product 1
text | text
```

This indicates that both columns contain text.

### Step 6: Automating the Process

To automate the process of identifying columns containing text, you can use tools like Burp Suite or SQLMap. These tools can automatically inject payloads and analyze the output to identify columns containing text.

### How to Prevent / Defend Against SQL Injection

Preventing SQL Injection requires a combination of secure coding practices, input validation, and proper use of parameterized queries.

#### Secure Coding Practices

1. **Use Parameterized Queries**: Instead of constructing SQL queries using string concatenation, use parameterized queries. This ensures that user input is treated as data rather than executable code.

   Example of a parameterized query in Python:

   ```python
   import sqlite3

   conn = sqlite3.connect('example.db')
   cursor = conn.cursor()

   user_input = '1'
   cursor.execute("SELECT id, name FROM products WHERE id = ?", (user_input,))
   ```

2. **Input Validation**: Validate all user input to ensure it meets expected formats and constraints. Use regular expressions or built-in validation functions to check input.

   Example of input validation in Python:

   ```python
   import re

   user_input = '1'
   if re.match(r'^\d+$', user_input):
       # Proceed with query
   else:
       raise ValueError("Invalid input")
   ```

#### Detection and Prevention Tools

1. **Web Application Firewalls (WAF)**: WAFs can detect and block SQL Injection attempts by analyzing incoming traffic for patterns indicative of SQL Injection attacks.

2. **Static Code Analysis Tools**: Tools like SonarQube, Fortify, and Veracode can scan source code for potential SQL Injection vulnerabilities and provide recommendations for fixing them.

3. **Dynamic Analysis Tools**: Tools like Burp Suite and SQLMap can simulate SQL Injection attacks and help identify vulnerable parts of the application.

### Conclusion

SQL Injection is a serious threat to web applications, but it can be effectively prevented through secure coding practices, input validation, and the use of parameterized queries. By understanding the mechanics of SQL Injection and implementing robust defenses, developers can protect their applications from these attacks.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering different aspects of SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.

By completing these labs, you can gain practical experience in identifying and preventing SQL Injection vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/02-SQL Injection Overview|SQL Injection Overview]]
