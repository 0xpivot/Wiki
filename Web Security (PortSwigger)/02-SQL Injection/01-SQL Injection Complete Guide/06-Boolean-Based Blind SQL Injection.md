---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Boolean-Based Blind SQL Injection

### What is Boolean-Based Blind SQL Injection?

Boolean-based blind SQL injection is a type of SQL injection attack where the attacker can infer information from the database by observing the behavior of the application based on the truth value of the injected SQL conditions. This technique is used when the application does not return any explicit data from the database but instead provides indirect feedback through the application's response.

#### Why Does It Matter?

Understanding boolean-based blind SQL injection is crucial because it allows attackers to extract sensitive information from a database even when direct data retrieval is not possible. This type of attack can lead to unauthorized access to confidential data, which can result in significant financial and reputational damage.

#### How Does It Work Under the Hood?

The core idea behind boolean-based blind SQL injection is to inject SQL conditions that evaluate to either `TRUE` or `FALSE`. By analyzing the application's response to these conditions, the attacker can determine whether the injected condition was true or false. This process is repeated iteratively to extract data bit by bit.

### Steps to Exploit Boolean-Based Blind SQL Injection

1. **Identify the Vulnerable Parameter**: Find a parameter in the application that is susceptible to SQL injection.
2. **Inject a False Condition**: Submit a SQL condition that evaluates to `FALSE` and observe the response.
3. **Inject a True Condition**: Submit a SQL condition that evaluates to `TRUE` and observe the response.
4. **Compare Responses**: Compare the responses from the false and true conditions to understand the application's behavior.
5. **Iterate to Extract Data**: Use conditional statements to ask the database a series of true/false questions and monitor the responses to extract data.

#### Example

Consider an application that takes a user ID as input and returns the corresponding username:

```http
GET /profile?userid=1 HTTP/1.1
Host: example.com
```

To check for boolean-based blind SQL injection, we can inject a false condition:

```http
GET /profile?userid=1 AND 1=2 HTTP/1.1
Host: example.com
```

If the application responds differently compared to the original request, it indicates a potential vulnerability.

Next, inject a true condition:

```http
GET /profile?userid=1 AND 1=1 HTTP/1.1
Host: example.com
```

By comparing the responses, we can determine if the application is vulnerable to boolean-based blind SQL injection.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the SQL injection vulnerability in the Joomla CMS (CVE-2017-8917). This vulnerability allowed attackers to inject malicious SQL queries, leading to unauthorized data extraction.

Another example is the SQL injection vulnerability in the WordPress plugin WP Event Manager (CVE-2018-16897). This vulnerability allowed attackers to inject SQL queries and potentially gain administrative access to the site.

### How to Prevent / Defend Against Boolean-Based Blind SQL Injection

#### Detection

- **Web Application Firewalls (WAF)**: Implement WAFs that can detect and block SQL injection attempts.
- **Intrusion Detection Systems (IDS)**: Use IDS to monitor network traffic for suspicious patterns indicative of SQL injection attacks.

#### Prevention

- **Parameterized Queries**: Use parameterized queries to ensure that user inputs are treated as data rather than executable code.
- **Stored Procedures**: Utilize stored procedures to encapsulate SQL logic and reduce the risk of injection.
- **Input Validation**: Validate and sanitize all user inputs to prevent malicious SQL queries from being executed.

#### Secure Coding Fixes

**Vulnerable Code Example**:

```php
$userid = $_GET['userid'];
$query = "SELECT * FROM users WHERE id = $userid";
$result = mysqli_query($conn, $query);
```

**Secure Code Example**:

```php
$userid = $_GET['userid'];
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $userid);
$stmt->execute();
$result = $stmt->get_result();
```

### Time-Based Blind SQL Injection

### What is Time-Based Blind SQL Injection?

