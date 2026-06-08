# VAPT Vault — PortSwigger Web Security Academy Complete Lab List
> Every lab from PortSwigger mapped to our vault modules.
> Difficulty: [A] Apprentice | [P] Practitioner | [E] Expert
> Status: [ ] not started | [x] done | [~] in progress

---

## 01 — SQL Injection (18 labs) → Vault MODULE 06

- [ ] [A] SQL injection vulnerability in WHERE clause allowing retrieval of hidden data
- [ ] [A] SQL injection vulnerability allowing login bypass
- [ ] [P] SQL injection attack, querying the database type and version on Oracle
- [ ] [P] SQL injection attack, querying the database type and version on MySQL and Microsoft
- [ ] [P] SQL injection attack, listing the database contents on non-Oracle databases
- [ ] [P] SQL injection attack, listing the database contents on Oracle
- [ ] [P] SQL injection UNION attack, determining the number of columns returned by the query
- [ ] [P] SQL injection UNION attack, finding a column containing text
- [ ] [P] SQL injection UNION attack, retrieving data from other tables
- [ ] [P] SQL injection UNION attack, retrieving multiple values in a single column
- [ ] [P] Blind SQL injection with conditional responses
- [ ] [P] Blind SQL injection with conditional errors
- [ ] [P] Visible error-based SQL injection
- [ ] [P] Blind SQL injection with time delays
- [ ] [P] Blind SQL injection with time delays and information retrieval
- [ ] [P] Blind SQL injection with out-of-band interaction
- [ ] [P] Blind SQL injection with out-of-band data exfiltration
- [ ] [E] SQL injection with filter bypass via XML encoding

---

## 02 — Authentication (14 labs) → Vault MODULE 16, 17

- [ ] [A] Username enumeration via different responses
- [ ] [A] 2FA simple bypass
- [ ] [A] Password reset broken logic
- [ ] [P] Username enumeration via subtly different responses
- [ ] [P] Username enumeration via response timing
- [ ] [P] Broken brute-force protection, IP block
- [ ] [P] Username enumeration via account lock
- [ ] [P] 2FA broken logic
- [ ] [P] Brute-forcing a stay-logged-in cookie
- [ ] [P] Offline password cracking
- [ ] [P] Password reset poisoning via middleware
- [ ] [P] Password brute-force via password change
- [ ] [E] Broken brute-force protection, multiple credentials per request
- [ ] [E] 2FA bypass using a brute-force attack

---

## 03 — Path Traversal (6 labs) → Vault MODULE 23

- [ ] [A] File path traversal, simple case
- [ ] [P] File path traversal, traversal sequences blocked with absolute path bypass
- [ ] [P] File path traversal, traversal sequences stripped non-recursively
- [ ] [P] File path traversal, traversal sequences stripped with superfluous URL-decode
- [ ] [P] File path traversal, validation of start of path
- [ ] [P] File path traversal, validation of file extension with null byte bypass

---

## 04 — Command Injection (5 labs) → Vault MODULE 08

- [ ] [A] OS command injection, simple case
- [ ] [P] Blind OS command injection with time delays
- [ ] [P] Blind OS command injection with output redirection
- [ ] [P] Blind OS command injection with out-of-band interaction
- [ ] [P] Blind OS command injection with out-of-band data exfiltration

---

## 05 — Business Logic Vulnerabilities (12 labs) → Vault MODULE 25

- [ ] [A] Excessive trust in client-side controls
- [ ] [A] High-level logic vulnerability
- [ ] [A] Inconsistent security controls
- [ ] [A] Flawed enforcement of business rules
- [ ] [P] Low-level logic flaw
- [ ] [P] Inconsistent handling of exceptional input
- [ ] [P] Weak isolation on dual-use endpoint
- [ ] [P] Insufficient workflow validation
- [ ] [P] Authentication bypass via flawed state machine
- [ ] [P] Infinite money logic flaw
- [ ] [E] Authentication bypass via encryption oracle
- [ ] [E] Bypassing access controls using email address parsing discrepancies

