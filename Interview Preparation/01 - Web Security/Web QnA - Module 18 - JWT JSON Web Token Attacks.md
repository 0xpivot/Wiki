---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 18"
---

# Web QnA - Module 18 - JWT JSON Web Token Attacks

## Architectural Overview: JWT Structure and Verification

```text
    [ HEADER ]      [ PAYLOAD ]      [ SIGNATURE ]
   eyJhbGciOi... . eyJzdWIiOi... . SflKxwRJSMeKKF2...

   +----------------+   +-------------------+  +------------------------+
   | "alg": "RS256" |   | "user_id": 1337   |  | RSA-SHA256(            |
   | "typ": "JWT"   |   | "role": "admin"   |  |   Header + "." +       |
   | "kid": "key1"  |   | "exp": 16999999   |  |   Payload,             |
   +----------------+   +-------------------+  |   Private_Key          |
                                               | )                      |
                                               +------------------------+
         |                    |                            |
    1. Defines crypto    2. Defines state/auth       3. Validates integrity
       algorithm            data (tamper target)        using Public Key
```

## Formal Technical Questions

**Q1: Explain the `alg=none` vulnerability. Why did this occur in so many JWT libraries historically?**
**A1:** 
The `alg=none` vulnerability occurs when an attacker modifies a legitimate JWT by changing the header to `{"alg": "none"}`, alters the payload to elevate privileges (e.g., changing `"role": "user"` to `"role": "admin"`), and completely strips the signature (leaving the trailing dot). 
Historically, many backend JWT libraries handled verification sequentially based on the header's instruction. The logic was roughly: `if (jwt.header.alg == "none") { verifyNone(); } else { verifySignature(); }`. Since `alg=none` was officially part of the JWT specification (intended for environments where security was handled at another layer, like mutual TLS), libraries blindly trusted the header and bypassed signature verification entirely, accepting the manipulated token as fully authenticated.

**Q2: Detail the JWT "Key Confusion" (RS256 to HS256) attack. What specific misconfiguration enables this?**
**A2:** 
JWTs support asymmetric algorithms (like RS256: private key signs, public key verifies) and symmetric algorithms (like HS256: single shared secret for both).
Key Confusion happens when the backend expects an RS256 token but dynamically switches to HS256 if the token's header specifies `{"alg": "HS256"}`. 
The vulnerability relies on the verification function: `verify(token, public_key)`.
If the attacker changes the header to HS256, the library treats the `public_key` string (which is often accessible to the attacker via a public `.well-known/jwks.json` endpoint) as the *symmetric HMAC shared secret*. 
The attacker simply creates a forged token, sets `alg: HS256`, and signs it themselves using the server's public key string as the HMAC secret. The backend logic unknowingly uses the same public key string to validate the HMAC, resulting in a successful bypass.

**Q3: What is the `kid` (Key ID) parameter in a JWT header, and what vulnerabilities arise from its mishandling?**
**A3:** 
The `kid` parameter tells the backend which specific key from its keystore to use for verifying the signature, which is useful for key rotation.
Because the server must dynamically retrieve the key based on this attacker-controllable parameter, it introduces severe vulnerabilities:
1. **Directory Traversal:** If the backend reads keys from the filesystem (e.g., `kid: "../../../dev/null"`), the attacker can force the server to use an empty file as the secret, allowing them to sign a token with an empty string.
2. **SQL Injection:** If the backend queries a database (`SELECT key FROM keys WHERE kid = '...'`), injecting SQL into the `kid` parameter can alter the returned key or execute arbitrary queries.
3. **Command Injection:** If the `kid` is passed to a shell command to fetch the key, it can lead to Remote Code Execution.

## Scenario-Based Questions

**Q4: You intercept a JWT. The `alg` is `RS256`. You find the application's public key exposed at `/api/jwks.json`. However, the backend strictly enforces RS256 and rejects `alg=none` and Key Confusion attempts. You notice the header contains a `jku` (JWK Set URL) parameter: `{"jku": "https://api.target.com/jwks.json", "alg": "RS256"}`. How do you exploit this to forge an admin token?**
**A4:** 
The `jku` parameter tells the server where to fetch the public key to verify the token. 
Since I control the token header, I will perform a JKU Injection attack:
1. I generate my own RSA key pair (Private Key + Public Key).
2. I host my Public Key in JWK format on my server: `https://evil.com/my-jwk.json`.
3. I modify the JWT header to point to my server: `{"jku": "https://evil.com/my-jwk.json", "alg": "RS256"}`.
4. I alter the JWT payload to `"role": "admin"`.
5. I sign the manipulated token with *my* Private Key.
If the backend does not enforce a strict whitelist on the domains allowed in the `jku` parameter, it will fetch my public key from `evil.com`, use it to verify the token, and accept the forged signature.

**Q5: During a web application penetration test, you receive a JWT signed with `HS256`. You do not have the source code. You suspect the shared secret might be weak. Walk me through your attack methodology.**
**A5:** 
Since `HS256` uses a symmetric secret, and the signature is simply `HMAC-SHA256(secret, header + "." + payload)`, an offline dictionary attack is highly effective against weak secrets.
1. I extract the target JWT.
2. I use a tool like `hashcat` or `john the ripper`. For hashcat, the module is 16500 (JWT).
   `hashcat -m 16500 jwt.txt rockyou.txt`
