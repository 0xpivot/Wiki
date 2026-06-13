---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.33 dalfox XSS Scanner DOM-aware"
---

# 59.33 dalfox XSS Scanner DOM-aware

## 1. Introduction
`DalFox` (which stands for DAL=Moon, FOX) is a massively parallel, incredibly fast, and feature-rich XSS scanner written entirely in Golang. While tools like XSStrike focus on mathematical precision and complex string parsing in Python, DalFox is built from the ground up for raw speed, highly concurrent CI/CD pipeline integration, and robust DOM-based XSS detection. 

DalFox analyzes parameters, discovers potentially vulnerable injection points, and verifies them using an embedded headless browser (DOM-aware capabilities). This makes it highly effective against modern Single Page Applications (SPAs) built with React, Vue, or Angular, where traditional reflected XSS scanners fail entirely because the payload is rendered client-side by JavaScript rather than server-side.

## 2. Architecture and Concurrency Model

DalFox utilizes Go's native goroutines to achieve extreme concurrency, making it ideal for scanning massive scope files (e.g., thousands of endpoints gathered from automated reconnaissance).

```ascii
+-----------------------------------------------------------------------------------+
|                                 DalFox Core Engine                                |
|                                                                                   |
|  +---------------+       +-------------------------+       +-------------------+  |
|  | Input Streams | ----> | Goroutine Worker Pool   | ----> | Injection Engine  |  |
|  | (Pipe, File,  |       | (Concurrency Control)   |       | (Reflected, Stored|  |
|  | Single URL)   |       +-------------------------+       | DOM, Blind)       |  |
|  +---------------+                   |                     +-------------------+  |
|                                      v                               |            |
|                          +-------------------------+                 |            |
|                          | Headless Browser (DOM)  | <---------------+            |
|                          | (Chromedp context)      |                              |
|                          +-------------------------+                              |
+-----------------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------------+
|                      Output Handling (CLI, JSON, Webhook)                         |
+-----------------------------------------------------------------------------------+
```

## 3. Core Features and Capabilities

DalFox is meticulously designed to cover the entire spectrum of XSS vulnerabilities, ensuring no variant goes untested.

*   **Reflected XSS**: Identifies parameters that reflect input directly in the server's HTTP response.
*   **Stored XSS**: Supports verifying delayed reflection, where a payload is sent in one request and executed in a different endpoint entirely (e.g., submitting a comment in an API and viewing it on a public article page).
*   **DOM XSS**: Analyzes the client-side execution environment natively. It checks if JavaScript sinks (like `innerHTML`, `document.write`, `eval()`, `setTimeout()`) improperly process user-controlled sources (like `location.hash`, `window.name`, `document.referrer`).
*   **Blind XSS**: Native, seamless integration with external Out-of-Band (OOB) testing frameworks.

## 4. Headless Browser Internals (Chromedp)
The most significant advantage of DalFox is its `--use-headless` flag. When enabled, DalFox utilizes the `chromedp` library to spin up an invisible Google Chrome instance. 

Instead of relying solely on regex to see if a payload is reflected, DalFox injects the payload and then allows the headless browser to fully render the page, execute all JavaScript, and listen for specific alert dialogs or DOM mutations. This drastically reduces false positives and is the only reliable way to test complex modern JavaScript applications where payloads must survive multiple layers of client-side parsing before hitting a vulnerable sink.

## 5. Parameter Analysis and Mining
DalFox includes built-in parameter mining (similar functionality to `Arjun` or `ParamSpider`), streamlining the recon-to-exploitation phase.

*   `--mine-dict`: Use a custom dictionary file to discover hidden parameters.
*   `--mine-dict-word`: Specify a specific wordlist directly for parameter brute-forcing.

By combining parameter discovery and XSS scanning in a single step, DalFox saves significant processing time.

## 6. Detailed Flag Reference and Usage Scenarios

DalFox's command-line interface is modular, supporting various execution modes: `url`, `file`, `pipe`, `sxss` (Stored XSS).

