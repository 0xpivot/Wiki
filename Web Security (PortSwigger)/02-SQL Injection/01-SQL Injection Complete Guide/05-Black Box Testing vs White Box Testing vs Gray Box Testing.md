---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Black Box Testing vs White Box Testing vs Gray Box Testing

When discussing the methodology of identifying SQL injection vulnerabilities, it's essential to understand the different types of testing approaches available. These methodologies can be broadly categorized into three types: black box testing, white box testing, and gray box testing. Each approach has its own advantages and disadvantages, and understanding them will help you choose the most appropriate method for your specific situation.

### Black Box Testing

Black box testing is a type of testing where the tester has minimal knowledge about the internal workings of the system. In the context of web applications, this means that the tester is provided with only the URL of the application and the scope of the engagement. This approach closely mirrors the actions of an external attacker who has no prior knowledge of the application's architecture or source code.

#### What is Black Box Testing?

In black box testing, the tester interacts with the application through its user interface, input fields, and APIs. The goal is to identify vulnerabilities by observing the behavior of the application in response to various inputs. This method is particularly useful for simulating real-world attacks, as attackers typically have no access to the source code or detailed documentation of the target application.

#### Why Use Black Box Testing?

Black box testing is valuable because it provides a realistic simulation of an external attacker's capabilities. By limiting the tester's knowledge to only the publicly accessible parts of the application, this method helps identify vulnerabilities that could be exploited by malicious actors. Additionally, black box testing is often used in penetration testing engagements where the client wants to assess the security posture of their application from an outsider's perspective.

#### How Does Black Box Testing Work?

The process of black box testing involves systematically probing the application with various inputs to observe its behavior. For example, consider a login form where the username and password are submitted via an HTTP POST request:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=12345
```

A black box tester might try injecting SQL payloads into the `username` field to see if the application is vulnerable to SQL injection. For instance, the tester might send the following request:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=' OR '1'='1&password=12345
```

If the application is vulnerable, it might respond with a successful login, indicating that the SQL injection payload was executed.

#### Real-World Example: CVE-2021-3129

CVE-2021-3129 is a real-world example of a SQL injection vulnerability found in the Joomla CMS. An attacker could exploit this vulnerability by sending a specially crafted SQL query through the search functionality of the Joomla site. This allowed the attacker to execute arbitrary SQL commands, potentially leading to unauthorized data access or modification.

#### How to Prevent / Defend Against Black Box SQL Injection

To prevent SQL injection vulnerabilities, developers should follow secure coding practices such as using parameterized queries or prepared statements. Here’s an example of how to securely handle user input in a PHP application:

**Vulnerable Code:**
```php
$username = $_POST['username'];
$password = $_POST['password'];

$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
$result = mysqli_query($conn, $query);
```

**Secure Code:**
```php
$username = $_POST['username'];
$password = $_POST['password'];

$stmt = $conn->prepare("SELECT * FROM users WHERE username=? AND password=?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
$result = $stmt->get_result();
```

By using prepared statements, the SQL query is precompiled and the parameters are safely escaped, preventing SQL injection attacks.

### White Box Testing

White box testing, also known as clear box testing, is a testing method where the tester has full access to the internal workings of the system, including the source code. This approach allows the tester to thoroughly examine the application's logic, data flow, and control structures.

#### What is White Box Testing?

In white box testing, the tester is provided with comprehensive details about the application, including the source code, database schema, and configuration files. This level of access enables the tester to perform a more thorough analysis of the application's security posture.

#### Why Use White Box Testing?

White box testing is valuable because it allows testers to identify vulnerabilities that may not be apparent through black box testing alone. By examining the source code, testers can uncover logical errors, insecure coding practices, and potential attack vectors that could be exploited by attackers.

#### How Does White Box Testing Work?

The process of white box testing involves reviewing the source code line by line to identify potential security issues. For example, consider a function in a PHP application that handles user input:

**Vulnerable Code:**
```php
function getUserData($id) {
    $query = "SELECT * FROM users WHERE id=$id";
    $result = mysqli_query($conn, $query);
    return $result;
}
```