---

## 06 — Information Disclosure (5 labs) → Vault MODULE 33

- [ ] [A] Information disclosure in error messages
- [ ] [A] Information disclosure on debug page
- [ ] [A] Source code disclosure via backup files
- [ ] [A] Authentication bypass via information disclosure
- [ ] [P] Information disclosure in version control history

---

## 07 — Access Control (13 labs) → Vault MODULE 21

- [ ] [A] Unprotected admin functionality
- [ ] [A] Unprotected admin functionality with unpredictable URL
- [ ] [A] User role controlled by request parameter
- [ ] [A] User role can be modified in user profile
- [ ] [A] User ID controlled by request parameter
- [ ] [A] User ID controlled by request parameter with unpredictable user IDs
- [ ] [A] User ID controlled by request parameter with data leakage in redirect
- [ ] [A] User ID controlled by request parameter with password disclosure
- [ ] [A] Insecure direct object references
- [ ] [P] URL-based access control can be circumvented
- [ ] [P] Method-based access control can be circumvented
- [ ] [P] Multi-step process with no access control on one step
- [ ] [P] Referer-based access control

---

## 08 — File Upload Vulnerabilities (7 labs) → Vault MODULE 22

- [ ] [A] Remote code execution via web shell upload
- [ ] [A] Web shell upload via Content-Type restriction bypass
- [ ] [P] Web shell upload via path traversal
- [ ] [P] Web shell upload via extension blacklist bypass
- [ ] [P] Web shell upload via obfuscated file extension
- [ ] [E] Remote code execution via polyglot web shell upload
- [ ] [E] Web shell upload via race condition

---

## 09 — Race Conditions (6 labs) → Vault MODULE 25

- [ ] [A] Limit overrun race conditions
- [ ] [P] Bypassing rate limits via race conditions
- [ ] [P] Multi-endpoint race conditions
- [ ] [P] Single-endpoint race conditions
- [ ] [E] Exploiting time-sensitive vulnerabilities
- [ ] [E] Partial construction race conditions

---

## 10 — Server-Side Request Forgery SSRF (7 labs) → Vault MODULE 13

- [ ] [A] Basic SSRF against the local server
- [ ] [A] Basic SSRF against another back-end system
- [ ] [P] SSRF with blacklist-based input filter
- [ ] [P] SSRF with whitelist-based input filter
- [ ] [P] SSRF with filter bypass via open redirection
- [ ] [P] Blind SSRF with out-of-band detection
- [ ] [E] Blind SSRF with Shellshock exploitation

---

## 11 — XML External Entity XXE (9 labs) → Vault MODULE 14

- [ ] [A] Exploiting XXE using external entities to retrieve files
- [ ] [A] Exploiting XXE to perform SSRF attacks
- [ ] [P] Blind XXE with out-of-band interaction
- [ ] [P] Exploiting blind XXE using out-of-band interaction via XML parameter entities
- [ ] [P] Exploiting blind XXE to exfiltrate data using a malicious external DTD
- [ ] [P] Exploiting blind XXE to retrieve data via error messages
- [ ] [P] Exploiting XInclude to retrieve files
- [ ] [P] Exploiting XXE via image file upload
- [ ] [E] Exploiting XXE to retrieve data by repurposing a local DTD

---

## 12 — NoSQL Injection (4 labs) → Vault MODULE 06

- [ ] [A] Detecting NoSQL injection
- [ ] [A] Exploiting NoSQL operator injection to bypass authentication
- [ ] [P] Exploiting NoSQL injection to extract data
- [ ] [P] Exploiting NoSQL operator injection to extract unknown fields

---

## 13 — API Testing (5 labs) → Vault MODULE 31

- [ ] [A] Exploiting an API endpoint using documentation
- [ ] [A] Exploiting unused API endpoint
- [ ] [P] Finding and exploiting an unused API endpoint
- [ ] [P] Exploiting a mass assignment vulnerability
- [ ] [P] Exploiting server-side parameter pollution in a query string

