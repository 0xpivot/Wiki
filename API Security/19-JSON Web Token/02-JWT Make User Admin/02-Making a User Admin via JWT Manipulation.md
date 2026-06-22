---
course: API Security
topic: JSON Web Token
tags: [api-security]
---

## Making a User Admin via JWT Manipulation

In the context of the lecture, we will explore how an attacker might manipulate a JWT to elevate a user's privileges to an admin role. This involves understanding the structure of the JWT and the potential weaknesses in its implementation.

### Step-by-Step Process

1. **Obtain the JWT**: The attacker first needs to obtain a valid JWT. This could be through a legitimate login process or by intercepting a token in transit.

2. **Decode the JWT**: Using tools like jwt.io, the attacker decodes the JWT to inspect its contents.

3. **Modify the Payload**: The attacker modifies the payload to change the user's role to admin. For example, changing `"admin": false` to `"admin": true`.

4. **Re-sign the JWT**: Without the secret key, the attacker cannot re-sign the JWT. However, some implementations may use weak or predictable keys, making it possible to guess or brute-force the key.

5. **Inject the Modified JWT**: The attacker injects the modified JWT into the `Authorization` header of subsequent requests to gain elevated privileges.

### Example Scenario

Consider a web application that uses JWT for authentication. An attacker wants to elevate their privileges to admin.

#### Original JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "admin": false,
    "iat": 1516239022
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

#### Modified JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "admin": true,
    "iat": 1516239022
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Mermaid Diagram: JWT Manipulation Attack Chain

```mermaid
sequenceDiagram
  participant Attacker
  participant Client
  participant Server

  Attacker->>Client: Obtain JWT
  Client-->>Attacker: JWT
  Attacker->>Attacker: Decode JWT
  Attacker->>Attacker: Modify Payload
  Attacker->>Attacker: Re-sign JWT (if possible)
  Attacker->>Server: Inject Modified JWT
  Server-->>Attacker: Elevated Privileges
```

### Common Pitfalls

1. **Weak Secret Key**: Using a weak or predictable secret key makes it easier for attackers to guess or brute-force the key.
2. **Improper Validation**: Failing to validate the `kid` claim or other critical fields can lead to forgery.
3. **Insecure Storage**: Storing JWTs insecurely, such as in cookies without the `HttpOnly` flag, can expose them to XSS attacks.

### How to Prevent / Defend

#### Detection

1. **Monitor JWT Usage**: Implement logging and monitoring to detect unusual patterns in JWT usage.
2. **Anomaly Detection**: Use machine learning algorithms to identify anomalous behavior indicative of JWT manipulation.

#### Prevention

1. **Use Strong Secret Keys**: Ensure the secret key is strong and kept confidential.
2. **Validate Claims**: Always validate critical claims like `kid`, `iss`, and `aud`.
3. **Secure Storage**: Store JWTs securely, using `HttpOnly` cookies and setting appropriate SameSite attributes.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def generate_jwt(user_id, name, admin=False):
    payload = {
        "sub": user_id,
        "name": name,
        "admin": admin,
        "iat": int(time.time())
    }
    return jwt.encode(payload, "secret_key", algorithm="HS256")
```

##### Secure Code

```python
import jwt

def generate_jwt(user_id, name, admin=False):
    payload = {
        "sub": user_id,
        "name": name,
        "admin": admin,
        "iat": int(time.time()),
        "iss": "your_domain",
        "aud": "your_audience"
    }
    return jwt.encode(payload, "strong_secret_key", algorithm="HS256")
```

### Complete Example: Full HTTP Request and Response

#### Vulnerable HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

#### Vulnerable HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOmZhbHNlLCJpYXQiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

#### Secure HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

#### Secure HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOmZhbHNlLCJpYXQiOjE1MTYyMzkwMjIsImlzcyI6InlvdXJfbG9naW4iLCJhdWQiOiJ5b3VyX2F1ZGl0aW9uIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Hands-On Labs

For practical experience with JWT security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing JWT-related attacks and defenses.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios where JWTs can be exploited.

By thoroughly understanding JWTs and their potential vulnerabilities, developers can implement more secure authentication and authorization mechanisms, protecting applications from unauthorized access and privilege escalation attacks.

---
<!-- nav -->
[[API Security/19-JSON Web Token/02-JWT Make User Admin/01-Introduction to JSON Web Tokens (JWT)|Introduction to JSON Web Tokens (JWT)]] | [[API Security/19-JSON Web Token/02-JWT Make User Admin/00-Overview|Overview]] | [[API Security/19-JSON Web Token/02-JWT Make User Admin/03-Practice Questions & Answers|Practice Questions & Answers]]
