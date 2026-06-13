---
tags: [ctf, practice, lab, vapt]
difficulty: intermediate
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.27 CTF Challenge Crypto"
---

# 60.27 CTF Challenge Walkthroughs: Crypto Category

## Introduction to Crypto CTF Challenges

Cryptography (Crypto) challenges in Capture The Flag (CTF) competitions rigorously test a participant's grasp of advanced mathematical concepts, the internal mechanics of cryptographic algorithms, and crucially, the catastrophic flaws that arise from improper implementation. 

Unlike real-world VAPT scenarios where attackers typically bypass cryptography entirely by stealing keys from memory, targeting the surrounding infrastructure, or relying on social engineering, CTF crypto challenges force the attacker to attack the cryptography directly. This requires breaking the underlying math, exploiting predictable random number generators, or abusing structural weaknesses in cipher modes.

Crypto challenges span a wide spectrum: from classical substitution ciphers (Caesar, Vigenère) to modern asymmetric public-key cryptography (RSA, Elliptic Curve Cryptography) and symmetric block/stream ciphers (AES, ChaCha20, RC4).

This document outlines a systematic methodology, explores common vulnerability classes, and provides deep-dive walkthroughs for conquering Crypto CTF challenges.

## The Crypto CTF Methodology

Approaching a Crypto CTF challenge requires a methodical, deeply analytical mindset. The process is less about running automated scanners and more about mathematical deduction and custom scripting.