---

## 14 — Web Cache Deception (5 labs) → Vault MODULE 27

- [ ] [P] Exploiting path-based cache rules
- [ ] [P] Exploiting path delimiters for web cache deception
- [ ] [P] Exploiting origin server normalization for web cache deception
- [ ] [P] Exploiting cache server normalization for web cache deception
- [ ] [E] Exploiting exact-match cache rules

---

## 15 — Web LLM Attacks (4 labs) → Vault MODULE 31 (31.25)

- [ ] [A] Exploiting LLM APIs with excessive agency
- [ ] [A] Exploiting vulnerabilities in LLM APIs
- [ ] [P] Indirect prompt injection
- [ ] [E] Exploiting insecure output handling in LLMs

---

## 16 — GraphQL API Vulnerabilities (5 labs) → Vault MODULE 30

- [ ] [A] Accessing private GraphQL posts
- [ ] [A] Accidental exposure of private GraphQL fields
- [ ] [P] Finding a hidden GraphQL endpoint
- [ ] [P] Bypassing GraphQL brute force protections
- [ ] [P] Performing CSRF exploits over GraphQL

---

## 17 — Server-Side Template Injection SSTI (7 labs) → Vault MODULE 09

- [ ] [A] Basic server-side template injection
- [ ] [A] Basic server-side template injection (code context)
- [ ] [P] Server-side template injection using documentation
- [ ] [P] Server-side template injection in an unknown language with a documented exploit
- [ ] [P] Server-side template injection with information disclosure via user-supplied objects
- [ ] [E] Server-side template injection in a sandboxed environment
- [ ] [E] Server-side template injection with a custom exploit

---

## 18 — Web Cache Poisoning (13 labs) → Vault MODULE 27

- [ ] [P] Web cache poisoning with an unkeyed header
- [ ] [P] Web cache poisoning with an unkeyed cookie
- [ ] [P] Web cache poisoning with multiple headers
- [ ] [P] Targeted web cache poisoning using an unknown header
- [ ] [P] Web cache poisoning to exploit a DOM vulnerability via a cache with strict cacheability criteria
- [ ] [P] Combining web cache poisoning vulnerabilities
- [ ] [P] Web cache poisoning via an unkeyed query string
- [ ] [P] Web cache poisoning via an unkeyed query parameter
- [ ] [P] Parameter cloaking
- [ ] [P] Web cache poisoning via a fat GET request
- [ ] [P] URL normalization
- [ ] [E] Cache key injection
- [ ] [E] Internal cache poisoning

---

## 19 — HTTP Host Header Attacks (7 labs) → Vault MODULE 03 (03.01)

- [ ] [A] Basic password reset poisoning
- [ ] [A] Host header authentication bypass
- [ ] [P] Web cache poisoning via ambiguous requests
- [ ] [P] Routing-based SSRF
- [ ] [P] SSRF via flawed request parsing
- [ ] [E] Host validation bypass via connection state attack
- [ ] [E] Password reset poisoning via dangling markup

---

## 20 — HTTP Request Smuggling (22 labs) → Vault MODULE 26

