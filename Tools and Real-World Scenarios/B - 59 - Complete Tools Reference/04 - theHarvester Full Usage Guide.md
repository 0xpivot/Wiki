---
tags: [tools, recon, vapt, osint, theharvester]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.04 theHarvester Full Usage Guide"
---

# theHarvester: Full Usage Guide for OSINT Gathering

theHarvester is one of the oldest and most trusted Open Source Intelligence (OSINT) gathering tools in the penetration testing community. While tools like Amass and Subfinder focus heavily on infrastructure (subdomains, ASNs), theHarvester straddles the line between infrastructure recon and human-centric OSINT. 

It is designed to discover:
- Subdomains and IP addresses
- Email addresses associated with the target domain
- Employee names
- Open ports and banners (via Shodan integration)

This unique blend makes theHarvester invaluable for both external infrastructure assessments and social engineering/phishing campaigns.

## Core Architecture and Modules

theHarvester is written in Python. It relies on a modular architecture where different "sources" (search engines, APIs, PGP key servers) are queried independently. 

```ascii
+-----------------------------------------------------------------------------------+
|                              THEHARVESTER ECOSYSTEM                               |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                         Target Input: example.com                                 |
|                                     |                                             |
|          +--------------------------+---------------------------+                 |
|          |                          |                           |                 |
|  +-------v--------+         +-------v--------+          +-------v--------+        |
|  |                |         |                |          |                |        |
|  | Search Engines |         | PGP / Intel    |          | Infrastructure |        |
|  | (Baidu, Bing,  |         | (PGP Servers,  |          | (Shodan,       |        |
|  |  DuckDuckGo,   |         |  Hunter.io,    |          |  DNSDumpster,  |        |
|  |  Yahoo)        |         |  LinkedIn)     |          |  Censys)       |        |
|  |                |         |                |          |                |        |
|  +-------+--------+         +-------+--------+          +-------+--------+        |
|          |                          |                           |                 |
|          +--------------------------+---------------------------+                 |
|                                     |                                             |
|                                     v                                             |
|                        +--------------------------+                               |
|                        |  Core Processing Engine  |                               |
|                        |  (Regex / Parsing)       |                               |
|                        +------------+-------------+                               |
|                                     |                                             |
|                +--------------------+---------------------+                       |
|                v                    v                     v                       |
|        +---------------+    +---------------+    +------------------+             |
|        | Subdomains    |    | Email Addrs   |    | Employee Names   |             |
|        +---------------+    +---------------+    +------------------+             |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## Configuration and API Keys

While theHarvester works out-of-the-box using standard search engine scraping, search engines frequently deploy CAPTCHAs or ban IPs that scrape them aggressively. To unlock theHarvester's full potential, you must configure its API keys.

The configuration file is typically located at `/etc/theHarvester/api-keys.yaml` (or within the cloned repository directory if running from source).

### Essential API Keys
1. **Hunter.io**: Absolutely critical for email discovery. Hunter.io maintains a massive database of corporate email addresses and the patterns used to generate them (e.g., `first.last@company.com`).
2. **Shodan**: Used for IP enumeration, port discovery, and service banner grabbing.
3. **Censys**: Excellent for historical SSL certificate data.
4. **SecurityTrails**: Powerful for historical DNS records and subdomain enumeration.

*Example `api-keys.yaml`:*
```yaml
apikeys:
  hunter: "YOUR_HUNTER_API_KEY"
  shodan: "YOUR_SHODAN_API_KEY"
  censys_id: "YOUR_CENSYS_ID"
  censys_secret: "YOUR_CENSYS_SECRET"
  securityTrails: "YOUR_SECURITYTRAILS_KEY"
