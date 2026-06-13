---
tags: [tools, recon, osint, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.09 FOFA Chinese IoT Search Engine"
---

# FOFA Chinese IoT Search Engine

## 1. Introduction to FOFA

FOFA (Cyberspace Mapping) is an internet-connected asset search engine developed by the Chinese security company NOSEC. While it operates similarly to Shodan and Censys, FOFA distinguishes itself through its massive database of Asian IP space, deep profiling of custom web applications, unique protocol parsing, and extensive coverage of Internet of Things (IoT) devices like webcams, routers, and industrial controllers.

For penetration testers and bug bounty hunters, FOFA is a goldmine. Because it utilizes different scanning nodes and custom fingerprinting algorithms compared to its Western counterparts, querying FOFA often reveals assets that Shodan and Censys missed.

## 2. Architecture and Scanning Mechanisms

FOFA's architecture is optimized for web application fingerprinting. It relies heavily on extracting specific features from HTTP/HTTPS responses to identify the underlying software stack.

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
| FOFA Mapping Node |------>|     FOFA Datacenter   |------>|   FOFA Web App    |
| (Global Crawlers) |       |     (Data Aggregation)|       |   (Search Engine) |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +-------------------+
         |                              |                             ^
         | HTTP/IoT probing             | API Requests                |
         v                              v                             |
+--------+----------+       +-----------+-----------+                 |
|                   |       |                       |                 |
|  IoT Devices /    |       |    Fofax CLI Tool     |-----------------+
|  Asian ASNs       |       |    (Automation)       |
|                   |       |                       |
+-------------------+       +-----------------------+
```

FOFA crawlers aggressively pull down website source code, parse javascript files, extract meta tags, and compute hashes of static assets. This makes FOFA exceptionally strong at identifying specific CMS versions, e-commerce platforms, and administrative panels.

## 3. FOFA Search Syntax and Dorks

FOFA's query syntax uses key-value pairs combined with logical operators (`&&`, `||`, `==`, `!=`).

### Essential Query Fields
- `domain="example.com"`: Search for all subdomains and hosts associated with the root domain.
- `ip="192.168.1.1"`: Search for a specific IP or CIDR block.
- `port="3389"`: Filter by open port.
- `app="Weblogic"`: Search by recognized application fingerprint. FOFA maintains thousands of signatures for commercial and open-source applications.
- `os="windows"`: Filter by underlying operating system.
- `country="CN"`: Filter by country code.

### Advanced Web Fingerprinting
These filters are where FOFA truly outshines other engines:
- `body="admin login"`: Searches the raw HTML body of the response for the exact string. Highly effective for finding generic or custom login panels.
- `header="X-Powered-By: PHP"`: Searches within HTTP response headers.
- `title="phpMyAdmin"`: Searches the HTML `<title>` tag.
- `icon_hash="-247388890"`: Searches by the MurmurHash3 of the favicon. Equivalent to Shodan's `http.favicon.hash`.
- `cert="example.com"`: Searches SSL/TLS certificates.
- `fid="xxxxxx"`: FOFA ID. FOFA aggregates multiple fingerprints into a unique identifier. Searching by FID allows you to find all assets matching a highly complex, multi-factor signature.

### ICP License Searching (China Specific)
In China, websites must register for an ICP (Internet Content Provider) license, which is displayed in the footer.
- `icp="京ICP证xxxxxx号"`: Allows mapping of entire corporate structures and subsidiaries in China based on their shared or related ICP licensing numbers.

## 4. FOFA API and Automation

FOFA offers a robust REST API. Authentication requires an email and API key. Notably, all FOFA API queries must be Base64 encoded.

### Fofax: The Ultimate CLI Tool
While you can write custom scripts, the community standard tool is `fofax`, written in Go.

**Installation**:
```bash
go install github.com/xiecat/fofax@latest
```

**Configuration**:
Set your credentials in `~/.fofax.yaml`:
```yaml
fofa_email: "your_email@example.com"
fofa_key: "your_api_key_here"
```

**Usage Examples**:
```bash
# Basic query, fetching IP and Port
fofax -q 'app="Apache-Tomcat"' -fs "ip,port"

# Query and output directly to a file for Nmap scanning
fofax -q 'domain="target.com"' -fs "ip:port" > targets.txt

# Base64 encoded query (useful if the query has complex quotes)
fofax -q 'YXBwPSJBcGFjaGUtVG9tY2F0Ig==' -base64
```

### Python API Integration
For custom logic, writing a Python wrapper is straightforward. This script queries FOFA, handles the base64 encoding, and parses the JSON response.

```python
import requests
import base64
import json
import sys

FOFA_EMAIL = "your_email@example.com"
FOFA_KEY = "your_api_key"

def query_fofa(query_string, size=100):
    # Base64 encode the query
    b64_query = base64.b64encode(query_string.encode('utf-8')).decode('utf-8')
    
    url = "https://fofa.info/api/v1/search/all"
    params = {
        "email": FOFA_EMAIL,
        "key": FOFA_KEY,
        "qbase64": b64_query,
        "size": size,
        "fields": "ip,port,host,title"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("error"):
            print(f"[-] API Error: {data.get('errmsg')}")
            return
            
        results = data.get("results", [])
        print(f"[+] Found {len(results)} results for query: {query_string}\n")
        
        for item in results:
            ip, port, host, title = item
            print(f"[{ip}:{port}] {host} - Title: {title}")
            
    except Exception as e:
        print(f"[-] Request failed: {e}")

if __name__ == "__main__":
    # Example: Hunting for exposed GitLab instances
    query = 'app="GitLab" && country="US"'
    query_fofa(query, size=10)
```

## 5. Case Studies and Threat Hunting

### Hunting for Compromised IoT Botnets
FOFA is heavily utilized by researchers tracking Mirai, Mozi, and other IoT botnets. By identifying the specific HTTP server banners of vulnerable routers (e.g., outdated MikroTik or Huawei home routers), researchers can map the potential pool of botnet recruits.
- Query: `app="MikroTik-RouterOS" && version="6.38"`

### Zero-Day Mass Exploitation Footprinting
When a new zero-day drops for an enterprise application (like Atlassian Confluence or Ivanti Connect Secure), attackers and defenders race to map the vulnerable attack surface. FOFA's rapid indexing of application specific fingerprints (`app="Ivanti-Connect-Secure"`) often provides faster visibility than Shodan.

### Malicious C2 Infrastructure
Threat actors often deploy predictable infrastructure. For instance, specific versions of XMRig web mining panels or default Deimos C2 login screens can be located by searching for their static HTML structure.
- Query: `body="Welcome to Deimos C2"` or `title="Cobalt Strike"`

## 6. Limitations and OPSEC

- **Language Barrier**: While the interface supports English, much of the community research, official documentation, and advanced dork discussions occur in Chinese forums and Telegram groups.
- **Paywalls**: FOFA's free tier is highly restrictive, heavily blurring IP addresses and limiting results. A paid API key (usually F-Coin based or subscription) is mandatory for serious professional use.
- **False Positives**: Because FOFA heavily relies on string matching in HTML bodies, it is susceptible to honeypots. A simple Apache server serving a static HTML file containing the word "Weblogic" might be misclassified as a Weblogic server. Always verify findings live.

## 7. FOFA Dork Expansion and Variations
A critical skill in utilizing FOFA is knowing how to iterate and expand on initial dorks to uncover variations of the same target.

### Bypassing WAFs with FOFA
Often, a target's primary domain is protected by Cloudflare or another WAF. By searching for the specific title, favicon hash, and an SSL certificate matching the target, you can identify the direct backend IP.
1. Primary target: `https://secure.example.com` (Cloudflare IP)
2. FOFA Search: `title="Example Secure Portal" && icon_hash="-12345678" && is_domain="false"`
3. The `is_domain="false"` filter forces FOFA to only return raw IP addresses, stripping out the CDN domains and revealing the origin server.

### Advanced Protocol Fingerprinting
FOFA excels at indexing protocols beyond HTTP. You can identify specific VPN gateways, databases, and message brokers:
- MQTT Servers: `protocol="mqtt" && port="1883"`
- Redis without Authentication: `protocol="redis" && "redis_version"` (By analyzing the banner response to an empty connection).
- Elasticsearch Clusters: `protocol="elastic" && port="9200"`

### Extracting Organization Data
By combining multiple fields, you can map out subsidiaries:
`cert.subject.org="TargetCorp" || icp="TargetCorp ICP"`

### Automating FOFA with CI/CD
Security teams often integrate `fofax` into their GitLab CI or GitHub Actions pipelines. By scheduling a daily run of `fofax -q 'domain="target.com"' -fs "ip,port"`, any new open ports are automatically committed to a monitoring repository, and Slack alerts are triggered if a high-risk port (like 3389 or 22) appears on the external perimeter. This shifts ASM (Attack Surface Management) into a GitOps workflow.

### Visualizing FOFA Data
A common practice is to export FOFA results and visualize the attack surface using tools like Gephi or Bloodhound to map the relationships between unique certificates, IP subnets, and organization names.

## 8. Chaining Opportunities

- **Nuclei**: Feed the `ip:port` output from the `fofax` CLI tool directly into Nuclei to immediately validate if the identified assets are vulnerable to known CVEs. See [[11 - Nuclei Automation and Templates]].
- **ProjectDiscovery Tools**: Use `httpx` alongside FOFA results to filter out dead hosts and capture live screenshots of the discovered web applications. See [[13 - ProjectDiscovery Ecosystem]].
- **Subfinder**: Combine Subfinder's passive DNS gathering with FOFA's domain query (`domain="target.com"`) to build a comprehensive list of a company's web assets.

## 8. Related Notes
- [[02 - OSINT Methodology and Frameworks]]
- [[07 - Shodan Web and CLI Complete Guide]]
- [[08 - Censys Search Syntax and API]]
- [[10 - Zoomeye Alternative to Shodan]]