- [ ] [A] HTTP request smuggling, basic CL.TE vulnerability
- [ ] [A] HTTP request smuggling, basic TE.CL vulnerability
- [ ] [P] HTTP request smuggling, obfuscating the TE header
- [ ] [P] HTTP request smuggling, confirming a CL.TE vulnerability via differential responses
- [ ] [P] HTTP request smuggling, confirming a TE.CL vulnerability via differential responses
- [ ] [P] Exploiting HTTP request smuggling to bypass front-end security controls, CL.TE vulnerability
- [ ] [P] Exploiting HTTP request smuggling to bypass front-end security controls, TE.CL vulnerability
- [ ] [P] Exploiting HTTP request smuggling to reveal front-end request rewriting
- [ ] [P] Exploiting HTTP request smuggling to capture other users' requests
- [ ] [P] Exploiting HTTP request smuggling to deliver reflected XSS
- [ ] [P] Response queue poisoning via H2.TE request smuggling
- [ ] [P] H2.CL request smuggling
- [ ] [P] HTTP/2 request smuggling via CRLF injection
- [ ] [P] HTTP/2 request fragmentation
- [ ] [P] Bypassing access controls via HTTP/2 request tunnelling
- [ ] [P] Web cache poisoning via HTTP/2 request smuggling
- [ ] [E] Client-side desync
- [ ] [E] Browser-powered request smuggling using CL.0
- [ ] [P] Exploiting HTTP request smuggling to perform web cache poisoning
- [ ] [P] Exploiting HTTP request smuggling to perform web cache deception
- [ ] [E] Bypassing access controls via HTTP/2 request tunnelling (advanced)
- [ ] [E] Server-side pause-based request smuggling

---

## 21 — OAuth Authentication (6 labs) → Vault MODULE 19

- [ ] [A] Authentication bypass via OAuth implicit flow
- [ ] [P] Forced OAuth profile linking
- [ ] [P] OAuth account hijacking via redirect_uri
- [ ] [P] Stealing OAuth access tokens via an open redirect
- [ ] [E] SSRF via OpenID dynamic client registration
- [ ] [E] Stealing OAuth access tokens via a proxy page

---

## 22 — JWT Attacks (8 labs) → Vault MODULE 18

- [ ] [A] JWT authentication bypass via unverified signature
- [ ] [A] JWT authentication bypass via flawed signature verification
- [ ] [P] JWT authentication bypass via weak signing secret
- [ ] [P] JWT authentication bypass via jwk header injection
- [ ] [P] JWT authentication bypass via jku header injection
- [ ] [P] JWT authentication bypass via kid header path traversal
- [ ] [E] JWT authentication bypass via algorithm confusion
- [ ] [E] JWT authentication bypass via algorithm confusion with no exposed key

---

## 23 — Prototype Pollution (10 labs) → Vault MODULE 10 (10.18)

- [ ] [A] DOM XSS via client-side prototype pollution
- [ ] [A] DOM XSS via an alternative prototype pollution vector
- [ ] [P] Client-side prototype pollution via browser APIs
- [ ] [P] Client-side prototype pollution in third-party libraries
- [ ] [P] Client-side prototype pollution via flawed sanitization
- [ ] [P] Server-side prototype pollution via flawed sanitization
- [ ] [P] Detecting server-side prototype pollution without polluted property reflection
- [ ] [P] Bypassing flawed input filters for server-side prototype pollution
- [ ] [E] Remote code execution via server-side prototype pollution
- [ ] [E] Exfiltrating sensitive data via server-side prototype pollution

---

## 24 — Essential Skills (2 labs) → Vault MODULE 04

- [ ] [P] Discovering vulnerabilities quickly with targeted scanning
- [ ] [P] Scanning non-standard data structures

---

## 25 — DOM-Based Vulnerabilities (7 labs) → Vault MODULE 07

- [ ] [A] DOM XSS using web messages
- [ ] [A] DOM XSS using web messages and a JavaScript URL
- [ ] [A] DOM XSS using web messages and JSON.parse
- [ ] [A] DOM-based open redirection
- [ ] [A] DOM-based cookie manipulation
- [ ] [E] Exploiting DOM clobbering to enable XSS
- [ ] [E] Clobbering DOM attributes to bypass HTML filters

---

## 26 — Cross-Site Scripting XSS (28 labs) → Vault MODULE 07

