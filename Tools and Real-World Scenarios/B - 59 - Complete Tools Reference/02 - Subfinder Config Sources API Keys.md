---
tags: [tools, recon, vapt, subfinder, passive]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.02 Subfinder Config Sources API Keys"
---

# Subfinder: Mastery of Passive Subdomain Enumeration

Subfinder, developed by ProjectDiscovery, is a lightning-fast, highly concurrent passive subdomain discovery tool. While tools like Amass attempt to map the entire network graph using both active and passive techniques, Subfinder specializes strictly in passive discovery. It scrapes search engines, interrogates public APIs, parses certificates, and extracts data from archival sources without directly touching the target's infrastructure.

For bug bounty hunters and penetration testers, Subfinder is often the first tool executed in a reconnaissance pipeline due to its unparalleled speed and excellent integration with standard Unix pipelines.

## Core Philosophy and Architecture

Subfinder is written in Go and leverages Go routines for massive concurrency. It reads from a predefined list of sources (over 50+ integrations exist natively) and aggregates the results, simultaneously removing duplicates in memory.

```ascii
+-----------------------------------------------------------------------------------+
|                            SUBFINDER ARCHITECTURE                                 |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +----------------+   +----------------+   +----------------+   +--------------+  |
|  | GitHub API     |   | Shodan API     |   | Crt.sh (SSL)   |   | WayBack      |  |
|  +-------+--------+   +-------+--------+   +-------+--------+   +-------+------+  |
|          |                    |                    |                    |         |
|          v                    v                    v                    v         |
|  +-------+--------------------+--------------------+--------------------+------+  |
|  |                                                                             |  |
|  |                        SUBFINDER CORE ENGINE                                |  |
|  |                                                                             |  |
|  |  +----------------+    +------------------+    +-----------------------+    |  |
|  |  | API Key Mgr    |    | Go Routines      |    | Deduplication         |    |  |
|  |  +----------------+    +------------------+    +-----------------------+    |  |
|  +---------------------------------+-------------------------------------------+  |
|                                    |                                              |
|                                    v                                              |
|  +---------------------------------+-------------------------------------------+  |
|  |                       Standard Output (stdout) / JSON Output                |  |
|  |                       e.g., api.target.com, dev.target.com                  |  |
|  +---------------------------------+-------------------------------------------+  |
|                                    |                                              |
|                                    v                                              |
|                          Pipeline to (httpx / dnsx / nuclei)                      |
+-----------------------------------------------------------------------------------+
```

Because Subfinder operates purely passively, it is completely stealthy. The target organization will not see any DNS requests or HTTP probes originating from your IP address during this phase of the engagement.

## Configuration: The `provider-config.yaml`

A common mistake made by junior testers is running Subfinder immediately after installation without configuring API keys. Without API keys, Subfinder will only query public, unauthenticated sources (like `crt.sh` and `Hackertarget`), severely limiting its scope.

The configuration file is typically located at:
`~/.config/subfinder/provider-config.yaml`

### Acquiring and Setting API Keys

