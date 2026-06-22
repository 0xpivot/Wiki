---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Detailed Steps of the Attack

### Step-by-Step Execution

1. **Access the JWKS Endpoint**
   - Send a GET request to the `.well-known/jwks.json` endpoint.
   - Extract the public key from the response.

2. **Modify the JWT Header**
   - Change the `alg` field to `HS256`.
   - Ensure the rest of the header remains unchanged.

3. **Sign the JWT**
   - Use the extracted public key to sign the JWT.
   - Ensure the signature is correct for the modified header and payload.

4. **Send the Modified JWT**
   - Include the modified JWT in the Authorization header of a request to the server.
   - Check if the server accepts the token and grants access.

### Complete Example

#### Raw HTTP Request

```http
POST /api/resource HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
Content-Type: application/json

{
  "data": "some data"
}
```

#### Raw HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 23 Nov 2020 18:25:43 GMT
Content-Type: application/json
Content-Length: 20

{
  "message": "success"
}
```

### Explanation of Each Part

- **Header**: Contains the `alg` and `typ` fields.
- **Payload**: Contains the claims.
- **Signature**: Ensures the integrity of the token.

### Common Pitfalls

- **Incorrectly Extracting the Public Key**: Ensure the public key is correctly extracted from the JWKS response.
- **Modifying the Wrong Field**: Ensure the `alg` field is modified and not other fields.
- **Incorrectly Signing the Token**: Ensure the token is signed correctly with the extracted public key.

---
<!-- nav -->
[[05-Lab Setup and Overview|Lab Setup and Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[07-Detailed Walkthrough|Detailed Walkthrough]]
