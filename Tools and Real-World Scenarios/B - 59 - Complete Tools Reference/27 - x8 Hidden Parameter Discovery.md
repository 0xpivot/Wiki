---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.27 x8 Hidden Parameter Discovery"
---

# x8: High-Performance Hidden Parameter Discovery

## 1. Introduction and Core Concepts
x8 is a modern, ultra-fast hidden parameter discovery tool written in Rust. While tools like Arjun pioneered the heuristic batching approach for parameter discovery, x8 takes these concepts and optimizes them for raw speed and concurrency. In the realm of web application penetration testing and bug bounty hunting, time is often the most critical resource. x8 is designed to map out hidden attack surface—undocumented API parameters, legacy debugging variables, and developer backdoors—at blinding speeds.

The primary advantage of x8 over its predecessors is its memory safety and low overhead execution, courtesy of the Rust language. It also introduces more aggressive heuristics and advanced comparison algorithms to deal with highly dynamic web applications that would otherwise produce false positives.

## 2. How the Tool Works (Internal Mechanics)
Like Arjun, x8 does not fuzz parameters one-by-one. It uses a divide-and-conquer algorithm (binary search logic) applied to HTTP parameter injection. 

x8 calculates a "baseline" response from the server by sending a request with randomized, non-existent parameters. It records the status code, response length, headers, and body hash. When testing real parameters, it injects them in large batches. If a batch alters the response beyond the calculated variance of the baseline, x8 splits the batch in half and tests both halves, continually dividing until the exact parameter causing the variance is identified.

### ASCII Diagram: x8 Architecture & Flow

```text
[ Input: Target URL + Wordlist ]
         |
         v
+---------------------------------------------------+
| 1. Baseline Calibration Phase                     |
| Sends 5-10 requests with random junk parameters   |
| Calculates dynamic content variance (e.g., CSRF)  |
+---------------------------------------------------+
         |
         v
+---------------------------------------------------+
| 2. Batch Execution Phase (Rust Async/Await)       |
| Worker 1: ?param1=1...param500=1                  |
| Worker 2: ?param501=1...param1000=1               |
| Worker 3: ?param1001=1...param1500=1              |
+---------------------------------------------------+
         |
         v
[ Anomalous Response Detected in Worker 2! ]
         |
         v
+---------------------------------------------------+
| 3. Binary Isolation Phase                         |
| Split 501-1000 into 501-750 and 751-1000          |
| Recurse until isolation: ?hidden_debug_mode=1     |
+---------------------------------------------------+
         |
         v
[ Output to JSON / CLI ]
```

## 3. Installation & Setup
Because x8 is built in Rust, it can be compiled from source via `cargo` or downloaded as a pre-compiled, statically linked binary. The pre-compiled binaries are highly recommended as they run without any dependencies on almost any Linux distribution.

```bash
# Option 1: Download Pre-compiled Binary (Recommended)
wget https://github.com/Sh1yo/x8/releases/latest/download/x8-linux.tar.gz
tar -xvf x8-linux.tar.gz
sudo mv x8 /usr/local/bin/

# Option 2: Install via Cargo (Requires Rust Toolchain)
cargo install x8

# Verify Installation
x8 --help
```

## 4. Basic Usage & Common Flags
x8 is designed with a straightforward syntax that mimics other popular CLI bug bounty tools, making it easy to integrate into existing workflows.

```bash
# Basic parameter discovery on a GET endpoint
x8 -u "https://api.example.com/v1/config" -w /path/to/wordlist.txt

# Post parameter discovery
x8 -u "https://api.example.com/v1/login" -X POST -w parameters.txt
```

### Core CLI Flags:
- `-u, --url`: The target URL to test.
- `-w, --wordlist`: Wordlist containing parameters.
- `-X, --method`: HTTP method (GET, POST, PUT, DELETE).
- `-W, --workers`: Number of concurrent workers (Default is highly optimized).
- `-c, --custom-parameters`: Inject custom parameters into every request.
- `--headers`: Add custom headers (e.g., for authentication).
- `-O, --output`: File to write the output.

