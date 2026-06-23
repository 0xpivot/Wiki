---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Authentication Bypass via Weak Signing Key

In the context of JWT authentication, one of the most critical vulnerabilities is the use of a weak signing key. This vulnerability can allow attackers to forge JWTs and gain unauthorized access to protected resources.

### Understanding Weak Signing Keys

A weak signing key is one that is either too short, predictable, or otherwise easily guessable. This makes it susceptible to brute-force attacks, where an attacker systematically tries all possible combinations until they find the correct key.

#### Example of a Weak Signing Key

Consider a scenario where the secret key used to sign JWTs is simply `"secret"`. This is a very weak key and can be easily guessed or brute-forced.

```python
import jwt

# Weak secret key
secret = "secret"

# Create a JWT with the weak secret key
payload = {
    "sub": "john.doe@example.com",
    "admin": True
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```

### Brute-Force Attack on Weak Signing Key

An attacker can use a brute-force approach to guess the secret key. This involves trying all possible combinations of keys until the correct one is found. Tools like `jwt-cracker` can automate this process.

#### Example of Brute-Force Attack

```bash
# Using jwt-cracker to brute-force the secret key
jwt-cracker --algorithm HS256 --wordlist /path/to/wordlist.txt <JWT>
```

### Real-World Examples of Weak Signing Key Vulnerabilities

One notable real-world example is the CVE-2019-16759, where a web application used a weak secret key to sign JWTs. This allowed attackers to forge JWTs and gain unauthorized access to administrative functions.

### How to Prevent / Defend Against Weak Signing Key Vulnerabilities

#### Secure Secret Key Management

1. **Use Strong, Random Secrets**: Ensure that the secret key used to sign JWTs is strong, random, and sufficiently long. A good practice is to use a cryptographically secure pseudo-random number generator (CSPRNG) to generate the key.

2. **Environment Variables**: Store the secret key in environment variables rather than hardcoding it in the source code. This helps prevent accidental exposure of the key.

3. **Key Rotation**: Regularly rotate the secret key to minimize the window of opportunity for an attacker to exploit a compromised key.

#### Secure Configuration

1. **Disable None Algorithm**: Ensure that the application does not accept JWTs signed with the `none` algorithm. This prevents attackers from forging JWTs without a valid signature.

2. **Validate Token Signatures**: Always validate the signature of incoming JWTs to ensure they have not been tampered with.

#### Secure Code Implementation

Here is an example of secure code implementation for generating and validating JWTs:

```python
import jwt
from datetime import datetime, timedelta

# Strong secret key stored in environment variable
import os
secret = os.getenv("JWT_SECRET")

def generate_jwt(user_id):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def validate_jwt(token):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Generate a JWT
user_id = "john.doe@example.com"
token = generate_jwt(user_id)
print(token)

# Validate the JWT
payload = validate_jwt(token)
if payload:
    print(f"Valid token for user: {payload['sub']}")
else:
    print("Invalid token")
```

### Detection of Weak Signing Key Vulnerabilities

Detection of weak signing key vulnerabilities can be achieved through automated tools and manual code reviews.

#### Automated Tools

Tools like `jwt-cracker` can be used to test the strength of the secret key by attempting to brute-force it.

#### Manual Code Review

Review the codebase to ensure that the secret key is managed securely and that JWT signatures are validated correctly.

### Hands-On Labs for Practice

For hands-on practice with JWT authentication bypass via weak signing key, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive lab on JWT authentication bypass.
- **OWASP Juice Shop**: Provides a real-world web application with various security vulnerabilities, including JWT-related issues.
- **DVWA (Damn Vulnerable Web Application)**: Contains a variety of web application vulnerabilities, including JWT authentication bypass.

By thoroughly understanding and implementing the preventive measures outlined above, developers can significantly reduce the risk of JWT authentication bypass via weak signing key vulnerabilities.

### Conclusion

JWTs are a powerful tool for securing web applications, but they come with their own set of vulnerabilities. By understanding the components of JWTs and the risks associated with weak signing keys, developers can implement robust security measures to protect against unauthorized access. Regularly reviewing and updating security practices ensures that applications remain secure against evolving threats.

---
<!-- nav -->
[[06-JWT Attacks Authentication Bypass via Weak Signing Key|JWT Attacks Authentication Bypass via Weak Signing Key]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[08-Real-World Examples|Real-World Examples]]
