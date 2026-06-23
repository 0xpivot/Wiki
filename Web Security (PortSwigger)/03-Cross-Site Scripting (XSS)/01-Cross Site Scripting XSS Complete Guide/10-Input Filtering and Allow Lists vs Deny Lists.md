---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Input Filtering and Allow Lists vs Deny Lists

### Background Theory

When dealing with user input in web applications, one of the primary concerns is ensuring that the input does not contain malicious content that could lead to security vulnerabilities such as Cross-Site Scripting (XSS). One of the most effective ways to handle user input is through input validation and filtering. There are two main approaches to input filtering: allow lists (white lists) and deny lists (black lists).

#### Allow Lists (White Lists)

An allow list is a list of acceptable inputs. This approach is more secure because it explicitly defines what is allowed, thereby blocking everything else. For example, if a form field is designed to accept only numbers, an allow list would ensure that only numeric characters are accepted.

**Why Use Allow Lists?**
- **Security**: By defining what is allowed, you minimize the risk of unexpected input leading to security issues.
- **Predictability**: Developers can predict the types of inputs that will be processed, making it easier to handle and validate data.

**Example of Allow List Filtering**

Consider a simple form field that accepts only numeric input:

```python
def validate_input(input_value):
    if input_value.isdigit():
        return True
    return False

# Example usage
user_input = "1234"
if validate_input(user_input):
    print("Input is valid")
else:
    print("Input is invalid")
```

#### Deny Lists (Black Lists)

A deny list, on the other hand, is a list of unacceptable inputs. This approach is less secure because it is difficult to anticipate all possible malicious inputs. For example, if a form field is designed to block certain keywords, an attacker might find a way to bypass the filter by using different keywords or encoding techniques.

**Why Use Deny Lists?**
- **Flexibility**: In some scenarios, it might be easier to define what is not allowed rather than what is allowed.
- **Complexity**: Implementing a deny list can be simpler in terms of coding, but it is inherently less secure.

**Example of Deny List Filtering**

Consider a form field that blocks certain keywords:

```python
def validate_input(input_value):
    deny_list = ["script", "alert"]
    for keyword in deny_list:
        if keyword in input_value:
            return False
    return True

# Example usage
user_input = "<script>alert('XSS')</script>"
if validate_input(user_input):
    print("Input is valid")
else:
    print("Input is invalid")
```

### Defense in Depth

While allow lists are generally more secure, there may be situations where you are forced to use a deny list. In such cases, it is important to implement additional layers of defense to mitigate the risks associated with using a deny list.

#### Filtering Input on Arrival

Filtering input on arrival is a crucial step in defense in depth. This means validating and sanitizing user input as soon as it is received by the server. This helps prevent malicious input from reaching the application logic.

**Example of Filtering Input on Arrival**

Consider a web application that receives user input via a POST request:

```http
POST /submit HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=JohnDoe&password=secret
```

The server should validate and sanitize the input immediately upon receipt:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']

    # Validate and sanitize input
    if not username.isalnum():
        return "Invalid username", 400

    if not password.isalnum():
        return "Invalid password", 400

    # Process valid input
    return "Input is valid"

if __name__ == '__main__':
    app.run()
```

### Response Headers and Content Type

Another layer of defense is to use appropriate response headers to indicate the format of the responses. Two key headers are `Content-Type` and `X-Content-Type-Options`.

#### Content-Type Header

The `Content-Type` header specifies the media type of the resource being served. This helps the browser understand how to interpret the content.

**Example of Setting Content-Type Header**

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example Page</h1>
</body>
</html>
```

#### X-Content-Type-Options Header

The `X-Content-Type-Options` header prevents MIME-sniffing, which is a technique used by browsers to guess the content type of a resource. This can be exploited to bypass the `Content-Type` header.

**Example of Setting X-Content-Type-Options Header**

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
X-Content-Type-Options: nosniff

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example Page</h1>
</body>
</html>
```

### Content Security Policy (CSP)

Content Security Policy (CSP) is a browser-based security mechanism that restricts the resources that a page can load and restricts whether a page can be framed by other pages. CSP helps mitigate vulnerabilities like XSS and clickjacking.

#### How CSP Works

CSP works by setting a response header called `Content-Security-Policy`. This header contains directives that specify the sources from which resources can be loaded.

**Example of Setting CSP Header**

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; style-src 'self' https://trusted.cdn.com; img-src 'self' data:; frame-src 'none'

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example Page</h1>
</body>
</html>
```

### Real-World Examples

#### Recent Breaches and CVEs

One notable example of an XSS vulnerability is CVE-2021-31166, which affected the WordPress plugin "WP GDPR Compliance." This vulnerability allowed attackers to inject arbitrary JavaScript code into the site, potentially leading to data theft or other malicious activities.

**Example of Vulnerable Code**

```php
// Vulnerable code in WP GDPR Compliance plugin
echo $_GET['callback'] . '(' . json_encode($data) . ')';
```

**Secure Code Fix**

```php
// Secure code fix
$callback = filter_var($_GET['callback'], FILTER_SANITIZE_STRING);
echo $callback . '(' . json_encode($data) . ')';
```

### How to Prevent / Defend

#### Detection

To detect XSS vulnerabilities, you can use automated tools such as Burp Suite, OWASP ZAP, or commercial scanners like Acunetix. These tools can help identify potential injection points and test for vulnerabilities.

#### Prevention

1. **Use Allow Lists**: Always prefer allow lists over deny lists for input validation.
2. **Sanitize Input**: Sanitize user input to remove any potentially harmful content.
3. **Set Appropriate Headers**: Set `Content-Type` and `X-Content-Type-Options` headers to prevent MIME-sniffing attacks.
4. **Implement CSP**: Use Content Security Policy to restrict the sources from which resources can be loaded.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of code to understand the differences:

**Vulnerable Code**

```php
echo $_GET['callback'] . '(' . json_encode($data) . ')';
```

**Secure Code**

```php
$callback = filter_var($_GET['callback'], FILTER_SANITIZE_STRING);
echo $callback . '(' . json_encode($data) . ')';
```

### Hands-On Labs

For hands-on practice with XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security vulnerabilities, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By following these practices and using the provided tools and labs, you can effectively prevent and defend against XSS vulnerabilities in web applications.

---
<!-- nav -->
[[09-How to Prevent or Mitigate XSS Vulnerabilities|How to Prevent or Mitigate XSS Vulnerabilities]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/01-Cross Site Scripting XSS Complete Guide/00-Overview|Overview]] | [[11-Types of XSS Vulnerabilities|Types of XSS Vulnerabilities]]
