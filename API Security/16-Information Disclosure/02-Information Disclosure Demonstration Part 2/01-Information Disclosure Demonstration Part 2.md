---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Information Disclosure Demonstration Part 2

### Background Theory

Information disclosure vulnerabilities occur when sensitive data is unintentionally exposed to unauthorized users. This can happen through various means, such as error messages, debug logs, or improperly configured APIs. The goal of an attacker exploiting these vulnerabilities is to gain access to sensitive information that could be used for further attacks or to compromise the system.

In the context of APIs, information disclosure can manifest in several ways:

1. **Error Messages**: Revealing internal details about the application or database structure.
2. **Debug Logs**: Exposing sensitive data in log files.
3. **Improper Error Handling**: Returning detailed error messages to the client.
4. **Sensitive Data Exposure**: Directly exposing sensitive data in API responses.

### Detailed Example: PUT Request Response

Let's start by examining the scenario described in the lecture. We have a PUT request that returns a 200 status code, indicating success, but the resource identified by the `ID` does not exist because it has been deleted.

```http
PUT /resource/123 HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 0
```

#### Analysis

- **Status Code**: The server returns a 200 status code, which typically indicates success. However, since the resource with `ID` 123 has been deleted, this response is misleading.
- **Content-Length**: The response has a `Content-Length` of 0, meaning no additional information is provided in the body.

This scenario demonstrates a potential information disclosure issue. An attacker might attempt to exploit this by sending a GET request to the same endpoint to see if any sensitive information is returned.

```http
GET /resource/123 HTTP/1.1
Host: example.com
```

Response:

```http
HTTP/1.1 404 Not Found
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 37

{
  "error": "Resource not found"
}
```

#### Analysis

- **Status Code**: The server returns a 404 status code, indicating that the resource is not found.
- **Error Message**: The response includes a generic error message, which is better than revealing internal details.

### Exploiting Information Disclosure

The lecture mentions that an attacker might try to generate errors by passing certain values in the request body. Let's explore this in more detail.

#### Example: Creating Users

Consider an API endpoint for creating users. An attacker might attempt to exploit this endpoint by passing invalid data to trigger an error.

```http
POST /users HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "admin",
  "password": "weakpassword"
}
```

Response:

```http
HTTP/1.1 500 Internal Server Error
Date: Mon, 23 Jan 2023 12:00:00 GMT
Content-Type: text/plain
Content-Length: 110

An unexpected error occurred: java.sql.SQLException: Incorrect syntax near 'admin'.
```

#### Analysis

- **Status Code**: The server returns a 500 status code, indicating an internal server error.
- **Error Message**: The response includes a detailed error message that reveals the underlying SQL syntax error.

This type of error message can provide valuable information to an attacker, such as the database schema or the specific SQL query being executed.

### Real-World Examples

Recent real-world examples of information disclosure vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the WordPress REST API allowed attackers to disclose sensitive information by manipulating certain parameters.
- **CVE-2022-22965**: A vulnerability in the Microsoft Exchange Server allowed attackers to disclose sensitive information through improper error handling.

These vulnerabilities highlight the importance of proper error handling and the need to avoid exposing sensitive information in error messages.

### How to Prevent / Defend

To prevent information disclosure vulnerabilities, follow these best practices:

#### Secure Error Handling

Ensure that error messages do not reveal sensitive information. Instead, return generic error messages and log detailed error information internally.

**Vulnerable Code:**

```java
try {
    // Database operation
} catch (SQLException e) {
    response.setStatus(500);
    response.getWriter().write("Error: " + e.getMessage());
}
```

**Secure Code:**

```java
try {
    // Database operation
} catch (SQLException e) {
    response.setStatus(500);
    response.getWriter().write("An unexpected error occurred.");
    logger.error("Database error: " + e.getMessage());
}
```

#### Proper Content Length Handling

Ensure that the `Content-Length` header is set correctly to avoid leaking information.

**Vulnerable Code:**

```python
@app.route('/resource/<int:id>', methods=['GET'])
def get_resource(id):
    resource = Resource.query.get(id)
    if resource is None:
        return jsonify({"error": "Resource not found"}), 404
    else:
        return jsonify(resource.serialize()), 200
```

**Secure Code:**

```python
@app.route('/resource/<int:id>', methods=['GET'])
def get_resource(id):
    resource = Resource.query.get(id)
    if resource is None:
        return jsonify({"error": "Resource not found"}), 404
    else:
        response = jsonify(resource.serialize())
        response.headers['Content-Length'] = str(len(response.data))
        return response, 200
```

#### Logging and Monitoring

Implement logging and monitoring to detect and respond to suspicious activity.

**Example Log Entry:**

```
2023-01-23T12:00:00Z ERROR [com.example.api] - Database error: java.sql.SQLException: Incorrect syntax near 'admin'.
```

#### Secure Configuration

Ensure that sensitive information is not exposed in configuration files or environment variables.

**Vulnerable Configuration:**

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "username": "root",
    "password": "password123"
  }
}
```

**Secure Configuration:**

```json
{
  "database": {
    "host": "${DB_HOST}",
    "port": "${DB_PORT}",
    "username": "${DB_USERNAME}",
    "password": "${DB_PASSWORD}"
  }
}
```

### Hands-On Practice

For hands-on practice, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on API security, including information disclosure.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide real-world scenarios and challenges to help you master the concepts covered in this chapter.

### Conclusion

Information disclosure vulnerabilities can have serious consequences, including the exposure of sensitive data and the potential for further attacks. By implementing proper error handling, securing configurations, and monitoring for suspicious activity, you can significantly reduce the risk of information disclosure vulnerabilities. Always ensure that your applications are designed with security in mind, and regularly test and audit your systems to identify and mitigate potential vulnerabilities.

---
<!-- nav -->
[[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/00-Overview|Overview]] | [[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/02-Information Disclosure in APIs|Information Disclosure in APIs]]
