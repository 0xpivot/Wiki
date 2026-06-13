---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.27 WhatWeb Wappalyzer"
---

# Web Technology Fingerprinting: WhatWeb & Wappalyzer

## 1. Introduction to Web Technology Fingerprinting

Web technology fingerprinting is the process of gathering information about a target web application's underlying technology stack. This includes identifying the web server, content management system (CMS), programming languages, frontend frameworks, analytics tools, and even specific versions of these components. This phase is critical in the reconnaissance process of a Vulnerability Assessment and Penetration Testing (VAPT) engagement.

By understanding the exact technologies powering a web application, a penetration tester can significantly narrow down the attack surface. For example, knowing a site runs on WordPress version 5.8 allows the tester to focus exclusively on vulnerabilities affecting that specific version, rather than testing generic exploits that are unlikely to succeed. Fingerprinting saves time, reduces noise, and prevents the target's monitoring systems from being overwhelmed by irrelevant payloads.

## 2. Architecture and Fingerprinting Flow (ASCII Diagram)

```text
+-------------------+       HTTP GET/POST        +-------------------+
|                   | -------------------------> |                   |
|  Attacker System  |                            | Target Web Server |
|  (WhatWeb /       | <------------------------- | (Apache/Nginx)    |
|   Wappalyzer)     |     HTTP Response          +-------------------+
+-------------------+     (Headers, HTML, JS)             |
        |                                                 |
        v                                                 |
+-------------------+                                     |
| Parsing Engine    |                                     v
| - Extract Headers |                            +-------------------+
| - Parse HTML DOM  |                            | Web Application   |
| - Analyze JS Vars |                            | (WordPress, React)|
+-------------------+                            +-------------------+
        |
        v
+-------------------+
| Pattern Matching  | ---> Matches against database of signatures (Regex)
| (Signatures)      |
+-------------------+
        |
        v
+-------------------+
| Result Aggregation| ---> Outputs identified technologies & versions
+-------------------+
```

## 3. WhatWeb Deep Dive

### 3.1 Overview
WhatWeb is a next-generation web scanner that identifies web technologies. It is written in Ruby and comes pre-installed on Kali Linux. It uses a vast library of plugins (over 1800) to detect systems, CMSs, blogging platforms, statistic/analytics packages, JavaScript libraries, web servers, and embedded devices. It is fast, lightweight, and specifically designed for the command-line interface.

### 3.2 How WhatWeb Works
WhatWeb operates by sending HTTP requests to the target and analyzing the responses. The analysis is driven by plugins. Each plugin contains one or more patterns (usually regular expressions) that match specific characteristics of a technology.

These characteristics include:
- **HTTP Headers:** Checking for specific `Server`, `X-Powered-By`, or custom headers indicating specific load balancers or WAFs.
- **HTML Content:** Looking for specific HTML tags, unique comments, or identifying class names within the DOM structure.
- **Meta Tags:** Analyzing `<meta name="generator" content="...">` tags, which many CMSs leave in place by default.
- **Cookies:** Identifying characteristic cookie names (e.g., `PHPSESSID` for PHP, `wp-settings` for WordPress).
- **URL Paths:** Checking for predictable file paths (e.g., `/wp-admin/`, `/administrator/`).

### 3.3 Aggression Levels
WhatWeb offers different levels of aggression, allowing testers to balance stealth and thoroughness.

*   **Level 1 (Stealthy / Passive):** This is the default mode. It sends a single HTTP GET request and analyzes the response. It is very fast and completely stealthy, as it mimics a normal user visiting the site.
*   **Level 3 (Aggressive):** This mode sends additional requests to verify findings or uncover more information. For example, if it suspects WordPress, it might try to access `/wp-login.php` or `/readme.html` to confirm the version. This level is easily detectable by IDS/IPS and WAFs.
*   **Level 4 (Heavy):** This mode makes a significant number of requests, attempting to guess URLs, brute-force directories, and trigger specific error messages to extract more details. It is highly noisy and should only be used when stealth is not a concern and explicit permission has been granted.

### 3.4 Key Commands and Flags