- [ ] [A] Reflected XSS into HTML context with nothing encoded
- [ ] [A] Stored XSS into HTML context with nothing encoded
- [ ] [A] DOM XSS in document.write sink using source location.search
- [ ] [A] DOM XSS in innerHTML sink using source location.search
- [ ] [A] DOM XSS in jQuery anchor href attribute sink using location.search source
- [ ] [A] DOM XSS in jQuery selector sink using a hashchange event
- [ ] [A] Reflected XSS into attribute with angle brackets HTML-encoded
- [ ] [A] Stored XSS into anchor href attribute with double quotes HTML-encoded
- [ ] [A] Reflected XSS into a JavaScript string with angle brackets HTML encoded
- [ ] [P] DOM XSS in document.write sink using source location.search inside a select element
- [ ] [P] DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded
- [ ] [P] Reflected DOM XSS
- [ ] [P] Stored DOM XSS
- [ ] [P] Exploiting cross-site scripting to steal cookies
- [ ] [P] Exploiting cross-site scripting to capture passwords
- [ ] [P] Exploiting XSS to perform CSRF
- [ ] [P] Reflected XSS into HTML context with most tags and attributes blocked
- [ ] [P] Reflected XSS into HTML context with all tags blocked except custom ones
- [ ] [P] Reflected XSS with some SVG markup allowed
- [ ] [P] Reflected XSS in canonical link tag
- [ ] [P] Reflected XSS into a JavaScript string with single quote and backslash escaped
- [ ] [P] Reflected XSS into a JavaScript string with angle brackets and double quotes HTML-encoded and single quotes escaped
- [ ] [P] Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped
- [ ] [P] Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped
- [ ] [E] Reflected XSS with event handlers and href attributes blocked
- [ ] [E] Reflected XSS in a JavaScript URL with some characters blocked
- [ ] [E] Reflected XSS protected by very strict CSP, with dangling markup attack
- [ ] [E] Reflected XSS protected by CSP, with CSP bypass

---

## 27 — Cross-Site Request Forgery CSRF (12 labs) → Vault MODULE 11

- [ ] [A] CSRF vulnerability with no defenses
- [ ] [P] CSRF where token validation depends on request method
- [ ] [P] CSRF where token validation depends on token being present
- [ ] [P] CSRF where token is not tied to user session
- [ ] [P] CSRF where token is tied to non-session cookie
- [ ] [P] CSRF where token is duplicated in cookie
- [ ] [P] SameSite Lax bypass via method override
- [ ] [P] SameSite Strict bypass via client-side redirect
- [ ] [P] SameSite Strict bypass via sibling domain
- [ ] [P] SameSite Lax bypass via cookie refresh
- [ ] [P] CSRF where Referer validation depends on header being present
- [ ] [P] CSRF with broken Referer validation

---

## 28 — Cross-Origin Resource Sharing CORS (4 labs) → Vault MODULE 12

- [ ] [A] CORS vulnerability with basic origin reflection
- [ ] [A] CORS vulnerability with trusted null origin
- [ ] [P] CORS vulnerability with trusted insecure protocols
- [ ] [E] CORS vulnerability with internal network pivot attack

---

## 29 — Clickjacking (5 labs) → Vault MODULE 28

- [ ] [A] Basic clickjacking with CSRF token protection
- [ ] [A] Clickjacking with form input data prefilled from a URL parameter
- [ ] [A] Clickjacking with a frame buster script
- [ ] [P] Exploiting clickjacking vulnerability to trigger DOM-based XSS
- [ ] [P] Multistep clickjacking

---

## 30 — WebSockets (3 labs) → Vault MODULE 29

- [ ] [A] Manipulating WebSocket messages to exploit vulnerabilities
- [ ] [A] Cross-site WebSocket hijacking
- [ ] [P] Manipulating the WebSocket handshake to exploit vulnerabilities

---

## 31 — Insecure Deserialization (10 labs) → Vault MODULE 15

