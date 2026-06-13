---
tags: [tools, recon, network, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.15 httpx HTTP Probing at Scale"
---

# httpx HTTP Probing at Scale

## Introduction to httpx

`httpx` is a robust, fast, and multi-purpose HTTP toolkit developed by ProjectDiscovery. In modern VAPT and Bug Bounty workflows, the transition from Network Layer (Layer 3/4) reconnaissance to Application Layer (Layer 7) reconnaissance is critical. You may have enumerated 10,000 live IP addresses or subdomains via DNS brute-forcing, but identifying which of those actually host a web server, what technologies they are running, and what their default responses look like is a monumental task.

`httpx` bridges this gap. It takes a raw list of domains, subdomains, or IP addresses, probes them across multiple ports, follows redirects, extracts metadata (titles, server headers, status codes, tech stacks), and presents the data in a clean, filterable format. Built in Go, it is designed for extreme concurrency, allowing a penetration tester to fingerprint thousands of web applications in seconds.

## Why Use httpx?

1. **Extreme Concurrency**: Can probe thousands of hosts simultaneously, gracefully handling network timeouts and closed ports.
2. **Deep Fingerprinting**: It doesn't just check if port 80/443 is open; it reads the HTTP response to extract the page Title, Server Header, Content-Length, and Web Technologies (via `wappalyzer` integration).
3. **Protocol Versatility**: Supports HTTP/1.1, HTTP/2, and handles complex TLS/SSL certificate extraction and validation.
4. **Pipeline Integration**: Accepts input via `stdin` and outputs results to `stdout` or structured JSON, making it the perfect middleman between DNS resolution tools (like `dnsx`) and vulnerability scanners (like `nuclei`).

## Architecture and Execution Pipeline

The following ASCII diagram illustrates how `httpx` processes raw subdomains and enriches them with Layer 7 metadata.

```text
+-------------------+       +---------------------------------------+
| Valid Subdomains  |       |                 httpx                 |
| / IP Addresses    | ----> |                                       |
| (from dnsx/nmap)  |       |  +---------------------------------+  |
+-------------------+       |  | Port Probing Engine             |  |
                            |  | (Check 80, 443, 8080, 8443, etc)|  |
                            |  +---------------------------------+  |
                                                |
                                                v
                            |  +---------------------------------+  |
                            |  | HTTP Request Engine             |  |
                            |  | (Follow Redirects, Handle TLS,  |  |
                            |  |  Determine HTTP/2 support)      |  |
                            |  +---------------------------------+  |
                                                |
                                                v
                            |  +---------------------------------+  |
                            |  | Response Parsing & Enrichment   |  |
                            |  | - Status Codes (200, 403, 404)  |  |
                            |  | - Page Titles & Content Length  |  |
                            |  | - Wappalyzer Tech Stack         |  |
                            |  | - JARM Fingerprinting           |  |
                            |  +---------------------------------+  |
                                                |
                                                v
                            +---------------------------------------+
                                                |
                                                v
                            +---------------------------------------+
                            | Enriched Output (stdout / JSON)       |
                            | e.g. https://dev.target.com [200]     |
                            | [Apache] [Title: Login Panel]         |
                            +---------------------------------------+
```

## Core Features and Usage

### 1. Basic Web Server Probing
The most standard use case is piping a list of live subdomains into `httpx` to see which ones respond via HTTP/HTTPS.
```bash
cat live_subs.txt | httpx -silent > alive_web_servers.txt
```
By default, this will probe ports 80 and 443.

### 2. Extracting Layer 7 Metadata
`httpx` shines when extracting contextual information about the web server. This is vital for prioritizing targets during an engagement.
```bash
cat live_subs.txt | httpx -sc -title -server -td -ip
```
**Flags Breakdown:**
- `-sc`: Display the HTTP Status Code (e.g., 200, 403, 404).
- `-title`: Extract and display the HTML `<title>` tag.
- `-server`: Display the `Server` HTTP response header (e.g., `nginx/1.18.0`).
- `-td`: Display the Web Technology fingerprint (Technology Detection via Wappalyzer logic).
- `-ip`: Display the resolving IP address.

**Example Output:**
```
https://admin.example.com [200] [Login Dashboard] [nginx/1.18.0] [React, Node.js] [10.0.0.5]
https://api.example.com [403] [Forbidden] [cloudflare] [104.21.3.4]
```

### 3. Custom Port Scanning
Web applications are often hidden on non-standard ports. You can instruct `httpx` to probe a specific set of ports for every host.
```bash
cat live_subs.txt | httpx -p 80,443,8080,8443,9090,8000 -sc -title
```
Alternatively, you can use predefined aliases:
- `-ports top-100`: Probes the top 100 most common web ports.
- `-ports top-1000`: Probes the top 1000 most common web ports.

### 4. Matching and Filtering
During large scale recon, you often want to filter out the noise (like 404 Not Found pages) or hone in on specific targets (like Administrative panels).

**Filtering by Status Code:**
```bash
cat domains.txt | httpx -fc 404,400 -mc 200,403,302
```
- `-fc`: Filter out (exclude) these status codes.
- `-mc`: Match only (include) these status codes.

**Filtering by Title or Content:**
```bash
cat domains.txt | httpx -match-title "Admin,Login,Dashboard"
cat domains.txt | httpx -match-regex "jira|confluence"
```

### 5. Advanced Fingerprinting (JARM)
JARM is an active TLS server fingerprinting tool. `httpx` can extract the JARM hash of a target, which can be cross-referenced with known malware C2 infrastructure or specific server configurations.
```bash
echo "example.com" | httpx -jarm
```

## Advanced Configuration and Pipeline Integration

### Structured JSON Output
For integration into Attack Surface Management (ASM) databases (like Elasticsearch) or for programmatic parsing, the `-json` flag outputs all extracted metadata as a structured JSON object.
```bash
cat domains.txt | httpx -json -o httpx_results.json
```
This JSON output contains incredible detail, including TLS certificate issuer chains, response headers, HTTP/2 support metrics, and CDN identification.

### Following Redirects
Often, `http://example.com` will 301 redirect to `https://www.example.com`. By default, `httpx` does not follow redirects to maintain speed. To accurately capture the final destination's metadata, enable redirect following.
```bash
cat domains.txt | httpx -follow-redirects -sc -title
```

### Proxying and Anonymity
If you need to route your HTTP probing traffic through an intermediary to avoid IP bans or to access internal networks via a SOCKS proxy, `httpx` supports standard proxy flags.
```bash
cat domains.txt | httpx -http-proxy http://127.0.0.1:8080
```

## Real-World Workflow Example

A complete reconnaissance pipeline taking raw passive data to actionable web targets:

1. Subdomain Enumeration: `subfinder -d target.com > subs.txt`
2. DNS Resolution: `cat subs.txt | dnsx -silent > live_subs.txt`
3. Web Probing & Filtering: Identify all web servers returning a 200 OK or 403 Forbidden, extract their titles, and save them.

```bash
cat live_subs.txt | httpx -p 80,443,8080,8443 -mc 200,403 -title -tech-detect -o web_targets.txt
```
4. Vulnerability Scanning: Pass the refined list of web targets directly to Nuclei.
```bash
cat web_targets.txt | awk '{print $1}' | nuclei -t nuclei-templates/
```

## Chaining Opportunities
- **Vulnerability Scanning**: The standard input for `nuclei` is the output of `httpx`.
- **Directory Bruteforcing**: Feed the URLs generated by `httpx` into `ffuf` or `feroxbuster` for targeted directory enumeration.
- **Visual Reconnaissance**: Use the list of responsive URLs with `gowitness` or `aquatone` to generate visual screenshots of every web application.

## Related Notes
- [[12 - dnsx DNS Bulk Resolution and Probing]]
- [[17 - nuclei Vulnerability Scanner]]
- [[19 - ffuf Fuzz Faster U Fool]]
- [[20 - gowitness Visual Web Recon]]
