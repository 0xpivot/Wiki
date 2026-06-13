---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.17 Burp Extensions"
---

# Burp Extensions: Active Scan++, Autorize, JWT, and More

## 1. The Burp Extensibility Framework
While Burp Suite Professional offers a formidable array of native tools, its true power and adaptability stem from its extensibility. The Burp Extender API provides a comprehensive framework that allows security researchers and developers to create custom plugins. These extensions can hook into almost every component of the Burp ecosystem.

Extensions can intercept HTTP and WebSocket traffic before it reaches the proxy, modify UI components by adding custom tabs to messages, register bespoke active and passive scanner checks, add new payload generators to Intruder, and implement custom session handling rules. Extensions can be written in Java (natively), Python (via the Jython bridge), or Ruby (via the JRuby bridge). The BApp Store, integrated directly into the Burp UI, serves as the official repository for community-vetted extensions.

## 2. Active Scan++: Enhancing Automated Discovery
Developed by James Kettle (Director of Research at PortSwigger), Active Scan++ is universally considered a mandatory extension for any professional penetration tester. It extends Burp's native active and passive scanning engines to detect esoteric and complex vulnerabilities that standard scanners often overlook.

### 2.1 Core Capabilities
*   **Advanced Host Header Attacks:** Active Scan++ aggressively tests for vulnerabilities arising from untrusted Host header injection. It attempts to manipulate the `Host`, `X-Forwarded-Host`, `X-Original-URL`, and other routing headers to identify cache poisoning, password reset poisoning, and routing-based SSRF.
*   **XML and JSON Injection:** It improves the detection logic for vulnerabilities embedded within complex data structures, ensuring that payloads are properly formatted and escaped for the specific context (e.g., injecting SQLi payloads correctly within a JSON boolean field).
*   **Blind SSRF via Collaborator:** The extension heavily utilizes Burp Collaborator to detect out-of-band interactions, identifying instances where the application reaches out to external infrastructure based on manipulated input.
*   **Code Execution:** Detects edge-case remote code execution (RCE) scenarios, such as insecure deserialization in specific Java/.NET frameworks, or template injection in lesser-known engines.

### 2.2 Workflow Integration
Active Scan++ operates passively in the background. Once installed, it automatically registers its checks. When a user initiates an Active Scan or when traffic flows through the proxy (for passive checks), the extension's logic is seamlessly executed alongside Burp's native checks. Findings are populated in the standard Issue Activity and Target Site Map windows.

## 3. Autorize: Automating IDOR/BOLA Detection
Broken Object Level Authorization (BOLA), also known as Insecure Direct Object Reference (IDOR), is one of the most prevalent and critical API vulnerabilities. Autorize automates the tedious process of discovering these flaws.

### 3.1 The Challenge of Authorization Testing
Testing authorization manually requires a tester to log in as an administrator (User A), intercept a privileged request, extract it, modify the session token (e.g., the `Authorization: Bearer` token or `Cookie`) to that of a low-privileged user (User B), replay the request, and compare the responses. Performing this manually across hundreds of API endpoints is unscalable and prone to human error.

### 3.2 Autorize Mechanics
1.  **Context Setup:** The tester provides Autorize with the session token of a low-privileged user (User B).
2.  **Proxy Interception:** The tester navigates the application using the browser authenticated as the high-privileged user (User A).
3.  **The Triplicate Strategy:** For every request intercepted, Autorize automatically generates and sends three variations to the server in the background:
    *   **Original Request:** Sent with User A's token (Baseline).
    *   **Modified Request:** Sent with User B's token (The IDOR test).
    *   **Unauthenticated Request:** Sent with no token (Testing for completely open endpoints).
4.  **Analysis and Flagging:** Autorize compares the HTTP response codes, response lengths, and response bodies. If the modified request (User B) receives a `200 OK` and the response length matches the baseline, Autorize flags it in its dedicated tab, indicating a high probability of an authorization bypass.

## 4. JSON Web Tokens (JWT) Editor
Modern stateless APIs rely heavily on JSON Web Tokens for authentication and authorization. The JWT Editor extension provides a vital interface for inspecting, manipulating, and attacking these tokens within Burp Suite.

### 4.1 Token Inspection and Key Management
*   **Automatic Decoding:** The extension highlights JWTs in HTTP messages and provides a custom tab that automatically decodes the Base64Url format, displaying the JSON Header, Payload (claims), and Signature.
*   **Cryptographic Key Store:** Testers can generate new cryptographic keys (RSA, Elliptic Curve, HMAC, Octet), import existing public/private keys (in JWK or PEM format), and manage them within the extension's key store.

