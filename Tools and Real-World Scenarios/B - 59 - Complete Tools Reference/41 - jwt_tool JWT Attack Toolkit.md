---
tags: [tools, web-testing, utility, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.41 jwt_tool JWT Attack Toolkit"
---

# 59.41 jwt_tool JWT Attack Toolkit

## 1. Introduction and Core Capabilities

The `jwt_tool` toolkit is an indispensable command-line utility for penetration testers, bug bounty hunters, and security researchers focusing on modern web applications and APIs. 

JSON Web Tokens (JWT) have become the de facto standard for stateless authentication and authorization. However, the flexibility and complexity of the JOSE (JSON Object Signing and Encryption) standards frequently lead to severe implementation flaws. Developers often trust user-supplied headers or misconfigure validation routines, transforming a secure token into an arbitrary authentication bypass vector.

### 1.1 Why jwt_tool?

While basic base64 decoding of JWTs can be done in a browser console, exploiting cryptographic flaws requires specialized automation. `jwt_tool` bridges this gap by providing an all-in-one suite to validate, forge, tamper with, and crack JWTs.

### 1.2 Primary Features

*   **Automated Vulnerability Scanning**: Sequentially tests for known CVEs and common implementation logic flaws.
*   **High-Speed Key Cracking**: Built-in dictionary and brute-force capabilities for discovering weak HMAC symmetric secrets.
*   **Seamless Token Forgery**: Easily tamper with payload claims (e.g., changing user IDs or roles) and automatically re-sign the token using known or extracted keys.
*   **Cryptographic Confusion**: Automates the highly complex process of substituting public RSA keys for HMAC verification (Key Confusion attacks).

## 2. Attack Architecture & Workflow

The following ASCII diagram illustrates the standard JWT testing workflow using `jwt_tool`, moving from initial interception to active forgery and exploitation.

```text
+-------------------+        [1] Intercept JWT         +----------------------+
|                   | -------------------------------> |                      |
|  Attacker Client  |                                  |  Target Application  |
|                   | <------------------------------- |  (API Gateway / Auth)|
+-------------------+        [5] Unauthorized Access   +----------------------+
        |  ^                                                      ^
        |  | [4] Inject Forged JWT                                |
        v  |                                                      |
+-----------------------------------------------------------------------------+
|                               jwt_tool Engine                               |
|                                                                             |
|  [2] Automated Tests (jwt_tool.py <TOKEN> -M pb)                            |
|  +-----------------------------------------------------------------------+  |
|  | * ALG: None Check (CVE-2015-9256)                                     |  |
|  | * Key Confusion (RSA to HMAC)                                         |  |
|  | * JWKS Spoofing / JKU Injection Header Checks                         |  |
|  | * Weak HMAC Offline Cracking (using local dictionary)                 |  |
|  +-----------------------------------------------------------------------+  |
|                                     |                                       |
|  [3] Token Forgery & Tampering (jwt_tool.py <TOKEN> -T)  v                  |
|  +-----------------------------------------------------------------------+  |
|  |   Header: {"alg":"HS256"} -> {"alg":"none"}                           |  |
|  |   Payload: {"user":"guest"} -> {"user":"admin", "role":"superuser"}   |  |
|  |   Signature: Stripped entirely or Recalculated with cracked secret    |  |
|  +-----------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------+
```

## 3. Installation and Setup

`jwt_tool` is actively maintained and relies on specific cryptographic libraries. It is highly recommended to run it within an isolated Python virtual environment.

### 3.1 Basic Installation

```bash
# Clone the repository
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool

# Install dependencies
python3 -m pip install termcolor cprint pycryptodomex requests

# Verify installation
python3 jwt_tool.py
```

### 3.2 Dictionary and Cache Setup

For offline HMAC cracking, `jwt_tool` relies on a local dictionary file. By default, the included dictionary is extremely small. For real-world assessments, link a robust wordlist like `rockyou.txt`.

```bash
# Backup the default
mv jwt_tool/dictionary.txt jwt_tool/dictionary.txt.bak

# Link a larger wordlist
ln -s /usr/share/wordlists/rockyou.txt jwt_tool/dictionary.txt
```

## 4. Deep Dive: Core Execution Modes

`jwt_tool` operates primarily through distinct 'Modes', specified by the `-M` flag. Understanding these modes is crucial for effective testing.

### 4.1 Mode `pb`: Playbook Mode (Automated Scanning)

Playbook mode is the recommended starting point for any JWT assessment. It runs a sequential battery of tests.

*   **Syntax**: `python3 jwt_tool.py <TOKEN> -M pb`
*   **Methodology**:
    1.  Validates basic formatting and decodes headers/payloads.
    2.  Checks if the backend strictly validates the signature (or if it blindly accepts modifications).
    3.  Attempts the 'None' algorithm vulnerability.
    4.  Tries common weak secrets via the configured dictionary.
    5.  Tests for Key Confusion if a public key certificate is supplied via flags.

### 4.2 Mode `c`: Crack Mode

When encountering tokens utilizing symmetric encryption (`HS256`, `HS384`, `HS512`), security relies entirely on the strength of the secret key.

*   **Syntax**: `python3 jwt_tool.py <TOKEN> -M c -d /path/to/wordlist.txt`
*   **Mechanics**: The tool iteratively hashes the original header and payload with each word in the dictionary. It then compares the resulting base64url-encoded string to the original signature. A match mathematically guarantees the secret has been found.

### 4.3 Mode `at`: All Tests

This mode is similar to Playbook but is highly aggressive and verbose. It attempts every single module and exploit path regardless of initial indicator results.

*   **Syntax**: `python3 jwt_tool.py <TOKEN> -M at`

## 5. Advanced Exploitation Vectors

### 5.1 The 'None' Algorithm Attack

Historically, many JWT libraries accepted `alg: none` (or case-variations like `NoNe`, `NONE`), treating the token as unencrypted and explicitly bypassing signature verification.

1.  **Tamper Payload**: Modify standard claims (e.g., `{"role": "user"}` to `{"role": "admin"}`).
2.  **Modify Header**: Change the algorithm definition to `none`.
3.  **Strip Signature**: Remove the cryptographic signature, leaving the trailing dot (`Header.Payload.`).

*   **jwt_tool Automation**: 
    ```bash
    python3 jwt_tool.py <TOKEN> -I -pc role -pv admin -X a
    ```
    *(Here, `-X a` explicitly tells the tool to execute the 'alg: none' exploit).*

### 5.2 RS256 to HS256 Key Confusion (CVE-2015-9256)

If an application expects an RSA signature (RS256) but relies on the token's `alg` header to determine the verification method, an attacker can exploit this if they obtain the backend's *public* key.

1.  The attacker extracts the target's public key (often found at endpoints like `/jwks.json` or within public TLS certificates).
2.  The attacker changes the JWT `alg` header from `RS256` to `HS256`.
3.  The attacker signs the tampered token using the *public key string* as the HMAC symmetric secret.
4.  The vulnerable backend reads `HS256`, assumes it must perform an HMAC verification, and uses its configured key (which is the public key) to verify. The signature matches!

*   **jwt_tool Automation**: 
    ```bash
    python3 jwt_tool.py <TOKEN> -M at -pk target_public_key.pem
    ```

### 5.3 JWKS Spoofing and JKU Header Injection

The `jku` (JWK Set URL) header instructs the verifying server where to fetch the public key. If the server trusts this header without validation, an attacker can host their own key set.

1.  Generate a malicious RSA private/public keypair.
2.  Host the public key in JWKS JSON format on an attacker-controlled server (`http://evil.com/jwks.json`).
3.  Modify the JWT header: `{"alg": "RS256", "jku": "http://evil.com/jwks.json"}`.
4.  Sign the payload with the malicious private key.

## 6. Token Tampering and Forgery (-T Mode)

Once a vulnerability is confirmed or a key is cracked, `jwt_tool` facilitates seamless token generation.

```bash
python3 jwt_tool.py <TOKEN> -T -S hs256 -p "SuperSecret123!" -I -pc username -pv admin
```

### 6.1 Command Line Flag Reference

| Flag | Description | Example Usage |
| :--- | :--- | :--- |
| `-M` | Execution Mode (`pb`, `c`, `at`). | `-M pb` |
| `-T` | Tamper Mode. Allows claim modification. | `-T` |
| `-I` | Interactive injection mode. | `-I` |
| `-pc` | Payload claim to target. | `-pc "role"` |
| `-pv` | Payload value to inject. | `-pv "administrator"` |
| `-hc` | Header claim to target. | `-hc "kid"` |
| `-S` | Signature algorithm to use when re-signing. | `-S hs256` |
| `-p` | Password/secret for HMAC signing. | `-p "cracked_secret"` |

### 6.2 Data Type Handling

When injecting claims via the CLI, it is critical to ensure data types match backend expectations.
*   **Strings**: `-pv "admin"`
*   **Integers**: `-pv 1` (jwt_tool will prompt for type conversion in Interactive mode).
*   **Booleans**: `-pv true`

## 7. Troubleshooting and Common Errors

*   **Malformed Base64**: If the application uses non-standard base64 padding or custom URL encoding, `jwt_tool` may fail to parse the token initially. Manual decoding/re-encoding may be required before feeding it to the tool.
*   **JWE (Encrypted Tokens)**: `jwt_tool` focuses heavily on JWS (Signed tokens). While it can parse the structure of JWEs, exploiting them typically requires the decryption key, which cannot be cracked via offline dictionary attacks in the same manner.
*   **Cracking Speed Limits**: Python is relatively slow for cryptographic hashing. If you are dealing with a strong HMAC secret, extract the token and use a dedicated GPU cracker like Hashcat.
    *   *Hashcat Syntax*: `hashcat -a 0 -m 16500 token.txt wordlist.txt`

## 8. Defensive Mitigation and Remediation

When authoring vulnerability reports based on `jwt_tool` findings, recommend the following architectural and code-level mitigations:

1.  **Strict Algorithm Whitelisting**: The backend must firmly reject `alg: none`. It must strictly enforce the expected algorithm natively in the code (e.g., `if (token.header.alg !== 'RS256') throw Error;`).
2.  **Explicit Key Verification**: Do not use overloaded, polymorphic validation methods like `verify(token, key)`. Use distinct functions for asymmetric versus symmetric verification to fundamentally prevent Key Confusion.
3.  **Cryptographically Strong Secrets**: HMAC secrets must be randomly generated and possess high entropy. Their length should be at least equal to the hash output size (e.g., minimum 256 bits for HS256).
4.  **Header Distrust**: Headers such as `jku`, `jwk`, `x5u`, and `kid` should be heavily restricted. If used, they must be validated against a strict, server-side whitelist.
5.  **Token Expiration**: Always implement short-lived `exp` (Expiration Time) claims and utilize refresh tokens to limit the window of opportunity for stolen or forged tokens.

## 9. Chaining Opportunities

*   **[[01 - Insecure Direct Object References (IDOR)]]**: Modifying user IDs, UUIDs, or email claims within a forged JWT payload to forcefully access other users' protected data.
*   **[[02 - Privilege Escalation]]**: Changing boolean flags like `is_admin` or string roles like `role: guest` to gain administrative application access.
*   **[[03 - Server-Side Request Forgery (SSRF)]]**: Exploiting the `jku` or `x5u` headers to force the backend server to make internal HTTP requests to retrieve keys, potentially exposing internal metadata services.
*   **[[17 - Path Traversal]]**: Injecting directory traversal payloads into the `kid` (Key ID) header to force the application to load symmetric keys from arbitrary local files (e.g., `../../../../dev/null`).

## 10. Related Notes

*   [[12 - Broken Authentication]]
*   [[15 - Cryptographic Failures]]
*   [[22 - API Authentication Bypasses]]
*   [[24 - JWT Security Best Practices]]
*   [[99 - Penetration Testing Cheatsheet]]
