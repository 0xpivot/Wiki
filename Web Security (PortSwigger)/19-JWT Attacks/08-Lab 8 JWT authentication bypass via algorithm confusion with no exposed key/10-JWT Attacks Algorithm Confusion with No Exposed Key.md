---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks: Algorithm Confusion with No Exposed Key

### Introduction to JWT and Asymmetric Encryption

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs consist of three parts: a header, a payload, and a signature. The header typically contains metadata about the token, such as the type of token and the signing algorithm used. The payload contains the actual data being transmitted, and the signature ensures the integrity and authenticity of the token.

Asymmetric encryption, also known as public-key cryptography, uses a pair of keys: a public key and a private key. The public key is used to encrypt messages, and the private key is used to decrypt them. This allows anyone to send an encrypted message using the public key, but only the holder of the private key can decrypt it. One common asymmetric encryption algorithm is RSA (Rivest–Shamir–Adleman).

### JWT Authentication Bypass via Algorithm Confusion

In the context of JWTs, algorithm confusion occurs when the server does not properly validate the algorithm specified in the JWT's header. This can lead to a situation where an attacker can manipulate the algorithm to use a different, potentially weaker, encryption scheme. Specifically, if the server is configured to use an asymmetric algorithm like RSA, but the attacker can force it to use a symmetric algorithm instead, the security of the token can be compromised.

#### Example Scenario

Consider a web application that uses JWTs for authentication. The application expects the JWTs to be signed using RSA, which requires a private key to sign and a public key to verify. However, due to a flaw in the implementation, the server does not properly validate the algorithm specified in the JWT header. An attacker can exploit this by crafting a JWT with a symmetric algorithm like HMAC-SHA256, which uses a shared secret key for both signing and verification.

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

If the server accepts this token and verifies it using the public key intended for RSA, the verification will fail because the public key cannot be used to verify a symmetrically signed token. However, if the server is misconfigured to accept any algorithm without proper validation, the attacker can craft a token that bypasses authentication.

### Obtaining the Public Key

In many cases, the public key required to verify the JWT is publicly accessible. However, in some scenarios, the public key might not be directly available. In such cases, an attacker might attempt to derive the public key from other sources, such as signed JWTs.

#### Deriving the Public Key from Signed JWTs

The process of deriving the public key from signed JWTs involves exploiting mathematical properties of the RSA algorithm. While it is not possible to derive the private key from a JWT, it is sometimes possible to derive the public key under certain conditions.

For RSA, the public key consists of the modulus \( n \) and the public exponent \( e \). The modulus \( n \) is the product of two large prime numbers, and the public exponent \( e \) is usually a small number like 65537. Given two signed JWTs, an attacker can use these to derive the public key.

```mermaid
sequenceDiagram
    participant Attacker
    participant Server
    participant Tool

    Attacker->>Server: Send two signed JWTs
    Server-->>Tool: Provide signed JWTs
    Tool-->>Attacker: Derived public key
```

### Real-World Examples and Recent Breaches

Several real-world examples and recent breaches have highlighted the importance of proper JWT implementation and validation:

- **CVE-2020-14774**: A vulnerability in the `jwt-go` library allowed attackers to bypass authentication by manipulating the algorithm field in the JWT header. This led to widespread adoption of more secure libraries and practices.
- **Capital One Data Breach (2019)**: Although not directly related to JWT, the breach highlighted the importance of proper key management and validation in cryptographic systems.

### Complete Code Example

Let's walk through a complete example of how an attacker might exploit algorithm confusion and derive the public key.

#### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("Authenticated successfully:", decoded)
    except jwt.exceptions.DecodeError:
        print("Invalid token")

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
authenticate(token)
```

#### Secure Code

To prevent such attacks, ensure proper validation of the algorithm and use a secure library that enforces strict checks.

```python
import jwt

def authenticate_secure(token):
    try:
        decoded = jwt.decode(token, "secret", algorithms=["HS256"])
        print("Authenticated successfully:", decoded)
    except jwt.exceptions.InvalidTokenError:
        print("Invalid token")

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
authenticate_secure(token)
```

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns in JWT usage, such as unexpected algorithms or repeated failed authentication attempts.
- **Security Tools**: Use security tools like Burp Suite, OWASP ZAP, or custom scripts to scan for vulnerabilities related to JWT implementation.

#### Prevention

- **Strict Validation**: Ensure that the server strictly validates the algorithm specified in the JWT header and only accepts the expected algorithms.
- **Secure Libraries**: Use well-maintained and secure libraries for JWT handling, such as `pyjwt` with proper configuration.

#### Secure Coding Practices

- **Key Management**: Properly manage and protect cryptographic keys. Ensure that private keys are kept secure and not exposed.
- **Algorithm Configuration**: Configure the JWT library to enforce strict algorithm validation and reject unsupported algorithms.

### Hands-On Labs

For practical experience with JWT attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT manipulation and algorithm confusion.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including JWT-related ones.
- **DVWA (Damn Vulnerable Web Application)**: Contains exercises on web application security, including JWT vulnerabilities.

By thoroughly understanding the concepts, mechanisms, and practical applications of JWT attacks and defenses, you can better secure your applications against such vulnerabilities.

---
<!-- nav -->
[[09-JWT Attacks Algorithm Confusion Vulnerability|JWT Attacks Algorithm Confusion Vulnerability]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[11-Lab Exercises|Lab Exercises]]
