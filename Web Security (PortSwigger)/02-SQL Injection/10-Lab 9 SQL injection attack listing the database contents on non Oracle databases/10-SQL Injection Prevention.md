---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## SQL Injection Prevention

### Secure Input Validation

One of the most effective ways to prevent SQL Injection is to ensure proper input validation. This involves validating user input to ensure it meets the expected format and does not contain malicious SQL code.

#### Example

Consider the following PHP code:

```php
$username = $_POST['username'];
$password = $_POST['password'];

// Validate input
if (!preg_match('/^[a-zA-Z0-9]+$/', $username)) {
    die('Invalid username');
}

if (!preg_match('/^[a-zA-Z0-9]+$/', $password)) {
    die('Invalid password');
}
```

This code ensures that the username and password only contain alphanumeric characters, preventing SQL Injection.

### Prepared Statements and Parameterized Queries

Prepared statements and parameterized queries are a robust defense against SQL Injection. These techniques involve separating the SQL code from the user input, ensuring that the input is treated as data rather than executable code.

#### Example

Consider the following PHP code using prepared statements:

```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username AND password = :password');
$stmt->execute(['username' => $username, 'password' => $password]);
```

This code uses prepared statements to separate the SQL code from the user input, preventing SQL Injection.

### Least Privilege Principle

The least privilege principle involves granting the minimum necessary permissions to the application's database connection. This reduces the potential damage an attacker can cause if they succeed in injecting SQL code.

#### Example

Consider the following MySQL user creation:

```sql
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE ON webapp.* TO 'webapp'@'localhost';
```

This code grants the `webapp` user only the necessary permissions to interact with the `webapp` database, reducing the potential damage an attacker can cause.

### Regular Security Audits

Regular security audits involve reviewing the application's code and configuration to identify and mitigate potential security vulnerabilities. This includes reviewing the application's input validation, SQL queries, and database permissions.

#### Example

Consider the following security audit checklist:

- Review all user input to ensure proper validation.
- Review all SQL queries to ensure the use of prepared statements and parameterized queries.
- Review database permissions to ensure the least privilege principle is followed.
- Review error handling to ensure error messages do not reveal sensitive information.

### Real-World Example: WordPress SQL Injection Vulnerability

In 2018, a critical SQL Injection vulnerability was discovered in WordPress, affecting versions 4.7.0 to 4.9.8. The vulnerability allowed attackers to inject SQL code through the search functionality, potentially leading to data theft or manipulation.

#### Vulnerable Code

```php
$search = $_GET['search'];
$query = "SELECT * FROM posts WHERE title LIKE '%$search%'";
```

#### Fixed Code

```php
$search = $_GET['search'];
$stmt = $pdo->prepare("SELECT * FROM posts WHERE title LIKE :search");
$stmt->execute(['search' => '%' . $search . '%']);
```

This code uses prepared statements to separate the SQL code from the user input, preventing SQL Injection.

---
<!-- nav -->
[[09-SQL Injection Detection|SQL Injection Detection]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[11-SQL Injection Techniques|SQL Injection Techniques]]
