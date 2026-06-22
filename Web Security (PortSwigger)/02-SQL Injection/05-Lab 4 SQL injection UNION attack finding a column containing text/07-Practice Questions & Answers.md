---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the purpose of the `UNION` operator in SQL and its role in SQL injection attacks.**

The `UNION` operator in SQL is used to combine the results of two or more `SELECT` statements into a single result set. For the `UNION` operator to work correctly, the number and order of columns in each `SELECT` statement must match, and the data types of corresponding columns must be compatible.

In SQL injection attacks, attackers use the `UNION` operator to manipulate the query structure and inject their own data into the result set. By doing so, they can bypass authentication mechanisms, extract sensitive information from the database, or alter the application's behavior. The attacker needs to determine the number of columns and their data types to craft a valid `UNION` query that blends seamlessly with the original query.

**Q2. How would you determine the number of columns in a SQL query vulnerable to a union-based SQL injection attack?**

To determine the number of columns in a SQL query vulnerable to a union-based SQL injection attack, you can use the `ORDER BY` clause. The idea is to incrementally increase the column index in the `ORDER BY` clause until you receive an error indicating that the specified column does not exist.

Here’s a step-by-step approach:

1. Start with `ORDER BY 1`.
2. Increment the column index (`ORDER BY 2`, `ORDER BY 3`, etc.) until you receive an error.
3. The number of columns is the last index that did not cause an error minus one.

For example, if `ORDER BY 4` causes an error, the query has 3 columns.

**Q3. How would you identify a column that accepts string data in a SQL query vulnerable to a union-based SQL injection attack?**

To identify a column that accepts string data in a SQL query vulnerable to a union-based SQL injection attack, you can inject a string value into each column and check if the injection is successful without causing an error.

Here’s a step-by-step approach:

1. Determine the number of columns using the `ORDER BY` method.
2. Inject a string value into each column one by one.
3. Check if the injected string appears in the response.
4. If the string appears, that column accepts string data.

For example, if you determined that the query has 3 columns, you would test each column as follows:

```sql
SELECT * FROM table WHERE column = 'value' UNION SELECT 'test', NULL, NULL -- 
```

If `'test'` appears in the response, the first column accepts string data.

**Q4. Why is it important to find a column that accepts string data during a union-based SQL injection attack?**

Finding a column that accepts string data is crucial during a union-based SQL injection attack because it allows the attacker to inject and display sensitive information such as usernames, passwords, or other textual data from the database. 

By identifying a column that accepts string data, the attacker can craft a `UNION` query to extract and display this information in the web application's response. This is particularly useful for extracting hashed passwords, usernames, or other textual data that can be used to further compromise the system.

**Q5. How would you script a union-based SQL injection attack to automatically determine the number of columns and identify a column that accepts string data?**

To script a union-based SQL injection attack to automatically determine the number of columns and identify a column that accepts string data, you can use a Python script that iterates through potential column numbers and tests each column for string data compatibility.

Here’s a sample Python script:

```python
import requests

def find_number_of_columns(url):
    for i in range(1, 50):
        payload = f"' ORDER BY {i}--"
        response = requests.get(url + payload)
        if response.status_code == 500:
            return i - 1
    return None

def find_string_column(url, num_columns):
    string_value = "test"
    for i in range(1, num_columns + 1):
        payload_list = ["NULL"] * num_columns
        payload_list[i - 1] = f"'{string_value}'"
        payload = f"' UNION SELECT {', '.join(payload_list)}--"
        response = requests.get(url + payload)
        if string_value in response.text:
            return i
    return None

url = "http://example.com/vulnerable_page?category="
num_columns = find_number_of_columns(url)
if num_columns:
    string_column = find_string_column(url, num_columns)
    if string_column:
        print(f"The column that accepts string data is: {string_column}")
    else:
        print("No column accepts string data.")
else:
    print("Could not determine the number of columns.")
```

This script first determines the number of columns using the `ORDER BY` method and then identifies a column that accepts string data by injecting a test string into each column and checking if it appears in the response.

**Q6. What recent real-world examples or CVEs demonstrate the impact of union-based SQL injection attacks?**

Union-based SQL injection attacks continue to pose significant risks to web applications. One notable example is the breach of the Capital One data, where an attacker exploited a vulnerability in a web application firewall (WAF) configuration to gain unauthorized access to sensitive customer data.

Another example is CVE-2021-30147, which affected the WordPress plugin WP Event Manager. An attacker could exploit a union-based SQL injection vulnerability to extract sensitive data from the database, including user credentials and personal information.

These examples highlight the importance of securing web applications against SQL injection attacks by implementing proper input validation, using parameterized queries, and regularly updating and patching software components.

---
<!-- nav -->
[[06-Understanding SQL Injection and UNION Attacks|Understanding SQL Injection and UNION Attacks]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]]
