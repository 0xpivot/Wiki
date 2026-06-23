---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Authentication Vulnerabilities: Offline Password Cracking

### Background Theory

Authentication is a fundamental aspect of web security, ensuring that users are who they claim to be. This process typically involves verifying credentials such as usernames and passwords. However, vulnerabilities in authentication mechanisms can lead to serious security breaches. One such vulnerability is the improper handling of passwords, particularly when they are stored or transmitted in a manner that allows offline cracking.

### Understanding the Scenario

In the given scenario, a web application has a "stay logged in" feature. When a user logs in and selects this option, the application performs a POST request that includes the username, password, and a flag indicating the "stay logged in" preference. Upon successful login, the server sets two cookies: one for the session and another for the "stay logged in" functionality.

#### Key Concepts

- **Cookies**: Small pieces of data sent from a website and stored on the user's computer by the user's web browser while the user is browsing.
- **Session Cookies**: Used to maintain a user's state across multiple pages.
- **Stay Logged In Cookies**: Typically used to remember a user's login status across sessions.
- **Base64 Encoding**: A binary-to-text encoding scheme that represents binary data in an ASCII string format.
- **MD5 Hash**: A cryptographic hash function that produces a 128-bit (16-byte) hash value. It is commonly used to check data integrity but is not suitable for security purposes due to its vulnerability to collisions.

### Detailed Analysis

#### Step-by-Step Mechanics

1. **User Login**:
    - The user enters their username (`peter`) and password.
    - They select the "stay logged in" option.
    - The browser sends a POST request to the server with these parameters.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 38

username=peter&password=peter&stayLoggedIn=true
```

2. **Server Response**:
    - The server processes the request and verifies the credentials.
    - Upon successful verification, the server sets two cookies:
        - `session`: A session identifier.
        - `stayLoggedIn`: Contains the username and an MD5 hash of the password.

```http
HTTP/1.1 200 OK
Set-Cookie: session=abc123; HttpOnly
Set-Cookie: stayLoggedIn=peter:5d41402abc4b2a76b9719d911017c592; HttpOnly
```

3. **Decoding the Stay Logged In Cookie**:
    - The `stayLoggedIn` cookie value (`peter:5d41402abc4b2a76b9719d911017c592`) is base64 encoded.
    - Decoding it reveals the username and the MD5 hash of the password.

```python
import base64

# Base64 encoded value
encoded_value = "cGV0ZXI6NWQ0MTQwMmFiYzRiMmE3NmI5NzE5ZDkxMTAxN2M1OTI="

# Decode the base64 value
decoded_value = base64.b64decode(encoded_value).decode('utf-8')
print(decoded_value)
```

Output:
```
peter:5d41402abc4b2a76b9719d911017c592
```

4. **Cracking the MD5 Hash**:
    - The MD5 hash (`5d41402abc4b2a76b9719d911017c592`) can be cracked using online services like CrackStation.net.
    - Submitting the hash to CrackStation reveals the plaintext password (`peter`).

### Real-World Examples

#### Recent Breaches

- **LinkedIn Breach (2012)**: LinkedIn stored passwords using SHA-1, which is also vulnerable to offline cracking. This led to the exposure of millions of user passwords.
- **Adobe Breach (2013)**: Adobe stored passwords using a weak hashing algorithm (SHA-256) without proper salting, leading to the exposure of 150 million user passwords.

### Pitfalls and Common Mistakes

1. **Using Weak Hashing Algorithms**: MD5 and SHA-1 are not secure for storing passwords due to their susceptibility to collisions and brute-force attacks.
2. **Improper Use of Salts**: Salts are used to add randomness to password hashes, making them harder to crack. Without proper salting, hashes can be easily cracked using precomputed tables (rainbow tables).
3. **Storing Passwords in Cookies**: Storing password hashes in cookies, especially in a non-random manner, exposes them to offline cracking attacks.

### How to Prevent / Defend

#### Detection

- **Monitor for Suspicious Activity**: Implement logging and monitoring to detect unusual login patterns or repeated failed login attempts.
- **Use Intrusion Detection Systems (IDS)**: IDS can help identify and alert on potential cracking attempts.

#### Prevention

1. **Use Strong Hashing Algorithms**: Use modern, secure hashing algorithms like bcrypt, scrypt, or Argon2.
2. **Implement Proper Salting**: Ensure each password hash is salted with a unique, random value.
3. **Avoid Storing Passwords in Cookies**: Instead of storing password hashes in cookies, use session management techniques that rely on server-side storage.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import hashlib

def generate_stay_logged_in_cookie(username, password):
    # Generate MD5 hash of the password
    password_hash = hashlib.md5(password.encode()).hexdigest()
    # Combine username and password hash
    combined = f"{username}:{password_hash}"
    # Base64 encode the combined string
    encoded = base64.b64encode(combined.encode()).decode()
    return encoded
```

##### Secure Code

```python
import os
import hashlib
import base64

def generate_secure_stay_logged_in_cookie(username, password):
    # Generate a random salt
    salt = os.urandom(16)
    # Combine salt and password
    combined = salt + password.encode()
    # Generate bcrypt hash of the combined string
    password_hash = hashlib.pbkdf2_hmac('sha256', combined, salt, 100000)
    # Combine username and salted hash
    combined = f"{username}:{salt.hex()}:{password_hash.hex()}"
    # Base64 encode the combined string
    encoded = base64.b64encode(combined.encode()).decode()
    return encoded
```

### Configuration Hardening

#### Example Nginx Configuration

Ensure that sensitive cookies are marked as `HttpOnly` and `Secure`.

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    location / {
        add_header Set-Cookie "session=abc123; HttpOnly; Secure";
        add_header Set-Cookie "stayLoggedIn=peter:5d41402abc4b2a76b9719d911017c592; HttpOnly; Secure";
    }
}
```

### Conclusion

Proper handling of authentication mechanisms is crucial for maintaining web security. By avoiding the use of weak hashing algorithms, implementing proper salting, and avoiding the storage of password hashes in cookies, developers can significantly reduce the risk of offline password cracking attacks.

### Practice Labs

For hands-on practice with web security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on various web security topics, including authentication vulnerabilities.
- **OWASP Juice Shop**: An intentionally vulnerable web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive training application designed to teach web security lessons.

These labs provide practical experience in identifying and mitigating authentication vulnerabilities, reinforcing the theoretical knowledge gained from this chapter.

---
<!-- nav -->
[[04-Additional Depth on XSS Vulnerabilities|Additional Depth on XSS Vulnerabilities]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/11-Lab 10 Offline password cracking/00-Overview|Overview]] | [[06-Cross-Site Scripting (XSS) Vulnerability|Cross-Site Scripting (XSS) Vulnerability]]