Time-based blind SQL injection is another type of SQL injection attack where the attacker exploits the time delay caused by the execution of SQL queries to infer information from the database. This technique is particularly useful when the application does not provide any direct feedback about the success or failure of the SQL injection attempt.

#### Why Does It Matter?

Time-based blind SQL injection is significant because it allows attackers to extract data from a database even when the application does not return any explicit data. This type of attack can lead to unauthorized access to sensitive information, which can have severe consequences.

#### How Does It Work Under the Hood?

The core idea behind time-based blind SQL injection is to inject SQL conditions that cause a delay in the execution of the query. By measuring the time taken for the query to execute, the attacker can determine whether the injected condition was true or false. This process is repeated iteratively to extract data bit by bit.

### Steps to Exploit Time-Based Blind SQL Injection

1. **Identify the Vulnerable Parameter**: Find a parameter in the application that is susceptible to SQL injection.
2. **Inject a Delay Condition**: Submit a SQL condition that causes a delay in the execution of the query.
3. **Measure the Response Time**: Measure the time taken for the query to execute and compare it to the normal response time.
4. **Iterate to Extract Data**: Use conditional statements to ask the database a series of true/false questions and measure the response times to extract data.

#### Example

Consider an application that takes a user ID as input and returns the corresponding username:

```http
GET /profile?userid=1 HTTP/1.1
Host: example.com
```

To check for time-based blind SQL injection, we can inject a delay condition:

```http
GET /profile?userid=1 AND SLEEP(5) HTTP/1.1
Host: example.com
```

If the application takes significantly longer to respond, it indicates a potential vulnerability.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the SQL injection vulnerability in the Drupal CMS (CVE-2018-7600). This vulnerability allowed attackers to inject malicious SQL queries and potentially cause a delay in the execution of the query.

Another example is the SQL injection vulnerability in the Magento e-commerce platform (CVE-2018-7572). This vulnerability allowed attackers to inject SQL queries and potentially cause a delay in the execution of the query.

### How to Prevent / Defend Against Time-Based Blind SQL Injection

#### Detection

- **Web Application Firewalls (WAF)**: Implement WAFs that can detect and block SQL injection attempts.
- **Intrusion Detection Systems (IDS)**: Use IDS to monitor network traffic for suspicious patterns indicative of SQL injection attacks.

#### Prevention

- **Parameterized Queries**: Use parameterized queries to ensure that user inputs are treated as data rather than executable code.
- **Stored Procedures**: Utilize stored procedures to encapsulate SQL logic and reduce the risk of injection.
- **Input Validation**: Validate and sanitize all user inputs to prevent malicious SQL queries from being executed.

#### Secure Coding Fixes

**Vulnerable Code Example**:

```php
$userid = $_GET['userid'];
$query = "SELECT * FROM users WHERE id = $userid";
$result = mysqli_query($conn, $query);
```

**Secure Code Example**:

```php
$userid = $_GET['userid'];
$stmt = $conn->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $userid);
$stmt->execute();
$result = $stmt->get_result();
```

### Practice Labs

For hands-on practice with SQL injection, consider the following well-known labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on SQL injection, including both boolean-based and time-based blind SQL injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various types of SQL injection attacks.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning and testing web application security.

These labs provide a safe environment to practice and understand the mechanics of SQL injection attacks and defenses.

### Conclusion

Boolean-based and time-based blind SQL injection are powerful techniques that allow attackers to extract sensitive information from databases even when the application does not provide direct feedback. Understanding these techniques is crucial for both attackers and defenders. By implementing secure coding practices, using parameterized queries, and validating user inputs, developers can significantly reduce the risk of SQL injection attacks. Additionally, using tools like WAFs and IDS can help detect and prevent such attacks in real-world scenarios.

---
<!-- nav -->
[[05-Black Box Testing vs White Box Testing vs Gray Box Testing|Black Box Testing vs White Box Testing vs Gray Box Testing]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[07-Boolean-Based SQL Injection|Boolean-Based SQL Injection]]
