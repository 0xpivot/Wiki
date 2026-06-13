---
tags: [tools, web-testing, crawler, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.21 Feroxbuster Recursive with Smart Filtering"
---

# Feroxbuster: Recursive Directory Discovery with Smart Filtering

## 1. Executive Summary & Overview
Feroxbuster is a highly concurrent, remarkably fast, and deeply customizable directory discovery tool written in Rust. Born out of the necessity to combine speed, smart filtering, and recursive scanning capabilities into a single utility, Feroxbuster has become an indispensable asset in modern Web Application Penetration Testing (VAPT), bug bounty hunting, and red teaming engagements.

## 2. Core Architectural Philosophy
### 2.1. Concurrency and Asynchronous Execution
Built on top of Rust's asynchronous runtime (Tokio) and utilizing the `reqwest` HTTP library, Feroxbuster can saturate network links without exhausting system resources. It multiplexes thousands of network connections simultaneously.
### 2.2. Automated Recursion
Instead of manually feeding newly discovered directories back into a tool, Feroxbuster autonomously handles recursive enumeration based on user-defined depth and constraints.
### 2.3. Smart Filtering
Web servers are notorious for lying. They return `200 OK` for nonexistent pages (soft 404s) or dynamically generate error pages. Feroxbuster implements sophisticated filtering based on status codes, line counts, word counts, character counts, and regular expressions.

## 3. ASCII Architecture Diagram
```text
+---------------------------------------------------------------------------------------+
|                              FEROXBUSTER INTERNAL ARCHITECTURE                        |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +-------------------+      +-----------------------+      +---------------------+   |
|   |                   |      |                       |      |                     |   |
|   | Wordlist Iterator |----->|  Target Queue Engine  |----->| HTTP Request Builder|   |
|   |                   |      |  (URLs + Exts)        |      |                     |   |
|   +-------------------+      +-----------------------+      +----------+----------+   |
|                                                                        |              |
|                                                                        v              |
|                                                             +---------------------+   |
|                                                             |                     |   |
|                                                             |   Async Thread Pool |   |
|                                                             |   (Tokio / Reqwest) |   |
|                                                             |                     |   |
|                                                             +----------+----------+   |
|                                                                        |              |
|                                                                        v              |
|   +-------------------+      +-----------------------+      +---------------------+   |
|   |                   |      |                       |      |                     |   |
|   |  State & Display  |<-----|  Smart Filter Engine  |<-----| HTTP Response Parser|   |
|   |  (Progress Bar)   |      |  (Regex, Size, Words) |      |                     |   |
|   |                   |      |                       |      |                     |   |
|   +---------+---------+      +-----------+-----------+      +---------------------+   |
|             |                            |                                            |
|             |                            v                                            |
|             |                +-----------------------+                                |
|             v                |                       |                                |
|   +-------------------+      | Recursion Logic Engine|                                |
|   |                   |      |                       |                                |
|   | Output Formatter  |<-----| Adds new dirs to      |                                |
|   | (JSON, Plaintext) |      | Target Queue          |                                |
|   |                   |      |                       |                                |
|   +-------------------+      +-----------------------+                                |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

## 4. Deep Dive into Features and Mechanics
### 4.1. Recursive Discovery Mechanics
Recursion is the beating heart of Feroxbuster. When it finds a directory, it dynamically creates a new scan task for it.
- **`--depth <NUM>`**: Limits the maximum recursion depth.
- **`--extract-links`**: Parses HTML to extract hidden hrefs.

### 4.2. Smart Filtering Engine
- **Dynamic Auto-Tuning**: The `--auto-tune` feature sends randomized strings to establish a "Not Found" baseline.
- **`--filter-size <BYTES>`**: Exclude responses of an exact size.

## 5. Practical Implementation and Advanced Use Cases
### 5.1. Baseline Execution
```bash
feroxbuster -u https://api.target.com/ -w wordlist.txt
```

### 5.2. JSON Output for Pipeline Integration
```bash
feroxbuster -u http://target.com -w wordlist.txt --json | jq -r '.url' | httpx -silent
```

## 6. Comprehensive Command Line Reference
1. `-u, --url`: Target URL.
2. `-w, --wordlist`: Path to wordlist.
3. `-x, --extensions`: File extensions to append.
4. `-H, --headers`: Custom headers.
5. `-p, --proxy`: Proxy URL.
6. `-d, --depth`: Maximum recursion depth.
7. `-t, --threads`: Number of concurrent threads.
8. `--json`: Output in JSON format.
9. `--silent`: Suppress output.
10. `--auto-tune`: Automatically calibrate filters.
11. `--filter-size`: Ignore exact response sizes.
12. `--filter-words`: Ignore specific word counts.
13. `--filter-lines`: Ignore specific line counts.
14. `--filter-regex`: Ignore regex patterns in body.
15. `--filter-status`: Exclude specific HTTP status codes.
16. `--rate-limit`: Max requests per second.
17. `--random-agent`: Randomize User-Agent header.
18. `--extract-links`: Extract links from response body.
19. `--dont-scan`: Exclude certain URLs from being scanned.
20. `--resume-from`: Resume a previous scan.
21. `-C, --collect-extensions`: Collect extensions.
22. `-A, --auto-bail`: Stop scanning on errors.
23. `--insecure`: Disable TLS cert validation.
24. `--no-recursion`: Do not recurse.
25. `--force-recursion`: Force recursion on every matched URL.

## 7. Extended Troubleshooting Guide
1. **Socket Exhaustion**: Run `ulimit -n 65535`.
2. **Timeouts**: Lower threads, use rate-limit.
3. **High CPU**: Reduce concurrent threads.
4. **Proxy Drops**: Verify proxy max connections.
5. **False Positives**: Use `--auto-tune`.
6. **Missing Auth**: Ensure `Authorization` header is passed.
7. **JSON Parse Error**: Always use `--silent` with `--json`.
8. **Stuck at 99%**: Likely a slow responding endpoint.
9. **WAF Blocks**: Use rotating proxies.
10. **File Not Found**: Verify wordlist path.
11. **Permission Denied**: Run as correct user.
12. **Out of Memory**: Rare, but reduce depth.
13. **Infinite Loops**: Use `--depth 2`.
14. **No Output**: Target might be blocking ping/HTTP.
15. **Bad Gateway**: Target backend is down.
16. **Rate Limit Hit**: Add random delays.
17. **DNS Resolution Failed**: Use custom DNS.
18. **SSL Error**: Add `--insecure`.
19. **Interrupted Scan**: Use `--resume-from`.
20. **Too Much Noise**: Add specific `--filter-status`.

## 8. Continuous Integration (CI/CD) Checklist
1. [ ] Install Feroxbuster binary.
2. [ ] Define a small, highly targeted wordlist.
3. [ ] Configure GitHub Secrets for Auth Headers.
4. [ ] Add `--json` flag.
5. [ ] Pipe to `jq` to extract routes.
6. [ ] Filter out known routes.
7. [ ] Assert no sensitive files (.env, .git) are found.
8. [ ] If sensitive file found, exit code 1.
9. [ ] Publish artifacts to S3.
10. [ ] Send Slack notification with new endpoints.
11. [ ] Ensure rate limiting to protect staging servers.
12. [ ] Rotate User-Agents in CI pipeline.
13. [ ] Monitor CI runner memory limits.
14. [ ] Implement weekly cron jobs for re-scanning.
15. [ ] Integrate with Nuclei for immediate triage.
16. [ ] Define custom `--filter-regex` for staging WAF.
17. [ ] Validate proxy connection if runner is isolated.
18. [ ] Backup previous JSON scans for diffing.
19. [ ] Alert on unexpected 500 status codes.
20. [ ] Document findings in Jira automatically.

## 9. Advanced Usage Scenarios
- **Blind Exploitation**: Feeding routes into blind SSRF testers.
- **Parameter Mining**: Forwarding findings to `Arjun`.
- **Cache Poisoning**: Testing discovered endpoints with custom headers.

## 10. Related Notes
- [[10 - Directory and File Brute-Forcing]]
- [[15 - Analyzing WAFs and Bypassing Filters]]
- [[35 - Automated Reconnaissance Pipelines]]
- [[24 - gau GetAllUrls from Wayback and OTX]]
- [[25 - waybackurls Wayback Machine URL Fetcher]]
- [[23 - Hakrawler Fast Web Crawler]]
- [[22 - Katana Web Crawler by Project Discovery]]

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
