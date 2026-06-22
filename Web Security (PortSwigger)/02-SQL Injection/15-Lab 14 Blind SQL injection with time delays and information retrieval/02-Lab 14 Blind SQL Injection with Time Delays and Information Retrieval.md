---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Lab 14: Blind SQL Injection with Time Delays and Information Retrieval

In this lab, we will cover a Blind SQL Injection vulnerability that uses time delays to retrieve information from the database. The application uses a tracking cookie for analytics and performs an SQL query containing the value of the submitted cookie. The results of the SQL query are not returned, and the application does not respond differently based on whether the query returns any rows or causes any error.

### Setup

To access the exercise, follow these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security)
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Click on Academy.
5. Select the learning path.
6. Select SQL Injection.
7. Select Blind SQL Injection.
8. Access lab number 14 titled "Blind SQL Injection with Time Delays and Information Retrieval."

### Vulnerable Parameter

The vulnerable parameter in this lab is the tracking cookie. The application uses the value of the submitted cookie in an SQL query. Since the results of the SQL query are not returned, and the application does not respond differently based on the query results, we must use Blind SQL Injection techniques to extract information.

### Exploitation Steps

To exploit this vulnerability, we will use time-based Blind SQL Injection. We will inject SQL code that causes a time delay if certain conditions are met. By observing the delay, we can infer the success of our injection.

#### Step 1: Identify the Vulnerable Parameter

First, identify the vulnerable parameter. In this case, it is the tracking cookie. You can test this by submitting different values for the cookie and observing the application's behavior.

#### Step 2: Craft the Injection Query

Next, craft the injection query to cause a time delay if certain conditions are met. For example, you can check if the first character of the MySQL version is '5':

```plaintext
' OR IF(SUBSTRING(@@version,1,1)='5', SLEEP(5), 0) --
```

This query checks if the first character of the MySQL version is '5'. If it is, the query will cause a 5-second delay.

#### Step 3: Observe the Delay

Submit the crafted injection query and observe the delay. If the delay is observed, it indicates that the condition was met. You can use this technique to extract information from the database.

### Full Example

Let's walk through a full example of exploiting this vulnerability.

#### Initial Request

First, send an initial request to the application with a normal cookie value:

```http
GET / HTTP/1.1
Host: vulnerable-app.com
Cookie: trackingid=normal_value
```

#### Injected Request

Next, send a request with the injected cookie value:

```http
GET / HTTP/1.1
Host: vulnerable-app.com
Cookie: trackingid=' OR IF(SUBSTRING(@@version,1,1)='5', SLEEP(5), 0) --
```

#### Response

Observe the response time. If there is a 5-second delay, it indicates that the condition was met.

### Detection and Prevention

#### How to Detect SQL Injection

To detect SQL Injection vulnerabilities, you can use automated tools such as SQLMap, Burp Suite, or OWASP ZAP. These tools can automatically test for SQL Injection vulnerabilities and provide detailed reports.

#### How to Prevent SQL Injection

To prevent SQL Injection, follow these best practices:

1. **Use Prepared Statements**: Prepared statements ensure that user input is treated as data rather than executable code.
2. **Input Validation**: Validate all user input to ensure it meets expected formats and constraints.
3. **Least Privilege Principle**: Ensure that the application database user has the least privilege necessary to perform its tasks.
4. **Error Handling**: Implement proper error handling to avoid revealing sensitive information about the database structure.

### Secure Code Fix

Here is an example of a vulnerable code snippet and its secure counterpart:

#### Vulnerable Code

```php
$tracking_id = $_COOKIE['trackingid'];
$query = "SELECT * FROM analytics WHERE tracking_id = '$tracking_id'";
$result = mysqli_query($conn, $query);
```

#### Secure Code

```php
$tracking_id = $_COOKIE['trackingid'];
$stmt = $conn->prepare("SELECT * FROM analytics WHERE tracking_id = ?");
$stmt->bind_param("s", $tracking_id);
$stmt->execute();
$result = $stmt->get_result();
```

### Conclusion

Blind SQL Injection with time delays is a powerful technique that allows attackers to extract information from a database even when the application does not return the results of the SQL query. By understanding how this vulnerability works and how to detect and prevent it, you can protect your applications from such attacks.

### Practice Labs

For hands-on practice with SQL Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice SQL Injection techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By completing these labs, you can gain practical experience in identifying and exploiting SQL Injection vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/01-Introduction to SQL Injection|Introduction to SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/15-Lab 14 Blind SQL injection with time delays and information retrieval/00-Overview|Overview]] | [[03-Blind SQL Injection with Time Delays|Blind SQL Injection with Time Delays]]
