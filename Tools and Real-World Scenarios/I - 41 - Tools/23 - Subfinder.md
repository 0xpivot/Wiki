---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.23 Subfinder"
---

# 23 - Subfinder

## 1. Introduction and Core Philosophy

Subfinder is a lightning-fast, passive subdomain discovery tool developed by ProjectDiscovery.
It is built in Go and is specifically engineered to be modular, extensible, and extremely fast.
Unlike comprehensive multi-tool suites like Amass, Subfinder focuses purely on passive enumeration—it discovers valid subdomains for websites by using passive online sources without directly interacting with the target's infrastructure.

This passive nature makes it an essential tool for stealthy reconnaissance, bug bounty hunting, and continuous asset monitoring where speed and OPSEC (Operational Security) are paramount.
Because it does not send requests directly to the target domain's nameservers or web servers, it leaves no immediate footprint on the target's intrusion detection systems (IDS).

## 2. Architecture and Internal Mechanics

Subfinder's architecture is based on highly concurrent Go routines.
It queries multiple specialized APIs, search engines, and certificate transparency logs simultaneously, parses the results concurrently, and deduplicates the output in real-time.

```text
+-----------------------------------------------------------------------+
|                               Subfinder                               |
+-----------------------------------------------------------------------+
|                                                                       |
|   +---------------------------------------------------------------+   |
|   |                   Passive Data Providers                      |   |
|   |  [Shodan] [Censys] [VirusTotal] [Crt.sh] [BinaryEdge] [etc]   |   |
|   +---------------------------------------------------------------+   |
|            |            |             |              |            |   |
|            v            v             v              v            |   |
|   +---------------------------------------------------------------+   |
|   |                  Concurrent Go Routines Engine                |   |
|   |            (Asynchronous fetching and parsing)                |   |
|   +---------------------------------------------------------------+   |
|                                |                                      |
|                                v                                      |
|   +---------------------------------------------------------------+   |
|   |                  Deduplication & Filtering Engine             |   |
|   |             (Removes duplicates, validates scope)             |   |
|   +---------------------------------------------------------------+   |
|                                |                                      |
|                                v                                      |
|   +---------------------------------------------------------------+   |
|   |                       Output Formatter                        |   |
|   |                   (Stdout, JSON, Text File)                   |   |
|   +---------------------------------------------------------------+   |
|                                                                       |
+-----------------------------------------------------------------------+
```

The tool uses a provider-based model. Each source of information (e.g., Shodan, Censys) is implemented as a separate provider module, making it incredibly easy to add new sources as they become available.

## 3. Key Features and Usage

### 3.1 Basic Enumeration

The simplest use case for Subfinder is to query all default, non-key-requiring providers for a single domain.

```bash
# Basic passive enumeration
subfinder -d example.com

# Enumerating subdomains and saving to a file
subfinder -d example.com -o subdomains.txt
```

### 3.2 Using API Keys for Extended Reach

While Subfinder is effective out-of-the-box, its true potential is unlocked when configured with API keys.
Many providers (like SecurityTrails, GitHub, Shodan, and Censys) require authentication.

API keys are stored in a configuration file, typically located at `~/.config/subfinder/provider-config.yaml`.

Example configuration:
```yaml
shodan:
  - YOUR_SHODAN_API_KEY
securitytrails:
  - YOUR_SECURITYTRAILS_API_KEY
censys:
  - YOUR_CENSYS_ID:YOUR_CENSYS_SECRET
github:
  - YOUR_GITHUB_TOKEN
```

### 3.3 Silent Mode and Pipelining

Subfinder is explicitly designed to fit into UNIX-style pipelines.
The `-silent` flag suppresses all banner and logging output, printing only the discovered subdomains to stdout.
This makes it perfect for chaining with other tools.

```bash
# Pipe Subfinder output directly into httpx to find live web servers
subfinder -d example.com -silent | httpx -silent
```

### 3.4 Multi-Domain Processing

