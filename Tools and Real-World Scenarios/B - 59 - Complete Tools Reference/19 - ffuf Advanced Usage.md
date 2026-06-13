---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.19 ffuf Advanced Usage"
---

# ffuf: Advanced Usage, Fuzzing, and Workflows

## 1. Introduction to the ffuf Engine
`ffuf` (Fuzz Faster U Fool) has rapidly become the standard CLI web fuzzer for security professionals and bug bounty hunters. Written in Go, it is designed for extreme speed and flexibility. While it excels at standard directory and file brute-forcing, classifying it merely as a directory buster underestimates its capabilities. 

Its true power lies in its agnostic approach to payload injection. `ffuf` can fuzz GET parameters, POST parameters, HTTP headers, HTTP methods, and complex JSON or XML data structures, making it an indispensable tool for advanced web application and API penetration testing.

## 2. Core Mechanics and Concurrency
The speed of `ffuf` is derived from its Go-based architecture, which utilizes lightweight goroutines for highly concurrent, non-blocking network I/O.
*   **Wordlists and Payloads:** `ffuf` reads payloads from specified wordlists and injects them into a template HTTP request using the `FUZZ` keyword.
*   **Multiple Injection Points:** Unlike rudimentary brute-forcers, `ffuf` allows multiple payload injection points in a single request, using different wordlists (e.g., `W1` for directories, `W2` for parameters) using the syntax `-w wordlist.txt:KEYWORD`.

## 3. Comprehensive Modes of Operation

### 3.1 Directory and File Enumeration
The most ubiquitous use case. It involves injecting the payload into the URL path to discover hidden resources.
```bash
# Basic directory enumeration
ffuf -w subdomains.txt -u https://target.com/FUZZ

# Enumeration with specific extensions
ffuf -w common.txt -u https://target.com/FUZZ -e .php,.txt,.bak,.old
```

### 3.2 Virtual Host (VHost) Discovery
Crucial for finding hidden development, staging, or internal administrative environments hosted on the same IP address but requiring a specific `Host` header to route correctly through the reverse proxy.
```bash
# VHost fuzzing using the Host header
ffuf -w subdomains.txt -u http://target.com -H "Host: FUZZ.target.com"
```

### 3.3 Parameter Discovery and Fuzzing
Discovering hidden parameters (GET or POST) is vital for finding debug functionality, hidden administrative toggles, or inputs that lead to injection vulnerabilities (SQLi, SSRF).
```bash
# GET Parameter Discovery
ffuf -w params.txt -u "https://target.com/api/users?FUZZ=1"

# POST JSON Parameter Fuzzing (crucial for APIs)
ffuf -w params.txt -u https://target.com/api/update -X POST -d '{"username":"admin", "FUZZ":"value"}' -H "Content-Type: application/json"
```

## 4. Advanced Matchers and Filters (The Art of ffuf)
The true mastery of `ffuf` lies in managing the output. Without proper filtering, you will be overwhelmed by false positives (e.g., wildcard DNS or catch-all routing returning a 200 OK for every single request).

### 4.1 Matchers (-m)
Instruct `ffuf` to *only* display results that match specific criteria.
*   `-mc`: Match Status Code (e.g., `-mc 200,204,301,302,401`).
*   `-ms`: Match Response Size (e.g., `-ms 1024`).
*   `-mw`: Match Word Count.
*   `-ml`: Match Line Count.
*   `-mr`: Match Regex. Highly powerful for finding specific strings in responses, such as a database error or a leaked API key.

### 4.2 Filters (-f)
Instruct `ffuf` to *hide* results that match specific criteria. This is usually the preferred method to filter out the "noise" of a default baseline response.
*   `-fc`: Filter Status Code (e.g., `-fc 404,403`).
*   `-fs`: Filter Response Size (e.g., `-fs 42`). Crucial for filtering out generic "Not Found" pages that technically return a 200 OK but always have the exact same byte size.
*   `-fw`: Filter Word Count.
*   `-fl`: Filter Line Count.

### 4.3 Auto-Calibration (-ac)
This is a critical feature for handling wildcards and generic error pages. If a target returns a 200 OK for every non-existent directory, `-ac` will send a few randomized requests (e.g., `/afsdfqwerty`), analyze the baseline responses (size, words, lines), and automatically create internal filters to ignore any future responses that match that baseline.

