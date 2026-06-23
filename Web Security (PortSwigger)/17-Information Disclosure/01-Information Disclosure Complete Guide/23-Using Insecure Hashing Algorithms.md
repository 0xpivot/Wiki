---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Using Insecure Hashing Algorithms

### What Are Insecure Hashing Algorithms?

Insecure hashing algorithms are cryptographic functions that are known to have vulnerabilities and weaknesses, making them unsuitable for securing sensitive data. One of the most commonly used insecure hashing algorithms is MD5.

### Why Does This Matter?

Using insecure hashing algorithms can lead to serious security risks, including hash collisions, which can be exploited by attackers to forge data or bypass security controls. For example, if passwords are hashed using MD5, an attacker can use precomputed rainbow tables to reverse-engineer the hashes and obtain the original passwords.

### How Does This Work Under the Hood?

MD5 is a cryptographic hash function that takes an input (or 'message') and returns a fixed-size string of bytes, which is typically represented as a hexadecimal number. However, MD5 is known to have vulnerabilities, including hash collisions, which can be exploited by attackers.

Here is an example of using MD5 to hash a password:

```python
import hashlib

password = "my_password"
hashed_password = hashlib.md5(password.encode()).hexdigest()
print(hashed_password)
```

In this example, the password is hashed using MD5, and the resulting hash is printed. However, since MD5 is insecure, an attacker can use precomputed rainbow tables to reverse-engineer the hash and obtain the original password.

### Real-World Examples

One of the most notable examples of using insecure hashing algorithms is the LinkedIn breach (CVE-2012-0001). In this breach, attackers obtained a list of hashed passwords from LinkedIn and used precomputed rainbow tables to reverse-engineer the hashes and obtain the original passwords.

### How to Prevent / Defend

#### Detection

To detect the use of insecure hashing algorithms, you can use static code analysis tools like SonarQube or Fortify. These tools scan the source code for patterns that indicate the use of insecure hashing algorithms and flag them for review.

#### Prevention

To prevent the use of insecure hashing algorithms, you should use cryptographically secure algorithms to hash sensitive data. One of the most commonly used secure hashing algorithms is bcrypt.

Here is an example of using bcrypt to hash a password:

```python
import bcrypt

password = "my_password".encode()
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password, salt)
print(hashed_password)
```

In this example, the password is hashed using bcrypt, and the resulting hash is printed. Since bcrypt is a secure hashing algorithm, it is resistant to attacks such as hash collisions.

### Secure Coding Fixes

#### Vulnerable Code

```python
import hashlib

password = "my_password"
hashed_password = hashlib.md5(password.encode()).hexdigest()
print(hashed_password)
```

#### Fixed Code

```python
import bcrypt

password = "my_password".encode()
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password, salt)
print(hashed_password)
```

In the fixed code, the password is hashed using bcrypt, which is a secure hashing algorithm. This ensures that the password is securely hashed and resistant to attacks such as hash collisions.

### Hands-On Labs

For hands-on practice with this topic, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises on detecting and preventing the use of insecure hashing algorithms.
- **OWASP Juice Shop**: This lab includes scenarios where insecure hashing algorithms are used, and you can practice identifying and fixing these issues.

---
<!-- nav -->
[[22-Understanding Sensitive Data and Information Disclosure|Understanding Sensitive Data and Information Disclosure]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[24-Verbose Error Messages and Business Design Leading to Information Disclosure|Verbose Error Messages and Business Design Leading to Information Disclosure]]
