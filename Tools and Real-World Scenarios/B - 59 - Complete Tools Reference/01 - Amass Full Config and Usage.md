---
tags: [tools, recon, vapt, amass, subdomains]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.01 Amass Full Config and Usage"
---

# OWASP Amass: Deep Dive into Configuration and Usage

OWASP Amass is widely considered the gold standard for in-depth, comprehensive DNS enumeration, attack surface mapping, and external asset discovery. Unlike simpler tools that only scrape APIs, Amass utilizes a sophisticated multi-stage architecture involving active DNS resolution, continuous tracking, graph database storage, and recursive permutation generation. 

It is designed for large-scale, thorough VAPT engagements where missing a single subdomain could mean missing a critical vulnerability. The tool goes far beyond simple API querying by understanding the relationships between assets (IPs, Netblocks, ASNs, Domains) and mapping them structurally using the Open Asset Model (OAM).

## Core Architecture and Workflow

Amass operates on a graph database backend (by default, Cayley running on SQLite). Every asset it finds is modeled as a node, and the relationships (e.g., `FQDN` resolves to `IPAddress`, `IPAddress` belongs to `Netblock`) are edges.

```ascii
+-----------------------------------------------------------------------------------+
|                                 OWASP AMASS WORKFLOW                              |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +----------------+       +-------------------+       +-----------------------+   |
|  |                |       |                   |       |                       |   |
|  |  Data Sources  +------>+   Amass Core      +------>+   Graph Database      |   |
|  |  (APIs, Certs, |       |   (Event Loop)    |       |   (Cayley/SQLite)     |   |
|  |  Scraping)     |       |                   |       |                       |   |
|  +----------------+       +-------+-----------+       +-----------+-----------+   |
|                                   |                               |               |
|                                   v                               v               |
|  +----------------+       +-------+-----------+       +-----------+-----------+   |
|  |                |       |                   |       |                       |   |
|  |  Resolvers     |<------+   Permutations    |       |   Track & Compare     |   |
|  |  (Active DNS)  +------>+   (Alterations)   |       |   (Diffing Data)      |   |
|  |                |       |                   |       |                       |   |
|  +----------------+       +-------------------+       +-----------------------+   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

This graph architecture is what makes Amass exceptionally powerful. When you query for subdomains, Amass does not just print a list; it builds a network. This network can be queried later using the `amass db` subcommand to find out *how* a subdomain was discovered.

## Configuration and the `config.ini`

To get the most out of Amass, you absolutely must use a configuration file. Relying on the default execution without API keys leaves more than 60% of its capabilities dormant.

### Setting Up the Config File

By default, Amass looks for its configuration directory at `~/.config/amass/`. You can download the default `config.ini` from the Amass GitHub repository and place it in this directory.

```bash
mkdir -p ~/.config/amass
curl -sL https://raw.githubusercontent.com/owasp-amass/amass/master/examples/config.ini > ~/.config/amass/config.ini
```

### Configuring API Keys

The `config.ini` contains sections for various OSINT data sources. Some require paid subscriptions, but many are free. Registering for the free tiers of the following services is highly recommended:
- **Censys**
- **SecurityTrails**
- **Shodan**
- **GitHub** (for scraping code repositories)
- **VirusTotal**
- **AlienVault**

Example of configuring an API key in the `config.ini`:

```ini
# https://securitytrails.com (Free tier available)
[data_sources.SecurityTrails]
[data_sources.SecurityTrails.Credentials]
apikey = "YOUR_API_KEY_HERE"

# https://censys.io (Free tier available)
[data_sources.Censys]
[data_sources.Censys.Credentials]
apikey = "YOUR_API_ID_HERE"
secret = "YOUR_SECRET_HERE"

