---
tags: [tools, recon, network, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.12 dnsx DNS Bulk Resolution and Probing"
---

# dnsx DNS Bulk Resolution and Probing

## Introduction to dnsx

`dnsx` is a highly versatile, fast, and multi-purpose DNS toolkit developed by ProjectDiscovery. In the realm of Bug Bounty and Vulnerability Assessment/Penetration Testing (VAPT), the ability to process and resolve millions of subdomains quickly is paramount. Passive enumeration tools (like `Amass`, `Sublist3r`, or `crt.sh`) yield massive lists of potential subdomains, but many of these are historical artifacts, decommissioned, or internal-only hosts that do not resolve on the public internet.

`dnsx` acts as the critical filtering layer. It takes raw lists of subdomains, queries a customizable list of DNS resolvers concurrently, and outputs only the live, resolvable domains. Beyond simple A-record resolution, `dnsx` supports a multitude of DNS record types (CNAME, TXT, PTR, AAAA, MX, NS, AXFR) and includes robust wildcard filtering logic to sanitize results.

## Why Use dnsx?

1. **Extreme Concurrency**: Built in Go, `dnsx` utilizes goroutines to perform thousands of asynchronous DNS queries simultaneously, bound only by network bandwidth and resolver rate limits.
2. **Wildcard Filtering**: Many targets configure wildcard DNS records (`*.example.com -> 10.0.0.1`), which break brute-forcing tools by causing every guessed subdomain to resolve successfully. `dnsx` detects and filters these out automatically.
3. **Versatility**: It serves as a DNS resolver, a wildcard filter, a zone transfer (AXFR) testing tool, and an active brute-forcer.
4. **Pipeline Friendly**: Designed to seamlessly integrate into Unix pipelines, taking `stdin` and outputting clean `stdout` or JSON data.

## Architecture and Execution Pipeline

The following ASCII diagram illustrates the internal processing flow of `dnsx` when filtering a list of passively gathered subdomains.

```text
+-------------------+       +-----------------------------------+
|  Subdomain List   |       |             dnsx Toolkit          |
| (stdin / file)    | ----> |                                   |
+-------------------+       |  +-----------------------------+  |
                            |  |  Wildcard Detection Logic   |  |
                            |  +-----------------------------+  |
                            |                 |                 |
+-------------------+       |  +-----------------------------+  |
|  Wordlist         |       |  | Goroutine Worker Pool       |  |
| (Bruteforcing)    | ----> |  | (Concurrent DNS Queries)    |  |
+-------------------+       |  +-----------------------------+  |
                            |        |               ^          |
                            |        v               |          |
                            |  +-----------------------------+  |
                            |  | Public / Custom Resolvers   |  |
                            |  | (1.1.1.1, 8.8.8.8, etc.)    |  |
                            |  +-----------------------------+  |
                            +-----------------------------------+
                                              |
                                              v
                            +-----------------------------------+
                            |  Valid, Live Subdomains (stdout)  |
                            |  (Optional JSON / Metadata)       |
                            +-----------------------------------+
```

## Core Features and Usage

### 1. Basic Subdomain Resolution
The most common use case is piping a list of passively gathered subdomains into `dnsx` to filter out dead hosts.
```bash
cat raw_subdomains.txt | dnsx -silent > live_subdomains.txt
```
- `-silent`: Suppresses the banner and progress bar, outputting only the resolving domains.

### 2. Extracting Specific Record Types
You can instruct `dnsx` to query and return specific DNS records.

**A Records (IPv4):**
```bash
cat subdomains.txt | dnsx -a -resp
```
- `-a`: Query A records.
- `-resp`: Print the response (the IP address) alongside the subdomain.

**CNAME Records (Crucial for Subdomain Takeovers):**
```bash
cat subdomains.txt | dnsx -cname -resp
```
Identifying CNAME records that point to third-party services (e.g., AWS S3, Heroku, GitHub Pages) is the first step in hunting for Subdomain Takeover vulnerabilities.

**TXT Records:**
```bash
echo "example.com" | dnsx -txt -resp
```
Useful for extracting SPF records, site verification tokens, and sometimes leaked internal information.

### 3. Active Subdomain Bruteforcing
While tools like `shuffledns` or `puredns` are often preferred for massive bruteforcing, `dnsx` includes built-in brute-force capabilities.
```bash
dnsx -d example.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -t 100
```
- `-d`: Target domain.
- `-w`: Wordlist for bruteforcing.
- `-t`: Number of concurrent threads (default is 100).

### 4. Wildcard Detection and Filtering
Wildcard DNS (`*.target.com IN A 192.168.1.1`) creates a scenario where *any* query resolves, producing massive false positives during bruteforcing. `dnsx` handles this using the `-wd` (wildcard filtering) flag.
```bash
dnsx -d target.com -w wordlist.txt -wd
```
`dnsx` will generate random subdomains (e.g., `njxkasdjqw.target.com`), query them, and if they resolve, it signatures the response IP. It will then filter out any bruteforced subdomains that resolve to that specific wildcard IP.

### 5. Zone Transfers (AXFR)
Zone transfers allow a secondary nameserver to sync records from a primary nameserver. If misconfigured, an unauthenticated user can request a full copy of the DNS zone, instantly revealing all subdomains.
```bash
dnsx -axfr -d example.com
```

### 6. Reverse DNS (PTR) Probing
Given a list of IP addresses or CIDR ranges, `dnsx` can perform PTR queries to resolve IPs back to hostnames. This is highly effective when enumerating assets owned by a company's autonomous system (ASN).
```bash
echo "192.168.1.0/24" | dnsx -ptr -resp
```

## Advanced Operations and Tuning

### JSON Output for Pipeline Integration
For integration into automated attack surfaces management (ASM) pipelines, JSON output provides structured data containing the query, the resolver used, the response IPs, and the record type.
```bash
cat subdomains.txt | dnsx -json -o output.json
```
Example JSON structure:
```json
{
  "host": "dev.example.com",
  "resolver": [
    "8.8.8.8:53"
  ],
  "a": [
    "10.0.0.5"
  ],
  "status_code": "NOERROR"
}
```

### Custom Resolvers and Rate Limiting
ISPs and public resolvers (like Google or Cloudflare) implement strict rate limits. Sending 10,000 queries per second to `8.8.8.8` will quickly get your IP temporarily banned.

To mitigate this, `dnsx` allows you to provide a custom list of trusted resolvers.
```bash
dnsx -l subdomains.txt -r resolvers.txt -t 200
```
- `-r resolvers.txt`: A file containing a large list of diverse, public DNS resolvers.
By distributing queries across hundreds of resolvers, you avoid triggering rate limits on any single server, dramatically increasing the speed and reliability of your enumeration.

### Dealing with "Dead" Resolvers
Public resolvers can be unreliable. `dnsx` handles timeouts gracefully, but using a pre-validated, sanitized resolver list (often generated using `puredns`) is highly recommended for optimal performance.

## Real-World Workflow Example

A typical passive reconnaissance phase might look like this:
1. Gather subdomains from `crt.sh`, `subfinder`, and `amass`.
2. Concatenate and sort the list into `raw_subs.txt`.
3. Use `dnsx` to resolve them, extract CNAMEs, and output valid hosts.

```bash
cat raw_subs.txt | sort -u | dnsx -silent -a -cname -resp -o live_subs.txt
```

## Chaining Opportunities
- **Passive Enumeration Source**: Take inputs from `subfinder` or `crt.sh` and pass them to `dnsx` for live verification.
- **Port Scanning**: Pass the resolved IP addresses from `dnsx` directly into `naabu` for fast port enumeration.
- **Subdomain Takeover**: Filter the JSON output for `CNAME` records pointing to vulnerable cloud providers, then feed them into `nuclei`.
- **HTTP Probing**: Pipe the successfully resolved subdomains into `httpx` to determine which hosts are running web servers.

## Related Notes
- [[11 - crt.sh Certificate Transparency Query]]
- [[13 - shuffledns DNS Bruteforcing at Scale]]
- [[14 - puredns Fast DNS Resolver]]
- [[15 - httpx HTTP Probing at Scale]]
