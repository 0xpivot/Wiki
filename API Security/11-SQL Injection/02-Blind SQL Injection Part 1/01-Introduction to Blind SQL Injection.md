---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Introduction to Blind SQL Injection

Blind SQL Injection is a type of SQL Injection attack where an attacker can manipulate a SQL query to extract data from a database, even though the application does not return any explicit error messages or data. This makes the attack more challenging but also more stealthy. In this section, we will delve deep into the mechanics of blind SQL injection, its implications, and how to defend against it.

### What is SQL Injection?

SQL Injection is a technique used by attackers to inject malicious SQL statements into an application’s input fields. These injected SQL statements can then be executed by the backend database, leading to unauthorized access, data theft, or even complete control of the database.

#### Why Does SQL Injection Matter?

SQL Injection is one of the most critical vulnerabilities in web applications. According to the OWASP Top Ten Project, SQL Injection ranks among the top vulnerabilities due to its potential to cause significant damage. Real-world examples include:

- **CVE-2018-1268**: A SQL Injection vulnerability was discovered in the WordPress REST API, allowing attackers to execute arbitrary SQL commands.
- **Equifax Data Breach (2017)**: A SQL Injection vulnerability led to the exposure of sensitive personal information of approximately 143 million people.

### Types of SQL Injection

There are two primary types of SQL Injection:

1. **Error-Based SQL Injection**: The application returns error messages that reveal details about the underlying database structure.
2. **Blind SQL Injection**: The application does not return any error messages, making it harder to detect and exploit.

In this chapter, we will focus on blind SQL Injection.

### How Blind SQL Injection Works

Blind SQL Injection occurs when an attacker can manipulate a SQL query to extract data from a database, even though the application does not return any explicit error messages or data. The attacker relies on conditional responses from the server to infer the data.

#### Example Scenario

Consider an API endpoint `/api/users` that accepts a `username` parameter. The backend SQL query might look like this:

```sql
SELECT * FROM users WHERE username = 'input_username';
```

If the application is vulnerable to blind SQL Injection, an attacker could inject a malicious payload into the `username` parameter to extract data.

### Steps to Exploit Blind SQL Injection

1. **Identify Vulnerable Parameters**: Determine which parameters are vulnerable to SQL Injection.
2. **Craft Malicious Payloads**: Create payloads that can be injected into the vulnerable parameters.
3. **Observe Conditional Responses**: Analyze the server’s responses to infer the data.

#### Identifying Vulnerable Parameters

To identify vulnerable parameters, an attacker would typically perform a series of tests. For example, using the `username` parameter:

```http
GET /api/users?username=admin' OR '1'='1 HTTP/1.1
Host: example.com
```

If the application returns a different response compared to a normal request, it may indicate a vulnerability.

#### Crafting Malicious Payloads

An attacker can craft payloads to extract data. For instance, to determine if a specific condition is true:

```http
GET /api/users?username=admin' AND (SELECT 1 FROM users WHERE username='admin')='1 HTTP/1.1
Host: example.com
```

This payload checks if the user `admin` exists in the database.

#### Observing Conditional Responses

The attacker observes the server’s responses to infer the data. For example, if the server responds differently when the condition is true, the attacker can deduce the existence of the user.

### Real-World Example: CVE-2018-1268

**CVE-2018-1268** is a SQL Injection vulnerability in the WordPress REST API. An attacker could inject malicious SQL queries through the API endpoints, potentially gaining unauthorized access to sensitive data.

#### Vulnerable Code

The vulnerable code in the WordPress REST API might look something like this:

```php
function get_user_data($username) {
    global $wpdb;
    $query = "SELECT * FROM wp_users WHERE username = '$username'";
    return $wpdb->get_results($query);
}
```

#### Exploitation

An attacker could inject a payload like:

```http
GET /wp-json/wp/v2/users?username=admin' UNION SELECT password FROM wp_users WHERE username='admin HTTP/1.1
Host: example.com
```

This would allow the attacker to extract the password of the `admin` user.

### How to Prevent / Defend Against Blind SQL Injection

#### Detection

To detect SQL Injection vulnerabilities, you can use automated tools such as:

- **OWASP ZAP**: A free, open-source tool for finding security vulnerabilities in web applications.
- **Burp Suite**: A comprehensive toolkit for web application security testing.

#### Prevention

1. **Use Prepared Statements**: Prepared statements ensure that user inputs are treated as data rather than executable code.
   
   ```php
   function get_user_data($username) {
       global $wpdb;
       $query = $wpdb->prepare("SELECT * FROM wp_users WHERE username = %s", $username);
       return $wpdb->get_results($query);
   }
   ```

2. **Input Validation**: Validate and sanitize all user inputs to ensure they meet expected formats and lengths.

3. **Least Privilege Principle**: Ensure that the database user has the minimum necessary privileges to perform its tasks.

4. **Web Application Firewalls (WAF)**: Implement WAFs to filter out malicious traffic.

#### Secure Coding Practices

Here is a comparison of vulnerable and secure code:

**Vulnerable Code:**

```php
function get_user_data($username) {
    global $wpdb;
    $query = "SELECT * FROM wp_users WHERE username = '$username'";
    return $wpdb->get_results($query);
}
```

**Secure Code:**

```php
function get_user_data($username) {
    global $wpdb;
    $query = $wpdb->prepare("SELECT * FROM wp_users WHERE username = %s", $username);
    return $wpdb->get_results($query);
}
```

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and practice SQL Injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various security attacks, including SQL Injection.

### Conclusion

Blind SQL Injection is a sophisticated form of SQL Injection that requires careful analysis and exploitation techniques. By understanding the mechanics of blind SQL Injection and implementing robust defensive measures, developers can significantly reduce the risk of such attacks. Always validate and sanitize user inputs, use prepared statements, and follow secure coding practices to protect your applications from SQL Injection vulnerabilities.

---
<!-- nav -->
[[API Security/11-SQL Injection/02-Blind SQL Injection Part 1/00-Overview|Overview]] | [[API Security/11-SQL Injection/02-Blind SQL Injection Part 1/02-Introduction to SQL Injection|Introduction to SQL Injection]]
