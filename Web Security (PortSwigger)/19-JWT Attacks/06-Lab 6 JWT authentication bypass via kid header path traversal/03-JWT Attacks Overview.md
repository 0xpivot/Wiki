---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks Overview

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs are commonly used for authentication and information exchange due to their compact, URL-safe form. However, JWTs can be vulnerable to various attacks if not implemented correctly.

### What is a JWT?

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the token. It is generated using the header, the payload, and a secret.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### How JWT Works

The JWT is created by the server and sent to the client. The client then sends the token back to the server with each request. The server verifies the signature to ensure the token hasn't been tampered with and checks the claims to determine whether the request should be granted.

#### Example of JWT Creation

```python
import jwt
import datetime

# Define the payload
payload = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": datetime.datetime.utcnow()
}

# Define the secret key
secret_key = "your_secret_key"

# Create the JWT
token = jwt.encode(payload, secret_key, algorithm="HS256")
print(token)
```

### Common JWT Vulnerabilities

1. **None Algorithm Attack**
2. **Path Traversal Attack**
3. **Token Injection Attack**

---
<!-- nav -->
[[02-Introduction to JWT and Its Usage in Web Applications|Introduction to JWT and Its Usage in Web Applications]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[04-JWT Overview|JWT Overview]]
