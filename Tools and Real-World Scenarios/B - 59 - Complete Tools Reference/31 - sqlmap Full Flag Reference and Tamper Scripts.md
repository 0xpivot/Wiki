---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.31 sqlmap Full Flag Reference"
---

# 59.31 sqlmap Full Flag Reference and Tamper Scripts

## 1. Introduction and Core Concepts
`sqlmap` is universally recognized as the most powerful, comprehensive, and automated SQL injection (SQLi) and database takeover tool in the penetration tester's arsenal. Written in Python, it automates the rigorous process of detecting and exploiting SQL injection flaws, taking over database servers, and exfiltrating data. It boasts a massive, constantly updated library of payloads and exploitation techniques, handling everything from basic error-based injections to complex boolean-based blind, time-based blind, and UNION-query-based injections. 

Beyond simple detection, `sqlmap` is engineered for extreme edge cases. It offers an extensive array of tamper scripts for Web Application Firewall (WAF) and Intrusion Prevention System (IPS) evasion, full capabilities to read/write files on the underlying operating system (depending on DB privileges), and out-of-band (OOB) DNS exfiltration for blind targets. Understanding `sqlmap` at a profound level is not just about memorizing flags, but understanding *how* it parses requests, evaluates heuristically the vulnerability of parameters, and builds its attack vectors dynamically.

## 2. Architecture and Execution Flow

The internal architecture of `sqlmap` is highly modular and intelligent. It dynamically adjusts its payloads based on the server's HTTP responses to initial mathematical and boolean heuristics.

```ascii
+-----------------------------------------------------------------------------------+
|                                 sqlmap Core Engine                                |
|                                                                                   |
|  +---------------+    +-------------------+    +-------------------------------+  |
|  | Target Parser | -> | Heuristics Engine | -> | Payload Generator & Injection |  |
|  | (URL/Request) |    | (WAF/DB Detect)   |    | (Error, Blind, Union, Time)   |  |
|  +---------------+    +-------------------+    +-------------------------------+  |
|                               ^                              |                    |
|                               |                              v                    |
|  +---------------+    +-------------------+    +-------------------------------+  |
|  | Tamper Scripts| <- | WAF/IPS Evasion   |    | Exfiltration Engine           |  |
|  | (Obfuscation) |    | Engine            |    | (Data Extraction & Parsing)   |  |
|  +---------------+    +-------------------+    +-------------------------------+  |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                            Network / Target Server                                |
+-----------------------------------------------------------------------------------+
```

## 3. Target Specifications and Input Parsing
The foundation of any `sqlmap` execution is defining the target. While `-u` is the most common, real-world assessments often require parsing complex HTTP requests, especially when dealing with REST APIs, JSON bodies, or authenticated SOAP requests.

*   `-u URL, --url=URL`: Direct target URL. Suitable for standard GET parameters. Example: `sqlmap -u "http://target.com/page?id=1"`
*   `-r REQUESTFILE`: Extremely critical for API testing or complex POST requests. You can save a Burp Suite request to a file and pass it to `sqlmap`. It automatically parses all headers, cookies, and body data.
    *   *Pro-Tip*: When using `-r request.txt`, you can manually specify the injection point by appending an asterisk (`*`) to the parameter value in the text file. This forces `sqlmap` to inject exactly at that byte location.
*   `-g GOOGLEDORK`: Process Google dork results as targets directly. Useful for wide-scale vulnerability research.
*   `-c CONFIGFILE`: Load options from a configuration INI file, useful for standardized pipeline integrations.
*   `-m BULKFILE`: Scan multiple targets listed in a text file concurrently.

## 4. Request Parameters and Authentication
APIs and modern web applications rarely allow unauthenticated testing. `sqlmap` provides granular control over how the HTTP request is constructed.

