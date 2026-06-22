---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the message and ensure that it has not been tampered with.

The structure can be visualized as follows:

```mermaid
graph LR
    A[Header] --> B[Payload]
    B --> C[Signature]
```

### Example of a JWT

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

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

### Decoding a JWT

To decode a JWT, you can use online tools or libraries. Here’s an example using Python:

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
decoded_token = jwt.decode(token, options={"verify_signature": False})
print(decoded_token)
```

Output:
```json
{
    "sub": "1109994",
    "name": "John Doe",
    "iat": 1516239022
}
```

### JWT Authentication Bypass via Algorithm Confusion

Algorithm confusion is a vulnerability where the server does not properly validate the algorithm used to sign the JWT. This allows an attacker to craft a token using a different algorithm than what the server expects, potentially bypassing authentication.

#### Example Scenario

Consider a web application that uses JWT for authentication. The application expects tokens to be signed using the `HS256` algorithm. An attacker crafts a token using the `none` algorithm, which effectively disables signature validation.

#### Crafting a Malicious Token

Here’s how an attacker might craft a malicious token:

1. **Create the Header**:
   ```json
   {
     "alg": "none",
     "typ": "JWT"
   }
   ```

2. **Create the Payload**:
   ```json
   {
     "sub": "admin",
     "name": "Admin User",
     "iat": 1516239022
   }
   ```

3. **Combine the Parts**:
   ```plaintext
   eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbiBVc2VyIiwiaWF0IjoxNTE2MzEwMDIyfQ.
   ```

Notice that the signature part is empty since the `none` algorithm does not require a signature.

#### Exploiting the Vulnerability

An attacker sends this crafted token to the server, which may accept it due to the lack of proper algorithm validation.

### Real-World Examples

#### CVE-2017-15372

This CVE describes a vulnerability in the `jsonwebtoken` library for Node.js. The library did not properly validate the algorithm used in the JWT, allowing attackers to craft tokens with the `none` algorithm.

#### CVE-2020-13958

This CVE details a vulnerability in the `auth0/node-jsonwebtoken` library. Similar to the previous CVE, the library failed to validate the algorithm, leading to potential bypasses.

### How to Prevent / Defend

#### Detection

To detect algorithm confusion vulnerabilities, you can:

1. **Review Code**: Ensure that the JWT library being used properly validates the algorithm.
2. **Use Tools**: Utilize security tools like `jwt.io` to test JWTs and identify potential issues.

#### Prevention

To prevent algorithm confusion vulnerabilities:

1. **Validate Algorithms**: Ensure that the server only accepts tokens signed with the expected algorithms.
2. **Use Secure Libraries**: Use well-maintained and secure JWT libraries that properly handle algorithm validation.

#### Secure Coding Fixes

Here’s an example of how to securely validate JWTs in Python using the `PyJWT` library:

```python
import jwt

def validate_jwt(token, secret):
    try:
        # Decode the token with HS256 algorithm
        decoded_token = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_token
    except jwt.exceptions.InvalidTokenError:
        return None

# Example usage
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
secret = "your_secret_key"

valid_token = validate_jwt(token, secret)
if valid_token:
    print("Valid token:", valid_token)
else:
    print("Invalid token")
```

#### Configuration Hardening

Ensure that your JWT configuration is hardened:

1. **Set Allowed Algorithms**: Specify allowed algorithms in your JWT configuration.
2. **Use Strong Secrets**: Use strong, unique secrets for signing JWTs.

### Conclusion

Understanding and preventing JWT algorithm confusion vulnerabilities is crucial for maintaining the security of web applications. By ensuring proper validation and using secure coding practices, developers can mitigate these risks effectively.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including JWT-related ones.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for learning web security through practical exercises.

These resources will help you gain a deeper understanding of JWT vulnerabilities and how to defend against them.

---
<!-- nav -->
[[07-How to Prevent  Defend Against Algorithm Confusion|How to Prevent  Defend Against Algorithm Confusion]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[09-JWT Attacks Algorithm Confusion Vulnerability|JWT Attacks Algorithm Confusion Vulnerability]]