### Basic Scanning and I/O
*   `dalfox url "http://example.com?q=1"`: Scan a single target URL.
*   `dalfox file urls.txt`: Scan a massive list of URLs concurrently.
*   `cat urls.txt | dalfox pipe`: Read targets from standard input. This is perfect for Unix philosophy chaining.

### Payload Control and Tuning
*   `--custom-payload`: Provide a file with custom, heavily obfuscated payloads, bypassing the built-in default ones.
*   `--worker`: Number of concurrent HTTP workers (default is 100). Tuning this is absolutely crucial; setting it too high on a fragile target may cause an unintentional Denial of Service (DoS) or trigger cloud rate limiters immediately.
*   `--timeout`: HTTP timeout in seconds to handle slow server responses.
*   `--user-agent`: Set a custom User-Agent to bypass rudimentary filter rules.
*   `--header`: Inject custom HTTP headers (e.g., `--header "Authorization: Bearer token"`).
*   `--cookie`: Set session cookies for deep authenticated scanning.

### Blind XSS Integration
*   `-b`, `--blind`: Specify a custom blind XSS payload (e.g., a URL from XSS Hunter or a custom interactsh instance).
    *   *Example*: `dalfox url "http://example.com" -b "https://your.xss.ht"`

### Evasion and Rate Limiting
*   `--evasion`: Enable evasion payloads. DalFox will obfuscate its payloads using various techniques (HTML entity encoding, Unicode encoding, whitespace manipulation) to bypass weak WAF rules.
*   `--delay`: Add precise milliseconds of delay between requests (WAF evasion and rate limit bypass).

## 7. Pipeline Integration (Nuclei, notify)
DalFox is heavily utilized in Bug Bounty automation and DevSecOps pipelines due to its speed and output formats.

*   `--format json`: Output results in structured JSON.
*   `--found-action`: Execute an external bash command when a vulnerability is found.
    *   *Example*: `--found-action "notify -data 'Critical XSS Found by DalFox!'"`. This integrates perfectly with ProjectDiscovery's `notify` tool to send Slack or Discord alerts instantly.
*   `--output`: Save the final report to a specified file.

## 8. Advanced Scenario: Stored XSS Testing
Stored XSS testing requires defining a logical "sequence" of actions: the injection point and the verification point.

*   `dalfox sxss --url "http://example.com/view_comment" --trigger "http://example.com/post_comment" --sequence "1"`
    This mode allows you to systematically test complex applications where payloads are stored in a database via a POST request and rendered on a completely different GET endpoint.

## 9. Evasion against Modern WAFs (Cloudflare/Akamai)
While DalFox is incredibly fast, aggressive scanning will quickly lead to a permanent IP ban from enterprise WAFs.
To mitigate this in professional environments:
1.  Lower the `--worker` count to a conservative 5 or 10.
2.  Introduce a `--delay` of 500-1500ms.
3.  Use rotation proxies in your HTTP client setup (or route traffic through a proxy manager).
4.  Utilize the `--evasion` flag combined with highly specific `--custom-payload` lists tailored to the target's WAF fingerprint (e.g., using backticks instead of parentheses for execution `alert`1``).

## 10. Chaining Opportunities
*   **WaybackURLs -> GF -> DalFox**: A classic, highly effective Bug Bounty chain. Fetch all historical URLs for a target domain using `waybackurls` or `gau`, filter for parameters likely vulnerable to XSS using `gf xss`, and pipe the result directly into DalFox for validation:
    `echo "target.com" | waybackurls | gf xss | dalfox pipe --use-headless`
*   **Nuclei Integration**: DalFox findings can be exported, analyzed, and used as base templates for custom Nuclei checks, automating regression testing across massive corporate infrastructures.

## 11. Related Notes
*   [[14 - Cross-Site Scripting (XSS) Deep Dive]]
*   [[32 - XSStrike XSS Fuzzer and Exploit]]
*   [[44 - Bug Bounty Automation Pipelines]]
*   [[19 - Client-Side Vulnerabilities]]
