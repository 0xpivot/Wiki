---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.26 arjun Parameter Discovery"
---

# Arjun: Advanced Hidden Parameter Discovery

## 1. Introduction and Core Concepts
Arjun is an open-source, highly efficient command-line tool designed specifically to discover hidden HTTP parameters. Web applications often contain legacy, undocumented, or administrative parameters that are not exposed in the regular user interface or standard API documentation (like Swagger/OpenAPI). Finding these hidden parameters is critical in bug bounty hunting and professional penetration testing because they are frequently vulnerable to common web flaws such as Cross-Site Scripting (XSS), Server-Side Request Forgery (SSRF), Local File Inclusion (LFI), or Mass Assignment vulnerabilities.

Unlike traditional fuzzers that might send one request per parameter (which is extremely noisy and slow), Arjun uses a smart mathematical approach based on dynamic parameter batching. This significantly reduces the number of HTTP requests required to find a hidden parameter, allowing it to scan thousands of parameters in a fraction of the time.

## 2. How the Tool Works (Internal Mechanics)
Arjun's primary innovation is its heuristic and batch-based parameter discovery system. 

When Arjun is given a large wordlist of parameters, it doesn't test them one by one. Instead, it groups them into large chunks and sends them in a single request. By analyzing the server's response (e.g., Content-Length, HTTP Status Code, reflection in the response body), Arjun can determine if any parameter within that chunk caused a different behavior. If a chunk triggers a difference, Arjun recursively splits that chunk into smaller pieces and re-tests until it isolates the exact parameter responsible for the anomaly.

### ASCII Diagram: Arjun's Batching Logic

```text
[ Initial Wordlist: 10,000 Parameters ]
          |
          v
+---------------------------------------------------+
| Request 1: ?param1=a&param2=a&...&param1000=a     | ---> Baseline Response (Length: 500)
+---------------------------------------------------+
          |
          v
+---------------------------------------------------+
| Request 2: ?param1001=a&...&param2000=a           | ---> Anomaly Detected! (Length: 520)
+---------------------------------------------------+
          |
          v
   [ Split Chunk 2 into smaller chunks ]
          |
          +---> Request 2A (1001-1500) ---> Baseline
          |
          +---> Request 2B (1501-2000) ---> Anomaly Detect!
                  |
                  v
           [ Split Chunk 2B further until isolated ]
                  |
                  v
            Hidden Parameter Found: ?debug=true
```

## 3. Installation & Setup
Arjun is written in Python and is highly portable. It can be installed directly from PyPI or cloned from the official GitHub repository.

```bash
# Option 1: Install via pip (Recommended)
pip3 install arjun

# Option 2: Clone from GitHub
git clone https://github.com/s0md3v/Arjun.git
cd Arjun
python3 setup.py install

# Verify installation
arjun --help
```

### Dependencies
Arjun relies on standard Python networking libraries but also utilizes `concurrent.futures` for threading and multi-processing, which makes its chunking algorithm extremely fast. Make sure your Python environment is up to date (Python 3.4+ required).

## 4. Basic Usage & Common Flags
The basic usage of Arjun involves specifying a target URL. By default, it will use its built-in wordlist of common parameter names and test the GET method.

```bash
# Basic GET parameter discovery
arjun -u https://api.example.com/v1/users

# Basic POST parameter discovery (JSON format)
arjun -u https://api.example.com/v1/users -m POST -j

# Specify a custom wordlist
arjun -u https://api.example.com/v1/users -w /usr/share/wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt
```

### Core CLI Flags:
- `-u, --url`: Target URL.
- `-w, --wordlist`: Path to a custom wordlist.
- `-m, --method`: HTTP method to use (GET, POST, XML, JSON).
- `-t, --threads`: Number of concurrent threads (Default is 2).
- `-d, --delay`: Delay between requests (useful for bypassing rate limits).
- `-oJ, --json`: Output results in JSON format.
- `-oB, --burp`: Output results in Burp Suite compatible format.
- `-c, --chunk-size`: Define the chunk size for parameter grouping (Default: 250).

## 5. Advanced Configuration & Tuning
When dealing with enterprise-grade Web Application Firewalls (WAFs) or brittle legacy APIs, you need to tune Arjun carefully.

