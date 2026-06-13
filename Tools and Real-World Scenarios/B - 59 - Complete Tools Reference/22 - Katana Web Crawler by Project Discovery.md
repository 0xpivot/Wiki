---
tags: [tools, web-testing, crawler, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.22 Katana Web Crawler"
---

# Katana Web Crawler by Project Discovery

## 1. Executive Summary & Overview
Katana is a cutting-edge, extremely fast, and highly configurable web crawler built by Project Discovery. In the modern landscape of Web Application Penetration Testing (VAPT), legacy crawlers fail drastically against complex Single Page Applications (SPAs) driven by dynamic JavaScript frameworks like React, Angular, and Vue. Katana bridges the gap between static HTML parsing and dynamic DOM rendering.

## 2. Core Architectural Philosophy
### 2.1. Dual-Engine Parsing
Katana natively supports both standard HTTP-based static parsing and Headless Browser-based dynamic parsing.
### 2.2. Modularity and Pipeline Integration
Like all Project Discovery tools, Katana strictly adheres to the Unix philosophy. It produces clean, JSON-structured output.
### 2.3. Heuristic Extraction
Katana utilizes advanced heuristics to identify JavaScript variables containing paths, hidden form fields, and dynamic API construction logic.

## 3. ASCII Architecture Diagram
```text
+---------------------------------------------------------------------------------------+
|                                KATANA CRAWLER ENGINE                                  |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   |  Target URLs  |----->|  Input Normalization &  |----->|   Crawl Strategy      |   |
|   |  (Stdin/File) |      |  Scope Management       |      |   (Depth, Scope)      |   |
|   +---------------+      +-------------------------+      +-----------+-----------+   |
|                                                                       |               |
|                                                                       v               |
|                                                           +-----------------------+   |
|                                                           |                       |   |
|                                                   +-------|  Execution Engine     |---+
|                                                   |       |                       |   |
|                                                   v       +-----------------------+   v
|                                       +-----------------------+       +-----------------------+
|                                       |                       |       |                       |
|                                       |  Static HTTP Parser   |       | Headless Browser (JS) |
|                                       |  (Fast, Lightweight)  |       | (DOM Rendering)       |
|                                       |                       |       |                       |
|                                       +-----------+-----------+       +-----------+-----------+
|                                                   |                               |
|                                                   v                               v
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | Output Formats|<-----|  Results Formatter      |<-----|  Heuristic Extractor  |   |
|   | (JSON, Text)  |      |  (Deduplication)        |      |  (Links, Forms, APIs) |   |
|   +---------------+      +-------------------------+      +-----------------------+   |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

## 4. Deep Dive into Features and Mechanics
### 4.1. Headless Browser Integration
The `-hl` (headless) flag instructs Katana to spin up a Chromium instance to render the target.
### 4.2. Deep Crawl Configuration
Operators have granular control over the crawl scope (Depth, Scope bounds).

## 5. Practical Implementation and Advanced Use Cases
### 5.1. Headless Dynamic Crawl
```bash
katana -u https://spa.example.com -hl -d 3 -cs sub
```
### 5.2. Pipeline Extraction
```bash
katana -u https://example.com -jc | grep "\.js$" | httpx -silent
```

## 6. Comprehensive Command Line Reference
1. `-u, --url`: Target URL.
2. `-list`: File containing a list of target URLs.
3. `-d, --depth`: Maximum depth to crawl (default 3).
4. `-jc, --js-crawl`: Enable parsing of endpoints in JavaScript files.
5. `-hl, --headless`: Enable headless browser mode.
6. `-cs, --crawl-scope`: Scope of crawling (`sub`, `rd`).
7. `-f, --field`: Fields to extract (`url`, `path`, `fqdn`).
8. `-H, --headers`: Custom headers to include in requests.
9. `-p, --proxy`: HTTP/SOCKS proxy.
10. `-j, --json`: Output in JSON format.
11. `-c, --concurrency`: Number of concurrent workers.
12. `-rl, --rate-limit`: Maximum requests per second.
13. `-delay`: Delay between requests.
14. `-timeout`: Connection timeout.
15. `-retry`: Number of retries for failed requests.
16. `-silent`: Suppress output and only print results.
17. `-v, --verbose`: Verbose logging.
18. `-do, --crawl-out-scope`: Crawl external out-of-scope domains.
19. `-iqp, --ignore-query-params`: Ignore query params.
20. `-kf, --known-files`: Add robots.txt and sitemaps.
21. `-ho, --headless-options`: Custom Chromium flags.
22. `-sc, --system-chrome`: Use local Chrome installation.
23. `-sh, --show-browser`: Display the GUI browser window.
24. `-rd, --retries`: Retry limits for the headless engine.
25. `-fx, --form-extraction`: Extract form data explicitly.

## 7. Extended Troubleshooting Guide
1. **OOM Killer / Memory Exhaustion**: Headless uses lots of RAM. Lower `-c`.
2. **Hanging Process**: Add `-timeout 10`.
3. **No Results**: Use `-kf` to force known paths.
4. **Bypassing Cloudflare**: Use `-hl` and custom `-H "User-Agent: ..."`.
5. **JSON Parsing Errors**: Use `-silent` with `-j`.
6. **Missing JS Endpoints**: Ensure `-jc` is passed.
7. **Chrome Crash**: Ensure system dependencies for Chromium exist.
8. **Proxy Timeout**: Validate proxy connection limits.
9. **Authentication Failure**: Verify cookie injection format.
10. **Crawling Infinity**: Check `-d` depth limits.
11. **Subdomain Hopping Failed**: Verify `-cs sub` is active.
12. **Too Slow**: Increase `-c` if not in headless mode.
13. **Blocked IP**: Use proxy rotation.
14. **DOM Not Fully Rendered**: Introduce custom delays.
15. **Form Extraction Fails**: Site might use custom GraphQL APIs.
16. **Dependency Errors**: Run `katana -up` to update.
17. **SSL Issues**: Target uses invalid certificates.
18. **Unwanted External Links**: Do not use `-do`!
19. **Localhost Issues**: Katana blocks loopback by default.
20. **Duplicate Results**: Pipe to `sort -u` or `uro`.

## 8. Continuous Integration (CI/CD) Checklist
1. [ ] Install latest Katana release.
2. [ ] Identify target staging URL.
3. [ ] Set up headless dependencies in Docker.
4. [ ] Define `-d 2` to prevent CI timeouts.
5. [ ] Pass authentication cookies via Action Secrets.
6. [ ] Enable `-jc` to find new JS routes.
7. [ ] Save JSON output as artifact.
8. [ ] Diff output with previous baseline.
9. [ ] Alert on any new unauthenticated API endpoints.
10. [ ] Fail build if admin routes leak.
11. [ ] Restrict concurrency to avoid DOSing staging.
12. [ ] Monitor CI runner RAM usage.
13. [ ] Use `jq` to format the Slack alert message.
14. [ ] Ignore static assets (.png, .css).
15. [ ] Feed output into DAST scanners.
16. [ ] Test with System Chrome (`-sc`) for stability.
17. [ ] Store output in an S3 bucket for auditing.
18. [ ] Integrate with project management (Jira).
19. [ ] Validate output against OpenAPI specs.
20. [ ] Schedule daily delta scans.

## 9. Advanced Usage Scenarios
- **Secret Hunting**: Piping raw JS files into `trufflehog`.
- **Attack Surface Mapping**: Feeding the output to `amass`.

## 10. Related Notes
- [[10 - Directory and File Brute-Forcing]]
- [[35 - Automated Reconnaissance Pipelines]]
- [[23 - Hakrawler Fast Web Crawler]]
- [[25 - waybackurls Wayback Machine URL Fetcher]]
- [[01 - Ffuf Fast Web Fuzzer]]
- [[21 - Feroxbuster Recursive with Smart Filtering]]

## 11. Appendix: Exhaustive Glossary & Deep Tuning Variables
To truly master this tool, operators must be familiar with the following environmental variables and edge-case configurations.
1. `HTTP_PROXY`: Specifies the proxy server for HTTP requests.
2. `HTTPS_PROXY`: Specifies the proxy server for HTTPS requests.
3. `NO_PROXY`: Comma-separated list of hosts to bypass the proxy.
4. `TIMEOUT_MS`: Absolute timeout in milliseconds for socket operations.
5. `MAX_RETRIES`: Maximum number of retries for dropped connections.
6. `TCP_KEEPALIVE`: Enables TCP keepalive probes.
7. `USER_AGENT`: The default User-Agent string.
8. `TLS_VERIFY`: Boolean flag to enforce strict TLS validation.
9. `DNS_RESOLVER`: Custom IP for resolving hostnames.
10. `MAX_CONCURRENCY`: Hard limit on the global thread pool.
11. `RATE_LIMIT_RPS`: Maximum requests allowed per second.
12. `PAYLOAD_MARKER`: The specific string (e.g., `FUZZ`) used for injection.
13. `OUTPUT_DIR`: The default directory for saving scan artifacts.
14. `DEBUG_MODE`: Enables highly verbose tracing information.
15. `LOG_LEVEL`: Standard logging levels (TRACE, INFO, WARN, ERROR).
16. `IGNORE_CODES`: HTTP status codes that will be completely ignored.
17. `MATCH_CODES`: HTTP status codes that trigger a positive match.
18. `MAX_DEPTH`: The deepest level the crawler/brute-forcer will go.
19. `FOLLOW_REDIRECTS`: Whether to automatically follow 301/302 responses.
20. `MAX_REDIRECTS`: Maximum redirect hops to follow to prevent loops.
21. `COOKIE_STRING`: Raw cookie string to inject into all headers.
22. `HEADER_AUTHORIZATION`: Bearer token for API endpoints.
23. `EXTENSIONS_LIST`: Comma-separated list of extensions (`php,txt,bak`).
24. `WORDLIST_PATH`: Absolute path to the dictionary file.
25. `JSON_OUTPUT_FORMAT`: Forces logs into single-line JSON objects.
26. `CSV_OUTPUT_FORMAT`: Outputs results as comma-separated values.
27. `SQL_BACKEND`: URI for storing state in a relational database.
28. `DISABLE_BANNERS`: Removes ASCII art from the standard output.
29. `COLOR_OUTPUT`: Enables or disables ANSI color codes.
30. `SILENT_MODE`: Mutes all output except successful hits.
31. `RESUME_STATE_FILE`: Path to the state file for resuming scans.
32. `AUTO_CALIBRATE`: Enables automatic baseline generation.
33. `RANDOM_DELAY_MS`: Introduces jitter between requests to avoid WAFs.
34. `MAX_BODY_SIZE`: Limits the amount of the response body read into memory.
35. `IGNORE_EMPTY_BODIES`: Drops any response with a 0-byte length.
36. `EXTRACT_COMMENTS`: Parses HTML responses for `<!-- -->` data.
37. `EXTRACT_JS`: Specifically pulls `.js` file paths from the DOM.
38. `EXTRACT_FORMS`: Pulls action URLs and input fields from `<form>` tags.
39. `MATCH_REGEX`: A PCRE regex that must match for a result to be valid.
40. `FILTER_REGEX`: A PCRE regex that invalidates a result if matched.
41. `MATCH_WORDS`: Number of words the response body must contain.
42. `FILTER_WORDS`: Number of words that invalidates the response.
43. `MATCH_LINES`: Number of lines the response body must contain.
44. `FILTER_LINES`: Number of lines that invalidates the response.
45. `SYSTEM_RESOLVER`: Forces the use of `/etc/resolv.conf`.
46. `INSECURE_CIPHERS`: Allows connection to legacy SSLv3/TLS1.0 servers.
47. `CLIENT_CERT`: Path to a PEM encoded client certificate for mTLS.
48. `CLIENT_KEY`: Path to the private key for the client certificate.
49. `SNI_SPOOFING`: Allows setting a custom Server Name Indication.
50. `HOST_HEADER`: Overrides the standard `Host` HTTP header.
51. `X_FORWARDED_FOR`: Injects a spoofed origin IP.
52. `CACHE_CONTROL`: Manually sets the cache directives.
53. `ACCEPT_ENCODING`: Configures gzip/deflate/br support.
54. `CONNECTION_CLOSE`: Forces `Connection: close` on every request.
55. `HTTP2_ONLY`: Forces the client to use HTTP/2 protocol.
56. `HTTP3_QUIC`: Enables experimental QUIC support.
57. `SOCKS5_PROXY`: Specific protocol identifier for SOCKS routing.
58. `PROXY_AUTH`: Credentials for authenticated proxies (`user:pass`).
59. `PAC_FILE`: Path to a Proxy Auto-Configuration file.
60. `THROTTLE_ON_ERRORS`: Automatically reduces threads if 500s spike.
61. `ERROR_THRESHOLD`: Number of errors before the scan aborts entirely.
62. `MEMORY_PROFILER`: Dumps runtime memory statistics for debugging.
63. `CPU_PROFILER`: Generates flame graphs for thread analysis.
64. `DUMP_TRAFFIC`: Saves raw PCAP-style HTTP requests and responses.
65. `REPLAY_PROXY`: Sends traffic to a secondary proxy (like Burp) for logging.
66. `WEBHOOK_URL`: Sends POST requests to this URL when a hit is found.
67. `SLACK_TOKEN`: Integrates directly with Slack for alerting.
68. `DISCORD_WEBHOOK`: Integrates directly with Discord.
69. `JIRA_API_KEY`: Automatically opens tickets for critical findings.
70. `EXCLUDE_IPS`: List of IP addresses to never scan (e.g., DOD space).
71. `INCLUDE_IPS`: Strict whitelist of allowed target IPs.
72. `RESOLVE_STRATEGY`: Dictates IPv4 vs IPv6 preference.
73. `CACHE_TTL`: Time-to-live for internal DNS cache.
74. `FILE_DESCRIPTOR_LIMIT`: Internal override for `ulimit`.
75. `STRICT_PATH_PARSING`: Prevents normalization of `../` in paths.
76. `ALLOW_INVALID_CERTS`: Alias for TLS_VERIFY=false.
77. `CHUNKED_TRANSFER`: Supports testing TE.CL / CL.TE desyncs.
78. `HTTP_METHODS`: Comma-separated list of methods (GET, POST, PUT).
79. `CUSTOM_PAYLOAD_GEN`: Invokes an external script to generate payloads.
80. `EXIT_ON_FIRST_MATCH`: Immediately stops execution once a target is found.
81. `DYNAMIC_WORDLIST`: Appends discovered paths to the active queue.
82. `FUZZ_HEADERS`: Specifically targets HTTP headers for injection.
83. `FUZZ_COOKIES`: Specifically targets the Cookie string.
84. `FUZZ_BODY`: Targets POST/PUT bodies.
85. `HTML_REPORT`: Generates a static HTML dashboard of results.
86. `MARKDOWN_REPORT`: Generates an Obsidian-compatible markdown file.
87. `NUCLEI_INTEGRATION`: Automatically pipes output to the Nuclei engine.
88. `CUSTOM_TEMPLATES`: Path to user-defined YAML templates.
89. `INTERACTIVE_MODE`: Allows pausing and modifying scans mid-flight.
90. `DAEMON_MODE`: Runs the tool as a background service listening on a port.