```

## Core Execution and Flags

theHarvester uses standard Python `argparse` flags. The most critical flags are `-d` (domain), `-b` (data source), and `-l` (limit).

### Basic Execution (Single Source)
To run a quick search against a specific engine like Baidu:
```bash
theHarvester -d example.com -b baidu -l 500
```
- `-d example.com`: The target domain.
- `-b baidu`: The data source to query.
- `-l 500`: Limit the number of search engine results to parse (prevents endless scraping and blocking).

### The "All" Sources Mode
To query every available module (search engines, APIs, certificate logs):
```bash
theHarvester -d example.com -b all
```
*Warning: Using `-b all` will send requests to dozens of services. If you are not using a proxy or VPN, your IP may get temporarily blacklisted by Google, Bing, and DuckDuckGo due to aggressive scraping behavior.*

### Proxying Requests
To avoid burning your primary IP address when scraping search engines, route theHarvester's traffic through HTTP/SOCKS proxies. Create a `proxies.yaml` file in the configuration directory and run:
```bash
theHarvester -d example.com -b all -p
```
The `-p` flag instructs the tool to proxy the requests based on the YAML config.

## Advanced Usage and Output Parsing

### Active DNS Resolution
theHarvester is primarily a passive tool, but it includes an active DNS resolution engine to verify if discovered subdomains actually exist.
```bash
theHarvester -d example.com -b all -r -c
```
- `-r`: Resolve discovered hostnames via DNS.
- `-c`: Perform DNS brute-forcing (this uses an internal dictionary to guess common subdomains like `vpn`, `mail`, `dev`).

### Shodan Integration
If you have configured a Shodan API key, you can instruct theHarvester to take the IP addresses it discovers and query Shodan for open ports and banners.
```bash
theHarvester -d example.com -b all -s
```
- `-s`: Query Shodan for discovered IP addresses. This is incredibly powerful as it bridges the gap between passive OSINT and active port scanning without sending a single packet to the target.

### Exporting Data (XML and JSON)
For reporting and pipeline automation, you must export the data. theHarvester supports robust XML and JSON outputs.

```bash
theHarvester -d example.com -b all -f harvester_results
```
The `-f` flag saves the output to `harvester_results.xml` and `harvester_results.json` simultaneously.

*Parsing JSON output using `jq`:*
To extract just the discovered emails for a phishing campaign:
```bash
jq -r '.emails[]' harvester_results.json > target_emails.txt
```
To extract subdomains:
```bash
jq -r '.hosts[]' harvester_results.json | awk -F':' '{print $1}' > target_subdomains.txt
```

## Tactical Use Cases

1. **Phishing Campaign Preparation:** Use theHarvester with Hunter.io and LinkedIn modules to build a list of valid employee emails. Parse this list into your GoPhish framework.
2. **Identifying Legacy Infrastructure:** Old IPs and subdomains often linger in search engine caches long after the company removes them from their main website. The `bing` and `yahoo` modules are surprisingly effective at finding forgotten infrastructure.
3. **Acquisition Mapping:** Using reverse WHOIS integrations to find other domains owned by the same organization.

## Limitations

- **Search Engine Blocks:** Google frequently updates its HTML structure and CAPTCHA aggressiveness. The Google module in theHarvester often breaks or returns zero results if your IP is flagged. Rely heavily on APIs (Hunter, Shodan) rather than purely on scraping.
- **False Positives in Emails:** Scraping web pages for the `@` symbol generates false positives (e.g., `info@w3.org`, `contact@example.com`). Always verify the emails using an SMTP verifier before launching a phishing campaign.

## Chaining Opportunities

- **theHarvester -> GoPhish**: Extract all employee emails and feed them into a spear-phishing platform.
- **theHarvester -> grep -> dnsx**: Extract the `hosts` array from the JSON output, filter for subdomains, and actively resolve them using `dnsx` to confirm they are still alive.
- **theHarvester -> nuclei**: Feed the discovered Shodan IPs/Ports directly into Nuclei to scan for CVEs on exposed services.

## Related Notes
- [[01 - Amass Full Config and Usage]]
- [[02 - Subfinder Config Sources API Keys]]
- [[05 - Recon-ng Modular OSINT Framework]]
- [[12 - Email Enumeration and Verification]]
- [[15 - Social Engineering and Phishing Infrastructure]]
