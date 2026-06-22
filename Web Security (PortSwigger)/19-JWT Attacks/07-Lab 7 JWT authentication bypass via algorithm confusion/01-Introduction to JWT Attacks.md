---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

### What is a JWT?

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the message. It is created by hashing the encoded header and payload with a secret key or a public/private key pair.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking down the components:

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

JWTs are crucial for securing web applications because they provide a way to transmit information securely and ensure that the information has not been tampered with. They are often used for authentication and authorization purposes.

### How JWTs Work Under the Hood

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token (usually in local storage or cookies) and includes it in the `Authorization` header of subsequent requests. The server verifies the token to ensure that it is valid and has not been tampered with.

#### Example of a JWT Request

```http
GET /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### Example of a JWT Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": "This is protected data."
}
```

### Algorithm Confusion Attack

Algorithm confusion, also known as key confusion, is a type of attack where an attacker forces the server to verify the signature of a JWT using a different algorithm than the one used by the developers. This can lead to unauthorized access if the server accepts the token despite the mismatched algorithm.

### Real-World Examples

One notable real-world example of an algorithm confusion attack is the CVE-2017-15357, which affected several popular libraries and frameworks that implemented JWTs. In this case, the vulnerability allowed attackers to bypass authentication by manipulating the `alg` field in the JWT header.

### Steps to Perform an Algorithm Confusion Attack

To perform an algorithm confusion attack, follow these steps:

1. **Capture the JWT**: Intercept the JWT sent by the server.
2. **Modify the JWT**: Change the `alg` field in the header to a different algorithm.
3. **Forge the Signature**: Generate a new signature using the modified algorithm.
4. **Submit the Modified JWT**: Send the modified JWT to the server.

### Example of an Algorithm Confusion Attack

Consider a scenario where the server uses the `RS256` algorithm to sign JWTs. An attacker captures the JWT and modifies it to use the `HS256` algorithm instead.

#### Original JWT

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  },
  "signature": "original_signature"
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
    "iat": 1516239022
  },
  "signature": "modified_signature"
}
```

### How to Prevent / Defend Against Algorithm Confusion Attacks

#### Detection

To detect algorithm confusion attacks, implement logging and monitoring to track JWT usage patterns. Look for anomalies such as unexpected algorithms or signatures.

#### Prevention

1. **Validate Algorithms**: Ensure that the server only accepts JWTs signed with the expected algorithm.
2. **Use Strong Algorithms**: Use strong cryptographic algorithms like `RS256` or `ES256` instead of weaker ones like `HS256`.
3. **Secure Key Management**: Store and manage keys securely to prevent unauthorized access.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

##### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        return payload['sub']
    except jwt.exceptions.InvalidTokenError:
        return None
```

##### Secure Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'], options={'verify_signature': True})
        return payload['sub']
    except jwt.exceptions.InvalidTokenError:
        return None
```

### Configuration Hardening

Ensure that the JWT library configurations are hardened:

```json
{
  "jwt": {
    "secret": "your_secret_key",
    "algorithm": "HS256",
    "options": {
      "verify_signature": true,
      "verify_aud": true,
      "verify_exp": true
    }
  }
}
```

### Conclusion

Algorithm confusion attacks are a serious threat to web applications that use JWTs for authentication and authorization. By understanding the mechanics of these attacks and implementing robust defenses, developers can protect their applications from such vulnerabilities.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including JWT-related issues.

By engaging with these labs, you can gain practical experience in identifying and defending against JWT attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/02-Introduction to JWT and Algorithm Confusion Attacks|Introduction to JWT and Algorithm Confusion Attacks]]