# https://github.com
[data_sources.GitHub]
[data_sources.GitHub.accountname]
apikey = "YOUR_GITHUB_PAT"
```

## Core Modules and Deep Usage

Amass is divided into several subcommands, each serving a specific phase of the reconnaissance lifecycle.

### 1. The `intel` Module (Target Discovery)

Before you can enumerate subdomains, you need to know what to enumerate. The `intel` module helps you discover root domains associated with an organization by looking up ASNs, CIDRs, and reverse WHOIS.

**Finding ASNs for a Company:**
```bash
amass intel -org "Tesla"
```
*Output might reveal ASN 394161.*

**Finding root domains inside an ASN:**
```bash
amass intel -asn 394161
```
*This will query the routing tables and public datasets to find domains hosted on Tesla's infrastructure.*

**Reverse WHOIS (Finding domains registered by the same email/name):**
```bash
amass intel -whois -d tesla.com
```

### 2. The `enum` Module (Subdomain Enumeration)

This is the workhorse of Amass. The `enum` module has multiple execution modes.

#### Passive Mode
Passive mode relies strictly on third-party APIs and scraping. It does not send any traffic to the target's infrastructure. This is crucial when operational security (OPSEC) requires stealth.

```bash
amass enum -passive -d example.com -config ~/.config/amass/config.ini
```

#### Active Mode (Default)
When run without `-passive`, Amass will actively attempt to resolve the discovered subdomains using DNS. It will also perform zone transfers (AXFR), certificate pulling, and scraping.

```bash
amass enum -active -d example.com -src -ip -dir ./amass_output
```
- `-src`: Prints the data source that found the subdomain.
- `-ip`: Resolves the subdomain to an IP address.
- `-dir`: Specifies an output directory for the database and logs.

#### Brute-Forcing and Permutations
Amass includes a highly optimized alteration engine. It takes discovered subdomains (e.g., `dev.example.com`) and applies permutations (e.g., `dev1.example.com`, `dev-staging.example.com`).

To enable aggressive brute-forcing and alterations:
```bash
amass enum -brute -w /path/to/seclists/Discovery/DNS/subdomains-top1million-110000.txt -d example.com
```

### 3. The `track` Module (Continuous Monitoring)

Bug bounty hunters and red teamers know that infrastructure changes over time. Amass allows you to track these changes by diffing the current graph database against previous runs.

To see what changed between the last two enumerations of a domain:
```bash
amass track -d example.com
```
*Output will cleanly show `[+]` for new subdomains and `[-]` for removed ones.*

### 4. The `db` Module (Graph Database Querying)

Because Amass stores everything in a graph, you can perform complex queries long after the enumeration has finished.

**List all domains in the database:**
```bash
amass db -names -d example.com
```

**Show the detailed OAM (Open Asset Model) information:**
```bash
amass db -show -d example.com
```

## Advanced Techniques and Edge Cases

### Handling Resolver Rate Limits
When performing active enumeration, Amass fires thousands of DNS queries. If you use your ISP's default DNS, you will get rate-limited, leading to massive false negatives. You must use a robust list of public resolvers.

Create a `resolvers.txt` file (you can generate this using `dnsvalidator`) and pass it to Amass:
```bash
amass enum -d example.com -rf resolvers.txt -trf trusted_resolvers.txt
```
*Note: `trusted_resolvers` are used for verifying wildcards, while standard `rf` resolvers are used for the heavy lifting of brute-forcing.*

### Dealing with Wildcard DNS
Wildcard DNS (where `*.example.com` resolves to the same IP) can ruin enumeration by generating infinite false positives. Amass handles wildcards automatically by detecting them and filtering out the noise. However, to ensure accuracy, always provide strong trusted resolvers.

## Output Parsing and Integration

Amass outputs data in several formats, including JSON line-by-line (`JSONL`). This is the preferred format for parsing into other tools.

```bash
jq -r '.name' ./amass_output/amass.json > final_subdomains.txt
```

## Chaining Opportunities

Amass is the foundation of the recon pipeline. Its output feeds directly into port scanners, HTTP probers, and vulnerability scanners:

1. **Subdomain Resolution and Probing:** Pipe Amass output into `httpx` to determine which of the thousands of subdomains actually host active web servers.
2. **Nuclei Integration:** Run the live hosts through Nuclei for quick CVE spotting.
3. **Targeted Port Scanning:** Feed the resolved IP addresses from Amass into `Naabu` or `Masscan` to discover exposed infrastructure on non-standard ports.
4. **Cloud Storage Hunting:** Pass the subdomains to cloud enum tools to find misconfigured S3 buckets related to the hostnames.

## Related Notes
- [[02 - Subfinder Config Sources API Keys]]
- [[03 - Assetfinder Lightweight Subdomain Discovery]]
- [[04 - theHarvester Full Usage Guide]]
- [[05 - Recon-ng Modular OSINT Framework]]
- [[06 - DNS Resolution and Brute Forcing]]
