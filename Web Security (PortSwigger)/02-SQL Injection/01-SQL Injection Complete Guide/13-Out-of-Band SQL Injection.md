---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Out-of-Band SQL Injection

### What is Out-of-Band SQL Injection?

Out-of-band SQL injection is a sophisticated form of SQL injection where the attacker triggers a network connection to a system they control. This technique is typically used when traditional SQL injection methods are not feasible due to lack of direct feedback or when the application does not allow for time-based attacks.

### Why Use Out-of-Band SQL Injection?

Out-of-band SQL injection is particularly useful when the attacker cannot receive immediate feedback from the application. By leveraging network connections, the attacker can confirm whether the injected SQL query was executed successfully.

### How Does Out-of-Band SQL Injection Work?

In out-of-band SQL injection, the attacker injects a SQL query that causes the database to initiate a network connection to a server controlled by the attacker. Commonly used protocols include DNS and HTTP. The attacker can then monitor the server to confirm if the query was executed.

#### Example Scenario

Consider a scenario where an attacker wants to extract the value of a specific column from a database table. The attacker can inject a query that causes the database to perform a DNS lookup to a domain controlled by the attacker.

```sql
SELECT * FROM users WHERE username = 'admin' AND (SELECT NULL FROM (SELECT 1 INTO OUTFILE '/tmp/log.txt') x);
```

This query will cause the database to write a log entry to a file, which can be monitored by the attacker.

### Real-World Example

A real-world example of out-of-band SQL injection occurred in the CVE-2021-27102 vulnerability in Oracle Database. An attacker could inject a query that caused the database to perform a DNS lookup to a domain controlled by the attacker, thereby confirming the existence of the query.

### How to Exploit Out-of-Band SQL Injection

To exploit out-of-band SQL injection, the attacker needs to inject a query that triggers a network connection. Here is an example using DNS:

1. **Generate a Unique Domain**: Use a tool like Burp Collaborator to generate a unique domain.
2. **Inject the Query**: Inject a query that causes the database to perform a DNS lookup to the generated domain.
3. **Monitor the Domain**: Monitor the domain to confirm if the query was executed.

#### Example Code

```sql
SELECT * FROM users WHERE username = 'admin' AND (SELECT NULL FROM (SELECT 1 INTO OUTFILE '/tmp/log.txt') x);
```

### How to Prevent / Defend Against Out-of-Band SQL Injection

#### Detection

To detect out-of-band SQL injection, monitor network traffic and DNS requests. Any unexpected DNS lookups or network connections should be investigated.

#### Prevention

1. **Disable Unnecessary Features**: Disable features in the database that allow for out-of-band network connections.
2. **Network Segmentation**: Segment the network to prevent the database from initiating external connections.
3. **Firewall Rules**: Implement firewall rules to block outgoing connections from the database server.
4. **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
5. **Use Prepared Statements**: Use prepared statements to ensure that user input is treated as data rather than executable code.

#### Secure Coding Fix

Here is an example of a vulnerable code and its secure counterpart:

**Vulnerable Code:**

```php
$username = $_GET['username'];
$query = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($conn, $query);
```

**Secure Code:**

```php
$username = $_GET['username'];
$stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();
```

### Summary

Out-of-band SQL injection is a sophisticated attack technique that leverages network connections to confirm the execution of injected SQL queries. To defend against this attack, disable unnecessary features, segment the network, implement firewall rules, validate inputs, and use prepared statements.

### Practice Labs

For hands-on experience with SQL injection, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on various types of SQL injection attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of SQL injection.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning and testing web application security.
- **WebGoat**: An interactive training application designed to teach web application security.

By practicing in these environments, you can gain a deeper understanding of SQL injection techniques and how to defend against them.

---
<!-- nav -->
[[12-Mapping the Application An Underrated but Critical Step|Mapping the Application An Underrated but Critical Step]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[14-Parameterized Queries and Prepared Statements|Parameterized Queries and Prepared Statements]]
