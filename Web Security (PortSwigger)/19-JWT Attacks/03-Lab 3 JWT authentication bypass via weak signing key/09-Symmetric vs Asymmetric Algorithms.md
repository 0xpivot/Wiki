---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Symmetric vs Asymmetric Algorithms

### Symmetric Algorithms

Symmetric algorithms use the same key for both encryption and decryption. Examples include AES and HMAC. In the context of JWTs, HS256 is a symmetric algorithm.

#### Weaknesses of Symmetric Algorithms

The main weakness of symmetric algorithms is that the key must be kept secret. If the key is compromised, an attacker can forge tokens. Additionally, if the key is weak or easily guessable, an attacker can brute-force the key.

### Asymmetric Algorithms

Asymmetric algorithms use a public-private key pair. The public key is used for encryption or verification, while the private key is used for decryption or signing. Examples include RSA and ECDSA. In the context of JWTs, RS256 is an asymmetric algorithm.

#### Strengths of Asymmetric Algorithms

Asymmetric algorithms are generally more secure than symmetric algorithms because the private key does not need to be shared. An attacker would need to obtain the private key to forge tokens, which is much harder than guessing a symmetric key.

---
<!-- nav -->
[[08-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/10-Practice Questions & Answers|Practice Questions & Answers]]
