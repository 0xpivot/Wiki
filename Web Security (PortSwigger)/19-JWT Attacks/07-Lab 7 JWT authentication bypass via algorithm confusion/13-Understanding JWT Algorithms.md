---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding JWT Algorithms

### Introduction to JWT Algorithms

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties in a compact and verifiable manner. JWTs consist of three parts: the header, the payload, and the signature. The header typically contains metadata about the token, including the type of token and the signing algorithm used. The payload contains the claims, which are statements about an entity and additional data. Finally, the signature ensures the integrity and authenticity of the token.

The signing algorithm is crucial for ensuring that the token has not been tampered with and that it was issued by a trusted party. There are two main types of signing algorithms: symmetric and asymmetric.

#### Symmetric Algorithms

Symmetric algorithms use a single key for both signing and verifying the token. This means that the same key is used to create the signature and to validate it. Examples of symmetric algorithms include HMAC SHA-256 (`HS256`), HMAC SHA-384 (`HS384`), and HMAC SHA-512 (`HS512`). These algorithms are generally faster than their asymmetric counterparts but require that the key be kept secret and shared securely between the parties involved.

**Example of a Symmetric Algorithm:**

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

In this example, the `alg` field specifies that the token is signed using the HMAC SHA-256 algorithm.

#### Asymmetric Algorithms

Asymmetric algorithms, also known as public-key cryptography, use a pair of keys: a private key and a public key. The private key is used to sign the token, and the public key is used to verify the signature. Examples of asymmetric algorithms include RSA (`RS256`, `RS384`, `RS512`) and Elliptic Curve Digital Signature Algorithm (ECDSA) (`ES256`, `ES384`, `ES512`).

**Example of an Asymmetric Algorithm:**

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

In this example, the `alg` field specifies that the token is signed using the RSA SHA-256 algorithm.

### Algorithm Confusion Attacks

Algorithm confusion attacks occur when an attacker can manipulate the `alg` parameter in the JWT header to trick the server into using a different signing algorithm than intended. This can lead to vulnerabilities if the server does not properly validate the algorithm used to sign the token.

#### How Algorithm Confusion Works

Consider a scenario where an application uses an asymmetric algorithm like RSA (`RS256`) to sign JWTs. However, due to a flaw in the implementation, the server does not properly check the `alg` parameter in the JWT header. An attacker can exploit this by changing the `alg` parameter to a symmetric algorithm like HMAC SHA-256 (`HS256`).

**Example of an Exploited JWT Header:**

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

If the server does not validate the `alg` parameter correctly, it may accept the token and use the symmetric algorithm to verify the signature. Since the attacker controls the symmetric key, they can easily generate a valid signature and bypass authentication.

### Real-World Example: CVE-2017-15359

One notable real-world example of an algorithm confusion attack is CVE-2017-15359, which affected the `jsonwebtoken` library in Node.js. The vulnerability allowed attackers to bypass authentication by manipulating the `alg` parameter in the JWT header.

**CVE-2017-15359 Details:**

- **Vulnerability Type:** Algorithm Confusion Attack
- **Affected Library:** `jsonwebtoken`
- **Impact:** Authentication Bypass

In this case, the `jsonwebtoken` library did not properly validate the `alg` parameter, allowing attackers to change it to a symmetric algorithm and bypass authentication.

### Full HTTP Request and Response

Let's consider a full HTTP request and response involving a JWT with an exploited `alg` parameter.

**HTTP Request:**

```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Authentication successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

In this example, the attacker has manipulated the `alg` parameter to `HS256` and generated a valid signature using a symmetric key. The server accepts the token and authenticates the user.

### Mermaid Diagram: Attack Chain

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant Server
    User->>Server: Send JWT with RS256
    Server-->>User: Validate RS256
    Attacker->>Server: Send JWT with HS256
    Server-->>Attacker: Validate HS256
    Attacker->>Server: Bypass Authentication
```

### How to Prevent / Defend Against Algorithm Confusion Attacks

#### Detection

To detect algorithm confusion attacks, you can implement logging and monitoring of JWT validation processes. Look for unexpected changes in the `alg` parameter or unusual patterns in the validation process.

#### Prevention

1. **Validate the `alg` Parameter:**
   Ensure that the server validates the `alg` parameter in the JWT header and only accepts the expected algorithm. For example, if the application uses `RS256`, the server should reject any JWT with a different algorithm.

2. **Use Strong Algorithms:**
   Use strong and secure algorithms like RSA (`RS256`) or ECDSA (`ES256`). Avoid using weak or deprecated algorithms.

3. **Secure Key Management:**
   Ensure that private keys are securely stored and not exposed to unauthorized parties. Public keys should be securely distributed and verified.

4. **Implement Rate Limiting:**
   Implement rate limiting on authentication endpoints to prevent brute-force attacks.

#### Secure Coding Fixes

Here is an example of how to properly validate the `alg` parameter in a secure manner:

**Vulnerable Code:**

```javascript
const jwt = require('jsonwebtoken');

function authenticate(token) {
    const decoded = jwt.verify(token, 'secret');
    return decoded;
}
```

**Fixed Code:**

```javascript
const jwt = require('jsonwebtoken');

function authenticate(token) {
    try {
        const decoded = jwt.verify(token, 'secret', { algorithms: ['RS256'] });
        return decoded;
    } catch (error) {
        console.error('JWT validation failed:', error);
        return null;
    }
}
```

In the fixed code, the `algorithms` option is used to specify the expected algorithm, preventing the server from accepting tokens with other algorithms.

### Configuration Hardening

Ensure that your JWT configuration is hardened against algorithm confusion attacks. Here is an example of a secure JWT configuration in a Node.js application:

**Secure JWT Configuration:**

```javascript
const jwt = require('jsonwebtoken');

const secret = 'your-secret-key';
const options = {
    issuer: 'example.com',
    audience: 'users',
    subject: 'user-id',
    expiresIn: '1h',
    algorithm: 'RS256'
};

function generateToken(user) {
    const token = jwt.sign({ sub: user.id }, secret, options);
    return token;
}

function authenticate(token) {
    try {
        const decoded = jwt.verify(token, secret, options);
        return decoded;
    } catch (error) {
        console.error('JWT validation failed:', error);
        return null;
    }
}
```

In this configuration, the `algorithm` option is set to `RS256`, ensuring that only tokens signed with this algorithm are accepted.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on JWT authentication bypass and other web security topics.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application):** Provides various web application vulnerabilities, including JWT-related issues.

These labs provide a safe environment to practice and understand JWT attacks and defenses.

### Conclusion

Understanding and defending against algorithm confusion attacks is crucial for securing JWT-based authentication systems. By validating the `alg` parameter, using strong algorithms, and implementing secure coding practices, you can protect your application from these vulnerabilities. Regularly monitor and update your security measures to stay ahead of potential threats.

---
<!-- nav -->
[[12-Understanding Algorithm Confusion|Understanding Algorithm Confusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[14-Understanding the Attack|Understanding the Attack]]
