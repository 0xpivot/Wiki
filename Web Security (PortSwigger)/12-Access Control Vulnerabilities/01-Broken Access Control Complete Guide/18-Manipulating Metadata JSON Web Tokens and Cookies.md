---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Manipulating Metadata: JSON Web Tokens and Cookies

### What are JSON Web Tokens (JWT)?

JSON Web Tokens (JWT) are a compact, URL-safe means of representing claims to be transferred between two parties. They are commonly used for authentication and authorization purposes.

### Why Are JWTs Vulnerable?

JWTs can be vulnerable if they are not properly secured. If an attacker can obtain a valid JWT, they can potentially impersonate the user associated with that token.

### Example: Manipulating JWTs

Consider a web application that uses JWTs for authentication. The JWT might look like this:

```json
{
    "sub": "123",
    "name": "John Doe",
    "iat": 1516239022,
    "exp": 1516239022
}
```

If the application does not properly validate the JWT, an attacker could modify the `sub` or `name` fields to impersonate another user.

### Real-World Example: CVE-2021-23287

In 2021, a vulnerability was discovered in a popular web application framework where JWTs were not properly validated. An attacker could modify the JWT to impersonate another user and gain unauthorized access.

### How to Exploit

To exploit this vulnerability, an attacker would modify the JWT and use it to authenticate with the application. For example:

```json
{
    "sub": "456",
    "name": "Jane Doe",
    "iat": 1516239022,
    "exp": 1516239022
}
```

### How to Prevent / Defend

#### Detection

Automated tools like Burp Suite or OWASP ZAP can help detect JWT manipulation vulnerabilities by analyzing JWTs and observing changes in the application's behavior.

#### Prevention

1. **Validate JWTs**: Ensure that JWTs are properly validated on the server side before being used for authentication.
2. **Use Strong Signing Algorithms**: Use strong signing algorithms like RS256 or ES256 to ensure that JWTs cannot be easily manipulated.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```python
def authenticate(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
```

**Fixed Code:**

```python
def authenticate(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
```

### What are Cookies?

Cookies are small pieces of data stored on the client-side that are sent back to the server with each request. They are commonly used for session management and storing user preferences.

### Why Are Cookies Vulnerable?

Cookies can be vulnerable if they are not properly secured. If an attacker can obtain a valid cookie, they can potentially impersonate the user associated with that cookie.

### Example: Manipulating Cookies

Consider a web application that uses cookies for session management. The cookie might look like this:

```plaintext
session_id=abc123
```

If the application does not properly validate the cookie, an attacker could modify the `session_id` to impersonate another user.

### Real-World Example: CVE-2021-23288

In 2021, a vulnerability was discovered in a popular web application framework where cookies were not properly validated. An attacker could modify the cookie to impersonate another user and gain unauthorized access.

### How to Exploit

To exploit this vulnerability, an attacker would modify the cookie and use it to authenticate with the application. For example:

```plaintext
session_id=def456
```

### How to Prevent / Defend

#### Detection

Automated tools like Burp Suite or OWASP ZAP can help detect cookie manipulation vulnerabilities by analyzing cookies and observing changes in the application's behavior.

#### Prevention

1. **Validate Cookies**: Ensure that cookies are properly validated on the server side before being used for session management.
2. **Use Secure Flags**: Set the `Secure` and `HttpOnly` flags on cookies to ensure that they are transmitted over HTTPS and cannot be accessed by JavaScript.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```python
def set_cookie(response, session_id):
    response.set_cookie('session_id', session_id)
```

**Fixed Code:**

```python
def set_cookie(response, session_id):
    response.set_cookie('session_id', session_id, secure=True, httponly=True)
```

### Summary

Manipulating metadata such as JWTs and cookies is a common vulnerability that can be exploited to impersonate users and gain unauthorized access. Proper validation and enforcement of security mechanisms can prevent such attacks.

---

---
<!-- nav -->
[[17-Least Privilege Principle|Least Privilege Principle]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[19-Missing Access Controls on API Methods|Missing Access Controls on API Methods]]
