---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Identifying Vulnerable Input Fields

The first step in performing a SQL Injection attack is to identify the input fields that are vulnerable to SQL Injection. Common vulnerable points include login forms, search boxes, and other user-input fields.

### Example: Login Form

Let's consider a login form with the following structure:

```html
<form action="login.php" method="POST">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Login</button>
</form>
```

When the form is submitted, the `login.php` script processes the input and constructs a SQL query. If the input is not properly validated, it can be exploited for SQL Injection.

### Crafting SQL Injection Payloads

To test for SQL Injection, we can inject a payload that causes the SQL query to behave differently. For example, we can inject a single quote (`'`) to see if it causes an error.

#### Example Payload

Inject the following payload into the username field:

```
admin'
```

If the application is vulnerable to SQL Injection, this payload will cause the SQL query to fail, resulting in an error message or unexpected behavior.

### Detecting SQL Injection Vulnerabilities

To detect SQL Injection vulnerabilities, we can use automated tools such as SQLMap or manually craft payloads to observe the application's behavior.

#### Using SQLMap

SQLMap is a powerful tool for automating the process of detecting and exploiting SQL Injection vulnerabilities. To use SQLMap, run the following command:

```bash
sqlmap -u "http://example.com/login.php?username=admin&password=password" --data="username=admin'&password=password"
```

This command tells SQLMap to test the specified URL and data for SQL Injection vulnerabilities.

### Manual Testing

Manual testing involves injecting various payloads and observing the application's response. Some common payloads include:

- `admin' OR '1'='1`
- `admin' UNION SELECT NULL--`
- `admin' AND 1=0 UNION SELECT username, password FROM users--`

By injecting these payloads, we can determine if the application is vulnerable to SQL Injection.

---
<!-- nav -->
[[07-How to Prevent  Defend Against SQL Injection|How to Prevent  Defend Against SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/11-Lab 10 SQL injection attack listing the database contents on Oracle/00-Overview|Overview]] | [[09-Manual SQL Injection Attack|Manual SQL Injection Attack]]
