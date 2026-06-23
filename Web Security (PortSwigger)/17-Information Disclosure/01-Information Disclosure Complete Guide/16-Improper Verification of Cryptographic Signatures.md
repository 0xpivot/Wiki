---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Improper Verification of Cryptographic Signatures

### What Is Improper Verification of Cryptographic Signatures?

Improper verification of cryptographic signatures occurs when the signature of a message is not properly verified before the message is processed. This can lead to serious security risks, including bypassing authentication and executing unauthorized actions.

### Why Does This Matter?

Cryptographic signatures are used to ensure the integrity and authenticity of messages. If the signature is not properly verified, an attacker can forge messages and bypass security controls. For example, if JSON Web Tokens (JWTs) are not properly verified, an attacker can forge a JWT and bypass authentication.

### How Does This Work Under the Hood?

JSON Web Tokens (JWTs) are a popular format for transmitting claims between parties. A JWT consists of three parts: a header, a payload, and a signature. The header contains metadata about the token, the payload contains the claims, and the signature is used to verify the integrity and authenticity of the token.

Here is an example of a JWT:

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
  "signature": "abcdefg"
}
```

In this example, the JWT contains a header, a payload, and a signature. If the signature is not properly verified, an attacker can forge a JWT and bypass authentication.

### Real-World Examples

One of the most notable examples of improper verification of cryptographic signatures is the OAuth 2.0 bearer token misuse (CVE-2017-15357). In this vulnerability, attackers could forge OAuth 2.0 bearer tokens and bypass authentication, leading to unauthorized access to resources.

### How to Prevent / Defend

#### Detection

To detect improper verification of cryptographic signatures, you can use static code analysis tools like SonarQube or Fortify. These tools scan the source code for patterns that indicate improper verification of cryptographic signatures and flag them for review.

#### Prevention

To prevent improper verification of cryptographic signatures, you should always verify the signature of a message before processing it. For example, when verifying a JWT, you should ensure that the signature is valid and that the claims in the payload are trusted.

Here is an example of verifying a JWT:

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
secret = "my_secret"

try:
    decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
    print(decoded_token)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

In this example, the JWT is verified using the `jwt.decode` function, which checks the signature and ensures that the claims in the payload are trusted.

### Secure Coding Fixes

#### Vulnerable Code

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
decoded_token = jwt.decode(token, options={"verify_signature": False})
print(decoded_token)
```

#### Fixed Code

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
secret = "my_secret"

try:
    decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
    print(decoded_token)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

In the fixed code, the JWT is verified using the `jwt.decode` function, which checks the signature and ensures that the claims in the payload are trusted.

### Hands-On Labs

For hands-on practice with this topic, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises on detecting and preventing improper verification of cryptographic signatures.
- **OWASP Juice Shop**: This lab includes scenarios where cryptographic signatures are not properly verified, and you can practice identifying and fixing these issues.

---
<!-- nav -->
[[15-Identifying Potential Information Disclosure|Identifying Potential Information Disclosure]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[17-Information Disclosure Vulnerabilities|Information Disclosure Vulnerabilities]]
