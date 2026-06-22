---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Hashing and Salting Stored Credentials

### What Are Hashing and Salting?

Hashing converts plaintext passwords into a fixed-length string of characters using a cryptographic hash function. Salting adds a random value to the password before hashing, ensuring that identical passwords produce different hashes.

### Why Use Hashing and Salting?

Storing plain-text passwords is highly insecure. Hashing and salting make it difficult for attackers to reverse-engineer passwords even if they gain access to the stored hashes.

### How to Hash and Salt Credentials

Use a strong, cryptographically secure hashing algorithm like bcrypt, scrypt, or Argon2. Always include a unique salt for each password.

#### Real-World Example: LinkedIn Breach (2012)

In the 2012 LinkedIn breach, attackers obtained millions of hashed passwords. Because LinkedIn used unsalted SHA-1 hashes, attackers could use rainbow tables to crack many of the passwords. Proper hashing and salting would have made this much harder.

### How to Prevent / Defend

**Detection:**
- Audit stored passwords to ensure they are properly hashed and salted.
- Use penetration testing to identify weak hashing practices.

**Prevention:**
- Use strong, modern hashing algorithms.
- Always include a unique salt for each password.

**Secure Coding Fix:**
```python
# Example of hashing and salting passwords in Python
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Usage
hashed_password = hash_password("mysecretpassword")
print(check_password(hashed_password, "mysecretpassword"))  # True
print(check_password(hashed_password, "wrongpassword"))     # False
```

### Conclusion

Implementing robust authentication mechanisms, such as MFA, changing default credentials, using encrypted channels, transmitting credentials via POST requests, and properly hashing and salting stored credentials, are crucial steps in securing web applications. Each of these measures plays a vital role in preventing unauthorized access and protecting sensitive data.

### Practice Labs

For hands-on experience with authentication vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on authentication vulnerabilities, including MFA, default credentials, and secure credential storage.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including authentication vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices, including authentication vulnerabilities.

By thoroughly understanding and implementing these security measures, you can significantly enhance the security of your web applications.

---
<!-- nav -->
[[11-Hashing Credentials|Hashing Credentials]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[13-Insecure Forgot Password Functionality|Insecure Forgot Password Functionality]]
