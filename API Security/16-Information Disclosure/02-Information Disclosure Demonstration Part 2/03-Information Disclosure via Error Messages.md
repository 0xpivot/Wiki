---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Information Disclosure via Error Messages

### Introduction to Information Disclosure

Information disclosure vulnerabilities occur when sensitive information is inadvertently exposed to unauthorized users. This can happen through various means, such as error messages, debug logs, or even comments in source code. One common form of information disclosure is through error messages, particularly stack traces, which can reveal internal details about an application's architecture, configuration, and even potential vulnerabilities.

### Understanding Stack Trace Errors

A stack trace is a report of the active stack frames at a particular point in time during the execution of a program. When an exception occurs, the runtime environment typically generates a stack trace to help developers understand the context in which the error happened. However, if this stack trace is displayed to end-users, it can expose sensitive information about the application's internal workings.

#### Example of a Stack Trace Error

Consider the following scenario where a web application encounters an error and displays a stack trace:

```plaintext
HTTP/1.1 500 Internal Server Error
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>
<body>
    <h1>An error occurred</h1>
    <pre>
        Traceback (most recent call last):
          File "/app/controllers/user_controller.py", line 23, in get_user
            user = User.objects.get(id=user_id)
          File "/app/models/user_model.py", line 45, in get
            return db.query("SELECT * FROM users WHERE id = %s", [user_id])
          File "/app/db/db_connection.py", line 78, in query
            cursor.execute(query, params)
        psycopg2.errors.UndefinedTable: relation "users" does not exist
    </pre>
</body>
</html>
```

In this example, the stack trace reveals several pieces of sensitive information:
- The file paths (`/app/controllers/user_controller.py`, `/app/models/user_model.py`, `/app/db/db_connection.py`) indicate the structure of the application's codebase.
- The database query (`SELECT * FROM users WHERE id = %s`) exposes the schema of the database.
- The specific error (`psycopg2.errors.UndefinedTable: relation "users" does not exist`) indicates that the `users` table might not exist, which could be used to infer the presence or absence of certain data structures.

### Real-World Examples of Information Disclosure

Information disclosure vulnerabilities have been exploited in numerous real-world scenarios. Here are a couple of recent examples:

#### CVE-2021-21972: Apache Struts Information Disclosure

Apache Struts is a popular Java framework for building web applications. In 2021, a vulnerability was discovered where certain error messages could disclose sensitive information about the server's filesystem and configuration. This could potentially allow attackers to gain insights into the server's architecture and identify other vulnerabilities.

#### CVE-2022-22965: Microsoft Exchange Server Information Disclosure

Microsoft Exchange Server is widely used for email management. In 2022, a vulnerability was found where certain error messages could reveal sensitive information about the server's configuration and installed components. This information could be used to craft targeted attacks against the server.

### How to Prevent / Defend Against Information Disclosure

To prevent information disclosure via error messages, it is crucial to implement proper error handling and logging practices. Here are some steps to mitigate this risk:

#### Secure Error Handling

Ensure that error messages are handled securely and do not expose sensitive information to end-users. Instead of displaying detailed stack traces, provide generic error messages that do not reveal internal details.

##### Vulnerable Code Example

```python
try:
    user = User.objects.get(id=user_id)
except Exception as e:
    return HttpResponse(f"Error: {str(e)}", status=500)
```

##### Secure Code Example

```python
try:
    user = User.objects.get(id=user_id)
except Exception as e:
    logger.error(f"Error retrieving user: {str(e)}")
    return HttpResponse("An unexpected error occurred.", status=500)
```

#### Logging Best Practices

Implement logging best practices to ensure that sensitive information is logged securely and not exposed to unauthorized users.

##### Vulnerable Configuration Example

```nginx
error_log /var/log/nginx/error.log;
```

##### Secure Configuration Example

```nginx
error_log /var/log/nginx/error.log warn;
```

By setting the log level to `warn`, only warnings and errors are logged, reducing the risk of exposing sensitive information.

### Detection and Monitoring

Regularly monitor your application's error logs and implement tools to detect and alert on potential information disclosure vulnerabilities.

#### Tools for Detection

- **Static Application Security Testing (SAST)**: Tools like SonarQube and Fortify can analyze source code for potential information disclosure vulnerabilities.
- **Dynamic Application Security Testing (DAST)**: Tools like Burp Suite and OWASP ZAP can simulate attacks and detect information disclosure issues.

### Hands-On Practice Labs

To practice securing against information disclosure vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security topics, including information disclosure.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

### Conclusion

Information disclosure vulnerabilities can significantly compromise the security of an application. By understanding the risks associated with stack trace errors and implementing proper error handling and logging practices, you can mitigate these risks and protect sensitive information. Regular monitoring and the use of security tools can further enhance your defense against such vulnerabilities.

---
<!-- nav -->
[[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/02-Information Disclosure in APIs|Information Disclosure in APIs]] | [[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/00-Overview|Overview]] | [[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/04-Practice Questions & Answers|Practice Questions & Answers]]
