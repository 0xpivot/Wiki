---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Introduction to API2: Broken Authentication

API2: Broken Authentication is one of the critical issues listed in the OWASP API Security Top 10. This vulnerability occurs when an application fails to properly manage authentication mechanisms, leading to unauthorized access to sensitive data or functionality. In this section, we will delve deep into the concepts of authentication in APIs, the structure of JWT tokens, and the vulnerabilities associated with improper handling of these tokens.

### What is Authentication in APIs?

Authentication is the process of verifying the identity of a user or system attempting to access a resource. In the context of APIs, authentication ensures that only authorized users can interact with the API endpoints. Common methods of authentication include:

- **Basic Authentication**: Uses a username and password pair encoded in Base64.
- **OAuth**: An open-standard authorization protocol that provides access tokens to third-party applications.
- **JWT (JSON Web Tokens)**: A compact, URL-safe means of representing claims to be transferred between two parties.

### JWT Structure

JWT tokens consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token by hashing the header and payload using a secret key.

#### Example of a JWT Token

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header**:
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
  ```

- **Signature**:
  ```plaintext
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  ```

### Vulnerabilities in JWT Handling

One of the most common vulnerabilities in JWT handling is the **None Algorithm Attack**. This attack exploits the flexibility of JWTs by allowing the attacker to change the `alg` field in the header to `"none"` and bypass the signature verification.

#### None Algorithm Attack

When the `alg` field is set to `"none"`, the server may fail to validate the signature, leading to unauthorized access. This is particularly dangerous because the attacker can modify the payload without being detected.

#### Example of None Algorithm Attack

Consider the following JWT token:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

An attacker can modify the header to `"none"`:

```plaintext
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

The server may accept this token without validating the signature, leading to unauthorized access.

### Real-World Examples

Several high-profile breaches have been attributed to vulnerabilities in JWT handling:

- **CVE-2020-14774**: A vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to bypass signature validation by setting the `alg` field to `"none"`.
- **CVE-2021-3129**: A similar vulnerability in the `firebase-admin` SDK for Node.js allowed attackers to forge JWT tokens.

### How to Prevent / Defend Against Broken Authentication

To prevent broken authentication vulnerabilities, follow these best practices:

#### Secure Coding Practices

1. **Validate JWT Signatures**: Always validate the signature of JWT tokens to ensure their authenticity.
2. **Use Strong Algorithms**: Use strong signing algorithms like `HS256` or `RS256` instead of weaker ones.
3. **Reject None Algorithm**: Reject JWT tokens with the `alg` field set to `"none"`.

#### Example of Secure JWT Validation

Here is an example of secure JWT validation using the `jsonwebtoken` library in Node.js:

```javascript
const jwt = require('jsonwebtoken');

function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });
    return decoded;
  } catch (err) {
    console.error('Invalid token:', err);
    return null;
  }
}

// Usage
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c';
const user = verifyToken(token);
if (user) {
  console.log('Authenticated user:', user);
} else {
  console.log('Failed to authenticate');
}
```

#### Configuration Hardening

1. **Disable Weak Algorithms**: Ensure that your JWT library does not support weak algorithms like `"none"`.
2. **Use Environment Variables**: Store sensitive information like JWT secrets in environment variables rather than hardcoding them.

#### Detection and Monitoring

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns in JWT usage.
2. **Security Scanning**: Regularly scan your codebase for known vulnerabilities using tools like `OWASP ZAP` or `SonarQube`.

### Mermaid Diagrams

#### JWT Token Structure

```mermaid
graph TD
    JWT[JWT Token] -->|Header| Header[{"alg":"HS256","typ":"JWT"}]
    JWT -->|Payload| Payload[{"sub":"1234567890","name":"John Doe","iat":1516239022}]
    JWT -->|Signature| Signature[SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c]
```

#### None Algorithm Attack Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: Send JWT with alg="none"
    Server-->>Client: Accept token without signature validation
    Client->>Server: Access protected resources
```

### Conclusion

Broken authentication is a serious vulnerability that can lead to unauthorized access to sensitive data. By understanding the structure of JWT tokens and implementing secure coding practices, you can mitigate these risks and ensure the security of your API endpoints.

### Practice Labs

For hands-on practice with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various API security topics, including JWT manipulation.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing web security skills, including API security.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including API-related issues.

By mastering the concepts and techniques covered in this chapter, you will be well-equipped to handle API security challenges effectively.

---
<!-- nav -->
[[API Security/05-OWASP API TOP 10/03-API2 Broken Authentication/00-Overview|Overview]] | [[02-Introduction to Broken Authentication|Introduction to Broken Authentication]]
