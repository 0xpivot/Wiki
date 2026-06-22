---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## How to Prevent / Defend Against SQL Injection

### Prevention Techniques

Preventing SQL Injection requires a combination of coding practices and security measures.

#### Secure Coding Practices

1. **Parameterized Queries**: Use parameterized queries to ensure that user input is treated as data rather than executable code.
2. **Stored Procedures**: Use stored procedures to encapsulate SQL logic and prevent direct execution of SQL statements.
3. **Input Validation**: Validate user input to ensure that it meets the expected format and constraints.

#### Example: Secure Code vs Vulnerable Code

##### Vulnerable Code

```php
$category = $_GET['category'];
$query = "SELECT * FROM products WHERE category = '$category'";
$result = mysqli_query($connection, $query);
```

##### Secure Code

```php
$category = $_GET['category'];
$stmt = $mysqli->prepare("SELECT * FROM products WHERE category = ?");
$stmt->bind_param("s", $category);
$stmt->execute();
$result = $stmt->get_result();
```

### Configuration Hardening

Hardening the database configuration can help mitigate the impact of SQL Injection attacks.

#### Disable Unnecessary Features

Disable unnecessary features and functions in the database to reduce the attack surface.

#### Least Privilege Principle

Ensure that the database user has the least privilege necessary to perform its tasks. Avoid using administrative accounts for regular operations.

### Detection and Monitoring

Regularly monitor the application and database for signs of SQL Injection attacks. Use tools like intrusion detection systems (IDS) and security information and event management (SIEM) systems to detect and respond to suspicious activity.

### Real-World Example: CVE-2021-22205

For the WPForms plugin, the vulnerability was detected through static analysis of the source code. The developers were able to patch the vulnerability by implementing parameterized queries and input validation.

---
<!-- nav -->
[[04-Constructing the UNION Query|Constructing the UNION Query]] | [[Web Security (PortSwigger)/02-SQL Injection/10-Lab 9 SQL injection attack listing the database contents on non Oracle databases/00-Overview|Overview]] | [[06-Identifying Vulnerable Fields|Identifying Vulnerable Fields]]