- [ ] [A] Modifying serialized objects
- [ ] [A] Modifying serialized data types
- [ ] [P] Using application functionality to exploit insecure deserialization
- [ ] [P] Arbitrary object injection in PHP
- [ ] [P] Exploiting Java deserialization with Apache Commons
- [ ] [P] Exploiting PHP deserialization with a pre-built gadget chain
- [ ] [P] Exploiting Ruby deserialization using a documented gadget chain
- [ ] [E] Developing a custom gadget chain for Java deserialization
- [ ] [E] Developing a custom gadget chain for PHP deserialization
- [ ] [E] Using PHAR deserialization to deploy a custom gadget chain

---

## Summary

| Topic | Labs | A | P | E |
|-------|------|---|---|---|
| SQL Injection | 18 | 2 | 15 | 1 |
| Authentication | 14 | 3 | 9 | 2 |
| Path Traversal | 6 | 1 | 5 | 0 |
| Command Injection | 5 | 1 | 4 | 0 |
| Business Logic | 12 | 4 | 6 | 2 |
| Information Disclosure | 5 | 4 | 1 | 0 |
| Access Control | 13 | 9 | 4 | 0 |
| File Upload | 7 | 2 | 3 | 2 |
| Race Conditions | 6 | 1 | 3 | 2 |
| SSRF | 7 | 2 | 4 | 1 |
| XXE | 9 | 2 | 6 | 1 |
| NoSQL Injection | 4 | 2 | 2 | 0 |
| API Testing | 5 | 2 | 3 | 0 |
| Web Cache Deception | 5 | 0 | 4 | 1 |
| Web LLM Attacks | 4 | 2 | 1 | 1 |
| GraphQL | 5 | 2 | 3 | 0 |
| SSTI | 7 | 2 | 3 | 2 |
| Web Cache Poisoning | 13 | 0 | 11 | 2 |
| HTTP Host Header | 7 | 2 | 3 | 2 |
| HTTP Smuggling | 22 | 2 | 16 | 4 |
| OAuth | 6 | 1 | 3 | 2 |
| JWT | 8 | 2 | 4 | 2 |
| Prototype Pollution | 10 | 2 | 6 | 2 |
| Essential Skills | 2 | 0 | 2 | 0 |
| DOM-Based | 7 | 5 | 0 | 2 |
| XSS | 28 | 9 | 13 | 6 |
| CSRF | 12 | 1 | 11 | 0 |
| CORS | 4 | 2 | 1 | 1 |
| Clickjacking | 5 | 3 | 2 | 0 |
| WebSockets | 3 | 2 | 1 | 0 |
| Insecure Deserialization | 10 | 2 | 5 | 3 |
| **TOTAL** | **278** | **82** | **154** | **42** |

---

## Recommended Learning Order (Apprentice → Expert)

### Phase 1 — Start Here (All Apprentice labs first)
1. Information Disclosure (all 5 A)
2. Access Control (all 9 A)
3. SQL Injection (2 A)
4. XSS (9 A)
5. CSRF (1 A)
6. Authentication (3 A)
7. Path Traversal (1 A)
8. Command Injection (1 A)
9. Business Logic (4 A)

### Phase 2 — Practitioner
10. SQL Injection (all remaining P)
11. Authentication (all P)
12. File Upload (all P)
13. SSRF (all P)
14. XXE (all P)
15. JWT (all P)
16. OAuth (all P)
17. XSS (all P)
18. CSRF (all P)

### Phase 3 — Advanced Practitioner
19. HTTP Request Smuggling (all P)
20. Web Cache Poisoning (all P)
21. SSTI (all P)
22. GraphQL (all P)
23. Prototype Pollution (all P)
24. Deserialization (all P)
25. Race Conditions (all P)

### Phase 4 — Expert
26. All Expert labs across all topics
27. HTTP Smuggling Expert
28. Prototype Pollution Expert (RCE)
29. Deserialization Expert (custom gadget chains)
30. XSS Expert (CSP bypass, dangling markup)

---

## Related Files
- [[VAPT-Vault-Plan]] — 776 topic build plan
- [[VAPT-Vault-Spec]] — project decisions
- [[00 - Learning Path]] — vault master index
