---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## How to Prevent / Defend Against Information Disclosure

### Secure Password Storage

To securely store passwords, you should use a strong hashing algorithm with salting. This makes it much harder for attackers to reverse-engineer the original passwords.

#### Example: Using bcrypt with Python

Here’s an example of how to securely store passwords using bcrypt:

```python
import bcrypt

# Input password
password = b"password1!"

# Generate a salt
salt = bcrypt.gensalt()

# Hash the password with the salt
hashed_password = bcrypt.hashpw(password, salt)

# Store the hashed password in the database
print(hashed_password)

# To verify a password
input_password = b"password1!"
if bcrypt.checkpw(input_password, hashed_password):
    print("Password matches")
else:
    print("Password does not match")
```

### Detection and Prevention

To detect and prevent information disclosure through weak password storage, you should:

1. **Regularly Audit Your Systems**: Ensure that all passwords are stored securely and that no plaintext passwords are stored.
2. **Use Strong Hashing Algorithms**: Use algorithms like bcrypt, scrypt, or Argon2, which are designed to be slow and resource-intensive, making brute-force attacks impractical.
3. **Implement Salting**: Always use a unique salt for each password. This makes it impossible for attackers to use precomputed hash tables.
4. **Educate Users**: Encourage users to choose strong, unique passwords and to change them regularly.

### Secure Coding Practices

Here’s an example of how to implement secure password storage in a web application:

#### Vulnerable Code

```python
import hashlib

def store_password(username, password):
    # Hash the password using SHA-256
    hash_object = hashlib.sha256()
    hash_object.update(password.encode('utf-8'))
    hashed_password = hash_object.hexdigest()
    
    # Store the username and hashed password in the database
    # (Assuming a simple dictionary for demonstration purposes)
    database[username] = hashed_password

database = {}
store_password("user1", "password1!")
```

#### Secure Code

```python
import bcrypt

def store_password(username, password):
    # Generate a salt
    salt = bcrypt.gensalt()
    
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Store the username and hashed password in the database
    # (Assuming a simple dictionary for demonstration purposes)
    database[username] = hashed_password

database = {}
store_password("user1", "password1!")
```

### Configuration Hardening

Ensure that your web server and application configurations are hardened to prevent information disclosure. For example, configure your web server to not leak sensitive information in error messages or headers.

#### Example: Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        try_files $uri $uri/ =404;
    }

    error_page 404 /404.html;
    location = /404.html {
        internal;
    }
}
```

### Real-World Lab Exercises

To practice and reinforce your understanding of secure password storage and preventing information disclosure, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including secure password storage.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By thoroughly understanding and implementing these practices, you can significantly reduce the risk of information disclosure through weak password storage.

---
<!-- nav -->
[[12-How to Prevent  Defend Against Information Disclosure Vulnerabilities|How to Prevent  Defend Against Information Disclosure Vulnerabilities]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[14-Identifying Information Disclosure Vulnerabilities|Identifying Information Disclosure Vulnerabilities]]
