---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## API8 Injection

### Introduction to Injection Vulnerabilities

Injection vulnerabilities occur when an attacker can insert malicious data into an application, which is then processed by the underlying system in a way that compromises security. This can happen in various contexts, such as SQL databases, NoSQL databases, XML parsers, and command execution. In the context of APIs, injection vulnerabilities are particularly dangerous because APIs often interact with backend systems that store sensitive data.

### Understanding Injection in APIs

In the context of the lecture, the instructor mentions performing injections on a database named `API`. Let's delve deeper into what this means and how it can be exploited.

#### What is Injection?

Injection occurs when untrusted data is sent to an interpreter as part of a command or query. The attacker’s hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data. Common types of injection attacks include:

- **SQL Injection**: Exploiting vulnerabilities in SQL queries to execute arbitrary SQL code.
- **NoSQL Injection**: Similar to SQL Injection but targeting NoSQL databases like MongoDB.
- **OS Command Injection**: Injecting malicious OS commands into a vulnerable application.
- **LDAP Injection**: Exploiting vulnerabilities in LDAP queries to gain unauthorized access.

#### Why Does Injection Matter?

Injection vulnerabilities can lead to severe consequences, including:

- **Data Leakage**: Unauthorized access to sensitive information stored in databases.
- **Data Manipulation**: Modification of data within the database.
- **Denial of Service (DoS)**: Disruption of service by overwhelming the system with malicious requests.
- **Remote Code Execution (RCE)**: Execution of arbitrary code on the server.

### Real-World Examples of Injection Attacks

Recent real-world examples of injection attacks include:

- **CVE-2021-22205**: A SQL injection vulnerability in the WordPress plugin WP Travel Engine allowed attackers to execute arbitrary SQL commands, potentially leading to data leakage or manipulation.
- **CVE-2020-14882**: An SQL injection vulnerability in the Joomla! CMS allowed attackers to execute arbitrary SQL commands, leading to potential data leakage or manipulation.

These examples highlight the critical nature of securing against injection attacks.

### Detailed Example: SQL Injection in an API

Let's consider a scenario where an API interacts with a SQL database. Suppose we have an endpoint `/api/users` that retrieves user information based on a provided username.

#### Vulnerable Code Example

```python
import sqlite3

def get_user(username):
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
```

#### Attack Scenario

An attacker could exploit this vulnerability by providing a specially crafted input to the `username` parameter. For example, if the attacker provides the following input:

```
' OR '1'='1
```

The resulting SQL query would be:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1'
```

This query would return all rows from the `users` table because the condition `'1'='1'` is always true.

#### Full HTTP Request and Response

**HTTP Request:**

```http
GET /api/users?username=%27+OR+%271%27%3D%271 HTTP/1.1
Host: example.com
Accept: application/json
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1024

{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com"
    },
    {
      "id": 2,
      "username": "user1",
      "email": "user1@example.com"
    }
  ]
}
```

### How to Prevent / Defend Against Injection Attacks

#### Secure Coding Practices

To prevent injection attacks, follow these secure coding practices:

1. **Use Parameterized Queries**: Instead of constructing SQL queries using string concatenation, use parameterized queries or prepared statements.

2. **Input Validation**: Validate and sanitize all user inputs to ensure they meet expected formats and constraints.

3. **Least Privilege Principle**: Ensure that database connections used by the application have the minimum necessary privileges.

#### Corrected Code Example

Here is the corrected version of the vulnerable code using parameterized queries:

```python
import sqlite3

def get_user(username):
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    return result
```

#### Full HTTP Request and Response with Secure Code

**HTTP Request:**

```http
GET /api/users?username=admin HTTP/1.1
Host: example.com
Accept: application/json
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1024

{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com"
    }
  ]
}
```

### Detection and Prevention Tools

Several tools and techniques can help detect and prevent injection attacks:

1. **Static Application Security Testing (SAST)**: Tools like SonarQube and Fortify can analyze source code for potential injection vulnerabilities.
2. **Dynamic Application Security Testing (DAST)**: Tools like Burp Suite and OWASP ZAP can simulate attacks to identify vulnerabilities.
3. **Web Application Firewalls (WAF)**: WAFs like ModSecurity can filter out malicious requests before they reach the application.

### Hands-On Practice Labs

For hands-on practice with API injection vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on SQL injection and other injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various security vulnerabilities, including injection attacks.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerable web applications, including those susceptible to injection attacks.

### Conclusion

Injection vulnerabilities are a significant threat to API security. By understanding the mechanisms behind these attacks and implementing robust defensive measures, developers can significantly reduce the risk of exploitation. Always validate and sanitize user inputs, use parameterized queries, and leverage security tools to detect and mitigate vulnerabilities.

---
<!-- nav -->
[[03-API8 Injection Vulnerability|API8 Injection Vulnerability]] | [[API Security/05-OWASP API TOP 10/09-API8 Injection/00-Overview|Overview]] | [[05-Injection Vulnerabilities in APIs|Injection Vulnerabilities in APIs]]