```bash
# Basic scan (Level 1)
whatweb example.com

# Verbose output (highly recommended for detailed analysis)
whatweb -v example.com

# Aggressive scan (Level 3)
whatweb -a 3 example.com

# Scan multiple targets from a file
whatweb -i targets.txt

# Export results to JSON format (useful for pipeline integration)
whatweb example.com --log-json=results.json

# Specify a custom User-Agent
whatweb --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" example.com

# Use a specific plugin
whatweb -p wordpress example.com
```

### 3.5 Detailed Output Analysis
When run in verbose mode (`-v`), WhatWeb provides a breakdown of every plugin that fired and the specific evidence it found.

```text
Summary for http://example.com
========================================================
[ Apache ]
  Apache HTTP Server is a prominent web server.
  * Version: 2.4.41

[ PHP ]
  PHP is a widely-used general-purpose scripting language that is especially suited for Web development.
  * Version: 7.4.3 (from X-Powered-By header)

[ WordPress ]
  WordPress is a free and open-source content management system written in PHP and paired with a MySQL or MariaDB database.
  * Version: 5.8.1 (from meta generator tag)
```

### 3.6 Custom Plugin Development for WhatWeb
WhatWeb allows penetration testers to write custom plugins using Ruby. This is exceptionally useful when hunting for custom, proprietary applications or tracking specific threat actor infrastructure across large swathes of the internet.
A basic plugin structure looks like this:
```ruby
Plugin.define "MyCustomApp" do
  author "PenTester"
  version "1.0"
  description "Detects My Custom Application"
  
  # Match looking for a specific meta tag
  matches [
    { :text => '<meta name="app-identifier" content="MyCustomApp">' },
    # Match looking for a specific HTTP header
    { :search => "headers[x-custom-app]", :regexp => /^Version 2\.0/ }
  ]
end
```
By saving this to the `plugins` directory, WhatWeb will seamlessly integrate this into its signature database, making your reconnaissance highly targeted.

## 4. Wappalyzer Deep Dive

### 4.1 Overview
Wappalyzer is a cross-platform utility that uncovers the technologies used on websites. It detects CMSs, eCommerce platforms, web frameworks, server software, analytics tools, and more. Wappalyzer is arguably more famous for its browser extension, but it also offers a robust CLI tool and API.

### 4.2 Browser Extension vs. CLI
*   **Browser Extension:** The extension runs passively in the background as you browse. It analyzes the DOM, headers, and JavaScript variables of the pages you visit. It's incredibly useful for manual testing and quick reconnaissance.
*   **CLI / Node.js Module:** The command-line version is ideal for automation. It uses a headless browser (like Puppeteer) to render the page, execute JavaScript, and then extract fingerprints. This makes it more capable than WhatWeb at detecting client-side rendering frameworks (like React, Angular, or Vue) that might not be visible in raw HTML.

### 4.3 How Wappalyzer Works
Wappalyzer relies on a vast JSON file containing thousands of regular expression patterns. It inspects:
- **Cookies:** Names and values indicative of specific session management libraries.
- **Headers:** HTTP response headers.
- **HTML:** Raw HTML source code.
- **Script Tags:** `src` attributes of `<script>` tags pointing to known library CDN endpoints.
- **JavaScript Variables:** Global variables defined in the `window` object (e.g., `window.React`, `window.__NUXT__`).
- **DOM:** Specific elements or attributes present after client-side rendering completes.

### 4.4 Usage Examples (CLI)

```bash
# Install via npm
npm install -g wappalyzer

# Basic scan
wappalyzer https://example.com

# Output detailed JSON
wappalyzer https://example.com --pretty
```

### 4.5 Wappalyzer JSON Output Example
The JSON output is highly structured, making it perfect for parsing by other tools in an automated pipeline.