1. **Identification and Fingerprinting:** Determine the cryptographic algorithm in use. This can be deduced from provided source code, file extensions (`.enc`, `.pem`), the structure of the ciphertext (hex dumps, Base64 strings), or standard cryptographic headers (like PKCS#7 or ASN.1 structures).
2. **Implementation Analysis:** Meticulously analyze the code for implementation flaws. Cryptography is notoriously difficult to implement securely; custom rolled crypto almost always contains fatal vulnerabilities. Look specifically for:
    - Reused Nonces or Initialization Vectors (IVs).
    - Dangerously small key sizes or predictable key generation logic.
    - Weak or non-cryptographically secure Pseudo-Random Number Generators (PRNGs), such as Python's default `random` module or PHP's `mt_rand()`.
    - Improper handling of cryptographic padding (leading to oracle attacks).
3. **Mathematical Attack Formulation:** Once the flaw is identified, formulate the mathematical or structural attack. This may involve modular arithmetic, lattice basis reduction (LLL algorithm), differential cryptanalysis, or algebraic manipulation.
4. **Scripting and Execution:** Implement the mathematical attack using robust programming languages. Python is the industry standard for this, relying heavily on libraries like `pwntools` for network interaction, `pycryptodome` for cryptographic primitives, and `SageMath` for advanced mathematical computations.

## ASCII Diagram: Typical Crypto CTF Attack Flow Architecture

```text
+-------------------+       1. Identify Algorithm  +-------------------+
|                   | ---------------------------> |                   |
|   CTF Player /    |                              |   Ciphertext /    |
|   Cryptanalyst    | <--------------------------- |   Source Code     |
|   (SageMath/Py)   |       (e.g., RSA, AES)       |   (Black/Whitebox)|
+-------------------+                              +-------------------+
        |                                                    |
        | 2. Analyze Implementation & Identify Flaws         |
        v                                                    v
+-------------------+                              +-------------------+
| Common Flaws:     |                              | Crypto Primitives:|
| - Small Primes (p)|                              | - Mod Arithmetic  |
| - IV / Nonce Reuse|                              | - XOR Operations  |
| - Predictable PRNG|                              | - Block Modes     |
+-------------------+                              +-------------------+
        |
        | 3. Formulate Mathematical Attack Strategy
        v
+-------------------------------------------------------------+
| Exploitation Phase & Mathematical Attacks:                  |
| [ ] Prime Factorization (Fermat, Wiener's, Coppersmith's)   |
| [ ] Padding Oracle Attack (Byte-at-a-time ECB/CBC decrypt)  |
| [ ] Hash Length Extension (Merkle-Damgård appending)        |
| [ ] PRNG State Recovery (Mersenne Twister cracking)         |
+-------------------------------------------------------------+
        |
        | 4. Execute Attack Script via Network or Locally
        v
+-------------------+                              +-------------------+
|                   |      Attack Payload          |                   |
|   Custom Python   | ---------------------------> |   Cryptosystem    |
|   Exploit Script  |                              |   (Local/Remote)  |
|                   | <--------------------------- |                   |
+-------------------+      Flag / Decrypted Data   +-------------------+
```

## Deep Dive Walkthrough 1: Asymmetric Cryptography (RSA Misconfigurations)

RSA (Rivest-Shamir-Adleman) is the cornerstone of public-key cryptography. In CTFs, RSA challenges are ubiquitous and typically involve exploiting mathematical relationships between the public and private keys due to poor parameter generation.

**The RSA Primer:**
- Generate two distinct, large prime numbers, $p$ and $q$.
- Compute the modulus $n = p \times q$.
- Compute Euler's totient function $\phi(n) = (p-1) \times (q-1)$.
- Choose a public exponent $e$ such that $1 < e < \phi(n)$ and $gcd(e, \phi(n)) = 1$. (Commonly 65537).
- Calculate the private exponent $d$ as the modular multiplicative inverse: $d \equiv e^{-1} \pmod{\phi(n)}$.

Public key: $(e, n)$. Private key: $(d, n)$.
Encryption: $c \equiv m^e \pmod{n}$
Decryption: $m \equiv c^d \pmod{n}$

### Scenario: The Small Exponent Attack (e=3)
You are provided with a public key where $e = 3$, a massive modulus $n$, and the ciphertext $c$. The plaintext message $m$ is known to be relatively small (e.g., just the flag string).

**Vulnerability Analysis:**
If the message $m$ is small enough, and the exponent $e$ is very small (like 3), the resulting value of $m^e$ might be mathematically smaller than the modulus $n$.
If $m^e < n$, then the modular reduction operation $\pmod{n}$ never actually occurs. The ciphertext $c$ is simply the standard integer cube of the message $m$ ($c = m^3$).

**Exploitation:**
To decrypt the message, we do not need the private key $d$. We merely need to calculate the standard integer cube root of the ciphertext $c$.

```python
import gmpy2
from Crypto.Util.number import long_to_bytes

c = 12345678901234567890... # Massive integer ciphertext
e = 3

# Calculate the exact integer cube root using gmpy2
m, is_perfect_cube = gmpy2.iroot(c, e)

if is_perfect_cube:
    # Convert the long integer back to a byte string
    flag = long_to_bytes(m)
    print(f"Decrypted Flag: {flag.decode('utf-8')}")
else:
    print("Not a perfect cube, message was padded or m^e > n.")
```

### Scenario: Common Modulus Attack
You intercept two distinct ciphertexts, $c_1$ and $c_2$, representing the exact same plaintext message $m$. They were encrypted using the same modulus $n$, but two different public exponents, $e_1$ and $e_2$.

**Exploitation (Extended Euclidean Algorithm):**
If the two exponents are coprime, meaning $gcd(e_1, e_2) = 1$, we can utilize the Extended Euclidean Algorithm to find integers $a$ and $b$ (where one is negative) such that Bezout's identity holds: $a \cdot e_1 + b \cdot e_2 = 1$.

Given $c_1 \equiv m^{e_1} \pmod{n}$ and $c_2 \equiv m^{e_2} \pmod{n}$:
$c_1^a \cdot c_2^b \equiv (m^{e_1})^a \cdot (m^{e_2})^b \equiv m^{a \cdot e_1 + b \cdot e_2} \equiv m^1 \equiv m \pmod{n}$

We calculate $c_1^a \cdot c_2^b \pmod{n}$ to recover the original message $m$ entirely bypassing the need to factor $n$.

## Deep Dive Walkthrough 2: Symmetric Cryptography (AES Block Cipher Modes)

The Advanced Encryption Standard (AES) is a symmetric block cipher. CTF challenges almost never attack the AES algorithm itself (which remains secure), but rather how the cipher is implemented via Block Cipher Modes of Operation (ECB, CBC, CTR, GCM).

### Scenario: Cipher Block Chaining (CBC) Padding Oracle Attack
CBC mode requires padding (usually PKCS#7) to ensure the plaintext aligns perfectly with the cipher's block size (16 bytes for AES). A Padding Oracle vulnerability arises when an application or API leaks information about whether the padding of a submitted, decrypted ciphertext is valid or invalid.

**Reconnaissance & Detection:**
A web service uses encrypted session tokens formatted as `IV || Ciphertext`.
- If you modify the ciphertext slightly and submit it, and the server responds with an HTTP 500 "Internal Server Error" (indicating padding failure).
- If you submit valid padding but garbage data, it responds with an HTTP 200 "OK" but a logical error "Invalid Session".
This discrepancy is a Padding Oracle.

**Exploitation Mechanics:**
This side-channel information leakage allows an attacker to systematically decrypt the entire ciphertext *without ever knowing the encryption key*.
In CBC decryption, the intermediate state (output of AES decryption before XORing with the previous block) is XORed with the previous ciphertext block to produce the plaintext.
By intentionally corrupting a byte in ciphertext block $C_{N-1}$, the attacker affects a single byte in the resulting plaintext block $P_N$.
By iterating through all 256 possible byte values and observing the server's response (hunting for the "Valid Padding" signal), the attacker deduces the intermediate state byte.
Once the intermediate state is known, the attacker simply XORs it with the original $C_{N-1}$ block to reveal the actual plaintext byte. This is repeated byte-by-byte for the entire ciphertext. Tools like `padBuster` or custom Python scripts automate this tedious process.

### Scenario: Stream Ciphers and Nonce Reuse (AES-CTR / ChaCha20)
Stream ciphers (or block ciphers operating in stream modes like Counter Mode - CTR) generate a pseudorandom keystream which is then XORed with the plaintext to create the ciphertext.
$C = P \oplus Keystream$

**The Fatal Flaw:**
The golden rule of stream ciphers is that a Keystream (Key + Nonce/IV) must **never** be used twice.
If two different plaintexts ($P_1$ and $P_2$) are encrypted with the identical keystream:
$C_1 = P_1 \oplus Keystream$
$C_2 = P_2 \oplus Keystream$
An attacker can XOR the two ciphertexts together:
$C_1 \oplus C_2 = (P_1 \oplus Keystream) \oplus (P_2 \oplus Keystream) = P_1 \oplus P_2$
The keystream cancels out entirely. The attacker is left with the XOR of the two plaintexts. By using statistical language analysis, crib dragging (guessing known plaintext words like "the", "flag{"), the attacker can unravel both original messages without knowing the key.

## Deep Dive Walkthrough 3: Hash Length Extension Attacks

Cryptographic hash functions like MD5, SHA-1, and SHA-256 utilize the Merkle-Damgård construction. This specific architectural choice makes them inherently vulnerable to Length Extension Attacks when used improperly as a Message Authentication Code (MAC).

### Scenario: The Insecure Custom MAC
An API authenticates administrative commands by checking a signature generated as follows:
`signature = SHA256(secret_key || user_data)`
You are provided with standard user data `user_data="role=guest"` and its corresponding valid signature.

**Exploitation Mechanics:**
Because of the Merkle-Damgård construction, the final output of the SHA-256 hash function essentially represents the internal state of the hashing algorithm after processing the entire input block.
An attacker can take the original signature, use it to initialize the internal registers of their own local SHA-256 implementation, and seamlessly continue hashing additional, malicious data.
This allows the attacker to append data and generate a perfectly valid signature for:
`user_data="role=guest" + padding + "&role=admin"`
The attacker achieves this forgery *without ever knowing the contents or length of the `secret_key`*. Dedicated tools like `hashpump` or `hash-extender` make executing this attack trivial.

## Advanced Concepts and Further Study

As practitioners advance to harder CTFs and real-world cryptographic audits, more complex mathematical concepts are required:
- **Lattice-Based Cryptography & LLL:** Using the Lenstra-Lenstra-Lovász lattice basis reduction algorithm to find small roots of polynomial equations. This is essential for Coppersmith's Attack on RSA (when parts of the message or key are known).
- **Elliptic Curve Cryptography (ECC):** Exploiting weak curve parameters, invalid curve attacks, or nonce reuse in ECDSA (which leaks the private signing key instantly).
- **PRNG Cracking:** Recovering the internal state of the Mersenne Twister (used in Python's `random`) after observing 624 consecutive 32-bit outputs, allowing perfect prediction of all future "random" numbers.

## Tooling and Environment Setup

A robust cryptographic auditing environment requires specialized tools. A standard Kali Linux VM might not suffice.
- **SageMath:** A colossal, open-source mathematics software system built on top of Python. It is absolutely mandatory for advanced algebraic and lattice-based attacks.
- **pwntools:** A Python CTF framework for rapid exploit development, specifically useful for scripting network interactions with remote crypto oracles.
- **pycryptodome:** The standard Python library for implementing and testing cryptographic primitives locally.

## Chaining Opportunities

- **Hash Length Extension to Authentication Bypass:** In bespoke web applications or custom APIs, bypassing MAC validation using length extension allows an attacker to forge administrative cookies or API tokens, leading to full application compromise and vertical privilege escalation.
- **Padding Oracle to Remote Code Execution:** A padding oracle can be utilized to decrypt encrypted session tokens that obscure internal file paths or serialized objects. Once decrypted, tampered with, and re-encrypted (via a CBC-MAC forgery or encryption oracle), the manipulated token can trigger Insecure Deserialization or Local File Inclusion (LFI), resulting in RCE.
- **Weak PRNG to Session Hijacking:** If an application generates password reset tokens or session IDs using a predictable, non-cryptographic PRNG (like PHP's `mt_rand()` or an unseeded standard random function), an attacker can observe several tokens, recover the PRNG state, predict the token for an administrator's password reset link, and completely hijack the account.

## Related Notes
- [[21 - Cryptographic Failures]]
- [[22 - Insufficient Logging and Monitoring]]
- [[26 - CTF Challenge Walkthroughs Web Category]]
- [[18 - Broken Access Control]]
- [[19 - Identification and Authentication Failures]]
