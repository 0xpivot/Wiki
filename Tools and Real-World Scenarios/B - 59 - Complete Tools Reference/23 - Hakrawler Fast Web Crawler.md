---
tags: [tools, web-testing, crawler, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.23 Hakrawler Fast Web Crawler"
---

# Hakrawler Fast Web Crawler

## 1. Executive Summary & Overview
Hakrawler is a fast, simple, and highly effective Go-based web crawler designed specifically for penetration testers and bug bounty hunters. Created by Luke Stephens (Hakluke), its primary mandate is to consume a list of domains via standard input and rapidly extract endpoints, JavaScript files, and hidden links. Unlike heavy UI crawlers, it favors Unix pipelines.

## 2. Core Architectural Philosophy
### 2.1. The Unix Philosophy
Hakrawler is built strictly around standard input (`stdin`) and standard output (`stdout`).
### 2.2. Go Concurrency
Written in Go, Hakrawler leverages goroutines to process multiple domains and paths simultaneously.
### 2.3. Targeted Extraction
It specifically looks for actionable items: standard URLs, JavaScript file references, form endpoints, and hidden paths inside HTML comments.

## 3. ASCII Architecture Diagram
```text
+---------------------------------------------------------------------------------------+
|                                HAKRAWLER ARCHITECTURE                                 |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | STDIN Input   |----->|  Goroutine Dispatcher   |----->|  HTTP Client Workers  |   |
|   | (Subdomains)  |      |  (Concurrency Control)  |      |  (GET Requests)       |   |
|   +---------------+      +-------------------------+      +-----------+-----------+   |
|                                                                       |               |
|                                                                       v               |
|                                                           +-----------------------+   |
|                                                           |                       |   |
|                                                           |   Response Parser     |   |
|                                                           |                       |   |
|                                                           +-----------+-----------+   |
|                                                                       |               |
|                                                                       v               |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | STDOUT Output |<-----|  Type Classifier        |<-----|  Regex / Extraction   |   |
|   | (URLs, JS)    |      |  (Forms, URLs, JS)      |      |  (HTML, Comments)     |   |
|   +---------------+      +-------------------------+      +-----------------------+   |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

## 4. Deep Dive into Features and Mechanics
### 4.1. Input Handling
Hakrawler accepts input purely via stdin. Easily piped from `subfinder` or `amass`.
### 4.2. Output Categorization
Hakrawler prepends its output with the type of asset discovered (e.g., `[url]`, `[form]`, `[js]`).

## 5. Practical Implementation and Advanced Use Cases
### 5.1. Mass Reconnaissance Pipeline
```bash
subfinder -d example.com -silent | httpx -silent | hakrawler -depth 2 > crawled.txt
```
### 5.2. Extracting JavaScript Files
```bash
cat targets.txt | hakrawler | grep "\[js\]" | awk '{print $2}' > js_files.txt
```

## 6. Comprehensive Command Line Reference
1. `-depth`: Maximum depth to crawl (default 1).
2. `-cookie`: Provide custom cookies for authentication.
3. `-header`: Provide custom headers.
4. `-plain`: Output only the URLs without the type tags.
5. `-proxy`: Route traffic through an HTTP/SOCKS proxy.
6. `-timeout`: Connection timeout per request.
7. `-insecure`: Skip TLS verification.
8. `-size`: Max body size to read (prevents memory exhaustion).
9. `-subs`: Include subdomains in the crawl scope.
10. `-t`: Thread count for concurrent crawling.
11. `-u`: Pass a single URL directly instead of via stdin.
12. `-d`: Delay between requests to bypass rate limits.
13. `-json`: Output results as JSON.
14. `-tags`: Display the HTML tags alongside the URLs.
15. `-forms`: Extract and display form endpoints explicitly.
16. `-robots`: Crawl robots.txt automatically.
17. `-sitemap`: Parse sitemap.xml files explicitly.
18. `-v`: Verbose mode.
19. `-h`: Help menu.
20. `-version`: Print version information.
21. `-dump`: Dump raw responses for debugging.
22. `-strict`: Strict URL parsing.
23. `-exclude`: Exclude specific patterns.
24. `-match`: Only output matched patterns.
25. `-no-redirect`: Do not follow HTTP redirects.

## 7. Extended Troubleshooting Guide
1. **Tool Hanging**: Use `-timeout 5`.
2. **No Output**: Ensure stdin contains `http://` prefix.
3. **Memory Exhaustion**: Use `-size 500000` to limit body read.
4. **SSL Errors**: Pass `-insecure`.
5. **Rate Limiting Blocks**: Increase delay between requests.
6. **Missing JS files**: Target might render purely client-side; use Katana instead.
7. **Proxy Failure**: Ensure proxy is running on local port.
8. **JSON Malformed**: Target returns invalid characters.
9. **Depth Trap**: Target has calendar loops. Reduce depth.
10. **Authentication Fails**: Verify cookie syntax.
11. **Subdomains ignored**: Explicitly pass `-subs`.
12. **Too Fast**: Set `-t 1` for stealth mode.
13. **Blank Lines**: Target server dropping empty responses.
14. **WAF Blocked**: Inject custom User-Agent via `-header`.
15. **Cannot Resolve Host**: DNS issue, use reliable resolvers.
16. **Redirect Loops**: Hakrawler handles them gracefully, but they can slow things down.
17. **Duplicate URLs**: Always pipe to `sort -u`.
18. **Forms not parsed**: Target uses Angular HTTPClient instead of HTML forms.
19. **Large Outputs**: Write to a file immediately.
20. **Binary Corrupted**: Recompile from source.

## 8. Continuous Integration (CI/CD) Checklist
1. [ ] Configure GitHub Runner.
2. [ ] Pipe known endpoints into Hakrawler.
3. [ ] Use `-plain` to extract raw URLs.
4. [ ] Pipe outputs to a diff engine.
5. [ ] Alert if new `[form]` tags are found.
6. [ ] Download all `[js]` files.
7. [ ] Run `trufflehog` on the JS files.
8. [ ] Ignore 404 links dynamically.
9. [ ] Run with authentication tokens.
10. [ ] Schedule weekly executions.
11. [ ] Send results to a centralized SIEM.
12. [ ] Filter out external domains.
13. [ ] Protect staging databases from aggressive crawls.
14. [ ] Add custom headers to bypass WAF.
15. [ ] Use `jq` if `-json` is utilized.
16. [ ] Store output in S3 bucket.
17. [ ] Cross-reference with API documentation.
18. [ ] Verify robots.txt hasn't expanded sensitive paths.
19. [ ] Automatically check for exposed .git folders.
20. [ ] Block known tarpits in the CI pipeline.

## 9. Advanced Usage Scenarios
- **Secret Hunting**: Fetching all JS files and searching for hardcoded API keys.
- **Form Bruteforcing**: Extracting all forms and feeding them to `ffuf`.

## 10. Related Notes
- [[22 - Katana Web Crawler by Project Discovery]]
- [[24 - gau GetAllUrls from Wayback and OTX]]
- [[25 - waybackurls Wayback Machine URL Fetcher]]
- [[10 - Directory and File Brute-Forcing]]
- [[35 - Automated Reconnaissance Pipelines]]
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
