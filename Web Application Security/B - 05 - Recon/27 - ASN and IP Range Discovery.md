---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.27 ASN and IP Range Discovery"
---

# 05.27 — ASN and IP Range Discovery

## What is an ASN?

An Autonomous System Number (ASN) is a unique identifier assigned to a collection of IP networks managed by a single organization. Large companies own entire ASNs — meaning all their IP ranges (including cloud infrastructure, data centers, offices) are linked to one ASN.

```
EXAMPLE:
  ASN15169 → Google LLC → 8.8.8.8, 8.8.4.4, 142.250.x.x, etc.
  ASN16509 → Amazon.com → 54.x.x.x, 52.x.x.x, etc.
  ASN13335 → Cloudflare → 104.16.x.x, 172.64.x.x, etc.

WHY CARE IN VAPT:
  Target company has ASN → all IPs they own in that ASN
  → Discover IPs not in scope at first glance but still owned by target
  → Find direct-connect servers bypassing CDN/WAF
  → Find exposed staging/dev/internal systems
  → Complete picture of internet-facing infrastructure
```

---

## Finding the Target's ASN

```bash
# METHOD 1: WHOIS ON TARGET DOMAIN'S IP:
dig +short target.com | head -1 → get IP
whois IP_ADDRESS | grep -E "ASN|OriginAS|origin"

# METHOD 2: BGP TOOLKIT (best):
curl -s "https://api.bgpview.io/ip/203.0.113.1" | python3 -m json.tool | grep -A5 "asn"
# Returns: ASN, prefix, description

# METHOD 3: ASNLOOKUP TOOLS:
# Online: https://bgp.he.net  (Hurricane Electric BGP Toolkit)
# Online: https://bgpview.io
# Online: https://asrank.caida.org

# METHOD 4: WHOIS DIRECTLY:
whois -h whois.radb.net 203.0.113.1
whois -h whois.arin.net 203.0.113.1   # Americas
whois -h whois.ripe.net 203.0.113.1   # Europe
whois -h whois.apnic.net 203.0.113.1  # Asia Pacific

# METHOD 5: NMAP:
nmap --script=asn-query target.com

# METHOD 6: SEARCH BY COMPANY NAME:
curl -s "https://api.bgpview.io/search?query_term=target+company" | \
  python3 -m json.tool | grep -E "asn|name|description"
```

---

## Enumerating IP Ranges from ASN

```bash
# GET ALL IP RANGES FOR AN ASN:
# BGPView API:
ASN=12345
curl -s "https://api.bgpview.io/asn/$ASN/prefixes" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for prefix in data['data']['ipv4_prefixes']:
    print(prefix['prefix'], '-', prefix.get('description', ''))
"

# WHOIS:
whois -h whois.radb.net -- '-i origin AS12345'
# Returns all prefixes announced by this ASN

# RIPE DB (European IPs):
curl -s "https://rest.db.ripe.net/search?query-string=AS12345&type-filter=route" | \
  python3 -m json.tool | grep "route"

# ARIN (American IPs):
curl -s "https://whois.arin.net/rest/asn/AS12345/nets" \
  -H "Accept: application/json" | python3 -m json.tool

# AMASS (automated ASN + prefix discovery):
amass intel -asn 12345
amass intel -org "Target Company"  # search by org name!
```

---

## Scanning ASN IP Ranges

Once you have the IP ranges, scan them to find all internet-facing systems.

```bash
# MASSCAN ON ENTIRE RANGE:
masscan 203.0.113.0/24 -p80,443,8080,8443 --rate=10000

# NMAP ON SMALLER RANGES:
nmap -sV -p80,443,8080,8443 203.0.113.0/24 --open

# HTTPX TO FIND WEB SERVICES:
# First: generate IP list
python3 -c "
import ipaddress
for ip in ipaddress.IPv4Network('203.0.113.0/24'):
    print(str(ip))
" | httpx -p 80,443,8080,8443 -title -status-code -web-server -o httpx-asn.txt

# DNSX REVERSE LOOKUP (IP → hostname):
cat ip-list.txt | dnsx -ptr -resp-only
# Many IPs will have PTR records → reveals service names!
# e.g.: 203.0.113.1 → prod-db-01.internal.target.com → database server!

# SHODAN ON ASN:
shodan search "asn:AS12345" --limit 1000
shodan search "asn:AS12345 port:22 product:OpenSSH"
shodan search "asn:AS12345 http.title:admin"

# CENSYS ON ASN:
censys search "autonomous_system.asn:12345" --index ipv4
```

