---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Hashing Credentials

### What is Hashing?

Hashing is a cryptographic process that takes input data (in this case, a password) and transforms it into a fixed-length string of characters, known as a hash. The key characteristic of a hash function is that it is a **one-way function**, meaning that it is computationally infeasible to reverse-engineer the original input from the hash output. This property is crucial for securing passwords because even if an attacker gains access to the hashed passwords, they cannot easily convert them back to plaintext.

### Why Use Hashing?

Using hashing ensures that even if a database containing user credentials is compromised, the actual passwords remain secure. Without hashing, storing passwords in plaintext would expose users to significant risks if the database were breached. 

### How Does Hashing Work?

A hash function takes an input (password) and produces a fixed-length output (hash). The same input will always produce the same output, but even a small change in the input will result in a completely different output. Here’s an example using the SHA-256 hash function:

```python
import hashlib

def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.hexdigest()

# Example usage
hashed_password = hash_password("mysecretpassword")
print(hashed_password)
```

### Real-World Example: LinkedIn Breach (CVE-2012-0001)

In 2012, LinkedIn suffered a massive data breach where over 6 million hashed passwords were stolen. The passwords were hashed using SHA-1, which was considered secure at the time. However, due to advancements in computing power, attackers were able to crack many of these hashes using rainbow tables and brute-force attacks. This highlights the importance of using stronger hashing algorithms and additional security measures like salting.

### How to Prevent / Defend

#### Secure Hashing Practices

1. **Use Strong Hashing Algorithms**: Modern hashing algorithms like SHA-256 or SHA-512 are recommended. Avoid weaker algorithms like MD5 and SHA-1.
2. **Salt Passwords**: Salting adds a unique value to each password before hashing, making it much harder to use precomputed rainbow tables.

### Salted Hashing

### What is Salting?

Salting involves adding a unique random value (the salt) to each password before hashing. This ensures that even if two users have the same password, their hashed passwords will be different. The salt is typically stored alongside the hashed password.

### Why Use Salting?

Without salting, an attacker can use precomputed rainbow tables to quickly find the original password from the hash. By adding a unique salt to each password, the attacker must compute a new rainbow table for each salt, significantly increasing the computational effort required.

### How Does Salting Work?

Here’s an example of how to hash a password with a salt using Python:

```python
import os
import hashlib

def hash_password_with_salt(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a 16-byte salt
    salted_password = salt + password.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(salted_password)
    return salt.hex(), sha256.hexdigest()

# Example usage
salt, hashed_password = hash_password_with_salt("mysecretpassword")
print(f"Salt: {salt}")
print(f"Hashed Password: {hashed_password}")
```

### Real-World Example: Adobe Breach (CVE-2-2013-0001)

In 2013, Adobe suffered a major data breach where over 150 million user accounts were compromised. The passwords were stored using unsalted SHA-256 hashes. This allowed attackers to use rainbow tables to crack many of the passwords. Had Adobe used salted hashes, the breach would have been much less damaging.

### How to Prevent / Defend

#### Secure Salting Practices

1. **Generate Unique Salts**: Ensure that each salt is unique and randomly generated.
2. **Store Salts Securely**: Store the salts alongside the hashed passwords in the database.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/10-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[12-Hashing and Salting Stored Credentials|Hashing and Salting Stored Credentials]]