To maximize Subfinder's potential, register for free tiers at the following essential services:
- **BinaryEdge**
- **Censys**
- **CertSpotter**
- **Chaos** (ProjectDiscovery's own dataset - requires invite/registration)
- **SecurityTrails** (Crucial for historical DNS data)
- **Shodan**
- **VirusTotal**
- **GitHub**

Once acquired, populate the `provider-config.yaml`:

```yaml
binaryedge:
  - YOUR_BINARYEDGE_KEY
censys:
  - YOUR_CENSYS_ID:YOUR_CENSYS_SECRET
certspotter:
  - YOUR_CERTSPOTTER_KEY
github:
  - ghp_YOUR_GITHUB_PERSONAL_ACCESS_TOKEN
securitytrails:
  - YOUR_SECURITYTRAILS_KEY
shodan:
  - YOUR_SHODAN_KEY
virustotal:
  - YOUR_VIRUSTOTAL_KEY
```

By adding these keys, Subfinder's yield will often increase by 300% to 400% compared to an unconfigured run.

## Core Flags and Execution

Subfinder is designed to do one thing perfectly, which means its command-line interface is highly focused.

### Basic Enumeration
To run a basic scan against a target domain:
```bash
subfinder -d example.com
```

### The `all` Flag
By default, Subfinder executes a curated list of reliable, fast sources. To force Subfinder to use *every* available source (including slower ones), use the `-all` flag. This takes longer but yields more results.
```bash
subfinder -d example.com -all
```

### Recursive Discovery
Sometimes, domains have deeply nested subdomains (e.g., `api.dev.eu.example.com`). Subfinder can be instructed to operate recursively. If it finds a subdomain, it will treat that subdomain as a new target and query the APIs again.
```bash
subfinder -d example.com -recursive
```

### JSON Output for Automation
For professional engagements, raw text is difficult to parse programmatically. Subfinder natively supports JSON lines (`JSONL`) output, which includes metadata such as the source that discovered the subdomain.
```bash
subfinder -d example.com -oJ -o subfinder_results.json
```
*Sample Output:*
```json
{"host":"api.example.com","source":"securitytrails"}
{"host":"dev.example.com","source":"github"}
```

## Advanced Workflows and Integrations

Subfinder thrives when used as the source for Unix pipelines in bash scripts. Because it outputs clean lists of subdomains to `stdout`, it integrates beautifully with the rest of the ProjectDiscovery ecosystem.

### Silent Mode for Clean Pipelines
When piping Subfinder's output, you do not want its banner or progress updates corrupting the downstream tools. The `-silent` flag ensures that *only* the discovered subdomains are printed.

### 1. The Resolution Pipeline (`dnsx`)
Subfinder finds *historical* and *passive* data. This means many of the subdomains it returns may no longer exist (dead DNS records). To clean the list and find only live targets, pipe it directly into `dnsx`:

```bash
subfinder -d example.com -silent | dnsx -silent -a -cname -resp
```
This command finds the subdomains passively, and immediately actively resolves them, printing only those that successfully resolve, along with their A and CNAME records.

### 2. The HTTP Probing Pipeline (`httpx`)
If you are looking for web applications, resolving IP addresses isn't enough; you need to know if HTTP/HTTPS services are running.

```bash
subfinder -d example.com -silent | httpx -silent -title -status-code -tech-detect
```
This powerful one-liner performs full passive recon and instantly fingerprints all running web services on the discovered subdomains, fetching the page title and underlying technologies (e.g., Nginx, React, PHP).

### 3. Continuous Monitoring (Cron Automation)
Because Subfinder is fast and resource-light, it is ideal for continuous monitoring in cron jobs. A simple bash script can run Subfinder daily, compare the new results to the previous day's results using `comm` or `anew`, and alert you via Slack/Discord if new infrastructure appears.

```bash
#!/bin/bash
TARGET="example.com"
subfinder -d $TARGET -silent -all | anew ~/.recon/$TARGET/subdomains.txt | notify -id slack
```
*(Requires `anew` and `notify` tools).*

## Troubleshooting and Edge Cases

- **Rate Limiting:** If you run Subfinder constantly on multiple domains concurrently, free-tier API providers (like SecurityTrails) will temporarily ban your key. Monitor your API usage limits carefully.
- **Wildcard Clutter:** Subfinder simply reports what it finds in APIs. If a target uses wildcard DNS, passive sources might contain thousands of randomly generated junk subdomains. Subfinder cannot filter wildcards natively (as it doesn't resolve DNS). You must handle wildcards downstream using `dnsx` or `puredns`.
- **Missing Internal Subdomains:** Subfinder will never find purely internal subdomains that have not been exposed in public DNS logs, certificates, or code repositories. Active brute-forcing is required for those.

## Chaining Opportunities

- **Subfinder -> dnsx -> httpx -> nuclei**: The classic ProjectDiscovery automated attack surface mapping and vulnerability scanning pipeline.
- **Subfinder -> naabu**: Feed the discovered domain names directly into the fast port scanner to map out non-HTTP services.
- **Subfinder -> waybackurls/gau**: Use the discovered subdomains to aggressively scrape the Wayback Machine for historical endpoints and parameters.

## Related Notes
- [[01 - Amass Full Config and Usage]]
- [[03 - Assetfinder Lightweight Subdomain Discovery]]
- [[04 - theHarvester Full Usage Guide]]
- [[05 - Recon-ng Modular OSINT Framework]]
- [[06 - DNS Resolution and Brute Forcing]]
