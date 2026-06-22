---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Introduction to SQL Injection

SQL Injection is a type of security vulnerability that allows an attacker to manipulate SQL queries executed by a web application. This manipulation can lead to unauthorized access to sensitive data, data corruption, or even complete control over the database server. Understanding SQL Injection is crucial for both developers and security professionals as it remains one of the most prevalent and dangerous vulnerabilities in web applications.

### What is SQL Injection?

SQL Injection occurs when user input is incorrectly filtered by a web application and is then used to construct dynamic SQL queries. An attacker can inject malicious SQL statements into these queries, which are then executed by the database server. This can result in unauthorized access to data, modification of data, or even the execution of arbitrary commands on the server.

#### Example of SQL Injection

Consider a simple login form where a user enters their username and password. The application might construct an SQL query like this:

```sql
SELECT * FROM users WHERE username = 'input_username' AND password = 'input_password';
```

If the `input_username` and `input_password` are directly inserted into the query without proper validation or sanitization, an attacker could inject malicious SQL code. For instance, if the attacker inputs `' OR '1'='1` as the username, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true.

### Types of SQL Injection

There are several types of SQL Injection vulnerabilities, each with its own characteristics and potential impacts:

1. **Classic SQL Injection**: This is the most common form where the attacker injects SQL code into a query that is executed directly by the database.
2. **Blind SQL Injection**: In this type, the attacker does not receive direct feedback from the database but can infer information based on the application's behavior.
3. **Union-Based SQL Injection**: Here, the attacker uses the `UNION` operator to combine the results of two or more SELECT statements.
4. **Error-Based SQL Injection**: The attacker exploits error messages returned by the database to extract information.
5. **Second-Order SQL Injection**: This occurs when the injected SQL code is stored in the database and executed later.

### How Common Are SQL Injection Vulnerabilities?

SQL Injection vulnerabilities are extremely common due to the widespread use of SQL databases and the ease with which developers can introduce them. According to the OWASP Top Ten Project, SQL Injection consistently ranks among the top vulnerabilities in web applications.

#### Recent Real-World Examples

- **CVE-2021-21972**: A SQL Injection vulnerability was discovered in the WordPress plugin "WP Event Manager". Attackers could exploit this vulnerability to execute arbitrary SQL commands, leading to data theft or manipulation.
- **CVE-2020-14882**: A SQL Injection vulnerability was found in the Joomla CMS. This allowed attackers to inject malicious SQL code, potentially gaining administrative privileges.

### Finding SQL Injection Vulnerabilities

Finding SQL Injection vulnerabilities requires a combination of manual testing and automated tools. The process differs depending on whether you have access to the source code (white-box testing) or only the application interface (black-box testing).

#### Black Box Testing

In black-box testing, you do not have access to the source code. You must rely on observing the application's behavior to identify potential vulnerabilities.

##### Example: Testing a Login Form

1. **Input Manipulation**: Enter various inputs into the login form, such as `' OR '1'='1`, `admin' --`, etc.
2. **Behavior Analysis**: Observe the application's response. If the application behaves unexpectedly (e.g., logs in without correct credentials), it may indicate a vulnerability.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin' --&password=anything
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
</head>
<body>
    <h1>Welcome, admin!</h1>
</body>
</html>
```

#### White Box Testing

In white-box testing, you have access to the source code. This allows you to review the code and identify potential SQL Injection points.

##### Example: Reviewing Code

Consider the following PHP code snippet:

```php
$username = $_GET['username'];
$password = $_GET['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($conn, $query);
```

This code is vulnerable to SQL Injection because it directly inserts user input into the SQL query without proper validation or sanitization.

### Exploiting SQL Injection Vulnerabilities

Exploiting SQL Injection vulnerabilities involves crafting malicious SQL queries to achieve specific goals, such as extracting data or gaining remote code execution.

#### Extracting Data

To extract data, an attacker can use UNION-based SQL Injection. Consider the following query:

```sql
SELECT username, password FROM users WHERE id = 1;
```

An attacker can inject a UNION statement to retrieve additional data:

```sql
SELECT username, password FROM users WHERE id = 1 UNION SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'database_name';
```

#### Gaining Remote Code Execution

In some cases, SQL Injection can lead to remote code execution. This typically involves exploiting a feature of the database that allows executing system commands.

##### Example: MySQL Command Execution

MySQL supports the `SYSTEM()` function, which can be used to execute system commands. An attacker can inject a query like:

```sql
SELECT LOAD_FILE('/etc/passwd');
```

This query reads the contents of the `/etc/passwd` file, which contains system user information.

### How to Prevent / Defend Against SQL Injection

Preventing SQL Injection involves a combination of secure coding practices, input validation, and the use of prepared statements or parameterized queries.

#### Secure Coding Practices

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.
3. **Least Privilege Principle**: Ensure that the database user has the minimum necessary permissions to perform its tasks.

##### Example: Using Prepared Statements

Consider the previous PHP code snippet. By using prepared statements, the code becomes secure:

```php
$username = $_GET['username'];
$password = $_GET['password'];

$stmt = $conn->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
```

#### Detection

Detecting SQL Injection vulnerabilities can be done through static code analysis tools and dynamic testing frameworks.

##### Static Code Analysis Tools

Tools like SonarQube, Fortify, and Veracode can analyze source code to identify potential SQL Injection points.

##### Dynamic Testing Frameworks

Frameworks like Burp Suite, OWASP ZAP, and SQLMap can be used to test applications for SQL Injection vulnerabilities.

#### Prevention

1. **Use ORM Libraries**: Object-Relational Mapping (ORM) libraries abstract away SQL queries and provide built-in protection against SQL Injection.
2. **Database Hardening**: Configure the database to minimize exposure to SQL Injection attacks. Disable unnecessary features and limit user permissions.

##### Example: Database Configuration

Ensure that the database user has limited permissions:

```sql
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'web_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON 'database_name'.* TO 'web_user'@'localhost';
```

### Conclusion

SQL Injection is a critical vulnerability that can have severe consequences for web applications. By understanding the theory, types, and methods of finding and exploiting SQL Injection vulnerabilities, developers and security professionals can take proactive steps to prevent and defend against these attacks. Regularly reviewing and updating security practices is essential to maintaining the integrity and security of web applications.

### Practice Labs

For hands-on experience with SQL Injection, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice SQL Injection techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security vulnerabilities, including SQL Injection.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable for educational purposes.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide a safe environment to explore and understand SQL Injection vulnerabilities in depth.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[02-SQL Injection A Comprehensive Guide|SQL Injection A Comprehensive Guide]]