### 5.1 Handling WAFs and Rate Limits
WAFs like Cloudflare or Akamai will quickly block IP addresses that send too many parameters in a single request, or simply drop requests with huge query strings. You must lower the chunk size and increase the delay.

```bash
# Bypassing strict WAFs
arjun -u https://api.example.com/v1/admin -c 50 -d 1 -t 1
```
By setting chunk size (`-c`) to 50, Arjun sends fewer parameters per request. The `-d 1` flag adds a 1-second delay, and `-t 1` ensures requests are sent serially.

### 5.2 Header and Cookie Injection
Many hidden parameters are only accessible if the user is authenticated. You can pass headers directly via the CLI.

```bash
arjun -u https://example.com/api/profile \
  --headers "Authorization: Bearer eyJhbGci..." \
  --headers "Cookie: session_id=12345"
```

### 5.3 Working with Different Content Types
Arjun natively supports testing JSON and XML endpoints, which is crucial for modern API security testing.

```bash
# Testing a JSON endpoint
arjun -u https://api.example.com/v1/graphql -m JSON

# Testing an XML endpoint (legacy SOAP)
arjun -u https://api.example.com/v1/soap -m XML
```

## 6. Output Formats & Parsing
For automation and pipeline integration, Arjun provides excellent machine-readable output formats.

### 6.1 JSON Output
Using `-oJ arjun_results.json` creates a cleanly formatted file.

```json
{
  "https://api.example.com/v1/users": {
    "method": "GET",
    "params": [
      "debug",
      "admin",
      "test"
    ]
  }
}
```
This can easily be parsed by `jq` to pass discovered parameters into other tools like Nuclei or Ffuf.

### 6.2 Burp XML Output
The `-oB` flag generates an XML file that can be imported directly into Burp Suite's target tree, allowing you to seamlessly transition from parameter discovery to manual exploitation.

## 7. Real-world Scenarios
### 7.1 Discovering Mass Assignment Vulnerabilities
In Ruby on Rails or Node.js applications, mass assignment is a common flaw. By pointing Arjun at a user profile update endpoint, you might discover hidden parameters like `is_admin` or `role`.

```bash
arjun -u https://api.example.com/profile/update -m JSON -w custom_roles.txt
```
If Arjun discovers `role`, you can craft a POST request `{"name":"User","role":"admin"}` to attempt privilege escalation.

### 7.2 Finding SSRF via Hidden Callbacks
Developers often leave debugging endpoints that fetch external resources. Finding parameters like `url`, `callback`, `webhook`, or `dest` is a prime indicator for SSRF testing.

## 8. Chaining Opportunities
Arjun is rarely used in isolation. It forms the middle step of a comprehensive reconnaissance pipeline.

1. **Amass / Subfinder** -> Find subdomains.
2. **Waybackurls / Gau** -> Find historical endpoints.
3. **Arjun** -> Find hidden parameters on those endpoints.
4. **SQLMap / Dalfox** -> Test discovered parameters for SQLi / XSS.
5. **Nuclei** -> Test parameters against known CVE templates.

### Example Automation Script:
```bash
echo "https://target.com/api/user" | arjun -i - -oJ params.json
cat params.json | jq -r '.[] | .params[]' | while read param; do
  ffuf -w payloads.txt -u "https://target.com/api/user?$param=FUZZ"
done
```

## 9. Limitations and False Positives
While Arjun is incredibly powerful, it relies heavily on heuristic analysis. If an API returns dynamic content (e.g., timestamps, rotating CSRF tokens, or highly variable response lengths), Arjun might flag false positives.

To mitigate this, Arjun takes a baseline measurement before scanning, but erratic server behavior can still confuse the tool. Always manually verify the discovered parameters using an intercepting proxy like Burp Suite.

## 10. Related Notes
- [[27 - x8 Hidden Parameter Discovery]] - A faster alternative written in Rust.
- [[28 - ParamSpider Parameter Mining from Web Archives]] - Mining parameters passively without touching the target.
- [[01 - API1 — Broken Object Level Authorization (BOLA)]] - Hidden parameters often lead to BOLA.
- [[06 - API6 — Mass Assignment]] - The primary vulnerability associated with hidden state-changing parameters.
