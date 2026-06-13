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

- [x] 11.01 What is CSRF?
- [x] 11.02 Same-Origin Policy and CSRF
- [x] 11.03 CSRF via GET Request
- [x] 11.04 CSRF via POST Request
- [x] 11.05 CSRF Token Bypass Techniques
- [x] 11.06 SameSite Cookie Bypass
- [x] 11.07 CSRF via CORS Misconfiguration
- [x] 11.08 CSRF via JSON (Content-Type tricks)
- [x] 11.09 CSRF to Account Takeover
- [x] 11.10 Defense — tokens, SameSite, double-submit cookie

---

## MODULE 12 — CORS (12) *(PS: 4 labs)*

- [x] 12.01 What is CORS and Why It Exists
- [x] 12.02 Simple vs Preflight Requests
- [x] 12.03 CORS Headers — Full Reference
- [x] 12.04 Origin Reflection Misconfiguration
- [x] 12.05 Null Origin Misconfiguration
- [x] 12.06 Wildcard with Credentials
- [x] 12.07 Subdomain Trust
- [x] 12.08 Regex Bypass (evil.com matching .com)
- [x] 12.09 CORS to Credential Theft
- [x] 12.10 CORS to Account Takeover Chain
- [x] 12.11 Detecting CORS Misconfigurations (CORScanner, manual)
- [x] 12.12 Defense — Strict Origin Whitelisting

---

## MODULE 13 — SSRF (20) *(PS: 7 labs)*

