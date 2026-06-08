---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.05 Censys — Certificate and Host Enumeration"
---

# 05.05 — Censys

## What is it?

Censys is an internet-wide scanner focused on hosts, certificates, and network infrastructure. Its strength is deep certificate transparency integration — making it excellent for subdomain discovery, certificate inventory, and infrastructure mapping. The free tier is useful; the API allows automation.

---

## Censys vs Shodan

```
CENSYS:                          SHODAN:
  ✓ Deep certificate analysis      ✓ Broader port/service coverage
  ✓ Better cert data               ✓ More vulnerability data
  ✓ Historical cert data           ✓ IoT and industrial device coverage
  ✓ Better API for bulk lookups    ✓ More third-party integrations
  
  USE CENSYS FOR:                  USE SHODAN FOR:
  - Certificate inventory          - Port/service discovery
  - Subdomain via SSL              - Vulnerability scanning
  - Infrastructure audit           - IoT research
  - TLS configuration analysis     - Exposed databases
```

---

## Censys Web Interface

```
SEARCH AT: censys.io/search

QUERY SYNTAX:
  services.tls.certificates.leaf_data.subject.common_name:target.com
  → Find all certs issued for target.com
  
  services.tls.certificates.leaf_data.subject.common_name:*.target.com
  → Wildcard certs for target.com
  
  services.tls.certificates.leaf_data.names:target.com
  → Certificates including target.com as SAN
  
  ip:203.0.113.1
  → Information on specific IP
  
  autonomous_system.name:"Target Corp"
  → All IPs owned by organization
  
  services.port:3306
  → All IPs with MySQL exposed
  
  services.software.product:"Apache httpd" and services.software.version:"2.4.49"
  → Specific vulnerable version!
```

---

## Censys CLI

```bash
# Install:
pip install censys

# Configure (get API from censys.io):
censys config

# Search hosts:
censys search "services.tls.certificates.leaf_data.subject.common_name:target.com" \
  --index-type hosts

# Get host details:
censys view 203.0.113.1 --index-type hosts

# Search certificates:
censys search "parsed.names: target.com" --index-type certificates

# Export results:
censys search "services.port:3306" --index-type hosts \
  --fields ip,services.port,autonomous_system.name \
  -o results.json
```

---

## Certificate Hunting for Subdomains

```bash
# Find all certificates mentioning target.com:
censys search "parsed.names: target.com" --index-type certificates \
  --fields parsed.names,parsed.subject.common_name,parsed.validity.start

# Python script for bulk lookup:
from censys.search import CensysCertificates
c = CensysCertificates(api_id="ID", api_secret="SECRET")
for cert in c.search("parsed.names: target.com", 
                      fields=["parsed.names"]):
    for name in cert.get("parsed.names", []):
        print(name)

# Alternative: crt.sh for same data (free, no API key):
curl "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "import json,sys; [print(x['name_value']) for x in json.load(sys.stdin)]" | \
  sort -u
```

---

## Infrastructure Analysis

```bash
# Find all IPs for an organization (ASN):
# First find ASN: https://bgp.he.net/ or whois target.com

censys search "autonomous_system.asn:XXXXX" --index-type hosts \
  --fields ip,services.port,services.service_name

# Find TLS misconfigurations:
censys search "autonomous_system.name:'Target Corp' and \
  services.tls.certificates.leaf_data.subject.common_name:target.com" \
  --fields ip,services.port,services.tls.version

# Find expired certificates (sign of unmaintained systems!):
censys search "parsed.subject.common_name:target.com and \
  parsed.validity.end:[* TO 2024-01-01]" \
  --index-type certificates

# Find weak TLS configs:
censys search "services.tls.version_selected: TLSv1 and \
  autonomous_system.name:'Target Corp'"
```

---

## Integration with Bug Bounty Workflow

```bash
# Combined subdomain discovery approach:
# Step 1: crt.sh for CT logs
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "import json,sys; [print(x['name_value']) for x in json.load(sys.stdin)]" | \
  sort -u > subs_crt.txt

# Step 2: Censys certificate search
censys search "parsed.names: target.com" --index-type certificates \
  --fields parsed.names | jq -r '.[].parsed.names[]' | sort -u > subs_censys.txt

# Step 3: Combine and deduplicate
cat subs_crt.txt subs_censys.txt | sort -u > all_subdomains.txt

# Step 4: Verify which ones are live
cat all_subdomains.txt | httpx -status-code -title > live_subdomains.txt
```

---

## Related Notes
- [[04 - Shodan]] — service-focused alternative
- [[09 - Certificate Transparency Logs]] — crt.sh workflow
- [[08 - Subdomain Enumeration]] — complete subdomain discovery
- [[27 - ASN and IP Range Discovery]] — organization IP mapping
