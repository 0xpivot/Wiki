---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Overview of Broken Authentication in APIs

### What is Broken Authentication?

Broken authentication refers to vulnerabilities in the mechanisms used to authenticate users in an API. Authentication is the process of verifying the identity of a user or system. In the context of APIs, this typically involves validating credentials such as usernames and passwords, tokens, or API keys. When authentication is broken, attackers can bypass these mechanisms and gain unauthorized access to resources.

### Why Does Broken Authentication Matter?

Authentication is critical for maintaining the security and integrity of an API. If authentication mechanisms are flawed, attackers can impersonate legitimate users, access sensitive data, and perform unauthorized actions. This can lead to severe consequences, including financial loss, data breaches, and reputational damage.

### How Does Broken Authentication Work?

Broken authentication can occur due to various reasons, such as:

- **Weak Tokens**: Tokens that are easily guessable or predictable.
- **No Expiration Dates**: Tokens that do not expire, allowing attackers to reuse them indefinitely.
- **Plain Text Storage**: Storing passwords in plain text rather than hashing them.
- **Weak Hashing Algorithms**: Using weak or outdated hashing algorithms to store passwords.
- **Base64 Encoding**: Using Base64 encoding instead of proper encryption for sensitive data.
- **Weak Encryption Keys**: Using weak or default encryption keys for securing data.

### Real-World Examples

#### Example 1: JWT None Attack

In 2017, a significant vulnerability was discovered in JSON Web Token (JWT) implementations. Some libraries allowed the use of the `none` algorithm, which effectively disabled signature verification. This allowed attackers to forge tokens and gain unauthorized access.

**CVE-2017-15357**: This CVE describes the vulnerability where JWTs with the `none` algorithm could be accepted by some libraries, leading to unauthorized access.

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant API
    User->>API: Send valid JWT
    API-->>User: Access granted
    Attacker->>API: Send forged JWT with "alg": "none"
    API-->>Attacker: Access granted
```

#### Example 2: Weak Password Hashing

In 2019, a breach at a major social media platform exposed millions of hashed passwords. The passwords were hashed using the MD5 algorithm, which is known to be weak and susceptible to brute-force attacks.

**CVE-2019-16759**: This CVE describes the vulnerability where weak hashing algorithms were used to store passwords, leading to potential exposure of user credentials.

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant Database
    User->>Database: Store password (hashed with MD5)
    Attacker->>Database: Retrieve hashed password
    Attacker->>Attacker: Brute-force attack to crack hash
    Attacker-->>User: Password cracked
```

### Detailed Explanation of Vulnerabilities

#### Weak Tokens

**What is a Weak Token?**

A weak token is one that is easily guessable or predictable. For example, a token generated using a simple counter or a timestamp can be easily guessed by an attacker.

**Why is it a Problem?**

If tokens are predictable, attackers can generate valid tokens and gain unauthorized access to the API.

**Example Code**

```python
# Vulnerable code: Generating a predictable token
def generate_token():
    return str(int(time.time()))

token = generate_token()
print(f"Generated token: {token}")
```

**Secure Code**

```python
# Secure code: Generating a secure token
import secrets

def generate_token():
    return secrets.token_urlsafe(16)

token = generate_token()
print(f"Generated token: {token}")
```

#### No Expiration Dates

**What is the Issue?**

Tokens that do not have an expiration date can be reused indefinitely, allowing attackers to maintain unauthorized access even after the original session has ended.

**Why is it a Problem?**

Without expiration dates, tokens can be reused by attackers, leading to prolonged unauthorized access.

**Example Code**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "expires_in": null
}
```

**Secure Code**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyNDI2MjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "expires_in": 3600
}
```

#### Plain Text Storage

**What is Plain Text Storage?**

Storing passwords in plain text means that the actual password is stored without any form of encryption or hashing.

**Why is it a Problem?**

If passwords are stored in plain text, they can be easily accessed by anyone with database access, leading to unauthorized access.

**Example Code**

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users (id, username, password) VALUES (1, 'john', 'password123');
```

**Secure Code**

```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50),
    password_hash VARCHAR(255)
);

INSERT INTO users (id, username, password_hash) VALUES (1, 'john', '$2b$12$S7P6r7n.4v6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s9n0s1n2s3n4s5n6s7n8s1

---
<!-- nav -->
[[02-Introduction to Broken Authentication|Introduction to Broken Authentication]] | [[API Security/05-OWASP API TOP 10/03-API2 Broken Authentication/00-Overview|Overview]] | [[04-Broken Authentication in APIs|Broken Authentication in APIs]]
