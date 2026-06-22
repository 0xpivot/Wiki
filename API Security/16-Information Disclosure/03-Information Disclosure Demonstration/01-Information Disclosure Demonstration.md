---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Information Disclosure Demonstration

### Introduction to Information Disclosure

Information disclosure vulnerabilities occur when an application unintentionally reveals sensitive data to unauthorized users. This can happen through various means such as error messages, debug logs, or even through improperly configured APIs. The goal of an attacker exploiting an information disclosure vulnerability is to obtain sensitive information that could be used for further attacks, such as authentication bypasses or privilege escalation.

### Understanding the Goal

The primary goal of an attacker when looking for information disclosure vulnerabilities is to extract sensitive data from the application. This can be achieved by:

1. **Stack Trace Errors**: These errors often reveal internal details of the application, such as file paths, function names, and sometimes even database queries.
2. **Sensitive Information in Responses**: This includes revealing passwords, API keys, session tokens, or other confidential data in the response payloads.

### Identifying Endpoints

To begin the process of identifying potential information disclosure vulnerabilities, we first need to enumerate the available endpoints of the API. This can be done using tools like `curl`, `HTTPie`, or automated scanners like Burp Suite.

#### Example Enumeration Using `curl`

```sh
curl -X GET "https://api.example.com/users"
```

This request will return a list of users or an error message if the endpoint is not properly configured.

### Analyzing Responses

Once we have enumerated the endpoints, we need to analyze the responses to identify any sensitive information that might be disclosed.

#### Example Response Analysis

Consider the following HTTP response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)

{
    "users": [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "hashed_password"
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "password": "hashed_password"
        }
    ]
}
```

In this example, the response contains user data, including email addresses and hashed passwords. While the passwords are hashed, the presence of email addresses in the response could be considered sensitive information.

### Stack Trace Errors

Stack trace errors are particularly dangerous because they can reveal detailed information about the application's internal structure and logic. These errors often occur due to unhandled exceptions or improper error handling.

#### Example Stack Trace Error

Consider the following HTTP response:

```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html; charset=UTF-8
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)

<!DOCTYPE html>
<html>
<head>
<title>500 Internal Server Error</title>
</head>
<body>
<h1>Internal Server Error</h1>
<p>The server encountered an unexpected condition which prevented it from fulfilling the request.</p>
<pre>
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 2464, in __call__
    return self.wsgi_app(environ, start_response)
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 2447, in wsgi_app
    response = self.handle_exception(e)
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1867, in handle_exception
    reraise(exc_type, exc_value, tb)
  File "/usr/local/lib/python3.8/dist-packages/flask/_compat.py", line 39, in reraise
    raise value
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 2444, in wsgi_app
    response = self.full_dispatch_request()
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1952, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1821, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "/usr/local/lib/python3.8/dist-packages/flask/_compat.py", line 39, in reraise
    raise value
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1950, in full_dispatch_request
    rv = self.dispatch_request()
  File "/usr/local/lib/python3.8/dist-packages/flask/app.py", line 1936, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "/app/views.py", line 10, in get_users
    return jsonify(users)
  File "/app/models.py", line 5, in get_users
    return User.query.all()
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/query.py", line 3329, in all
    return list(self)
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in instances
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc(row) for row in fetch]
  File "/usr/local/lib/python3.8/dist-packages/sqlalchemy/orm/loading.py", line 111, in <listcomp>
    return [proc

---
<!-- nav -->
[[API Security/16-Information Disclosure/03-Information Disclosure Demonstration/00-Overview|Overview]] | [[API Security/16-Information Disclosure/03-Information Disclosure Demonstration/02-Information Disclosure in APIs|Information Disclosure in APIs]]
