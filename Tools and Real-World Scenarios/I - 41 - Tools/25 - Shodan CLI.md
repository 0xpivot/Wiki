---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.25 Shodan CLI"
---

# 25 - Shodan CLI

## 1. Introduction and Core Philosophy

Shodan is famously known as the "search engine for the Internet of Things" and internet-connected devices.
While the web interface is powerful, the Shodan Command Line Interface (CLI) provides security professionals, bug bounty hunters, and researchers with a much faster, scriptable, and highly efficient way to interact with Shodan's massive dataset.

The Shodan CLI allows users to query millions of IP addresses, search for specific open ports, identify exposed databases, and download raw JSON data of vulnerable devices—all without ever sending a single packet to the target infrastructure.
This makes it the ultimate passive reconnaissance tool.

## 2. Architecture and Internal Mechanics

The Shodan CLI is written in Python and acts as a wrapper around the Shodan REST API.
It authenticates using an API key and converts command-line arguments into complex API queries.

```text
+-----------------------------------------------------------------------+
|                              Shodan CLI                               |
+-----------------------------------------------------------------------+
|                                                                       |
|   [ User Terminal ]                                                   |
|          |  (Commands: search, host, stats, download)                 |
|          v                                                            |
|   +---------------------------------------------------------------+   |
|   |                       Shodan Python API Wrapper               |   |
|   |            (Handles Authentication, Pagination, Parsing)      |   |
|   +---------------------------------------------------------------+   |
|          |                                              ^             |
|          | HTTPS REST API Requests                      | JSON Output |
|          v                                              |             |
|   +---------------------------------------------------------------+   |
|   |                       Shodan Global Backend                   |   |
|   |   - Banner Databases         - Facet & Aggregation Engine     |   |
|   |   - CVE Mappings             - Global Crawlers                |   |
|   +---------------------------------------------------------------+   |
|                                                                       |
+-----------------------------------------------------------------------+
```

When a user executes a search, the CLI fetches the data in pages and formats it according to the user's requirements (e.g., extracting just the IP addresses or printing full service banners).

## 3. Installation and Initialization

The Shodan CLI is easily installed via Python's package manager (`pip`).
Once installed, it must be initialized with an API key, which is saved locally.

```bash
# Installation
pip install shodan

# Initialization
shodan init YOUR_SHODAN_API_KEY
```

## 4. Key Commands and Usage

### 4.1 Host Information (`host`)

The `host` command provides detailed intelligence on a single IP address.
It reveals open ports, service banners, physical location, ASN, and identified vulnerabilities (CVEs).

```bash
# Querying a specific IP address
shodan host 8.8.8.8
```

### 4.2 Searching the Global Database (`search`)

The `search` command is the equivalent of using the Shodan web search bar.
It returns a list of devices matching the query.
Using Shodan search filters (like `port:`, `org:`, `product:`) is highly recommended to narrow down results.

```bash
# Basic search for Apache servers
shodan search apache

# Targeted search: Tomcat servers in Germany
shodan search "product:Tomcat country:DE"

# Searching for specific exposed services by port
shodan search "port:3389 org:'Target Company'"
```

To make the output script-friendly, the `--fields` argument is heavily used:
```bash
# Extracting only IP address and port for pipelining
shodan search "port:22" --fields ip_str,port
```

### 4.3 Statistical Aggregation (`stats`)

The `stats` command provides a macroscopic view of a query without downloading the individual host data.
It is excellent for identifying trends, such as "What are the most common versions of IIS running globally?" or "Which countries have the most exposed RDP ports?"

```bash
# Aggregate statistics for exposed RDP ports by country
shodan stats port:3389 --facets country
```

### 4.4 Downloading Data (`download` and `parse`)

For large engagements, downloading the raw JSON data is preferable to querying it continuously.
The `download` command saves the results to a compressed JSON file, which can later be queried locally using `parse`.

```bash
# Download up to 1000 results for a specific query
shodan download exposed_dbs "product:MongoDB" --limit 1000

# Parse the downloaded file locally to extract IPs
shodan parse --fields ip_str exposed_dbs.json.gz
```

### 4.5 Monitoring Infrastructure (`alert`)

The CLI allows users to create network alerts.
Shodan will actively monitor a specific IP range and notify the user (via email or webhook) if a new port opens or a new service is detected.
This is heavily used for continuous attack surface management (ASM).

```bash
# Creating a monitoring alert for a specific netblock
shodan alert create "Corporate Infrastructure" 192.0.2.0/24
```

## 5. Advanced Search Filters

Mastering the CLI requires mastering Shodan's query syntax:
- `city:` Find devices in a specific city.
- `country:` Find devices in a specific country.
- `geo:` Define a bounding box using coordinates.
- `hostname:` Match text in the hostname/domain.
- `net:` Search based on an IP range or CIDR.
- `os:` Filter by operating system.
- `port:` Filter by specific open port.
- `vuln:` Search for specific CVEs (Requires an Enterprise API key).

Example of a complex query:
```bash
# Finding exposed Jenkins instances on AWS infrastructure in the US
shodan search "product:Jenkins org:'Amazon.com' country:US"
```

## 6. Common Pitfalls and Limitations

1. **Data Staleness:** Shodan crawlers hit different parts of the internet at different intervals. An IP listed as having Port 80 open might have been firewalled three days ago. Always verify Shodan data with active tools (like Nmap) if OPSEC allows.
2. **Query Credits:** The `search` and `download` commands consume API query credits. Free or basic tier accounts will hit limits quickly if overly broad searches are executed.
3. **Enterprise Filters:** Certain filters, notably `vuln:`, require expensive enterprise licenses and will error out on standard accounts.

## 7. Practical Assessment Scenarios

### 7.1 Identifying Shadow IT
A penetration tester is given a list of ASNs owned by the client.
They use the Shodan CLI to query the entire ASN for exposed databases, immediately identifying an unauthenticated MongoDB instance left over from a forgotten development project.
```bash
shodan search "asn:AS12345 product:MongoDB"
```

### 7.2 Threat Intelligence and Global Research
A security researcher tracking a new IoT botnet uses the `stats` command to track the geographical distribution of compromised devices exposing a specific banner.

## 8. Chaining Opportunities

- **[[06 - Nmap]]**: IPs extracted from Shodan CLI using `parse` are fed directly into Nmap to verify if the ports are currently open and to gather real-time state.
- **[[22 - Amass]]**: IPs discovered via Amass enumeration can be queried one-by-one using `shodan host` to passively identify running services without actively scanning.
- **[[23 - Subfinder]]**: Combined with Subfinder, researchers can map an entire subdomain structure and immediately correlate those subdomains to vulnerable software versions indexed by Shodan.
- **[[24 - theHarvester]]**: Can complement Shodan by providing context (like employee emails) to the technical infrastructure discovered.

## 9. Related Notes

- [[03 - Passive OSINT and Intelligence Gathering]]
- [[01 - External Reconnaissance Methodologies]]
- [[26 - Arjun]]
- [[16 - Vulnerability Scanning and Triage]]
