---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT and CSRF Tokens

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe means of representing claims to be transferred between two parties. It allows you to encode information in a token that can be signed (using a secret) or encrypted. JWTs are commonly used for authentication and information exchange in web applications.

#### Structure of a JWT

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the authenticity of the sender.

Here is an example of a JWT:

```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking down the components:

- **Header**:
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
  ```

- **Signature**:
  ```plaintext
  SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  ```

#### Why JWT Matters

JWTs provide a secure way to transmit information between parties as a JSON object. They are widely used in web applications for authentication and authorization purposes. By using JWTs, developers can ensure that the transmitted information is both secure and verifiable.

### What is a CSRF Token?

Cross-Site Request Forgery (CSRF) tokens are used to protect against CSRF attacks. A CSRF attack occurs when an attacker tricks a user into performing an unwanted action on a website where they are authenticated. CSRF tokens help mitigate this risk by ensuring that each request is legitimate.

#### How CSRF Tokens Work

When a user visits a webpage, the server generates a unique CSRF token and sends it to the client. This token is then included in subsequent requests made by the client. The server verifies the presence and validity of the CSRF token before processing the request. If the token is missing or invalid, the request is rejected.

Here is an example of a CSRF token in a form:

```html
<form method="POST">
  <input type="hidden" name="csrf_token" value="abc123">
  <!-- Other form fields -->
</form>
```

### Why CSRF Tokens Matter

CSRF tokens are crucial for maintaining the security of web applications. Without them, attackers could exploit authenticated sessions to perform actions on behalf of the user, leading to unauthorized access and potential data loss.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/02-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[04-Introduction to JWT and Its Role in Web Security|Introduction to JWT and Its Role in Web Security]]
