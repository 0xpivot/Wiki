---
course: API Security
topic: Hidden API Functionality Exposure
tags: [api-security]
---

## Introduction to Hidden API Functionality Exposure

Hidden API functionality exposure occurs when certain endpoints or functionalities within an API are not properly documented or secured, leading to potential unauthorized access or exploitation. This can happen due to various reasons such as oversight during development, lack of proper documentation, or unintended exposure through testing or debugging features. In this chapter, we will delve deep into the concept of hidden API functionality exposure, understand its implications, and learn how to prevent and defend against it.

### Background Theory

APIs (Application Programming Interfaces) are sets of protocols, routines, and tools used for building software applications. They allow different software components to communicate and interact with each other. APIs can be categorized into several types, including RESTful APIs, SOAP APIs, GraphQL APIs, and more. RESTful APIs, which use HTTP methods like GET, POST, PUT, DELETE, etc., are particularly popular due to their simplicity and flexibility.

#### RESTful API Basics

REST (Representational State Transfer) is an architectural style for designing networked applications. It relies on a client-server model, where the client makes requests to the server using HTTP methods. The server responds with appropriate data and status codes. RESTful APIs are stateless, meaning each request from the client to the server must contain all the information necessary to understand and process the request.

##### HTTP Methods

- **GET**: Requests data from a specified resource.
- **POST**: Submits data to be processed to a specified resource.
- **PUT**: Replaces all current representations of the target resource with the uploaded content.
- **DELETE**: Removes the specified resource.
- **PATCH**: Applies partial modifications to a resource.

##### HTTP Status Codes

HTTP status codes provide information about the result of a request. Common status codes include:

- **200 OK**: The request succeeded.
- **201 Created**: The request succeeded and a new resource was created.
- **400 Bad Request**: The request could not be understood due to invalid syntax.
- **401 Unauthorized**: Authentication is required and has failed or has not yet been provided.
- **403 Forbidden**: The server understood the request but refuses to authorize it.
- **404 Not Found**: The requested resource could not be found but may be available in the future.

### Real-World Examples

Hidden API functionality exposure has led to several high-profile breaches and vulnerabilities. Here are some recent examples:

#### Example 1: Tesla API Exposure

In 2020, researchers discovered that Tesla's API had several undocumented endpoints that could be exploited to gain unauthorized access to user data. One such endpoint allowed attackers to retrieve vehicle telemetry data without proper authentication. This exposed sensitive information about Tesla owners, including their driving habits and location data.

#### Example 2: Zoom API Vulnerability

In 2021, a security researcher found that Zoom's API had undocumented endpoints that could be used to bypass authentication and gain unauthorized access to user accounts. This vulnerability allowed attackers to reset passwords and take control of user accounts, leading to a significant breach.

### Detailed Explanation of the Lecture Chunk

Let's break down the lecture chunk and understand the concepts in detail.

#### Generating and Using Tokens

The lecturer starts by generating a token to authenticate API requests. Tokens are often used in API authentication to ensure that only authorized clients can access the API resources. There are different types of tokens, including:

- **Bearer Token**: A token that is passed in the `Authorization` header of an HTTP request.
- **JWT (19-JSON Web Token)**: A compact, URL-safe means of representing claims to be transferred between two parties.

Here is an example of how a token might be generated and used in an API request:

```http
POST /api/v1/auth/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "user",
  "password": "pass"
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Now, the token can be used in subsequent API requests:

```http
GET /api/v2/info HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Forbidden Responses

The lecturer mentions encountering `403 Forbidden` responses when trying to access certain endpoints. This status code indicates that the server understood the request but refuses to authorize it. This can happen due to insufficient permissions, incorrect authentication, or other security policies.

For example, consider the following request:

```http
GET /api/v2/users HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "Forbidden",
  "message": "Access to this resource is restricted."
}
```

#### Capturing and Analyzing Requests

The lecturer captures an API request and sends it to a repeater tool to analyze the response. This is a common technique used in penetration testing and debugging to understand how the API behaves under different conditions.

