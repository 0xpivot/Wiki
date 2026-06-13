---
tags: [tools, vapt, utility, cryptography, cracking]
difficulty: intermediate
module: "41 - Tools"
topic: "41.20 Hashcat"
---

# Hashcat: The World's Fastest Password Cracker

## 1. Overview and Introduction

Hashcat is the undisputed king of password cracking. It is an open-source, advanced password recovery utility that leverages the immense parallel processing power of modern GPUs (Graphics Processing Units) via OpenCL and CUDA. 

In the realm of VAPT and API Security (Module 31), extracting hashes is only half the battle. Whether an attacker dumps an `NTDS.dit` file from an Active Directory controller, captures NetNTLMv2 hashes over the network, or exploits an API SQL injection to dump a database of bcrypt/SHA256 user hashes, they must convert those cryptographic hashes back into plaintext to be useful. Hashcat is the tool that makes this computationally feasible.

## 2. Cryptographic Hashes vs. Encryption

It is critical to distinguish hashing from encryption. Encryption is a two-way mathematical function requiring a key to encrypt and decrypt. Hashing is a **one-way** mathematical function. You cannot "decrypt" a hash. 

Therefore, Hashcat does not decrypt; it **guesses**. It rapidly generates millions or billions of plaintext guesses, hashes them using the same algorithm, and compares the resulting hash to the target hash. If they match, the password is "cracked."

## 3. Architecture and GPU Acceleration

CPUs are designed for complex, sequential task switching (having a few very fast, versatile cores). GPUs are designed for graphics rendering, which requires performing the exact same mathematical operation on millions of pixels simultaneously (having thousands of slower, specialized cores). 

Hash computations (like MD5, SHA1, NTLM) are simple, repetitive mathematical operations perfectly suited for GPU architecture.

### 3.1 Custom ASCII Architecture Diagram

```text
+-------------------------------------------------------+
|                Hashcat Cracking Pipeline              |
+-------------------------------------------------------+
|                                                       |
|  +----------------+      Hash Input + Rules           |
|  | Input Hashes   | ----------------------------+     |
|  | (NTLM, SHA256) |                             |     |
|  +-------+--------+                             v     |
|                                        +--------+--------+
|        +------------------+            | Hashcat Engine  |
|        | Dictionary / Mask| ---------> |   (OpenCL /     |
|        +------------------+            |     CUDA)       |
|                                        +--------+--------+
|                                                 |     |
|    Billions of Hashes / Sec (GPU Cores)         |     |
|                                                 v     |
|                                        +-----------------+
|                                        | Cracked Output  |
|                                        |  (Plaintext)    |
|                                        +-----------------+
|                                                       |
+-------------------------------------------------------+
```

## 4. Attack Modes and Strategies

Hashcat supports over 300 highly optimized hash algorithms (specified via the `-m` flag) and various attack modes (specified via the `-a` flag).

### 4.1 Dictionary Attack (Mode 0)
The simplest attack. Hashcat reads words from a wordlist (like `rockyou.txt`), hashes them, and compares them.
```bash
hashcat -m 1000 -a 0 target_hashes.txt rockyou.txt
```
*(Mode 1000 = NTLM)*

### 4.2 Combinator Attack (Mode 1)
Combines words from two dictionaries. If dict1 contains "admin" and dict2 contains "123", it tests "admin123".

### 4.3 Brute-Force and Mask Attack (Mode 3)
A mask attack is a highly optimized brute-force attack where the attacker specifies a pattern. This is vastly superior to pure brute-force because it eliminates mathematically impossible or highly improbable combinations.
- `?l` = lowercase
- `?u` = uppercase
- `?d` = digit
- `?s` = symbol
- `?a` = all characters

**Example (Cracking an 8-character password starting with an uppercase letter, followed by 5 lowercase letters, and ending in 2 digits):**
```bash
hashcat -m 1000 -a 3 target_hashes.txt ?u?l?l?l?l?l?d?d
```

### 4.4 Rule-Based Attack (Mode 0 with Rules)
The most powerful technique used by professionals. It takes a base dictionary and applies rules to mutate the words (e.g., capitalize the first letter, append "2023", toggle case, leetspeak conversion). Hashcat comes with powerful rule sets like `best64.rule` and `OneRuleToRuleThemAll.rule`.
```bash
hashcat -m 1000 -a 0 target_hashes.txt rockyou.txt -r rules/best64.rule
```

## 5. Distributed Cracking (Brain Mode)

For massive hash lists or highly complex passwords, a single GPU rig is insufficient. Hashcat incorporates "Brain" mode, a distributed cracking client/server architecture. 
The Hashcat Brain server coordinates the attack space among multiple connected client rigs over the network, ensuring no two nodes calculate the same password candidate, maximizing efficiency.

## 6. Identifying Hashes

Before cracking, one must know the hash type. Tools like `hashid` or `name-that-hash` can analyze the hash structure.
- `$1$`: MD5 crypt
- `$2a$` / `$2b$`: bcrypt (Heavily used in modern web APIs)
- `$5$`: SHA256 crypt
- `$6$`: SHA512 crypt
- `1000`: NTLM (No prefix, exactly 32 hex characters)

## 7. Defenses Against Password Cracking

The only defense against offline cracking is computational expense and length.
1.  **Use Key Derivation Functions (KDFs):** APIs must never store passwords using fast algorithms like MD5, SHA1, or even plain SHA256. They must use KDFs like `bcrypt`, `scrypt`, or `Argon2`. These algorithms incorporate a Work Factor (iterations) designed specifically to be slow on CPUs and resistant to GPU parallelization.
2.  **Salting:** Append a unique, random string (salt) to every password before hashing. This defeats pre-computed Rainbow Tables and forces the attacker to crack each user's hash individually, destroying the economy of scale.
3.  **Password Length:** Enforce passphrases (>15 characters) rather than passwords. Even with the fastest GPUs, masking a 15-character password is mathematically unfeasible within a human lifetime.

## 8. Conclusion

Hashcat represents the culmination of cryptographic reverse-engineering. It transforms what was once considered mathematically secure into a mere matter of time and electricity. Understanding Hashcat's capabilities is essential for API developers to realize why strong hashing algorithms like Argon2 are strictly necessary.

---

## Chaining Opportunities
- **[[17 - Responder]]:** Responder captures NetNTLMv2 hashes from the network. These are fed directly into Hashcat (Mode 5600) to recover the plaintext passwords.
- **[[18 - Mimikatz]]:** Mimikatz can dump NTLM hashes (Mode 1000) or Kerberos TGS tickets (`.kirbi` files). Hashcat can crack these Kerberos tickets (Mode 13100) offline to recover service account passwords (Kerberoasting).
- **[[19 - jwt_tool]]:** If a JWT uses symmetric encryption (HS256) with a weak secret, Hashcat (Mode 16500) can crack the secret offline significantly faster than `jwt_tool`'s CPU-based cracker.

## Related Notes
- [[17 - Cryptographic Weaknesses]]
- [[18 - Pass the Hash]]
- [[19 - Password Policies and Authentication]]