Subfinder can process a list of domains efficiently, applying concurrent querying across the entire list.

```bash
# Process a list of root domains
subfinder -dL domains.txt -o all_subdomains.txt
```

## 4. Advanced Options and Tuning

Subfinder offers several flags to tune its performance and alter its behavior depending on network conditions and OPSEC requirements.

- **Excluding Providers:** Sometimes a specific provider might be slow or currently blocking the IP. It can be excluded.
  ```bash
  subfinder -d example.com -exclude-sources shodan,censys
  ```

- **Specific Providers Only:** Conversely, you can restrict Subfinder to only query specific, highly trusted sources.
  ```bash
  subfinder -d example.com -sources securitytrails,crtsh
  ```

- **Concurrency Control:** While fast, too much concurrency might lead to dropped connections or local resource exhaustion.
  ```bash
  # Limiting the maximum number of concurrent HTTP requests
  subfinder -d example.com -t 10
  ```

## 5. Subfinder vs. Amass

It is common to compare Subfinder with Amass, as both are premier subdomain enumeration tools.
- **Speed:** Subfinder is significantly faster because it operates exclusively passively (unless actively resolving with external tools). Amass includes active brute-forcing and recursive resolution, which takes longer.
- **Scope:** Amass builds a holistic graph of the infrastructure (ASNs, Netblocks). Subfinder strictly returns lists of subdomains.
- **Use Case:** Subfinder is favored for rapid bug bounty pipelines and quick recon. Amass is favored for deep, exhaustive penetration tests where time is less of a constraint.

## 6. Integration in Automation Pipelines

Due to its speed and JSON output capabilities, Subfinder is a staple in automated reconnaissance pipelines (e.g., using bash scripts or workflow orchestrators like ProjectDiscovery's Notify or Axiom).

```bash
# Outputting results in JSON format for parsing by other tools like jq
subfinder -d example.com -json | jq -r '.host'
```

## 7. Practical Scenarios

### 7.1 Continuous Asset Monitoring
A security team sets up a cron job to run Subfinder against their organization's domains daily.
The output is compared against the previous day's output using `diff`.
Any new subdomains are immediately flagged and sent to a Slack channel via a webhook, alerting the team to shadow IT or newly deployed infrastructure.

### 7.2 The "Recon.sh" Bash Pipeline
A bug bounty hunter creates a script:
```bash
#!/bin/bash
DOMAIN=$1
echo "[+] Running Subfinder..."
subfinder -d $DOMAIN -silent > subs.txt
echo "[+] Resolving live hosts..."
cat subs.txt | dnsx -silent > alive_subs.txt
echo "[+] Probing for HTTP..."
cat alive_subs.txt | httpx -silent > live_http.txt
```

## 8. Pitfalls and Limitations

- **Blind Spots:** Because Subfinder is passive, it can only find subdomains that have been indexed by third parties or logged in public certificate transparency logs. Internal subdomains or newly created dev environments without public SSL certificates will be missed.
- **API Exhaustion:** If running across massive lists of root domains, free-tier API limits on configured providers will be hit rapidly.

## 9. Chaining Opportunities

- **[[22 - Amass]]**: Subfinder's output is often combined with Amass's output to ensure maximum coverage before deduplication.
- **[[08 - Httpx]]**: As shown above, Subfinder is almost always piped into `httpx` to determine which of the discovered subdomains actually host live web applications.
- **[[25 - Shodan CLI]]**: Discovered subdomains can be resolved to IPs and fed into Shodan to identify the underlying infrastructure and open ports.
- **[[24 - theHarvester]]**: Can be used alongside theHarvester to correlate discovered subdomains with employee emails found in similar OSINT sources.

## 10. Related Notes

- [[01 - External Reconnaissance Methodologies]]
- [[03 - Passive OSINT and Intelligence Gathering]]
- [[13 - Automating Bug Bounty Pipelines]]
- [[26 - Arjun]]
