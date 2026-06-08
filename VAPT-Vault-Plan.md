# VAPT Vault — Complete Build Plan
> 1800+ topics across 60 modules. Each item = one note or one section.
> Status: [ ] not started | [x] done | [~] in progress
> PortSwigger labs: see [[VAPT-Plan2-PortSwigger]]
> Spec: [[VAPT-Vault-Spec]]

---

## PortSwigger Lab → Vault Module Map

| PortSwigger Topic | Labs | Our Module |
|---|---|---|
| SQL Injection | 18 | MODULE 06 |
| Authentication | 14 | MODULE 16, 17 |
| Path Traversal | 6 | MODULE 23 |
| Command Injection | 5 | MODULE 08 |
| Business Logic | 12 | MODULE 25 |
| Information Disclosure | 5 | MODULE 33 |
| Access Control | 13 | MODULE 21 |
| File Upload | 7 | MODULE 22 |
| Race Conditions | 6 | MODULE 25 |
| SSRF | 7 | MODULE 13 |
| XXE | 9 | MODULE 14 |
| NoSQL Injection | 4 | MODULE 06 |
| API Testing | 5 | MODULE 31 |
| Web Cache Deception | 5 | MODULE 27 |
| Web LLM Attacks | 4 | MODULE 31 |
| GraphQL | 5 | MODULE 30 |
| SSTI | 7 | MODULE 09 |
| Web Cache Poisoning | 13 | MODULE 27 |
| HTTP Host Header Attacks | 7 | MODULE 03 (03.01) |
| HTTP Request Smuggling | 22 | MODULE 26 |
| OAuth | 6 | MODULE 19 |
| JWT | 8 | MODULE 18 |
| Prototype Pollution | 10 | MODULE 10 |
| Essential Skills | 2 | MODULE 04 |
| DOM-Based Vulnerabilities | 7 | MODULE 07 |
| XSS | 28 | MODULE 07 |
| CSRF | 12 | MODULE 11 |
| CORS | 4 | MODULE 12 |
| Clickjacking | 5 | MODULE 28 |
| WebSockets | 3 | MODULE 29 |
| Insecure Deserialization | 10 | MODULE 15 |
| **Total PortSwigger Labs** | **278** | |

---

## MODULE 01 — Networking Foundations (22)

- [x] 01.01 What is a Network?
- [x] 01.02 IP Addresses (IPv4 and IPv6)
- [x] 01.03 MAC Addresses
- [x] 01.04 Subnets and CIDR Notation
- [x] 01.05 Ports and Protocols
- [x] 01.06 TCP — Three-Way Handshake
- [x] 01.07 UDP — Connectionless Communication
- [x] 01.08 DNS — How Domain Names Resolve
- [x] 01.09 DNS Record Types (A, AAAA, CNAME, MX, TXT, NS, PTR, SOA)
- [x] 01.10 ARP — Address Resolution Protocol
- [x] 01.11 NAT and Private IP Ranges
- [x] 01.12 Firewalls — How They Work
- [x] 01.13 Proxies — Forward and Reverse
- [x] 01.14 Load Balancers
- [x] 01.15 CDNs — Content Delivery Networks
- [x] 01.16 VPNs — How They Tunnel Traffic
- [x] 01.17 TLS/SSL — How HTTPS Works
- [x] 01.18 Certificates and Certificate Authorities (CA)
- [x] 01.19 OSI Model — 7 Layers
- [x] 01.20 TCP/IP Model
- [x] 01.21 Packet Structure — Reading Raw Traffic
- [x] 01.22 Wireshark Basics — Capturing and Analyzing Traffic

---

## MODULE 02 — HTTP Protocol Deep Dive (28)

- [x] 02.01 What is HTTP?
- [x] 02.02 HTTP vs HTTPS
- [x] 02.03 HTTP Versions (1.0, 1.1, 2, 3)
- [x] 02.04 HTTP Request Structure (Method, URL, Headers, Body)
- [x] 02.05 HTTP Response Structure (Status Code, Headers, Body)
- [x] 02.06 HTTP Methods — GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, TRACE, CONNECT
- [x] 02.07 HTTP Status Codes — Full Reference (1xx, 2xx, 3xx, 4xx, 5xx)
- [x] 02.08 URLs — Anatomy (scheme, host, port, path, query, fragment)
- [x] 02.09 Query Strings and Parameters
- [x] 02.10 URL Encoding and Percent Encoding
- [x] 02.11 Cookies — Structure, Flags, Lifecycle
- [x] 02.12 Sessions — How Server-Side Sessions Work
- [x] 02.13 HTTP Authentication Schemes (Basic, Bearer, Digest, NTLM)
- [x] 02.14 MIME Types and Content-Type
- [x] 02.15 Transfer-Encoding (chunked, gzip, deflate, br)
- [x] 02.16 HTTP Caching (Cache-Control, ETag, If-Modified-Since)
- [x] 02.17 HTTP Redirects (301, 302, 307, 308)
- [x] 02.18 HTTP Pipelining
- [x] 02.19 HTTP Keep-Alive and Connection Reuse
- [x] 02.20 HTTP/2 — Multiplexing, HPACK, Server Push
- [x] 02.21 HTTP/3 and QUIC
- [x] 02.22 WebSockets — Upgrade Handshake
- [x] 02.23 REST API Architecture
- [x] 02.24 GraphQL — How It Differs from REST
- [x] 02.25 SOAP and WSDL
- [x] 02.26 gRPC and Protocol Buffers
- [x] 02.27 JSON and XML Structure
- [x] 02.28 Same-Origin Policy (SOP)

---

## MODULE 03 — HTTP Headers: Security Context (65)

### Request Headers — Attackable / Abusable
- [x] 03.01 Host — virtual hosting, password reset poisoning, SSRF, cache poisoning *(PS: HTTP Host header attacks — 7 labs)*
- [x] 03.02 X-Forwarded-For — IP spoofing, rate limit bypass
- [x] 03.03 X-Forwarded-Host — SSRF, cache poisoning
- [x] 03.04 X-Forwarded-Proto — HTTP downgrade
- [x] 03.05 X-Real-IP — IP bypass
- [x] 03.06 X-Original-URL — URL override, access control bypass
- [x] 03.07 X-Rewrite-URL — URL override
- [x] 03.08 X-Custom-IP-Authorization — WAF/access bypass
- [x] 03.09 X-Remote-IP / X-Remote-Addr — IP spoofing
- [x] 03.10 True-Client-IP — Cloudflare IP bypass
- [x] 03.11 CF-Connecting-IP — Cloudflare header abuse
- [x] 03.12 Forwarded — RFC 7239, abuse patterns
- [x] 03.13 Via — proxy chain disclosure
- [x] 03.14 User-Agent — fingerprinting, WAF bypass
- [x] 03.15 Referer — info leakage, CSRF bypass, token leakage
- [x] 03.16 Origin — CORS bypass
- [x] 03.17 Cookie — session hijacking, flag abuse
- [x] 03.18 Authorization — Bearer abuse, Basic cracking
- [x] 03.19 Content-Type — type confusion, JSON/XML switching
- [x] 03.20 Transfer-Encoding — HTTP smuggling *(PS: HTTP request smuggling — 22 labs)*
- [x] 03.21 Content-Length — smuggling, desync
- [x] 03.22 X-HTTP-Method-Override — method tunneling, WAF bypass
- [x] 03.23 X-Method-Override — method tunneling
- [x] 03.24 _method (POST body) — REST method override
- [x] 03.25 SOAPAction — SOAP injection
- [x] 03.26 Range — partial content, DoS
- [x] 03.27 If-Modified-Since / If-None-Match — cache bypass
- [x] 03.28 Upgrade — WebSocket hijacking
- [x] 03.29 Connection — hop-by-hop abuse
- [x] 03.30 TE (chunked) — HTTP/2 downgrade smuggling
- [x] 03.31 Accept — content negotiation, MIME sniffing
- [x] 03.32 Accept-Encoding — BREACH attack
- [x] 03.33 X-Requested-With — CSRF bypass in AJAX

### Response Headers — Security Controls
- [x] 03.34 Content-Security-Policy (CSP) — directives, bypasses *(PS: XSS Expert labs)*
- [x] 03.35 X-Content-Type-Options: nosniff — MIME sniffing prevention
- [x] 03.36 X-Frame-Options — clickjacking *(PS: Clickjacking — 5 labs)*
- [x] 03.37 Strict-Transport-Security (HSTS) — HTTPS enforcement
- [x] 03.38 Referrer-Policy — leakage control
- [x] 03.39 Permissions-Policy — browser feature control
- [x] 03.40 X-XSS-Protection — legacy, abusable
- [x] 03.41 Access-Control-Allow-Origin — CORS *(PS: CORS — 4 labs)*
- [x] 03.42 Access-Control-Allow-Credentials — credential CORS risk
- [x] 03.43 Access-Control-Allow-Methods — CORS method control
- [x] 03.44 Access-Control-Allow-Headers — CORS header whitelist
- [x] 03.45 Access-Control-Expose-Headers — response leakage
- [x] 03.46 Access-Control-Max-Age — preflight caching
- [x] 03.47 Set-Cookie flags — HttpOnly, Secure, SameSite, Path, Domain
- [x] 03.48 Cache-Control — sensitive data caching
- [x] 03.49 Pragma: no-cache — legacy cache control
- [x] 03.50 Expires — caching behavior
- [x] 03.51 Content-Disposition — filename injection, download vs inline
- [x] 03.52 X-Powered-By — tech fingerprinting, remove it
- [x] 03.53 Server — version disclosure, remove it
- [x] 03.54 X-AspNet-Version / X-AspNetMvc-Version — framework disclosure
- [x] 03.55 WWW-Authenticate — auth challenge
- [x] 03.56 Clear-Site-Data — logout clearing
- [x] 03.57 Cross-Origin-Embedder-Policy (COEP)
- [x] 03.58 Cross-Origin-Opener-Policy (COOP)
- [x] 03.59 Cross-Origin-Resource-Policy (CORP)
- [x] 03.60 Expect-CT — certificate transparency
- [x] 03.61 Content-Encoding — compression disclosure
- [x] 03.62 Location — open redirect
- [x] 03.63 Retry-After — rate limit bypass timing
- [x] 03.64 Subresource Integrity (SRI) — integrity attribute
- [x] 03.65 Public-Key-Pins (HPKP) — deprecated, history

---

## MODULE 04 — VAPT Methodology (12) *(PS: Essential Skills — 2 labs)*

- [x] 04.01 VAPT vs Penetration Testing vs Red Team
- [x] 04.02 Rules of Engagement (RoE) and Scope
- [x] 04.03 Reconnaissance Phase
- [x] 04.04 Scanning and Enumeration Phase
- [x] 04.05 Vulnerability Identification Phase
- [x] 04.06 Exploitation Phase
- [x] 04.07 Post-Exploitation Phase
- [x] 04.08 Reporting Phase
- [x] 04.09 Black Box vs Grey Box vs White Box
- [x] 04.10 Bug Bounty vs Pentest Engagement
- [x] 04.11 OWASP Testing Guide Overview
- [x] 04.12 Legal and Ethical Considerations

---

## MODULE 05 — Reconnaissance (30)

- [x] 05.01 Passive vs Active Recon
- [x] 05.02 OSINT — Open Source Intelligence
- [x] 05.03 Google Dorking
- [x] 05.04 Shodan — IoT and exposed services
- [x] 05.05 Censys — certificate and host enumeration
- [x] 05.06 WHOIS and Domain Lookup
- [x] 05.07 DNS Enumeration (dig, nslookup, dnsx)
- [x] 05.08 Subdomain Enumeration (amass, subfinder, assetfinder)
- [x] 05.09 Certificate Transparency Logs (crt.sh)
- [x] 05.10 Web Archive — Wayback Machine for hidden endpoints
- [x] 05.11 GitHub Dorking for secrets
- [x] 05.12 LinkedIn and Employee OSINT
- [x] 05.13 Email Harvesting (theHarvester)
- [x] 05.14 Technology Fingerprinting (Wappalyzer, WhatWeb)
- [x] 05.15 robots.txt and sitemap.xml
- [x] 05.16 .well-known directory
- [x] 05.17 JavaScript File Analysis for endpoints and secrets
- [x] 05.18 API Discovery from JS files (LinkFinder, JSParser)
- [x] 05.19 Source Code Leakage (.git, .svn, .env exposed)
- [x] 05.20 Cloud Storage Enumeration (S3, Azure Blob, GCP)
- [x] 05.21 Port Scanning with Nmap
- [x] 05.22 Banner Grabbing
- [x] 05.23 Service Version Detection
- [x] 05.24 OS Fingerprinting
- [x] 05.25 WAF Detection (wafw00f)
- [x] 05.26 CDN Detection and Origin IP Discovery
- [x] 05.27 ASN and IP Range Discovery
- [x] 05.28 Virtual Host (vHost) Enumeration
- [x] 05.29 Directory and File Bruteforcing (ffuf, gobuster, feroxbuster)
- [x] 05.30 Parameter Discovery (Arjun, x8)

