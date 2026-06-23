---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attacks: Bypassing Authentication via `kid` Header Path Traversal

### Introduction to JWT and Its Vulnerabilities

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information is encoded in a compact, URL-safe string format and can be signed to ensure the integrity and authenticity of the data. JWTs are commonly used for authentication and authorization purposes in web applications.

However, JWTs can also introduce significant security vulnerabilities if not implemented correctly. One such vulnerability is related to the `kid` (key ID) header, which can be exploited through path traversal attacks. This attack vector allows an attacker to manipulate the JWT to gain unauthorized access to sensitive resources.

### Understanding JWT Structure

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token by verifying that the header and payload have not been tampered with.

Here is an example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking down the components:

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

### Symmetric Algorithms and Their Risks

Symmetric algorithms, such as HMAC-SHA256 (`HS256`), use the same secret key for both encryption and decryption. While this simplifies key management, it also introduces risks if the key is compromised or improperly managed.

#### Example of a Symmetric Algorithm in Action

Consider the following scenario where a JWT is signed using a symmetric algorithm:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user123",
    "name": "Alice",
    "admin": false
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

If an attacker knows the secret key used to sign the JWT, they can modify the payload and re-sign it, effectively bypassing authentication checks.

### The `kid` Header and Path Traversal Attack

The `kid` header is used to identify which key should be used to verify the signature of the JWT. In some implementations, the `kid` value can be manipulated to point to a different key file, potentially leading to a path traversal attack.

#### How Path Traversal Works

Path traversal attacks allow an attacker to access files outside of the intended directory structure by manipulating input parameters. In the context of JWTs, an attacker might use the `kid` header to specify a path to a file that contains a known key.

For example, consider the following JWT with a `kid` header:

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "/etc/passwd"
  },
  "payload": {
    "sub": "user123",
    "name": "Alice",
    "admin": false
  },
  "signature": "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

If the server is configured to read the key from the path specified in the `kid` header, an attacker could potentially read the contents of `/etc/passwd`, which might contain a known key.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example of a JWT vulnerability that was discovered in the Auth0 platform. The vulnerability allowed attackers to bypass authentication by manipulating the `kid` header to point to a different key file.

#### Detailed Explanation of CVE-2021-21972

In this case, the Auth0 platform allowed the `kid` header to be manipulated, leading to a path traversal attack. An attacker could specify a path to a file containing a known key, thereby gaining unauthorized access to the system.

### Lab Setup: Bypassing Authentication via `kid` Header Path Traversal

To demonstrate this attack, we will set up a simple web application that uses JWTs for authentication. The application will be configured to use a symmetric algorithm and will allow the `kid` header to be manipulated.

#### Step-by-Step Lab Instructions

1. **Set Up the Application**:
   - Create a basic web application that uses JWTs for authentication.
   - Configure the application to use a symmetric algorithm (e.g., `HS256`).

2. **Generate a JWT**:
   - Generate a JWT with a `kid` header pointing to a known key file.
   - Modify the payload to include an `admin` claim set to `true`.

3. **Send the Modified JWT**:
   - Send the modified JWT to the server and observe the response.

#### Code Example: Generating a JWT

Here is an example of generating a JWT using Python:

```python
import jwt
import datetime

# Secret key
secret_key = "my_secret_key"

# Payload
payload = {
    "sub": "user123",
    "name": "Alice",
    "admin": False,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

# Header
header = {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "/etc/passwd"
}

# Generate JWT
token = jwt.encode(payload, secret_key, algorithm="HS256", headers=header)

print(token)
```

#### Sending the JWT to the Server

When sending the JWT to the server, the server will attempt to verify the signature using the key specified in the `kid` header. If the server reads the key from the specified path, the attacker can bypass authentication.

### Detection and Prevention

#### How to Detect the Attack

To detect this attack, you can monitor for unusual `kid` header values or unexpected file accesses. Additionally, you can implement logging and alerting mechanisms to notify administrators of suspicious activity.

#### How to Prevent the Attack

To prevent this attack, follow these best practices:

1. **Validate the `kid` Header**:
   - Ensure that the `kid` header value is validated and does not allow path traversal.
   - Use a whitelist of allowed `kid` values.

2. **Use Asymmetric Algorithms**:
   - Consider using asymmetric algorithms (e.g., RSA) instead of symmetric algorithms.
   - This reduces the risk of key compromise.

3. **Secure Key Management**:
   - Store keys securely and limit access to them.
   - Use environment variables or secure vaults to manage keys.

4. **Implement Input Validation**:
   - Validate all input parameters to prevent injection attacks.
   - Use libraries and frameworks that provide built-in validation mechanisms.

#### Secure Coding Fix

Here is an example of a secure coding fix:

```python
import jwt
import datetime

# Secret key
secret_key = "my_secret_key"

# Payload
payload = {
    "sub": "user123",
    "name": "Alice",
    "admin": False,
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}

# Header
header = {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "valid_kid_value"
}

# Generate JWT
token = jwt.encode(payload, secret_key, algorithm="HS256", headers=header)

print(token)
```

### Conclusion

JWTs are a powerful tool for securing web applications, but they must be implemented correctly to avoid vulnerabilities. By understanding the risks associated with the `kid` header and implementing proper security measures, you can protect your application from path traversal attacks.

### Further Reading and Practice Labs

For further practice and deeper understanding, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By engaging with these resources, you can gain hands-on experience and reinforce your understanding of JWT security.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/07-JSON Web Tokens (JWT)|JSON Web Tokens (JWT)]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[09-JWT Authentication Bypass via `kid` Header Path Traversal|JWT Authentication Bypass via `kid` Header Path Traversal]]