## 5. Advanced Configuration & Tuning

### 5.1 Handling Dynamic Content and WAFs
Modern web apps frequently inject dynamic content into every response (timestamps, nonces, CSRF tokens). x8 uses a sophisticated comparison engine to ignore these dynamic elements. If the default engine struggles, you can tune the similarity threshold.

```bash
# Adjusting the similarity threshold (e.g., 95% similarity)
x8 -u "https://target.com/page" -w words.txt --tolerance 5
```

If a Web Application Firewall (WAF) blocks requests with too many parameters, you can reduce the chunk size, similar to Arjun.

```bash
# Limit the maximum parameters sent per request
x8 -u "https://target.com/api" -w words.txt --max-params 50
```

### 5.2 Template Parameter Fuzzing
x8 allows for specific payload injection templates. Instead of just appending parameters, you can define exactly where and how they should be injected using template syntax.

```bash
# Fuzzing JSON bodies directly
x8 -u "https://api.example.com/update" -X POST \
   --headers "Content-Type: application/json" \
   --body '{"user":"admin", "%s":"%s"}' \
   -w params.txt
```
In this example, x8 will replace `%s` with the parameter names and values, dynamically expanding the JSON payload during the batch phase.

## 6. Output Formats & Parsing
x8 supports multiple output formats designed for pipelining. You can output results in plain text or JSON.

```bash
x8 -u "https://api.example.com" -w params.txt -O json_output.json
```

Sample JSON Output:
```json
{
  "url": "https://api.example.com",
  "method": "GET",
  "parameters": {
    "admin_bypass": "1",
    "debug_sql": "1"
  }
}
```

## 7. Real-world Scenarios
### 7.1 Exploiting Bypasses via Hidden Headers
While primarily a parameter tool, x8 can also be utilized to discover hidden headers by feeding it a header wordlist and using the template injection method. Discovering a header like `X-Forwarded-Host` or `X-Custom-IP-Authorization` can lead directly to authentication bypasses or SSRF.

### 7.2 API Versioning Discovery
Sometimes legacy API functionality is hidden behind query parameters rather than URL paths. Using x8, you might find parameters like `?v=1.0` or `?version=beta` on a `v2` endpoint, forcing the application to downgrade its routing to a vulnerable, deprecated codebase.

## 8. Chaining Opportunities
Because of its immense speed, x8 is often deployed across entire environments rather than just single endpoints.

1. **Katana / Hakrawler** -> Spider a target to find all active endpoints.
2. **x8** -> Run against the compiled list of endpoints to discover hidden parameters.
3. **Kxss / Dalfox** -> Feed the x8 output to XSS scanners.

### Mass Execution Example
If you have a list of URLs in `urls.txt`:
```bash
cat urls.txt | xargs -I {} x8 -u {} -w params.txt -O output_{}.json
```
*(Note: x8 also natively supports multi-url inputs in newer versions)*

## 9. Limitations vs Arjun
While x8 is significantly faster than Arjun, Arjun sometimes has an edge in extremely complex heuristic edge-cases due to years of community-driven Python regex tuning. x8 is preferred for speed and mass-scanning, while Arjun is often reserved for deep, surgical analysis of a single, brittle, highly dynamic endpoint where x8's fast execution might cause server instability.

## 10. Related Notes
- [[26 - arjun Parameter Discovery]] - The Python predecessor to x8.
- [[28 - ParamSpider Parameter Mining from Web Archives]] - Passive parameter discovery.
- [[04 - API4 — Lack of Resources & Rate Limiting]] - Fast tools like x8 can inadvertently DoS an API lacking rate limits.
- [[06 - API6 — Mass Assignment]] - Exploiting the parameters discovered by x8.