---

## MODULE 06 — SQL Injection (25) *(PS: 18 SQLi + 4 NoSQL = 22 labs)*

- [x] 06.01 What is SQL Injection?
- [x] 06.02 How Databases Work (SELECT, INSERT, UPDATE, DELETE)
- [x] 06.03 Error-Based SQLi
- [x] 06.04 Union-Based SQLi
- [x] 06.05 Blind SQLi — Boolean-Based
- [x] 06.06 Blind SQLi — Time-Based
- [x] 06.07 Out-of-Band SQLi (DNS exfiltration)
- [x] 06.08 Second-Order SQLi (Stored SQLi)
- [x] 06.09 SQLi in GET Parameters
- [x] 06.10 SQLi in POST Body (JSON, form data)
- [x] 06.11 SQLi in HTTP Headers (User-Agent, Cookie, Referer, X-Forwarded-For)
- [x] 06.12 SQLi in JSON APIs
- [x] 06.13 SQLi in ORDER BY / GROUP BY
- [x] 06.14 SQLi WAF Bypass Techniques
- [x] 06.15 MySQL Specific Payloads
- [x] 06.16 PostgreSQL Specific Payloads
- [x] 06.17 MSSQL Specific Payloads (xp_cmdshell, stacked queries)
- [x] 06.18 Oracle Specific Payloads
- [x] 06.19 SQLite Specific Payloads
- [x] 06.20 NoSQL Injection (MongoDB, CouchDB)
- [x] 06.21 sqlmap — Full Usage Guide
- [x] 06.22 Manual SQLi Testing Methodology
- [x] 06.23 Extracting Schema, Tables, Columns
- [x] 06.24 Reading Files via SQLi (LOAD_FILE)
- [x] 06.25 Writing Files / Webshells via SQLi (INTO OUTFILE)

---

## MODULE 07 — XSS (22) *(PS: 28 XSS + 7 DOM-based = 35 labs)*

- [x] 07.01 What is XSS and Why It Matters
- [x] 07.02 Reflected XSS
- [x] 07.03 Stored XSS (Persistent XSS)
- [x] 07.04 DOM-Based XSS
- [x] 07.05 Blind XSS
- [x] 07.06 Self-XSS and Social Engineering
- [x] 07.07 XSS in HTML Attributes
- [x] 07.08 XSS in JavaScript Context
- [x] 07.09 XSS in CSS Context
- [x] 07.10 XSS in URL/href Context
- [x] 07.11 XSS in JSON Response (without Content-Type)
- [x] 07.12 XSS in SVG, XML, and HTML5
- [x] 07.13 XSS via HTTP Response Splitting
- [x] 07.14 XSS Filter Bypass Techniques
- [x] 07.15 CSP Bypass for XSS
- [x] 07.16 XSS to Session Hijacking
- [x] 07.17 XSS to Account Takeover
- [x] 07.18 XSS to CSRF
- [x] 07.19 XSS to Keylogging
- [x] 07.20 XSS to Port Scanning (internal via browser)
- [x] 07.21 XSS Payloads — Comprehensive List
- [x] 07.22 XSS Tools (XSStrike, dalfox, Burp Scanner)

---

## MODULE 08 — Command Injection (12) *(PS: 5 labs)*

- [x] 08.01 What is Command Injection?
- [x] 08.02 OS Command Injection — Linux
- [x] 08.03 OS Command Injection — Windows
- [x] 08.04 Blind Command Injection (time-based, out-of-band)
- [x] 08.05 Command Injection via Filename
- [x] 08.06 Command Injection via HTTP Headers
- [x] 08.07 Command Injection in API Parameters
- [x] 08.08 Chaining Operators (; && || | \n)
- [x] 08.09 WAF Bypass for Command Injection
- [x] 08.10 Command Injection to Reverse Shell
- [x] 08.11 Reverse Shell Payloads (bash, Python, PHP, PowerShell, nc)
- [x] 08.12 Defense — Input Sanitization and Allowlists

---

## MODULE 09 — SSTI (10) *(PS: 7 labs)*

- [x] 09.01 What is SSTI?
- [x] 09.02 Template Engines (Jinja2, Twig, Freemarker, Pebble, Velocity, Handlebars, ERB, Smarty)
- [x] 09.03 Detecting SSTI (polyglot payloads)
- [x] 09.04 SSTI in Jinja2 (Python/Flask)
- [x] 09.05 SSTI in Twig (PHP)
- [x] 09.06 SSTI in Freemarker (Java)
- [x] 09.07 SSTI in ERB (Ruby)
- [x] 09.08 SSTI to RCE Escalation
- [x] 09.09 SSTI WAF Bypass
- [x] 09.10 SSTImap Tool Usage

---

## MODULE 10 — Other Injections (18) *(PS: 10 Prototype Pollution labs)*

- [x] 10.01 LDAP Injection
- [x] 10.02 XPath Injection
- [x] 10.03 XML Injection
- [x] 10.04 HTML Injection
- [x] 10.05 CSS Injection
- [x] 10.06 Email Header Injection (SMTP Injection)
- [x] 10.07 HTTP Header Injection
- [x] 10.08 Log Injection
- [x] 10.09 CRLF Injection (\r\n)
- [x] 10.10 Formula Injection (CSV Injection)
- [x] 10.11 SSI Injection (Server-Side Includes)
- [x] 10.12 XQuery Injection
- [x] 10.13 GraphQL Injection
- [x] 10.14 Regex Injection (ReDoS)
- [x] 10.15 gRPC Injection
- [x] 10.16 PDF Injection
- [x] 10.17 LaTeX Injection
- [x] 10.18 Prototype Pollution (JavaScript)

---

## MODULE 11 — CSRF (10) *(PS: 12 labs)*

- [ ] 11.01 What is CSRF?
- [ ] 11.02 Same-Origin Policy and CSRF
- [ ] 11.03 CSRF via GET Request
- [ ] 11.04 CSRF via POST Request
- [ ] 11.05 CSRF Token Bypass Techniques
- [ ] 11.06 SameSite Cookie Bypass
- [ ] 11.07 CSRF via CORS Misconfiguration
- [ ] 11.08 CSRF via JSON (Content-Type tricks)
- [ ] 11.09 CSRF to Account Takeover
- [ ] 11.10 Defense — tokens, SameSite, double-submit cookie

---

## MODULE 12 — CORS (12) *(PS: 4 labs)*

- [ ] 12.01 What is CORS and Why It Exists
- [ ] 12.02 Simple vs Preflight Requests
- [ ] 12.03 CORS Headers — Full Reference
- [ ] 12.04 Origin Reflection Misconfiguration
- [ ] 12.05 Null Origin Misconfiguration
- [ ] 12.06 Wildcard with Credentials
- [ ] 12.07 Subdomain Trust
- [ ] 12.08 Regex Bypass (evil.com matching .com)
- [ ] 12.09 CORS to Credential Theft
- [ ] 12.10 CORS to Account Takeover Chain
- [ ] 12.11 Detecting CORS Misconfigurations (CORScanner, manual)
- [ ] 12.12 Defense — Strict Origin Whitelisting

---

## MODULE 13 — SSRF (20) *(PS: 7 labs)*

