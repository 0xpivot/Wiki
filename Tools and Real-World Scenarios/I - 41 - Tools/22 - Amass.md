---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.22 Amass"
---

# 22 - Amass

## 1. Introduction and Core Philosophy

OWASP Amass is a highly advanced, open-source information gathering and attack surface mapping tool.
It specializes in deep DNS enumeration, subdomain discovery, and mapping out the external assets of a target organization.
Unlike simple dictionary-based subdomain brute-forcers, Amass uses a multitude of techniques including scraping, API integration, certificate parsing, and recursive brute-forcing to build a comprehensive picture of a target's infrastructure.

Amass is heavily utilized during the initial reconnaissance phase of penetration tests, bug bounty hunting, and red team engagements.
Its ability to correlate data from dozens of sources simultaneously makes it an indispensable utility for identifying forgotten, unmonitored, or hidden subdomains that may host vulnerable applications.

## 2. Architecture and Internal Mechanics

Amass operates on an intelligent graph-based engine. 
Instead of just maintaining a flat list of subdomains, it understands relationships between IP addresses, netblocks, ASNs, and domains.

```text
+-----------------------------------------------------------------------+
|                              OWASP Amass                              |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ External Data Sources ]                                           |
|     - Search Engines (Google, Bing)                                   |
|     - APIs (Censys, Shodan, SecurityTrails)                           |
|     - Certificate Transparency Logs (Crt.sh)                          |
|             |                                                         |
|             v                                                         |
|   +-------------------+       +-------------------------+             |
|   |                   |       |                         |             |
|   |  Data Collector   | ----> |  Graph Database Engine  |             |
|   |  (Scraper/API)    |       |  (Stores Relationships) |             |
|   |                   |       |                         |             |
|   +-------------------+       +-------------------------+             |
|             |                               |                         |
|             v                               v                         |
|   +-------------------+       +-------------------------+             |
|   |                   |       |                         |             |
|   | DNS Resolution &  | ----> |   Output Formatters     |             |
|   |   Brute-forcing   |       | (JSON, Text, Graph DB)  |             |
|   |                   |       |                         |             |
|   +-------------------+       +-------------------------+             |
|                                                                       |
+-----------------------------------------------------------------------+
```

This graph database approach allows Amass to continuously feed newly discovered assets back into its engine, pivoting off IP ranges to find even more domains associated with the target.

## 3. Key Subcommands and Features

Amass is divided into several subcommands, each serving a distinct purpose in the reconnaissance lifecycle.

### 3.1 Enum (Enumeration)

The `enum` subcommand is the most frequently used feature. It performs DNS enumeration and network mapping.
It can run in passive or active modes.

```bash
# Passive enumeration (no direct interaction with the target)
amass enum -passive -d example.com

# Active enumeration (includes zone transfers and active DNS resolution)
amass enum -active -d example.com

# Using a specific wordlist for brute-forcing
amass enum -brute -w /path/to/wordlist.txt -d example.com
```

### 3.2 Intel (Intelligence Gathering)

The `intel` subcommand is used to discover the root domain names associated with an organization.
It can search via ASN (Autonomous System Number) or organization names.

```bash
# Finding domains belonging to a specific ASN
amass intel -asn 1337

# Finding domains based on an organization name
amass intel -org "Example Corp"

# Reverse Whois search
amass intel -whois -d example.com
```

### 3.3 DB (Database Management)

Since Amass stores results in a local graph database, the `db` subcommand allows users to query and manipulate historical data without having to re-run time-consuming enumerations.

```bash
# Showing the summary of the database
amass db -show

# Listing all discovered names for a specific domain from past scans
amass db -names -d example.com
```

### 3.4 Track (Tracking Changes)

The `track` subcommand compares previous enumerations to identify changes in the target's infrastructure.
This is incredibly useful for continuous monitoring and bug bounty hunting to spot newly deployed assets.

```bash
# Tracking changes across the last two scans
amass track -d example.com
```

## 4. Advanced Configuration Options

Amass's true power is unlocked when configured with API keys for external services.
The `config.ini` file allows users to define API keys for services like Shodan, Censys, SecurityTrails, and VirusTotal, drastically increasing the tool's effectiveness.

Example snippet from `config.ini`:
```ini
[data_sources.SecurityTrails]
apikey = "YOUR_API_KEY_HERE"

[data_sources.Censys]
apikey = "YOUR_API_KEY_HERE"
secret = "YOUR_SECRET_HERE"

[data_sources.Shodan]
apikey = "YOUR_API_KEY_HERE"
```

Using the configuration file during enumeration:
```bash
amass enum -config config.ini -d example.com
```

## 5. Performance and Tuning

Amass can be resource-intensive, particularly regarding network traffic and DNS queries.
Tuning its performance is essential to prevent network congestion or getting banned by DNS resolvers.

- **Resolvers:** Supplying a list of reliable, fast DNS resolvers prevents Amass from bottlenecking on default system resolvers.
- **Max DNS Queries:** Limiting the number of concurrent DNS queries.

```bash
# Using custom resolvers and limiting concurrent queries
amass enum -d example.com -rf resolvers.txt -max-dns-queries 100
```

## 6. Output Formats and Integration

Amass supports multiple output formats, making it easy to integrate into larger automation pipelines.

- **Plaintext:** Simple list of subdomains.
- **JSON / JSONL:** Detailed output including IP addresses, sources, and ASN data.
- **Graph:** Exporting data for visualization in tools like Gephi or Maltego.

```bash
# Outputting results to a JSON file
amass enum -d example.com -json amass_output.json

# Outputting relationships in D3.js format for visualization
amass viz -d3 -d example.com
```

## 7. Common Pitfalls and Troubleshooting

1. **False Positives:** Wildcard DNS records can cause Amass (and any brute-forcer) to report non-existent subdomains as alive. Amass has built-in wildcard detection, but it can occasionally fail.
2. **API Rate Limiting:** Free-tier API keys may get exhausted quickly. It is critical to monitor API usage and spread queries over time if necessary.
3. **Database Corruption:** Interrupting Amass forcefully can corrupt its local database. Always allow it to shut down gracefully.

## 8. Practical Scenarios

### 8.1 Bug Bounty Reconnaissance
A bug bounty hunter starts an engagement by running `amass intel` to map out the target's ASNs, followed by `amass enum` using multiple API keys to discover thousands of subdomains. The results are fed into tools like `httpx` to probe for live web servers.

### 8.2 Red Team Infrastructure Mapping
A red team uses Amass in strict passive mode to map the target's external footprint without generating any direct traffic that might trigger SIEM alerts or IDS rules.

## 9. Chaining Opportunities

- **[[23 - Subfinder]]**: While Amass is exhaustive, Subfinder is incredibly fast. They are often used together, piping their combined, deduplicated output into a master asset list.
- **[[25 - Shodan CLI]]**: IPs discovered via Amass can be fed into Shodan CLI to rapidly identify open ports, banners, and known CVEs without active scanning.
- **[[06 - Nmap]]**: The final list of resolved IP addresses from Amass can be fed directly into Nmap for detailed port scanning and service enumeration.
- **[[26 - Arjun]]**: Once live web applications are found on Amass-discovered subdomains, Arjun can be used to discover hidden parameters on those endpoints.

## 10. Related Notes

- [[01 - External Reconnaissance Methodologies]]
- [[05 - DNS Enumeration and Zone Transfers]]
- [[13 - Automating Bug Bounty Pipelines]]
- [[24 - theHarvester]]
- [[21 - John the Ripper]]
