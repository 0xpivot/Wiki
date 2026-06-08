---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.04 Shodan — IoT and Exposed Services"
---

# 05.04 — Shodan

## What is it?

Shodan is a search engine for internet-connected devices. Unlike Google which indexes web pages, Shodan scans the entire internet and indexes service banners, open ports, SSL certificates, and other metadata from every reachable IP. It reveals exposed databases, cameras, industrial control systems, admin panels, and services that shouldn't be public.

---

## How Shodan Works

```
SHODAN CRAWLS:
  Continuously scans entire IPv4 space (4 billion addresses)
  Probes common ports: 21, 22, 23, 25, 80, 443, 8080, 3306, etc.
  Captures: banner responses, SSL certs, HTTP headers, protocol info

WHAT SHODAN STORES:
  - IP address and location
  - Open ports and protocols
  - Service banners (version info!)
  - SSL certificate details (subdomains via SANs!)
  - HTTP headers (server, X-Powered-By)
  - Organization and ISP
  - Hostnames (via reverse DNS and SSL)
  - Screenshot of web pages (Shodan Images)
```

---

## Shodan Search Operators

```
hostname:target.com           → all records for this hostname
ip:203.0.113.1               → specific IP
net:192.168.0.0/24           → CIDR range
org:"Target Company"         → by organization name
ssl.cert.subject.CN:*.target.com  → SSL certs for domain (find subdomains!)
product:"Apache httpd"       → by service product
version:"2.4.49"             → specific version
os:"Windows"                 → by operating system
country:IN                   → by country code (IN = India)
city:"New York"              → by city
port:3306                    → MySQL on port 3306
port:27017                   → MongoDB
port:9200                    → Elasticsearch
port:6379                    → Redis
port:5432                    → PostgreSQL
has_screenshot:true          → has visual screenshot
vuln:CVE-2021-44228          → vulnerable to Log4Shell!
```

---

## Shodan CLI

```bash
# Install:
pip install shodan

# Initialize with API key:
shodan init YOUR_API_KEY

# Search by domain:
shodan search "hostname:target.com"
shodan search --fields ip_str,port,org,hostnames "hostname:target.com"

# Get specific host info:
shodan host 203.0.113.1
shodan host 203.0.113.1 --history  # past scan history!

# Download results:
shodan download --limit 1000 results "hostname:target.com"
shodan parse results.json.gz --fields ip_str,port,hostnames

# Alert: notify when new hosts for your domain appear:
shodan alert create "target" net:203.0.113.0/24
shodan alert list

# STATS (good for overview):
shodan stats --facets port "hostname:target.com"
shodan stats --facets org "net:203.0.113.0/24"
```

---

## High-Value Shodan Searches

```
EXPOSED DATABASES:
  port:3306 hostname:target.com     → MySQL
  port:27017 hostname:target.com    → MongoDB (often no auth!)
  port:9200 hostname:target.com     → Elasticsearch
  port:6379 hostname:target.com     → Redis (often no auth!)
  port:5432 hostname:target.com     → PostgreSQL
  port:1433 hostname:target.com     → MSSQL

EXPOSED ADMIN PANELS:
  "Jenkins" hostname:target.com
  "Kibana" hostname:target.com
  "Grafana" hostname:target.com
  "phpMyAdmin" hostname:target.com
  "Kubernetes Dashboard" hostname:target.com

EXPOSED INFRASTRUCTURE:
  "SSH" hostname:target.com port:22
  "RDP" hostname:target.com port:3389
  "VNC" hostname:target.com port:5900
  "Telnet" hostname:target.com port:23

FIND SUBDOMAIN VIA SSL CERTS:
  ssl.cert.subject.CN:target.com
  ssl:"target.com"
  ssl.cert.subject.CN:"*.target.com"

FIND BY VULNERABILITY:
  vuln:CVE-2021-44228             → Log4Shell vulnerable hosts
  vuln:CVE-2021-41773             → Apache path traversal
  vuln:CVE-2019-0708              → BlueKeep (RDP RCE)
```

---

## Real Attack Scenarios

```
SCENARIO 1: Exposed MongoDB
  shodan search "port:27017 hostname:target.com"
  → Finds open MongoDB on cloud host
  
  mongo <target-ip>:27017
  > show dbs
  > use customer_data
  > db.users.find().limit(5)
  → Customer database accessible without auth!

SCENARIO 2: Find Origin IP Behind Cloudflare
  target.com → Cloudflare (protected)
  
  shodan search "ssl.cert.subject.CN:target.com -has_screenshot:false"
  → Finds real origin server (same SSL cert, different IP!)
  → Bypass Cloudflare: curl -H "Host: target.com" http://ORIGIN-IP/

SCENARIO 3: Old Exposed Development Server
  shodan search "org:Target Company" "HTTP/1.1 200 OK"
  → Find forgotten dev server: dev.target.com or 203.0.113.5
  → Dev server often has weaker security!

SCENARIO 4: Find All IPs for Organization
  shodan search "org:Target Corp" --fields ip_str,port,hostnames
  → Complete infrastructure map!
```

---

## Shodan Alternatives

```
CENSYS (censys.io):
  More focused on certificates and infrastructure
  Better for academic/research use
  Free tier available

FOFA (fofa.info):
  Chinese alternative, broader coverage of Asia
  Good for finding IoT and industrial systems

ZOOMEYE (zoomeye.org):
  Chinese alternative to Shodan

GREYNOISE (greynoise.io):
  Shows what IPs are scanning the internet (noise vs signal)
  Good for blocking scanner IPs

BINARYEDGE (binaryedge.io):
  Similar to Shodan, different coverage

ONYPHE (onyphe.io):
  French alternative, includes dark web data
```

---

## Related Notes
- [[03 - Google Dorking]] — web-content search
- [[05 - Censys]] — certificate-focused alternative
- [[26 - CDN Detection and Origin IP Discovery]] — using Shodan for CDN bypass
- [[21 - Port Scanning with Nmap]] — active scanning vs passive Shodan
