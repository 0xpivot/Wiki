---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Introduction to Injection Attacks

Injection attacks occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data can trick the interpreter into executing unintended commands or accessing unauthorized data. This can happen in various contexts such as SQL databases, LDAP servers, XML parsers, and even operating system commands.

### Types of Injection Attacks

- **SQL Injection**: Occurs when an attacker manipulates a SQL query by inserting or altering parts of the query.
- **NoSQL Injection**: Similar to SQL injection but affects NoSQL databases like MongoDB.
- **LDAP Injection**: Exploits vulnerabilities in LDAP queries to manipulate search results or execute unauthorized commands.
- **OS Command Injection**: Occurs when an attacker injects malicious commands into a program that executes shell commands.
- **XML External Entity (XXE) Injection**: Exploits vulnerabilities in XML parsers to access sensitive files or execute remote commands.
- **ORM Injection**: Occurs when an attacker manipulates Object-Relational Mapping (ORM) queries to bypass intended logic.

### Why Injection Attacks Matter

Injection attacks are critical because they can lead to severe consequences such as:

- **Information Disclosure**: Exposure of sensitive data.
- **Data Loss**: Deletion or corruption of important data.
- **Denial of Service (DoS)**: Disruption of service availability.
- **Host Takeover**: Complete control over the server or application.

### How Injection Attacks Work

To understand injection attacks, consider the following example of a SQL injection attack. Suppose an API endpoint accepts a username and password for authentication:

```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

If the backend code constructs a SQL query like this:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```

An attacker can inject malicious data into the `username` field to manipulate the query:

```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "admin' OR '1'='1",
  "password": "password"
}
```

This results in the following SQL query:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'password';
```

The condition `'1'='1'` is always true, effectively bypassing the password check.

### Real-World Examples

#### CVE-2018-1259

In 2018, a SQL injection vulnerability was discovered in the WordPress REST API. An attacker could inject malicious SQL code into the `filter` parameter, leading to unauthorized data access.

#### CVE-2019-11510

In 2019, a NoSQL injection vulnerability was found in the MongoDB database. Attackers could inject malicious commands into the query, potentially gaining full access to the database.

### Detection and Prevention

#### How to Detect Injection Vulnerabilities

Attackers often use automated tools like fuzzers to detect injection vulnerabilities. A fuzzer sends a series of malformed inputs to the application to see if any cause unexpected behavior.

For example, using a fuzzer to test the `/api/login` endpoint:

```python
import requests

# List of potential injection payloads
payloads = ["'", '"', "OR '1'='1", "admin' --"]

for payload in payloads:
    data = {
        "username": payload,
        "password": "password"
    }
    response = requests.post("http://example.com/api/login", json=data)
    print(f"Payload: {payload} | Response: {response.status_code}")
```

#### How to Prevent Injection Attacks

1. **Input Validation**: Ensure that all user inputs are validated against a strict set of rules.
2. **Parameterized Queries**: Use parameterized queries or prepared statements to separate data from commands.
3. **Least Privilege Principle**: Run applications with the least privileges necessary to perform their tasks.
4. **Web Application Firewalls (WAF)**: Implement WAFs to filter out malicious requests.

### Secure Coding Practices

#### Example: Secure SQL Query

**Vulnerable Code**:

```sql
SELECT * FROM users WHERE username = '$username' AND password = '$password';
```

**Secure Code**:

```sql
PreparedStatement stmt = connection.prepareStatement(
    "SELECT * FROM users WHERE username = ? AND password = ?");
stmt.setString(1, username);
stmt.setString(2, password);
ResultSet rs = stmt.executeQuery();
```

### Configuration Hardening

#### Example: Hardening MySQL Configuration

Edit the MySQL configuration file (`my.cnf`):

```ini
[mysqld]
sql_mode=NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION
```

### Hands-On Labs

- **PortSwigger Web Security Academy**: Offers interactive labs to practice detecting and preventing SQL injection.
- **OWASP Juice Shop**: Provides a vulnerable web application to learn about various injection attacks.
- **DVWA (Damn Vulnerable Web Application)**: Contains multiple injection vulnerabilities for educational purposes.

### Conclusion

Injection attacks are a significant threat to API security. By understanding the types of injection attacks, their mechanisms, and implementing robust detection and prevention strategies, developers can significantly reduce the risk of such vulnerabilities. Always validate inputs, use parameterized queries, and follow secure coding practices to ensure the safety of your applications.

---
<!-- nav -->
[[01-Introduction to API8 Injection|Introduction to API8 Injection]] | [[API Security/05-OWASP API TOP 10/09-API8 Injection/00-Overview|Overview]] | [[03-API8 Injection Vulnerability|API8 Injection Vulnerability]]