### 4.2 Exploitation Vectors Facilitated
*   **Signature Stripping (None Algorithm):** The extension allows testers to easily modify the `alg` header to `none` and remove the signature payload, testing if the backend fails to enforce signature validation.
*   **Algorithm Confusion (RS256 to HS256):** If an application uses an asymmetric algorithm (RS256) but fails to differentiate between symmetric and asymmetric verification, a tester can change the `alg` to `HS256` and sign the token using the application's *public* key as the HMAC secret. The JWT Editor streamlines this entire cryptographic attack.
*   **JWK Injection:** Testers can inject their own custom JSON Web Key into the header (`jwk` parameter) and sign the token with their private key, testing if the server blindly trusts the provided key for verification.

## 5. Param Miner: Uncovering the Hidden Surface
Param Miner, another powerful tool by James Kettle, automates the discovery of hidden, unlinked parameters and HTTP headers.

### 5.1 The Need for Parameter Discovery
Developers frequently leave debug parameters, backdoor administrative functions, or legacy inputs in production code. These are never linked in the HTML or JavaScript, making them invisible to crawlers. Furthermore, hidden HTTP headers are the primary vector for Web Cache Poisoning attacks.

### 5.2 Advanced Heuristics
Param Miner does not simply brute-force parameters; it uses intelligent heuristics.
*   **Wordlists:** It utilizes built-in, highly optimized wordlists derived from extensive internet scanning.
*   **Contextual Guessing:** It analyzes the application's responses to infer naming conventions.
*   **Cache Poisoning Detection:** It specifically hunts for unkeyed inputs (headers or parameters) that alter the application's response and get cached by intermediate CDNs or reverse proxies, leading to devastating cache poisoning vulnerabilities.

## 6. Architecture Diagram: Autorize Triplicate Flow

```ascii
+-------------------+        Original Request (Cookie: User_A_Admin)    +-------------------+
|                   |-------------------------------------------------->|                   |
|  Browser (User A) |                                                   |                   |
|                   |<--------------------------------------------------|                   |
+--------+----------+             200 OK (Returns Admin Panel Data)     |                   |
         |                                                              |                   |
         | Proxy Intercept                                              |   Target API      |
         v                                                              |   Backend         |
+--------+----------+        Modified Request (Cookie: User_B_Basic)    |                   |
|                   |-------------------------------------------------->|                   |
|  Autorize Engine  |                                                   |                   |
|  (Background Task)|<--------------------------------------------------|                   |
|                   |        200 OK (Same Data) ----> IDOR DETECTED!    |                   |
|                   |                                                   |                   |
|                   |        Unauthenticated Request (No Cookie)        |                   |
|                   |-------------------------------------------------->|                   |
|                   |<--------------------------------------------------|                   |
+-------------------+             401 Unauthorized                      +-------------------+
```

## 7. Custom Extension Development Workflow
When off-the-shelf tools fail, writing custom extensions is necessary.
1.  **Environment Setup:** Download the Jython standalone JAR and configure it in Burp's Extender options to support Python scripts.
2.  **API Implementation:** The entry point is always the `IBurpExtender` interface. From there, scripts can implement `IHttpListener` to inspect and modify traffic, `IMessageEditorTabFactory` to add custom UI tabs to the Repeater, or `IScannerCheck` to define custom vulnerability signatures.
3.  **Debugging:** Extensions run within Burp's JVM. `print()` statements in Python or `System.out.println()` in Java output to the Extender UI's dedicated output/error tabs for debugging.

## 8. Chaining Opportunities
*   **[[16 - Burp Suite Pro Complete Feature Reference]]:** Combine Param Miner with Burp Intruder. Use Param Miner to discover a hidden, unlinked parameter (e.g., `?debug_cmd=`), then send that parameter to Intruder to fuzz it for Command Injection using a comprehensive payload list.
*   **[[19 - ffuf Advanced Usage]]:** Use `ffuf` for high-speed directory brute-forcing to uncover unlinked API versions (e.g., `/api/v1/`, `/api/v2/`). Proxy the traffic of the discovered endpoints through Burp Suite, allowing Autorize to passively monitor the traffic and automatically hunt for IDOR vulnerabilities across the new API surface.

## 9. Related Notes
*   [[01 - API1 — Broken Object Level Authorization (BOLA)]] - Autorize is the single most important automated tool for identifying BOLA vulnerabilities at scale.
*   [[02 - API2 — Broken User Authentication]] - The JWT Editor extension is critical for auditing the cryptographic integrity and implementation logic of token-based authentication schemas.
*   [[05 - API5 — Broken Function Level Authorization]] - Autorize assists in finding BFLA by verifying if lower-privileged tokens can access administrative API routes discovered during testing.
