---
tags: [cryptography, hashing, passwords, salt, beginner]
difficulty: beginner
module: "32 - Cryptography Vulnerabilities"
topic: "32.03 Unsalted Password Hashes"
---

# Unsalted Password Hashes

## 1. Introduction: The Need for Salting

When applications store user passwords, they must never store them in plaintext. The standard mechanism is to store a cryptographic hash of the password. However, a naive implementation of hashing—simply taking the user's password and applying a hash function like SHA-256—introduces a critical vulnerability: **deterministic output**.

Because cryptographic hash functions are deterministic, the exact same input will always produce the exact same output. If two users choose the password `P@ssword123`, their database records will contain the exact same hash.

An **Unsalted Password Hash** vulnerability occurs when developers fail to introduce a random, unique value (a "salt") into the hashing process. This oversight allows attackers to perform massive, highly efficient precomputation attacks and statistical analyses against stolen credential databases.

## 2. Anatomy of the Vulnerability

### 2.1 Identical Hashes for Identical Passwords
When a database uses unsalted hashes, an attacker who compromises the database immediately gains vast amounts of information without cracking a single hash. By observing the frequency of duplicate hashes, the attacker knows which users share passwords.

### 2.2 Global Precomputation
Because the hash of `admin123` is universally the same in an unsalted system, an attacker only has to crack it once. If the attacker precomputes the hashes for the top 10,000,000 most common passwords (using a standard list like `rockyou.txt`), they can instantly look up the plaintext for any matching hash in any unsalted database they compromise in the future. 
This is the core concept that enabled **Rainbow Tables**.

### 2.3 The "Crack One, Crack Many" Effect
If an attacker manages to crack a difficult hash in an unsalted database, and 50 other users have that exact same hash, the attacker has instantly compromised 51 accounts for the computational price of one. 

## 3. Architectural Diagram: Unsalted vs Salted Databases

```ascii
==================== UNSALTED DATABASE (VULNERABLE) ====================

User      Password (Input)     Hash Algorithm        Stored Hash (DB Column)
----      ----------------     --------------        -----------------------
Alice  -> [ password123 ]  -->    SHA-256     -->  [ ef92b77... (Hash A) ]
Bob    -> [ iloveyou    ]  -->    SHA-256     -->  [ 3f8a0c2... (Hash B) ]
Charlie-> [ password123 ]  -->    SHA-256     -->  [ ef92b77... (Hash A) ] <-- IDENTICAL!

*Attacker Attack Vector:* Attacker hashes "password123" once, looks for "ef92b77..." 
and instantly compromises both Alice and Charlie.

====================== SALTED DATABASE (SECURE) ========================

User      Password        Unique Salt (DB)     Hash Function             Stored Hash
----      ---------       ----------------     -------------             -----------
Alice  -> [ password123 ] + [ xk9L2p... ] --> SHA-256(Pass+Salt) --> [ 8b4d9a1... (Hash X) ]
Bob    -> [ iloveyou    ] + [ z1Qw8m... ] --> SHA-256(Pass+Salt) --> [ 1a9f3b2... (Hash Y) ]
Charlie-> [ password123 ] + [ m4N7rV... ] --> SHA-256(Pass+Salt) --> [ 5c2e8d9... (Hash Z) ] <-- UNIQUE!

*Attacker Attack Vector:* Even though Alice and Charlie have the same password, 
their stored hashes are completely different. The attacker cannot use precomputed 
tables and must crack Alice and Charlie separately.
```

## 4. Identifying and Exploiting Unsalted Hashes

### 4.1 Identifying the Vulnerability
During a penetration test, if you obtain a database dump (via SQLi, backup file exposure, etc.), identifying unsalted hashes is straightforward:
1.  **Check the Schema:** Look at the user table structure. Is there a column named `salt`? If not, it might be unsalted (though modern algorithms like Bcrypt include the salt inside the hash string itself).
2.  **Frequency Analysis:** Run a simple SQL `GROUP BY` or use a shell command to count duplicate hashes.
    ```bash
    cat hashes.txt | sort | uniq -c | sort -nr | head -n 10
    ```
    If you see multiple users with the exact same hash, the database is unequivocally unsalted (or a single global salt/pepper is being used, which provides identical hashes for identical passwords).

### 4.2 Exploitation via Hashcat
When attacking unsalted hashes, you do not need to specify any salt rules. The raw hashes are fed directly into the cracking tool.

