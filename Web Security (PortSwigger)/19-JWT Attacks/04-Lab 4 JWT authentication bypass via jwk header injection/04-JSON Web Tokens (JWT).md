---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JSON Web Tokens (JWT)

JSON Web Tokens (JWT) are a widely used method for transmitting information between parties as a JSON object. This information is encoded in a compact and URL-safe manner, making it suitable for use in web applications. JWTs consist of three parts: the header, the payload, and the signature. Each part is Base64Url encoded and separated by dots (`.`).

### Structure of a JWT

A typical JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwianRpIjoiMTIzNDU2Nzg5IiwicGF5bG9hZCI6WyJjbGllbnQiXX0.eyJhbGciOiJIUzI1NiIsImtpZCI6IjEifQ.eyJhbGciOiJIUzI1NiIsImtpZCI6IjEifQ
```

This JWT is composed of three parts:

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
2. **Payload**: Contains claims, which are statements about an entity and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it was issued by the expected party.

### Header

The header typically includes two fields:

- `alg`: Algorithm used for signing the token.
- `typ`: Type of the token (usually `JWT`).

Example header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload

The payload contains claims, which are statements about an entity. Claims can be registered (standardized) or custom. Common registered claims include:

- `iss`: Issuer of the token.
- `sub`: Subject of the token.
- `aud`: Audience of the token.
- `exp`: Expiration time of the token.
- `nbf`: Not before time of the token.
- `iat`: Issued at time of the token.
- `jti`: JWT ID (unique identifier).

Example payload:

```json
{
  "iss": "https://example.com",
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "jti": "123456789"
}
```

### Signature

The signature ensures the integrity of the token and verifies that it was issued by the expected party. It is created by taking the encoded header and payload, concatenating them with a dot (`.`), and then signing the result with a secret key or a public/private key pair.

### Asymmetric Cryptography

Asymmetric cryptography uses a pair of keys: a public key and a private key. The public key is used to encrypt data, and the private key is used to decrypt it. Conversely, the private key can be used to sign data, and the public key can be used to verify the signature.

### JSON Web Key (JWK)

JSON Web Key (JWK) is a JSON-based representation of cryptographic keys. A JWK can represent both symmetric and asymmetric keys. For asymmetric keys, a JWK includes fields such as `kty`, `n`, `e`, `d`, `p`, `q`, etc., depending on the key type.

Example JWK for an RSA key:

```json
{
  "kty": "RSA",
  "n": "0vx74L2yf... (long string)",
  "e": "AQAB"
}
```

### JWK Injection Attack

JWK injection is a type of attack that exploits misconfigurations in JWT implementations. Specifically, it targets applications that accept an arbitrary JWK in the JWT header and use it to verify the token's signature.

#### How the Attack Works

1. **Generate a Public/Private Key Pair**: The attacker generates their own public/private key pair.
2. **Inject the Public Key**: The attacker injects their public key into the JWT header using the `jwk` parameter.
3. **Sign the Token**: The attacker signs the token with their private key.
4. **Verification**: If the application is misconfigured to use any key embedded in the `jwk` parameter, it will use the attacker's public key to verify the signature, allowing the attacker to bypass authentication.

#### Example

Let's walk through a detailed example of how this attack can be performed.

1. **Generate a Public/Private Key Pair**:
    - Use a tool like OpenSSL to generate an RSA key pair.
    - Convert the keys to JWK format.

```bash
# Generate RSA key pair
openssl genrsa -out private_key.pem 2048
openssl rsa -pubout -in private_key.pem -out public_key.pem

# Convert to JWK format
cat private_key.pem | openssl rsa -outform der | base64 | tr -d '\n' > private_key.der
cat public_key.pem | openssl rsa -pubin -outform der | base64 | tr -d '\n' > public_key.der

# Use a tool like jwt.io to convert PEM to JWK
```

2. **Inject the Public Key**:
    - Modify the JWT header to include the `jwk` parameter with the attacker's public key.

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "jwk": {
    "kty": "RSA",
    "n": "0vx74L2yf... (long string)",
    "e": "AQAB"
  }
}
```

3. **Sign the Token**:
    - Sign the token with the attacker's private key.

```bash
# Sign the token using the private key
echo -n '{"header":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImp3ayI6eyJrdHkiOiJSU0EiLCJuIjoiMHZ4NzRMMXkmLi4iLCJlIjoiQUFBIn19","payload":"eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwianRpIjoiMTIzNDU2Nzg5IiwicGF5bG9hZCI6WyJjbGllbnQiXX0"}' | jwt.io --sign --key private_key.pem
```

4. **Verification**:
    - The application will use the attacker's public key to verify the signature, allowing the attacker to bypass authentication.

### Real-World Examples

Recent vulnerabilities involving JWK injection include:

- **CVE-2021-22907**: A vulnerability in Auth0's JWT implementation allowed attackers to inject a JWK and bypass authentication.
- **CVE-2022-23277**: A similar vulnerability in Okta's JWT implementation allowed attackers to inject a JWK and gain unauthorized access.

### How to Prevent / Defend

#### Detection

- **Monitor JWT Headers**: Implement logging and monitoring to detect unexpected `jwk` parameters in JWT headers.
- **Security Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, or commercial security scanners to detect potential JWK injection vulnerabilities.

#### Prevention

- **Validate JWT Headers**: Ensure that the application only accepts predefined and trusted JWKs in the JWT header.
- **Use Strong Key Management Practices**: Store and manage cryptographic keys securely. Avoid hardcoding keys in the application code.
- **Implement Strict Validation Rules**: Validate JWT headers and payloads strictly according to the expected schema. Reject tokens with unexpected or malformed headers.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

def authenticate(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": True})
        return decoded["sub"]
    except jwt.exceptions.InvalidTokenError:
        return None
```

##### Fixed Code

```python
import jwt

def authenticate(token):
    try:
        # Define a trusted JWK
        trusted_jwk = {
            "kty": "RSA",
            "n": "trusted_public_key_modulus",
            "e": "AQAB"
        }

        # Decode the token with the trusted JWK
        decoded = jwt.decode(token, trusted_jwk, algorithms=["RS256"])
        return decoded["sub"]
    except jwt.exceptions.InvalidTokenError:
        return None
```

### Configuration Hardening

- **Disable Arbitrary JWK Injection**: Configure the JWT library to reject tokens with arbitrary `jwk` parameters.
- **Use Environment Variables for Keys**: Store cryptographic keys in environment variables rather than hardcoding them in the application.

### Conclusion

JWK injection attacks exploit misconfigurations in JWT implementations, allowing attackers to bypass authentication. By understanding the structure of JWTs, the principles of asymmetric cryptography, and the mechanics of JWK injection, developers can implement robust defenses against these attacks. Regular security audits, strict validation rules, and strong key management practices are essential to preventing such vulnerabilities.

### Practice Labs

For hands-on experience with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on JWT vulnerabilities, including JWK injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: Includes a variety of web application vulnerabilities, including JWT-related issues.

These labs provide practical scenarios to test and reinforce the concepts discussed in this chapter.

---
<!-- nav -->
[[03-How to Prevent  Defend Against JWK Header Injection|How to Prevent  Defend Against JWK Header Injection]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]] | [[05-JWK Header Injection Attack|JWK Header Injection Attack]]