Here is an example of capturing and analyzing an API request using Burp Suite:

```mermaid
sequenceDiagram
  participant Client
  participant Server
  participant Repeater

  Client->>Server: GET /api/v2/info HTTP/1.1
  Server-->>Client: HTTP/1.1 200 OK
  Client->>Repeater: Capture Request
  Repeater->>Server: GET /api/v2/info HTTP/1.1
  Server-->>Repeater: HTTP/1.1 200 OK
```

#### Finding Hidden Endpoints

The lecturer uses an intruder tool to find hidden endpoints by sending different payloads to the API. This technique is often used to discover undocumented or hidden endpoints that could be exploited.

Here is an example of using an intruder tool to find hidden endpoints:

```mermaid
sequenceDiagram
  participant Client
  participant Server
  participant Intruder

  Client->>Intruder: Load Payloads
  Intruder->>Server: GET /api/v2/<payload> HTTP/1.1
  Server-->>Intruder: HTTP/1.1 400 Bad Request
  Server-->>Intruder: HTTP/1.1 403 Forbidden
  Server-->>Intruder: HTTP/1.1 200 OK
```

### Pitfalls and Common Mistakes

When dealing with hidden API functionality exposure, there are several pitfalls and common mistakes to avoid:

1. **Insufficient Documentation**: Lack of proper documentation can lead to hidden endpoints being overlooked during security assessments.
2. **Improper Authentication**: Failing to properly authenticate requests can expose sensitive data to unauthorized users.
3. **Inadequate Authorization**: Insufficient authorization checks can allow unauthorized access to protected resources.
4. **Testing and Debugging Features**: Leaving testing and debugging features enabled in production environments can expose hidden functionalities.

### How to Prevent / Defend Against Hidden API Functionality Exposure

To prevent and defend against hidden API functionality exposure, follow these best practices:

#### Secure Coding Practices

Ensure that your API is developed with security in mind. Follow secure coding practices such as:

- **Input Validation**: Validate all input data to prevent injection attacks.
- **Authentication and Authorization**: Implement strong authentication mechanisms and enforce proper authorization checks.
- **Error Handling**: Handle errors gracefully and avoid exposing sensitive information in error messages.

Here is an example of secure coding practices in action:

```python
from flask import Flask, request, jsonify
from functools import wraps
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/v2/info', methods=['GET'])
@token_required
def get_info():
    return jsonify({'info': 'This is a secure endpoint.'})

if __name__ == '__main__':
    app.run(debug=True)
```

#### Proper Documentation

Ensure that all API endpoints are properly documented. This includes:

- **Endpoint Descriptions**: Provide detailed descriptions of each endpoint, including input parameters, output formats, and expected behavior.
- **Security Requirements**: Document any security requirements, such as authentication and authorization mechanisms.

Here is an example of proper API documentation:

```json
{
  "paths": {
    "/api/v2/info": {
      "get": {
        "summary": "Retrieve system information.",
        "responses": {
          "200": {
            "description": "Successful response.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "info": {
                      "type": "string",
                      "description": "System information."
                    }
                  }
                }
              }
            }
          },
          "401": {
            "description": "Unauthorized access."
          },
          "403": {
            "description": "Forbidden access."
          }
        }
      }
    }
  }
}
```

#### Regular Security Assessments

Perform regular security assessments to identify and mitigate hidden API functionality exposure. This includes:

- **Penetration Testing**: Conduct penetration tests to simulate real-world attacks and identify vulnerabilities.
- **Code Reviews**: Perform code reviews to ensure that security best practices are followed.

Here is an example of a penetration test report:

```markdown
# Penetration Test Report

---
<!-- nav -->
[[API Security/25-Hidden API Functionality Exposure/02-Hidden API Exposure/00-Overview|Overview]] | [[API Security/25-Hidden API Functionality Exposure/02-Hidden API Exposure/02-Overview|Overview]]
