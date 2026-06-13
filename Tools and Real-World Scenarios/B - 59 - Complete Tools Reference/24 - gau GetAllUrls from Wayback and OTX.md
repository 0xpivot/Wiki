---
tags: [tools, web-testing, crawler, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.24 gau GetAllUrls"
---

# gau: GetAllUrls from Wayback and OTX

## 1. Executive Summary & Overview
GetAllUrls (`gau`) is a powerful passive reconnaissance tool that revolutionizes endpoint discovery by fetching known URLs from massive public datasets, specifically AlienVault's Open Threat Exchange (OTX), the Internet Archive's Wayback Machine, and Common Crawl. By querying these external providers instead of the target server directly, `gau` allows security researchers to uncover legacy endpoints.

## 2. Core Architectural Philosophy
### 2.1. Passive Intelligence Gathering
The core tenet of `gau` is absolute stealth. It does not send a single packet to the target domain.
### 2.2. Multi-Provider Concurrency
To ensure maximum coverage, `gau` queries multiple data providers simultaneously.
### 2.3. Pipeline Centric Design
Output is delivered as a raw stream of URLs to standard output.

## 3. ASCII Architecture Diagram
```text
+---------------------------------------------------------------------------------------+
|                                    GAU ARCHITECTURE                                   |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|                               +-----------------------+                               |
|                               |                       |                               |
|   +---------------+           |   Wayback Machine API |           +---------------+   |
|   | Target Domain |---------->|   (Internet Archive)  |---------->|               |   |
|   +---------------+           |                       |           |               |   |
|          |                    +-----------------------+           |               |   |
|          |                                                        |  Concurrent   |   |
|          +------------------->|                       |---------->|  Response     |   |
|          |                    |  AlienVault OTX API   |           |  Aggregator   |   |
|          |                    |                       |           |               |   |
|          |                    +-----------------------+           |               |   |
|          +------------------->|                       |---------->|               |   |
|                               |  Common Crawl API     |           +-------+-------+   |
|                               |                       |                   |           |
|                               +-----------------------+                   v           |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | STDOUT Output |<-----|     Deduplication &     |<-----|   Filter Engine       |   |
|   | (Clean URLs)  |      |     Formatting          |      |   (Regex, Blacklist)  |   |
|   +---------------+      +-------------------------+      +-----------------------+   |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

## 4. Deep Dive into Features and Mechanics
### 4.1. Provider Selection
By default, `gau` queries all available providers. Utilize `--providers` to isolate them.
### 4.2. Subdomain Inclusion
The `--subs` flag is incredibly powerful, fetching data for all subdomains.

## 5. Practical Implementation and Advanced Use Cases
### 5.1. Expanding to Subdomains
```bash
gau --subs example.com > historical_urls.txt
```
### 5.2. Advanced Pipeline Integration
```bash
gau --subs example.com | grep -vE "\.(jpg|jpeg|gif|css|png)$" | httpx -silent -status-code | grep 200 > live.txt
```

## 6. Comprehensive Command Line Reference
1. `--subs`: Include subdomains of the target domain.
2. `--providers`: Specify data providers to use (e.g., `wayback,otx,commoncrawl`).
3. `--o, --output`: Write results to a specific file.
4. `--b, --blacklist`: Blacklist specific extensions from output.
5. `--t, --threads`: Number of concurrent workers to spawn.
6. `--verbose`: Enable verbose logging.
7. `--json`: Output results in JSON format.
8. `--retries`: Number of retries for failed API requests.
9. `--fp, --fetch-parameters`: Fetch only URLs that contain parameters.
10. `--version`: Show version info.
11. `--proxy`: Set a proxy for API requests.
12. `--timeout`: Adjust timeout for API requests.
13. `--config`: Path to a custom config file.
14. `--random-agent`: Randomize User-Agent for API requests.
15. `--match-status`: Match specific status codes.
16. `--filter-status`: Drop specific status codes.
17. `--include-body`: Include body content in JSON output.
18. `--headers`: Add custom headers to API requests.
19. `--insecure`: Disable TLS validation for proxy.
20. `--max-results`: Limit the number of results returned.
21. `--from`: Fetch URLs archived after a specific date.
22. `--to`: Fetch URLs archived before a specific date.
23. `--domain`: Limit scope to specific domain.
24. `--dedupe`: Deduplicate results in memory.
25. `--silent`: Suppress all error messages.

## 7. Extended Troubleshooting Guide
1. **API Rate Limiting**: The Wayback Machine aggressively rate limits.
2. **Massive Output Size**: Pipe to files immediately.
3. **Stale Data**: Always use `httpx` to validate output.
4. **Hanging Process**: Common Crawl can take minutes to respond.
5. **No Output**: Target might be excluded from archives.
6. **JSON Errors**: Ensure `-silent` is used when piping.
7. **Timeout Errors**: Increase `--timeout`.
8. **Memory Exhaustion**: Use `uro` for deduplication instead of in-memory.
9. **Proxy Drops**: Verify proxy is correctly formatted.
10. **OTX Key Missing**: Some versions require OTX API keys in config.
11. **Regex Failures**: Use built-in `--blacklist` instead of grep.
12. **Subdomains Missing**: Verify `--subs` flag is active.
13. **Parameter Filtering**: Use `--fp` to narrow results.
14. **Connection Refused**: Your ISP might be blocking archive sites.
15. **Duplicate URLs**: Always pipe to `sort -u`.
16. **Date Filtering Fails**: Verify `YYYYMMDD` format.
17. **CommonCrawl Fails**: CommonCrawl API is notoriously unstable.
18. **Too Fast**: Reduce threads if API bans IP.
19. **Missing Specific URLs**: Archive.org doesn't index everything.
20. **Corrupted Binary**: Reinstall using Go.

## 8. Continuous Integration (CI/CD) Checklist
1. [ ] Implement scheduled `gau` runs.
2. [ ] Compare daily outputs to detect newly indexed sensitive paths.
3. [ ] Filter out known static assets dynamically.
4. [ ] Pipe findings directly into `nuclei`.
5. [ ] Alert on any newly discovered subdomains.
6. [ ] Utilize `--json` for SIEM integration.
7. [ ] Implement rate limiting to respect API providers.
8. [ ] Store outputs in a centralized data lake.
9. [ ] Write custom `jq` scripts to parse parameters.
10. [ ] Flag any URLs containing `token=`, `key=`, `pwd=`.
11. [ ] Forward alerts to Slack/Teams.
12. [ ] Validate all discovered URLs with `httpx`.
13. [ ] Discard 404s before scanning.
14. [ ] Use OTX API keys securely from secrets manager.
15. [ ] Backup previous logs for historical diffing.
16. [ ] Limit concurrent CI jobs to avoid IP ban.
17. [ ] Monitor artifact size limits.
18. [ ] Execute on multiple cloud runners for redundancy.
19. [ ] Sanitize outputs before storage.
20. [ ] Periodically rotate proxy IPs if used.

## 9. Advanced Usage Scenarios
- **Blind XSS Hunting**: Extract parameters and inject polyglots.
- **Legacy API Discovery**: Discovering `/api/v1/` when only `/api/v3/` is active.

## 10. Related Notes
- [[25 - waybackurls Wayback Machine URL Fetcher]]
- [[22 - Katana Web Crawler by Project Discovery]]
- [[23 - Hakrawler Fast Web Crawler]]
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