---

## BGP Toolkit (Hurricane Electric)

```bash
# BEST FREE TOOL: bgp.he.net
# Enter: target IP or domain → see full BGP info

# CLI EQUIVALENT:
# HE BGP WHOIS:
whois -h bgp.he.net target.com

# RETURNS:
# ASN: AS12345
# Net Name: TARGET-US
# Organization: Target Corp
# CIDR: 203.0.113.0/24
# Route: 203.0.113.0/24
# Origin: AS12345
```

---

## Reverse WHOIS (Find All Domains on Same IP Range)

```bash
# FIND ALL DOMAINS REGISTERED TO SAME ORG:
# ViewDNS Reverse WHOIS:
curl -s "https://viewdns.info/reversewhois/?q=target+company"

# DomainTools (commercial):
# Search by registrant name, email, or organization

# SHODAN REVERSE:
# Get all hostnames pointing to IPs in range:
shodan search "net:203.0.113.0/24" --fields ip_str,hostnames,org

# FIND SISTER COMPANIES / ACQUISITIONS ON SAME ASN:
curl -s "https://api.bgpview.io/asn/AS12345" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Name:', data['data']['name'])
print('Description:', data['data']['description'])
print('Country:', data['data']['country_code'])
"
```

---

## Cloud Provider IP Range Detection

Determine if a target IP belongs to a cloud provider's range:

```bash
# AWS IP RANGES (updated regularly):
curl -s "https://ip-ranges.amazonaws.com/ip-ranges.json" | \
  python3 -c "
import json, sys, ipaddress
data = json.load(sys.stdin)
target = ipaddress.ip_address('203.0.113.1')
for prefix in data['prefixes']:
    if target in ipaddress.IPv4Network(prefix['ip_prefix']):
        print('AWS Region:', prefix['region'])
        print('Service:', prefix['service'])
        break
"

# AZURE IP RANGES:
# Download from Microsoft: https://www.microsoft.com/en-us/download/details.aspx?id=56519

# GCP IP RANGES:
curl -s "https://www.gstatic.com/ipranges/cloud.json" | \
  python3 -c "
import json, sys, ipaddress
data = json.load(sys.stdin)
target = ipaddress.ip_address('203.0.113.1')
for prefix in data.get('prefixes', []):
    cidr = prefix.get('ipv4Prefix')
    if cidr and target in ipaddress.IPv4Network(cidr):
        print('GCP Region:', prefix.get('scope'))
        break
"

# SIMPLE CHECK WITH IPINFO:
curl -s "https://ipinfo.io/203.0.113.1" | python3 -m json.tool
# Returns: org, country, region, city, ASN
```

---

## Tools Summary

```bash
# FULL WORKFLOW:
# 1. Find target's IP:
dig +short target.com

# 2. Get ASN:
curl -s "https://api.bgpview.io/ip/$(dig +short target.com)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['asns'])"

# 3. Get all prefixes for ASN:
curl -s "https://api.bgpview.io/asn/AS12345/prefixes" | \
  python3 -c "import json,sys; [print(p['prefix']) for p in json.load(sys.stdin)['data']['ipv4_prefixes']]"

# 4. Scan with masscan:
masscan -iL prefixes.txt -p80,443,8080,8443,22,21,3306,6379,27017 --rate=5000 -oL masscan.txt

# 5. Discover web services:
grep "open" masscan.txt | awk '{print $4":"$3}' | \
  httpx -title -status-code -web-server -o web-services.txt

# AMASS INTEL MODE (combines all of the above):
amass intel -d target.com -whois -asn
```

---

## Related Notes
- [[06 - WHOIS and Domain Lookup]] — WHOIS fundamentals
- [[08 - Subdomain Enumeration]] — mapping all subdomains
- [[26 - CDN Detection and Origin IP Discovery]] — finding origin IPs
- [[21 - Port Scanning with Nmap]] — scanning discovered IP ranges
