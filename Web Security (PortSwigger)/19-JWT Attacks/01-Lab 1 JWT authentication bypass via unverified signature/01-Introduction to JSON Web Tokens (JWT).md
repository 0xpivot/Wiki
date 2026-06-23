---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely adopted standard for securely transmitting information between parties as a JSON object. They are particularly useful in web applications for maintaining state and authenticating users across different requests. A JWT consists of three parts: the header, the payload, and the signature. Each part is base64url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This JWT can be broken down into three parts:

1. **Header**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
   - Decoded: `{"alg":"HS256","typ":"JWT"}`
   - This specifies the algorithm used for signing the token (HMAC SHA-256 in this case) and the type of token (JWT).

2. **Payload**: `eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ`
   - Decoded: `{"sub":"1234567890","name":"John Doe","iat":1516239022}`
   - This contains claims about the user, such as their ID, name, and the time the token was issued.

3. **Signature**: `SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`
   - This is created by taking the encoded header, the encoded payload, a secret, and the algorithm specified in the header. The signature ensures that the message wasn't changed along the way and lets the receiver verify the sender.

### Usage in Web Applications

JWTs are commonly used in web applications to maintain user sessions and authenticate requests. When a user logs in, the server generates a JWT and sends it back to the client. The client then includes this token in subsequent requests, typically in an `Authorization` header using the Bearer scheme.

#### Example of JWT in HTTP Request

```http
GET /api/user HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Importance of Verifying the Signature

One of the most critical aspects of using JWTs is ensuring that the signature is verified. This prevents attackers from tampering with the token or creating their own tokens. If the signature is not properly verified, an attacker could potentially bypass authentication mechanisms.

### Lab Setup

In this lab, we will explore a scenario where a web application uses JWTs but fails to verify the signature correctly. This can lead to an authentication bypass vulnerability.

#### Initial Setup

Let's start by examining the login process of the web application. When a user logs in, the application checks the CSRF token, username, and password. If these credentials are correct, the application sets a session cookie containing the JWT.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

csrf_token=abc123&username=admin&password=secret
```

If the credentials are valid, the server responds with a session cookie containing the JWT.

```http
HTTP/1.1 200 OK
Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0; HttpOnly
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
</head>
<body>
    <h1>Welcome, admin!</h1>
</body>
</html>
```

### Identifying JWT in the Response

The JSON Web Token Editor extension helps identify and decode JWTs. In this case, the extension highlights the JWT in the session cookie.

```http
Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0; HttpOnly
```

### Modifying the JWT

The JSON Web Token Editor extension allows us to modify the token. However, for this lab, we will use the Repeater tool to modify and resend the token.

#### Using Repeater to Modify the JWT

1. Capture the login request in the Repeater tool.
2. Modify the JWT in the `Authorization` header.
3. Resend the modified request.

```http
GET /api/user HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0
```

### Authentication Bypass Vulnerability

If the server does not properly verify the signature of the JWT, an attacker can craft a new token with arbitrary claims and bypass authentication.

#### Real-World Example: CVE-2020-14182

CVE-2020-14182 is a real-world example where a web application failed to validate the JWT signature, leading to unauthorized access. The application trusted the JWT without verifying the signature, allowing an attacker to craft a token with elevated privileges.

### How to Prevent / Defend Against JWT Attacks

To prevent JWT attacks, it is crucial to ensure that the signature is properly verified. Here are some steps to secure JWT usage:

1. **Verify the Signature**: Always verify the signature of the JWT to ensure it hasn't been tampered with.
2. **Use Strong Algorithms**: Use strong cryptographic algorithms like HMAC SHA-256 or RSA with a large key size.
3. **Secure Secret Keys**: Store secret keys securely and rotate them regularly.
4. **Implement Expiration**: Set an expiration time for JWTs to limit their validity period.
5. **Use HTTPS**: Ensure that JWTs are transmitted over HTTPS to prevent interception.

#### Secure Code Example

Here is an example of how to securely verify a JWT in Python using the `PyJWT` library:

```python
import jwt

# Secret key used for signing and verification
SECRET_KEY = 'your_secret_key'

# Sample JWT
jwt_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJhZG1pbiIsImlhdCI6MTYwNjIwNDQwMX0'

try:
    # Verify the JWT
    decoded_jwt = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
    print(decoded_jwt)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

### Detection and Prevention

To detect and prevent JWT attacks, implement the following measures:

1. **Logging and Monitoring**: Log and monitor JWT usage to detect unusual patterns.
2. **Security Audits**: Regularly perform security audits to identify vulnerabilities.
3. **Penetration Testing**: Conduct penetration testing to simulate attacks and identify weaknesses.

### Conclusion

Understanding and securing JWT usage is crucial for maintaining the integrity and security of web applications. By verifying signatures, using strong algorithms, and implementing proper security measures, developers can mitigate the risks associated with JWT attacks.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT manipulation and attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including JWT attacks.

By completing these labs, you can gain practical experience in identifying and preventing JWT-related vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/02-Introduction to JWT Attacks|Introduction to JWT Attacks]]