## 5. Advanced Techniques, Tuning, and Evasion

### 5.1 Recursion (-recursion)
`ffuf` can automatically fuzz newly discovered directories.
```bash
ffuf -w dirs.txt -u https://target.com/FUZZ -recursion -recursion-depth 2
```

### 5.2 Rate Limiting and Evasion
When testing production systems, hitting WAFs, or trying to avoid bringing down fragile infrastructure, you must control the request rate.
*   `-p`: Delay between requests (e.g., `-p 0.1` for 100ms).
*   `-rate`: Enforce a strict requests-per-second limit.
*   `-t`: Number of concurrent threads (default is 40). Lower this when testing unstable APIs.

### 5.3 Custom Headers and Authentication
You can pass cookies, authorization tokens, or custom headers seamlessly to test authenticated attack surfaces.
```bash
ffuf -w paths.txt -u https://target.com/FUZZ -H "Authorization: Bearer <jwt_token>" -H "X-Forwarded-For: 127.0.0.1"
```

## 6. Architecture Diagram: VHost Fuzzing Flow

```ascii
+-------------+       Wordlist (vhosts.txt)          +-------------------+
|             |          [ dev, api, admin ]         |                   |
|   ffuf      |------------------------------------->|  Target Server    |
|   Engine    |       GET / HTTP/1.1                 |  IP: 192.168.1.50 |
|             |       Host: dev.target.com           |                   |
+------+------+                                      +---------+---------+
       |                                                       |
       | <-----------------------------------------------------|
       |               HTTP/1.1 200 OK (dev site)              |
       v                                                       |
+------+------+       GET / HTTP/1.1                 +---------+---------+
|             |       Host: api.target.com           |                   |
|   Matcher   |------------------------------------->|  Routing Engine   |
|   Filter    |                                      |  (Nginx/Apache)   |
|             |<-------------------------------------|                   |
+------+------+       HTTP/1.1 403 Forbidden         +-------------------+
       |
       | Result Log (Filtered out the 403 based on baseline)
       v
  [200] dev.target.com (Size: 4500)
```

## 7. Output and Integration Workflows
`ffuf` generates clean, highly parseable output designed for toolchain integration.
*   `-o results.json -of json`: Outputs findings in JSON, perfect for piping into `jq` for filtering or integrating into custom bash/python scripts.
*   `-o results.ejson -of ejson`: Outputs everything, including the full raw HTTP request and response for later detailed analysis.

### 7.1 Burp Suite Proxy Integration
A highly effective workflow is to use `ffuf`'s raw speed to find live endpoints, and then route those interesting requests into Burp Suite for deep manual testing.
```bash
# Proxying all traffic (Noisy)
ffuf -w paths.txt -u https://target.com/FUZZ -x http://127.0.0.1:8080

# Replay Proxy (Stealthy/Clean)
ffuf -w paths.txt -u https://target.com/FUZZ -replay-proxy http://127.0.0.1:8080
```
*The `-replay-proxy` flag is incredibly useful. It only sends successful matches (based on your matchers/filters) to Burp. This keeps your Burp HTTP history incredibly clean, saving you from sorting through thousands of 404s.*

## 8. Chaining Opportunities
*   **[[20 - Gobuster DNS Dir VHost modes]]:** Use Gobuster's specialized DNS mode for initial broad-scope subdomain discovery across an entire root domain. Feed the resulting list of live subdomains into `ffuf` for aggressive, multi-threaded parameter and directory fuzzing.
*   **[[16 - Burp Suite Pro Complete Feature Reference]]:** As detailed above, use `ffuf`'s `-replay-proxy` to populate Burp's site map only with valid, discovered endpoints, skipping the noise and preparing the environment for Burp's Active Scanner.

## 9. Related Notes
*   [[06 - API6 — Mass Assignment]] - Use `ffuf` to fuzz JSON POST bodies with a dictionary of common administrative parameter names (`is_admin`, `role`, `permissions`) to test for mass assignment vulnerabilities.
*   [[08 - API8 — Security Misconfiguration]] - `ffuf` is vital for discovering exposed backup files (`.bak`, `.swp`), `.git` directories, `.env` files, and unlinked legacy admin panels.
*   [[03 - API3 — Broken Object Property Level Authorization]] - Fuzz API endpoints to uncover hidden data fields being returned in anomalous responses by utilizing size matchers (`-ms`).
