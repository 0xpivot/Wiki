---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely adopted standard for transmitting information between parties in a compact, URL-safe manner. They are commonly used for authentication and information exchange in web applications. A JWT consists of three parts: the header, the payload, and the signature. Each part is Base64Url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

This JWT can be broken down into three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it was issued by a trusted party.

### Header

The header typically includes two fields:

- `alg`: Algorithm used to sign the token.
- `typ`: Type of the token (usually `JWT`).

For example:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

The payload contains claims, which are statements about an entity. Claims can be registered or custom. Common registered claims include:

- `iss`: Issuer of the token.
- `sub`: Subject of the token (usually the user ID).
- `aud`: Audience of the token.
- `exp`: Expiration time of the token.
- `nbf`: Not before time.
- `iat`: Issued at time.

For example:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

### Signature

The signature is created by taking the encoded header and payload, concatenating them with a dot (`.`), and then signing the result using the algorithm specified in the header. The secret used for signing is kept confidential and known only to the issuer and the intended recipient.

For example, if the header and payload are:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ
```

And the secret is `secret`, the signature would be:

```
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Thus, the complete JWT would be:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### JWT in Web Applications

JWTs are often used in web applications for stateless authentication. When a user logs in, the server generates a JWT and sends it back to the client. The client stores the JWT (often in a cookie or local storage) and includes it in subsequent requests to authenticate the user.

### Example HTTP Request with JWT

Here is an example of an HTTP request that includes a JWT in the `Authorization` header:

```http
GET /api/user HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Example HTTP Response

The corresponding HTTP response might look like this:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "user_id": "1234567890",
  "username": "john.doe",
  "email": "john.doe@example.com"
}
```

### Flawed Signature Verification

One common vulnerability in JWT implementations is flawed signature verification. If the server does not properly validate the signature, an attacker can modify the payload and still have a valid token.

#### Real-World Example: CVE-2021-22919

CVE-2021-22919 is a vulnerability in the Spring framework where the `JwtAuthenticationProvider` did not properly validate the signature of the JWT. An attacker could craft a JWT with a modified payload and still authenticate successfully.

### Attack Scenario

Let's consider the scenario described in the lecture transcript. We will use Burp Suite to intercept and manipulate the JWT.

#### Step-by-Step Attack

1. **Intercept the Request**:
   - Use Burp Suite to intercept the HTTP request containing the JWT.
   - The JWT is stored in a cookie named `Session`.

2. **Modify the JWT**:
   - Decode the JWT to view its contents.
   - Modify the payload to change the user ID or other sensitive information.
   - Re-sign the JWT with a different key or algorithm if possible.

3. **Send the Modified Request**:
   - Send the modified request to the server.
   - If the server does not properly verify the signature, the modified JWT will be accepted.

#### Example Code

Here is an example of how to decode and modify a JWT using Python:

```python
import base64
import json

# Decode the JWT
def decode_jwt(jwt):
    header, payload, signature = jwt.split('.')
    decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
    decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
    return json.loads(decoded_header), json.loads(decoded_payload), signature

# Modify the payload
def modify_payload(payload, new_user_id):
    payload['sub'] = new_user_id
    return payload

# Encode the JWT
def encode_jwt(header, payload, signature):
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).rstrip(b'=')
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).rstrip(b'=')
    return f"{encoded_header.decode('utf-8')}.{encoded_payload.decode('utf-8')}.{signature}"

# Example usage
jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
header, payload, signature = decode_jwt(jwt)
new_payload = modify_payload(payload, "9876543210")
modified_jwt = encode_jwt(header, new_payload, signature)
print(modified_jwt)
```

### How to Prevent / Defend

To prevent JWT attacks, ensure proper signature verification and follow best practices:

1. **Verify the Signature**:
   - Always verify the signature of the JWT using the appropriate key and algorithm.
   - Use libraries that handle signature verification securely.

2. **Use Strong Algorithms**:
   - Use strong algorithms like `RS256` instead of `HS256`.
   - Ensure the private key is kept secure and not exposed.

3. **Validate Claims**:
   - Validate all claims in the payload to ensure they are within expected ranges.
   - Use libraries that provide built-in validation mechanisms.

4. **Secure Storage**:
   - Store JWTs securely in cookies or local storage.
   - Set the `HttpOnly` flag on cookies to prevent access via JavaScript.

5. **Regular Audits**:
   - Regularly audit JWT implementations to identify and fix vulnerabilities.
   - Follow security advisories and update dependencies promptly.

### Example Secure Configuration

Here is an example of a secure JWT configuration using Node.js and the `jsonwebtoken` library:

```javascript
const jwt = require('jsonwebtoken');

// Secret key
const secretKey = 'your_secret_key';

// Generate JWT
function generateToken(user) {
  const payload = {
    sub: user.id,
    name: user.name,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hour expiration
  };
  return jwt.sign(payload, secretKey, { algorithm: 'HS256' });
}

// Verify JWT
function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, secretKey);
    return decoded;
  } catch (err) {
    throw new Error('Invalid token');
  }
}

// Example usage
const user = { id: '1234567890', name: 'John Doe' };
const token = generateToken(user);
console.log(token);

try {
  const decoded = verifyToken(token);
  console.log(decoded);
} catch (err) {
  console.error(err.message);
}
```

### Conclusion

JWTs are a powerful tool for stateless authentication in web applications. However, they must be implemented securely to prevent attacks. By verifying signatures, using strong algorithms, validating claims, and securing storage, developers can mitigate the risks associated with JWTs.

### Practice Labs

To practice JWT attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT manipulation.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning and testing web security concepts.

By working through these labs, you can gain hands-on experience with JWT attacks and defenses, enhancing your understanding and skills in web security.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/02-Introduction to JWT Attacks|Introduction to JWT Attacks]]
