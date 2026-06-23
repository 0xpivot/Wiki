---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection UNION Attack

A UNION-based SQL Injection attack allows an attacker to retrieve data from multiple tables within the same database. This technique is particularly useful when the attacker wants to extract data from tables that are not directly accessible through the application's normal functionality.

### How UNION Attack Works

The UNION operator combines the results of two or more SELECT statements into a single result set. By injecting a UNION clause into a SQL query, an attacker can manipulate the query to retrieve data from other tables.

#### Example Scenario

Consider a search feature in a web application that constructs a SQL query based on user input:

```sql
SELECT product_name, price FROM products WHERE product_id = 'input_product_id';
```

An attacker can inject a UNION clause to retrieve data from another table, such as the `users` table:

```sql
SELECT product_name, price FROM products WHERE product_id = '1' UNION SELECT username, password FROM users;
```

This query will return a result set that includes both product information and user credentials.

### Real-World Example

A real-world example of a UNION-based SQL Injection attack occurred in the 2017 Equifax breach. Attackers exploited a vulnerability in the Apache Struts framework to inject SQL commands, including UNION clauses, to extract sensitive data from the company's databases.

### Prevention Techniques

To prevent UNION-based SQL Injection attacks, developers should:

1. **Use Parameterized Queries**: Ensure that all user input is properly parameterized to prevent injection of arbitrary SQL code.
2. **Limit Database Permissions**: Restrict database permissions to ensure that the application account can only access the necessary tables and columns.
3. **Input Validation**: Validate and sanitize user input to ensure it conforms to expected formats.

### Secure Coding Practices

Here is an example of a secure coding practice using parameterized queries in Python with MySQL:

```python
import mysql.connector

def get_product(product_id):
    conn = mysql.connector.connect(user='user', password='password', host='localhost', database='mydatabase')
    cursor = conn.cursor()
    
    # Using a parameterized query
    query = "SELECT product_name, price FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    
    product = cursor.fetchone()
    conn.close()
    return product
```

In this example, the `%s` placeholder is replaced with the actual value provided by the user, ensuring that the input is treated as data rather than executable code.

---
<!-- nav -->
[[03-Extracting Data with SQL Injection|Extracting Data with SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/06-Lab 5 SQL injection UNION attack retrieving data from other tables/00-Overview|Overview]] | [[05-SQL Injection Union Attack Retrieving Data from Other Tables|SQL Injection Union Attack Retrieving Data from Other Tables]]