3. The tool takes the header and payload of my token, and systematically hashes them with every word in `rockyou.txt`. It compares the resulting HMAC with the signature in the intercepted JWT.
4. If a match is found, the tool outputs the plaintext secret.
5. With the secret recovered, I can use a tool like CyberChef or a local Python script to forge new JWTs with arbitrary claims (e.g., changing the user ID or expiration date) and sign them with the cracked secret.

**Q6: You are testing a hardened web application. They use RS256, don't use `jku`/`jwk`, strictly validate algorithms, and have no `kid` vulnerabilities. You steal an admin's JWT via XSS. However, when you use it from your IP address, the server rejects it. You decode the token and see: `{"user": "admin", "exp": 1790000000, "ip": "192.168.1.50"}`. How do you bypass this IP-binding restriction?**
**A6:** 
The JWT contains an IP-binding claim (`"ip"`). The backend is extracting my source IP from the network layer and comparing it against the token's payload.
Since I cannot forge the signature to change the IP inside the token, I must manipulate my perceived source IP on the network layer.
I will use HTTP request headers designed for proxies and load balancers to spoof my IP to match the victim's IP (`192.168.1.50`):
- `X-Forwarded-For: 192.168.1.50`
- `X-Real-IP: 192.168.1.50`
- `Client-IP: 192.168.1.50`
- `True-Client-IP: 192.168.1.50`
If the web server or application framework naively trusts these headers for the IP-binding check, it will believe the request is originating from the admin's legitimate IP, and the stolen token will be accepted.

## Deep-Dive Defensive Questions

**Q7: How should a developer properly configure a JWT library to completely eliminate the risk of Key Confusion and `alg=none` attacks?**
**A7:** 
Developers must shift from dynamically trusting the token's header to explicitly defining the security constraints on the backend.
1. **Algorithm Whitelisting:** When calling the `verify()` function, explicitly pass an array of allowed algorithms. `jwt.verify(token, publicKey, { algorithms: ['RS256'] })`. This forces the library to reject `alg=none` and `HS256` outright.
2. **Key Separation:** Never use the same variable or endpoint for retrieving both symmetric and asymmetric keys. The application logic should strictly provide a public key object when `RS256` is expected, which will fail if a library attempts an HMAC operation against an asymmetric key format.

**Q8: What are the severe drawbacks of using JWTs for session management, specifically regarding token revocation, and what is the architectural solution?**
**A8:** 
The fundamental nature of JWTs is that they are stateless. Once a token is signed and issued, the server does not need to look it up in a database to verify it. 
This makes **revocation nearly impossible** by default. If a user logs out, or if an attacker steals a token, that token remains perfectly valid until its mathematical expiration time (`exp` claim) is reached.
**Architectural Solutions:**
1. **Short Expirations + Refresh Tokens:** Issue JWTs with very short lifespans (e.g., 15 minutes). Issue a long-lived, stateful "Refresh Token" stored in the database. When the JWT expires, the client uses the Refresh Token to get a new JWT. To revoke access, the server simply deletes the Refresh Token from the DB. The attacker loses access within 15 minutes.
2. **Denylisting (Stateful JWTs):** Maintain a database or Redis cache of invalidated JWT IDs (`jti` claim). The server must check this cache on every request. This defeats the primary stateless advantage of JWTs but guarantees immediate revocation.

## Real-World Attack Scenario

**The Path Traversal Key Hijack**
A modern SaaS platform used JWTs for authentication. The backend supported multi-tenancy, and each tenant had their own JWT signing keys. The JWT header included a `kid` parameter to specify which tenant's key to use: `{"kid": "tenant-A-key.pem", "alg": "HS256"}`.

1. **Reconnaissance:** The attacker decoded their low-privilege JWT and noticed the `kid` parameter looked like a filename.
2. **Vulnerability Identification:** The attacker tested for path traversal by modifying the `kid` to `../../../../dev/null`.
3. **Exploitation:** The attacker changed their payload to `{"role": "SuperAdmin"}`. Because `/dev/null` is an empty file on Linux, the backend loaded an empty string as the HMAC shared secret. 
4. **Execution:** The attacker signed their manipulated JWT using an empty string as the secret (`HMAC-SHA256("", header+"."+payload)`). 
5. **Impact:** The backend processed the token, read `/dev/null`, and successfully verified the attacker's empty-string signature. The attacker achieved zero-click administrative takeover of the entire SaaS platform.

## Chaining Opportunities

- **Open Redirect -> JWT Leak:** Chaining an open redirect during an OAuth flow to steal the JWT from the URL fragment (`#access_token=eyJ...`).
- **XSS -> JWT Extraction:** If JWTs are stored in `localStorage` or `sessionStorage` instead of `HttpOnly` cookies, XSS can be used to exfiltrate the token, bypassing CSRF protections entirely.
- **SQL Injection -> JWT Forgery:** If the backend uses symmetric keys stored in a database, a blind SQL injection can be used to exfiltrate the key, leading to total offline JWT forgery.

## Related Notes
- [[04 - Session Management Vulnerabilities]]
- [[19 - OAuth and SAML Attacks]]
- [[08 - Path Traversal (Directory Traversal)]]
- [[13 - Insecure Deserialization]]
