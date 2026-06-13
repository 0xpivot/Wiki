---
tags: [tools, web-testing, crawler, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.25 waybackurls Wayback Machine URL Fetcher"
---

# waybackurls: Wayback Machine URL Fetcher

## 1. Executive Summary & Overview
`waybackurls`, developed by tomnomnom, is the minimalist predecessor to modern aggregation tools. It strictly adheres to the Unix philosophy: do exactly one thing, and do it perfectly. Its sole purpose is to accept a domain name via standard input and query the Internet Archive's Wayback Machine CDX API to retrieve every URL associated with that domain that has ever been archived.

## 2. Core Architectural Philosophy
### 2.1. The Unix Philosophy in Action
`waybackurls` requires zero configuration files, no API keys, and practically no complex flags.
### 2.2. Passive and Invisible
Like `gau`, `waybackurls` never touches the target infrastructure.
### 2.3. Simplicity Over Complexity
While newer tools have added multiple providers, `waybackurls` remains popular due to its raw speed and reliability.

## 3. ASCII Architecture Diagram
```text
+---------------------------------------------------------------------------------------+
|                                WAYBACKURLS ARCHITECTURE                               |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | STDIN Input   |----->|  Domain Parser          |----->|  HTTP Client          |   |
|   | (Subdomains)  |      |  (Prepares Query)       |      |  (GET Requests)       |   |
|   +---------------+      +-------------------------+      +-----------+-----------+   |
|                                                                       |               |
|                                                                       v               |
|                                                           +-----------------------+   |
|                                                           |                       |   |
|                                                           |  Wayback Machine      |   |
|                                                           |  CDX API Endpoint     |   |
|                                                           |                       |   |
|                                                           +-----------+-----------+   |
|                                                                       |               |
|                                                                       v               |
|   +---------------+      +-------------------------+      +-----------------------+   |
|   | STDOUT Output |<-----|  JSON Parser            |<-----|  Response Stream      |   |
|   | (Raw URLs)    |      |  (Extracts URL array)   |      |  (JSON Data)          |   |
|   +---------------+      +-------------------------+      +-----------------------+   |
|                                                                                       |
+---------------------------------------------------------------------------------------+
```

## 4. Deep Dive into Features and Mechanics
### 4.1. The CDX API
The tool interfaces directly with the Internet Archive's CDX Server API.
### 4.2. Exact Matches vs Wildcards
By default, `waybackurls` searches for wildcard matches of the provided domain.

## 5. Practical Implementation and Advanced Use Cases
### 5.1. Isolating Hidden Parameters
```bash
cat subdomains.txt | waybackurls | grep "=" | sort -u > parameters.txt
```
### 5.2. Chaining for Liveness
```bash
echo "example.com" | waybackurls | sort -u | httpx -silent -status-code | grep 200
```

## 6. Comprehensive Command Line Reference
1. `-dates`: Print the timestamp of when the URL was archived.
2. `-no-subs`: Do not include subdomains in the search.
3. `-get-versions`: Get all versions of a URL.
4. `-h`: Print help menu.
5. `(No other flags)`: The tool is intentionally minimalist.

## 7. Extended Troubleshooting Guide
1. **API Timeouts**: The Wayback Machine CDX API is frequently under heavy load. Retry later.
2. **Extreme Output Redundancy**: Always pipe output through `sort -u`.
3. **No Results**: Domain might be actively blocking archive.org via robots.txt.
4. **Hanging Terminal**: Use `Ctrl+C` and retry.
5. **Slow Speed**: The API is notoriously slow during peak hours.
6. **Missing Latest Pages**: The Wayback Machine takes time to index new pages.
7. **Connection Reset**: Your local ISP might be dropping connections.
8. **Memory Issues**: `waybackurls` streams output, so it uses minimal RAM.
9. **Dead Links**: Expect 90% of links to be dead. Use `httpx`.
10. **JSON Format**: `waybackurls` does NOT support JSON out of the box. Use `gau` for that.
11. **Subdomains Excluded**: Verify you didn't pass `-no-subs`.
12. **Versions Clutter**: Avoid `-get-versions` unless forensically necessary.
13. **Binary Path**: Ensure `~/go/bin` is in your `$PATH`.
14. **Parsing Errors**: Clean domain inputs before piping.
15. **Wildcard Fails**: Some large apex domains will cause API timeouts due to size.
16. **Rate Limit 429**: Wait 24 hours or change IP.
17. **Empty Lines**: Ignore them with `grep -v '^$'`.
18. **Unwanted Domains**: Ensure your input list is clean.
19. **Network Flake**: Run inside a `tmux` session.
20. **Compiling Error**: Ensure Go version > 1.14.

## 8. Continuous Integration (CI/CD) Checklist
1. [ ] Add `waybackurls` binary to CI environment.
2. [ ] Feed list of apex domains via file.
3. [ ] Pipe output to `sort -u`.
4. [ ] Filter out common noise (`.jpg`, `.png`).
5. [ ] Pass through `httpx` to verify liveness.
6. [ ] Pass live URLs to `nuclei`.
7. [ ] Implement a timeout threshold (e.g., 30 mins max).
8. [ ] Store the raw historical data in S3.
9. [ ] Run `qsreplace` on parameterized endpoints.
10. [ ] Send XSS payloads to discovered parameters.
11. [ ] Alert on any `.git` or `.env` URLs historically present.
12. [ ] Trigger alerts via Webhooks.
13. [ ] Monitor for CI execution time limits.
14. [ ] Compare daily runs using `comm -13`.
15. [ ] Highlight new historical endpoints discovered.
16. [ ] Utilize dedicated cloud IPs.
17. [ ] Implement fallback to `gau` if CDX fails.
18. [ ] Avoid running during peak US hours for better API speed.
19. [ ] Sanitize outputs for PII before storing.
20. [ ] Automate Jira ticket creation for exposed credentials.

## 9. Advanced Usage Scenarios
- **Finding Old Admin Panels**: Grepping for `/admin`, `/login`, `/dashboard`.
- **Finding Backup Files**: Grepping for `.bak`, `.old`, `.sql`.

## 10. Related Notes
- [[24 - gau GetAllUrls from Wayback and OTX]]
- [[22 - Katana Web Crawler by Project Discovery]]
- [[23 - Hakrawler Fast Web Crawler]]
- [[35 - Automated Reconnaissance Pipelines]]
- [[10 - Directory and File Brute-Forcing]]
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
