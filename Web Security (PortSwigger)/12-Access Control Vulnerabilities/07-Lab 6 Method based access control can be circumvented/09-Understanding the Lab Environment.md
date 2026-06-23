---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Understanding the Lab Environment

In this lab, we will explore a scenario where access control is implemented based on the HTTP method of requests. The goal is to exploit a broken access control vulnerability to promote a regular user to an administrator.

### Setting Up the Lab

To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you don't already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the Learning Path.
6. Choose the Access Control module.
7. Go to Lab Number 6, titled "Method-Based Access Control can be circumvented."

### Logging In as Administrator

First, log in using the administrator credentials (`administrator`/`admin`). This will help you understand the functionality of the application, particularly how user promotion works.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
```

### Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=abc123; Path=/; HttpOnly

<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
</head>
<body>
    <h1>Welcome, Admin!</h1>
</body>
</html>
```

### Logging In as Regular User

Next, log in using the regular user credentials provided in the lab. This user will be the one you attempt to promote to an administrator.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=user&password=password
```

### Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=def456; Path=/; HttpOnly

<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
</head>
<body>
    <h1>Welcome, User!</h1>
</body>
</html>
```

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/08-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/10-Conclusion|Conclusion]]