- [ ] 13.01 What is SSRF?
- [ ] 13.02 Basic SSRF — Fetching Internal URLs
- [ ] 13.03 SSRF via URL Parameters
- [ ] 13.04 SSRF via HTTP Headers (Host, Referer, X-Forwarded-For)
- [ ] 13.05 SSRF via File Imports (PDF, webhooks, image fetchers)
- [ ] 13.06 SSRF via XML (XXE chained)
- [ ] 13.07 Blind SSRF (Burp Collaborator / interactsh)
- [ ] 13.08 Semi-Blind SSRF (timing-based)
- [ ] 13.09 SSRF — Cloud Metadata (AWS 169.254.169.254, GCP, Azure)
- [ ] 13.10 SSRF — AWS IMDSv1 vs IMDSv2
- [ ] 13.11 SSRF — Internal Port Scanning
- [ ] 13.12 SSRF — Internal Services (Redis, Elasticsearch, Memcached)
- [ ] 13.13 SSRF — Protocol Smuggling (file://, gopher://, dict://, ftp://)
- [ ] 13.14 SSRF — Localhost Bypass (127.0.0.1, [::1], 0.0.0.0, 2130706433)
- [ ] 13.15 SSRF — DNS Rebinding
- [ ] 13.16 SSRF — URL Parser Confusion
- [ ] 13.17 SSRF WAF Bypass
- [ ] 13.18 SSRF to RCE via Internal Services
- [ ] 13.19 SSRF to Cloud Credential Theft → Full Takeover
- [ ] 13.20 Defense — Allowlists, IMDSv2, Network Segmentation

---

## MODULE 14 — XXE (10) *(PS: 9 labs)*

- [ ] 14.01 What is XXE?
- [ ] 14.02 XML Basics and DTD
- [ ] 14.03 Classic XXE — File Read (/etc/passwd)
- [ ] 14.04 XXE via SVG Upload
- [ ] 14.05 XXE via XLSX / DOCX
- [ ] 14.06 Blind XXE — OOB Data Exfiltration
- [ ] 14.07 XXE via XInclude
- [ ] 14.08 XXE to SSRF
- [ ] 14.09 XXE WAF Bypass (encoding, whitespace)
- [ ] 14.10 Defense — Disable External Entity Processing

---

## MODULE 15 — Insecure Deserialization (12) *(PS: 10 labs)*

- [ ] 15.01 What is Serialization and Deserialization?
- [ ] 15.02 Java Deserialization (ysoserial)
- [ ] 15.03 PHP Object Injection
- [ ] 15.04 Python Pickle Deserialization
- [ ] 15.05 .NET Deserialization (BinaryFormatter, ViewState)
- [ ] 15.06 Ruby Deserialization
- [ ] 15.07 Node.js Deserialization (node-serialize)
- [ ] 15.08 JSON Deserialization Type Confusion
- [ ] 15.09 YAML Deserialization
- [ ] 15.10 XML Deserialization
- [ ] 15.11 Magic Methods Abuse (__wakeup, __destruct, readObject)
- [ ] 15.12 Defense — Avoid Untrusted Deserialization, Use Safe Formats

---

## MODULE 16 — Authentication Attacks (28) *(PS: 14 labs)*

- [ ] 16.01 Username Enumeration (error messages, timing)
- [ ] 16.02 Password Brute Force
- [ ] 16.03 Credential Stuffing
- [ ] 16.04 Password Spraying
- [ ] 16.05 Default Credentials
- [ ] 16.06 Weak Password Policies
- [ ] 16.07 Forgot Password — Token Predictability
- [ ] 16.08 Forgot Password — Host Header Poisoning
- [ ] 16.09 Forgot Password — Token Reuse
- [ ] 16.10 Account Lockout Bypass
- [ ] 16.11 MFA Bypass — Response Manipulation
- [ ] 16.12 MFA Bypass — Code Reuse
- [ ] 16.13 MFA Bypass — Brute Force OTP
- [ ] 16.14 MFA Bypass — Backup Code Abuse
- [ ] 16.15 MFA Bypass — SIM Swapping
- [ ] 16.16 Login CSRF
- [ ] 16.17 Basic Auth Cracking
- [ ] 16.18 HTTP Digest Auth Attacks
- [ ] 16.19 NTLM Authentication Attacks
- [ ] 16.20 OAuth Login CSRF
- [ ] 16.21 Magic Link Vulnerabilities
- [ ] 16.22 SSO Bypass (SAML, OAuth)
- [ ] 16.23 Pre-Authentication SQLi
- [ ] 16.24 Username/Password in URL
- [ ] 16.25 Autocomplete on Sensitive Fields
- [ ] 16.26 Verbose Error Messages
- [ ] 16.27 Client-Side Auth Bypass (JavaScript checks)
- [ ] 16.28 Defense — Rate Limiting, Lockout, MFA, Secure Password Storage

---

## MODULE 17 — Session Management (15) *(PS: Authentication labs)*

- [ ] 17.01 What is a Session?
- [ ] 17.02 Session Token Entropy and Predictability
- [ ] 17.03 Session Fixation
- [ ] 17.04 Session Hijacking via Cookie Theft (XSS)
- [ ] 17.05 Session Hijacking via Network Sniffing
- [ ] 17.06 Session Puzzle / Session Confusion
- [ ] 17.07 Insecure Session Storage (localStorage, URL params)
- [ ] 17.08 Session Not Invalidated on Logout
- [ ] 17.09 Long-Lived Sessions
- [ ] 17.10 Concurrent Session Not Invalidated
- [ ] 17.11 Cookie Flags — Attack Scenarios
- [ ] 17.12 Cookie Scope Abuse (Domain and Path)
- [ ] 17.13 Cookie Tossing
- [ ] 17.14 Client-Side Session Tokens (JWT, Signed Cookies)
- [ ] 17.15 Defense — Secure Session Configuration

---

## MODULE 18 — JWT Attacks (18) *(PS: 8 labs)*

- [ ] 18.01 What is a JWT?
- [ ] 18.02 JWT Structure (Header.Payload.Signature)
- [ ] 18.03 JWT Claims Reference (iss, sub, aud, exp, nbf, iat, jti)
- [ ] 18.04 Algorithm None Attack
- [ ] 18.05 RS256 to HS256 Algorithm Confusion
- [ ] 18.06 Weak Secret Brute Force (hashcat, jwt_tool)
- [ ] 18.07 JWT Header Injection — jwk claim
- [ ] 18.08 JWT Header Injection — jku claim
- [ ] 18.09 JWT Header Injection — kid claim (SQLi, path traversal)
- [ ] 18.10 JWT Expiry Manipulation (exp claim)
- [ ] 18.11 JWT Replay Attack
- [ ] 18.12 JWT Substitution Attack (swapping tokens between users)
- [ ] 18.13 JWT in Cookies vs Authorization Header
- [ ] 18.14 JWT Cracking with jwt_tool
- [ ] 18.15 JWT Cracking with hashcat
- [ ] 18.16 Refresh Token Attacks
- [ ] 18.17 JWT Confusion in Multi-Tenant Apps
- [ ] 18.18 Defense — Strong Algorithms, Validation, Short Expiry

---

## MODULE 19 — OAuth 2.0 Attacks (20) *(PS: 6 labs)*

- [ ] 19.01 OAuth 2.0 Overview and Flow Types
- [ ] 19.02 Authorization Code Flow — Step by Step
- [ ] 19.03 Implicit Flow (deprecated) — Vulnerabilities
- [ ] 19.04 Client Credentials Flow
- [ ] 19.05 PKCE — What It Protects Against
- [ ] 19.06 OAuth State Parameter — CSRF in OAuth
- [ ] 19.07 Redirect URI Manipulation
- [ ] 19.08 Open Redirect in Redirect URI
- [ ] 19.09 Authorization Code Interception
- [ ] 19.10 Token Leakage via Referer Header
- [ ] 19.11 Token Leakage via Browser History
- [ ] 19.12 Account Linking Abuse
- [ ] 19.13 Scope Escalation
- [ ] 19.14 Token Replay Attack
- [ ] 19.15 Client Secret Exposure
- [ ] 19.16 OAuth Misconfig — Wildcard Redirect URI
- [ ] 19.17 OAuth Misconfig — Lack of State Validation
- [ ] 19.18 OAuth to Account Takeover Chain
- [ ] 19.19 OpenID Connect (OIDC) Attack Surface
- [ ] 19.20 Defense — Strict Redirect URI, PKCE, State Validation

---

## MODULE 20 — SAML Attacks (10)

- [ ] 20.01 What is SAML and How SSO Works
- [ ] 20.02 SAML Assertion Structure
- [ ] 20.03 XML Signature Wrapping (XSW) Attacks
- [ ] 20.04 SAML Replay Attack
- [ ] 20.05 SAML Attribute Manipulation
- [ ] 20.06 SAML Comment Injection
- [ ] 20.07 SAML External Entity (SAML + XXE)
- [ ] 20.08 SAML Signature Bypass (none algorithm)
- [ ] 20.09 SAML to Account Takeover
- [ ] 20.10 Defense — Strict Schema Validation, Signed Assertions

---

## MODULE 21 — Access Control (20) *(PS: 13 labs)*

- [ ] 21.01 Vertical Privilege Escalation
- [ ] 21.02 Horizontal Privilege Escalation
- [ ] 21.03 IDOR — Insecure Direct Object Reference
- [ ] 21.04 IDOR in URL Parameters
- [ ] 21.05 IDOR in POST Body
- [ ] 21.06 IDOR in Cookies
- [ ] 21.07 IDOR in HTTP Headers
- [ ] 21.08 Mass Assignment Vulnerability
- [ ] 21.09 BOLA — Broken Object Level Authorization (OWASP API #1)
- [ ] 21.10 BFLA — Broken Function Level Authorization (OWASP API #5)
- [ ] 21.11 Forced Browsing / Unprotected Admin Endpoints
- [ ] 21.12 Parameter Tampering (role=admin, isAdmin=true)
- [ ] 21.13 HTTP Method Bypass (GET vs POST vs PUT)
- [ ] 21.14 Path Traversal to Bypass Access Controls
- [ ] 21.15 IDOR via API Versioning
- [ ] 21.16 GraphQL Authorization Bypass
- [ ] 21.17 JWT Claim Manipulation for Privilege Escalation
- [ ] 21.18 Account Takeover via IDOR on Password Reset
- [ ] 21.19 Referrer-Based Access Control Bypass
- [ ] 21.20 Defense — Server-Side Authorization, Object-Level Checks

---

## MODULE 22 — File Upload (15) *(PS: 7 labs)*

- [ ] 22.01 What Makes File Upload Dangerous
- [ ] 22.02 Unrestricted File Upload — Webshell Upload
- [ ] 22.03 Content-Type Bypass
- [ ] 22.04 Extension Bypass (.php5, .phtml, .phar, .shtml)
- [ ] 22.05 Double Extension (file.php.jpg)
- [ ] 22.06 Null Byte Injection (file.php%00.jpg)
- [ ] 22.07 File Upload + Path Traversal
- [ ] 22.08 File Upload + SSRF (SVG with SSRF payload)
- [ ] 22.09 File Upload + XSS (SVG with XSS payload)
- [ ] 22.10 File Upload + XXE (malicious DOCX/XLSX)
- [ ] 22.11 ZIP Slip (malicious ZIP with path traversal)
- [ ] 22.12 Image Upload Magic Bytes Bypass
- [ ] 22.13 Uploading Server-Side Scripts (JSP, ASP, ASPX)
- [ ] 22.14 Overwriting Existing Files
- [ ] 22.15 Defense — Extension Allowlists, Content Validation, Separate Storage

---

## MODULE 23 — Path Traversal and LFI/RFI (12) *(PS: 6 labs)*

- [ ] 23.01 What is Path Traversal?
- [ ] 23.02 Basic Path Traversal (../../../etc/passwd)
- [ ] 23.03 Encoding Bypass for Path Traversal
- [ ] 23.04 Null Byte Path Traversal
- [ ] 23.05 Local File Inclusion (LFI)
- [ ] 23.06 LFI via PHP Wrappers (php://filter, php://input, data://)
- [ ] 23.07 LFI to RCE via Log Poisoning
- [ ] 23.08 LFI to RCE via /proc/self/environ
- [ ] 23.09 LFI to RCE via PHP Session File
- [ ] 23.10 Remote File Inclusion (RFI)
- [ ] 23.11 Path Traversal in API Parameters
- [ ] 23.12 Defense — Canonicalization, Allowlists, Chroot

---

## MODULE 24 — Open Redirect (8)

- [ ] 24.01 What is Open Redirect?
- [ ] 24.02 Open Redirect in redirect= and url= Parameters
- [ ] 24.03 Bypass Techniques (//evil.com, /\evil.com, ///evil.com)
- [ ] 24.04 Open Redirect via Referer Header
- [ ] 24.05 Open Redirect to Phishing
- [ ] 24.06 Open Redirect + OAuth (token stealing)
- [ ] 24.07 Open Redirect + SSRF (chained)
- [ ] 24.08 Defense — Allowlist of Redirect Destinations

---

## MODULE 25 — Business Logic (18) *(PS: 12 Business Logic + 6 Race Conditions = 18 labs)*

- [ ] 25.01 What are Business Logic Flaws?
- [ ] 25.02 Price Manipulation in E-commerce
- [ ] 25.03 Quantity Manipulation (negative quantities)
- [ ] 25.04 Discount/Coupon Abuse
- [ ] 25.05 Free Trial Abuse
- [ ] 25.06 Account Limit Bypass
- [ ] 25.07 Workflow Bypass (skipping payment step)
- [ ] 25.08 Order Manipulation After Checkout
- [ ] 25.09 Race Conditions in Financial Transactions
- [ ] 25.10 Double Submit / Double Spend
- [ ] 25.11 Referral Abuse / Self-Referral
- [ ] 25.12 Rate Limit Bypass for Votes / Likes
- [ ] 25.13 Function-Level Access Control Bypass
- [ ] 25.14 Exploiting Trust Between Microservices
- [ ] 25.15 Hidden API Parameters
- [ ] 25.16 Email Verification Bypass
- [ ] 25.17 Phone Number Verification Bypass
- [ ] 25.18 Defense — State Machine Validation, Server-Side Checks

---

## MODULE 26 — HTTP Request Smuggling (12) *(PS: 22 labs)*

- [ ] 26.01 What is HTTP Request Smuggling?
- [ ] 26.02 CL.TE Smuggling
- [ ] 26.03 TE.CL Smuggling
- [ ] 26.04 TE.TE Smuggling (obfuscated TE headers)
- [ ] 26.05 HTTP/2 Request Smuggling (H2.CL, H2.TE)
- [ ] 26.06 Response Queue Poisoning
- [ ] 26.07 Smuggling to Bypass Front-End Controls
- [ ] 26.08 Smuggling to Capture Other Users' Requests
- [ ] 26.09 Smuggling to Deliver XSS
- [ ] 26.10 Smuggling to Escalate SSRF
- [ ] 26.11 Detecting Smuggling (timing, differential responses)
- [ ] 26.12 Defense — Normalize Requests at Proxy, Disable TE

---

## MODULE 27 — Web Cache Poisoning and Deception (10) *(PS: 13 Cache Poisoning + 5 Cache Deception = 18 labs)*

- [ ] 27.01 What is Web Caching?
- [ ] 27.02 Cache Keys and Unkeyed Inputs
- [ ] 27.03 Cache Poisoning via X-Forwarded-Host
- [ ] 27.04 Cache Poisoning via X-Forwarded-Scheme
- [ ] 27.05 Cache Poisoning via Unkeyed Headers
- [ ] 27.06 Cache Poisoning via Fat GET
- [ ] 27.07 Cache Poisoning to Deliver XSS
- [ ] 27.08 Cache Poisoning to Redirect Users
- [ ] 27.09 Web Cache Deception Attack
- [ ] 27.10 Defense — Cache Key Configuration, Vary Header

---

## MODULE 28 — Clickjacking (6) *(PS: 5 labs)*

- [ ] 28.01 What is Clickjacking?
- [ ] 28.02 Basic iframe Clickjacking
- [ ] 28.03 Multistep Clickjacking
- [ ] 28.04 Drag and Drop Clickjacking
- [ ] 28.05 Clickjacking + CSRF Chain
- [ ] 28.06 Defense — X-Frame-Options, CSP frame-ancestors

---

## MODULE 29 — WebSockets Security (10) *(PS: 3 labs)*

- [ ] 29.01 WebSocket Protocol — How It Works
- [ ] 29.02 WebSocket Upgrade Security Implications
- [ ] 29.03 Cross-Site WebSocket Hijacking (CSWSH)
- [ ] 29.04 WebSocket Message Manipulation
- [ ] 29.05 WebSocket XSS
- [ ] 29.06 WebSocket SQLi
- [ ] 29.07 WebSocket Command Injection
- [ ] 29.08 WebSocket DoS
- [ ] 29.09 Lack of Authentication on WebSocket Endpoints
- [ ] 29.10 Defense — Origin Check, Authentication per Message

---

## MODULE 30 — GraphQL Security (18) *(PS: 5 labs)*

- [ ] 30.01 What is GraphQL?
- [ ] 30.02 GraphQL vs REST — Attack Surface Differences
- [ ] 30.03 Introspection Query — Information Disclosure
- [ ] 30.04 GraphQL Enumeration (clairvoyance, graphql-cop)
- [ ] 30.05 GraphQL Injection
- [ ] 30.06 GraphQL Batching Attacks (brute force via batching)
- [ ] 30.07 GraphQL Alias-Based Rate Limit Bypass
- [ ] 30.08 GraphQL IDOR
- [ ] 30.09 GraphQL Mutations — Unauthorized Write Operations
- [ ] 30.10 GraphQL Subscriptions Abuse
- [ ] 30.11 GraphQL Depth and Complexity DoS
- [ ] 30.12 GraphQL SSRF via Directives
- [ ] 30.13 GraphQL Upload Vulnerabilities
- [ ] 30.14 GraphQL Authorization Bypass
- [ ] 30.15 Broken Access Control in Nested Queries
- [ ] 30.16 GraphQL Type Confusion
- [ ] 30.17 GraphQL Endpoint Discovery
- [ ] 30.18 Defense — Disable Introspection in Production, Query Depth Limits

---

## MODULE 31 — API Security — OWASP API Top 10 (25) *(PS: 5 API + 4 LLM = 9 labs)*

- [ ] 31.01 API1 — Broken Object Level Authorization (BOLA)
- [ ] 31.02 API2 — Broken Authentication
- [ ] 31.03 API3 — Broken Object Property Level Authorization
- [ ] 31.04 API4 — Unrestricted Resource Consumption
- [ ] 31.05 API5 — Broken Function Level Authorization (BFLA)
- [ ] 31.06 API6 — Unrestricted Access to Sensitive Business Flows
- [ ] 31.07 API7 — Server Side Request Forgery (SSRF)
- [ ] 31.08 API8 — Security Misconfiguration
- [ ] 31.09 API9 — Improper Inventory Management
- [ ] 31.10 API10 — Unsafe Consumption of APIs
- [ ] 31.11 API Key Exposure in Source Code / JS Files
- [ ] 31.12 API Key in URL Parameters (logged in access logs)
- [ ] 31.13 API Versioning Abuse (v1 vs v2)
- [ ] 31.14 Mass Assignment in REST APIs
- [ ] 31.15 Excessive Data Exposure
- [ ] 31.16 Lack of Resource Rate Limiting
- [ ] 31.17 API Fuzzing with ffuf and Burp
- [ ] 31.18 API Documentation Discovery (Swagger, OpenAPI, WADL)
- [ ] 31.19 REST API Method Override Attacks
- [ ] 31.20 API Token Leakage in Logs
- [ ] 31.21 API Key Rotation Failures
- [ ] 31.22 Unauthenticated API Endpoints
- [ ] 31.23 SOAP API Attacks (SOAPAction manipulation, WSDL scraping)
- [ ] 31.24 gRPC Security Testing
- [ ] 31.25 Web LLM Attacks (prompt injection, indirect prompt injection, data exfil)

---

## MODULE 32 — Cryptography Vulnerabilities (15)

- [ ] 32.01 Weak Hashing Algorithms (MD5, SHA1 for passwords)
- [ ] 32.02 Rainbow Table Attacks
- [ ] 32.03 Unsalted Password Hashes
- [ ] 32.04 ECB Mode Encryption — Block Boundary Manipulation
- [ ] 32.05 CBC Padding Oracle Attack
- [ ] 32.06 Predictable IVs and Nonces
- [ ] 32.07 Insecure Random Number Generation
- [ ] 32.08 Hardcoded Secrets in Code
- [ ] 32.09 Weak TLS Configuration (SSLv3, TLS 1.0, RC4, DES)
- [ ] 32.10 Certificate Validation Bypass
- [ ] 32.11 BEAST Attack
- [ ] 32.12 BREACH Attack (compression + secret)
- [ ] 32.13 CRIME Attack (compression of cookies over TLS)
- [ ] 32.14 Diffie-Hellman Weak Parameters (Logjam)
- [ ] 32.15 Defense — Strong Algorithms, Key Management, TLS Best Practices

---

## MODULE 33 — Information Disclosure (12) *(PS: 5 labs)*

- [ ] 33.01 Verbose Error Messages
- [ ] 33.02 Stack Traces in Responses
- [ ] 33.03 Debug Endpoints (/debug, /actuator, /console)
- [ ] 33.04 Source Code Disclosure
- [ ] 33.05 .git Directory Exposed
- [ ] 33.06 .env File Exposed
- [ ] 33.07 Backup Files Exposed (.bak, .old, .swp)
- [ ] 33.08 Version Disclosure (Server, X-Powered-By)
- [ ] 33.09 Internal IP Disclosure in Headers
- [ ] 33.10 Comment Disclosure in HTML Source
- [ ] 33.11 API Response Over-Exposure
- [ ] 33.12 Defense — Error Handling, Remove Debug Info

---

## MODULE 34 — Subdomain Takeover (8)

- [ ] 34.01 What is Subdomain Takeover?
- [ ] 34.02 CNAME to Unclaimed External Service (GitHub Pages, Heroku, S3)
- [ ] 34.03 Fingerprinting Vulnerable Services
- [ ] 34.04 Subdomain Takeover — Full Exploit Walkthrough
- [ ] 34.05 NS Takeover
- [ ] 34.06 MX Takeover (email interception)
- [ ] 34.07 Tools — subjack, nuclei, can-i-take-over-xyz
- [ ] 34.08 Defense — Remove Dangling DNS Records

---

## MODULE 35 — Network Protocol Attacks (35)

- [ ] 35.01 FTP — Anonymous Login, Bounce Attack, Credential Brute Force
- [ ] 35.02 SSH — Brute Force, Weak Keys, Version Vulns
- [ ] 35.03 Telnet — Cleartext Protocol Attacks
- [ ] 35.04 SMTP — Open Relay, User Enumeration (VRFY, EXPN), Spoofing
- [ ] 35.05 IMAP/POP3 — Credential Attacks
- [ ] 35.06 DNS — Zone Transfer (AXFR), Cache Poisoning, Spoofing
- [ ] 35.07 DHCP — Starvation, Rogue DHCP Server
- [ ] 35.08 SNMP — Default Community Strings, Information Disclosure
- [ ] 35.09 RDP — Brute Force, BlueKeep, DejaBlue
- [ ] 35.10 SMB — EternalBlue, Null Session, Relay Attacks
- [ ] 35.11 NetBIOS — Enumeration, NBNS Poisoning
- [ ] 35.12 LDAP — Anonymous Bind, Enumeration, Injection
- [ ] 35.13 Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden/Silver Ticket, Kerberoasting, AS-REP Roasting
- [ ] 35.14 NFS — No_Root_Squash Exploitation
- [ ] 35.15 MySQL/MSSQL/PostgreSQL — Remote Access, Brute Force, UDF
- [ ] 35.16 Redis — Unauthenticated Access, RCE via Config Set
- [ ] 35.17 MongoDB — No Auth, Exposed Port
- [ ] 35.18 Elasticsearch — Open Access, Data Exfiltration
- [ ] 35.19 Memcached — Amplification Attack, Data Dumping
- [ ] 35.20 Docker API — Exposed Daemon, Container Escape
- [ ] 35.21 Kubernetes API — Unauthenticated Access, RBAC Bypass
- [ ] 35.22 etcd — Exposed Key-Value Store
- [ ] 35.23 Consul — Service Mesh Misconfig
- [ ] 35.24 Zookeeper — Unauthenticated Access
- [ ] 35.25 Jenkins — Groovy Script Console, Unauthenticated RCE
- [ ] 35.26 GitLab / GitHub — Exposed Tokens, LFI CVEs
- [ ] 35.27 Jira / Confluence — Authentication Bypass CVEs
- [ ] 35.28 Prometheus / Grafana — Metrics Exposure, Credential Disclosure
- [ ] 35.29 VNC — No Authentication, Weak Password
- [ ] 35.30 X11 — Exposed Display Server
- [ ] 35.31 MSMQ — Unauthenticated Access
- [ ] 35.32 MQTT — Unauthenticated Broker
- [ ] 35.33 CoAP — IoT Protocol Attacks
- [ ] 35.34 SIP / VoIP — Enumeration, Eavesdropping, Toll Fraud
- [ ] 35.35 BGP — Route Hijacking (conceptual)

---

## MODULE 36 — Active Directory Attacks (30)

- [ ] 36.01 Active Directory Overview (Domain, DC, OU, GPO)
- [ ] 36.02 AD Enumeration (BloodHound, ldapdomaindump, enum4linux)
- [ ] 36.03 Kerberosable Accounts — SPN Scanning
- [ ] 36.04 Kerberoasting — Hash Cracking of Service Accounts
- [ ] 36.05 AS-REP Roasting — No Pre-Auth Accounts
- [ ] 36.06 Pass the Hash (PtH)
- [ ] 36.07 Pass the Ticket (PtT)
- [ ] 36.08 Overpass the Hash
- [ ] 36.09 Golden Ticket Attack (krbtgt hash)
- [ ] 36.10 Silver Ticket Attack (service account hash)
- [ ] 36.11 NTLM Relay Attack
- [ ] 36.12 SMB Relay
- [ ] 36.13 LDAP Relay
- [ ] 36.14 LLMNR / NBT-NS Poisoning (Responder)
- [ ] 36.15 DCSync Attack
- [ ] 36.16 DCShadow Attack
- [ ] 36.17 ACL Abuse (GenericAll, WriteDACL, ForceChangePassword)
- [ ] 36.18 GPO Abuse
- [ ] 36.19 AdminSDHolder Abuse
- [ ] 36.20 Mimikatz — Credential Dumping
- [ ] 36.21 LSASS Dumping
- [ ] 36.22 SAM Hive Extraction
- [ ] 36.23 BloodHound — Attack Path Analysis
- [ ] 36.24 Domain Privilege Escalation via Trust Relationships
- [ ] 36.25 Forest Trust Attacks
- [ ] 36.26 PrintNightmare (CVE-2021-34527)
- [ ] 36.27 ZeroLogon (CVE-2020-1472)
- [ ] 36.28 MS14-068 (Kerberos PAC Vulnerability)
- [ ] 36.29 Exchange — ProxyLogon, ProxyShell, ProxyNotShell
- [ ] 36.30 Defense — Tiering, Least Privilege, LAPS, Defender for Identity

---

## MODULE 37 — Cloud Infrastructure (35)

### AWS
- [ ] 37.01 AWS IAM — Roles, Policies, Misconfigurations
- [ ] 37.02 AWS S3 — Public Access, ACL Misconfiguration
- [ ] 37.03 AWS EC2 — Metadata Service (IMDS) Exploitation
- [ ] 37.04 AWS Lambda — Privilege Escalation, Event Injection
- [ ] 37.05 AWS ECS / EKS — Container Privilege Escalation
- [ ] 37.06 AWS SecretsManager / Parameter Store — Misconfigured Access
- [ ] 37.07 AWS CloudTrail — Disabling Logging
- [ ] 37.08 AWS RDS — Publicly Exposed Databases
- [ ] 37.09 AWS SQS / SNS — Message Queue Interception
- [ ] 37.10 AWS API Gateway — Authorization Bypass
- [ ] 37.11 AWS Cognito — Misconfigured User Pools
- [ ] 37.12 AWS IAM Privilege Escalation (21 Rhino Security methods)

### GCP
- [ ] 37.13 GCP IAM — Service Account Key Abuse
- [ ] 37.14 GCP Cloud Storage — Public Bucket Access
- [ ] 37.15 GCP Metadata Server — Credential Theft
- [ ] 37.16 GCP Cloud Functions — Privilege Escalation
- [ ] 37.17 GCP Compute Engine — Default Service Account Abuse

### Azure
- [ ] 37.18 Azure AD — Misconfiguration, Privilege Escalation
- [ ] 37.19 Azure Blob Storage — Public Access
- [ ] 37.20 Azure Function Apps — Exposed Secrets
- [ ] 37.21 Azure SSRF via Metadata
- [ ] 37.22 Azure Service Principal Abuse
- [ ] 37.23 Azure Managed Identity Abuse

### Cross-Cloud
- [ ] 37.24 Cloud Metadata Endpoint Cheat Sheet (all providers)
- [ ] 37.25 IMDSv2 Bypass Techniques
- [ ] 37.26 Cloud Enumeration Tools (ScoutSuite, Prowler, CloudFox)
- [ ] 37.27 Cloud SSRF to Credential Theft — Full Chain
- [ ] 37.28 Serverless Security Testing
- [ ] 37.29 Container Registry Attacks (ECR, GCR, ACR)
- [ ] 37.30 Terraform / CloudFormation Misconfigurations
- [ ] 37.31 Kubernetes on Cloud — EKS, GKE, AKS
- [ ] 37.32 Cloud Storage Mining (secrets in S3/GCS/Blobs)
- [ ] 37.33 CI/CD Pipeline Attacks (GitHub Actions, GitLab CI)
- [ ] 37.34 Cloud Backdoor via IAM Role
- [ ] 37.35 Defense — Least Privilege IAM, IMDSv2, Logging, SCP

---

## MODULE 38 — Container and Kubernetes Security (22)

- [ ] 38.01 Docker Overview — Images, Containers, Registries
- [ ] 38.02 Docker Daemon Exposed (TCP 2375/2376)
- [ ] 38.03 Docker Socket Mount Privilege Escalation
- [ ] 38.04 Container Escape — Privileged Container
- [ ] 38.05 Container Escape — Mounted Host Filesystem
- [ ] 38.06 Container Escape — SYS_PTRACE Capability
- [ ] 38.07 Container Escape — Kernel Exploits
- [ ] 38.08 Dockerfile Security Misconfigurations
- [ ] 38.09 Secrets in Docker Images (layers, ENV vars)
- [ ] 38.10 Kubernetes Architecture — Control Plane, Nodes, Pods
- [ ] 38.11 Kubernetes RBAC — ClusterAdmin Misconfig
- [ ] 38.12 Exposed Kubernetes Dashboard
- [ ] 38.13 Kubernetes API Server — Unauthenticated Access
- [ ] 38.14 Kubernetes etcd — Direct Access to Secrets
- [ ] 38.15 Pod Security — Privileged Pods
- [ ] 38.16 HostPath Volume Mount Abuse
- [ ] 38.17 Service Account Token Theft
- [ ] 38.18 Kubernetes Secret Enumeration
- [ ] 38.19 Lateral Movement in K8s (pod to pod)
- [ ] 38.20 Admission Controller Bypass
- [ ] 38.21 Supply Chain — Malicious Container Images
- [ ] 38.22 Defense — Pod Security Admission, Network Policies, RBAC Hardening

---

## MODULE 39 — WAF Bypass Techniques (20)

- [ ] 39.01 What is a WAF and How It Works
- [ ] 39.02 WAF Fingerprinting (wafw00f, manual)
- [ ] 39.03 URL Encoding Bypass
- [ ] 39.04 Double URL Encoding
- [ ] 39.05 Unicode Normalization Bypass
- [ ] 39.06 Case Variation (SeLeCt vs SELECT)
- [ ] 39.07 Comment Insertion (SEL/**/ECT)
- [ ] 39.08 Whitespace Substitution (tab, newline, vertical tab)
- [ ] 39.09 Keyword Splitting and Concatenation
- [ ] 39.10 HTTP Parameter Pollution (HPP)
- [ ] 39.11 Chunked Transfer Encoding Bypass
- [ ] 39.12 Content-Type Switching
- [ ] 39.13 JSON/XML Wrapping
- [ ] 39.14 Wildcard Bypass (* in SQL)
- [ ] 39.15 Out-of-Band Bypass (DNS exfiltration)
- [ ] 39.16 IP Rotation
- [ ] 39.17 Slowloris and Rate Manipulation
- [ ] 39.18 HTTP/2 Cleartext (h2c) Smuggling past WAF
- [ ] 39.19 CDN Origin Direct Access (bypassing WAF entirely)
- [ ] 39.20 ML-Based WAF Evasion Concepts

---

## MODULE 40 — Vulnerability Chaining Playbook (25)

- [ ] 40.01 Recon → Subdomain Takeover → Phishing Campaign
- [ ] 40.02 Open Redirect → OAuth Token Theft → Account Takeover
- [ ] 40.03 SSRF → Cloud Metadata → IAM Credential Theft → Cloud Takeover
- [ ] 40.04 XSS → CSRF → Admin Account Takeover
- [ ] 40.05 XSS → Session Hijacking → Privilege Escalation
- [ ] 40.06 IDOR → PII Exfiltration → Mass Account Breach
- [ ] 40.07 SQLi → File Read → Credentials → RCE
- [ ] 40.08 File Upload → Webshell → RCE → Lateral Movement
- [ ] 40.09 JWT Algorithm Confusion → Admin JWT → Full App Takeover
- [ ] 40.10 CORS Misconfiguration → CSRF → Credential Theft
- [ ] 40.11 XXE → SSRF → Internal API Access → Data Exfiltration
- [ ] 40.12 Path Traversal → LFI → Log Poisoning → RCE
- [ ] 40.13 GraphQL Introspection → Mutation Abuse → Privilege Escalation
- [ ] 40.14 Host Header Injection → Password Reset Poisoning → Account Takeover
- [ ] 40.15 Mass Assignment → Admin Role → Full App Control
- [ ] 40.16 HTTP Smuggling → Cache Poisoning → Stored XSS
- [ ] 40.17 Subdomain Takeover → Cookie Theft → Account Takeover
- [ ] 40.18 SSTI → RCE → Container Escape → Host Compromise
- [ ] 40.19 Recon → Default Creds → Internal Network → AD Compromise
- [ ] 40.20 API Key in JS → Cloud Access → S3 Data Exfiltration
- [ ] 40.21 OAuth State CSRF → Account Linking → ATO
- [ ] 40.22 Race Condition → Double Spend → Financial Fraud
- [ ] 40.23 Deserialization → RCE → Persistence via Cron
- [ ] 40.24 LDAP Injection → Credential Dump → Lateral Movement
- [ ] 40.25 Full Red Team Simulation — Recon to Domain Admin

---

## MODULE 41 — Tools (32)

- [ ] 41.01 Burp Suite — Proxy, Scanner, Repeater, Intruder, Decoder, Collaborator
- [ ] 41.02 OWASP ZAP — Open Source Alternative
- [ ] 41.03 Nmap — Port Scanning, Service Detection, NSE Scripts
- [ ] 41.04 Masscan — High-Speed Port Scanner
- [ ] 41.05 Rustscan — Fast Nmap Wrapper
- [ ] 41.06 ffuf — Web Fuzzer (dirs, params, vhosts)
- [ ] 41.07 Gobuster — Directory and DNS Bruteforcer
- [ ] 41.08 Feroxbuster — Recursive Content Discovery
- [ ] 41.09 sqlmap — Automated SQL Injection
- [ ] 41.10 Nikto — Web Vulnerability Scanner
- [ ] 41.11 Nuclei — Template-Based Vulnerability Scanner
- [ ] 41.12 Metasploit Framework — Exploitation and Post-Exploitation
- [ ] 41.13 Hydra — Network Login Brute Forcer
- [ ] 41.14 CrackMapExec / NetExec — SMB, LDAP, WinRM Attacks
- [ ] 41.15 BloodHound — AD Attack Path Visualizer
- [ ] 41.16 Impacket — Python AD Attack Toolkit
- [ ] 41.17 Responder — LLMNR/NBT-NS/mDNS Poisoner
- [ ] 41.18 Mimikatz — Windows Credential Dumping
- [ ] 41.19 jwt_tool — JWT Testing and Exploitation
- [ ] 41.20 Hashcat — Password Hash Cracking
- [ ] 41.21 John the Ripper — Password Cracking
- [ ] 41.22 Amass — Subdomain Enumeration
- [ ] 41.23 Subfinder — Fast Subdomain Finder
- [ ] 41.24 theHarvester — OSINT Harvesting
- [ ] 41.25 Shodan CLI — Command-Line Shodan
- [ ] 41.26 Arjun — HTTP Parameter Discovery
- [ ] 41.27 WhatWeb / Wappalyzer — Technology Fingerprinting
- [ ] 41.28 Wireshark / tcpdump — Packet Analysis
- [ ] 41.29 Interactsh / Burp Collaborator — OOB Detection
- [ ] 41.30 XSStrike / dalfox — XSS Scanning
- [ ] 41.31 ScoutSuite / Prowler — Cloud Security Auditing
- [ ] 41.32 LinkFinder / JSParser — JS Endpoint Discovery

---

## MODULE 42 — VAPT Reporting (15)

- [ ] 42.01 Why Reporting Matters
- [ ] 42.02 VAPT Report Structure (Executive Summary, Scope, Findings, Appendix)
- [ ] 42.03 Executive Summary — Writing for Non-Technical Stakeholders
- [ ] 42.04 Findings Section — Finding Template
- [ ] 42.05 Severity Ratings — Critical, High, Medium, Low, Informational
- [ ] 42.06 CVSS v3.1 Scoring — Base, Temporal, Environmental
- [ ] 42.07 CVSS Vector String — How to Read and Write
- [ ] 42.08 Risk Rating vs CVSS — Differences
- [ ] 42.09 Proof of Concept (PoC) — What to Include
- [ ] 42.10 Screenshots and Evidence — Best Practices
- [ ] 42.11 Remediation Guidance — Writing Actionable Fixes
- [ ] 42.12 Attack Narrative — Telling the Story of a Chain
- [ ] 42.13 Retesting Methodology
- [ ] 42.14 Sample Finding — SQL Injection (fully worked)
- [ ] 42.15 Sample Full Report — End-to-End Template

---

## TOTAL

| Module | Topics |
|--------|--------|
| 01 Networking Foundations | 22 |
| 02 HTTP Protocol | 28 |
| 03 HTTP Headers | 65 |
| 04 VAPT Methodology | 12 |
| 05 Reconnaissance | 30 |
| 06 SQL Injection | 25 |
| 07 XSS | 22 |
| 08 Command Injection | 12 |
| 09 SSTI | 10 |
| 10 Other Injections | 18 |
| 11 CSRF | 10 |
| 12 CORS | 12 |
| 13 SSRF | 20 |
| 14 XXE | 10 |
| 15 Deserialization | 12 |
| 16 Authentication | 28 |
| 17 Session Management | 15 |
| 18 JWT | 18 |
| 19 OAuth | 20 |
| 20 SAML | 10 |
| 21 Access Control | 20 |
| 22 File Upload | 15 |
| 23 Path Traversal / LFI | 12 |
| 24 Open Redirect | 8 |
| 25 Business Logic | 18 |
| 26 HTTP Smuggling | 12 |
| 27 Cache Poisoning | 10 |
| 28 Clickjacking | 6 |
| 29 WebSockets | 10 |
| 30 GraphQL | 18 |
| 31 API Security | 25 |
| 32 Cryptography | 15 |
| 33 Information Disclosure | 12 |
| 34 Subdomain Takeover | 8 |
| 35 Network Protocols | 35 |
| 36 Active Directory | 30 |
| 37 Cloud Infrastructure | 35 |
| 38 Container / Kubernetes | 22 |
| 39 WAF Bypass | 20 |
| 40 Chaining Playbook | 25 |
| 41 Tools | 32 |
| 42 Reporting | 15 |
| **TOTAL** | **776** |

---

## Related Files
- [[VAPT-Plan2-PortSwigger]] — all 278 PortSwigger labs with individual names and difficulty
- [[VAPT-Vault-Spec]] — project decisions
- [[00 - Learning Path]] — master index

---

## MODULE 43 — Windows Privilege Escalation (40)

- [ ] 43.01 Windows PrivEsc Methodology Overview
- [ ] 43.02 Enumerating Windows System Info (systeminfo, whoami, net user)
- [ ] 43.03 Unquoted Service Paths
- [ ] 43.04 Weak Service Permissions (sc.exe, accesschk)
- [ ] 43.05 Modifiable Service Binaries
- [ ] 43.06 DLL Hijacking
- [ ] 43.07 DLL Search Order Abuse
- [ ] 43.08 AlwaysInstallElevated — MSI Privilege Escalation
- [ ] 43.09 Token Impersonation — SeImpersonatePrivilege
- [ ] 43.10 JuicyPotato, RoguePotato, PrintSpoofer
- [ ] 43.11 Hot Potato / Sweet Potato / Ghost Potato
- [ ] 43.12 UAC Bypass Techniques
- [ ] 43.13 Scheduled Task Hijacking
- [ ] 43.14 Startup Applications Abuse
- [ ] 43.15 Registry Autorun Key Abuse
- [ ] 43.16 Stored Credentials — Windows Credential Manager
- [ ] 43.17 Stored Credentials — Unattend.xml, web.config, SAM
- [ ] 43.18 PowerShell History File (ConsoleHost_history.txt)
- [ ] 43.19 DPAPI — Credential Blob Decryption
- [ ] 43.20 Pass the Hash on Local Admin
- [ ] 43.21 Password in Group Policy Preferences (GPP)
- [ ] 43.22 LAPS — Reading Managed Admin Passwords
- [ ] 43.23 Abusing SeDebugPrivilege
- [ ] 43.24 Abusing SeTakeOwnershipPrivilege
- [ ] 43.25 Abusing SeBackupPrivilege / SeRestorePrivilege
- [ ] 43.26 Insecure File/Folder Permissions
- [ ] 43.27 Kernel Exploits (MS16-032, MS15-051)
- [ ] 43.28 Named Pipe Impersonation
- [ ] 43.29 COM Object Hijacking
- [ ] 43.30 Windows Subsystem for Linux (WSL) Abuse
- [ ] 43.31 Credential Dumping — SAM, SYSTEM, SECURITY hives
- [ ] 43.32 Volume Shadow Copy Theft
- [ ] 43.33 NTDS.dit Extraction
- [ ] 43.34 Living off the Land Binaries (LOLBins) — certutil, mshta, regsvr32, rundll32, msiexec
- [ ] 43.35 AppLocker and WDAC Bypass
- [ ] 43.36 Bypassing PowerShell Execution Policy
- [ ] 43.37 AMSI Bypass Techniques
- [ ] 43.38 Event Log Clearing and Evasion
- [ ] 43.39 Windows Defender Evasion Basics
- [ ] 43.40 Defense — Least Privilege, Patch Management, LAPS

---

## MODULE 44 — Linux Privilege Escalation (35)

- [ ] 44.01 Linux PrivEsc Methodology Overview
- [ ] 44.02 Enumeration Tools (LinPEAS, LinEnum, linux-exploit-suggester)
- [ ] 44.03 SUID Binaries Abuse
- [ ] 44.04 SGID Binaries Abuse
- [ ] 44.05 Capabilities Abuse (cap_setuid, cap_net_raw)
- [ ] 44.06 Sudo Misconfigurations (sudo -l, GTFOBins)
- [ ] 44.07 Writable /etc/passwd — Adding Root User
- [ ] 44.08 Writable /etc/shadow
- [ ] 44.09 Cron Job Abuse — Writable Scripts
- [ ] 44.10 Cron Job Abuse — PATH Hijacking
- [ ] 44.11 PATH Environment Variable Hijacking
- [ ] 44.12 LD_PRELOAD Abuse
- [ ] 44.13 Shared Library Injection
- [ ] 44.14 NFS No_Root_Squash Exploitation
- [ ] 44.15 Weak File Permissions on Sensitive Files
- [ ] 44.16 Password in Config Files, History, Env Vars
- [ ] 44.17 SSH Private Key Reuse
- [ ] 44.18 Writeable /etc/hosts
- [ ] 44.19 Docker Group Membership
- [ ] 44.20 LXC/LXD Group Abuse
- [ ] 44.21 Disk Group — Reading Raw Device Files
- [ ] 44.22 Wildcard Injection in Cron (tar, rsync, chown)
- [ ] 44.23 Kernel Exploits (DirtyCow, PwnKit, Baron Samedit)
- [ ] 44.24 PwnKit (CVE-2021-4034) — pkexec PrivEsc
- [ ] 44.25 DirtyPipe (CVE-2022-0847) — Kernel 5.8+
- [ ] 44.26 Systemd Service File Abuse
- [ ] 44.27 D-Bus Interface Misconfigurations
- [ ] 44.28 /proc Filesystem Information Leakage
- [ ] 44.29 Core Dump Analysis for Credentials
- [ ] 44.30 Tmux / Screen Session Hijacking
- [ ] 44.31 /tmp Race Conditions (symlink attacks)
- [ ] 44.32 Insecure Sudo Rules (NOPASSWD, ALL)
- [ ] 44.33 Python / Perl / Ruby Library Hijacking
- [ ] 44.34 Logrotate Exploitation
- [ ] 44.35 Defense — File Permission Hardening, Sudo Audit, Patch Management

---

## MODULE 45 — Post-Exploitation and Persistence (30)

- [ ] 45.01 Post-Exploitation Goals and Phases
- [ ] 45.02 Situational Awareness — What to Enumerate First
- [ ] 45.03 Data Exfiltration Techniques (DNS, HTTP, ICMP, FTP)
- [ ] 45.04 Persistence — Windows (Registry, Scheduled Tasks, Services)
- [ ] 45.05 Persistence — Linux (Cron, .bashrc, SSH keys, systemd)
- [ ] 45.06 Backdoor Accounts
- [ ] 45.07 Web Shell Persistence
- [ ] 45.08 Reverse Shell Stability (pty upgrade, socat, rlwrap)
- [ ] 45.09 Pivoting — Port Forwarding (SSH, chisel, ligolo)
- [ ] 45.10 Pivoting — SOCKS Proxy (proxychains)
- [ ] 45.11 Pivoting — Dynamic Port Forwarding
- [ ] 45.12 Lateral Movement — WMI (wmic, Invoke-WMIMethod)
- [ ] 45.13 Lateral Movement — WinRM (evil-winrm)
- [ ] 45.14 Lateral Movement — PsExec, SMBExec
- [ ] 45.15 Lateral Movement — RDP Pass-Through
- [ ] 45.16 Token Stealing with Incognito / Meterpreter
- [ ] 45.17 Credential Dumping — Windows (Mimikatz, Pypykatz)
- [ ] 45.18 Credential Dumping — Linux (/etc/shadow, memory)
- [ ] 45.19 Browser Credential Extraction (Chrome, Firefox)
- [ ] 45.20 Email Client Credential Extraction
- [ ] 45.21 SSH Agent Hijacking
- [ ] 45.22 LOLBins for Persistence (WMIC, schtasks, reg)
- [ ] 45.23 COM Hijacking for Persistence
- [ ] 45.24 DLL Side-Loading for Persistence
- [ ] 45.25 Rootkits — Concept and Detection
- [ ] 45.26 Bootkit — Concept and Detection
- [ ] 45.27 Memory-Only Malware (Fileless Malware)
- [ ] 45.28 Clearing Tracks — Windows (Event Logs, Prefetch, Shimcache)
- [ ] 45.29 Clearing Tracks — Linux (bash_history, wtmp, lastlog)
- [ ] 45.30 Defense — EDR, SIEM, Honeytokens, Integrity Monitoring

---

## MODULE 46 — Social Engineering and Phishing (20)

- [ ] 46.01 Social Engineering — Psychology and Principles
- [ ] 46.02 Phishing — Types (Spear, Whaling, Vishing, Smishing)
- [ ] 46.03 Building a Phishing Email (GoPhish setup)
- [ ] 46.04 Phishing Page Cloning (evilginx2, SET)
- [ ] 46.05 Credential Harvesting Pages
- [ ] 46.06 Evilginx2 — Adversary-in-the-Middle Phishing (MFA Bypass)
- [ ] 46.07 Pretexting — Building a Convincing Scenario
- [ ] 46.08 Spear Phishing — Targeting with OSINT
- [ ] 46.09 Phishing via OAuth Consent Pages
- [ ] 46.10 QR Code Phishing (Quishing)
- [ ] 46.11 Browser-in-the-Browser (BitB) Attack
- [ ] 46.12 USB Drop Attacks (Rubber Ducky, O.MG Cable)
- [ ] 46.13 Vishing — Phone-Based Social Engineering
- [ ] 46.14 Smishing — SMS-Based Attacks
- [ ] 46.15 Pretexting via Help Desk
- [ ] 46.16 Physical Security — Tailgating and Piggybacking
- [ ] 46.17 Baiting and Impersonation
- [ ] 46.18 Open Redirect for Phishing Lure
- [ ] 46.19 Domain Squatting — Typosquatting, Homograph Attacks
- [ ] 46.20 Defense — Security Awareness Training, Email Filtering, MFA

---

## MODULE 47 — Mobile Application Security (30)

- [ ] 47.01 Mobile App Attack Surface Overview (Android vs iOS)
- [ ] 47.02 Android Architecture — APK, ADB, Dalvik/ART
- [ ] 47.03 iOS Architecture — IPA, Jailbreaking, Secure Enclave
- [ ] 47.04 Setting Up Android Test Environment (Emulator, ADB)
- [ ] 47.05 Setting Up iOS Test Environment (Jailbroken Device, Frida)
- [ ] 47.06 Static Analysis — APK Decompilation (jadx, apktool)
- [ ] 47.07 Static Analysis — iOS IPA (class-dump, otool, MobSF)
- [ ] 47.08 Dynamic Analysis — Frida (Android and iOS)
- [ ] 47.09 MobSF — Mobile Security Framework
- [ ] 47.10 Insecure Data Storage (SharedPreferences, SQLite, files)
- [ ] 47.11 Hardcoded Credentials and API Keys in APK
- [ ] 47.12 Insecure Communication — SSL Pinning Bypass
- [ ] 47.13 Traffic Interception (Burp + Android proxy setup)
- [ ] 47.14 Improper Authentication — Biometric Bypass
- [ ] 47.15 Broken Access Control in Mobile APIs
- [ ] 47.16 Insecure IPC — Intent Hijacking, Content Provider Leakage
- [ ] 47.17 Deep Link Hijacking
- [ ] 47.18 Task Hijacking (Android StrandHogg)
- [ ] 47.19 Exported Activities and Services Abuse
- [ ] 47.20 WebView Attacks (XSS via WebView, addJavascriptInterface)
- [ ] 47.21 Clipboard Sniffing
- [ ] 47.22 Screenshot / Screen Capture Leakage
- [ ] 47.23 Tapjacking (Android Clickjacking)
- [ ] 47.24 App Reversing for Logic Flaws
- [ ] 47.25 Patching APKs (repackaging with malicious code)
- [ ] 47.26 Root Detection and Jailbreak Detection Bypass
- [ ] 47.27 Certificate Pinning Bypass (Frida, objection)
- [ ] 47.28 OWASP Mobile Top 10 Overview
- [ ] 47.29 Firebase Misconfiguration (Exposed Databases)
- [ ] 47.30 Defense — Certificate Pinning, Root Detection, Obfuscation

---

## MODULE 48 — Wireless Security (20)

- [ ] 48.01 Wireless Networking Basics (802.11 a/b/g/n/ac/ax)
- [ ] 48.02 WEP Cracking (RC4 weakness, aircrack-ng)
- [ ] 48.03 WPA/WPA2 — 4-Way Handshake Capture
- [ ] 48.04 WPA2 Handshake Cracking (hashcat, aircrack-ng)
- [ ] 48.05 WPA3 — SAE Handshake, Dragonblood Attacks
- [ ] 48.06 PMKID Attack (WPA2 without full handshake)
- [ ] 48.07 Evil Twin / Rogue AP Attack
- [ ] 48.08 Deauthentication Attack (aireplay-ng)
- [ ] 48.09 KARMA Attack
- [ ] 48.10 WPS PIN Attack (Pixie Dust, Reaver)
- [ ] 48.11 Enterprise WPA2 (PEAP/EAP) — MSCHAPv2 Capture
- [ ] 48.12 Captive Portal Bypass
- [ ] 48.13 SSID Spoofing and Hidden SSID Discovery
- [ ] 48.14 Bluetooth Attacks — BLE Sniffing, BlueBorne
- [ ] 48.15 Bluetooth — MITM (BlueSmack, Bluesnarfing, Bluejacking)
- [ ] 48.16 Zigbee and Z-Wave IoT Protocol Attacks
- [ ] 48.17 NFC Attacks — Relay and Sniffing
- [ ] 48.18 RFID Cloning
- [ ] 48.19 Wi-Fi Tools (aircrack-ng suite, hcxtools, bettercap)
- [ ] 48.20 Defense — WPA3, EAP-TLS, 802.1X, Network Segmentation

---

## MODULE 49 — IoT Security (20)

- [ ] 49.01 IoT Attack Surface Overview
- [ ] 49.02 IoT Device Firmware Extraction
- [ ] 49.03 Firmware Analysis and Reverse Engineering (binwalk, strings, Ghidra)
- [ ] 49.04 Hardcoded Credentials in Firmware
- [ ] 49.05 Telnet/SSH Exposed on IoT Devices
- [ ] 49.06 Insecure Update Mechanisms
- [ ] 49.07 UART / JTAG Hardware Debugging Interfaces
- [ ] 49.08 Serial Console Access
- [ ] 49.09 SPI Flash Dumping
- [ ] 49.10 Command Injection in IoT Web Interfaces
- [ ] 49.11 MQTT — Unauthenticated Broker Exploitation
- [ ] 49.12 CoAP Protocol Attacks
- [ ] 49.13 Modbus / DNP3 — Industrial Protocol Attacks
- [ ] 49.14 Shodan for IoT Device Discovery
- [ ] 49.15 Router Exploitation (default creds, CVEs)
- [ ] 49.16 IP Camera Exploitation (RTSP, ONVIF, CVEs)
- [ ] 49.17 Smart Home Device Attacks (Zigbee, Z-Wave)
- [ ] 49.18 Medical Device Security Overview
- [ ] 49.19 SCADA / ICS Security Concepts
- [ ] 49.20 Defense — Network Segmentation, Firmware Signing, Patch Management

---

## MODULE 50 — Thick Client Application Security (15)

- [ ] 50.01 Thick Client Architecture Overview
- [ ] 50.02 Static Analysis — .NET (dnSpy, ILSpy, dotPeek)
- [ ] 50.03 Static Analysis — Java (jd-gui, fernflower, jadx)
- [ ] 50.04 Static Analysis — Electron Apps
- [ ] 50.05 Dynamic Analysis — Process Monitor, API Monitor, Wireshark
- [ ] 50.06 Traffic Interception for Thick Clients (Burp + proxy settings)
- [ ] 50.07 DLL Injection and Hooking
- [ ] 50.08 Memory Analysis — Credential Extraction from Memory
- [ ] 50.09 Insecure Data Storage — SQLite, Registry, Local Files
- [ ] 50.10 Hardcoded Credentials in Executables
- [ ] 50.11 Client-Side Validation Bypass
- [ ] 50.12 Binary Patching and Reverse Engineering (x64dbg, Ghidra)
- [ ] 50.13 DLL Side-Loading in Thick Clients
- [ ] 50.14 Electron App Attacks (Node.js injection, preload bypass)
- [ ] 50.15 Defense — Code Signing, ASLR, DEP, Obfuscation

---

## MODULE 51 — Source Code Review / SAST (20)

- [ ] 51.01 What is SAST (Static Application Security Testing)?
- [ ] 51.02 Source Code Review Methodology
- [ ] 51.03 Identifying Dangerous Functions (PHP, Python, Java, JS, Go)
- [ ] 51.04 Taint Analysis — Tracking User Input to Sinks
- [ ] 51.05 SQL Injection in Source Code (PHP, Java, Python, Node.js)
- [ ] 51.06 XSS in Source Code (template rendering, innerHTML)
- [ ] 51.07 Command Injection in Source Code (os.system, exec, shell=True)
- [ ] 51.08 Path Traversal in Source Code
- [ ] 51.09 Insecure Deserialization in Source Code
- [ ] 51.10 Hardcoded Secrets in Source Code (grep patterns)
- [ ] 51.11 Insecure Cryptography in Source Code
- [ ] 51.12 Race Conditions in Source Code
- [ ] 51.13 IDOR in Source Code (missing authorization checks)
- [ ] 51.14 Mass Assignment in Source Code (Laravel, Rails, Django)
- [ ] 51.15 SAST Tools — Semgrep, Bandit, Brakeman, SonarQube, CodeQL
- [ ] 51.16 Semgrep — Writing Custom Rules
- [ ] 51.17 GitHub Actions / CI Pipeline SAST Integration
- [ ] 51.18 Secrets Scanning — GitLeaks, TruffleHog, detect-secrets
- [ ] 51.19 Dependency Confusion and Supply Chain in Dependencies
- [ ] 51.20 Reviewing Terraform / IaC for Security Misconfigs

---

## MODULE 52 — Dynamic Analysis / DAST (15)

- [ ] 52.01 What is DAST (Dynamic Application Security Testing)?
- [ ] 52.02 DAST vs SAST vs IAST — Comparison
- [ ] 52.03 Automated DAST — Burp Suite Scanner
- [ ] 52.04 Automated DAST — OWASP ZAP
- [ ] 52.05 Automated DAST — Nikto
- [ ] 52.06 Automated DAST — Nuclei Custom Templates
- [ ] 52.07 Fuzzing — AFL, libFuzzer Concepts (web context)
- [ ] 52.08 API Fuzz Testing — ffuf, Burp Intruder
- [ ] 52.09 DAST Integration in CI/CD Pipelines
- [ ] 52.10 Crawling and Spidering — Spider vs Passive Crawl
- [ ] 52.11 Authenticated DAST — Session Management in Scans
- [ ] 52.12 IAST — Runtime Agent Analysis
- [ ] 52.13 Correlation — SAST Findings vs DAST Confirmation
- [ ] 52.14 False Positive Management in DAST
- [ ] 52.15 Defense — Shift-Left Security, DevSecOps Integration

---

## MODULE 53 — Supply Chain Security (15)

- [ ] 53.01 What is a Supply Chain Attack?
- [ ] 53.02 SolarWinds — Case Study
- [ ] 53.03 XZ Utils Backdoor (CVE-2024-3094) — Case Study
- [ ] 53.04 npm/PyPI/RubyGems Package Hijacking
- [ ] 53.05 Dependency Confusion Attack
- [ ] 53.06 Typosquatting in Package Registries
- [ ] 53.07 Malicious Packages — Detection and Prevention
- [ ] 53.08 Build Pipeline Compromise (GitHub Actions, Jenkins)
- [ ] 53.09 CI/CD Secret Leakage (env vars, logs)
- [ ] 53.10 Compromised Container Base Images
- [ ] 53.11 SBOM (Software Bill of Materials) — What and Why
- [ ] 53.12 Sigstore / cosign — Supply Chain Signing
- [ ] 53.13 Artifact Registry Security (Artifactory, Nexus)
- [ ] 53.14 Open Source Dependency Audit (Snyk, Dependabot, OWASP Dependency-Check)
- [ ] 53.15 Defense — Pinned Dependencies, Signed Commits, SLSA Framework

---

## MODULE 54 — Exploit Development Basics (20)

- [ ] 54.01 What is Exploit Development?
- [ ] 54.02 Memory Layout — Stack, Heap, BSS, Text
- [ ] 54.03 Stack Buffer Overflow — Basics
- [ ] 54.04 Finding the EIP Offset (pattern_create, pattern_offset)
- [ ] 54.05 Controlling EIP — JMP ESP Technique
- [ ] 54.06 Shellcode — What It Is and How It Works
- [ ] 54.07 Bad Characters — Identifying and Removing
- [ ] 54.08 SEH-Based Buffer Overflow
- [ ] 54.09 Heap Overflow — Concepts
- [ ] 54.10 Format String Vulnerabilities
- [ ] 54.11 Use-After-Free Vulnerabilities
- [ ] 54.12 Integer Overflow — Web and Binary Context
- [ ] 54.13 Return-Oriented Programming (ROP) — Concepts
- [ ] 54.14 ASLR, DEP, Stack Canary — Protections Overview
- [ ] 54.15 Bypassing DEP — ROP Chains
- [ ] 54.16 Bypassing ASLR — Info Leak + ROP
- [ ] 54.17 pwndbg / pwntools — Tools for Exploit Dev
- [ ] 54.18 GDB — Debugging for Exploit Dev
- [ ] 54.19 Immunity Debugger + Mona.py (Windows)
- [ ] 54.20 Metasploit — Module Development Basics

---

## MODULE 55 — Threat Intelligence and CVEs (15)

- [ ] 55.01 What is Threat Intelligence?
- [ ] 55.02 CVE, CVSS, CWE — Terminology
- [ ] 55.03 NVD — National Vulnerability Database
- [ ] 55.04 Exploit-DB and Packet Storm — Finding Public Exploits
- [ ] 55.05 SearchSploit — Offline Exploit-DB Search
- [ ] 55.06 MITRE ATT&CK Framework — Tactics, Techniques, Procedures
- [ ] 55.07 MITRE ATT&CK — Mapping Findings to TTPs
- [ ] 55.08 Cyber Kill Chain — Lockheed Martin Model
- [ ] 55.09 Threat Modeling — STRIDE, PASTA, DREAD
- [ ] 55.10 CVE Research — Finding PoCs from GitHub
- [ ] 55.11 Vulnerability Disclosure — Responsible Disclosure Process
- [ ] 55.12 Bug Bounty Programs — HackerOne, Bugcrowd, Intigriti
- [ ] 55.13 Patch Diffing — Finding Vulns from Patches
- [ ] 55.14 1-Day vs 0-Day Research Concepts
- [ ] 55.15 IOCs — Indicators of Compromise

---

## MODULE 56 — Defensive Security and Hardening (25)

- [ ] 56.01 Defense-in-Depth — Layered Security Model
- [ ] 56.02 Security Hardening — CIS Benchmarks
- [ ] 56.03 Linux Hardening (SSH, firewall, sysctl, AppArmor, SELinux)
- [ ] 56.04 Windows Hardening (GPO, Windows Defender, Attack Surface Reduction)
- [ ] 56.05 Web Server Hardening (Nginx, Apache — headers, TLS, directory listing)
- [ ] 56.06 Database Hardening (MySQL, PostgreSQL — users, permissions, encryption)
- [ ] 56.07 Firewall Rules — Allowlist vs Denylist
- [ ] 56.08 Network Segmentation and VLANs
- [ ] 56.09 Zero Trust Architecture
- [ ] 56.10 Intrusion Detection — IDS vs IPS (Snort, Suricata)
- [ ] 56.11 SIEM — Concepts, Log Aggregation, Alerting (Splunk, ELK, Wazuh)
- [ ] 56.12 SOC Operations — Tier 1/2/3 Overview
- [ ] 56.13 Incident Response — PICERL (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned)
- [ ] 56.14 Digital Forensics — Evidence Collection, Chain of Custody
- [ ] 56.15 Memory Forensics (Volatility)
- [ ] 56.16 Disk Forensics (Autopsy, FTK)
- [ ] 56.17 Log Analysis for Attack Detection
- [ ] 56.18 Honeypots and Honeytokens
- [ ] 56.19 Threat Hunting — Hypothesis-Driven Approach
- [ ] 56.20 EDR Solutions — CrowdStrike, SentinelOne, Microsoft Defender for Endpoint
- [ ] 56.21 Security Monitoring — What to Alert On
- [ ] 56.22 Patch Management Strategy
- [ ] 56.23 Vulnerability Management Program
- [ ] 56.24 Purple Team — Red + Blue Collaboration
- [ ] 56.25 Security Maturity Models (CMMI, BSIMM, OpenSAMM)

---

## MODULE 57 — OWASP Frameworks and Standards (15)

- [ ] 57.01 OWASP Top 10 2021 — Full Walkthrough
- [ ] 57.02 OWASP API Security Top 10 2023
- [ ] 57.03 OWASP Mobile Top 10
- [ ] 57.04 OWASP Testing Guide (OTG) — Web Application
- [ ] 57.05 OWASP ASVS (Application Security Verification Standard)
- [ ] 57.06 OWASP SAMM (Software Assurance Maturity Model)
- [ ] 57.07 OWASP WSTG — Testing Checklist
- [ ] 57.08 OWASP Cheat Sheet Series — Key Sheets
- [ ] 57.09 OWASP Dependency-Check
- [ ] 57.10 OWASP ModSecurity CRS — WAF Rules
- [ ] 57.11 OWASP ZAP — Full Configuration Guide
- [ ] 57.12 NIST Cybersecurity Framework
- [ ] 57.13 PCI DSS — Payment Card Security Requirements
- [ ] 57.14 GDPR Security Requirements for Developers
- [ ] 57.15 ISO 27001 — Information Security Management

---

## MODULE 58 — Advanced Web Techniques (25)

- [ ] 58.01 HTTP Parameter Pollution (HPP) — Deep Dive
- [ ] 58.02 Mass Assignment — Rails, Laravel, Spring, Django
- [ ] 58.03 Dangling Markup Injection
- [ ] 58.04 CSS Injection — Exfiltrating Data via CSS
- [ ] 58.05 Browser Cache Attacks
- [ ] 58.06 Relative Path Overwrite (RPO)
- [ ] 58.07 URL Confusion — Parser Differential Attacks
- [ ] 58.08 Origin Header Spoofing
- [ ] 58.09 Host Override via Forwarded Headers
- [ ] 58.10 HTTP/2 Specific Attacks (Rapid Reset, h2c Upgrade)
- [ ] 58.11 Compression Side-Channel (BREACH, TIME)
- [ ] 58.12 Timing Attacks — Remote Timing Analysis
- [ ] 58.13 Race Condition — TOCTOU (Time-of-Check Time-of-Use)
- [ ] 58.14 Insecure Randomness in Web Context
- [ ] 58.15 Account Takeover via Email Domain Takeover
- [ ] 58.16 HTTP Response Splitting
- [ ] 58.17 Unicode Normalization Attacks
- [ ] 58.18 Homograph Attacks (IDN — International Domain Names)
- [ ] 58.19 Browser Fingerprinting — Detection and Evasion
- [ ] 58.20 Postmessage Vulnerabilities (XSS via postMessage)
- [ ] 58.21 Reverse Tabnapping
- [ ] 58.22 DNS Rebinding — Deep Dive
- [ ] 58.23 Cross-Window Messaging Attacks
- [ ] 58.24 Service Worker Attacks (Cache Poisoning, XSS Storage)
- [ ] 58.25 Abuse of Browser APIs (CORS, Fetch, XMLHttpRequest)

---

## MODULE 59 — Complete Tools Reference (80)

### Reconnaissance
- [ ] 59.01 Amass — Full Config and Usage
- [ ] 59.02 Subfinder — Config, Sources, API Keys
- [ ] 59.03 Assetfinder — Lightweight Subdomain Discovery
- [ ] 59.04 theHarvester — Full Usage Guide
- [ ] 59.05 Recon-ng — Modular OSINT Framework
- [ ] 59.06 Maltego — Visual OSINT and Link Analysis
- [ ] 59.07 Shodan — Web and CLI Complete Guide
- [ ] 59.08 Censys — Search Syntax and API
- [ ] 59.09 FOFA — Chinese IoT Search Engine
- [ ] 59.10 Zoomeye — Alternative to Shodan
- [ ] 59.11 crt.sh — Certificate Transparency Query
- [ ] 59.12 dnsx — DNS Bulk Resolution and Probing
- [ ] 59.13 shuffledns — DNS Bruteforcing at Scale
- [ ] 59.14 puredns — Fast DNS Resolver with Wildcard Filtering
- [ ] 59.15 httpx — HTTP Probing at Scale

### Web Application Testing
- [ ] 59.16 Burp Suite Pro — Complete Feature Reference
- [ ] 59.17 Burp Extensions (Active Scan++, Autorize, JWT Editor, Turbo Intruder)
- [ ] 59.18 OWASP ZAP — Full Scan Modes and API
- [ ] 59.19 ffuf — Advanced Usage (recursion, rate limiting, filters)
- [ ] 59.20 Gobuster — DNS, Dir, VHost modes
- [ ] 59.21 Feroxbuster — Recursive with Smart Filtering
- [ ] 59.22 Katana — Web Crawler by Project Discovery
- [ ] 59.23 Hakrawler — Fast Web Crawler
- [ ] 59.24 gau — GetAllUrls from Wayback and OTX
- [ ] 59.25 waybackurls — Wayback Machine URL Fetcher
- [ ] 59.26 arjun — Parameter Discovery
- [ ] 59.27 x8 — Hidden Parameter Discovery
- [ ] 59.28 ParamSpider — Parameter Mining from Web Archives
- [ ] 59.29 Nikto — Full Config and Output Interpretation
- [ ] 59.30 Nuclei — Writing Custom Templates

### Exploitation
- [ ] 59.31 sqlmap — Full Flag Reference and Tamper Scripts
- [ ] 59.32 XSStrike — XSS Fuzzer and Exploit
- [ ] 59.33 dalfox — XSS Scanner (DOM-aware)
- [ ] 59.34 SSTImap — SSTI Scanner and Exploiter
- [ ] 59.35 tplmap — Template Injection Tester
- [ ] 59.36 Commix — Command Injection Exploiter
- [ ] 59.37 corsy — CORS Scanner
- [ ] 59.38 CORStest — CORS Misconfiguration Tester
- [ ] 59.39 smuggler.py — HTTP Request Smuggling Detector
- [ ] 59.40 h2csmuggler — HTTP/2 Cleartext Smuggling
- [ ] 59.41 jwt_tool — JWT Attack Toolkit (Full Reference)
- [ ] 59.42 ysoserial — Java Deserialization Payload Generator
- [ ] 59.43 PHPGGC — PHP Gadget Chain Generator
- [ ] 59.44 noSQLmap — NoSQL Injection Tool

### Network and Infrastructure
- [ ] 59.45 Nmap — NSE Scripts Reference
- [ ] 59.46 Masscan — High-Speed Port Scanner
- [ ] 59.47 Rustscan — Fast Pre-Scanner for Nmap
- [ ] 59.48 Metasploit — Auxiliary, Exploits, Post Modules
- [ ] 59.49 Msfvenom — Payload Generation Reference
- [ ] 59.50 Hydra — All Protocols Reference
- [ ] 59.51 Medusa — Parallel Login Brute Forcer
- [ ] 59.52 Netcat (nc / ncat) — Swiss Army Knife
- [ ] 59.53 Socat — Advanced Netcat Replacement
- [ ] 59.54 Chisel — TCP Tunneling over HTTP
- [ ] 59.55 Ligolo-ng — Layer 3 Pivot Tool
- [ ] 59.56 proxychains — SOCKS Proxy Chaining

### Active Directory
- [ ] 59.57 BloodHound — Complete Usage and Query Reference
- [ ] 59.58 SharpHound — Data Collection for BloodHound
- [ ] 59.59 Impacket — All Scripts (secretsdump, psexec, wmiexec, GetUserSPNs, ASREPRoast)
- [ ] 59.60 CrackMapExec / NetExec — Full Command Reference
- [ ] 59.61 Responder — All Modes and Config
- [ ] 59.62 Mimikatz — All Modules (sekurlsa, lsadump, kerberos, token)
- [ ] 59.63 Rubeus — Kerberos Attack Toolkit
- [ ] 59.64 PowerView — AD Enumeration PowerShell
- [ ] 59.65 evil-winrm — WinRM Shell
- [ ] 59.66 enum4linux-ng — SMB/LDAP Enumeration

### Password Cracking
- [ ] 59.67 Hashcat — Complete Mode and Hash Type Reference
- [ ] 59.68 John the Ripper — Rules and Wordlist Generation
- [ ] 59.69 CeWL — Custom Wordlist Generator
- [ ] 59.70 crunch — Wordlist Generator by Pattern
- [ ] 59.71 Mentalist — GUI Wordlist Builder
- [ ] 59.72 rockyou.txt and Common Wordlists Reference

### Cloud and Container
- [ ] 59.73 ScoutSuite — Multi-Cloud Security Auditor
- [ ] 59.74 Prowler — AWS/GCP/Azure Security Checks
- [ ] 59.75 CloudFox — Cloud Pentesting Tool
- [ ] 59.76 Pacu — AWS Exploitation Framework
- [ ] 59.77 aws-cli — Pentester's Command Reference
- [ ] 59.78 trivy — Container and IaC Vulnerability Scanner
- [ ] 59.79 kube-hunter — Kubernetes Vulnerability Scanner
- [ ] 59.80 kubectl — Security-Relevant Commands for Pentesters

---

## MODULE 60 — Advanced Chaining and Real-World Scenarios (30)

- [ ] 60.01 Real Bug Bounty Report Analysis — Critical SQLi
- [ ] 60.02 Real Bug Bounty Report Analysis — Account Takeover Chain
- [ ] 60.03 Real Bug Bounty Report Analysis — SSRF to RCE
- [ ] 60.04 Real Bug Bounty Report Analysis — Subdomain Takeover
- [ ] 60.05 Real Bug Bounty Report Analysis — XXE in XML API
- [ ] 60.06 HackerOne Disclosed Reports — Top 10 Most Educational
- [ ] 60.07 Facebook Bug — SSRF via Profile Picture
- [ ] 60.08 Twitter Bug — XSS in OAuth Flow
- [ ] 60.09 Shopify Bug — IDOR on Admin Panel
- [ ] 60.10 Uber Bug — SQLi via Subdomain
- [ ] 60.11 Chain: Recon → GitHub Secret → AWS Access → S3 Dump → RDS Creds → DB Admin
- [ ] 60.12 Chain: Phishing → Creds → VPN → Internal Network → AD → Domain Admin
- [ ] 60.13 Chain: XSS → Steal Admin Cookie → IDOR → Mass Export PII
- [ ] 60.14 Chain: Deserialization → RCE → Pivot → Cloud Metadata → IAM Takeover
- [ ] 60.15 Chain: GraphQL Introspection → Hidden Mutation → Account Takeover → Admin
- [ ] 60.16 Chain: Race Condition → Coupon Reuse → Financial Loss at Scale
- [ ] 60.17 Chain: CORS → CSRF → Password Change → Full ATO
- [ ] 60.18 Chain: Open Redirect → Phishing → OAuth Token → API Takeover
- [ ] 60.19 Chain: Path Traversal → /etc/passwd → SSH Brute Force → Shell
- [ ] 60.20 Chain: HTTP Smuggling → Capture Admin Request → CSRF → Privilege Escalation
- [ ] 60.21 Full Web App Pentest Simulation (E-commerce target)
- [ ] 60.22 Full API Pentest Simulation (REST API target)
- [ ] 60.23 Full Cloud Infrastructure Pentest Simulation (AWS target)
- [ ] 60.24 Full Internal Network Pentest Simulation (Corp LAN target)
- [ ] 60.25 Full Active Directory Pentest Simulation (Domain target)
- [ ] 60.26 CTF Challenge Walkthroughs — Web Category
- [ ] 60.27 CTF Challenge Walkthroughs — Crypto Category
- [ ] 60.28 HackTheBox Machine Walkthroughs — Methodology
- [ ] 60.29 TryHackMe Learning Path Mapping
- [ ] 60.30 Building a Home Lab for VAPT Practice

---

## UPDATED GRAND TOTAL

| Module | Topics |
|--------|--------|
| 01–42 (original modules) | 776 |
| 43 Windows PrivEsc | 40 |
| 44 Linux PrivEsc | 35 |
| 45 Post-Exploitation and Persistence | 30 |
| 46 Social Engineering and Phishing | 20 |
| 47 Mobile Application Security | 30 |
| 48 Wireless Security | 20 |
| 49 IoT Security | 20 |
| 50 Thick Client Security | 15 |
| 51 Source Code Review / SAST | 20 |
| 52 Dynamic Analysis / DAST | 15 |
| 53 Supply Chain Security | 15 |
| 54 Exploit Development Basics | 20 |
| 55 Threat Intelligence and CVEs | 15 |
| 56 Defensive Security and Hardening | 25 |
| 57 OWASP Frameworks and Standards | 15 |
| 58 Advanced Web Techniques | 25 |
| 59 Complete Tools Reference | 80 |
| 60 Advanced Chaining and Real-World | 30 |
| **GRAND TOTAL** | **1246** |

---

## Related Files
- [[VAPT-Plan2-PortSwigger]] — all 278 PortSwigger labs with individual names and difficulty
- [[VAPT-Vault-Spec]] — project decisions
- [[00 - Learning Path]] — master index
