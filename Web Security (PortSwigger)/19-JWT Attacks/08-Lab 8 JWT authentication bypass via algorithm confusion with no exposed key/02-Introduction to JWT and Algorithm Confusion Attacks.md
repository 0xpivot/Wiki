---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and Algorithm Confusion Attacks

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a token that can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

#### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional data.
3. **Signature**: Used to verify the integrity of the message. The signature is created using the header, the payload, a secret, and the algorithm specified in the header.

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

### Algorithm Confusion Attack

Algorithm confusion, also known as key confusion attack, is a type of attack where an attacker forces the server to verify the signature of a JSON Web Token (JWT) using a different algorithm than the one intended by the developers. This can lead to unauthorized access if the server does not properly validate the algorithm used in the token.

#### Types of Algorithms

There are two main types of algorithms used in JWTs:

1. **Symmetric Algorithms**: These use a single key for both signing and verifying the token. Common examples include HMAC-SHA256 (HS256).

2. **Asymmetric Algorithms**: These use a pair of keys, one for signing (private key) and one for verification (public key). Common examples include RSA and ECDSA.

### Example of Algorithm Confusion Attack

Consider a scenario where a developer uses HS256 (HMAC-SHA256) to sign a JWT but does not properly validate the algorithm in the token. An attacker could craft a token with a different algorithm, such as none, and the server might accept it due to improper validation.

#### Vulnerable Code Example

Here is an example of a vulnerable implementation in Python:

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
        return decoded['user']
    except jwt.exceptions.DecodeError:
        return None
```

In this example, the `jwt.decode` function is called with the `algorithms` parameter set to `['HS256']`. However, if the attacker crafts a token with a different algorithm, such as `none`, the server might still accept it.

#### Exploiting the Vulnerability

An attacker could craft a token with the `none` algorithm and pass it to the server:

```plaintext
eyJhbGciOiJub25lIiwidHlwIjoianN1In0.eyJzdWIiOiJKb2huIERvZSJ9.
```

Breaking it down:

- **Header**:
  ```json
  {
    "alg": "none",
    "typ": "jws"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "John Doe"
  }
  ```

- **Signature**: Empty since the algorithm is `none`.

The server would accept this token because it does not properly validate the algorithm.

### Real-World Examples

#### CVE-2017-1000488

This CVE describes a vulnerability in the `jsonwebtoken` library for Node.js, where the library did not properly validate the algorithm used in the token. This allowed attackers to craft tokens with the `none` algorithm and gain unauthorized access.

#### CVE-2019-16759

This CVE describes a vulnerability in the `auth0/node-jsonwebtoken` library, where the library did not properly validate the algorithm used in the token. This allowed attackers to craft tokens with the `none` algorithm and gain unauthorized access.

### How to Prevent / Defend

#### Secure Coding Practices

To prevent algorithm confusion attacks, ensure that the server properly validates the algorithm used in the token. Here are some steps to follow:

1. **Validate the Algorithm**: Ensure that the server only accepts tokens with the expected algorithm. For example, if the server expects HS256, it should reject any token with a different algorithm.

2. **Use Strong Algorithms**: Use strong algorithms like HS256, RS256, or ES256. Avoid using weak algorithms like HS256 with a short secret.

3. **Do Not Allow `none` Algorithm**: Explicitly disallow the `none` algorithm. This prevents attackers from crafting tokens with no signature.

#### Example of Secure Code

Here is an example of secure code in Python:

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'], options={'verify_signature': True})
        return decoded['user']
    except jwt.exceptions.DecodeError:
        return None
```

In this example, the `jwt.decode` function is called with the `options` parameter set to `{'verify_signature': True}`. This ensures that the server verifies the signature of the token.

#### Detection

To detect algorithm confusion attacks, monitor the logs for any unexpected algorithms in the tokens. You can also use tools like Burp Suite or OWASP ZAP to intercept and analyze the tokens.

#### Hardening

To harden the system against algorithm confusion attacks, follow these steps:

1. **Update Libraries**: Ensure that all libraries are up-to-date and patched against known vulnerabilities.

2. **Use Secure Configurations**: Configure the server to only accept tokens with the expected algorithm.

3. **Monitor Logs**: Monitor the logs for any unexpected behavior, such as tokens with unexpected algorithms.

### Conclusion

Algorithm confusion attacks are a serious threat to web applications that use JWTs. By understanding the structure of JWTs and the types of algorithms used, you can better defend against these attacks. Always validate the algorithm used in the token and use strong algorithms to ensure the security of your application.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including JWT attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and understand JWT attacks in depth.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[03-Introduction to JWT and Algorithm Confusion|Introduction to JWT and Algorithm Confusion]]