A white box tester would immediately recognize that this function is vulnerable to SQL injection because the `$id` variable is directly concatenated into the SQL query without proper sanitization.

#### Real-World Example: CVE-2-2021-26855

CVE-2021-26855 is a real-world example of a SQL injection vulnerability found in the WordPress REST API. An attacker could exploit this vulnerability by sending a specially crafted request to the `/wp-json/wp/v2/users` endpoint, allowing them to execute arbitrary SQL commands and potentially gain unauthorized access to sensitive data.

#### How to Prevent / Defend Against White Box SQL Injection

To prevent SQL injection vulnerabilities, developers should follow secure coding practices such as using parameterized queries or prepared statements. Here’s an example of how to securely handle user input in a PHP application:

**Vulnerable Code:**
```php
function getUserData($id) {
    $query = "SELECT * FROM users WHERE id=$id";
    $result = mysqli_query($conn, $query);
    return $result;
}
```

**Secure Code:**
```php
function getUserData($id) {
    $stmt = $conn->prepare("SELECT * FROM users WHERE id=?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    return $result;
}
```

By using prepared statements, the SQL query is precompiled and the parameters are safely escaped, preventing SQL injection attacks.

### Gray Box Testing

Gray box testing is a hybrid approach that combines elements of both black box and white box testing. In gray box testing, the tester is provided with limited information and access to the system, such as partial source code or some documentation, but not full access to the entire system.

#### What is Gray Box Testing?

In gray box testing, the tester is given some information about the system, such as the URL of the application and some accounts to the application, but not the full source code or detailed documentation. This approach provides a balance between the realism of black box testing and the thoroughness of white box testing.

#### Why Use Gray Box Testing?

Gray box testing is valuable because it provides a more realistic simulation of an attacker who has some insider knowledge but is still limited in their access. This approach can help identify vulnerabilities that might not be caught through purely black box or white box testing.

#### How Does Gray Box Testing Work?

The process of gray box testing involves using the limited information provided to the tester to probe the application for vulnerabilities. For example, consider a scenario where the tester is given a username and password to log into the application. The tester can use this account to explore the application and identify potential vulnerabilities.

#### Real-World Example: CVE-2021-3129

CVE-2021-3129 is a real-world example of a SQL injection vulnerability found in the Joomla CMS. An attacker could exploit this vulnerability by sending a specially crafted SQL query through the search functionality of the Joomla site. This allowed the attacker to execute arbitrary SQL commands, potentially leading to unauthorized data access or modification.

#### How to Prevent / Defend Against Gray Box SQL Injection

To prevent SQL injection vulnerabilities, developers should follow secure coding practices such as using parameterized queries or prepared statements. Here’s an example of how to securely handle user input in a PHP application:

**Vulnerable Code:**
```php
function getUserData($id) {
    $query = "SELECT * FROM users WHERE id=$id";
    $result = mysqli_query($conn, $query);
    return $result;
}
```

**Secure Code:**
```php
function getUserData($id) {
    $stmt = $conn->prepare("SELECT * FROM users WHERE id=?");
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    return $result;
}
```

By using prepared statements, the SQL query is precompiled and the parameters are safely escaped, preventing SQL injection attacks.

### Conclusion

Understanding the different types of testing methodologies—black box, white box, and gray box—is crucial for effectively identifying and mitigating SQL injection vulnerabilities. Each approach has its own strengths and weaknesses, and choosing the right method depends on the specific context and goals of the testing engagement. By following secure coding practices and implementing robust defenses, developers can significantly reduce the risk of SQL injection attacks.

### Practice Labs

For hands-on experience with SQL injection vulnerabilities, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including SQL injection.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training purposes, which includes several SQL injection challenges.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, providing a safe environment to learn about web application security.

These labs provide practical scenarios where you can apply the concepts learned in this chapter and gain hands-on experience with identifying and mitigating SQL injection vulnerabilities.

---
<!-- nav -->
[[04-What is SQL Injection|What is SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/01-SQL Injection Complete Guide/00-Overview|Overview]] | [[06-Boolean-Based Blind SQL Injection|Boolean-Based Blind SQL Injection]]
