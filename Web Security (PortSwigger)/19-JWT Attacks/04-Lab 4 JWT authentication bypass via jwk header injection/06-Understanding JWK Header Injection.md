---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding JWK Header Injection

Now that we have a basic understanding of JWTs, let's dive into the specific attack we will be discussing: JWK Header Injection.

### What is JWK Header Injection?

JWK Header Injection is a type of attack where an attacker injects a malicious JWK into the JWT header. The JWK is used to verify the signature of the JWT, and if the server fails to validate the source of the JWK, the attacker can use a custom JWK to forge a valid signature.

#### How Does JWK Header Injection Work?

1. **Attacker Injects Malicious JWK**: The attacker modifies the JWT header to include a JWK that points to a public key controlled by the attacker.
2. **Server Verifies Signature Using Malicious JWK**: The server uses the injected JWK to verify the signature of the JWT, which results in a successful validation even though the token was forged.
3. **Bypasses Authentication**: The attacker gains unauthorized access to protected resources.

### Example of JWK Header Injection

Let's consider a scenario where a web application uses JWTs for authentication. The server supports the `jwk` parameter in the JWT header, which is used to embed the correct verification key directly in the token.

#### Vulnerable JWT Header

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "jwk": {
    "kty": "RSA",
    "n": "0vxWJq...",
    "e": "AQAB"
  }
}
```

The attacker can modify the `jwk` parameter to point to a public key controlled by them.

#### Attacker's Modified JWT Header

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "jwk": {
    "kty": "RSA",
    "n": "attacker_public_key_n_value",
    "e": "attacker_public_key_e_value"
  }
}
```

By using this modified JWT, the attacker can bypass the authentication mechanism and gain unauthorized access to the application.

### Real-World Example: CVE-2021-21974

In the `jwt-go` library, a vulnerability allowed attackers to bypass authentication by manipulating the JWT header. The library failed to validate the source of the JWK, allowing attackers to inject a malicious JWK and forge a valid signature.

#### Exploit Details

- **Vulnerable Code**:
  ```go
  func ParseWithClaims(token string, claims Claims, keyFunc Keyfunc) (*Token, error) {
      // ...
      if token.Header["jwk"] != nil {
          jwk := token.Header["jwk"].(map[string]interface{})
          // ...
      }
      // ...
  }
  ```

- **Exploit**:
  ```json
  {
    "alg": "RS256",
    "typ": "JWT",
    "jwk": {
      "kty": "RSA",
      "n": "attacker_public_key_n_value",
      "e": "attacker_public_key_e_value"
    }
  }
  ```

### How to Prevent / Defend Against JWK Header Injection

To prevent JWK Header Injection attacks, it is crucial to implement proper validation and security measures.

#### Secure Coding Practices

1. **Validate the Source of JWK**: Ensure that the JWK embedded in the JWT header comes from a trusted source. This can be achieved by maintaining a whitelist of trusted JWKs or by verifying the JWK against a known set of keys.
2. **Use Strong Signing Algorithms**: Use strong signing algorithms like RS256 or ES256 to ensure the integrity of the JWT.
3. **Avoid Embedding JWK in JWT**: Instead of embedding the JWK in the JWT header, use a separate mechanism to distribute and validate the JWK.

#### Example of Secure JWT Header

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

#### Secure Configuration

1. **Whitelist Trusted JWKs**: Maintain a list of trusted JWKs and validate the JWK embedded in the JWT header against this list.
2. **Use a Trusted Key Store**: Use a trusted key store to manage and distribute JWKs securely.

#### Detection and Prevention

1. **Monitor JWT Headers**: Implement monitoring and logging to detect any suspicious modifications to the JWT header.
2. **Regular Security Audits**: Conduct regular security audits to identify and mitigate potential vulnerabilities in JWT implementations.

### Complete Example

Let's walk through a complete example of how to implement and secure JWTs against JWK Header Injection attacks.

#### Vulnerable Implementation

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'password':
        token = jwt.encode({'sub': username}, 'secret', algorithm='RS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/admin', methods=['GET'])
def admin():
    token = request.headers.get('Authorization').split()[1]
    try:
        decoded = jwt.decode(token, 'secret', algorithms=['RS256'])
        if decoded['sub'] == 'admin':
            return jsonify({'message': 'Welcome, admin!'})
        else:
            return jsonify({'error': 'Unauthorized'}), 401
    except jwt.exceptions.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

#### Secure Implementation

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

trusted_jwks = [
    {
        "kty": "RSA",
        "n": "trusted_public_key_n_value",
        "e": "trusted_public_key_e_value"
    }
]

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'password':
        token = jwt.encode({'sub': username}, 'secret', algorithm='RS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/admin', methods=['GET'])
def admin():
    token = request.headers.get('Authorization').split()[1]
    try:
        header = jwt.get_unverified_header(token)
        if 'jwk' in header:
            jwk = header['jwk']
            if jwk not in trusted_jwks:
                return jsonify({'error': 'Unauthorized JWK'}), 401

        decoded = jwt.decode(token, 'secret', algorithms=['RS256'], audience='admin')
        if decoded['sub'] == 'admin':
            return jsonify({'message': 'Welcome, admin!'})
        else:
            return jsonify({'error': 'Unauthorized'}), 
    except jwt.exceptions.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

### HTTP Request and Response

#### Vulnerable Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

#### Vulnerable Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.Rs256_signature"
}
```

#### Secure Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

#### Secure Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.Rs256_signature"
}
```

### Common Pitfalls

1. **Embedding JWK in JWT Header**: Avoid embedding the JWK in the JWT header. Instead, use a separate mechanism to distribute and validate the JWK.
2. **Weak Signing Algorithms**: Use strong signing algorithms like RS256 or ES256 to ensure the integrity of the JWT.
3. **Lack of Validation**: Ensure that the JWK embedded in the JWT header comes from a trusted source. Validate the JWK against a known set of keys.

### Practice Labs

To practice and understand JWT attacks better, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to JWT attacks, including JWK Header Injection.
- **OWASP Juice Shop**: Provides a comprehensive set of labs for practicing web security, including JWT-related vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Offers a range of web application vulnerabilities, including JWT attacks.

By thoroughly understanding and implementing the necessary security measures, you can effectively prevent JWK Header Injection attacks and ensure the security of your web applications.

---

This completes our detailed exploration of JWT attacks, specifically focusing on JWK Header Injection. By understanding the concepts, real-world examples, and secure coding practices, you can effectively defend against these types of attacks.

---
<!-- nav -->
[[05-JWK Header Injection Attack|JWK Header Injection Attack]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/07-Practice Questions & Answers|Practice Questions & Answers]]
