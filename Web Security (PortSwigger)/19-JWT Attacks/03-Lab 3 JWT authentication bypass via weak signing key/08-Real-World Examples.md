---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Real-World Examples

### Recent Breaches Involving Weak JWT Keys

#### Example 1: CVE-2021-3129

In 2021, a vulnerability was discovered in the Jenkins CI/CD platform (CVE-2021-3129). This vulnerability allowed attackers to bypass authentication by exploiting a weak signing key used in JWTs. The attackers could generate valid tokens and gain unauthorized access to the system.

#### Example 2: CVE-2022-22965

Another notable example is CVE-2022-22965, which affected the Apache Log4j library. Although this vulnerability primarily involved remote code execution, it also highlighted the importance of securing JWTs. Attackers could leverage weak keys to forge tokens and escalate their privileges within the system.

### How Weak Keys Are Exploited

Attackers often use tools like `Hashcat` to brute-force the signing key. `Hashcat` is a powerful password recovery tool that supports various hashing algorithms, including those commonly used in JWTs.

### Steps to Exploit Weak JWT Keys

1. **Obtain the JWT**: The attacker needs to obtain a valid JWT from the target system. This can be done through various methods, such as intercepting network traffic or social engineering.
2. **Extract the Header and Payload**: The attacker extracts the header and payload from the JWT.
3. **Brute-Force the Signature**: Using a tool like `Hashcat`, the attacker attempts to brute-force the signing key. This process can take a significant amount of time, depending on the complexity of the key.

### Example of Brute-Forcing a JWT Key

Let's walk through an example of how an attacker might brute-force a JWT key using `Hashcat`.

#### Step 1: Obtain the JWT

Assume the attacker has obtained the following JWT:

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MzEwMDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

#### Step 2: Extract the Header and Payload

Using a JWT decoder, the attacker extracts the header and payload:

- **Header**:
  ```json
  {
    "alg": "HS256",
    "typ": "JWT"
  }
  ```

- **Payload**:
  ```json
  {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
  }
  ```

#### Step 3: Brute-Force the Signature

The attacker uses `Hashcat` to brute-force the signing key. Here is an example of how to set up `Hashcat` for this task:

```bash
hashcat -m 16500 -a 3 --force <hash> <wordlist>
```

Where:
- `-m 16500`: Specifies the hash mode (HS256 in this case).
- `-a 3`: Specifies the attack mode (brute-force).
- `<hash>`: The hash value to crack (the signature part of the JWT).
- `<wordlist>`: The wordlist to use for the brute-force attack.

### Mermaid Diagram: JWT Brute-Force Attack Chain

```mermaid
sequenceDiagram
    participant Attacker
    participant JWT
    participant Hashcat
    participant TargetSystem

    Attacker->>JWT: Obtain JWT
    JWT-->>Attacker: JWT Token
    Attacker->>Hashcat: Extract Header and Payload
    Hashcat-->>Attacker: Header and Payload
    Attacker->>Hashcat: Brute-Force Signature
    Hashcat-->>Attacker: Cracked Key
    Attacker->>TargetSystem: Forge New JWT
    TargetSystem-->>Attacker: Unauthorized Access
```

---
<!-- nav -->
[[07-JWT Authentication Bypass via Weak Signing Key|JWT Authentication Bypass via Weak Signing Key]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]] | [[09-Symmetric vs Asymmetric Algorithms|Symmetric vs Asymmetric Algorithms]]
