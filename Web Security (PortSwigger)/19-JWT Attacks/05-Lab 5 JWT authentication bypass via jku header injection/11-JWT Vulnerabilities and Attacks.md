---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Vulnerabilities and Attacks

One of the most critical vulnerabilities associated with JWTs is the ability to manipulate the token's contents. This can lead to unauthorized access and privilege escalation. One such attack vector involves the `jku` header.

### Understanding the `jku` Header

The `jku` (JWK Set URL) header is used to specify the URL of a JSON Web Key (JWK) set. This set contains the keys used to verify the signature of the JWT. If an attacker can inject a malicious `jku` header, they can potentially trick the server into using a different set of keys, allowing them to forge a valid JWT.

#### Example of a JWT with `jku` Header

Consider the following JWT with a `jku` header:

```plaintext
eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJqdGkiOiIyIiwianYiOiIyIiwianUiOiJodHRwczovL2V4YW1wbGUuY29tL2p3ay5qc29uIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQwNjAwMCwiaWF0IjoxNjA2MzIwMDAwfQ.abcdef1234567890
```

Breaking it down:

- **Header**:
  ```json
  {
    "alg": "RS256",
    "kid": "1",
    "jti": "2",
    "jvn": "2",
    "jku": "https://example.com/jwk.json"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "admin",
    "exp": 1606406000,
    "iat": 1606320000
  }
  ```

- **Signature**:
  ```plaintext
  abcdef1234567890
  ```

### Attack Scenario: Injecting a Malicious `jku` Header

An attacker can craft a JWT with a malicious `jku` header pointing to a controlled JWK set. This allows the attacker to sign the JWT with a key that the server will trust, effectively bypassing authentication.

#### Example of a Malicious JWT

```plaintext
eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJqdGkiOiIyIiwianYiOiIyIiwianUiOiJodHRwczovL2F0dGFjaGluZy5jb20vamdrLnNvdW5kIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQwNjAwMCwiaWF0IjoxNjA2MzIwMDAwfQ.abcdef1234567890
```

Breaking it down:

- **Header**:
  ```json
  {
    "alg": "RS256",
    1. "kid": "1",
    2. "jti": "2",
    3. "jvn": "2",
    4. "jku": "https://attacking.com/jwk.signed"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "admin",
    "exp": 1606406000,
    "iat": 1606320000
  }
  ```

- **Signature**:
  ```plaintext
  abcdef1234567890
  ```

### Real-World Example: CVE-2021-22205

CVE-2021-22205 is a real-world example where a vulnerability in the `jku` header allowed attackers to bypass authentication in certain applications. The vulnerability was exploited by injecting a malicious `jku` header, leading to unauthorized access.

### How to Prevent / Defend Against `jku` Header Injection

#### Detection

To detect `jku` header injection attacks, you should monitor your logs for unexpected `jku` headers and validate the integrity of the JWK set URLs.

#### Prevention

1. **Validate JWK Set URLs**: Ensure that the `jku` header points to a trusted URL. Whitelist known good URLs and reject any others.
2. **Use Strong Signing Algorithms**: Use strong signing algorithms like RS256 or ES256 to prevent signature forgery.
3. **Secure JWK Sets**: Ensure that the JWK sets are securely hosted and cannot be tampered with.

#### Secure Coding Fixes

Here is an example of how to implement these defenses in code:

```python
import jwt

# Trusted JWK set URL
trusted_jku = "https://example.com/jwk.json"

def validate_jwt(token):
    try:
        # Extract the jku header
        header = jwt.get_unverified_header(token)
        jku = header.get('jku')

        # Validate the jku header
        if jku != trusted_jku:
            raise ValueError("Invalid jku header")

        # Decode the token
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token
    except Exception as e:
        print(f"Error validating JWT: {e}")
        return None

# Example usage
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJqdGkiOiIyIiwianYiOiIyIiwianUiOiJodHRwczovL2V4YW1wbGUuY29tL2p3ay5qc29uIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQwNjAwMCwiaWF0IjoxNjA2MzIwMDAwfQ.abcdef1234567890"
decoded_token = validate_jwt(token)
print(decoded_token)
```

### Complete Example of HTTP Request and Response

Here is a complete example of an HTTP request and response involving a JWT with a `jku` header:

#### HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Cookie: jwt=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJqdGkiOiIyIiwianYiOiIyIiwianUiOiJodHRwczovL2V4YW1wbGUuY29tL2p3ay5qc29uIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQwNjAwMCwiaWF0IjoxNjA2MzIwMDAwfQ.abcdef1234567890

{
  "username": "admin",
  "password": "password"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 27 Jul 2020 12:28:53 GMT
Content-Type: application/json
Set-Cookie: jwt=eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJqdGkiOiIyIiwianYiOiIyIiwianUiOiJodHRwczovL2V4YW1wbGUuY29tL2p3ay5qc29uIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQwNjAwMCwiaWF0IjoxNjA2MzIwMDAwfQ.abcdef1234567890; Path=/; HttpOnly

{
  "message": "Login successful"
}
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security attacks, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and testing web security concepts.

These labs provide a safe environment to explore and understand the intricacies of JWT attacks and how to defend against them.

By thoroughly understanding the structure and vulnerabilities of JWTs, you can better protect your applications from unauthorized access and ensure secure authentication mechanisms.

---
<!-- nav -->
[[10-JWT Key Management|JWT Key Management]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[12-Understanding the `jku` Header Injection Attack|Understanding the `jku` Header Injection Attack]]
