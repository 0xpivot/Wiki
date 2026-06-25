---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Types of Security Attacks Part 1: SQL Injection and Data Manipulation

### Introduction to SQL Injection

SQL Injection is a type of attack where an attacker manipulates a SQL query to gain unauthorized access to sensitive data or perform actions that compromise the integrity of the database. This attack exploits vulnerabilities in the way applications handle user input, particularly when constructing SQL queries dynamically.

#### What is SQL Injection?

SQL Injection occurs when an attacker inserts or "injects" malicious SQL statements into a query that is executed by the database. This can lead to unauthorized access to data, manipulation of data, or even complete control over the database.

#### Why Does SQL Injection Matter?

SQL Injection attacks are significant because they can result in severe consequences, including:

- **Data Theft**: Attackers can extract sensitive information such as credit card numbers, personal identification details, and confidential business data.
- **Data Manipulation**: Attackers can alter data within the database, leading to incorrect business decisions or financial losses.
- **Denial of Service**: By deleting or corrupting data, attackers can render the application unusable, causing downtime and loss of revenue.
- **Unauthorized Access**: Attackers can gain elevated privileges within the database, potentially leading to further exploitation of the system.

#### How Does SQL Injection Work?

To understand how SQL Injection works, let's consider a simple example. Suppose we have a login form where a user enters their username and password. The application constructs a SQL query to check if the provided credentials match those stored in the database.

```sql
SELECT * FROM users WHERE username = 'user_input' AND password = 'password_input';
```

If the application does not properly sanitize the user input, an attacker could inject malicious SQL code. For instance, if the attacker inputs `username` as `' OR '1'='1` and leaves the password field empty, the resulting SQL query would look like this:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
```

This query will return all rows from the `users` table because the condition `'1'='1'` is always true. Thus, the attacker bypasses authentication and gains access to the system.

### Real-World Example: Heartland Payment Systems Breach (2008)

One of the most notable SQL Injection attacks occurred in 2008 when Heartland Payment Systems, a major payment processor, was breached. The attackers used a SQL Injection attack to gain access to the internal company network.

#### Background of the Incident

Heartland Payment Systems processed millions of credit card transactions daily. In December 2008, the company reported a massive data breach affecting approximately 130 million credit and debit card accounts. The breach was attributed to a SQL Injection attack that allowed hackers to inject malware into the company's systems.

#### Technical Details

The attackers exploited a vulnerability in a web form on the company's website. They injected malicious SQL code through the web form, which allowed them to execute arbitrary commands on the server. This gave them access to the internal network, where they could move laterally and steal sensitive data.

#### Impact

The breach had far-reaching consequences:

- **Financial Loss**: Heartland faced significant financial losses due to the breach, including fines and legal settlements.
- **Reputation Damage**: The company's reputation suffered, leading to a loss of trust among its clients and partners.
- **Widespread Impact**: All businesses that partnered with Heartland to process their payments were affected. This included banks, retailers, and other financial institutions.

### How to Prevent / Defend Against SQL Injection

#### Detection

Detecting SQL Injection attacks involves monitoring for suspicious activity and using tools to identify potential vulnerabilities. Some methods include:

- **Web Application Firewalls (WAF)**: WAFs can help detect and block SQL Injection attempts by analyzing incoming traffic.
- **Intrusion Detection Systems (IDS)**: IDS can monitor network traffic and alert administrators to potential SQL Injection attacks.
- **Logging and Monitoring**: Regularly reviewing logs can help identify patterns indicative of SQL Injection attempts.

#### Prevention

Preventing SQL Injection attacks requires a combination of secure coding practices, proper input validation, and the use of security mechanisms.

##### Secure Coding Practices

1. **Parameterized Queries**: Use parameterized queries to ensure that user input is treated as data rather than executable code.
   
   ```sql
   SELECT * FROM users WHERE username = ? AND password = ?;
   ```

2. **Stored Procedures**: Use stored procedures to encapsulate SQL logic and reduce the risk of injection.

##### Input Validation

Validate all user input to ensure it meets expected formats and constraints. This includes checking for length, format, and type of input.

##### Example: Vulnerable vs. Secure Code

**Vulnerable Code**

```php
$username = $_POST['username'];
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
$result = mysqli_query($connection, $query);
```

**Secure Code**

```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $connection->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
```

#### Hardening Measures

1. **Least Privilege Principle**: Ensure that database users have the minimum necessary permissions to perform their tasks.
2. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.
3. **Patch Management**: Keep all software up to date with the latest security patches.

### Conclusion

SQL Injection attacks pose a significant threat to the security and integrity of web applications. Understanding how these attacks work, recognizing real-world examples, and implementing robust preventive measures are crucial steps in safeguarding against such threats.

### Practice Labs

For hands-on experience with SQL Injection and other security essentials, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs covering various types of SQL Injection attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of vulnerabilities, including SQL Injection, for educational purposes.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

By engaging with these resources, you can deepen your understanding and practical skills in defending against SQL Injection and other security threats.

---
<!-- nav -->
[[13-Social Engineering Attacks|Social Engineering Attacks]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[15-Types of Security Attacks Part 1|Types of Security Attacks Part 1]]