- [x] 13.01 What is SSRF?
- [x] 13.02 Basic SSRF — Fetching Internal URLs
- [x] 13.03 SSRF via URL Parameters
- [x] 13.04 SSRF via HTTP Headers (Host, Referer, X-Forwarded-For)
- [x] 13.05 SSRF via File Imports (PDF, webhooks, image fetchers)
- [x] 13.06 SSRF via XML (XXE chained)
- [x] 13.07 Blind SSRF (Burp Collaborator / interactsh)
- [x] 13.08 Semi-Blind SSRF (timing-based)
- [x] 13.09 SSRF — Cloud Metadata (AWS 169.254.169.254, GCP, Azure)
- [x] 13.10 SSRF — AWS IMDSv1 vs IMDSv2
- [x] 13.11 SSRF — Internal Port Scanning
- [x] 13.12 SSRF — Internal Services (Redis, Elasticsearch, Memcached)
- [x] 13.13 SSRF — Protocol Smuggling (file://, gopher://, dict://, ftp://)
- [x] 13.14 SSRF — Localhost Bypass (127.0.0.1, [::1], 0.0.0.0, 2130706433)
- [x] 13.15 SSRF — DNS Rebinding
- [x] 13.16 SSRF — URL Parser Confusion
- [x] 13.17 SSRF WAF Bypass
- [x] 13.18 SSRF to RCE via Internal Services
- [x] 13.19 SSRF to Cloud Credential Theft → Full Takeover
- [x] 13.20 Defense — Allowlists, IMDSv2, Network Segmentation

---

## MODULE 14 — XXE (10) *(PS: 9 labs)*

- [x] 14.01 What is XXE?
- [x] 14.02 XML Basics and DTD
- [x] 14.03 Classic XXE — File Read (/etc/passwd)
- [x] 14.04 XXE via SVG Upload
- [x] 14.05 XXE via XLSX / DOCX
- [x] 14.06 Blind XXE — OOB Data Exfiltration
- [x] 14.07 XXE via XInclude
- [x] 14.08 XXE to SSRF
- [x] 14.09 XXE WAF Bypass (encoding, whitespace)
- [x] 14.10 Defense — Disable External Entity Processing

---

## MODULE 15 — Insecure Deserialization (12) *(PS: 10 labs)*

- [x] 15.01 What is Serialization and Deserialization?
- [x] 15.02 Java Deserialization (ysoserial)
- [x] 15.03 PHP Object Injection
- [x] 15.04 Python Pickle Deserialization
- [x] 15.05 .NET Deserialization (BinaryFormatter, ViewState)
- [x] 15.06 Ruby Deserialization
- [x] 15.07 Node.js Deserialization (node-serialize)
- [x] 15.08 JSON Deserialization Type Confusion
- [x] 15.09 YAML Deserialization
- [x] 15.10 XML Deserialization
- [x] 15.11 Magic Methods Abuse (__wakeup, __destruct, readObject)
- [x] 15.12 Defense — Avoid Untrusted Deserialization, Use Safe Formats

---

## MODULE 16 — Authentication Attacks (28) *(PS: 14 labs)*

- [x] 16.01 Username Enumeration (error messages, timing)
- [x] 16.02 Password Brute Force
- [x] 16.03 Credential Stuffing
- [x] 16.04 Password Spraying
- [x] 16.05 Default Credentials
- [x] 16.06 Weak Password Policies
- [x] 16.07 Forgot Password — Token Predictability
- [x] 16.08 Forgot Password — Host Header Poisoning
- [x] 16.09 Forgot Password — Token Reuse
- [x] 16.10 Account Lockout Bypass
- [x] 16.11 MFA Bypass — Response Manipulation
- [x] 16.12 MFA Bypass — Code Reuse
- [x] 16.13 MFA Bypass — Brute Force OTP
- [x] 16.14 MFA Bypass — Backup Code Abuse
- [x] 16.15 MFA Bypass — SIM Swapping
- [x] 16.16 Login CSRF
- [x] 16.17 Basic Auth Cracking
- [x] 16.18 HTTP Digest Auth Attacks
- [x] 16.19 NTLM Authentication Attacks
- [x] 16.20 OAuth Login CSRF
- [x] 16.21 Magic Link Vulnerabilities
- [x] 16.22 SSO Bypass (SAML, OAuth)
- [x] 16.23 Pre-Authentication SQLi
- [x] 16.24 Username/Password in URL
- [x] 16.25 Autocomplete on Sensitive Fields
- [x] 16.26 Verbose Error Messages
- [x] 16.27 Client-Side Auth Bypass (JavaScript checks)
- [x] 16.28 Defense — Rate Limiting, Lockout, MFA, Secure Password Storage

---

## MODULE 17 — Session Management (15) *(PS: Authentication labs)*

- [x] 17.01 What is a Session?
- [x] 17.02 Session Token Entropy and Predictability
- [x] 17.03 Session Fixation
- [x] 17.04 Session Hijacking via Cookie Theft (XSS)
- [x] 17.05 Session Hijacking via Network Sniffing
- [x] 17.06 Session Puzzle / Session Confusion
- [x] 17.07 Insecure Session Storage (localStorage, URL params)
- [x] 17.08 Session Not Invalidated on Logout
- [x] 17.09 Long-Lived Sessions
- [x] 17.10 Concurrent Session Not Invalidated
- [x] 17.11 Cookie Flags — Attack Scenarios
- [x] 17.12 Cookie Scope Abuse (Domain and Path)
- [x] 17.13 Cookie Tossing
- [x] 17.14 Client-Side Session Tokens (JWT, Signed Cookies)
- [x] 17.15 Defense — Secure Session Configuration

---

## MODULE 18 — JWT Attacks (18) *(PS: 8 labs)*

- [x] 18.01 What is a JWT?
- [x] 18.02 JWT Structure (Header.Payload.Signature)
- [x] 18.03 JWT Claims Reference (iss, sub, aud, exp, nbf, iat, jti)
- [x] 18.04 Algorithm None Attack
- [x] 18.05 RS256 to HS256 Algorithm Confusion
- [x] 18.06 Weak Secret Brute Force (hashcat, jwt_tool)
- [x] 18.07 JWT Header Injection — jwk claim
- [x] 18.08 JWT Header Injection — jku claim
- [x] 18.09 JWT Header Injection — kid claim (SQLi, path traversal)
- [x] 18.10 JWT Expiry Manipulation (exp claim)
- [x] 18.11 JWT Replay Attack
- [x] 18.12 JWT Substitution Attack (swapping tokens between users)
- [x] 18.13 JWT in Cookies vs Authorization Header
- [x] 18.14 JWT Cracking with jwt_tool
- [x] 18.15 JWT Cracking with hashcat
- [x] 18.16 Refresh Token Attacks
- [x] 18.17 JWT Confusion in Multi-Tenant Apps
- [x] 18.18 Defense — Strong Algorithms, Validation, Short Expiry

---

## MODULE 19 — OAuth 2.0 Attacks (20) *(PS: 6 labs)*

- [x] 19.01 OAuth 2.0 Overview and Flow Types
- [x] 19.02 Authorization Code Flow — Step by Step
- [x] 19.03 Implicit Flow (deprecated) — Vulnerabilities
- [x] 19.04 Client Credentials Flow
- [x] 19.05 PKCE — What It Protects Against
- [x] 19.06 OAuth State Parameter — CSRF in OAuth
- [x] 19.07 Redirect URI Manipulation
- [x] 19.08 Open Redirect in Redirect URI
- [x] 19.09 Authorization Code Interception
- [x] 19.10 Token Leakage via Referer Header
- [x] 19.11 Token Leakage via Browser History
- [x] 19.12 Account Linking Abuse
- [x] 19.13 Scope Escalation
- [x] 19.14 Token Replay Attack
- [x] 19.15 Client Secret Exposure
- [x] 19.16 OAuth Misconfig — Wildcard Redirect URI
- [x] 19.17 OAuth Misconfig — Lack of State Validation
- [x] 19.18 OAuth to Account Takeover Chain
- [x] 19.19 OpenID Connect (OIDC) Attack Surface
- [x] 19.20 Defense — Strict Redirect URI, PKCE, State Validation

---

## MODULE 20 — SAML Attacks (10)

- [x] 20.01 What is SAML and How SSO Works
- [x] 20.02 SAML Assertion Structure
- [x] 20.03 XML Signature Wrapping (XSW) Attacks
- [x] 20.04 SAML Replay Attack
- [x] 20.05 SAML Attribute Manipulation
- [x] 20.06 SAML Comment Injection
- [x] 20.07 SAML External Entity (SAML + XXE)
- [x] 20.08 SAML Signature Bypass (none algorithm)
- [x] 20.09 SAML to Account Takeover
- [x] 20.10 Defense — Strict Schema Validation, Signed Assertions

---

## MODULE 21 — Access Control (20) *(PS: 13 labs)*

- [x] 21.01 Vertical Privilege Escalation
- [x] 21.02 Horizontal Privilege Escalation
- [x] 21.03 IDOR — Insecure Direct Object Reference
- [x] 21.04 IDOR in URL Parameters
- [x] 21.05 IDOR in POST Body
- [x] 21.06 IDOR in Cookies
- [x] 21.07 IDOR in HTTP Headers
- [x] 21.08 Mass Assignment Vulnerability
- [x] 21.09 BOLA — Broken Object Level Authorization (OWASP API #1)
- [x] 21.10 BFLA — Broken Function Level Authorization (OWASP API #5)
- [x] 21.11 Forced Browsing / Unprotected Admin Endpoints
- [x] 21.12 Parameter Tampering (role=admin, isAdmin=true)
- [x] 21.13 HTTP Method Bypass (GET vs POST vs PUT)
- [x] 21.14 Path Traversal to Bypass Access Controls
- [x] 21.15 IDOR via API Versioning
- [x] 21.16 GraphQL Authorization Bypass
- [x] 21.17 JWT Claim Manipulation for Privilege Escalation
- [x] 21.18 Account Takeover via IDOR on Password Reset
- [x] 21.19 Referrer-Based Access Control Bypass
- [x] 21.20 Defense — Server-Side Authorization, Object-Level Checks

---

## MODULE 22 — File Upload (15) *(PS: 7 labs)*

- [x] 22.01 What Makes File Upload Dangerous
- [x] 22.02 Unrestricted File Upload — Webshell Upload
- [x] 22.03 Content-Type Bypass
- [x] 22.04 Extension Bypass (.php5, .phtml, .phar, .shtml)
- [x] 22.05 Double Extension (file.php.jpg)
- [x] 22.06 Null Byte Injection (file.php%00.jpg)
- [x] 22.07 File Upload + Path Traversal
- [x] 22.08 File Upload + SSRF (SVG with SSRF payload)
- [x] 22.09 File Upload + XSS (SVG with XSS payload)
- [x] 22.10 File Upload + XXE (malicious DOCX/XLSX)
- [x] 22.11 ZIP Slip (malicious ZIP with path traversal)
- [x] 22.12 Image Upload Magic Bytes Bypass
- [x] 22.13 Uploading Server-Side Scripts (JSP, ASP, ASPX)
- [x] 22.14 Overwriting Existing Files
- [x] 22.15 Defense — Extension Allowlists, Content Validation, Separate Storage

---

## MODULE 23 — Path Traversal and LFI/RFI (12) *(PS: 6 labs)*

- [x] 23.01 What is Path Traversal?
- [x] 23.02 Basic Path Traversal (../../../etc/passwd)
- [x] 23.03 Encoding Bypass for Path Traversal
- [x] 23.04 Null Byte Path Traversal
- [x] 23.05 Local File Inclusion (LFI)
- [x] 23.06 LFI via PHP Wrappers (php://filter, php://input, data://)
- [x] 23.07 LFI to RCE via Log Poisoning
- [x] 23.08 LFI to RCE via /proc/self/environ
- [x] 23.09 LFI to RCE via PHP Session File
- [x] 23.10 Remote File Inclusion (RFI)
- [x] 23.11 Path Traversal in API Parameters
- [x] 23.12 Defense — Canonicalization, Allowlists, Chroot

---

## MODULE 24 — Open Redirect (8)

- [x] 24.01 What is Open Redirect?
- [x] 24.02 Open Redirect in redirect= and url= Parameters
- [x] 24.03 Bypass Techniques (//evil.com, /\evil.com, ///evil.com)
- [x] 24.04 Open Redirect via Referer Header
- [x] 24.05 Open Redirect to Phishing
- [x] 24.06 Open Redirect + OAuth (token stealing)
- [x] 24.07 Open Redirect + SSRF (chained)
- [x] 24.08 Defense — Allowlist of Redirect Destinations

---

## MODULE 25 — Business Logic (18) *(PS: 12 Business Logic + 6 Race Conditions = 18 labs)*

- [x] 25.01 What are Business Logic Flaws?
- [x] 25.02 Price Manipulation in E-commerce
- [x] 25.03 Quantity Manipulation (negative quantities)
- [x] 25.04 Discount/Coupon Abuse
- [x] 25.05 Free Trial Abuse
- [x] 25.06 Account Limit Bypass
- [x] 25.07 Workflow Bypass (skipping payment step)
- [x] 25.08 Order Manipulation After Checkout
- [x] 25.09 Race Conditions in Financial Transactions
- [x] 25.10 Double Submit / Double Spend
- [x] 25.11 Referral Abuse / Self-Referral
- [x] 25.12 Rate Limit Bypass for Votes / Likes
- [x] 25.13 Function-Level Access Control Bypass
- [x] 25.14 Exploiting Trust Between Microservices
- [x] 25.15 Hidden API Parameters
- [x] 25.16 Email Verification Bypass
- [x] 25.17 Phone Number Verification Bypass
- [x] 25.18 Defense — State Machine Validation, Server-Side Checks

---

## MODULE 26 — HTTP Request Smuggling (12) *(PS: 22 labs)*

- [x] 26.01 What is HTTP Request Smuggling?
- [x] 26.02 CL.TE Smuggling
- [x] 26.03 TE.CL Smuggling
- [x] 26.04 TE.TE Smuggling (obfuscated TE headers)
- [x] 26.05 HTTP/2 Request Smuggling (H2.CL, H2.TE)
- [x] 26.06 Response Queue Poisoning
- [x] 26.07 Smuggling to Bypass Front-End Controls
- [x] 26.08 Smuggling to Capture Other Users' Requests
- [x] 26.09 Smuggling to Deliver XSS
- [x] 26.10 Smuggling to Escalate SSRF
- [x] 26.11 Detecting Smuggling (timing, differential responses)
- [x] 26.12 Defense — Normalize Requests at Proxy, Disable TE

---

## MODULE 27 — Web Cache Poisoning and Deception (10) *(PS: 13 Cache Poisoning + 5 Cache Deception = 18 labs)*

- [x] 27.01 What is Web Caching?
- [x] 27.02 Cache Keys and Unkeyed Inputs
- [x] 27.03 Cache Poisoning via X-Forwarded-Host
- [x] 27.04 Cache Poisoning via X-Forwarded-Scheme
- [x] 27.05 Cache Poisoning via Unkeyed Headers
- [x] 27.06 Cache Poisoning via Fat GET
- [x] 27.07 Cache Poisoning to Deliver XSS
- [x] 27.08 Cache Poisoning to Redirect Users
- [x] 27.09 Web Cache Deception Attack
- [x] 27.10 Defense — Cache Key Configuration, Vary Header

---

## MODULE 28 — Clickjacking (6) *(PS: 5 labs)*

- [x] 28.01 What is Clickjacking?
- [x] 28.02 Basic iframe Clickjacking
- [x] 28.03 Multistep Clickjacking
- [x] 28.04 Drag and Drop Clickjacking
- [x] 28.05 Clickjacking + CSRF Chain
- [x] 28.06 Defense — X-Frame-Options, CSP frame-ancestors

---

## MODULE 29 — WebSockets Security (10) *(PS: 3 labs)*

- [x] 29.01 WebSocket Protocol — How It Works
- [x] 29.02 WebSocket Upgrade Security Implications
- [x] 29.03 Cross-Site WebSocket Hijacking (CSWSH)
- [x] 29.04 WebSocket Message Manipulation
- [x] 29.05 WebSocket XSS
- [x] 29.06 WebSocket SQLi
- [x] 29.07 WebSocket Command Injection
- [x] 29.08 WebSocket DoS
- [x] 29.09 Lack of Authentication on WebSocket Endpoints
- [x] 29.10 Defense — Origin Check, Authentication per Message

---

## MODULE 30 — GraphQL Security (18) *(PS: 5 labs)*

- [x] 30.01 What is GraphQL?
- [x] 30.02 GraphQL vs REST — Attack Surface Differences
- [x] 30.03 Introspection Query — Information Disclosure
- [x] 30.04 GraphQL Enumeration (clairvoyance, graphql-cop)
- [x] 30.05 GraphQL Injection
- [x] 30.06 GraphQL Batching Attacks (brute force via batching)
- [x] 30.07 GraphQL Alias-Based Rate Limit Bypass
- [x] 30.08 GraphQL IDOR
- [x] 30.09 GraphQL Mutations — Unauthorized Write Operations
- [x] 30.10 GraphQL Subscriptions Abuse
- [x] 30.11 GraphQL Depth and Complexity DoS
- [x] 30.12 GraphQL SSRF via Directives
- [x] 30.13 GraphQL Upload Vulnerabilities
- [x] 30.14 GraphQL Authorization Bypass
- [x] 30.15 Broken Access Control in Nested Queries
- [x] 30.16 GraphQL Type Confusion
- [x] 30.17 GraphQL Endpoint Discovery
- [x] 30.18 Defense — Disable Introspection in Production, Query Depth Limits

---

## MODULE 31 — API Security — OWASP API Top 10 (25) *(PS: 5 API + 4 LLM = 9 labs)*

- [x] 31.01 API1 — Broken Object Level Authorization (BOLA)
- [x] 31.02 API2 — Broken Authentication
- [x] 31.03 API3 — Broken Object Property Level Authorization
- [x] 31.04 API4 — Unrestricted Resource Consumption
- [x] 31.05 API5 — Broken Function Level Authorization (BFLA)
- [x] 31.06 API6 — Unrestricted Access to Sensitive Business Flows
- [x] 31.07 API7 — Server Side Request Forgery (SSRF)
- [x] 31.08 API8 — Security Misconfiguration
- [x] 31.09 API9 — Improper Inventory Management
- [x] 31.10 API10 — Unsafe Consumption of APIs
- [x] 31.11 API Key Exposure in Source Code / JS Files
- [x] 31.12 API Key in URL Parameters (logged in access logs)
- [x] 31.13 API Versioning Abuse (v1 vs v2)
- [x] 31.14 Mass Assignment in REST APIs
- [x] 31.15 Excessive Data Exposure
- [x] 31.16 Lack of Resource Rate Limiting
- [x] 31.17 API Fuzzing with ffuf and Burp
- [x] 31.18 API Documentation Discovery (Swagger, OpenAPI, WADL)
- [x] 31.19 REST API Method Override Attacks
- [x] 31.20 API Token Leakage in Logs
- [x] 31.21 API Key Rotation Failures
- [x] 31.22 Unauthenticated API Endpoints
- [x] 31.23 SOAP API Attacks (SOAPAction manipulation, WSDL scraping)
- [x] 31.24 gRPC Security Testing
- [x] 31.25 Web LLM Attacks (prompt injection, indirect prompt injection, data exfil)

---

## MODULE 32 — Cryptography Vulnerabilities (15)

- [x] 32.01 Weak Hashing Algorithms (MD5, SHA1 for passwords)
- [x] 32.02 Rainbow Table Attacks
- [x] 32.03 Unsalted Password Hashes
- [x] 32.04 ECB Mode Encryption — Block Boundary Manipulation
- [x] 32.05 CBC Padding Oracle Attack
- [x] 32.06 Predictable IVs and Nonces
- [x] 32.07 Insecure Random Number Generation
- [x] 32.08 Hardcoded Secrets in Code
- [x] 32.09 Weak TLS Configuration (SSLv3, TLS 1.0, RC4, DES)
- [x] 32.10 Certificate Validation Bypass
- [x] 32.11 BEAST Attack
- [x] 32.12 BREACH Attack (compression + secret)
- [x] 32.13 CRIME Attack (compression of cookies over TLS)
- [x] 32.14 Diffie-Hellman Weak Parameters (Logjam)
- [x] 32.15 Defense — Strong Algorithms, Key Management, TLS Best Practices

---

## MODULE 33 — Information Disclosure (12) *(PS: 5 labs)*

- [x] 33.01 Verbose Error Messages
- [x] 33.02 Stack Traces in Responses
- [x] 33.03 Debug Endpoints (/debug, /actuator, /console)
- [x] 33.04 Source Code Disclosure
- [x] 33.05 .git Directory Exposed
- [x] 33.06 .env File Exposed
- [x] 33.07 Backup Files Exposed (.bak, .old, .swp)
- [x] 33.08 Version Disclosure (Server, X-Powered-By)
- [x] 33.09 Internal IP Disclosure in Headers
- [x] 33.10 Comment Disclosure in HTML Source
- [x] 33.11 API Response Over-Exposure
- [x] 33.12 Defense — Error Handling, Remove Debug Info

---

## MODULE 34 — Subdomain Takeover (8)

- [x] 34.01 What is Subdomain Takeover?
- [x] 34.02 CNAME to Unclaimed External Service (GitHub Pages, Heroku, S3)
- [x] 34.03 Fingerprinting Vulnerable Services
- [x] 34.04 Subdomain Takeover — Full Exploit Walkthrough
- [x] 34.05 NS Takeover
- [x] 34.06 MX Takeover (email interception)
- [x] 34.07 Tools — subjack, nuclei, can-i-take-over-xyz
- [x] 34.08 Defense — Remove Dangling DNS Records

---

## MODULE 35 — Network Protocol Attacks (35)

- [x] 35.01 FTP — Anonymous Login, Bounce Attack, Credential Brute Force
- [x] 35.02 SSH — Brute Force, Weak Keys, Version Vulns
- [x] 35.03 Telnet — Cleartext Protocol Attacks
- [x] 35.04 SMTP — Open Relay, User Enumeration (VRFY, EXPN), Spoofing
- [x] 35.05 IMAP/POP3 — Credential Attacks
- [x] 35.06 DNS — Zone Transfer (AXFR), Cache Poisoning, Spoofing
- [x] 35.07 DHCP — Starvation, Rogue DHCP Server
- [x] 35.08 SNMP — Default Community Strings, Information Disclosure
- [x] 35.09 RDP — Brute Force, BlueKeep, DejaBlue
- [x] 35.10 SMB — EternalBlue, Null Session, Relay Attacks
- [x] 35.11 NetBIOS — Enumeration, NBNS Poisoning
- [x] 35.12 LDAP — Anonymous Bind, Enumeration, Injection
- [x] 35.13 Kerberos — Pass-the-Hash, Pass-the-Ticket, Golden/Silver Ticket, Kerberoasting, AS-REP Roasting
- [x] 35.14 NFS — No_Root_Squash Exploitation
- [x] 35.15 MySQL/MSSQL/PostgreSQL — Remote Access, Brute Force, UDF
- [x] 35.16 Redis — Unauthenticated Access, RCE via Config Set
- [x] 35.17 MongoDB — No Auth, Exposed Port
- [x] 35.18 Elasticsearch — Open Access, Data Exfiltration
- [x] 35.19 Memcached — Amplification Attack, Data Dumping
- [x] 35.20 Docker API — Exposed Daemon, Container Escape
- [x] 35.21 Kubernetes API — Unauthenticated Access, RBAC Bypass
- [x] 35.22 etcd — Exposed Key-Value Store
- [x] 35.23 Consul — Service Mesh Misconfig
- [x] 35.24 Zookeeper — Unauthenticated Access
- [x] 35.25 Jenkins — Groovy Script Console, Unauthenticated RCE
- [x] 35.26 GitLab / GitHub — Exposed Tokens, LFI CVEs
- [x] 35.27 Jira / Confluence — Authentication Bypass CVEs
- [x] 35.28 Prometheus / Grafana — Metrics Exposure, Credential Disclosure
- [x] 35.29 VNC — No Authentication, Weak Password
- [x] 35.30 X11 — Exposed Display Server
- [x] 35.31 MSMQ — Unauthenticated Access
- [x] 35.32 MQTT — Unauthenticated Broker
- [x] 35.33 CoAP — IoT Protocol Attacks
- [x] 35.34 SIP / VoIP — Enumeration, Eavesdropping, Toll Fraud
- [x] 35.35 BGP — Route Hijacking (conceptual)

---

## MODULE 36 — Active Directory Attacks (30)

- [x] 36.01 Active Directory Overview (Domain, DC, OU, GPO)
- [x] 36.02 AD Enumeration (BloodHound, ldapdomaindump, enum4linux)
- [x] 36.03 Kerberosable Accounts — SPN Scanning
- [x] 36.04 Kerberoasting — Hash Cracking of Service Accounts
- [x] 36.05 AS-REP Roasting — No Pre-Auth Accounts
- [x] 36.06 Pass the Hash (PtH)
- [x] 36.07 Pass the Ticket (PtT)
- [x] 36.08 Overpass the Hash
- [x] 36.09 Golden Ticket Attack (krbtgt hash)
- [x] 36.10 Silver Ticket Attack (service account hash)
- [x] 36.11 NTLM Relay Attack
- [x] 36.12 SMB Relay
- [x] 36.13 LDAP Relay
- [x] 36.14 LLMNR / NBT-NS Poisoning (Responder)
- [x] 36.15 DCSync Attack
- [x] 36.16 DCShadow Attack
- [x] 36.17 ACL Abuse (GenericAll, WriteDACL, ForceChangePassword)
- [x] 36.18 GPO Abuse
- [x] 36.19 AdminSDHolder Abuse
- [x] 36.20 Mimikatz — Credential Dumping
- [x] 36.21 LSASS Dumping
- [x] 36.22 SAM Hive Extraction
- [x] 36.23 BloodHound — Attack Path Analysis
- [x] 36.24 Domain Privilege Escalation via Trust Relationships
- [x] 36.25 Forest Trust Attacks
- [x] 36.26 PrintNightmare (CVE-2021-34527)
- [x] 36.27 ZeroLogon (CVE-2020-1472)
- [x] 36.28 MS14-068 (Kerberos PAC Vulnerability)
- [x] 36.29 Exchange — ProxyLogon, ProxyShell, ProxyNotShell
- [x] 36.30 Defense — Tiering, Least Privilege, LAPS, Defender for Identity

---

## MODULE 37 — Cloud Infrastructure (35)

### AWS
- [x] 37.01 AWS IAM — Roles, Policies, Misconfigurations
- [x] 37.02 AWS S3 — Public Access, ACL Misconfiguration
- [x] 37.03 AWS EC2 — Metadata Service (IMDS) Exploitation
- [x] 37.04 AWS Lambda — Privilege Escalation, Event Injection
- [x] 37.05 AWS ECS / EKS — Container Privilege Escalation
- [x] 37.06 AWS SecretsManager / Parameter Store — Misconfigured Access
- [x] 37.07 AWS CloudTrail — Disabling Logging
- [x] 37.08 AWS RDS — Publicly Exposed Databases
- [x] 37.09 AWS SQS / SNS — Message Queue Interception
- [x] 37.10 AWS API Gateway — Authorization Bypass
- [x] 37.11 AWS Cognito — Misconfigured User Pools
- [x] 37.12 AWS IAM Privilege Escalation (21 Rhino Security methods)

### GCP
- [x] 37.13 GCP IAM — Service Account Key Abuse
- [x] 37.14 GCP Cloud Storage — Public Bucket Access
- [x] 37.15 GCP Metadata Server — Credential Theft
- [x] 37.16 GCP Cloud Functions — Privilege Escalation
- [x] 37.17 GCP Compute Engine — Default Service Account Abuse

### Azure
- [x] 37.18 Azure AD — Misconfiguration, Privilege Escalation
- [x] 37.19 Azure Blob Storage — Public Access
- [x] 37.20 Azure Function Apps — Exposed Secrets
- [x] 37.21 Azure SSRF via Metadata
- [x] 37.22 Azure Service Principal Abuse
- [x] 37.23 Azure Managed Identity Abuse

### Cross-Cloud
- [x] 37.24 Cloud Metadata Endpoint Cheat Sheet (all providers)
- [x] 37.25 IMDSv2 Bypass Techniques
- [x] 37.26 Cloud Enumeration Tools (ScoutSuite, Prowler, CloudFox)
- [x] 37.27 Cloud SSRF to Credential Theft — Full Chain
- [x] 37.28 Serverless Security Testing
- [x] 37.29 Container Registry Attacks (ECR, GCR, ACR)
- [x] 37.30 Terraform / CloudFormation Misconfigurations
- [x] 37.31 Kubernetes on Cloud — EKS, GKE, AKS
- [x] 37.32 Cloud Storage Mining (secrets in S3/GCS/Blobs)
- [x] 37.33 CI/CD Pipeline Attacks (GitHub Actions, GitLab CI)
- [x] 37.34 Cloud Backdoor via IAM Role
- [x] 37.35 Defense — Least Privilege IAM, IMDSv2, Logging, SCP

---

## MODULE 38 — Container and Kubernetes Security (22)

- [x] 38.01 Docker Overview — Images, Containers, Registries
- [x] 38.02 Docker Daemon Exposed (TCP 2375/2376)
- [x] 38.03 Docker Socket Mount Privilege Escalation
- [x] 38.04 Container Escape — Privileged Container
- [x] 38.05 Container Escape — Mounted Host Filesystem
- [x] 38.06 Container Escape — SYS_PTRACE Capability
- [x] 38.07 Container Escape — Kernel Exploits
- [x] 38.08 Dockerfile Security Misconfigurations
- [x] 38.09 Secrets in Docker Images (layers, ENV vars)
- [x] 38.10 Kubernetes Architecture — Control Plane, Nodes, Pods
- [x] 38.11 Kubernetes RBAC — ClusterAdmin Misconfig
- [x] 38.12 Exposed Kubernetes Dashboard
- [x] 38.13 Kubernetes API Server — Unauthenticated Access
- [x] 38.14 Kubernetes etcd — Direct Access to Secrets
- [x] 38.15 Pod Security — Privileged Pods
- [x] 38.16 HostPath Volume Mount Abuse
- [x] 38.17 Service Account Token Theft
- [x] 38.18 Kubernetes Secret Enumeration
- [x] 38.19 Lateral Movement in K8s (pod to pod)
- [x] 38.20 Admission Controller Bypass
- [x] 38.21 Supply Chain — Malicious Container Images
- [x] 38.22 Defense — Pod Security Admission, Network Policies, RBAC Hardening

---

## MODULE 39 — WAF Bypass Techniques (20)

- [x] 39.01 What is a WAF and How It Works
- [x] 39.02 WAF Fingerprinting (wafw00f, manual)
- [x] 39.03 URL Encoding Bypass
- [x] 39.04 Double URL Encoding
- [x] 39.05 Unicode Normalization Bypass
- [x] 39.06 Case Variation (SeLeCt vs SELECT)
- [x] 39.07 Comment Insertion (SEL/**/ECT)
- [x] 39.08 Whitespace Substitution (tab, newline, vertical tab)
- [x] 39.09 Keyword Splitting and Concatenation
- [x] 39.10 HTTP Parameter Pollution (HPP)
- [x] 39.11 Chunked Transfer Encoding Bypass
- [x] 39.12 Content-Type Switching
- [x] 39.13 JSON/XML Wrapping
- [x] 39.14 Wildcard Bypass (* in SQL)
- [x] 39.15 Out-of-Band Bypass (DNS exfiltration)
- [x] 39.16 IP Rotation
- [x] 39.17 Slowloris and Rate Manipulation
- [x] 39.18 HTTP/2 Cleartext (h2c) Smuggling past WAF
- [x] 39.19 CDN Origin Direct Access (bypassing WAF entirely)
- [x] 39.20 ML-Based WAF Evasion Concepts

---

## MODULE 40 — Vulnerability Chaining Playbook (25)

- [x] 40.01 Recon → Subdomain Takeover → Phishing Campaign
- [x] 40.02 Open Redirect → OAuth Token Theft → Account Takeover
- [x] 40.03 SSRF → Cloud Metadata → IAM Credential Theft → Cloud Takeover
- [x] 40.04 XSS → CSRF → Admin Account Takeover
- [x] 40.05 XSS → Session Hijacking → Privilege Escalation
- [x] 40.06 IDOR → PII Exfiltration → Mass Account Breach
- [x] 40.07 SQLi → File Read → Credentials → RCE
- [x] 40.08 File Upload → Webshell → RCE → Lateral Movement
- [x] 40.09 JWT Algorithm Confusion → Admin JWT → Full App Takeover
- [x] 40.10 CORS Misconfiguration → CSRF → Credential Theft
- [x] 40.11 XXE → SSRF → Internal API Access → Data Exfiltration
- [x] 40.12 Path Traversal → LFI → Log Poisoning → RCE
- [x] 40.13 GraphQL Introspection → Mutation Abuse → Privilege Escalation
- [x] 40.14 Host Header Injection → Password Reset Poisoning → Account Takeover
- [x] 40.15 Mass Assignment → Admin Role → Full App Control
- [x] 40.16 HTTP Smuggling → Cache Poisoning → Stored XSS
- [x] 40.17 Subdomain Takeover → Cookie Theft → Account Takeover
- [x] 40.18 SSTI → RCE → Container Escape → Host Compromise
- [x] 40.19 Recon → Default Creds → Internal Network → AD Compromise
- [x] 40.20 API Key in JS → Cloud Access → S3 Data Exfiltration
- [x] 40.21 OAuth State CSRF → Account Linking → ATO
- [x] 40.22 Race Condition → Double Spend → Financial Fraud
- [x] 40.23 Deserialization → RCE → Persistence via Cron
- [x] 40.24 LDAP Injection → Credential Dump → Lateral Movement
- [x] 40.25 Full Red Team Simulation — Recon to Domain Admin

---

## MODULE 41 — Tools (32)

- [x] 41.01 Burp Suite — Proxy, Scanner, Repeater, Intruder, Decoder, Collaborator
- [x] 41.02 OWASP ZAP — Open Source Alternative
- [x] 41.03 Nmap — Port Scanning, Service Detection, NSE Scripts
- [x] 41.04 Masscan — High-Speed Port Scanner
- [x] 41.05 Rustscan — Fast Nmap Wrapper
- [x] 41.06 ffuf — Web Fuzzer (dirs, params, vhosts)
- [x] 41.07 Gobuster — Directory and DNS Bruteforcer
- [x] 41.08 Feroxbuster — Recursive Content Discovery
- [x] 41.09 sqlmap — Automated SQL Injection
- [x] 41.10 Nikto — Web Vulnerability Scanner
- [x] 41.11 Nuclei — Template-Based Vulnerability Scanner
- [x] 41.12 Metasploit Framework — Exploitation and Post-Exploitation
- [x] 41.13 Hydra — Network Login Brute Forcer
- [x] 41.14 CrackMapExec / NetExec — SMB, LDAP, WinRM Attacks
- [x] 41.15 BloodHound — AD Attack Path Visualizer
- [x] 41.16 Impacket — Python AD Attack Toolkit
- [x] 41.17 Responder — LLMNR/NBT-NS/mDNS Poisoner
- [x] 41.18 Mimikatz — Windows Credential Dumping
- [x] 41.19 jwt_tool — JWT Testing and Exploitation
- [x] 41.20 Hashcat — Password Hash Cracking
- [x] 41.21 John the Ripper — Password Cracking
- [x] 41.22 Amass — Subdomain Enumeration
- [x] 41.23 Subfinder — Fast Subdomain Finder
- [x] 41.24 theHarvester — OSINT Harvesting
- [x] 41.25 Shodan CLI — Command-Line Shodan
- [x] 41.26 Arjun — HTTP Parameter Discovery
- [x] 41.27 WhatWeb / Wappalyzer — Technology Fingerprinting
- [x] 41.28 Wireshark / tcpdump — Packet Analysis
- [x] 41.29 Interactsh / Burp Collaborator — OOB Detection
- [x] 41.30 XSStrike / dalfox — XSS Scanning
- [x] 41.31 ScoutSuite / Prowler — Cloud Security Auditing
- [x] 41.32 LinkFinder / JSParser — JS Endpoint Discovery

---

## MODULE 42 — VAPT Reporting (15)

- [x] 42.01 Why Reporting Matters
- [x] 42.02 VAPT Report Structure (Executive Summary, Scope, Findings, Appendix)
- [x] 42.03 Executive Summary — Writing for Non-Technical Stakeholders
- [x] 42.04 Findings Section — Finding Template
- [x] 42.05 Severity Ratings — Critical, High, Medium, Low, Informational
- [x] 42.06 CVSS v3.1 Scoring — Base, Temporal, Environmental
- [x] 42.07 CVSS Vector String — How to Read and Write
- [x] 42.08 Risk Rating vs CVSS — Differences
- [x] 42.09 Proof of Concept (PoC) — What to Include
- [x] 42.10 Screenshots and Evidence — Best Practices
- [x] 42.11 Remediation Guidance — Writing Actionable Fixes
- [x] 42.12 Attack Narrative — Telling the Story of a Chain
- [x] 42.13 Retesting Methodology
- [x] 42.14 Sample Finding — SQL Injection (fully worked)
- [x] 42.15 Sample Full Report — End-to-End Template

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

- [x] 43.01 Windows PrivEsc Methodology Overview
- [x] 43.02 Enumerating Windows System Info (systeminfo, whoami, net user)
- [x] 43.03 Unquoted Service Paths
- [x] 43.04 Weak Service Permissions (sc.exe, accesschk)
- [x] 43.05 Modifiable Service Binaries
- [x] 43.06 DLL Hijacking
- [x] 43.07 DLL Search Order Abuse
- [x] 43.08 AlwaysInstallElevated — MSI Privilege Escalation
- [x] 43.09 Token Impersonation — SeImpersonatePrivilege
- [x] 43.10 JuicyPotato, RoguePotato, PrintSpoofer
- [x] 43.11 Hot Potato / Sweet Potato / Ghost Potato
- [x] 43.12 UAC Bypass Techniques
- [x] 43.13 Scheduled Task Hijacking
- [x] 43.14 Startup Applications Abuse
- [x] 43.15 Registry Autorun Key Abuse
- [x] 43.16 Stored Credentials — Windows Credential Manager
- [x] 43.17 Stored Credentials — Unattend.xml, web.config, SAM
- [x] 43.18 PowerShell History File (ConsoleHost_history.txt)
- [x] 43.19 DPAPI — Credential Blob Decryption
- [x] 43.20 Pass the Hash on Local Admin
- [x] 43.21 Password in Group Policy Preferences (GPP)
- [x] 43.22 LAPS — Reading Managed Admin Passwords
- [x] 43.23 Abusing SeDebugPrivilege
- [x] 43.24 Abusing SeTakeOwnershipPrivilege
- [x] 43.25 Abusing SeBackupPrivilege / SeRestorePrivilege
- [x] 43.26 Insecure File/Folder Permissions
- [x] 43.27 Kernel Exploits (MS16-032, MS15-051)
- [x] 43.28 Named Pipe Impersonation
- [x] 43.29 COM Object Hijacking
- [x] 43.30 Windows Subsystem for Linux (WSL) Abuse
- [x] 43.31 Credential Dumping — SAM, SYSTEM, SECURITY hives
- [x] 43.32 Volume Shadow Copy Theft
- [x] 43.33 NTDS.dit Extraction
- [x] 43.34 Living off the Land Binaries (LOLBins) — certutil, mshta, regsvr32, rundll32, msiexec
- [x] 43.35 AppLocker and WDAC Bypass
- [x] 43.36 Bypassing PowerShell Execution Policy
- [x] 43.37 AMSI Bypass Techniques
- [x] 43.38 Event Log Clearing and Evasion
- [x] 43.39 Windows Defender Evasion Basics
- [x] 43.40 Defense — Least Privilege, Patch Management, LAPS

---

## MODULE 44 — Linux Privilege Escalation (35)

- [x] 44.01 Linux PrivEsc Methodology Overview
- [x] 44.02 Enumeration Tools (LinPEAS, LinEnum, linux-exploit-suggester)
- [x] 44.03 SUID Binaries Abuse
- [x] 44.04 SGID Binaries Abuse
- [x] 44.05 Capabilities Abuse (cap_setuid, cap_net_raw)
- [x] 44.06 Sudo Misconfigurations (sudo -l, GTFOBins)
- [x] 44.07 Writable /etc/passwd — Adding Root User
- [x] 44.08 Writable /etc/shadow
- [x] 44.09 Cron Job Abuse — Writable Scripts
- [x] 44.10 Cron Job Abuse — PATH Hijacking
- [x] 44.11 PATH Environment Variable Hijacking
- [x] 44.12 LD_PRELOAD Abuse
- [x] 44.13 Shared Library Injection
- [x] 44.14 NFS No_Root_Squash Exploitation
- [x] 44.15 Weak File Permissions on Sensitive Files
- [x] 44.16 Password in Config Files, History, Env Vars
- [x] 44.17 SSH Private Key Reuse
- [x] 44.18 Writeable /etc/hosts
- [x] 44.19 Docker Group Membership
- [x] 44.20 LXC/LXD Group Abuse
- [x] 44.21 Disk Group — Reading Raw Device Files
- [x] 44.22 Wildcard Injection in Cron (tar, rsync, chown)
- [x] 44.23 Kernel Exploits (DirtyCow, PwnKit, Baron Samedit)
- [x] 44.24 PwnKit (CVE-2021-4034) — pkexec PrivEsc
- [x] 44.25 DirtyPipe (CVE-2022-0847) — Kernel 5.8+
- [x] 44.26 Systemd Service File Abuse
- [x] 44.27 D-Bus Interface Misconfigurations
- [x] 44.28 /proc Filesystem Information Leakage
- [x] 44.29 Core Dump Analysis for Credentials
- [x] 44.30 Tmux / Screen Session Hijacking
- [x] 44.31 /tmp Race Conditions (symlink attacks)
- [x] 44.32 Insecure Sudo Rules (NOPASSWD, ALL)
- [x] 44.33 Python / Perl / Ruby Library Hijacking
- [x] 44.34 Logrotate Exploitation
- [x] 44.35 Defense — File Permission Hardening, Sudo Audit, Patch Management

---

## MODULE 45 — Post-Exploitation and Persistence (30)

- [x] 45.01 Post-Exploitation Goals and Phases
- [x] 45.02 Situational Awareness — What to Enumerate First
- [x] 45.03 Data Exfiltration Techniques (DNS, HTTP, ICMP, FTP)
- [x] 45.04 Persistence — Windows (Registry, Scheduled Tasks, Services)
- [x] 45.05 Persistence — Linux (Cron, .bashrc, SSH keys, systemd)
- [x] 45.06 Backdoor Accounts
- [x] 45.07 Web Shell Persistence
- [x] 45.08 Reverse Shell Stability (pty upgrade, socat, rlwrap)
- [x] 45.09 Pivoting — Port Forwarding (SSH, chisel, ligolo)
- [x] 45.10 Pivoting — SOCKS Proxy (proxychains)
- [x] 45.11 Pivoting — Dynamic Port Forwarding
- [x] 45.12 Lateral Movement — WMI (wmic, Invoke-WMIMethod)
- [x] 45.13 Lateral Movement — WinRM (evil-winrm)
- [x] 45.14 Lateral Movement — PsExec, SMBExec
- [x] 45.15 Lateral Movement — RDP Pass-Through
- [x] 45.16 Token Stealing with Incognito / Meterpreter
- [x] 45.17 Credential Dumping — Windows (Mimikatz, Pypykatz)
- [x] 45.18 Credential Dumping — Linux (/etc/shadow, memory)
- [x] 45.19 Browser Credential Extraction (Chrome, Firefox)
- [x] 45.20 Email Client Credential Extraction
- [x] 45.21 SSH Agent Hijacking
- [x] 45.22 LOLBins for Persistence (WMIC, schtasks, reg)
- [x] 45.23 COM Hijacking for Persistence
- [x] 45.24 DLL Side-Loading for Persistence
- [x] 45.25 Rootkits — Concept and Detection
- [x] 45.26 Bootkit — Concept and Detection
- [x] 45.27 Memory-Only Malware (Fileless Malware)
- [x] 45.28 Clearing Tracks — Windows (Event Logs, Prefetch, Shimcache)
- [x] 45.29 Clearing Tracks — Linux (bash_history, wtmp, lastlog)
- [x] 45.30 Defense — EDR, SIEM, Honeytokens, Integrity Monitoring

---

## MODULE 49 — IoT Security (20)

- [x] 49.01 IoT Attack Surface Overview
- [x] 49.02 IoT Device Firmware Extraction
- [x] 49.03 Firmware Analysis and Reverse Engineering (binwalk, strings, Ghidra)
- [x] 49.04 Hardcoded Credentials in Firmware
- [x] 49.05 Telnet/SSH Exposed on IoT Devices
- [x] 49.06 Insecure Update Mechanisms
- [x] 49.07 UART / JTAG Hardware Debugging Interfaces
- [x] 49.08 Serial Console Access
- [x] 49.09 SPI Flash Dumping
- [x] 49.10 Command Injection in IoT Web Interfaces
- [x] 49.11 MQTT — Unauthenticated Broker Exploitation
- [x] 49.12 CoAP Protocol Attacks
- [x] 49.13 Modbus / DNP3 — Industrial Protocol Attacks
- [x] 49.14 Shodan for IoT Device Discovery
- [x] 49.15 Router Exploitation (default creds, CVEs)
- [x] 49.16 IP Camera Exploitation (RTSP, ONVIF, CVEs)
- [x] 49.17 Smart Home Device Attacks (Zigbee, Z-Wave)
- [x] 49.18 Medical Device Security Overview
- [x] 49.19 SCADA / ICS Security Concepts
- [x] 49.20 Defense — Network Segmentation, Firmware Signing, Patch Management

---

## MODULE 55 — Threat Intelligence and CVEs (15)

- [x] 55.01 What is Threat Intelligence?
- [x] 55.02 CVE, CVSS, CWE — Terminology
- [x] 55.03 NVD — National Vulnerability Database
- [x] 55.04 Exploit-DB and Packet Storm — Finding Public Exploits
- [x] 55.05 SearchSploit — Offline Exploit-DB Search
- [x] 55.06 MITRE ATT&CK Framework — Tactics, Techniques, Procedures
- [x] 55.07 MITRE ATT&CK — Mapping Findings to TTPs
- [x] 55.08 Cyber Kill Chain — Lockheed Martin Model
- [x] 55.09 Threat Modeling — STRIDE, PASTA, DREAD
- [x] 55.10 CVE Research — Finding PoCs from GitHub
- [x] 55.11 Vulnerability Disclosure — Responsible Disclosure Process
- [x] 55.12 Bug Bounty Programs — HackerOne, Bugcrowd, Intigriti
- [x] 55.13 Patch Diffing — Finding Vulns from Patches
- [x] 55.14 1-Day vs 0-Day Research Concepts
- [x] 55.15 IOCs — Indicators of Compromise

---

## MODULE 56 — Defensive Security and Hardening (25)

- [x] 56.01 Defense-in-Depth — Layered Security Model
- [x] 56.02 Security Hardening — CIS Benchmarks
- [x] 56.03 Linux Hardening (SSH, firewall, sysctl, AppArmor, SELinux)
- [x] 56.04 Windows Hardening (GPO, Windows Defender, Attack Surface Reduction)
- [x] 56.05 Web Server Hardening (Nginx, Apache — headers, TLS, directory listing)
- [x] 56.06 Database Hardening (MySQL, PostgreSQL — users, permissions, encryption)
- [x] 56.07 Firewall Rules — Allowlist vs Denylist
- [x] 56.08 Network Segmentation and VLANs
- [x] 56.09 Zero Trust Architecture
- [x] 56.10 Intrusion Detection — IDS vs IPS (Snort, Suricata)
- [x] 56.11 SIEM — Concepts, Log Aggregation, Alerting (Splunk, ELK, Wazuh)
- [x] 56.12 SOC Operations — Tier 1/2/3 Overview
- [x] 56.13 Incident Response — PICERL (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned)
- [x] 56.14 Digital Forensics — Evidence Collection, Chain of Custody
- [x] 56.15 Memory Forensics (Volatility)
- [x] 56.16 Disk Forensics (Autopsy, FTK)
- [x] 56.17 Log Analysis for Attack Detection
- [x] 56.18 Honeypots and Honeytokens
- [x] 56.19 Threat Hunting — Hypothesis-Driven Approach
- [x] 56.20 EDR Solutions — CrowdStrike, SentinelOne, Microsoft Defender for Endpoint
- [x] 56.21 Security Monitoring — What to Alert On
- [x] 56.22 Patch Management Strategy
- [x] 56.23 Vulnerability Management Program
- [x] 56.24 Purple Team — Red + Blue Collaboration
- [x] 56.25 Security Maturity Models (CMMI, BSIMM, OpenSAMM)

---

## MODULE 57 — OWASP Frameworks and Standards (15)

- [x] 57.01 OWASP Top 10 2021 — Full Walkthrough
- [x] 57.02 OWASP API Security Top 10 2023
- [x] 57.03 OWASP Mobile Top 10
- [x] 57.04 OWASP Testing Guide (OTG) — Web Application
- [x] 57.05 OWASP ASVS (Application Security Verification Standard)
- [x] 57.06 OWASP SAMM (Software Assurance Maturity Model)
- [x] 57.07 OWASP WSTG — Testing Checklist
- [x] 57.08 OWASP Cheat Sheet Series — Key Sheets
- [x] 57.09 OWASP Dependency-Check
- [x] 57.10 OWASP ModSecurity CRS — WAF Rules
- [x] 57.11 OWASP ZAP — Full Configuration Guide
- [x] 57.12 NIST Cybersecurity Framework
- [x] 57.13 PCI DSS — Payment Card Security Requirements
- [x] 57.14 GDPR Security Requirements for Developers
- [x] 57.15 ISO 27001 — Information Security Management

---

## MODULE 58 — Advanced Web Techniques (25)

- [x] 58.01 HTTP Parameter Pollution (HPP) — Deep Dive
- [x] 58.02 Mass Assignment — Rails, Laravel, Spring, Django
- [x] 58.03 Dangling Markup Injection
- [x] 58.04 CSS Injection — Exfiltrating Data via CSS
- [x] 58.05 Browser Cache Attacks
- [x] 58.06 Relative Path Overwrite (RPO)
- [x] 58.07 URL Confusion — Parser Differential Attacks
- [x] 58.08 Origin Header Spoofing
- [x] 58.09 Host Override via Forwarded Headers
- [x] 58.10 HTTP/2 Specific Attacks (Rapid Reset, h2c Upgrade)
- [x] 58.11 Compression Side-Channel (BREACH, TIME)
- [x] 58.12 Timing Attacks — Remote Timing Analysis
- [x] 58.13 Race Condition — TOCTOU (Time-of-Check Time-of-Use)
- [x] 58.14 Insecure Randomness in Web Context
- [x] 58.15 Account Takeover via Email Domain Takeover
- [x] 58.16 HTTP Response Splitting
- [x] 58.17 Unicode Normalization Attacks
- [x] 58.18 Homograph Attacks (IDN — International Domain Names)
- [x] 58.19 Browser Fingerprinting — Detection and Evasion
- [x] 58.20 Postmessage Vulnerabilities (XSS via postMessage)
- [x] 58.21 Reverse Tabnapping
- [x] 58.22 DNS Rebinding — Deep Dive
- [x] 58.23 Cross-Window Messaging Attacks
- [x] 58.24 Service Worker Attacks (Cache Poisoning, XSS Storage)
- [x] 58.25 Abuse of Browser APIs (CORS, Fetch, XMLHttpRequest)

---

## MODULE 59 — Complete Tools Reference (80)

### Reconnaissance
- [x] 59.01 Amass — Full Config and Usage
- [x] 59.02 Subfinder — Config, Sources, API Keys
- [x] 59.03 Assetfinder — Lightweight Subdomain Discovery
- [x] 59.04 theHarvester — Full Usage Guide
- [x] 59.05 Recon-ng — Modular OSINT Framework
- [x] 59.06 Maltego — Visual OSINT and Link Analysis
- [x] 59.07 Shodan — Web and CLI Complete Guide
- [x] 59.08 Censys — Search Syntax and API
- [x] 59.09 FOFA — Chinese IoT Search Engine
- [x] 59.10 Zoomeye — Alternative to Shodan
- [x] 59.11 crt.sh — Certificate Transparency Query
- [x] 59.12 dnsx — DNS Bulk Resolution and Probing
- [x] 59.13 shuffledns — DNS Bruteforcing at Scale
- [x] 59.14 puredns — Fast DNS Resolver with Wildcard Filtering
- [x] 59.15 httpx — HTTP Probing at Scale

### Web Application Testing
- [x] 59.16 Burp Suite Pro — Complete Feature Reference
- [x] 59.17 Burp Extensions (Active Scan++, Autorize, JWT Editor, Turbo Intruder)
- [x] 59.18 OWASP ZAP — Full Scan Modes and API
- [x] 59.19 ffuf — Advanced Usage (recursion, rate limiting, filters)
- [x] 59.20 Gobuster — DNS, Dir, VHost modes
- [x] 59.21 Feroxbuster — Recursive with Smart Filtering
- [x] 59.22 Katana — Web Crawler by Project Discovery
- [x] 59.23 Hakrawler — Fast Web Crawler
- [x] 59.24 gau — GetAllUrls from Wayback and OTX
- [x] 59.25 waybackurls — Wayback Machine URL Fetcher
- [x] 59.26 arjun — Parameter Discovery
- [x] 59.27 x8 — Hidden Parameter Discovery
- [x] 59.28 ParamSpider — Parameter Mining from Web Archives
- [x] 59.29 Nikto — Full Config and Output Interpretation
- [x] 59.30 Nuclei — Writing Custom Templates

### Exploitation
- [x] 59.31 sqlmap — Full Flag Reference and Tamper Scripts
- [x] 59.32 XSStrike — XSS Fuzzer and Exploit
- [x] 59.33 dalfox — XSS Scanner (DOM-aware)
- [x] 59.34 SSTImap — SSTI Scanner and Exploiter
- [x] 59.35 tplmap — Template Injection Tester
- [x] 59.36 Commix — Command Injection Exploiter
- [x] 59.37 corsy — CORS Scanner
- [x] 59.38 CORStest — CORS Misconfiguration Tester
- [x] 59.39 smuggler.py — HTTP Request Smuggling Detector
- [x] 59.40 h2csmuggler — HTTP/2 Cleartext Smuggling
- [x] 59.41 jwt_tool — JWT Attack Toolkit (Full Reference)
- [x] 59.42 ysoserial — Java Deserialization Payload Generator
- [x] 59.43 PHPGGC — PHP Gadget Chain Generator
- [x] 59.44 noSQLmap — NoSQL Injection Tool

### Network and Infrastructure
- [x] 59.45 Nmap — NSE Scripts Reference
- [x] 59.46 Masscan — High-Speed Port Scanner
- [x] 59.47 Rustscan — Fast Pre-Scanner for Nmap
- [x] 59.48 Metasploit — Auxiliary, Exploits, Post Modules
- [x] 59.49 Msfvenom — Payload Generation Reference
- [x] 59.50 Hydra — All Protocols Reference
- [x] 59.51 Medusa — Parallel Login Brute Forcer
- [x] 59.52 Netcat (nc / ncat) — Swiss Army Knife
- [x] 59.53 Socat — Advanced Netcat Replacement
- [x] 59.54 Chisel — TCP Tunneling over HTTP
- [x] 59.55 Ligolo-ng — Layer 3 Pivot Tool
- [x] 59.56 proxychains — SOCKS Proxy Chaining

### Active Directory
- [x] 59.57 BloodHound — Complete Usage and Query Reference
- [x] 59.58 SharpHound — Data Collection for BloodHound
- [x] 59.59 Impacket — All Scripts (secretsdump, psexec, wmiexec, GetUserSPNs, ASREPRoast)
- [x] 59.60 CrackMapExec / NetExec — Full Command Reference
- [x] 59.61 Responder — All Modes and Config
- [x] 59.62 Mimikatz — All Modules (sekurlsa, lsadump, kerberos, token)
- [x] 59.63 Rubeus — Kerberos Attack Toolkit
- [x] 59.64 Certify — AD CS Attack Tool
- [x] 59.65 Hashcat — Full Mode and Rule Reference

### Privilege Escalation & Enumeration
- [x] 59.66 John the Ripper — Complete Guide
- [x] 59.67 wpscan — Full Config and Exploit Usage
- [x] 59.68 enum4linux — SMB Enumeration
- [x] 59.69 smbclient — Full Usage Guide
- [x] 59.70 sqlcmd — Connecting to MSSQL
- [x] 59.71 pspy — Linux Process Snooper
- [x] 59.72 LinPEAS — Complete Output Analysis
- [x] 59.73 WinPEAS — Complete Output Analysis
- [x] 59.74 Seatbelt — C# Host Enumeration
- [x] 59.75 Snaffler — Finding Secrets in AD
- [x] 59.76 Pacu — AWS Exploitation Framework
- [x] 59.77 aws-cli — Pentester's Command Reference
- [x] 59.78 trivy — Container and IaC Vulnerability Scanner
- [x] 59.79 kube-hunter — Kubernetes Vulnerability Scanner
- [x] 59.80 kubectl — Security-Relevant Commands for Pentesters

---

## MODULE 60 — Advanced Chaining and Real-World Scenarios (30)

- [x] 60.01 Real Bug Bounty Report Analysis — Critical SQLi
- [x] 60.02 Real Bug Bounty Report Analysis — Account Takeover Chain
- [x] 60.03 Real Bug Bounty Report Analysis — SSRF to RCE
- [x] 60.04 Real Bug Bounty Report Analysis — Subdomain Takeover
- [x] 60.05 Real Bug Bounty Report Analysis — XXE in XML API
- [x] 60.06 HackerOne Disclosed Reports — Top 10 Most Educational
- [x] 60.07 Facebook Bug — SSRF via Profile Picture
- [x] 60.08 Twitter Bug — XSS in OAuth Flow
- [x] 60.09 Shopify Bug — IDOR on Admin Panel
- [x] 60.10 Uber Bug — SQLi via Subdomain
- [x] 60.11 Chain: Recon → GitHub Secret → AWS Access → S3 Dump → RDS Creds → DB Admin
- [x] 60.12 Chain: Phishing → Creds → VPN → Internal Network → AD → Domain Admin
- [x] 60.13 Chain: XSS → Steal Admin Cookie → IDOR → Mass Export PII
- [x] 60.14 Chain: Deserialization → RCE → Pivot → Cloud Metadata → IAM Takeover
- [x] 60.15 Chain: GraphQL Introspection → Hidden Mutation → Account Takeover → Admin
- [x] 60.16 Chain: Race Condition → Coupon Reuse → Financial Loss at Scale
- [x] 60.17 Chain: CORS → CSRF → Password Change → Full ATO
- [x] 60.18 Chain: Open Redirect → Phishing → OAuth Token → API Takeover
- [x] 60.19 Chain: Path Traversal → /etc/passwd → SSH Brute Force → Shell
- [x] 60.20 Chain: HTTP Smuggling → Capture Admin Request → CSRF → Privilege Escalation
- [x] 60.21 Full Web App Pentest Simulation (E-commerce target)
- [x] 60.22 Full API Pentest Simulation (REST API target)
- [x] 60.23 Full Cloud Infrastructure Pentest Simulation (AWS target)
- [x] 60.24 Full Internal Network Pentest Simulation (Corp LAN target)
- [x] 60.25 Full Active Directory Pentest Simulation (Domain target)
- [x] 60.26 CTF Challenge Walkthroughs — Web Category
- [x] 60.27 CTF Challenge Walkthroughs — Crypto Category
- [x] 60.28 HackTheBox Machine Walkthroughs — Methodology
- [x] 60.29 TryHackMe Learning Path Mapping
- [x] 60.30 Building a Home Lab for VAPT Practice

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

## MODULE 61 — Reverse Engineering (20)

- [x] 61.01 Introduction to Reverse Engineering and Assembly (x86/x64)
- [x] 61.02 CPU Registers, Stack, and Heap Basics
- [x] 61.03 PE File Format Overview (Windows)
- [x] 61.04 ELF File Format Overview (Linux)
- [x] 61.05 Static Analysis Tools (Strings, Binwalk, ExifTool)
- [x] 61.06 Introduction to IDA Pro and Ghidra
- [x] 61.07 Decompiling vs Disassembling
- [x] 61.08 Identifying Common C/C++ Constructs in Assembly (Loops, Ifs, Functions)
- [x] 61.09 Dynamic Analysis Basics (strace, ltrace, Process Monitor)
- [x] 61.10 Debugging with GDB and Pwndbg
- [x] 61.11 Debugging with x64dbg and OllyDbg
- [x] 61.12 Anti-Debugging and Anti-Disassembly Techniques
- [x] 61.13 Bypassing Anti-Debugging Checks
- [x] 61.14 Unpacking Packed Executables (UPX, custom packers)
- [x] 61.15 Patching Binaries (NOPing out instructions, modifying jumps)
- [x] 61.16 Analyzing Malware Loaders and Droppers
- [x] 61.17 Reverse Engineering .NET Applications (dnSpy, ILSpy)
- [x] 61.18 Reverse Engineering Go Binaries
- [x] 61.19 Reverse Engineering Rust Binaries
- [x] 61.20 Scripting in Ghidra and IDA (Python APIs)

## MODULE 62 — Advanced AWS Exploitation (15)

- [x] 62.01 AWS IAM Privilege Escalation Advanced Vectors
- [x] 62.02 AWS SSRF to Metadata and IMDSv2 Bypass
- [x] 62.03 S3 Bucket Misconfigurations and Ransomware
- [x] 62.04 Exploiting AWS Lambda and Serverless Functions
- [x] 62.05 API Gateway Authorization Bypasses
- [x] 62.06 Cognito Misconfigurations and Privilege Escalation
- [x] 62.07 AWS RDS Database Snapshots and Public Exposure
- [x] 62.08 EKS Cluster Takeover from Pod to Node to IAM
- [x] 62.09 AWS CloudTrail Evasion and Log Manipulation
- [x] 62.10 SecretsManager and Parameter Store Data Exfiltration
- [x] 62.11 AWS Systems Manager SSM Run Command Abuse
- [x] 62.12 Route53 Subdomain Takeover and DNS Hijacking
- [x] 62.13 EC2 User Data and Startup Script Injection
- [x] 62.14 Cross-Account Trust Abuse and AssumeRole Chaining
- [x] 62.15 Pacu and AWS CLI Penetration Testing Workflows

## MODULE 63 — AD CS (Active Directory Certificate Services) Exploitation (15)

- [x] 63.01 AD CS Architecture and Enumeration
- [x] 63.02 ESC1 - Misconfigured Certificate Templates
- [x] 63.03 ESC2 - Any Purpose EKU Abuse
- [x] 63.04 ESC3 - Enrollment Agent Abuse
- [x] 63.05 ESC4 - Template Access Control Abuse
- [x] 63.06 ESC5 - PKI Control Abuse
- [x] 63.07 ESC6 - EDITF_ATTRIBUTESUBJECTALTNAME2 Abuse
- [x] 63.08 ESC7 - Certificate Authority Access Control Abuse
- [x] 63.09 ESC8 - NTLM Relay to AD CS HTTP Endpoints
- [x] 63.10 ESC9 - No Security Extension Abuse
- [x] 63.11 ESC10 - Weak Certificate Mapping Abuse
- [x] 63.12 ESC11 - NTLM Relay to ICPR
- [x] 63.13 ESC12 to ESC15 - Modern ADCS Vectors
- [x] 63.14 ForgeCert - Forging Certificates with CA Keys
- [x] 63.15 AD CS Defensive Hardening and EPA

## MODULE 64 — Advanced Coercion and Relay Attacks (15)

- [x] 64.01 Authentication Coercion Overview
- [x] 64.02 PrinterBug SpoolSample Exploitation
- [x] 64.03 PetitPotam MS-EFSRPC Deep Dive
- [x] 64.04 ShadowCoerce MS-FSRVP Exploitation
- [x] 64.05 DFSCoerce MS-DFSNM Exploitation
- [x] 64.06 Coercer - The Universal Coercion Toolkit
- [x] 64.07 NTLM Relay to LDAP - LDAP Signing Bypasses
- [x] 64.08 NTLM Relay to SMB - SMB Signing Bypasses
- [x] 64.09 NTLM Relay to AD CS - Web Enrollment
- [x] 64.10 Resource-Based Constrained Delegation RBCD via Relay
- [x] 64.11 Shadow Credentials - MSDS-KeyCredentialLink
- [x] 64.12 Drop-the-MIC - Bypassing NTLM MIC
- [x] 64.13 EPA Extended Protection Bypasses
- [x] 64.14 Relay across Forest Trusts
- [x] 64.15 Coercion and Relay Defense Strategies

## MODULE 65 — Hybrid Identity, Entra ID, and Exchange Attacks (20)

- [x] 65.01 Entra ID vs On-Prem AD Architecture
- [x] 65.02 Pass-the-PRT Primary Refresh Token Attacks
- [x] 65.03 Azure AD Connect Sync Credential Extraction
- [x] 65.04 Seamless SSO Desktop SSO Abuse
- [x] 65.05 Golden SAML - Forging IDP Tokens
- [x] 65.06 Pass-the-Certificate in Hybrid Environments
- [x] 65.07 PrivExchange - Exchange to Domain Admin
- [x] 65.08 ProxyLogon Chaining
- [x] 65.09 ProxyShell Chaining
- [x] 65.10 ProxyNotShell and OWASSRF
- [x] 65.11 Exchange Web Services EWS Abuse
- [x] 65.12 Bypassing LAPS Local Admin Password Solution
- [x] 65.13 Extracting gMSA Group Managed Service Accounts
- [x] 65.14 GPO Abuse at Scale
- [x] 65.15 DPAPI and DPAPI-NG Master Key Extraction
- [x] 65.16 Bypassing Microsoft Defender for Identity MDI
- [x] 65.17 Custom BloodHound Cypher Queries for Tier 0 Paths
- [x] 65.18 Overcoming Tiered Administration Models
- [x] 65.19 DCSync Bypasses and Replication Evasion
- [x] 65.20 Ultimate Active Directory Pentest Methodology

## MODULE 66 — AD Foundations and Core Concepts (15)

- [x] 66.01 What is Active Directory? Domains, Trees, and Forests
- [x] 66.02 Understanding FSMO Roles and Domain Controllers
- [x] 66.03 Active Directory DNS and Name Resolution
- [x] 66.04 LDAP Structure and Querying Basics
- [x] 66.05 Users, Groups, and Computers (OUs vs Containers)
- [x] 66.06 Group Policy Objects (GPOs) Explained
- [x] 66.07 Access Control Lists (ACLs) and Access Control Entries (ACEs)
- [x] 66.08 NTLM vs Kerberos Authentication Basics
- [x] 66.09 Service Principal Names (SPNs) and Delegation
- [x] 66.10 Active Directory Trusts (One-way, Two-way, Transitive)
- [x] 66.11 Security Identifiers (SIDs) and Relative IDs (RIDs)
- [x] 66.12 Active Directory Schema and Attributes
- [x] 66.13 Local Administrator vs Domain Administrator
- [x] 66.14 User Account Control (UAC) in AD Environments
- [x] 66.15 Setting Up a Vulnerable AD Lab (GOAD)

## MODULE 67 — AD Enumeration and Tooling Basics (15)

- [x] 67.01 Introduction to BloodHound and SharpHound
- [x] 67.02 Using PowerView for AD Enumeration
- [x] 67.03 Ping Sweeping and Host Discovery in AD
- [x] 67.04 NetExec (CrackMapExec) Basics and Module Usage
- [x] 67.05 Enumerating Users and Groups via LDAP
- [x] 67.06 Enumerating SMB Shares and Null Sessions
- [x] 67.07 Discovering GPOs and Analyzing Passwords in SYSVOL
- [x] 67.08 Enumerating SPNs and Finding Service Accounts
- [x] 67.09 Identifying Domain Controllers and Global Catalogs
- [x] 67.10 Enumerating AD Trusts and Forest Boundaries
- [x] 67.11 Identifying Local Administrators via RPC
- [x] 67.12 Password Spraying Basics and Lockout Policies
- [x] 67.13 AS-REP Roasting Basics and Detection
- [x] 67.14 Kerberoasting Basics and Identification
- [x] 67.15 LLMNR and NBT-NS Poisoning Basics (Responder)

## MODULE 68 — AD Lateral Movement and Credential Access (15)

- [x] 68.01 Lateral Movement via RDP and Hijacking Sessions
- [x] 68.02 Lateral Movement via WinRM and PSRemoting
- [x] 68.03 Lateral Movement via SMB (PsExec, SmbExec)
- [x] 68.04 Lateral Movement via WMI (WMIExec)
- [x] 68.05 Dumping LSASS Memory (Mimikatz, Procdump, Comsvcs)
- [x] 68.06 Dumping Local SAM and LSA Secrets
- [x] 68.07 Pass-the-Hash (PtH) Mechanics and Execution
- [x] 68.08 Over-Pass-the-Hash (Pass-the-Key)
- [x] 68.09 Pass-the-Ticket (PtT) and Ticket Management
- [x] 68.10 Extracting Credentials from Browsers and Credential Manager
- [x] 68.11 Extracting Credentials from Configuration Files (Unattend.xml)
- [x] 68.12 Harvesting Credentials from Password Managers
- [x] 68.13 NTDS.dit Extraction via VSSAdmin and NTDSUtil
- [x] 68.14 Parsing NTDS.dit (Secretsdump)
- [x] 68.15 Token Impersonation and Stealing (Incognito)

## MODULE 69 — AD Access Controls and Escalation Basics (15)

- [x] 69.01 Exploiting Weak ACLs (GenericAll, GenericWrite)
- [x] 69.02 Exploiting WriteDacl and WriteOwner
- [x] 69.03 Exploiting ForceChangePassword
- [x] 69.04 Exploiting AddMember on Sensitive Groups
- [x] 69.05 Exploiting Weak GPO Permissions
- [x] 69.06 Exploiting Weak Service Permissions
- [x] 69.07 Unquoted Service Paths in AD Environments
- [x] 69.08 AlwaysInstallElevated Abuse
- [x] 69.09 Exploiting Weak Registry Permissions
- [x] 69.10 DLL Hijacking Basics for Privilege Escalation
- [x] 69.11 Bypassing UAC (User Account Control)
- [x] 69.12 Exploiting LAPS (Local Administrator Password Solution) Basics
- [x] 69.13 Kerberos Constrained Delegation Basics
- [x] 69.14 Kerberos Unconstrained Delegation Basics
- [x] 69.15 Defending Against Basic AD Attacks

## MODULE 70 — Network Foundations and Core Concepts (15)

- [ ] 70.01 OSI Model and TCP IP Protocol Suite
- [ ] 70.02 IP Addressing Subnetting and CIDR Notation
- [ ] 70.03 Introduction to Routing and Switching
- [ ] 70.04 Understanding TCP UDP and ICMP
- [ ] 70.05 ARP Protocol and Layer 2 Networking
- [ ] 70.06 DNS Protocol Basics and Name Resolution
- [ ] 70.07 DHCP Protocol Basics and Address Allocation
- [ ] 70.08 HTTP HTTPS and TLS Handshake Explained
- [ ] 70.09 SMB Protocol Basics and File Sharing
- [ ] 70.10 FTP TFTP and Telnet Protocols
- [ ] 70.11 SSH Protocol Basics and Key Authentication
- [ ] 70.12 SMTP POP3 and IMAP Email Protocols
- [ ] 70.13 SNMP Protocol Basics and Community Strings
- [ ] 70.14 Firewalls IDS IPS and NAT Explained
- [ ] 70.15 VPNs IPsec and Tunneling Basics

## MODULE 71 — Network Enumeration, Scanning, and Sniffing (15)

- [ ] 71.01 Ping Sweeps and Host Discovery
- [ ] 71.02 Nmap Port Scanning Techniques TCP UDP
- [ ] 71.03 Nmap Service and OS Detection
- [ ] 71.04 Nmap Scripting Engine NSE Basics
- [ ] 71.05 Masscan and RustScan for Fast Discovery
- [ ] 71.06 Wireshark Basics and Packet Capture Analysis
- [ ] 71.07 tcpdump Basics and Command Line Sniffing
- [ ] 71.08 Enumerating DNS Nslookup Dig Fierce
- [ ] 71.09 Enumerating SMB Null Sessions Enum4linux
- [ ] 71.10 Enumerating SNMP Snmpwalk
- [ ] 71.11 Enumerating FTP and TFTP
- [ ] 71.12 Enumerating SMTP VRFY EXPN
- [ ] 71.13 Vulnerability Scanning with Nessus and OpenVAS
- [ ] 71.14 Active vs Passive Reconnaissance in Networks
- [ ] 71.15 Identifying Firewalls and WAFs

## MODULE 72 — Network Exploitation and Protocol Abuse (15)

- [ ] 72.01 ARP Spoofing and Man-in-the-Middle Attacks
- [ ] 72.02 DHCP Starvation and Rogue DHCP Servers
- [ ] 72.03 DNS Spoofing and Cache Poisoning
- [ ] 72.04 Exploiting SNMP Public Private Strings
- [ ] 72.05 SMB Relay Attacks (NTLM Relay on Network Level)
- [ ] 72.06 IPv6 Spoofing and MITM (mitm6)
- [ ] 72.07 VLAN Hopping Attacks
- [ ] 72.08 Exploiting Weak SSH Configurations and Keys
- [ ] 72.09 Anonymous FTP and Directory Traversal
- [ ] 72.10 Exploiting Remote Desktop Protocol RDP
- [ ] 72.11 Exploiting VNC Unauthenticated Access
- [ ] 72.12 Exploiting NFS and Weak RPC Exports
- [ ] 72.13 Exploiting Telnet and Cleartext Protocols
- [ ] 72.14 Bypassing Network Access Control NAC
- [ ] 72.15 Network Denial of Service DoS Attacks

## MODULE 73 — Advanced Network Pivoting, Tunnels, and Evasion (15)

- [ ] 73.01 Port Forwarding Local Remote and Dynamic
- [ ] 73.02 SSH Tunneling and SOCKS Proxies
- [ ] 73.03 ProxyChains and Traffic Routing
- [ ] 73.04 Chisel for TCP UDP Tunneling
- [ ] 73.05 Ligolo-ng Advanced TUN Interface Pivoting
- [ ] 73.06 Meterpreter Portfwd and Autoroute
- [ ] 73.07 Socat Relays and Bind Shells
- [ ] 73.08 ICMP Tunneling PingTunnel
- [ ] 73.09 DNS Tunneling Iodine dnscat2
- [ ] 73.10 Bypassing Firewalls via Egress Testing
- [ ] 73.11 Bypassing Deep Packet Inspection DPI
- [ ] 73.12 Evading Network IDS IPS Signatures
- [ ] 73.13 Double Pivoting and Multi-hop Routing
- [ ] 73.14 VPN Exploitation and Compromise
- [ ] 73.15 C2 Infrastructure Traffic Obfuscation

## MODULE 74 — Cloud Foundations, Identity, and Access (15)

- [x] 74.01 Introduction to Cloud Computing IaaS PaaS SaaS
- [x] 74.02 Cloud Shared Responsibility Model
- [x] 74.03 Introduction to AWS Architecture and Services
- [x] 74.04 Introduction to Azure Architecture and Services
- [x] 74.05 Introduction to GCP Architecture and Services
- [x] 74.06 Cloud Identity and Access Management IAM Basics
- [x] 74.07 Understanding AWS Policies Roles and Users
- [x] 74.08 Understanding Azure Active Directory Entra ID Basics
- [x] 74.09 Understanding GCP Service Accounts and IAM
- [x] 74.10 Cloud Storage Basics S3 Blobs Buckets
- [x] 74.11 Cloud Networking VPCs Subnets and Security Groups
- [x] 74.12 Serverless Computing Basics Lambda Functions
- [x] 74.13 Managed Databases RDS SQL Azure Cloud SQL
- [x] 74.14 Cloud API Gateways and Endpoints
- [x] 74.15 Introduction to Containerization Docker Basics

## MODULE 75 — Cloud Enumeration and Reconnaissance (15)

- [x] 75.01 OSINT for Cloud Assets Domain to Cloud IP
- [x] 75.02 Discovering Exposed Cloud Storage S3 Scanner
- [x] 75.03 Using AWS CLI for Reconnaissance
- [x] 75.04 Using Azure CLI and AzureHound for Recon
- [x] 75.05 Using GCP CLI gcloud for Reconnaissance
- [x] 75.06 Enumerating AWS IAM Permissions
- [x] 75.07 Enumerating Azure Entra ID and Subscriptions
- [x] 75.08 Enumerating GCP Projects and Service Accounts
- [x] 75.09 Cloud Metadata Services IMDS Overview
- [x] 75.10 Identifying Serverless Endpoints and API Gateways
- [x] 75.11 GitHub Recon for Leaked Cloud Keys
- [x] 75.12 Using CloudBrute and Pacu for Discovery
- [x] 75.13 Using ScoutSuite for Cloud Security Auditing
- [x] 75.14 Identifying Misconfigured Cloud Networking Security Groups
- [x] 75.15 Container Registry Enumeration

## MODULE 76 — Advanced Azure / Entra ID Exploitation (15)

- [x] 76.01 Azure AD Privilege Escalation Vectors
- [x] 76.02 Exploiting Azure Managed Identities
- [x] 76.03 Azure Function Apps and Exposed Secrets
- [x] 76.04 Azure Blob Storage Public Access and SAS Tokens
- [x] 76.05 Azure SSRF to IMDS Data Exfiltration
- [x] 76.06 Abusing Azure Service Principals
- [x] 76.07 Azure Automation Accounts and Runbooks Exploitation
- [x] 76.08 Azure Key Vault Extraction and Secrets Dumping
- [x] 76.09 Attacking Azure DevOps CI CD Pipelines
- [x] 76.10 Azure Logic Apps Abuse
- [x] 76.11 Illicit Consent Grants and OAuth Phishing in Azure
- [x] 76.12 Azure Custom Role Definition Abuse
- [x] 76.13 Bypassing Conditional Access Policies CAPs
- [x] 76.14 Lateral Movement from On-Prem AD to Azure
- [x] 76.15 MicroBurst Toolkit and Azure Pentesting Workflows

## MODULE 77 — Advanced GCP (Google Cloud) Exploitation (15)

- [x] 77.01 GCP IAM Privilege Escalation Vectors
- [x] 77.02 Exploiting GCP Default Service Accounts
- [x] 77.03 GCP Metadata Server SSRF to Credential Theft
- [x] 77.04 GCP Cloud Storage Public Bucket Access
- [x] 77.05 GCP Cloud Functions Privilege Escalation
- [x] 77.06 Abuse of OS Login and SSH Keys in GCP
- [x] 77.07 Exploiting GCP Workload Identity
- [x] 77.08 Extracting Secrets from GCP Secret Manager
- [x] 77.09 GCP Cloud Run and App Engine Exploitation
- [x] 77.10 Exploiting GCP Service Account Impersonation
- [x] 77.11 Attacking Google Workspace and G Suite
- [x] 77.12 Privilege Escalation via GCP Deployment Manager
- [x] 77.13 GCP Cloud Build CI CD Poisoning
- [x] 77.14 Lateral Movement across GCP Projects
- [x] 77.15 GCPBuster and GCP Pentesting Workflows

## MODULE 78 — Active Directory Exotic Protocols & Cross-Forest (15)

- [x] 78.01 Exploiting Active Directory Web Services ADWS
- [x] 78.02 Cross-Forest Trust Exploitation and SID History
- [x] 78.03 Exploiting AD FS Active Directory Federation Services
- [x] 78.04 AD CS ESC1-ESC15 Advanced Chaining
- [x] 78.05 Attacking RODC Read-Only Domain Controllers
- [x] 78.06 Exploiting Microsoft Identity Manager MIM
- [x] 78.07 Bypassing LSA Protection and Credential Guard
- [x] 78.08 Advanced NTLM Relaying to MSSQL
- [x] 78.09 PrinterBug and PetitPotam Alternatives
- [x] 78.10 Abuse of Exchange Web Services in AD
- [x] 78.11 Forging Ticket Granting Tickets TGTs
- [x] 78.12 Advanced Golden SAML Attacks
- [x] 78.13 Delegated Authentication Bypass
- [x] 78.14 SCCM and WSUS Exploitation in AD
- [x] 78.15 Tier 0 Compromise and Domain Dominance

## MODULE 79 — Advanced Network Services: ICS, SCADA, Mainframes, SAP (15)

- [x] 79.01 Introduction to ICS and SCADA Security
- [x] 79.02 Modbus Protocol Exploitation
- [x] 79.03 DNP3 Protocol Exploitation
- [x] 79.04 Siemens S7 Protocol Attacks
- [x] 79.05 Attacking SAP NetWeaver and RFCs
- [x] 79.06 Attacking SAP GUI and Client Interfaces
- [x] 79.07 Mainframe Penetration Testing TN3270
- [x] 79.08 IBM WebSphere MQ Exploitation
- [x] 79.09 Exploiting Oracle Databases TNS Poisoning
- [x] 79.10 Advanced MSSQL Exploitation and xp_cmdshell
- [x] 79.11 IoT Protocols MQTT and CoAP Exploitation
- [x] 79.12 CAN Bus and Automotive Network Exploitation
- [x] 79.13 VoIP and SIP Protocol Attacks
- [x] 79.14 Attacking BGP Routing and Infrastructure
- [x] 79.15 Physical Security Systems and Access Control Bypass

## MODULE 80 — Enterprise Web Apps: WebLogic, ColdFusion, Liferay (15)

- [x] 80.01 Oracle WebLogic Deserialization Vulnerabilities
- [x] 80.02 Exploiting Adobe ColdFusion Server Vulnerabilities
- [x] 80.03 Liferay Portal Exploitation Techniques
- [x] 80.04 Apache Struts Remote Code Execution
- [x] 80.05 Java Deserialization ysoserial Deep Dive
- [x] 80.06 Attacking Microsoft SharePoint Servers
- [x] 80.07 Exploiting Atlassian Jira and Confluence
- [x] 80.08 Advanced Java Server Faces JSF Exploitation
- [x] 80.09 Spring Framework Vulnerabilities Spring4Shell
- [x] 80.10 Exploiting JBoss and WildFly Application Servers
- [x] 80.11 .NET Deserialization ysoserial.net
- [x] 80.12 Attacking Node.js Prototype Pollution
- [x] 80.13 GraphQL Introspection and Exploitation
- [x] 80.14 Exploiting gRPC Endpoints
- [x] 80.15 Server-Side Template Injection SSTI in Enterprise Apps

## MODULE 81 — Advanced Kubernetes and Container Breakouts (15)

- [x] 81.01 Kubernetes Architecture and Attack Surface
- [x] 81.02 Enumerating Kubernetes Clusters Kubelet API
- [x] 81.03 Exploiting Unauthenticated Kubelet Endpoints
- [x] 81.04 RBAC Exploitation and Privilege Escalation in K8s
- [x] 81.05 Advanced Docker Breakouts Capabilities and Mounts
- [x] 81.06 Bypassing AppArmor and Seccomp in Containers
- [x] 81.07 Exploiting Tiller and Helm v2 v3
- [x] 81.08 Lateral Movement in Kubernetes Pod to Pod
- [x] 81.09 Secrets Extraction from etcd
- [x] 81.10 Escaping Privileged Containers Deep Dive
- [x] 81.11 Exploiting Cloud Native CI CD Pipelines
- [x] 81.12 Serverless Container Exploitation Fargate Cloud Run
- [x] 81.13 Attacking Istio and Service Meshes
- [x] 81.14 Exploiting Exotic AWS and GCP Container Services
- [x] 81.15 Ultimate Container Pentesting Methodology

# Cyber Threat Intelligence and Dark Web Monitoring

## MODULE 82 — CTI Foundations and Intelligence Lifecycle (15)

- [ ] 82.01 Introduction to Cyber Threat Intelligence CTI
- [ ] 82.02 The Intelligence Cycle Direction Collection Processing
- [ ] 82.03 Tactical vs Operational vs Strategic Intelligence
- [ ] 82.04 Threat Modeling Frameworks Diamond Model
- [ ] 82.05 Mitre ATT&CK Framework Deep Dive
- [ ] 82.06 Lockheed Martin Cyber Kill Chain
- [ ] 82.07 Intelligence Driven Incident Response
- [ ] 82.08 Indicators of Compromise IoC vs Indicators of Attack IoA
- [ ] 82.09 STIX and TAXII Standards Explained
- [ ] 82.10 Open Source Threat Intelligence Feeds OTX MISP
- [ ] 82.11 Setting up a MISP Malware Information Sharing Platform
- [ ] 82.12 YARA Rules for Threat Intelligence
- [ ] 82.13 Evaluating Source Reliability and Information Credibility
- [ ] 82.14 Writing Actionable CTI Reports
- [ ] 82.15 Legal and Ethical Boundaries of CTI

## MODULE 83 — Dark Web Infrastructure and Tor Internals (15)

- [ ] 83.01 Clearnet vs Deep Web vs Dark Web
- [ ] 83.02 The Onion Router Tor Architecture and Mechanics
- [ ] 83.03 Tor Hidden Services v3 Cryptography
- [ ] 83.04 Tor Relays Guard Middle and Exit Nodes
- [ ] 83.05 I2P Invisible Internet Project Architecture
- [ ] 83.06 Freenet and ZeroNet Decentralized Networks
- [ ] 83.07 OPSEC for Dark Web Researchers
- [ ] 83.08 Setting up a Secure Investigation VM Whonix Tails
- [ ] 83.09 Managing Sockpuppet Personas and Identities
- [ ] 83.10 Cryptocurrencies in the Dark Web Bitcoin Privacy
- [ ] 83.11 Monero XMR Cryptography and Tracing Resistance
- [ ] 83.12 De-anonymization Techniques and Traffic Correlation
- [ ] 83.13 Deanonymizing Tor Users via Browser Exploits
- [ ] 83.14 Malicious Exit Node Profiling and SSL Stripping
- [ ] 83.15 Operational Security Failures in Historic Takedowns

## MODULE 84 — Dark Web Forums, Marketplaces, and Data Leaks (15)

- [ ] 84.01 Evolution of Dark Web Marketplaces Silk Road to Present
- [ ] 84.02 Escrow Systems and PGP Authentication in Markets
- [ ] 84.03 Russian Hacker Forums Exploit.in XSS.is
- [ ] 84.04 Initial Access Brokers IABs Ecosystem
- [ ] 84.05 Ransomware as a Service RaaS Operations
- [ ] 84.06 Double and Triple Extortion Leak Sites
- [ ] 84.07 Data Breach Forums BreachForums Alternatives
- [ ] 84.08 Malware Crypting and FUD Services
- [ ] 84.09 Bulletproof Hosting Providers and Fast Flux
- [ ] 84.10 Credit Card Carding Forums and Dumps
- [ ] 84.11 Navigating and Searching Dark Web Indexes Ahmia
- [ ] 84.12 Translating and Parsing Russian Chinese Threat Slang
- [ ] 84.13 Infiltrating Closed Forums Proof of Concept Challenges
- [ ] 84.14 Monitoring Telegram and Discord for Threat Intel
- [ ] 84.15 Tracking Phishing Kits and MaaS Offerings

## MODULE 85 — OSINT for Threat Intelligence and Actor Tracking (15)

- [ ] 85.01 Advanced Search Engine Dorking for Threat Intel
- [ ] 85.02 Reverse Image Searching and EXIF Data Analysis
- [ ] 85.03 Shodan and Censys for Tracking Threat Infrastructure
- [ ] 85.04 RiskIQ PassiveTotal and Passive DNS
- [ ] 85.05 WHOIS History and Domain Registration Reversals
- [ ] 85.06 Tracking Malicious SSL TLS Certificates
- [ ] 85.07 Social Media Intelligence SOCMINT on Threat Actors
- [ ] 85.08 Code Repository Intelligence GitHub GitLab Search
- [ ] 85.09 Tracking Pastebin and Ghostbin Leaks
- [ ] 85.10 Email OSINT and Data Breach Search HaveIBeenPwned DeHashed
- [ ] 85.11 Geolocation and Tracking Threat Actors
- [ ] 85.12 Utilizing Maltego for Infrastructure Graphing
- [ ] 85.13 SpiderFoot and Automating OSINT Gathering
- [ ] 85.14 Identifying Command and Control C2 Servers via OSINT
- [ ] 85.15 OSINT OPSEC Preventing Counter-Intelligence

## MODULE 86 — Advanced Threat Actor Attribution and TTPs (15)

- [ ] 86.01 The Complexity of Attribution False Flags
- [ ] 86.02 Advanced Persistent Threats APT Definitions
- [ ] 86.03 Russian State-Sponsored APTs Cozy Bear Fancy Bear
- [ ] 86.04 Chinese State-Sponsored APTs Equation Group Axiom
- [ ] 86.05 North Korean APTs Lazarus Group HIDDEN COBRA
- [ ] 86.06 Iranian State-Sponsored APTs MuddyWater Charming Kitten
- [ ] 86.07 Financial Crime Syndicates FIN7 FIN11
- [ ] 86.08 Analyzing Malware Compilations Timestamps and Toolmarks
- [ ] 86.09 Code Overlap and String Similarity Analysis
- [ ] 86.10 Tracking Threat Actors via PDB Paths
- [ ] 86.11 Linguistic Profiling in Threat Actor Communications
- [ ] 86.12 Infrastructure Reuse and IP BGP Profiling
- [ ] 86.13 TTP Overlap using ATT&CK Navigator
- [ ] 86.14 Evaluating Public Attribution Reports
- [ ] 86.15 Constructing the Attribution Case

## MODULE 87 — Automated Dark Web Monitoring and Scraping (15)

- [ ] 87.01 Challenges in Scraping the Dark Web
- [ ] 87.02 Routing Python Scripts through Tor Proxies
- [ ] 87.03 Defeating CAPTCHAs and Anti-Bot Protections
- [ ] 87.04 Building Custom Tor Scrapers with BeautifulSoup
- [ ] 87.05 Using Selenium and Playwright over Tor
- [ ] 87.06 Scraping Telegram Channels with Telethon
- [ ] 87.07 Extracting and Normalizing IoCs from Scraping
- [ ] 87.08 NLP for Identifying Credential Leaks in Dumps
- [ ] 87.09 Real-time Alerting for Brand Mentions on Dark Forums
- [ ] 87.10 Ingesting Scraped Data into Elasticsearch
- [ ] 87.11 Network Graphing of Criminal Relationships
- [ ] 87.12 Automated PGP Key Discovery and Tracking
- [ ] 87.13 Dark Web Data Enrichment using MISP
- [ ] 87.14 Building a Custom CTI Dashboard
- [ ] 87.15 Legal and Storage Considerations for Malicious Data

# Threat Hunting and Incident Response

## MODULE 88 — Threat Hunting Foundations and Methodologies (15)

- [ ] 88.01 Introduction to Proactive Threat Hunting
- [ ] 88.02 The Threat Hunting Loop Hypothesis to Triage
- [ ] 88.03 Hypothesis Generation Methodologies
- [ ] 88.04 Known Bad vs Known Good vs Outliers
- [ ] 88.05 Crown Jewel Analysis and Identifying Vital Assets
- [ ] 88.06 The Pyramid of Pain in Hunting
- [ ] 88.07 Baseline Establishment and Anomaly Detection
- [ ] 88.08 Using Sigma Rules for Vendor-Agnostic Hunting
- [ ] 88.09 Threat Hunting Maturity Model THMM
- [ ] 88.10 Data Sources Endpoint Network and Cloud
- [ ] 88.11 Creating a Threat Hunting Runbook
- [ ] 88.12 False Positives vs False Negatives in Hunting
- [ ] 88.13 Transitioning from Hunt to Incident Response
- [ ] 88.14 Automating Hunts vs Manual Investigations
- [ ] 88.15 Measuring the ROI of a Threat Hunting Program

## MODULE 89 — Endpoint Threat Hunting: Windows, Sysmon, EDR (15)

- [ ] 89.01 Windows Event Logs Deep Dive Event IDs 4624 4688
- [ ] 89.02 Microsoft Sysmon Configuration and Telemetry
- [ ] 89.03 Hunting for Process Injection and Hollowing
- [ ] 89.04 Hunting for Living off the Land Binaries LOLBAS
- [ ] 89.05 Detecting PowerShell Downgrade and Obfuscation
- [ ] 89.06 Hunting for WMI Abuse and Persistence
- [ ] 89.07 Detecting Malicious Scheduled Tasks and Services
- [ ] 89.08 Hunting for Registry Modifications and Run Keys
- [ ] 89.09 Detecting Credential Dumping LSASS Access
- [ ] 89.10 Identifying Suspicious Parent-Child Process Trees
- [ ] 89.11 Hunting for UAC Bypasses
- [ ] 89.12 Endpoint Detection and Response EDR Telemetry Analysis
- [ ] 89.13 Hunting for Fileless Malware and In-Memory Execution
- [ ] 89.14 Analyzing Windows Prefetch Amcache and Shimcache
- [ ] 89.15 MacOS and Linux Endpoint Hunting Basics

## MODULE 90 — Network Threat Hunting: Zeek, Suricata, PCAP (15)

- [ ] 90.01 Packet Capture PCAP Analysis at Scale
- [ ] 90.02 Introduction to Zeek Network Security Monitor
- [ ] 90.03 Writing Custom Zeek Scripts for Detection
- [ ] 90.04 Suricata IDS IPS Rule Writing and Tuning
- [ ] 90.05 Hunting for C2 Beacons and Jitter
- [ ] 90.06 Detecting Domain Generation Algorithms DGAs
- [ ] 90.07 Hunting for DNS Tunneling and Exfiltration
- [ ] 90.08 Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting
- [ ] 90.09 Detecting Lateral Movement via SMB and RDP
- [ ] 90.10 Hunting for Web Shells in HTTP Traffic
- [ ] 90.11 Analyzing Network Flow NetFlow IPFIX Data
- [ ] 90.12 Detecting Suspicious User Agent Strings
- [ ] 90.13 RITA Real Intelligence Threat Analytics for C2
- [ ] 90.14 Correlating Network and Endpoint Events
- [ ] 90.15 Dealing with Encrypted Network Traffic in Hunts

## MODULE 91 — Cloud Threat Hunting: AWS, Azure, GCP (15)

- [ ] 91.01 Differences in Cloud vs On-Premises Hunting
- [ ] 91.02 AWS CloudTrail Analysis for Persistence
- [ ] 91.03 Hunting for Compromised IAM Credentials in AWS
- [ ] 91.04 Analyzing AWS GuardDuty and Security Hub Findings
- [ ] 91.05 Azure Activity Logs and Entra ID Sign-in Logs
- [ ] 91.06 Hunting for Illicit Consent Grants in Azure
- [ ] 91.07 Microsoft Defender for Cloud Telemetry
- [ ] 91.08 GCP Cloud Audit Logs Analysis
- [ ] 91.09 Detecting GCP Service Account Impersonation
- [ ] 91.10 Hunting for Cloud Metadata SSRF Exfiltration
- [ ] 91.11 Identifying Anomalous Cloud Storage Access Buckets
- [ ] 91.12 Serverless Function Lambda Abuse Detection
- [ ] 91.13 Hunting in Kubernetes Cluster Audit Logs
- [ ] 91.14 Correlating Cloud Identity with Network Activity
- [ ] 91.15 Building a Cloud Native Threat Hunting Pipeline

## MODULE 92 — Advanced Memory Forensics and Rootkit Detection (15)

- [ ] 92.01 Introduction to Volatility 3 and Memory Acquisition
- [ ] 92.02 Analyzing Windows Process Structures EPROCESS
- [ ] 92.03 Detecting Hidden and Unlinked Processes
- [ ] 92.04 Hunting for Injected Threads and Hollowed Processes
- [ ] 92.05 Extracting Malware Payloads from Memory Dumps
- [ ] 92.06 Analyzing Network Connections in Memory Netscan
- [ ] 92.07 Recovering Passwords and Keys from LSASS Memory
- [ ] 92.08 Kernel Level Rootkits SSDT Hooking Detection
- [ ] 92.09 Direct Kernel Object Manipulation DKOM Detection
- [ ] 92.10 Analyzing Master Boot Record MBR and VBR Infections
- [ ] 92.11 Memory Forensics on Linux Volatility Linux Profiles
- [ ] 92.12 Extracting Browser History and Cryptowallets from RAM
- [ ] 92.13 Defeating Anti-Forensic and Anti-Dumping Techniques
- [ ] 92.14 Analyzing Hypervisor-Level Rootkits Blue Pill
- [ ] 92.15 YARA Scanning over Memory Images

## MODULE 93 — Threat Hunting with SIEM: Splunk, ELK, KQL (15)

- [ ] 93.01 Building a Hunting Dashboard in Splunk
- [ ] 93.02 Advanced Splunk Processing Language SPL for Hunts
- [ ] 93.03 Statistical Outlier Detection in Splunk
- [ ] 93.04 Introduction to Elastic Stack ELK for Threat Hunting
- [ ] 93.05 Writing Elastic Query DSL and EQL for Detection
- [ ] 93.06 Kusto Query Language KQL Basics in Microsoft Sentinel
- [ ] 93.07 Advanced KQL Joins and Time-Series Analysis
- [ ] 93.08 Integrating MISP with Splunk ELK
- [ ] 93.09 SOAR Security Orchestration and Automated Response
- [ ] 93.10 Normalizing Data Sources Common Information Model CIM
- [ ] 93.11 Using Jupyter Notebooks for Threat Hunting
- [ ] 93.12 Machine Learning for Log Anomaly Detection
- [ ] 93.13 Designing High-Fidelity Alerting Rules
- [ ] 93.14 Creating Honeytokens and Deception Decoys
- [ ] 93.15 Case Study Tracking APT29 across a SIEM

# Command and Control (C2) Operations

## MODULE 94 — Command and Control Foundations and Architectures (15)

- [x] 94.01 Introduction to Command and Control C2 Frameworks
- [x] 94.02 C2 Architecture Listeners Implants and Team Servers
- [x] 94.03 Communication Protocols HTTP HTTPS DNS SMB
- [x] 94.04 Bind vs Reverse Shells and Bind vs Reverse TCP
- [x] 94.05 Staged vs Stageless Payloads
- [x] 94.06 Domain Fronting and CDN Abuse
- [x] 94.07 Redirectors Socat Iptables Nginx
- [x] 94.08 Cloud Infrastructure for C2 AWS Azure DigitalOcean
- [x] 94.09 C2 Obfuscation and Jitter
- [x] 94.10 C2 Network Signatures and TLS Fingerprinting
- [x] 94.11 Multi-Tier C2 Architectures
- [x] 94.12 C2 OPSEC Best Practices
- [x] 94.13 Automating Infrastructure Deployment Terraform Ansible
- [x] 94.14 Popular Open Source Frameworks Metasploit Empire Covenant
- [x] 94.15 Evolution of C2 from IRC to Web APIs

## MODULE 95 — Sliver C2 Advanced Deployment and Profiles (15)

- [x] 95.01 Introduction to Sliver C2 Architecture
- [x] 95.02 Deploying Sliver Team Server and Multiplayer Mode
- [x] 95.03 Generating Sliver Implants Beacons vs Sessions
- [x] 95.04 Sliver Listeners mTLS WireGuard HTTP DNS
- [x] 95.05 Customizing Sliver Profiles for OPSEC
- [x] 95.06 Sliver Stagers and Shellcode Execution
- [x] 95.07 Sliver Armory Installing Custom Extensions
- [x] 95.08 Evasion Techniques in Sliver Process Hollowing BlockDLLs
- [x] 95.09 Sliver Lateral Movement PsExec WMI
- [x] 95.10 Integrating BOFs Beacon Object Files in Sliver
- [x] 95.11 Sliver C2 HTTP Profiles mimicking legitimate traffic
- [x] 95.12 DNS C2 with Sliver Under the Radar
- [x] 95.13 Sliver Pivot Listeners and Internal Routing
- [x] 95.14 Bypassing EDRs with Sliver Custom Compiles
- [x] 95.15 Automating Sliver Operations with Python Scripting

## MODULE 96 — Cobalt Strike and Advanced Malleable C2 (15)

- [x] 96.01 Cobalt Strike Architecture and Team Server Setup
- [x] 96.02 Understanding the Beacon Payload
- [x] 96.03 Listeners Beacons and SMB Named Pipes
- [x] 96.04 Introduction to Malleable C2 Profiles
- [x] 96.05 Malleable C2 HTTP-GET and HTTP-POST blocks
- [x] 96.06 Malleable C2 PE and Memory Indicators
- [x] 96.07 Malleable C2 Process Injection and Evasion
- [x] 96.08 Crafting Advanced Malleable C2 Profiles for OPSEC
- [x] 96.09 Artifact Kit and Payload Obfuscation
- [x] 96.10 Resource Kit and Web Delivery
- [x] 96.11 Elevate Kit for Privilege Escalation
- [x] 96.12 Aggressor Scripts Automating Red Team Tasks
- [x] 96.13 Cobalt Strike BOFs Beacon Object Files Development
- [x] 96.14 Lateral Movement and Pivoting with Cobalt Strike
- [x] 96.15 EDR Evasion with Custom Cobalt Strike Kits

## MODULE 97 — Mythic C2 Custom Agents and Payload Generation (15)

- [x] 97.01 Introduction to Mythic C2 Architecture and Docker
- [x] 97.02 Deploying Mythic and Managing the Web Interface
- [x] 97.03 Mythic C2 Profiles HTTP WebSocket SMB
- [x] 97.04 Understanding Mythic Payload Types Agents
- [x] 97.05 Apollo Agent Advanced Windows C2
- [x] 97.06 Poseidon Agent macOS and Linux C2
- [x] 97.07 Medusa Agent Cross-Platform Python C2
- [x] 97.08 Customizing Mythic Agent Builds and OPSEC
- [x] 97.09 Mythic Browser Scripts and UI Customization
- [x] 97.10 SOCKS Proxies and Pivoting with Mythic
- [x] 97.11 Integrating BOFs in Mythic
- [x] 97.12 Developing Custom Mythic Agents from Scratch
- [x] 97.13 Mythic Event Feed and Team Collaboration
- [x] 97.14 Evading Signatures with Unique Mythic Payloads
- [x] 97.15 Mythic Scripting API Automating Operations

## MODULE 98 — Building Custom C2 Frameworks from Scratch (15)

- [x] 98.01 Why Build a Custom C2 Framework
- [x] 98.02 Core Components Server Agent and Protocol
- [x] 98.03 Designing the Communication Protocol HTTP REST vs Websockets
- [x] 98.04 Cryptography for Custom C2 AES RSA and Key Exchange
- [x] 98.05 Developing the Team Server Python Flask FastAPI
- [x] 98.06 Developing the Agent C C++ Golang
- [x] 98.07 Implementing Command Execution and Output Parsing
- [x] 98.08 File Upload and Download Capabilities
- [x] 98.09 Implementing Jitter and Sleep Mechanics
- [x] 98.10 Asynchronous Execution and Background Jobs
- [x] 98.11 Implementing Evasion Techniques directly in the Agent
- [x] 98.12 Developing a Web Interface for the C2 React Vue
- [x] 98.13 Obfuscating the Custom Agent AV EDR Evasion
- [x] 98.14 Adding Lateral Movement Modules to Custom C2
- [x] 98.15 Open-Sourcing vs Private Use Operational Considerations

## MODULE 99 — C2 OPSEC and EDR Evasion Techniques (15)

- [x] 99.01 Modern EDR Architecture and Detection Mechanisms
- [x] 99.02 Bypassing Static Signatures and YARA
- [x] 99.03 Bypassing Heuristics and Behavioral Analysis
- [x] 99.04 Unhooking Userland APIs EDR Bypass
- [x] 99.05 Direct and Indirect Syscalls using HellsGates
- [x] 99.06 Process Hollowing and Injection OPSEC
- [x] 99.07 Thread Stack Spoofing and Call Stack Evasion
- [x] 99.08 PPID Spoofing and Command Line Obfuscation
- [x] 99.09 ETW Event Tracing for Windows Patching
- [x] 99.10 AMSI Antimalware Scan Interface Bypass Techniques
- [x] 99.11 Evading Memory Scanners Sleeping and Encrypting Memory
- [x] 99.12 Malicious Driver loading and Bring Your Own Vulnerable Driver BYOVD
- [x] 99.13 Living off the Land C2 using Native APIs
- [x] 99.14 Creating FUD Fully Undetectable Payloads
- [x] 99.15 Continuous Testing against EDR Sandboxes

## MODULE 100 — Deep Dive: Sliver Custom Compiles & EDR Bypass Mastery (15)

- [x] 100.01 The Anatomy of the Sliver Implant Go Binaries
- [x] 100.02 Setting up the Custom Compilation Environment for Sliver
- [x] 100.03 Modifying Slivers Source Code to Break Static Signatures
- [x] 100.04 Advanced Obfuscation with Garble in Custom Compiles
- [x] 100.05 Stripping Debug Symbols and Metadata from Sliver Implants
- [x] 100.06 Integrating Custom Syscalls directly into the Sliver Agent
- [x] 100.07 Building Custom Loaders for Sliver Shellcode
- [x] 100.08 Bypassing CrowdStrike Falcon with Custom Sliver Profiles
- [x] 100.09 Evading Microsoft Defender for Endpoint MDE with Sliver
- [x] 100.10 Modifying the Sliver Stager to Bypass Heuristic Detection
- [x] 100.11 Implementing Sleep Obfuscation Ekko Foliage in Custom Builds
- [x] 100.12 Custom CGO Bindings for Native Windows API Abuse
- [x] 100.13 Evading Memory Scanners by modifying Slivers Memory Allocation
- [x] 100.14 Automating the Custom Compile Pipeline with CI CD
- [x] 100.15 Case Study A Fully Undetectable FUD Sliver Campaign

# Interview Preparation: Scenario-Based Q&A

## Web Security Interview Q&A

- [x] Web Q&A - Module 01
- [x] Web Q&A - Module 02
- [x] Web Q&A - Module 03
- [x] Web Q&A - Module 04
- [x] Web Q&A - Module 05
- [x] Web Q&A - Module 06
- [x] Web Q&A - Module 07
- [x] Web Q&A - Module 08
- [x] Web Q&A - Module 09
- [x] Web Q&A - Module 10
- [x] Web Q&A - Module 11
- [x] Web Q&A - Module 12
- [x] Web Q&A - Module 13
- [x] Web Q&A - Module 14
- [x] Web Q&A - Module 15
- [x] Web Q&A - Module 16
- [x] Web Q&A - Module 17
- [x] Web Q&A - Module 18
- [x] Web Q&A - Module 19
- [x] Web Q&A - Module 20
- [x] Web Q&A - Module 21
- [x] Web Q&A - Module 22
- [x] Web Q&A - Module 23
- [x] Web Q&A - Module 24
- [x] Web Q&A - Module 25
- [x] Web Q&A - Module 26
- [x] Web Q&A - Module 27
- [x] Web Q&A - Module 28
- [x] Web Q&A - Module 29
- [x] Web Q&A - Module 30

## API Security Interview Q&A

- [x] API Q&A - Module 31
- [x] API Q&A - Module 32
- [x] API Q&A - Module 33
- [x] API Q&A - Module 34
- [x] API Q&A - Module 35
- [x] API Q&A - Module 36
- [x] API Q&A - Module 37
- [x] API Q&A - Module 38
- [x] API Q&A - Module 39
- [x] API Q&A - Module 40

## Network Security Interview Q&A

- [x] Network Q&A - Module 41
- [x] Network Q&A - Module 42
- [x] Network Q&A - Module 43
- [x] Network Q&A - Module 44
- [x] Network Q&A - Module 45
- [x] Network Q&A - Module 46
- [x] Network Q&A - Module 47
- [x] Network Q&A - Module 48
- [x] Network Q&A - Module 49
- [x] Network Q&A - Module 50
- [x] Network Q&A - Module 51
- [x] Network Q&A - Module 52
- [x] Network Q&A - Module 53
- [x] Network Q&A - Module 54
- [x] Network Q&A - Module 55
- [x] Network Q&A - Module 56
- [x] Network Q&A - Module 57
- [x] Network Q&A - Module 58
- [x] Network Q&A - Module 59
- [x] Network Q&A - Module 60

## Active Directory Interview Q&A

- [x] AD Q&A - Module 61
- [x] AD Q&A - Module 62
- [x] AD Q&A - Module 63
- [x] AD Q&A - Module 64
- [x] AD Q&A - Module 65
- [x] AD Q&A - Module 66
- [x] AD Q&A - Module 67
- [x] AD Q&A - Module 68
- [x] AD Q&A - Module 69
- [x] AD Q&A - Module 70
- [x] AD Q&A - Module 71
- [x] AD Q&A - Module 72
- [x] AD Q&A - Module 73
- [x] AD Q&A - Module 74
- [x] AD Q&A - Module 75
- [x] AD Q&A - Module 76
- [x] AD Q&A - Module 77
- [x] AD Q&A - Module 78

## Cloud Penetration Testing Interview Q&A

- [x] Cloud Q&A - Module 79
- [x] Cloud Q&A - Module 80
- [x] Cloud Q&A - Module 81

## Cyber Threat Intelligence & OSINT Interview Q&A

- [x] CTI Q&A - Module 82
- [x] CTI Q&A - Module 83
- [x] CTI Q&A - Module 84
- [x] CTI Q&A - Module 85
- [x] CTI Q&A - Module 86
- [x] CTI Q&A - Module 87

## Threat Hunting & Incident Response Interview Q&A

- [x] TH-IR Q&A - Module 88
- [x] TH-IR Q&A - Module 89
- [x] TH-IR Q&A - Module 90
- [x] TH-IR Q&A - Module 91
- [x] TH-IR Q&A - Module 92
- [x] TH-IR Q&A - Module 93

## Command & Control (C2) Operations Interview Q&A

- [x] C2 Q&A - Module 94
- [x] C2 Q&A - Module 95
- [x] C2 Q&A - Module 96
- [x] C2 Q&A - Module 97
- [x] C2 Q&A - Module 98
- [x] C2 Q&A - Module 99
- [x] C2 Q&A - Module 100

# Ultimate VAPT Methodology & Exploit Master Guides

## Web VAPT Master Guides

- [x] Web VAPT 01 - Recon and Attack Surface Mapping Methodology
- [x] Web VAPT 02 - Exploiting Authentication and Session Management
- [x] Web VAPT 03 - Deep Dive into Injection Exploits SQLi XXE Command
- [x] Web VAPT 04 - Client-Side Exploitation XSS CSRF CORS
- [x] Web VAPT 05 - Advanced Business Logic and Smuggling Exploits

## API VAPT Master Guides

- [x] API VAPT 01 - API Reconnaissance and Endpoint Discovery
- [x] API VAPT 02 - Exploiting BOLA and Authorization Flaws
- [x] API VAPT 03 - Bypassing API Authentication and JWT Exploits
- [x] API VAPT 04 - API Rate Limiting and Resource Exhaustion
- [x] API VAPT 05 - Advanced API Exploits SSRF Mass Assignment

## Network VAPT Master Guides

- [x] Network VAPT 01 - External and Internal Network Recon Methodology
- [x] Network VAPT 02 - Exploiting Layer 2 and Layer 3 Vulnerabilities
- [x] Network VAPT 03 - Attacking Network Services SMB FTP SSH
- [x] Network VAPT 04 - Bypassing Firewalls NAC and Network Segregation
- [x] Network VAPT 05 - Pivoting and Lateral Movement Methodologies

## Active Directory VAPT Master Guides

- [x] AD VAPT 01 - Initial Breach and AD Enumeration Methodology
- [x] AD VAPT 02 - Credential Harvesting and Local Privilege Escalation
- [x] AD VAPT 03 - Exploiting NTLM Relays and Kerberos Flaws
- [x] AD VAPT 04 - Domain Privilege Escalation DCSync DCShadow
- [x] AD VAPT 05 - Cross-Forest Trusts and AD Persistence

# Ultimate Expert Scenario Bank (No Limits Expansion)

## Web Security Ultra-Scenarios
- [ ] Web Ultra-Scenario 01
- [ ] Web Ultra-Scenario 02
- [ ] Web Ultra-Scenario 03
- [ ] Web Ultra-Scenario 04
- [ ] Web Ultra-Scenario 05

## API Security Ultra-Scenarios
- [ ] API Ultra-Scenario 01
- [ ] API Ultra-Scenario 02
- [ ] API Ultra-Scenario 03
- [ ] API Ultra-Scenario 04
- [ ] API Ultra-Scenario 05

## Network Security Ultra-Scenarios
- [ ] Network Ultra-Scenario 01
- [ ] Network Ultra-Scenario 02
- [ ] Network Ultra-Scenario 03
- [ ] Network Ultra-Scenario 04
- [ ] Network Ultra-Scenario 05

## Active Directory Ultra-Scenarios
- [ ] AD Ultra-Scenario 01
- [ ] AD Ultra-Scenario 02
- [ ] AD Ultra-Scenario 03
- [ ] AD Ultra-Scenario 04
- [ ] AD Ultra-Scenario 05
