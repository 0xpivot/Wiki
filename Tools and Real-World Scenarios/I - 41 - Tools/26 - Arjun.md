---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.26 Arjun"
---

# 26 - Arjun

## 1. Introduction and Core Philosophy

Arjun is an open-source, highly specialized HTTP parameter discovery tool.
In modern web applications, web endpoints often accept hidden, undocumented, or forgotten parameters (e.g., `?debug=true`, `?admin=1`, `?user_id=5`).
These parameters can lead to critical vulnerabilities such as Local File Inclusion (LFI), Server-Side Request Forgery (SSRF), Cross-Site Scripting (XSS), or Information Disclosure.

The core philosophy of Arjun is speed and precision.
Brute-forcing parameters by sending one request per word in a dictionary is incredibly slow and noisy.
Arjun solves this by heavily chunking parameters, identifying heuristic delays, and using complex reflection analysis to determine which parameters the server is actually processing.

## 2. Architecture and Internal Mechanics

Arjun's architecture is built around reducing the number of total HTTP requests required to discover a parameter.
It utilizes a mathematical approach to chunking, similar to a binary search.

```text
+-----------------------------------------------------------------------+
|                                 Arjun                                 |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ Target URL (e.g., api/users) ]     [ Parameter Wordlist ]         |
|                     |                            |                    |
|                     v                            v                    |
|   +---------------------------------------------------------------+   |
|   |                   Chunking & Batching Engine                  |   |
|   |  (Groups 500 parameters into a single HTTP request)           |   |
|   +---------------------------------------------------------------+   |
|                                |                                      |
|                                v                                      |
|   +---------------------------------------------------------------+   |
|   |                   HTTP Request Dispatcher                     |   |
|   |        (Sends GET/POST/JSON requests to target)               |   |
|   +---------------------------------------------------------------+   |
|                                |                                      |
|                                v                                      |
|   +---------------------------------------------------------------+   |
|   |                  Reflection & Heuristic Engine                |   |
|   | - Checks if a parameter altered the HTTP Status Code          |   |
|   | - Checks if parameter names/values are reflected in the body  |   |
|   | - Checks for anomalous Time Delays                            |   |
|   +---------------------------------------------------------------+   |
|                                |                                      |
|   [ Binary Search Reduction ]<-+ (If a chunk causes a change,     |   |
|                                   split it and test again)        |   |
|                                |                                      |
|                                v                                      |
|                [ Valid Hidden Parameters Discovered ]                 |
|                                                                       |
+-----------------------------------------------------------------------+
```

If a chunk of 500 parameters is sent and the server response is identical to the baseline, Arjun discards all 500 parameters immediately.
If the response changes, Arjun splits the chunk into smaller pieces, narrowing down until the exact valid parameter is identified.

## 3. Key Features and Usage

### 3.1 Basic Parameter Discovery (GET Requests)

The most common usage is discovering hidden parameters in a simple GET request.
Arjun includes a highly optimized default wordlist of common parameters.

```bash
# Basic discovery on a target URL
arjun -u https://example.com/api/v1/endpoint
```

### 3.2 Discovering POST and JSON Parameters

Modern APIs rarely rely solely on GET parameters.
Arjun excels at discovering parameters in JSON bodies or standard form-encoded POST requests.

```bash
# Discovering parameters in a standard POST request
arjun -u https://example.com/login -m POST

# Discovering parameters in a JSON API endpoint
arjun -u https://example.com/api/update -m JSON
```

### 3.3 Specifying Custom Wordlists

While the default wordlist is excellent, penetration testers often use larger lists (like those from SecLists) for deep enumeration.

```bash
# Using a custom wordlist
arjun -u https://example.com/api/user -w /path/to/parameters.txt
```

### 3.4 Handling Authentication and Headers

When testing authenticated endpoints, Arjun allows the inclusion of custom HTTP headers, such as Authorization tokens or Cookies.

```bash
# Passing an Authorization header
arjun -u https://example.com/api/secure --headers "Authorization: Bearer token123"

# Passing multiple headers
arjun -u https://example.com/api/secure --headers "Cookie: session=xyz; X-Forwarded-For: 127.0.0.1"
```

## 4. Advanced Configuration and Tuning

Arjun's heuristic engine is powerful, but aggressive Web Application Firewalls (WAFs) can sometimes block requests containing hundreds of parameters.
Tuning the chunk size and thread count is critical for bypassing WAFs and maintaining stability.

- **Chunk Size (`-c`):** Determines how many parameters are sent in a single request. If the server throws a `414 URI Too Long` or a WAF blocks it, lower this number.
  ```bash
  # Lowering the chunk size to 100 parameters per request
  arjun -u https://example.com/api/test -c 100
  ```

- **Thread Count (`-t`):** Controls concurrency. Lowering threads is essential for fragile APIs.
  ```bash
  # Limiting concurrency to 5 threads
  arjun -u https://example.com/api/test -t 5
  ```

- **Delay (`-d`):** Introduces a delay between requests to evade rate-limiting.
  ```bash
  arjun -u https://example.com/api/test -d 2
  ```

## 5. Interpreting Results

When Arjun identifies a valid parameter, it specifies how the server reacted:
- **Heuristic:** The server responded differently compared to the baseline (e.g., content length changed).
- **Reflected:** The parameter name or value was explicitly reflected in the HTML/JSON response, making it a prime candidate for XSS.
- **Status Code:** The parameter caused the server to return a different status code (e.g., jumping from 200 OK to 403 Forbidden).

## 6. Common Pitfalls and Limitations

1. **WAF Blocking:** Because Arjun sends highly anomalous requests (URLs packed with 500 parameters), modern WAFs often flag it as malicious activity immediately.
2. **False Positives on Dynamic Pages:** If a webpage includes dynamic content (like a timestamp or random CSRF token) in its response body, Arjun might interpret the changing content length as a valid parameter response. It uses stability checks to mitigate this, but it isn't perfect.
3. **Destructive Actions:** Parameter brute-forcing can unintentionally trigger destructive actions if you hit a parameter like `?delete=all` or `?reset=true`.

## 7. Practical Assessment Scenarios

### 7.1 Finding SSRF in Image Export
During a web application test, an auditor finds an endpoint `/export_pdf`.
They run Arjun and discover a hidden parameter `?url=`.
Passing an internal IP to this parameter `?url=http://169.254.169.254/latest/meta-data/` results in an SSRF vulnerability, revealing AWS cloud credentials.

### 7.2 Privilege Escalation via Hidden Parameter
On a profile update endpoint `/api/profile`, Arjun discovers an undocumented JSON parameter `{"role": ""}`.
Changing this to `{"role": "admin"}` results in an administrative privilege escalation.

## 8. Chaining Opportunities

- **[[08 - Httpx]]**: Httpx is used to find live endpoints. Those endpoints are then fed into Arjun for deep parameter discovery.
- **[[32 - SQLMap]]**: Once a parameter is discovered by Arjun, it is fed directly into SQLMap to test for SQL Injection vulnerabilities.
- **[[22 - Amass]]**: Subdomains discovered by Amass host the applications that Arjun will ultimately test.
- **[[23 - Subfinder]]**: Similar to Amass, discovering the infrastructure is the first step before Arjun can analyze the application layer.

## 9. Related Notes

- [[07 - Web Application Testing Methodologies]]
- [[17 - Server-Side Request Forgery (SSRF)]]
- [[18 - Local File Inclusion (LFI)]]
- [[24 - theHarvester]]
- [[25 - Shodan CLI]]
