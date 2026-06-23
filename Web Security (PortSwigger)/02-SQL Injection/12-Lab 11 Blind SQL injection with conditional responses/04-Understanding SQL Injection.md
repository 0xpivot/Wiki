---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Understanding SQL Injection

SQL Injection (SQLi) is a type of attack where an attacker manipulates a SQL query to gain unauthorized access to data or execute malicious actions within a database. This attack exploits vulnerabilities in the way applications handle user input, particularly when constructing SQL queries dynamically.

### What is SQL Injection?

SQL Injection occurs when an application fails to properly validate or sanitize user input, allowing an attacker to inject arbitrary SQL code into a query. This can lead to unauthorized data retrieval, data manipulation, or even complete control over the database.

#### Why Does SQL Injection Matter?

SQL Injection is one of the most common and dangerous types of attacks in web applications. It can result in significant data breaches, financial losses, and reputational damage. For instance, the infamous Target data breach in 2013 was partly due to SQL Injection, which exposed sensitive information of millions of customers.

### How SQL Injection Works

To understand SQL Injection, let's break down the process:

1. **User Input**: An application takes user input, such as a username or search query.
2. **Dynamic Query Construction**: The application constructs a SQL query using this input.
3. **Injection Point**: If the input is not properly validated or sanitized, an attacker can inject SQL code at this point.
4. **Execution**: The modified SQL query is executed by the database, potentially leading to unintended actions.

#### Example of SQL Injection

Consider a simple login form where the SQL query is constructed like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If an attacker inputs `'' OR '1'='1` as the username, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will always return true, allowing the attacker to bypass authentication.

### Types of SQL Injection

There are several types of SQL Injection attacks, including:

1. **Classic SQL Injection**: The attacker injects SQL code into a query that is executed immediately.
2. **Blind SQL Injection**: The attacker cannot see the results of their injected SQL code but can infer information based on the application's behavior.
3. **Union-Based SQL Injection**: The attacker uses the UNION operator to combine the results of two or more SELECT statements.
4. **Error-Based SQL Injection**: The attacker relies on error messages returned by the database to infer information about the database structure.

### Lab 11: Blind SQL Injection with Conditional Responses

In this lab, we will explore a scenario where the application behaves differently based on the existence of a tracking ID in the database. This behavior can be exploited through blind SQL Injection.

#### Scenario Setup

Imagine a web application that tracks user visits using a unique tracking ID. When a user visits a page with a specific tracking ID, the application checks if the ID exists in the database. Based on this check, the application displays either a "welcome back" message or no message.

The SQL query might look something like this:

```sql
SELECT tracking_id FROM visits WHERE tracking_id = 'input_tracking_id';
```

If the tracking ID exists, the query returns a value, and the application displays a "welcome back" message. If the tracking ID does not exist, the query returns nothing, and the application shows no message.

#### Exploiting the Behavior

To confirm if the application is vulnerable to blind SQL Injection, we need to observe the behavior when we manipulate the tracking ID.

1. **Existing Tracking ID**:
    - Send a request with an existing tracking ID.
    - Observe the response.

```http
POST /track HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

tracking_id=existing_id
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

Welcome back!
```

2. **Non-Existing Tracking ID**:
    - Send a request with a non-existing tracking ID.
    - Observe the response.

```http
POST /track HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

tracking_id=non_existing_id
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!-- No welcome back message -->
```

By observing these responses, we can confirm that the application behaves differently based on the existence of the tracking ID.

### Exploiting Blind SQL Injection

To exploit this behavior, we can use conditional SQL statements to infer information about the database.

#### Example Exploit

Let's assume we want to determine the length of the tracking ID stored in the database. We can use a conditional statement to check if the length of the tracking ID is greater than a certain value.

1. **Check Length Greater Than 5**:
    - Modify the tracking ID to include a conditional statement.
    - Send the request and observe the response.

```http
POST /track HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

tracking_id=existing_id' AND LENGTH(tracking_id) > 5 --
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

Welcome back!
```

Since we received a "welcome back" message, we know that the length of the tracking ID is greater than 5.

2. **Check Length Greater Than 10**:
    - Modify the tracking ID to check if the length is greater than 10.
    - Send the request and observe the response.

```http
POST /track HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

tracking_id=existing_id' AND LENGTH(tracking_id) > 10 --
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!-- No welcome back message -->
```

Since we did not receive a "welcome back" message, we know that the length of the tracking ID is not greater than 10.

By systematically checking different lengths, we can determine the exact length of the tracking ID.

### Real-World Examples

Recent real-world examples of SQL Injection attacks include:

- **CVE-2021-21972**: A vulnerability in the WordPress REST API allowed attackers to perform SQL Injection, leading to unauthorized data access.
- **CVE-2020-14882**: A vulnerability in the Joomla CMS allowed attackers to perform SQL Injection, leading to unauthorized data access and potential server compromise.

These examples highlight the importance of securing applications against SQL Injection attacks.

### How to Prevent / Defend Against SQL Injection

#### Detection

To detect SQL Injection vulnerabilities, you can use automated tools such as:

- **OWASP ZAP**: A free, open-source tool for detecting security vulnerabilities in web applications.
- **Burp Suite**: A commercial tool for testing web application security.

#### Prevention

To prevent SQL Injection, follow these best practices:

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.

```java
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE username = ? AND password = ?");
stmt.setString(1, username);
stmt.setString(2, password);
ResultSet rs = stmt.executeQuery();
```

2. **Input Validation**: Validate and sanitize user input to ensure it meets expected formats.

```python
import re

def validate_input(input_string):
    if re.match(r'^[a-zA-Z0-9]+$', input_string):
        return True
    return False
```

3. **Least Privilege Principle**: Ensure that database accounts used by the application have the minimum necessary privileges.

4. **Web Application Firewalls (WAF)**: Use WAFs to filter out malicious SQL Injection attempts.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Code:**

```php
$tracking_id = $_GET['tracking_id'];
$query = "SELECT tracking_id FROM visits WHERE tracking_id = '$tracking_id'";
$result = mysqli_query($conn, $query);
```

**Secure Code:**

```php
$tracking_id = $_GET['tracking_id'];
$stmt = $conn->prepare("SELECT tracking_id FROM visits WHERE tracking_id = ?");
$stmt->bind_param("s", $tracking_id);
$stmt->execute();
$result = $stmt->get_result();
```

### Conclusion

Understanding and preventing SQL Injection is crucial for securing web applications. By following best practices and using secure coding techniques, you can significantly reduce the risk of SQL Injection attacks.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice various types of SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

By engaging with these labs, you can gain practical experience in identifying and mitigating SQL Injection vulnerabilities.

---
<!-- nav -->
[[03-Understanding Blind SQL Injection|Understanding Blind SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/12-Lab 11 Blind SQL injection with conditional responses/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/12-Lab 11 Blind SQL injection with conditional responses/05-Conclusion|Conclusion]]
