---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.08 OWASP Cheat Sheet Series"
---

# OWASP Cheat Sheet Series Key Sheets

## 1. Introduction to the OWASP Cheat Sheet Series
The **OWASP Cheat Sheet Series** provides concise, actionable, and focused guidance on implementing secure coding practices and mitigating specific vulnerabilities. While the WSTG focuses on *testing* and SAMM focuses on *governance*, the Cheat Sheet Series is designed directly for *developers and security engineers* actively building or defending applications.

It bridges the gap between theoretical vulnerability descriptions (like the OWASP Top 10) and practical, language-agnostic implementation details.

---

## 2. Cheat Sheet Architectural Diagram

The following ASCII diagram illustrates how key cheat sheets map to different layers of an application's architecture.

```text
+-----------------------------------------------------------------------------------+
|                           Application Security Architecture                       |
|                                                                                   |
|  [ Client / Browser ]                                                             |
|   |-- DOM XSS Prevention Cheat Sheet                                              |
|   |-- HTML5 Security Cheat Sheet                                                  |
|   |-- Clickjacking Defense Cheat Sheet                                            |
|                                                                                   |
|  [ Network / Transport ]                                                          |
|   |-- Transport Layer Protection Cheat Sheet (TLS, HSTS)                          |
|   |-- CORS Origin Cheat Sheet                                                     |
|                                                                                   |
|  [ Web / API Gateway ]                                                            |
|   |-- API Security Cheat Sheet                                                    |
|   |-- Authentication Cheat Sheet                                                  |
|   |-- Session Management Cheat Sheet                                              |
|                                                                                   |
|  [ Application Logic Layer ]                                                      |
|   |-- Cross-Site Request Forgery (CSRF) Prevention Cheat Sheet                    |
|   |-- Cross-Site Scripting (XSS) Prevention Cheat Sheet                           |
|   |-- Input Validation Cheat Sheet                                                |
|   |-- Deserialization Cheat Sheet                                                 |
|                                                                                   |
|  [ Data Access / Storage Layer ]                                                  |
|   |-- SQL Injection Prevention Cheat Sheet                                        |
|   |-- Cryptographic Storage Cheat Sheet                                           |
|   |-- Password Storage Cheat Sheet                                                |
+-----------------------------------------------------------------------------------+
```

---

## 3. Deep Dive into Key Cheat Sheets

### 3.1 Authentication Cheat Sheet
Provides best practices for verifying user identity securely.
*   **Password Requirements:** Enforce complexity and length (minimum 12 characters recommended). Check passwords against known breached databases (e.g., using HaveIBeenPwned API).
*   **Multi-Factor Authentication (MFA):** Require MFA for highly privileged accounts. Prefer FIDO2/WebAuthn or TOTP over SMS-based OTPs.
*   **Brute-Force Protection:** Implement rate limiting, account lockouts, or CAPTCHAs after a threshold of failed attempts.
*   **Secure Password Recovery:** Use time-limited, single-use tokens sent via email. Do not reveal if an account exists during the recovery process.

### 3.2 Session Management Cheat Sheet
Focuses on securely handling state over HTTP.
*   **Token Generation:** Use cryptographically secure pseudorandom number generators (CSPRNG) to generate session IDs with at least 128 bits of entropy.
*   **Cookie Security Attributes:**
    *   `Secure`: Ensures cookies are only sent over HTTPS.
    *   `HttpOnly`: Prevents JavaScript from accessing the cookie (mitigates XSS token theft).
    *   `SameSite=Strict` or `Lax`: Prevents the browser from sending cookies in cross-site requests (mitigates CSRF).
*   **Session Expiration:** Implement both absolute timeout (e.g., 24 hours) and idle timeout (e.g., 15 minutes).
*   **Session Fixation Defense:** Invalidate the old session ID and generate a new one immediately after a successful login or privilege escalation.

### 3.3 Cross-Site Scripting (XSS) Prevention Cheat Sheet
Provides rules for safely rendering untrusted data in the browser.
*   **Rule 1:** Never insert untrusted data except in allowed locations.
*   **Rule 2:** HTML Entity Encode before inserting untrusted data into HTML Element content.
*   **Rule 3:** Attribute Encode before inserting untrusted data into HTML Common Attributes.
*   **Rule 4:** JavaScript Encode before inserting untrusted data into JavaScript Data Values.
*   **Rule 5:** CSS Encode before inserting untrusted data into HTML Style Property Values.
*   **Rule 6:** URL Encode before inserting untrusted data into HTML URL Parameter Values.
*   **Defense in Depth:** Implement a strict Content Security Policy (CSP) to restrict where scripts can be loaded from and prohibit inline scripting (`unsafe-inline`).