*   `--data=DATA`: Specify POST data manually (e.g., `--data="id=1&name=test"`).
*   `--cookie=COOKIE`: Set HTTP Cookie header. Essential for authenticated endpoints.
*   `--headers=HEADERS`: Extra headers. Crucial for bypassing certain reverse proxy checks (e.g., `--headers="X-Forwarded-For: 127.0.0.1"`).
*   `--auth-type` and `--auth-cred`: Basic, Digest, NTLM, or PKI authentication configurations.
*   `--proxy=PROXY`: Route traffic through an interception proxy (e.g., `--proxy="http://127.0.0.1:8080"` for tracking `sqlmap`'s payloads in Burp Suite).
*   `--force-ssl`: Force SSL/TLS on the target, crucial when the target redirects dynamically or when testing APIs over port 443 without a specific protocol prefix.
*   `--random-agent`: Randomize the User-Agent header, which is highly recommended to bypass basic logging filters that look for `sqlmap` default agents.

## 5. Injection Mechanics and Optimization
Controlling exactly *how* `sqlmap` injects payloads is vital to avoid denial-of-service (DoS) conditions (especially with time-based payloads) and to bypass specific input validation schemas.

*   `-p TESTPARAMETER`: Specify exactly which parameter to test, bypassing the testing of others to save time.
*   `--skip=SKIP`: Parameters to explicitly skip.
*   `--dbms=DBMS`: Force `sqlmap` to use payloads for a specific DBMS (e.g., `MySQL`, `PostgreSQL`, `Oracle`, `Microsoft SQL Server`). This drastically speeds up the scan by skipping fingerprinting and irrelevant payloads.
*   `--os=OS`: Force backend operating system (e.g., `Windows`, `Linux`).
*   `--prefix=PREFIX` / `--suffix=SUFFIX`: Crucial for breaking out of complex backend queries. If the backend query is `SELECT * FROM users WHERE (username = '$input')`, you might use `--prefix="') " --suffix=" AND ('1'='1"`.
*   `--technique=TECH`: Specify injection techniques to test:
    *   `B`: Boolean-based blind
    *   `E`: Error-based
    *   `U`: Union query-based
    *   `S`: Stacked queries (critical for executing multiple statements, required for `os-shell`)
    *   `T`: Time-based blind
    *   `Q`: Inline queries

## 6. Deep Dive: Tamper Scripts and WAF Evasion
Tamper scripts are Python modules that modify the payload *after* it's generated but *before* it's sent over the network. This is the primary and most powerful method for bypassing Web Application Firewalls (WAFs) and Intrusion Prevention Systems (IPS).

You apply them via `--tamper=SCRIPT1,SCRIPT2`. They can be chained together.

### High-Value Tamper Scripts Reference
*   **`apostrophemask.py`**: Replaces the apostrophe character (`'`) with its UTF-8 full-width equivalent (`%EF%BC%A7`). Extremely useful against poorly configured WAFs that only filter ASCII quotes.
*   **`space2comment.py`**: Replaces spaces with SQL block comments (`/**/`). Highly effective against legacy WAFs that filter spaces to prevent `UNION SELECT` statement construction.
*   **`space2dash.py`**: Replaces space characters with a dash comment (`--`) followed by a random string and a new line.
*   **`charencode.py`**: URL-encodes all characters in the given payload. Useful when the backend server decodes input multiple times.
*   **`charunicodeencode.py`**: Unicode-encodes all characters in a given payload. Often bypasses regex filters that aren't Unicode-aware.
*   **`equaltolike.py`**: Replaces all occurrences of the equals sign (`=`) with the `LIKE` operator. Crucial when the `=` operator is entirely blocked by a WAF rule.
*   **`greatest.py`**: Bypasses filters on the greater-than sign (`>`). Replaces `>` with the `GREATEST()` function.
*   **`modsecurityversioned.py`**: Embraces the complete query with a MySQL versioned comment, specifically designed to bypass older ModSecurity Core Rule Sets.
*   **`halfversionedmorekeywords.py`**: Adds MySQL versioned comments before each SQL keyword.
*   **`base64encode.py`**: Base64 encodes all characters. Useful if the vulnerable parameter itself expects Base64 encoded input (e.g., a serialized token).
*   **`between.py`**: Replaces the greater-than operator (`>`) with `NOT BETWEEN 0 AND #` and the equals operator (`=`) with `BETWEEN # AND #`.
*   **`percentage.py`**: Adds a percentage sign (`%`) in front of each character (e.g., `SELECT` becomes `%S%E%L%E%C%T`). ASP/ASPX targets often ignore these signs, while WAFs fail to read the keyword.

## 7. Detection, Level, and Risk Optimization
`sqlmap` can be incredibly noisy, slow, and potentially destructive if not optimized correctly, especially on time-based blind SQLi where it evaluates results character by character based on server response times.

*   `--level=LEVEL`: Ranges from 1 to 5. Level 1 tests standard GET/POST parameters. Level 2 adds Cookie header testing. Level 3 adds User-Agent and Referer headers. Level 5 tests all headers, including the Host header.
*   `--risk=RISK`: Ranges from 1 to 3. Risk 1 is safe. Risk 2 adds heavy query time-based payloads. Risk 3 adds OR-based SQL injection payloads (dangerous, can update/delete all rows if injected into an `UPDATE`/`DELETE` statement inadvertently).
*   `--threads=THREADS`: Max number of concurrent HTTP(s) requests (default 1). Increasing this drastically speeds up blind injections.
*   `-o`: Turn on all optimization switches dynamically.
*   `--keep-alive`: Use persistent HTTP(s) connections.

## 8. Enumeration and Data Exfiltration
Once the vulnerability is confirmed, the data extraction phase begins. `sqlmap` handles the complex SQL queries required to dump data dynamically.

*   `--banner`: Retrieve the DBMS banner and version.
*   `--current-user`, `--current-db`, `--hostname`: Gather basic context about the execution environment.
*   `--is-dba`: Check if the current database user has DBA (root/sysadmin) privileges. This dictates whether file read/write or OS execution is possible.
*   `--users`, `--passwords`, `--privileges`: Extract database users and attempt to crack their hashes automatically.
*   `--dbs`, `--tables`, `--columns`: Enumerate the database relational structure.
*   `--schema`: Enumerate the entire DBMS schema.
*   `--dump`: Dump the entire table or database. Use `-D DB_NAME -T TABLE_NAME` to specify exactly what to dump.
*   `--dump-all`: Dump all databases (extremely noisy and slow, rarely recommended).
*   `--search`: Search for specific database names, tables, or columns (e.g., `--search -C password,email`).
*   `--sql-query=QUERY`: Execute an arbitrary SQL query and return the results.

## 9. Operating System Takeover and UDF Creation
If the database user has sufficient privileges (e.g., DBA) and the DBMS supports it (e.g., `xp_cmdshell` on MSSQL, `INTO OUTFILE` and User Defined Functions (UDF) on MySQL), `sqlmap` can compromise the underlying host OS.

*   `--os-cmd=OSCMD`: Execute a single OS command.
*   `--os-shell`: Prompt for an interactive OS shell. On MySQL, `sqlmap` will attempt to upload a shared library (DLL/SO) to create a `sys_exec` or `sys_eval` UDF to achieve this. On MSSQL, it enables `xp_cmdshell`.
*   `--os-pwn`: Prompt for an Out-of-Band (OOB) shell, Meterpreter session, or VNC connection.
*   `--file-read=RFILE`: Read a file from the backend file system (e.g., `/etc/passwd`).
*   `--file-write=WFILE --file-dest=DFILE`: Upload a local file to the backend file system (e.g., uploading a PHP web shell to `/var/www/html/`).

## 10. Second-Order SQL Injection
Second-order SQL injection occurs when user input is safely stored in the database but later retrieved and used unsafely in a different SQL query. `sqlmap` handles this complex scenario natively.

*   `--second-order=URL`: Specify the URL where the injected payload will be executed or reflected. The typical workflow involves `sqlmap` injecting the payload into the primary target URL (or request file) and then immediately requesting the `--second-order` URL to evaluate the result of the injection.

## 11. Windows Registry Access
When testing against Microsoft SQL Server running on Windows, `sqlmap` provides direct access to the Windows Registry, assuming DBA privileges are met.

*   `--reg-read`: Read a Windows registry key value.
*   `--reg-add`: Write a Windows registry key value data.
*   `--reg-del`: Delete a Windows registry key value.
*   `--reg-key`, `--reg-value`, `--reg-data`, `--reg-type`: Granular control parameters for registry manipulation.

## 12. Advanced Bypass and OOB DNS Exfiltration
When dealing with extreme WAFs or heavily segmented networks where no inbound HTTP traffic is allowed back, `sqlmap` provides advanced mechanisms.

*   `--dns-domain=DOMAIN`: Use Out-of-Band (OOB) DNS exfiltration. If you control a domain (e.g., `attacker.com`), `sqlmap` forces the database server to resolve subdomains containing the exfiltrated hex-encoded data (e.g., `data.attacker.com`). This is exponentially faster than time-based blind SQLi and often bypasses outbound firewalls.
*   `--hex`: Use hex conversion for data retrieval to avoid encoding or binary corruption issues.
*   `--no-cast`: Turn off the payload casting mechanism (useful on older, brittle DBMS versions that crash on `CAST()` functions).
*   `--hpp`: Use HTTP Parameter Pollution to bypass WAFs that only inspect the first occurrence of a parameter.

## 13. Chaining Opportunities
*   **Reconnaissance Integration**: Output from automated crawlers (like `hakrawler` or `gospider`) can be fed directly into `sqlmap` using the `-m` (multiple URLs) flag for automated scanning of thousands of endpoints.
*   **Burp Suite to sqlmap**: The `sqlmap` API can be integrated with Burp Suite plugins (like CO2 or SQLiPy) to seamlessly pass identified parameters directly to the engine without leaving the proxy environment.
*   **XSS to SQLi**: Cross-Site Scripting (XSS) can be leveraged to steal administrative session tokens, which can then be used in `sqlmap` `--cookie` flags to test internal, highly privileged authenticated endpoints for SQLi.

## 14. Related Notes
*   [[05 - Advanced SQL Injection Techniques]]
*   [[06 - WAF Evasion Strategies]]
*   [[12 - Out of Band (OOB) Exploitation]]
*   [[59 - Database Specific Payloads Reference]]
