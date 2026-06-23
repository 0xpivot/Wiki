---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## How to Prevent / Defend Against SQL Injection

### Secure Coding Practices

#### Prepared Statements

Prepared statements are a secure way to execute SQL queries. They separate the SQL logic from the data, preventing SQL Injection.

**Vulnerable Code:**

```php
$username = $_POST['username'];
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($connection, $query);
```

**Secure Code:**

```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $connection->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
```

### Parameterized Queries

Parameterized queries work similarly to prepared statements by separating the SQL logic from the data.

**Vulnerable Code:**

```python
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

username = input("Enter username: ")
password = input("Enter password: ")

query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

**Secure Code:**

```python
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

username = input("Enter username: ")
password = input("Enter password: ")

query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

### Input Validation

Always validate user input to ensure it meets expected criteria.

**Vulnerable Code:**

```javascript
const userId = req.query.userId;

db.query(`SELECT * FROM users WHERE id = ${userId}`, (err, results) => {
  // Handle results
});
```

**Secure Code:**

```javascript
const userId = parseInt(req.query.userId);

if (isNaN(userId)) {
  res.status(400).send('Invalid user ID');
} else {
  db.query('SELECT * FROM users WHERE id = ?', [userId], (err, results) => {
    // Handle results
  });
}
```

### Detection and Monitoring

Regularly monitor your application for signs of SQL Injection attempts. Tools like intrusion detection systems (IDS) can help identify suspicious activity.

### Hardening Database Configurations

- **Least Privilege Principle**: Ensure that database users have the minimum permissions necessary to perform their tasks.
- **Disable Unnecessary Features**: Disable features that are not required, such as stored procedures or triggers.
- **Use Strong Passwords**: Enforce strong password policies for database users.

### Real-World Lab Exercises

To practice and understand SQL Injection, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about SQL Injection and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

---
<!-- nav -->
[[API Security/11-SQL Injection/04-SQL Injection/02-SQL Injection Overview|SQL Injection Overview]] | [[API Security/11-SQL Injection/04-SQL Injection/00-Overview|Overview]] | [[04-Understanding the Attack Vector|Understanding the Attack Vector]]
