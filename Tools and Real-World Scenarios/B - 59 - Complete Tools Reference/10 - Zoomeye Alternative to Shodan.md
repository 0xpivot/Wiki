---
tags: [tools, recon, osint, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.10 Zoomeye Alternative to Shodan"
---

# Zoomeye Alternative to Shodan

## 1. Introduction to ZoomEye

ZoomEye, developed by the Chinese cybersecurity firm Knownsec, brands itself as a "Cyber Space Search Engine." It is one of the "Big Four" global asset search engines alongside Shodan, Censys, and FOFA. ZoomEye specializes in continuously mapping and cataloging devices, websites, and services connected to the global internet.

ZoomEye is particularly valued by VAPT professionals for its deep integration into vulnerability research frameworks (like Metasploit) and its distinct scanning engines. It maintains an extensive repository of historical data, allowing analysts to track the evolution of a target's infrastructure over several years.

## 2. ZoomEye Components: Xmap and Wmap

ZoomEye utilizes two distinct, proprietary scanning engines to build its database.

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
| Xmap / Wmap       |------>| ZoomEye Core Engine   |------>| ZoomEye Dashboard |
| (Port/Web Scanners|       | (Knownsec Data Pool)  |       | (Visual Search)   |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +-------------------+
         |                              |                             ^
         | Fingerprinting               | API/Dorking                 |
         v                              v                             |
+--------+----------+       +-----------+-----------+                 |
|                   |       |                       |                 |
| Unknown Assets    |       |    ZoomEye Tools      |-----------------+
| Vulnerable Hosts  |       |    (Metasploit/CLI)   |
|                   |       |                       |
+-------------------+       +-----------------------+
```

1. **Xmap**: The global IPv4 port scanning engine. Xmap is responsible for discovering live hosts, identifying open ports, grabbing banners, and determining running services and operating systems based on protocol fingerprints.
2. **Wmap**: The web application scanning engine. Wmap crawls discovered HTTP/HTTPS services to extract deeper metadata, such as CMS versions, HTTP headers, javascript libraries, backend frameworks, and geolocation mapping.

## 3. ZoomEye Search Syntax

ZoomEye divides its search functionality into two distinct tabs/modes: **Host Search** (IP/Port focus) and **Web Search** (Domain/URL focus).

### Host Search Dorks
- `app:"application_name"`: Search for a specific application. (e.g., `app:"Apache httpd"`).
- `ver:"version"`: Specify the version of the application. (e.g., `app:"ProFTPD" ver:"1.3.5"`).
- `os:"operating_system"`: Filter by OS. (e.g., `os:"Linux"` or `os:"Windows"`).
- `port:"port_number"`: Filter by open port. (e.g., `port:21`).
- `service:"service_name"`: Filter by protocol service. (e.g., `service:"ssh"`).
- `cidr:"IP/mask"`: Search within a specific network block. (e.g., `cidr:192.168.1.0/24`).
- `country:"country_code"`: Geolocation filtering. (e.g., `country:"JP"`).
- `device:"device_type"`: Search for device classifications. (e.g., `device:"router"` or `device:"webcam"`).

### Web Search Dorks
- `site:"domain"`: Search for subdomains and pages associated with a domain. (e.g., `site:"example.com"`).
- `title:"page_title"`: Search the HTML title tag. (e.g., `title:"Welcome to IIS"`).
- `header:"header_content"`: Search within HTTP headers. (e.g., `header:"X-Pingback"`).
- `keywords:"keyword"`: Search for specific keywords extracted by Wmap's crawler.

## 4. Historical Data and Analytics

One of ZoomEye's most powerful features for red teamers is its **Historical Data** capability. 
When viewing an IP address, ZoomEye allows you to view the "timeline" of that asset. You can see what ports were open in 2018 versus today. 

**Use Case**: An organization tightens its perimeter firewall, blocking port 3389 (RDP) globally, but allowing traffic from specific whitelisted IPs. By using ZoomEye's historical data, an attacker can determine that the RDP service *used* to be public. The attacker now knows the internal RDP service still exists and can target the VPN or spear-phish employees to gain internal access to reach it, rather than assuming the service was completely decommissioned.

## 5. ZoomEye API and Scripting

ZoomEye provides a REST API that returns data in JSON format. Users authenticate via an API key. 

### The zoomeye-python Wrapper
ZoomEye provides an official CLI and Python library, which greatly simplifies interaction.

**Installation**:
```bash
pip install zoomeye
```

**CLI Configuration**:
```bash
zoomeye init -apikey "YOUR_API_KEY_HERE"
```

**CLI Usage**:
Search for webcams in a specific country and download the results:
```bash
zoomeye search "device:webcam country:BR" -num 100 -type host
```

### Custom Python Integration
For deep automation, integrating the library directly into custom python scripts allows for dynamic asset discovery during a pentest.

```python
import zoomeye.sdk as ze
import sys

API_KEY = "your_api_key_here"

def search_vulnerable_routers():
    # Initialize the ZoomEye SDK
    zm = ze.ZoomEye(api_key=API_KEY)
    
    # Query: Looking for older Cisco routers
    query = 'app:"Cisco IOS http config" country:"US"'
    
    try:
        # Perform a host search
        print(f"[*] Executing ZoomEye query: {query}")
        # Fetching page 1
        data = zm.dork_search(query, resource="host", page=1)
        
        if not data:
            print("[-] No results found.")
            return

        matches = data.get('matches', [])
        print(f"[+] Retrieved {len(matches)} results on page 1.")
        
        for match in matches:
            ip = match.get('ip')
            portinfo = match.get('portinfo', {})
            port = portinfo.get('port')
            service = portinfo.get('service')
            os = portinfo.get('os', 'Unknown')
            
            print(f"Target: {ip}:{port} | Service: {service} | OS: {os}")
            
    except Exception as e:
        print(f"[-] ZoomEye API Error: {e}")

if __name__ == "__main__":
    search_vulnerable_routers()
```

## 6. Integration with Penetration Testing Frameworks

ZoomEye has prioritized integration with offensive security tools. 

### Metasploit Integration
Metasploit contains auxiliary modules specifically designed to query ZoomEye. This allows attackers to seamlessly move from reconnaissance to exploitation within the same console.

1. **Load Metasploit and search for the module:**
   ```bash
   msfconsole
   msf6 > search zoomeye
   ```
2. **Use the module:**
   ```bash
   msf6 > use auxiliary/gather/zoomeye_search
   ```
3. **Configure and Run:**
   ```bash
   msf6 auxiliary(gather/zoomeye_search) > set ZOOMEYE_APIKEY your_api_key
   msf6 auxiliary(gather/zoomeye_search) > set ZOOMEYE_DORK "app:Weblogic ver:10.3.6.0"
   msf6 auxiliary(gather/zoomeye_search) > run
   ```
The results are automatically saved to the Metasploit database (`hosts` and `services`), allowing the user to immediately pivot to `exploit/multi/misc/weblogic_deserialize`.

## 7. Limitations and OPSEC

- **Quota Restrictions**: ZoomEye operates on a strict quota system. Free accounts receive a limited number of search credits per month. Complex queries or bulk downloads will exhaust these credits rapidly.
- **Data Freshness**: Depending on the obscurity of the IP address, the last scanned date might be months old. Always validate the existence of a vulnerability or open port using an active tool like Nmap or Netcat before including it in a report or attempting exploitation.
- **Geographic Bias**: While ZoomEye is a global scanner, its placement of scanning nodes and organizational focus results in exceptionally high fidelity for Asian infrastructure (China, Japan, South Korea), sometimes outperforming Shodan in these specific regions.

## 8. Advanced ZoomEye Data Parsing
When downloading bulk data from ZoomEye via the CLI or API, parsing the resulting JSON efficiently is paramount. The raw JSON contains significant metadata beyond just the IP and port, including geographic coordinates, banner hashes, and ASN details.

### Using jq for Rapid Parsing
Instead of writing custom python scripts for every query, you can use the command-line tool `jq` to parse ZoomEye's JSON output directly.

**Extracting Unique IP Addresses**:
```bash
cat zoomeye_results.json | jq -r '.matches[].ip' | sort -u > ips.txt
```

**Extracting IP:Port Combinations**:
```bash
cat zoomeye_results.json | jq -r '.matches[] | "\(.ip):\(.portinfo.port)"' > targets.txt
```

**Extracting Banners for Offline Analysis**:
```bash
cat zoomeye_results.json | jq -r '.matches[] | "\(.ip) -> \(.portinfo.banner)"' > banners.txt
```

### Correlating Data Sources
Because ZoomEye has high fidelity in Asia, it is highly recommended to run identical queries across ZoomEye, FOFA, and Shodan, then merge and deduplicate the results. This multi-engine approach ensures maximum coverage of the target's attack surface, accounting for the blind spots of any single scanning network.

## 9. Chaining Opportunities

- **Metasploit Framework**: Native integration allows direct population of the MSF database from ZoomEye queries, bridging the gap between OSINT and active exploitation. See [[20 - Metasploit Framework Fundamentals]].
- **Nmap**: Export IP addresses discovered via ZoomEye and run aggressive Nmap scripts (`--script vuln`) to verify the findings. See [[03 - Nmap Advanced Port Scanning]].
- **Maltego**: Similar to Shodan, ZoomEye data can be integrated into Maltego via custom local transforms to visually map target infrastructure. See [[06 - Maltego Visual OSINT and Link Analysis]].

## 9. Related Notes
- [[02 - OSINT Methodology and Frameworks]]
- [[07 - Shodan Web and CLI Complete Guide]]
- [[08 - Censys Search Syntax and API]]
- [[09 - FOFA Chinese IoT Search Engine]]

