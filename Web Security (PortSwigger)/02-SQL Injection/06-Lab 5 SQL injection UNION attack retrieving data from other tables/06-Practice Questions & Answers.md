---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the process of determining the number of columns in a SQL injection vulnerability.**

To determine the number of columns in a SQL injection vulnerability, you can use the `ORDER BY` clause. By incrementally increasing the column number in the `ORDER BY` clause, you can identify the point at which an error occurs. This error indicates that you have exceeded the actual number of columns in the query. For example, if `ORDER BY 1` and `ORDER BY 2` work without errors, but `ORDER BY 3` causes an error, it implies that the query uses 2 columns.

**Q2. How would you exploit a SQL injection vulnerability to retrieve data from another table using a UNION attack?**

To exploit a SQL injection vulnerability to retrieve data from another table using a UNION attack, follow these steps:

1. Determine the number of columns in the original query using the `ORDER BY` technique.
2. Determine the data types of the columns by injecting `UNION SELECT NULL, NULL` and checking for errors.
3. Construct a `UNION SELECT` query to retrieve data from the desired table. Ensure the number of selected columns matches the original query.

For example, if the original query has 2 columns and both are of string type, you can inject:
```sql
' UNION SELECT username, password FROM users--
```
This will append the usernames and passwords from the `users` table to the original query's results.

**Q3. Why is it important to determine the data types of the columns in a SQL injection attack?**

Determining the data types of the columns is crucial because the injected SQL query must match the structure of the original query. If the data types do not align, the database will throw an error, preventing successful exploitation. For instance, if a column expects a numeric value and you inject a string, the query will fail. Ensuring the correct data types allows the injected query to blend seamlessly with the original query, enabling the retrieval of data from other tables.

**Q4. How would you parse the response from a SQL injection attack to extract specific data, such as an administrator's password?**

To parse the response from a SQL injection attack and extract specific data like an administrator's password, you can use a web scraping library like BeautifulSoup in Python. Here’s a step-by-step approach:

1. Send the SQL injection payload and capture the response.
2. Use BeautifulSoup to parse the HTML content of the response.
3. Locate the specific elements containing the desired data (e.g., usernames and passwords).
4. Extract the content of these elements.

Example code snippet:
```python
from bs4 import BeautifulSoup

# Assume 'response' contains the HTML content of the response
soup = BeautifulSoup(response.text, 'html.parser')

# Find the element containing the administrator's password
admin_password_element = soup.find('td', text='administrator').find_next_sibling('td')
admin_password = admin_password_element.get_text()

print(f"Administrator password: {admin_password}")
```

**Q5. What recent real-world examples or CVEs demonstrate the impact of SQL injection vulnerabilities?**

One notable example is the SQL injection vulnerability in the Joomla CMS, tracked as CVE-2019-9161. This vulnerability allowed attackers to execute arbitrary SQL commands, potentially leading to unauthorized access to sensitive data such as user credentials. Another example is the SQL injection vulnerability in the phpMyAdmin tool, tracked as CVE-2018-12611, which allowed attackers to bypass authentication mechanisms and gain administrative privileges.

These examples highlight the critical importance of securing web applications against SQL injection attacks, emphasizing the need for proper input validation, parameterized queries, and regular security audits.

---
<!-- nav -->
[[05-SQL Injection Union Attack Retrieving Data from Other Tables|SQL Injection Union Attack Retrieving Data from Other Tables]] | [[Web Security (PortSwigger)/02-SQL Injection/06-Lab 5 SQL injection UNION attack retrieving data from other tables/00-Overview|Overview]]