```json
{
  "urls": {
    "https://example.com/": {
      "status": 200
    }
  },
  "technologies": [
    {
      "slug": "wordpress",
      "name": "WordPress",
      "confidence": 100,
      "version": "5.8",
      "icon": "WordPress.svg",
      "website": "https://wordpress.org",
      "cpe": "cpe:2.3:a:wordpress:wordpress:5.8:*:*:*:*:*:*:*",
      "categories": [
        {
          "id": 1,
          "slug": "cms",
          "name": "CMS"
        }
      ]
    }
  ]
}
```

## 5. Comparison: WhatWeb vs. Wappalyzer

| Feature | WhatWeb | Wappalyzer (CLI) |
| :--- | :--- | :--- |
| **Language** | Ruby | JavaScript (Node.js) |
| **Execution** | Raw HTTP requests | Headless Browser (evaluates JS) |
| **Speed** | Extremely fast (Level 1) | Slower (requires browser rendering) |
| **Client-Side Frameworks** | Poor (struggles with SPA) | Excellent (evaluates DOM/JS) |
| **Aggression Levels** | Yes (Level 1-4) | No (Passive analysis of rendered page) |
| **Ecosystem** | Standalone tool | Browser Extension, API, CLI |

## 6. Advanced Usage and Chaining

### 6.1 Automation Pipeline Integration
Both tools excel when integrated into larger reconnaissance scripts. A common workflow is:
1. Subdomain enumeration using tools like `Sublist3r` or `Amass`.
2. Probe for live hosts using `httpx`.
3. Feed the live hosts into WhatWeb or Wappalyzer to build a comprehensive technology matrix.

```bash
cat subdomains.txt | httpx -silent | awk '{print $1}' > live_hosts.txt
whatweb -i live_hosts.txt --log-json=tech_stack.json
```

### 6.2 Using Outputs for Targeted Exploitation
Once the technology stack is known, the next step is targeted vulnerability scanning. If generic vulnerability scanners are used, they generate excessive noise. Using the fingerprint, we can be surgical:
*   If `WordPress` is found -> Launch `wpscan` directly against it.
*   If `Joomla` is found -> Launch `joomscan`.
*   If a specific `Apache` version is found -> Search `searchsploit` or Metasploit for associated CVEs and memory corruption exploits.

## 7. Defending Against Fingerprinting (Evasion)

As a defender, minimizing the information exposed to these tools is crucial for defense-in-depth. While hiding technology doesn't fix underlying bugs, it severely hinders automated scanning and casual reconnaissance.
*   **Remove Default Headers:** Configure the web server (Apache/Nginx/IIS) to omit headers like `Server` and `X-Powered-By`. In IIS, remove the `X-AspNet-Version` header.
*   **Modify Default Configurations:** Change default file paths, rename default cookies (e.g., change `PHPSESSID` to something generic like `SESSIONID` or `AUTH_TOKEN`).
*   **Remove Meta Generators:** Ensure CMS templates do not output `<meta name="generator" content="...">`.
*   **Obfuscate Client-Side Code:** While difficult, minifying, aggressively bundling, and obfuscating JS can sometimes confuse simpler fingerprinting signatures that rely on variable names.
*   **WAF Interference:** A properly configured Web Application Firewall can intercept WhatWeb's aggressive probes, block the request, and feed false information back to the scanning IP.

## 8. Conclusion

WhatWeb and Wappalyzer are indispensable tools in the early stages of a penetration test. WhatWeb provides a fast, raw HTTP perspective with adjustable aggression levels, while Wappalyzer excels at identifying modern, JavaScript-heavy client-side frameworks through browser rendering. Mastering both ensures a comprehensive, highly accurate understanding of the target's attack surface, setting the stage for focused and effective vulnerability exploitation.

## 9. Chaining Opportunities
- Use results to feed specific vulnerability scanners like [[38 - WPScan JoomScan]].
- Combine with [[12 - Subdomain Enumeration]] to map the technology landscape of an entire organization.
- Use outputs to determine payload types for [[30 - XSStrike dalfox]].
- Correlate CMS versions identified here with known CVEs from external threat intel.

## 10. Related Notes
- [[02 - Information Gathering Methodology]]
- [[15 - Active Reconnaissance]]
- [[42 - Burp Suite Pro Features]]
- [[11 - Web Application Architecture]]
