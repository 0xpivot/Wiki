---
tags: [tools, recon, osint, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.07 Shodan Web and CLI Complete Guide"
---

# Shodan Web and CLI Complete Guide

## 1. Introduction to Shodan

Shodan is often referred to as the "search engine for the Internet of Things" or the "hacker's search engine." Unlike traditional search engines like Google that index web pages based on HTTP content and links, Shodan indexes service banners. It actively scans the entire public IPv4 space (and increasingly IPv6), connecting to thousands of ports to grab banners, negotiate SSL/TLS connections, parse FTP directories, and identify running software and hardware configurations.

For VAPT professionals, Shodan is a primary source of passive reconnaissance. It allows attackers and defenders to identify exposed infrastructure, default credentials, unpatched vulnerabilities, and misconfigured services without sending a single packet directly to the target.

## 2. Shodan Architecture and Mechanics

Shodan operates a distributed network of crawlers located around the globe. This geographic distribution helps bypass regional blocks and provides a more accurate representation of global connectivity.

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Shodan Crawler  |------>|    Shodan Database    |------>|   Shodan Web UI   |
|   (Global Scanners|       |    (Elastic/NoSQL)    |       |   (Port 443)      |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +-------------------+
         |                              |                             ^
         | Internet Scan                | API Query                   |
         v                              v                             |
+--------+----------+       +-----------+-----------+                 |
|                   |       |                       |                 |
| Target IP / Range |       |  Shodan CLI / Python  |-----------------+
| (Ports 80, 443..) |       |  (API Key Auth)       |
|                   |       |                       |
+-------------------+       +-----------------------+
```

When a Shodan crawler connects to a host, it records metadata about the connection. For an HTTP service, this includes the full HTTP response headers, the HTML body, the SSL/TLS certificate details, and computed hashes of the response (like the favicon hash).

## 3. Web Interface Search Syntax

Mastering Shodan requires fluency in its advanced search filters. Free accounts have limited access to filters, whereas paid accounts (or academic accounts) unlock full capabilities.

### Core Filters
- `port:` - Find devices listening on a specific port (e.g., `port:3389` for RDP).
- `org:` - Filter by the organization name associated with the IP's ASN (e.g., `org:"Tesla Motors"`).
- `asn:` - Search by Autonomous System Number (e.g., `asn:AS12345`).
- `country:` - Two-letter country code (e.g., `country:US`).
- `city:` - Filter by city name (e.g., `city:"San Francisco"`).

### Advanced and Vulnerability Filters
- `vuln:` - Search for specific CVEs. Shodan checks for specific vulnerabilities based on banner versions or specific probing (e.g., `vuln:CVE-2014-0160` for Heartbleed). *Note: Requires enterprise or small business tier for full access.*
- `has_vuln:True` - Quickly find hosts that Shodan has definitively identified as vulnerable.
- `http.title:` - Search the HTML title tag (e.g., `http.title:"Dashboard"`).
- `http.favicon.hash:` - Extremely powerful for finding specific web applications regardless of the domain or URL. You can hash a known favicon and find all instances globally (e.g., `http.favicon.hash:81586312` for specific spring boot apps).
- `ssl.cert.subject.CN:` - Search for SSL certificates matching a common name. Excellent for finding infrastructure hosting internal tools but exposed to the internet (e.g., `ssl.cert.subject.CN:"jira.targetcorp.com"`).

## 4. Shodan CLI Complete Reference

The Shodan Command Line Interface brings the power of the web UI to the terminal, allowing for scriptable automation and deep data extraction.

### Installation and Initialization
```bash
# Install via pip
pip3 install shodan

# Initialize with API key
shodan init YOUR_API_KEY_HERE
```

### Essential CLI Commands

1. **Host Lookup**
Provides a summary of a specific IP address, including open ports, vulnerabilities, and hostnames.
```bash
shodan host 8.8.8.8
```

2. **Searching and Downloading Data**
Instead of just viewing results, you can download the raw JSON data for offline processing. This is highly recommended for OPSEC and preserving API credits.
```bash
# Download up to 1000 results for exposed Jenkins servers
shodan download jenkins_data "port:8080 http.title:Dashboard" --limit 1000
```

3. **Parsing Downloaded Data**
The `parse` command extracts specific fields from the downloaded JSON file, outputting them in a format suitable for other tools (like Nmap or Nuclei).
```bash
# Extract IP and Port, separated by a colon
shodan parse --fields ip_str,port --separator : jenkins_data.json.gz > target_list.txt
```

4. **Network Monitoring and Alerts**
Shodan can continuously monitor your organization's IP blocks and alert you if new ports open or vulnerabilities are detected.
```bash
# Create a network alert for an IP range
shodan alert create "Corporate Subnet" 192.168.1.0/24

# List active alerts
shodan alert list
```

5. **My IP and Honeyscore**
```bash
# Check how Shodan sees your public IP
shodan myip

# Check if an IP is a honeypot (returns a score from 0.0 to 1.0)
shodan honeyscore 1.2.3.4
```

## 5. Using Shodan API in Python

For custom workflows, writing Python scripts against the Shodan API is incredibly powerful. The official `shodan` Python library provides a clean wrapper.

### Example: Bulk IP Vulnerability Checker
This script reads a list of IPs and queries Shodan for known vulnerabilities, handling rate limits gracefully.

```python
import shodan
import time
import sys

API_KEY = 'YOUR_API_KEY_HERE'
api = shodan.Shodan(API_KEY)

def check_ip(ip_address):
    try:
        # Perform the lookup
        host = api.host(ip_address)
        print(f"\n[+] Results for {ip_address}")
        print(f"Organization: {host.get('org', 'n/a')}")
        print(f"Operating System: {host.get('os', 'n/a')}")
        
        # Print all open ports
        ports = host.get('ports', [])
        print(f"Open Ports: {', '.join(map(str, ports))}")
        
        # Check for vulnerabilities
        vulns = host.get('vulns', [])
        if vulns:
            print(f"[*] VULNERABILITIES FOUND: {len(vulns)}")
            for vuln in vulns:
                print(f"  - {vuln}")
        else:
            print("[-] No vulnerabilities found in Shodan database.")
            
    except shodan.APIError as e:
        print(f"Error for {ip_address}: {e}")
        # Handle rate limiting specifically
        if "Rate limit" in str(e):
            print("Sleeping for 2 seconds due to rate limits...")
            time.sleep(2)
            check_ip(ip_address) # Retry

if __name__ == "__main__":
    ips = ["1.1.1.1", "8.8.8.8"] # Replace with target list
    for ip in ips:
        check_ip(ip)
        # Sleep to respect API limits (typically 1 request per second for basic tiers)
        time.sleep(1)
```

## 6. Case Studies and Threat Hunting

### Hunting for Unpatched Exchange Servers (ProxyLogon)
During massive exploitation events like ProxyLogon (CVE-2021-26855), Shodan can identify the global attack surface.
Query: `port:443 http.component:"Outlook Web App"`
From the results, analysts can extract the build versions from the HTTP headers to determine if the server is patched.

### Discovering Exposed ICS/SCADA Systems
Shodan is notorious for indexing industrial control systems left exposed without authentication.
- Modbus: `port:502`
- Siemens S7: `port:102`
- BACnet: `port:47808`
*Caution: Interacting directly with ICS systems during a VAPT engagement requires extreme care and explicit authorization, as fragile PLCs can crash from simple port scans.*

### The Favicon Hash Trick
Many frameworks use distinct default favicons. If a company rebrands their internal portals, they often forget to change the favicon.
1. Calculate the MurmurHash3 of the favicon.
2. Search Shodan: `http.favicon.hash:-12345678`
3. Uncover all instances of that specific application globally, bypassing CDN protections or custom domains.

## 7. Defending Against Shodan

As a defender, you want your footprint on Shodan to be as small as possible.
- **Firewall Filtering**: Block Shodan's known scanning IP addresses. While Shodan rotates IPs, a significant portion is static. However, this only blocks *Shodan*, not actual attackers.
- **Default Port Obfuscation**: Moving SSH from 22 to 2222 or RDP from 3389 to something obscure will drop you out of lazy, mass-automated searches. (Security by obscurity, but effective against untargeted noise).
- **Banner Stripping**: Remove version numbers from HTTP headers (e.g., `Server: Apache` instead of `Server: Apache/2.4.41 (Ubuntu)`).
- **Honeypots**: Deploying deceptive services that tarpit Shodan scanners or return bogus banners to waste attacker resources.

## 8. Limitations and Considerations

- **Passive vs. Active**: Shodan is passive *for you*, but active *for Shodan*. The data is only as fresh as the last crawl. A machine might show as vulnerable on Shodan but was patched yesterday.
- **IPv6 Coverage**: While improving, IPv6 scanning is vastly more complex due to the sheer size of the address space. Shodan primarily relies on finding active IPv6 addresses via NTP pools, public DNS, and other seeds.

## 9. Chaining Opportunities

- **Nuclei**: Feed IPs and Ports extracted from Shodan (`shodan parse`) directly into Nuclei for automated vulnerability verification. See [[11 - Nuclei Automation and Templates]].
- **Metasploit**: Use the `shodan_search` auxiliary module to find targets and automatically populate the RHOSTS parameter for exploitation modules.
- **Maltego**: Integrate Shodan into Maltego via the Transform Hub to visually map an organization's exposed services alongside their DNS records. See [[06 - Maltego Visual OSINT and Link Analysis]].

## 10. Related Notes
- [[02 - OSINT Methodology and Frameworks]]
- [[08 - Censys Search Syntax and API]]
- [[09 - FOFA Chinese IoT Search Engine]]
- [[03 - Nmap Advanced Port Scanning]]
