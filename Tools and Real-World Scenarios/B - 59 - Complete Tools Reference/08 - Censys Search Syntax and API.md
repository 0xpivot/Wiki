---
tags: [tools, recon, osint, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.08 Censys Search Syntax and API"
---

# Censys Search Syntax and API

## 1. Introduction to Censys

Censys is a continuous attack surface management platform and search engine that actively scans the public Internet. Developed by the researchers at the University of Michigan (who also created the ZMap scanner), Censys provides a comprehensive, structured dataset of hosts, services, and digital certificates. 

While Shodan is often considered the general-purpose "hacker search engine," Censys excels in its rigorous parsing of cryptographic data, specifically **X.509 certificates**, and its robust structured JSON architecture. For penetration testers and threat intelligence analysts, Censys is unparalleled for tracking infrastructure through certificate transparency (CT) logs and pivoting from known malicious certificates to hidden IP addresses.

## 2. Architecture: ZMap and ZGrab2

Censys relies on open-source scanning technologies developed by its founders.

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|  ZMap (Stateless) |------>|   ZGrab2 (Stateful)   |------>|  Censys Database  |
|  (Finds Open Ports|       |   (Banner Grabbing)   |       |  (BigQuery / DB)  |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +---------+---------+
         |                              |                             |
         | SYN Packets                  | App-layer Probes            | Web & API
         v                              v                             v
+--------+----------+       +-----------+-----------+       +---------+---------+
|                   |       |                       |       |                   |
| Global IPv4 /     |       |   TLS/HTTP/SSH/FTP    |       | Security Analyst  |
| IPv6 Space        |       |   Handshakes & Certs  |       | (Query via UI/CLI)|
|                   |       |                       |       |                   |
+-------------------+       +-----------------------+       +-------------------+
```

- **ZMap**: A fast, single-packet network scanner capable of surveying the entire IPv4 address space in under 45 minutes. It performs the initial port discovery.
- **ZGrab2**: An application-layer scanner written in Go. Once ZMap finds an open port, ZGrab2 performs the deep handshake (e.g., TLS negotiation) to pull down certificates, HTTP headers, and protocol-specific metadata.

## 3. Search Language and Syntax

Censys utilizes a highly structured, strongly typed query language. Understanding the field structure is essential. The search syntax supports boolean logic (`AND`, `OR`, `NOT`), wildcards, and regular expressions.

### Host Search Syntax
The Hosts dataset contains information about IPs and their running services.

- **Basic IP Search**: `ip: 8.8.8.8`
- **Searching by Port**: `services.port: 22`
- **Searching by Service Name**: `services.service_name: SSH`
- **Autonomous System**: `autonomous_system.asn: 15169`
- **Operating System**: `operating_system.product: "Windows"`
- **Software Specifics**: `services.software.product: "nginx" AND services.software.version: "1.14.0"`
- **Geolocation**: `location.country: "DE" AND location.city: "Berlin"`

### Certificate Search Syntax
The Certificates dataset is Censys's strongest asset. It parses every field of an X.509 certificate.

- **Common Name (CN)**: `parsed.subject.common_name: "example.com"`
- **Subject Alternative Names (SAN)**: `parsed.extensions.subject_alt_name.dns_names: "dev.example.com"`
- **Issuer**: `parsed.issuer.organization: "Let's Encrypt"`
- **Certificate Validity**: `parsed.validity.end: [2024-01-01 TO *]`
- **Certificate Fingerprint**: `parsed.fingerprint_sha256: "a1b2c3d4..."`

## 4. Advanced Pivoting Techniques

Censys is highly effective for "pivoting" to uncover hidden infrastructure, especially finding the origin IP of a server hidden behind a WAF or CDN like Cloudflare.

### The Origin IP Uncovering Technique
1. **Identify the Target**: A target uses Cloudflare. Ping resolves to Cloudflare IPs.
2. **Find the Certificate**: Search the Censys Certificates dataset for the target domain: `parsed.names: "target.com"`.
3. **Extract Fingerprint**: Obtain the SHA-256 fingerprint of the valid certificate used by the target.
4. **Pivot to Hosts**: Switch to the Censys Hosts search. Query the hosts database for any IP presenting that specific certificate fingerprint: 
   `services.tls.certificates.leaf_data.fingerprint_sha256: "the_extracted_fingerprint"`
5. **Result**: The search returns the direct, unproxied IP address of the backend server, entirely bypassing the WAF.

## 5. Censys CLI and Automation

The `censys-python` library provides both a programmatic API wrapper and a powerful command-line interface.

### Installation
```bash
pip install censys
censys config
# Enter your API ID and API Secret when prompted
```

### CLI Usage
Search for hosts running vulnerable instances of Confluence:
```bash
censys search "services.http.response.headers.X-Confluence-Version: *" --index-type hosts --pages 2
```

View detailed information for a specific IP:
```bash
censys view 1.1.1.1
```

## 6. Programmatic Access with Python

Automating Censys queries is crucial for continuous monitoring or bulk analysis. The V2 API handles pagination automatically via iterators.

### Example: Bulk Extracting Domains from an ASN
This script queries an organization's ASN and extracts all unique subject alternative names (SANs) from the TLS certificates presented by those hosts.

```python
import os
from censys.search import CensysHosts

def extract_domains_from_asn(asn):
    # Initialize the client. Requires CENSYS_API_ID and CENSYS_API_SECRET env vars.
    h = CensysHosts()
    
    query = f"autonomous_system.asn: {asn} AND services.service_name: HTTP"
    print(f"[*] Querying Censys for ASN: {asn}...")
    
    try:
        # Search returns an iterator over all results
        results = h.search(query, per_page=100, pages=5) # Limit to 5 pages for testing
        
        unique_domains = set()
        
        for host in results:
            ip = host.get("ip")
            services = host.get("services", [])
            
            for service in services:
                # Check if TLS data exists
                tls = service.get("tls", {})
                if tls:
                    cert = tls.get("certificate", {}).get("parsed", {})
                    # Extract SANs
                    sans = cert.get("extensions", {}).get("subject_alt_name", {}).get("dns_names", [])
                    for domain in sans:
                        unique_domains.add(domain)
                        
        print(f"[+] Found {len(unique_domains)} unique domains.")
        for d in sorted(list(unique_domains)):
            print(f"  - {d}")
            
    except Exception as e:
        print(f"[-] Error querying API: {e}")

if __name__ == "__main__":
    # Example: AS15169 (Google)
    extract_domains_from_asn("15169")
```

## 7. Threat Hunting with Censys

Censys is frequently used by Threat Intelligence teams to find Command and Control (C2) infrastructure proactively.

### Finding Cobalt Strike Servers
Cobalt Strike servers often use default configurations that generate identifiable HTTP headers, TLS certificates, or JARM signatures.
- **JARM Fingerprinting**: JARM is an active TLS server fingerprinting tool. Censys indexes JARM hashes.
  `services.jarm.fingerprint: "07d14d16d21d21d07c42d41d000000..."`
- **Default Certificates**: Searching for the default Cobalt Strike certificate.
  `parsed.issuer.organization: "cobaltstrike" AND parsed.subject.organization: "cobaltstrike"`

### Identifying Phishing Infrastructure
Attackers frequently register domains that closely resemble legitimate domains (typosquatting) and provision Let's Encrypt certificates.
- Search Certificates: `parsed.names: /.*paypal.*/ AND parsed.issuer.organization: "Let's Encrypt"`
By continuously monitoring the CT logs via Censys, defenders can identify phishing sites the moment a certificate is issued, often before the campaign even launches.

## 8. Censys Enterprise / Attack Surface Management (ASM)

Censys offers an enterprise ASM product built on top of their dataset. ASM automates the process of mapping an organization's digital footprint.
- **Seed Discovery**: Starts with a known domain or CIDR block.
- **Continuous Discovery**: Automatically finds related infrastructure via WHOIS, DNS, and CT logs.
- **Risk Assessment**: Flags misconfigurations (e.g., exposed RDP, expired certificates, unpatched software) continuously.
While costly, the underlying methodology of the ASM platform can be replicated manually using the free/community API tiers and custom scripting.

## 9. OPSEC and Limitations

- **Search Visibility**: Unlike Shodan, which provides raw banners, Censys structures everything into JSON. If a service returns a non-standard protocol or malformed HTTP header, Censys might discard or fail to parse it, missing edge cases.
- **Rate Limits**: The free tier of the Censys API is heavily rate-limited (typically 250 queries/month). Extensive scripting requires careful token management or a commercial license.
- **Cloud Ephemerality**: Cloud providers (AWS, Azure) rotate IPs constantly. A Censys record from two weeks ago for an EC2 instance might now belong to a completely different company. Always verify findings live before launching attacks.

## 10. Querying Censys via BigQuery
For enterprise users, Censys provides direct access to its dataset via Google BigQuery. This allows for complex SQL queries across the entire internet, which is impossible via the standard search API.

### Example: Finding Expiring Certs on specific ASNs
```sql
SELECT
  parsed.subject_dn,
  parsed.validity.end
FROM
  `censys-io.certificates.certificates`
WHERE
  REGEXP_CONTAINS(parsed.subject_dn, r'O=MyCorp')
  AND parsed.validity.end < CURRENT_TIMESTAMP()
LIMIT 100
```
BigQuery integration is ideal for continuous monitoring dashboards, combining Censys data with internal SIEM logs to identify externally facing assets that fall out of compliance.

## 11. Chaining Opportunities

- **Amass**: Integrate Censys API keys into OWASP Amass config files. Amass will use Censys CT logs to dramatically improve subdomain enumeration. See [[01 - Amass Comprehensive Subdomain Enumeration]].
- **Nmap**: Once a block of IPs is identified via Censys, use Nmap to perform live validation of the services. See [[03 - Nmap Advanced Port Scanning]].
- **Shodan**: Cross-reference findings. An IP might have recent port data in Shodan, but rich historical certificate data in Censys. See [[07 - Shodan Web and CLI Complete Guide]].

## 11. Related Notes
- [[02 - OSINT Methodology and Frameworks]]
- [[07 - Shodan Web and CLI Complete Guide]]
- [[09 - FOFA Chinese IoT Search Engine]]
- [[12 - Open Source Threat Intelligence]]
