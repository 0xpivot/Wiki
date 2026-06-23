---
course: API Security
topic: Using Postman tool for API Security Testing
tags: [api-security]
---

## Introduction to JWT Authentication and Postman

Welcome to the world of API security testing using Postman, a powerful tool for developers and security professionals alike. In this chapter, we will delve deep into the use of JSON Web Tokens (JWT) for authentication within APIs and how to test these mechanisms effectively using Postman.

### What is JWT?

JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. They are particularly useful for transmitting information between parties in a way that can be verified and trusted as being authentic. A typical JWT consists of three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the authenticity of the sender.

#### Example of a JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
}
```

The above JWT is composed of three parts separated by dots (`.`):

- **Header**: `{"alg":"HS256","typ":"JWT"}`
- **Payload**: `{"sub":"1234567890","name":"John Doe","iat":1111111111}`
- **Signature**: `HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)`

### Why Use JWT?

JWTs are widely used because they provide a simple and secure method for transmitting information between parties. They are particularly useful in stateless environments like RESTful APIs, where maintaining session state on the server is impractical.

### How JWT Works

When a user logs in, the server generates a JWT and sends it to the client. The client then includes this token in subsequent requests, typically in the `Authorization` header. The server verifies the token and processes the request if valid.

#### Example Request with JWT

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Setting Up Postman for JWT Authentication

Postman is a versatile tool for testing APIs, including those that use JWT for authentication. Let’s walk through the steps to set up Postman for JWT-based API testing.

#### Importing APIs into Postman

First, import your APIs into Postman. You can do this by importing a collection from a file or creating a new collection manually.

```mermaid
sequenceDiagram
  participant User
  participant Postman
  User->>Postman: Import Collection
  Postman-->>User: Collection Imported
```

#### Sending a Request Without JWT

Before setting up JWT, let’s try sending a request without it to see the `401 Unauthorized` error.

```http
GET /api/resource HTTP/1.1
Host: example.com
```

Response:

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "message": "Unauthorized"
}
```

### Adding JWT to Postman

Now, let’s add the JWT to our request in Postman.

1. **Generate JWT**: Obtain a valid JWT from your authentication service.
2. **Set Authorization Header**: Add the JWT to the `Authorization` header in Postman.

#### Step-by-Step Instructions

1. **Open the Request**:
   - Click on the request you want to modify.
   
2. **Add Authorization**:
   - Go to the `Authorization` tab.
   - Select `Bearer Token`.
   - Enter your JWT in the `Token` field.

```mermaid
sequenceDiagram
  participant User
  participant Postman
  User->>Postman: Open Request
  Postman-->>User: Request Opened
  User->>Postman: Go to Authorization Tab
  Postman-->>User: Authorization Tab Opened
  User->>Postman: Select Bearer Token
  Postman-->>User: Bearer Token Selected
  User->>Postman: Enter JWT
  Postman-->>User: JWT Entered
```

#### Sending the Request with JWT

Now, send the request again with the JWT included.

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": "Resource Data"
}
```

### Real-World Examples and Breaches

JWTs have been involved in several high-profile breaches due to improper implementation or configuration. One notable example is the breach of a popular cryptocurrency exchange, where attackers exploited a vulnerability in the JWT handling mechanism to gain unauthorized access.

#### CVE-2021-21972

CVE-2021-21972 is a critical vulnerability affecting the `jsonwebtoken` library in Node.js. This vulnerability allows attackers to bypass authentication checks by manipulating the JWT signature.

```mermaid
sequenceDiagram
  participant Attacker
  participant Server
  Attacker->>Server: Send Malformed JWT
  Server-->>Attacker: Unauthorized Access
```

### How to Prevent / Defend Against JWT Vulnerabilities

To ensure the security of JWTs, follow these best practices:

1. **Use Strong Algorithms**: Always use strong algorithms like `RS256` or `ES256` instead of `HS256`.
2. **Validate Tokens Properly**: Ensure tokens are validated correctly on the server-side.
3. **Secure Storage**: Store JWTs securely in HTTP-only cookies or local storage.
4. **Regular Audits**: Regularly audit JWT implementations for vulnerabilities.

#### Secure Code Example

Here is a comparison of insecure and secure JWT handling in a Node.js application.

**Insecure Code**

```javascript
const jwt = require('jsonwebtoken');

function authenticate(req, res) {
  const token = req.headers.authorization.split(' ')[1];
  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) return res.status(401).send({ message: 'Unauthorized' });
    req.user = decoded;
    next();
  });
}
```

**Secure Code**

```javascript
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

function authenticate(req, res) {
  const token = req.headers.authorization.split(' ')[1];
  jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['RS256'] }, (err, decoded) => {
    if (err) return res.status(401).send({ message: 'Unauthorized' });
    req.user = decoded;
    next();
  });
}

function generateToken(user) {
  const payload = {
    userId: user.id,
    iat: Math.floor(Date.now() / 1000),
    jti: uuidv4(),
  };
  return jwt.sign(payload, process.env.JWT_SECRET, { algorithm: 'RS256' });
}
```

### Conclusion

Using JWTs for API authentication is a powerful and flexible approach, but it requires careful implementation to avoid security vulnerabilities. Postman provides a robust environment for testing these mechanisms, ensuring that your APIs remain secure and reliable.

### Practice Labs

For hands-on practice with JWT authentication and API security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on JWT and API security.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing various security techniques, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of security vulnerabilities, including JWT-related issues.

By mastering JWT authentication and testing with tools like Postman, you can significantly enhance the security of your APIs and protect against potential threats.

---
<!-- nav -->
[[API Security/04-Using Postman tool for API Security Testing/04-JWT Token in Postman/01-Introduction to API Security Testing with Postman|Introduction to API Security Testing with Postman]] | [[API Security/04-Using Postman tool for API Security Testing/04-JWT Token in Postman/00-Overview|Overview]] | [[API Security/04-Using Postman tool for API Security Testing/04-JWT Token in Postman/03-Practice Questions & Answers|Practice Questions & Answers]]
