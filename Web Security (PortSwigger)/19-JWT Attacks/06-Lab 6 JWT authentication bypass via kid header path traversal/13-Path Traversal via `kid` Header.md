---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Path Traversal via `kid` Header

One specific vulnerability involves the `kid` (key ID) header in JWTs. The `kid` header is used to identify the key used to sign the JWT. If the application does not properly validate the `kid` value, an attacker might exploit this to perform path traversal attacks.

### Exploitation Steps

1. **Identify the Vulnerability**:
   - The application uses the `kid` header to determine which key to use for verifying the JWT.
   - The `kid` value is not properly validated, allowing an attacker to specify arbitrary paths.

2. **Craft the JWT**:
   - The attacker crafts a JWT with a `kid` value that points to a malicious file path.
   - The attacker uses a base64-encoded null byte to bypass restrictions on empty strings.

3. **Base64 Encoding Null Byte**:
   - A null byte (`\x00`) is often used to terminate strings in C-based languages.
   - To encode a null byte in Base64, the attacker uses `AA==`.

```plaintext
Base64(\x00) = AA==
```

4. **Generate the JWT**:
   - The attacker uses a tool like the JOT editor extension to generate the JWT.
   - The attacker deletes the default key and generates a new symmetric key with the `k` attribute set to `AA==`.

```plaintext
Header:
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "AA=="
}

Payload:
{
  "sub": "attacker",
  "admin": true
}
```

5. **Sign the JWT**:
   - The attacker signs the JWT using the generated key.
   - The signature is computed using the null byte as the key.

```plaintext
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  "\x00")
```

6. **Send the JWT**:
   - The attacker sends the crafted JWT to the server.
   - The server reads the `kid` value and attempts to load the corresponding key from the specified path.
   - If the path traversal is successful, the server loads the null byte as the key and verifies the signature.

### Example Attack Scenario

Consider a web application that uses JWTs for authentication. The application expects the `kid` header to point to a valid key file. However, due to a lack of proper validation, an attacker can exploit this to read arbitrary files.

#### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        kid = jwt.get_unverified_header(token)['kid']
        with open(f'/path/to/keys/{kid}', 'r') as f:
            key = f.read()
        decoded = jwt.decode(token, key, algorithms=['HS256'])
        return decoded['admin']
    except Exception as e:
        print(e)
        return False
```

#### Attacker's Crafted JWT

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkFBPT0ifQ.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### Server Response

When the server receives the JWT, it attempts to load the key from `/path/to/keys/AA==`. Since `AA==` decodes to a null byte, the server reads the null byte as the key and verifies the signature.

### Real-World Examples

- **CVE-2021-3504**: This vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to bypass signature verification by manipulating the `kid` header.
- **CVE-2020-14182**: This vulnerability in the `firebase-admin` SDK allowed attackers to bypass authentication by exploiting the `kid` header.

### How to Prevent / Defend

#### Detection

- **Logging**: Implement logging to monitor JWT-related activities.
- **Anomaly Detection**: Use anomaly detection tools to identify unusual patterns in JWT usage.

#### Prevention

- **Validate `kid` Values**: Ensure that the `kid` value is properly validated and does not allow path traversal.
- **Use Strong Keys**: Use strong keys and ensure that they are securely stored.
- **Least Privilege**: Follow the principle of least privilege when handling JWTs.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        kid = jwt.get_unverified_header(token)['kid']
        with open(f'/path/to/keys/{kid}', 'r') as f:
            key = f.read()
        decoded = jwt.decode(token, key, algorithms=['HS256'])
        return decoded['admin']
    except Exception as e:
        print(e)
        return False
```

##### Fixed Code

```python
import jwt
import os

def authenticate(token):
    try:
        kid = jwt.get_unverified_header(token)['kid']
        if not os.path.basename(kid) == kid:
            raise ValueError("Invalid kid value")
        with open(f'/path/to/keys/{kid}', 'r') as f:
            key = f.read()
        decoded = jwt.decode(token, key, algorithms=['HS256'])
        return decoded['admin']
    except Exception as e:
        print(e)
        return False
```

### Mermaid Diagrams

#### JWT Structure

```mermaid
graph TD;
    JWT -->|Base64Url Encode| Header;
    JWT -->|Base64Url Encode| Payload;
    JWT -->|HMACSHA256| Signature;
    Header -->|{"alg":"HS256","typ":"JWT"}| HeaderContent;
    Payload -->|{"sub":"1234567890","name":"John Doe","iat":1516239022}| PayloadContent;
    Signature -->|HMACSHA256(Header + "." + Payload, Secret)| SignatureContent;
```

#### Attack Flow

```mermaid
sequenceDiagram
    participant Attacker
    participant Server
    Attacker->>Server: Send JWT with kid="AA=="
    Server-->>Attacker: Load key from "/path/to/keys/AA=="
    Server-->>Attacker: Verify signature using null byte
    Server-->>Attacker: Return admin access
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive section on JWT attacks.
- **OWASP Juice Shop**: Provides a variety of JWT-related challenges.
- **DVWA**: Has a section dedicated to JWT vulnerabilities.

By thoroughly understanding the structure and potential vulnerabilities of JWTs, developers can implement robust security measures to protect against attacks.

---
<!-- nav -->
[[12-Path Traversal via KID Parameter|Path Traversal via KID Parameter]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[14-Understanding Path Traversal Attacks|Understanding Path Traversal Attacks]]
