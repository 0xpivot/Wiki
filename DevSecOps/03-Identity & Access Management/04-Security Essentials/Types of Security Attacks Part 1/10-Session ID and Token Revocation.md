---
course: DevSecOps
topic: Security Essentials
tags: [devsecops]
---

## Session ID and Token Revocation

### What is Session ID and Token Revocation?

Session ID and token revocation is a critical aspect of maintaining security in web applications. A session ID is a unique identifier assigned to a user during a session, allowing the server to track the user's activity. Tokens, such as JWT (JSON Web Tokens), are used to authenticate and authorize users. Proper revocation ensures that once a user logs out or reports a stolen session, the session ID or token is invalidated, preventing unauthorized access.

### Why is Session ID and Token Revocation Important?

Without proper revocation, an attacker who gains access to a session ID or token can continue to impersonate the user indefinitely. This can lead to unauthorized access to sensitive data, financial losses, and reputational damage. For instance, in the case of the Capital One breach in 2019 (CVE-2019-11231), an attacker exploited a misconfigured web application firewall to gain access to sensitive customer data. The lack of proper session management allowed the attacker to maintain access for an extended period.

### How Does Session ID and Token Revocation Work?

When a user logs out or reports a stolen session, the application should immediately invalidate the session ID or token. This typically involves marking the session ID or token as invalid in the database or token store. For JWTs, this often involves maintaining a list of revoked tokens.

#### Example: Session ID Revocation

Consider a simple web application using PHP sessions:

```php
session_start();
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // User logs out
    session_destroy();
}
```

In this example, `session_destroy()` invalidates the session ID, ensuring that the user cannot be authenticated using the old session.

#### Example: JWT Revocation

For JWTs, you might maintain a list of revoked tokens:

```python
import jwt

revoked_tokens = set()

def revoke_token(token):
    revoked_tokens.add(token)

def check_token(token):
    if token in revoked_tokens:
        return False
    try:
        decoded = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
```

Here, `revoke_token` adds a token to the set of revoked tokens, and `check_token` verifies whether a token is valid and not revoked.

### Common Pitfalls and Detection

One common pitfall is failing to properly invalidate session IDs or tokens. This can occur due to improper implementation or configuration. To detect such issues, you can use tools like Burp Suite or ZAP to monitor session IDs and tokens. Additionally, logging and monitoring can help identify unauthorized access attempts.

### How to Prevent / Defend

#### Secure Coding Practices

Ensure that session IDs and tokens are properly invalidated upon logout or report of theft. Use secure coding practices to avoid common vulnerabilities such as SQL injection or XSS.

#### Configuration Hardening

Configure your application to automatically invalidate session IDs and tokens after a certain period of inactivity. Use strong encryption and hashing algorithms to protect session IDs and tokens.

#### Real-World Example: Capital One Breach

In the Capital One breach, the attacker gained access to sensitive customer data by exploiting a misconfigured web application firewall. The lack of proper session management allowed the attacker to maintain access for an extended period. To prevent such breaches, ensure that session IDs and tokens are properly managed and invalidated.

---
<!-- nav -->
[[10-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/04-Security Essentials/Types of Security Attacks Part 1/00-Overview|Overview]] | [[12-Social Engineering Attacks Part 1|Social Engineering Attacks Part 1]]
