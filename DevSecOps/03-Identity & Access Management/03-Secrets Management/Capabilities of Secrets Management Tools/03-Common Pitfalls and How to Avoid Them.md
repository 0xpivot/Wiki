---
course: DevSecOps
topic: Secrets Management
tags: [devsecops]
---

## Common Pitfalls and How to Avoid Them

### Storing Secrets in Plaintext

#### What Is the Risk?

Storing secrets in plaintext exposes them to unauthorized access. If an attacker gains access to the storage location, they can easily read and misuse the secrets.

#### How to Prevent

Ensure that all secrets are encrypted both at rest and in transit. Use strong encryption algorithms and keep the encryption keys secure.

#### Secure Code Fix

Vulnerable Code:
```python
# Vulnerable Code
config = {
    "database_password": "my-secret-password"
}
```

Secure Code:
```python
# Secure Code
import os
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

config = {
    "encrypted_database_password": cipher_suite.encrypt(b"my-secret-password").decode()
}

# Store key securely
os.environ["ENCRYPTION_KEY"] = key.decode()
```

### Inadequate Access Controls

#### What Is the Risk?

Inadequate access controls allow unauthorized users to access secrets. This can lead to data breaches and misuse of sensitive information.

#### How to Prevent

Implement role-based access control (RBAC) and ensure that users are granted the minimum permissions necessary to perform their tasks.

#### Secure Code Fix

Vulnerable Code:
```python
# Vulnerable Code
def get_secret(user):
    return "my-secret-password"
```

Secure Code:
```python
# Secure Code
def get_secret(user):
    if user.role == "admin":
        return "my-secret-password"
    else:
        raise PermissionError("Insufficient privileges")
```

### Lack of Auditing and Monitoring

#### What Is the Risk?

Lack of auditing and monitoring makes it difficult to detect and respond to security incidents. Without proper logging, it is challenging to trace the source of a breach.

#### How to Prevent

Enable auditing and monitoring features in the secrets management tool. Regularly review audit logs to identify and respond to suspicious activities.

#### Secure Code Fix

Vulnerable Code:
```python
# Vulnerable Code
def log_action(action):
    pass
```

Secure Code:
```python
# Secure Code
import logging

logging.basicConfig(filename='audit.log', level=logging.INFO)

def log_action(action):
    logging.info(f"Action: {action}")
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Capabilities of Secrets Management Tools/02-Introduction to Secrets Management|Introduction to Secrets Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/03-Secrets Management/Capabilities of Secrets Management Tools/00-Overview|Overview]] | [[04-Implementation and Best Practices|Implementation and Best Practices]]