### 3.4 SQL Injection (SQLi) Prevention Cheat Sheet
Details how to prevent untrusted input from modifying SQL queries.
*   **Primary Defense:** Use Prepared Statements (Parameterized Queries). This ensures the database treats input as data, not executable code.
    ```java
    // Java JDBC Example
    String query = "SELECT account_balance FROM accounts WHERE customer_id = ?";
    PreparedStatement pstmt = connection.prepareStatement(query);
    pstmt.setString(1, custId);
    ResultSet results = pstmt.executeQuery();
    ```
*   **Secondary Defense:** Use Stored Procedures (provided they are internally parameterized).
*   **Tertiary Defense:** Allow-list input validation (e.g., validating that an input intended as an integer is actually an integer).
*   **Defense in Depth:** Enforce the Principle of Least Privilege on the database user account (e.g., the web application account cannot `DROP TABLE`).

### 3.5 Cross-Site Request Forgery (CSRF) Prevention Cheat Sheet
Prevents attackers from forcing an authenticated user to execute unwanted actions.
*   **Token-Based Mitigation:** Use the Synchronizer Token Pattern. The server generates a unique, cryptographically strong, and unpredictable token for the user's session. This token is embedded in state-changing requests (e.g., hidden form fields) and verified by the server.
*   **SameSite Cookie Attribute:** Use `SameSite=Lax` or `SameSite=Strict` to prevent the browser from appending session cookies in cross-origin POST requests.
*   **Double Submit Cookie Pattern:** Send a random value in both a cookie and as a request parameter. The server verifies they match. (Useful for stateless applications).

### 3.6 Password Storage Cheat Sheet
Guidance on securely storing user credentials.
*   **Never store plain-text passwords.**
*   **Use robust cryptographic hashing algorithms:** Argon2id is the current top recommendation. Alternatives include PBKDF2 and bcrypt.
*   **Salting:** Generate a unique, random salt (at least 16 bytes) for *each* user using a CSPRNG. Store the salt alongside the hash.
*   **Peppering (Optional but recommended):** Add a secret key (pepper) to the hashing process. The pepper is stored securely (e.g., in an HSM or KMS), separate from the database.
*   **Work Factors:** Configure the cost/iteration count of the hashing algorithm to be as high as the server hardware can handle without degrading user experience (target ~250ms to 500ms processing time per login).

### 3.7 File Upload Cheat Sheet
Mitigating risks associated with accepting files from users.
*   **Extension Validation:** Use a strict allow-list of acceptable file extensions. Never use a deny-list.
*   **Content-Type Validation:** Verify the MIME type, but do not rely on the `Content-Type` header (it can be spoofed). Use file signature (magic number) checking.
*   **Filename Sanitization:** Strip directory traversal sequences (`../`), null bytes (`%00`), and special characters from filenames. Use server-generated UUIDs for storing files instead of original filenames.
*   **Storage Location:** Store uploaded files outside the web root, ideally on a separate storage server or CDN.
*   **Execution Prevention:** Ensure the directory where files are stored does not have execute permissions, and configure the web server to serve these files with `Content-Type: application/octet-stream` or `Content-Disposition: attachment`.

---

## 4. Integration into CI/CD

The guidelines in the Cheat Sheet Series should be formalized via tools in the CI/CD pipeline:
*   **SAST Integration:** Configure Static Application Security Testing tools (like SonarQube, Semgrep) with rules derived directly from the Cheat Sheets (e.g., flag any concatenated SQL queries).
*   **Linter Rules:** Use linters (like ESLint for JS) to enforce secure coding patterns, such as requiring parameterization or prohibiting unsafe functions (e.g., `eval()`).
*   **Security Champions:** Use the cheat sheets as curriculum for training developers to become security champions within their respective teams.

---

## 5. Chaining Opportunities

Understanding secure implementations allows a penetration tester to identify nuanced bypasses:
*   **Bypassing Incomplete XSS Defenses:** If an application implements HTML Entity Encoding (Cheat Sheet Rule 2) but places the input inside a JavaScript block without JavaScript Encoding (Cheat Sheet Rule 4), an attacker can easily break out of the string context and execute code.
*   **File Upload + Directory Traversal:** If file extension validation is strong, but filename sanitization is weak, an attacker might upload a safe image file but use directory traversal (`../../../../etc/cron.d/malicious`) to overwrite system files, leading to RCE.

---

## 6. Related Notes
*   [[07 - OWASP WSTG Testing Checklist]]
*   [[03 - Injection]]
*   [[12 - Cross Site Scripting XSS]]
*   [[13 - Cross-Site Request Forgery CSRF]]
*   [[04 - Broken Access Control]]
