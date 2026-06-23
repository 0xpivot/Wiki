---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into a webpage viewed by other users. These scripts can steal sensitive data, perform actions as the user, or even take control of the user's session. XSS vulnerabilities arise due to the lack of proper input validation and output encoding mechanisms in web applications.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off the web server, usually in the form of an error message, search result, or any other response that includes data provided by the user. This type of XSS is often exploited through phishing attacks, where the attacker tricks the victim into clicking a malicious link.

2. **Stored XSS**: The injected script is permanently stored on the server, such as in a database, comment field, or message board. Every time the affected page is viewed, the malicious script is executed.

3. **DOM-based XSS**: The vulnerability exists in the client-side code rather than the server-side code. The script is executed based on the way the DOM (Document Object Model) is manipulated by JavaScript.

In this lab, we will focus on **Reflected XSS** into an HTML context with nothing encoded.

### Setting Up the Lab Environment

To access the lab, follow these steps:

1. Visit the URL `portswigger.net/web-security`.
2. Click on the sign-up button to create an account if you don't already have one.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select "All Labs".
6. Search for "cross-site scripting labs".
7. Choose "Lab Number One: Reflected XSS into HTML context with nothing encoded".

### Understanding the Vulnerability

The lab contains a simple reflected XSS vulnerability in the search functionality. The goal is to exploit this vulnerability to call the `alert` function. This means that the input provided by the user is reflected back into the HTML context without any encoding, making it susceptible to XSS attacks.

#### Example Scenario

Consider a web application with a search feature. When a user enters a search query, the application reflects this query back in the response. If the application does not properly encode the input, an attacker can inject a script tag (`<script>`) that executes arbitrary JavaScript code.

### Steps to Exploit the Vulnerability

1. **Identify the Input Field**: Locate the search input field in the application.
2. **Inject Malicious Script**: Enter a script tag that calls the `alert` function. For example:
    ```html
    <script>alert('XSS');</script>
    ```
3. **Submit the Input**: Submit the search query and observe the response.

#### Example Request and Response

Here is a complete example of the HTTP request and response:

```http
GET /search?q=<script>alert('XSS');</script> HTTP/1.1
Host: vulnerable-website.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Cookie: session_id=abc123
Connection: close
```

```http
HTTP/1.1 200 OK
Date: Mon, 10 Jan 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for "<script>alert('XSS');</script>"</h1>
    <p>No results found.</p>
</body>
</html>
```

Notice how the `<script>` tag is reflected back in the HTML response, leading to the execution of the `alert` function.

### Real-World Examples

#### Recent Breaches and CVEs

1. **CVE-2021-21972**: A reflected XSS vulnerability was found in the WordPress plugin "WPML Multilingual CMS". Attackers could inject malicious scripts via the search functionality, leading to unauthorized access and potential data theft.

2. **CVE-2020-14882**: A stored XSS vulnerability was discovered in the popular web forum software vBulletin. Attackers could inject malicious scripts into forum posts, which would execute whenever a user viewed the post.

These examples highlight the importance of proper input validation and output encoding to prevent XSS attacks.

### How to Prevent / Defend Against XSS

#### Detection

1. **Static Analysis Tools**: Use tools like SonarQube, Fortify, or Veracode to scan your codebase for potential XSS vulnerabilities.
2. **Dynamic Analysis Tools**: Employ tools like Burp Suite, OWASP ZAP, or Acunetix to test your application for runtime vulnerabilities.

#### Prevention

1. **Input Validation**: Ensure that all user inputs are validated against a strict set of rules. Use regular expressions to filter out potentially harmful characters.
2. **Output Encoding**: Encode all user inputs before reflecting them back in the HTML context. Use libraries like OWASP Java Encoder or Microsoft AntiXSS Library to perform encoding.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This helps mitigate the impact of XSS attacks.

#### Secure Coding Practices

Here is an example of how to securely handle user inputs in a web application:

**Vulnerable Code:**
```php
<?php
$search_query = $_GET['q'];
echo "<h1>Search Results for \"$search_query\"</h1>";
?>
```

**Secure Code:**
```php
<?php
$search_query = htmlspecialchars($_GET['q'], ENT_QUOTES, 'UTF-8');
echo "<h1>Search Results for \"$search_query\"</h1>";
?>
```

In the secure code, `htmlspecialchars` is used to encode special characters in the user input, preventing the injection of malicious scripts.

### Additional Considerations

#### Edge Cases

1. **Encoding Contexts**: Different contexts within HTML require different types of encoding. For example, attribute values should be encoded differently from content within tags.
2. **JavaScript Contexts**: When injecting user input into JavaScript, ensure that the input is properly escaped to prevent script injection.

#### Defense Mechanisms

1. **Web Application Firewalls (WAF)**: Deploy WAFs to filter out malicious requests before they reach your application.
2. **Security Headers**: Use security headers like `X-Content-Type-Options`, `X-XSS-Protection`, and `Strict-Transport-Security` to enhance the security of your web application.

### Conclusion

Understanding and mitigating XSS vulnerabilities is crucial for securing web applications. By following best practices in input validation, output encoding, and implementing security measures, developers can significantly reduce the risk of XSS attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs specifically designed to teach and test XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning and testing security concepts.

By engaging with these labs, you can gain practical experience in identifying and mitigating XSS vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/02-Lab 1 Reflected XSS into HTML context with nothing encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/02-Lab 1 Reflected XSS into HTML context with nothing encoded/02-Practice Questions & Answers|Practice Questions & Answers]]
