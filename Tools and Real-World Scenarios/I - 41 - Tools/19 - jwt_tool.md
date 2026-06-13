---
tags: [tools, vapt, utility, web, api-security, jwt]
difficulty: intermediate
module: "41 - Tools"
topic: "41.19 jwt_tool"
---

# jwt_tool: The Swiss Army Knife for JSON Web Token Exploitation

## 1. Overview and Introduction

`jwt_tool` is an advanced, open-source toolkit written in Python, designed specifically for testing, tweaking, and cracking JSON Web Tokens (JWTs). In the realm of API Security (Module 31), JWTs have become the standard mechanism for stateless authentication and authorization. Because the state is stored client-side within the token itself, vulnerabilities in how the backend API verifies the token's signature can lead to devastating consequences, including complete account takeover and privilege escalation.

`jwt_tool` automates the complex cryptographic attacks associated with JWTs, making it an indispensable asset for API penetration testing.

## 2. Anatomy of a JSON Web Token

A JWT consists of three parts, separated by dots (`.`): `Header.Payload.Signature`.

1.  **Header:** Contains metadata about the token, specifically the `alg` (algorithm) used for signing (e.g., `HS256`, `RS256`) and the `typ` (type), which is `JWT`.
2.  **Payload:** Contains the claims (the actual data), such as `{"user_id": 123, "role": "user"}`.
3.  **Signature:** A cryptographic hash of the Base64Url-encoded header and payload, signed using a secret key (symmetric) or a private key (asymmetric).

The vulnerability arises when an attacker can modify the payload (e.g., change `"role": "user"` to `"role": "admin"`) and successfully forge a valid signature that the API accepts.

## 3. Architecture and Attack Diagram

### 3.1 Custom ASCII Attack Diagram

```text
+-------------------------------------------------------+
|                 JWT Forgery Attack Flow               |
+-------------------------------------------------------+
|                                                       |
|  +-----------------+        Intercept / Modify        |
|  | Attacker Client | ---------------------------+     |
|  | (jwt_tool)      |                            |     |
|  +--------+--------+                            |     |
|           |                                     v     |
|           |   1. Parse Original JWT      +---------------+
|           |   2. Tamper Payload          |  Target API   |
|           |      (role: admin)           | (Resource)    |
|           |   3. Modify Signature        +---------------+
|           |      (None Alg / Crack)             |     |
|           |   4. Send Malicious Request         |     |
|           +-------------------------------------+     |
|                                                       |
|   eyJhbGci...  ----(tampered)----> API Validates?     |
|                                                       |
+-------------------------------------------------------+
```

## 4. Key Attack Vectors Automated by jwt_tool

### 4.1 The 'None' Algorithm Attack
The JWT specification originally allowed an `alg` of `none`. If an API blindly trusts the header, an attacker can set `"alg": "none"`, modify the payload, strip the signature, and the API will accept it.
**Usage in jwt_tool:**
```bash
python3 jwt_tool.py <token> -X a
```
*This command runs through all known bypass variations of the `none` algorithm (e.g., `None`, `NONE`, `nOnE`).*

### 4.2 Algorithm Confusion (RS256 to HS256)
If an API expects an asymmetric signature (`RS256` using a public/private keypair) but doesn't verify the algorithm, an attacker can obtain the server's *public* key, change the header to `HS256` (symmetric), and sign the token using the public key as the symmetric HMAC secret. If the backend uses the same verification function and just passes the public key as the secret, it will validate successfully.
**Usage in jwt_tool:**
```bash
python3 jwt_tool.py <token> -X k -pk public.pem
```

### 4.3 Signature Brute-Forcing / Cracking
If a JWT uses `HS256` (symmetric) and the secret key is weak (e.g., "secret", "password123"), attackers can crack it offline. Once the secret is known, the attacker can forge valid tokens at will.
**Usage in jwt_tool (Dictionary Attack):**
```bash
python3 jwt_tool.py <token> -C -d rockyou.txt
```

### 4.4 JWKS (JSON Web Key Set) Spoofing
APIs often fetch the public key dynamically from a URL specified in the `jku` (JWK Set URL) header parameter. An attacker can host their own JWKS file, inject their `jku` URL into the header, and sign the token with their corresponding private key.
**Usage in jwt_tool:**
```bash
python3 jwt_tool.py <token> -X i -jku https://attacker.com/jwks.json
```

### 4.5 Kid (Key ID) Injection
The `kid` header parameter points to a specific key in a database or file system. This is vulnerable to Path Traversal or SQL Injection.
- **Path Traversal:** Set `"kid": "../../../dev/null"` and sign the token with an empty string.
- **SQLi:** Set `"kid": "key1' UNION SELECT 'attacker_key'--"`

## 5. Integrating jwt_tool into the Workflow

`jwt_tool` can be used as a standalone CLI tool or integrated dynamically into Burp Suite via the `jwt_tool` Burp extension or by using it in a proxy chain.

**Interactive Mode:**
For deep manipulation, `jwt_tool` offers an interactive mode:
```bash
python3 jwt_tool.py <token> -I
```
This drops the user into a console where they can modify claims, inject headers, tamper with timestamps (`exp`, `iat`), and dynamically re-sign the token.

## 6. Detection and Defenses

### 6.1 Detection
- **WAF Rules:** Web Application Firewalls can detect common `alg: none` payloads or obvious SQLi/Path Traversal attempts in the JWT header.
- **Log Analysis:** Monitor for rejected tokens with abnormal `kid` or `jku` parameters.

### 6.2 Mitigation
1.  **Enforce Algorithms:** Backend APIs MUST hardcode the expected algorithm (e.g., enforce `RS256`) and reject tokens that specify anything else, regardless of what the header says.
2.  **Strong Secrets:** For `HS256`, use a cryptographically secure random string of at least 256 bits (32 bytes).
3.  **Validate `jku` and `kid`:** Maintain a strict whitelist of allowed JWKS URLs and sanitize/validate any `kid` inputs before querying databases or file systems.
4.  **Use established libraries:** Never write a custom JWT verification library. Use established, patched libraries that handle `none` algorithm and algorithm confusion attacks by default.

## 7. Conclusion

As APIs transition from stateful session cookies to stateless JWTs, the attack surface shifts from the application logic to cryptographic implementation flaws. `jwt_tool` perfectly bridges this gap, providing penetration testers with the capability to rapidly identify and exploit misconfigurations in API authentication mechanisms.

---

## Chaining Opportunities
- **[[05 - Authentication Bypasses]]:** Use `jwt_tool` to forge an admin token, completely bypassing the authentication portal of a web application.
- **[[20 - Hashcat]]:** If `jwt_tool`'s CPU-based cracking is too slow for a complex HMAC secret, pass the JWT to Hashcat (Mode 16500) to leverage GPU acceleration.
- **[[01 - API1 — Broken Object Level Authorization (BOLA)]]:** Even if the signature cannot be forged, decoding the JWT with `jwt_tool` can reveal predictable identifiers (like `user_id: 1234`). Modifying these IDs (if signatures aren't properly validated) leads directly to BOLA vulnerabilities.

## Related Notes
- [[14 - Cryptography Basics]]
- [[15 - OAuth and OIDC Internals]]
- [[16 - API Security Top 10]]
