---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what API injection is and provide an example of how it can occur.**

API injection occurs when an attacker constructs malicious input that is executed by the backend system, such as a database or an operating system. The attacker can inject commands or queries into the API call, which the backend processes without proper validation or sanitization. 

For example, consider an API that retrieves user information based on a username parameter:

```plaintext
GET /api/users?username=admin
```

If the backend does not properly sanitize the `username` parameter, an attacker could inject a SQL query:

```plaintext
GET /api/users?username=admin' OR '1'='1
```

This would result in the backend executing a modified SQL query that could return all user records instead of just the admin record.

**Q2. How can an attacker exploit SQL injection vulnerabilities in an API?**

An attacker can exploit SQL injection vulnerabilities by crafting malicious inputs that manipulate the SQL queries executed by the backend. Here’s a step-by-step process:

1. **Identify Vulnerable Parameters**: Find parameters that are used in SQL queries, such as usernames or IDs.
2. **Test for Injection**: Use payloads like `' OR '1'='1` to test if the parameter is vulnerable.
3. **Exploit Injection**: Once confirmed, the attacker can craft more complex SQL statements to extract sensitive data, modify records, or even execute arbitrary commands.

Example payload to test for SQL injection:

```plaintext
GET /api/users?username=admin' UNION SELECT username, password FROM users --
```

This payload attempts to retrieve all usernames and passwords from the `users` table.

**Q3. What types of injection attacks can occur besides SQL injection? Provide recent real-world examples.**

Besides SQL injection, other types of injection attacks include:

- **NoSQL Injection**: Occurs in databases that do not use SQL, such as MongoDB.
- **LDAP Injection**: Exploits vulnerabilities in Lightweight Directory Access Protocol.
- **OS Command Injection**: Allows execution of arbitrary commands on the server.
- **XML External Entity (XXE) Injection**: Exploits XML parsers to read files or execute commands.

Recent real-world examples include:

- **CVE-2021-21974**: An XXE vulnerability in VMware Workspace ONE Access and Identity Manager allowed attackers to read arbitrary files.
- **CVE-2021-35602**: An OS command injection vulnerability in Apache Struts allowed remote code execution.

**Q4. How can developers prevent API injection attacks?**

Developers can prevent API injection attacks by implementing the following best practices:

1. **Input Validation**: Ensure all input parameters are validated against expected formats and ranges.
2. **Parameterized Queries**: Use parameterized queries or prepared statements to separate SQL logic from user input.
3. **Sanitization**: Sanitize input to remove potentially harmful characters or patterns.
4. **Least Privilege Principle**: Ensure the backend service runs with minimal necessary privileges.
5. **Regular Audits**: Conduct regular security audits and penetration testing to identify and fix vulnerabilities.

Example of a parameterized query in Python:

```python
import sqlite3

def get_user(username):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    results = cursor.fetchall()
    conn.close()
    return results
```

**Q5. How can you detect if an API is vulnerable to injection attacks?**

To detect if an API is vulnerable to injection attacks, you can use the following methods:

1. **Manual Testing**: Send crafted payloads to the API and observe the responses for signs of successful injection.
2. **Automated Scanners**: Use tools like Burp Suite, OWASP ZAP, or commercial scanners to automatically test for vulnerabilities.
3. **Code Review**: Perform static code analysis to check for insecure coding practices and lack of input validation.
4. **Fuzzing**: Use fuzzing tools to send random or malformed inputs to the API and monitor for unexpected behavior.

Example of using Burp Suite to test for SQL injection:

1. Capture the API request in Burp Suite.
2. Use the Intruder tool to send payloads like `' OR '1'='1`.
3. Analyze the responses to determine if the API is vulnerable.

By combining these methods, you can effectively identify and mitigate injection vulnerabilities in APIs.

---
<!-- nav -->
[[05-Injection Vulnerabilities in APIs|Injection Vulnerabilities in APIs]] | [[API Security/05-OWASP API TOP 10/09-API8 Injection/00-Overview|Overview]]