```bash
# Example: Cracking unsalted SHA-256 (Mode 1400) using a dictionary
hashcat -m 1400 hashes_unsalted.txt rockyou.txt
```

If the attacker has a precomputed database (like a massive dictionary of plaintext to SHA-256 mappings), exploitation is reduced to a simple database `JOIN` query, turning months of compute time into milliseconds.

## 5. The Cryptographic Fix: Implementing Salts Properly

A salt is random data that is used as an additional input to a one-way function that hashes data, a password or passphrase.

### 5.1 Rules for Secure Salting
To be effective, a salt must adhere to strict rules:
1.  **Uniqueness:** Every single user MUST have a unique salt. If you use the same salt for every user (a global salt), it defeats the purpose, as identical passwords will still yield identical hashes.
2.  **Randomness:** The salt must be generated using a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG), such as `/dev/urandom` on Linux or `random.SystemRandom` in Python.
3.  **Length:** The salt should be at least 16 bytes (128 bits) long to ensure there are enough possible salts to prevent collisions.
4.  **Storage:** The salt does *not* need to be kept secret. It is entirely safe to store the salt in plaintext in the database right next to the hash (or prepended to the hash string, as Bcrypt does). The salt's job is not to be a secret key; its job is to ensure uniqueness.

### 5.2 Code Example: Vulnerable vs. Secure Implementation

**Vulnerable Python Implementation (No Salt):**
```python
import hashlib

def hash_password_vulnerable(password):
    # CRITICAL VULNERABILITY: No salt used. Deterministic output.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Storing in DB:
# User: Alice, Hash: hash_password_vulnerable("secret")
```

**Secure Python Implementation (Using proper KDF and Salt):**
*Note: In modern development, you should use a library like `bcrypt` or `argon2-cffi`. However, if using standard libraries, `hashlib.pbkdf2_hmac` with a salt is required.*

```python
import os
import hashlib

def hash_password_secure(password):
    # 1. Generate a unique, random 16-byte salt using a CSPRNG
    salt = os.urandom(16)
    
    # 2. Use a Key Derivation Function (PBKDF2) with the salt and a high iteration count
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt, 
        100000 # Cost factor
    )
    
    # Return both the salt and the hash so they can be stored in the DB
    return salt, hashed_password

# To verify later:
# check_hash = hashlib.pbkdf2_hmac('sha256', input_password, retrieved_salt, 100000)
# if check_hash == retrieved_hash: ...
```

*Note: Modern algorithms like Bcrypt handle the salt generation and storage internally, formatting the output into a single string containing the algorithm identifier, cost factor, salt, and hash. E.g., `$2a$12$Nq9...`*

## 6. Beyond Salting: Peppering
While salting protects against precomputation and identical hash attacks, it does not prevent offline brute-forcing if the database is stolen (since the attacker steals the salts along with the hashes).

A **Pepper** is a secret cryptographic key added to the password along with the salt before hashing. Unlike a salt, the pepper is *not* stored in the database. It is stored securely in the application's configuration files, environment variables, or a Hardware Security Module (HSM). If an attacker steals only the database via SQL injection but fails to compromise the web server filesystem (where the pepper lives), they cannot crack the passwords because they do not have the pepper.

## 7. Summary
The absence of a salt in password hashing is a catastrophic design flaw that reduces the security of the entire database to the strength of its weakest passwords. Unsalted hashes allow attackers to detect identical passwords instantly and utilize precomputed tables to crack thousands of accounts simultaneously. Implementing unique, random salts via modern Key Derivation Functions (Bcrypt, Argon2) is a mandatory requirement for any application handling authentication.

---

## Chaining Opportunities
*   **SQL Injection (SQLi):** Database compromise via SQLi is the standard prerequisite for exploiting unsalted hashes.
*   **Horizontal Privilege Escalation:** Identifying that a low-privileged user and an Administrator share the exact same unsalted hash allows the attacker to instantly impersonate the Administrator.
*   **Open Source Intelligence (OSINT) & Password Reuse:** Once an unsalted password is cracked, attackers will likely use the plaintext credential across other platforms associated with the user's email.

## Related Notes
*   [[02 - Rainbow Table Attacks]] - The primary tool used historically to exploit unsalted hashes.
*   [[01 - Weak Hashing Algorithms (MD5, SHA1 for passwords)]] - The combination of weak algorithms and no salt is the worst-case scenario.
*   [[04 - Key Derivation Functions (KDFs)]] - The proper modern solution that inherently handles salting and computation cost.
