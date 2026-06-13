---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.14 Insecure Randomness in Web Context"
---
# Insecure Randomness in Web Applications

## Introduction to Random Number Generation

Randomness is a cornerstone of modern web security. It is relied upon for generating session IDs, Anti-CSRF tokens, password reset links, OAuth states, cryptographic keys, and CAPTCHAs. 

Computers are deterministic machines; they cannot produce true randomness natively without hardware entropy sources. Instead, they use algorithms called Pseudorandom Number Generators (PRNGs). 

If an application uses a weak PRNG for security-critical functions, an attacker can predict future outputs or reverse-engineer past outputs, leading to catastrophic security failures.

## PRNG vs CSPRNG

1. **PRNG (Pseudorandom Number Generator)**: Algorithms designed for statistical randomness and speed. They are deterministic functions that take a starting value (the "seed") and produce a sequence of numbers. If you know the seed or the internal state, you can predict all future and past numbers. Examples: `Math.random()`, `rand()`, `mt_rand()`, `System.Random`.
2. **CSPRNG (Cryptographically Secure PRNG)**: Designed to resist prediction even if the attacker observes a massive sequence of outputs. They gather entropy from the operating system (e.g., hardware interrupts, mouse movements) and use cryptographic hashes or ciphers to mix the internal state. Examples: `/dev/urandom`, `random_bytes()`, `crypto.getRandomValues()`, `SecureRandom`.

## The Vulnerability: Using PRNGs for Security

A vulnerability occurs when developers use standard PRNGs instead of CSPRNGs for sensitive tokens.

### Common Predictability Vectors
- **Password Reset Tokens**: If generated with a weak PRNG, an attacker can request a reset token for their own account, calculate the PRNG state, request a reset for the admin account, and predict the admin's token.
- **Session IDs**: Predictable session IDs allow an attacker to hijack active user sessions.
- **CSRF Tokens**: Defeats Cross-Site Request Forgery protections.
- **UUIDv1**: UUID version 1 is based on the MAC address of the server and the exact timestamp. It is highly predictable and should never be used for security tokens. (UUIDv4 uses random numbers).

## Anatomy of an Attack: Cracking PHP's `mt_rand()`

For many years, PHP developers heavily relied on `mt_rand()`, which is an implementation of the Mersenne Twister algorithm (MT19937). 

The Mersenne Twister has a massive internal state (624 32-bit integers). However, it is explicitly *not* cryptographically secure. The math governing its state transitions is entirely linear.

### The Attack Flow
1. **Observation**: The attacker interacts with the application to observe outputs derived from `mt_rand()`. (e.g., creating 624 dummy accounts to see their random "user codes").
2. **State Recovery**: Because MT19937 is linear, observing exactly 624 outputs allows an attacker to perfectly reconstruct the internal state matrix.
3. **Prediction**: Once the state is rebuilt, the attacker can run a local copy of the Mersenne Twister algorithm, initialized with the stolen state, to predict the exact sequence of numbers the target server will generate next.

### ASCII Diagram: PRNG State Recovery

```text
Server (Mersenne Twister PRNG)                 Attacker
   |                                               |
   | Initialize State (Seed)                       |
   |                                               |
   | Generate Token 1 (Output 1)                   |
   |---------------------------------------------->|
   | ...                                           | Observe Outputs
   | Generate Token 624 (Output 624)               |
   |---------------------------------------------->|
   |                                               | Run Untwister Algorithm
   |                                               | Calculate Internal State
   | Generate Reset Token for Admin (Output 625)   |
   | (Stored in DB)                                | Attacker locally predicts Output 625!
   |                                               |
   |<----------------------------------------------| Submit Password Reset using Predicted Token
   | Check Token == Predicted (Match!)             |
   v                                               v
 Account Takeover Success
```

## Attacking `Math.random()` in JavaScript / V8

In Node.js and modern browsers (V8 engine), `Math.random()` is powered by the `XorShift128+` algorithm. 
Like Mersenne Twister, XorShift is not cryptographically secure. Its internal state consists of only two 64-bit integers. 

By collecting just a few outputs from `Math.random()` (e.g., from an exposed password generation endpoint in Node.js), an attacker can use SMT solvers (like Z3) to solve the algebraic equations of the XorShift algorithm and recover the two 64-bit state variables. From there, future outputs are 100% predictable.

## The Seed Brute-Force Attack

Sometimes, observing the internal state isn't necessary if the PRNG is seeded weakly. 
For example, if an application seeds a PRNG with the current UNIX timestamp (seconds since 1970) right before generating a token:

```php
// VULNERABLE
srand(time());
$token = md5(rand());
```

An attacker knows the approximate time the token was generated. They can write a script to brute-force the `time()` value locally across a small window (e.g., +/- 10 minutes = 1200 seconds), generating 1200 possible tokens, and testing them against the target.

## Mitigation Strategies

### 1. Always Use CSPRNGs for Security Contexts
Never use `rand()`, `mt_rand()`, `Math.random()`, or `System.Random` for anything security-related.
- **PHP**: Use `random_bytes()` or `random_int()`.
- **Node.js**: Use `crypto.randomBytes()`.
- **Python**: Use the `secrets` module (e.g., `secrets.token_hex()`), not the `random` module.
- **Java**: Use `java.security.SecureRandom`.

### 2. Use UUIDv4 (Correctly)
If using UUIDs for sensitive identifiers (like IDOR-resistant object references or password reset links), ensure you are using UUIDv4, and verify that the underlying library uses a CSPRNG to generate the random bits. Never use UUIDv1.

### 3. High Entropy Generation
Ensure that generated tokens have sufficient entropy to resist brute-force attacks. A password reset token should be at least 32 bytes (256 bits) of true random data, encoded in hex or base64.

## Chaining Opportunities
- **Account Takeover**: Predicting password reset links or email verification codes.
- **Session Hijacking**: Predicting session IDs to impersonate active users.
- **CSRF Bypass**: Predicting Anti-CSRF tokens to successfully forge state-changing requests.
- **Cryptographic Failures**: If a weak PRNG is used to generate RSA/AES keys, the keys themselves can be recovered.

## Related Notes
- [[04 - Cross-Site Request Forgery (CSRF)]]
- [[38 - Cryptographic Failures]]
- [[05 - Broken Access Control]]
- [[34 - JSON Web Token (JWT) Security]]
