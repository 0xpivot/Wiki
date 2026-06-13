---
tags: [tools, recon, osint, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.06 Maltego Visual OSINT and Link Analysis"
---

# Maltego Visual OSINT and Link Analysis

## 1. Introduction and Core Concepts

Maltego is an interactive data mining tool that renders directed graphs for link analysis. The tool is used in online investigations for finding relationships between pieces of information from various sources located on the Internet. Maltego is primarily designed to perform open-source intelligence (OSINT) and visually represent the connections between different entities, including people, domains, IP addresses, autonomous systems, and affiliations. 

At its core, Maltego relies on two primary primitives:
1. **Entities**: The fundamental data points on the graph (e.g., an IPv4 address, a DNS name, a Person, an Email Address).
2. **Transforms**: Small pieces of code (run either locally or remotely) that take an entity as input, query a data source, and return connected entities as output.

Maltego is an indispensable tool in the reconnaissance and footprinting phases of a penetration test. It allows security analysts to map out the external attack surface of a target organization dynamically, pivoting from a primary domain name to subdomains, to associated IP addresses, to related Netblocks, and eventually to employees and exposed email addresses.

## 2. Architecture and Mechanics

Maltego operates on a client-server architecture, allowing it to distribute the execution of transforms across various nodes.

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Maltego Client  |------>|  Transform Dispenser  |------>| Public Transform  |
|   (Desktop GUI)   |<------|  (TAS Server)         |<------| Server (API)      |
|                   |       |                       |       |                   |
+--------+----------+       +-----------------------+       +---------+---------+
         |                                                            |
         | Local Execution                                            | External Queries
         v                                                            v
+--------+----------+                                       +---------+---------+
|                   |                                       |                   |
| Local Transforms  |                                       | Target Data /     |
| (Python/Bash)     |                                       | OSINT Sources     |
|                   |                                       |                   |
+-------------------+                                       +-------------------+
```

### Components Detailed Breakdown
- **Maltego Client**: The Java-based GUI application where the analyst visually constructs and explores the graph.
- **Maltego Transform Application Server (TAS)**: The infrastructure that hosts remote transforms. Standard community transforms are hosted by Paterva (the creators of Maltego).
- **Transform Hub**: A marketplace within the Maltego client allowing users to install transform sets from third-party vendors (e.g., Shodan, VirusTotal, CrowdStrike, Social Links).
- **Local Transforms**: Custom scripts written by the analyst (often in Python) that execute directly on the host machine. This is crucial for querying internal tools, custom databases, or sensitive data sources where OPSEC forbids sending data to public TAS servers.

## 3. Key Transform Hub Integrations for VAPT

When setting up Maltego for an engagement, configuring the Transform Hub is the first critical step. Some essential integrations include:

1. **Standard Transforms (Paterva)**: Basic DNS enumeration, WHOIS lookups, and search engine scraping.
2. **Shodan**: Allows pivoting from IP addresses to open ports, banners, and known vulnerabilities directly within the graph.
3. **VirusTotal**: Useful for analyzing domains and IP addresses to see if they are associated with malware distribution or C2 infrastructure.
4. **PassiveTotal (RiskIQ)**: Essential for historical DNS resolutions and WHOIS history, helping uncover hidden infrastructure.
5. **Censys**: Similar to Shodan, focuses on certificate transparency logs and deep IP scans.
6. **HaveIBeenPwned**: Pivoting from target email addresses to known breaches, useful for credential stuffing or password spraying campaigns.

## 4. Building Custom Local Transforms

While the Transform Hub is powerful, advanced adversaries and red teamers often need custom local transforms. Local transforms are executed on the user's machine, keeping the data private and allowing integration with bespoke internal tooling.

### Python Local Transform Example: Port Scanner

To create a local transform, we can use the `maltego-trx` Python library. This script takes an IPv4 entity and returns Port entities for open ports found via a quick scan.

```python
import sys
from maltego_trx.transform import DiscoverableTransform
from maltego_trx.entities import Port
from maltego_trx.maltego import UIM_PARTIAL
import socket

class PortScannerTransform(DiscoverableTransform):
    """
    A simple local transform that takes an IPv4 entity and 
    checks a few common ports.
    """
    
    @classmethod
    def create_entities(cls, request, response):
        target_ip = request.Value
        
        # Ports to check
        ports_to_check = [21, 22, 80, 443, 445, 3389, 8080]
        
        for port in ports_to_check:
            if cls.check_port(target_ip, port):
                # If open, create a Port entity
                entity = response.addEntity(Port, str(port))
                entity.addProperty(fieldName="port.number", displayName="Port Number", value=str(port))
                entity.addProperty(fieldName="service.status", displayName="Status", value="Open")

    @staticmethod
    def check_port(ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0

if __name__ == "__main__":
    # Standard boilerplate for Maltego local transforms
    # It reads XML/JSON from stdin and writes to stdout
    from maltego_trx.registry import register_transform_classes
    from maltego_trx.server import app, application
    # Execution logic usually handled by maltego-trx CLI, 
    # but the concept remains: read stdin, output Maltego XML.
```

### Registering the Transform
To use this in Maltego:
1. Navigate to `Transforms -> Transform Manager`.
2. Click `New Local Transform`.
3. Provide the Display Name (`Local Port Scan`).
4. Set Input Entity to `IPv4 Address`.
5. Set the Command to your Python interpreter (e.g., `/usr/bin/python3`).
6. Set the Parameters to the script path and execution arguments.
7. Set the Working Directory.

## 5. Automating Reconnaissance with Maltego Machines

A "Machine" in Maltego is an automated script that sequentially executes multiple transforms on an entity or set of entities. Instead of manually clicking and waiting for each transform to complete, a Machine can automate the entire footprinting phase.

### Example Machine Macro: Footprint L1

Maltego comes with several built-in machines. "Footprint L1" is standard for basic domain recon:
1. Starts with a Domain entity.
2. Runs `To DNS Name` (NS, MX, A records).
3. Runs `To IP Address` on all discovered DNS names.
4. Runs `To Netblock` on all discovered IP addresses.
5. Maps the relationship between the organization's domain and its hosting infrastructure.

### Building Custom Machines
Custom machines are written in Maltego's scripting language (based on a dialect of XML/JSON). They define state transitions, loops, and conditions based on the results of transforms.

## 6. Case Study: Corporate Infrastructure and Employee Targeting

During a red team engagement, Maltego can bridge the gap between technical infrastructure and human targets.

### Phase 1: Infrastructure
1. Drop a `Domain` entity onto the graph (e.g., `targetcorp.com`).
2. Execute `To Subdomains [Fierce]` or standard brute-forcing transforms.
3. Select all resulting `DNS Name` entities and execute `To IP Address`.
4. Identify IP addresses that fall outside the corporate ASNs (e.g., AWS, Azure, DigitalOcean). These are often misconfigured shadow IT assets.

### Phase 2: Human Recon
1. Go back to the `Domain` entity.
2. Execute `To Email addresses [Search Engine]`.
3. Extract naming conventions (e.g., `first.last@targetcorp.com`).
4. Execute `To Person [Social Networks]` to map employee roles (e.g., IT Admin, HR).
5. For high-value targets (e.g., System Administrators), run their emails against `HaveIBeenPwned` transforms to check for exposed passwords in third-party breaches.
6. The resulting graph provides a clear hit-list for spear-phishing campaigns, specifically targeting individuals with known external vulnerabilities.

## 7. OPSEC and Limitations

### OPSEC Considerations
When conducting covert operations, Maltego presents significant OPSEC risks if not configured properly:
- **DNS Leaks**: Some community transforms perform DNS resolutions locally on the client machine. This can alert the target's SOC if they monitor DNS query logs.
- **API Rate Limits**: Running a bulk transform on thousands of entities can exhaust API keys rapidly.
- **Third-Party Logging**: Using public TAS servers means Paterva (or the transform provider) can theoretically see what you are searching for. For highly sensitive investigations, rely exclusively on local transforms and private infrastructure.

### Limitations
- **Graph Clutter**: Graphs with over 10,000 entities become computationally heavy and difficult to visually parse. Use Maltego's filtering, views, and weighting algorithms to hide low-value nodes.
- **False Positives**: Search engine scraping transforms frequently return inaccurate or outdated data. Manual verification is always required.

## 8. Advanced Configuration: Setting up a TAS Server internally
When executing engagements against highly secure environments, organizations may opt to run their own internal Maltego Transform Application Server (TAS). This entirely self-hosted approach guarantees that no external queries reach Paterva's infrastructure.

### TAS Architecture Requirements
- **Seed Server**: Distributes the configuration and transform lists to the Maltego clients.
- **Transform Server**: The execution engine running the Python or Java based transforms.
- **Database Backend**: Local storage for caching and historical analysis.

### Benefits of Internal TAS
1. **Total Privacy**: You can integrate directly with internal Active Directory, SIEM (like Splunk), or proprietary threat intelligence platforms without exposing API keys.
2. **Collaboration**: The team can collaborate on identical graphs (using the Shared Graphs feature) over a local network.
3. **Custom Assets**: Custom icons, entity types, and machine macros can be synchronized across all team members securely.
4. **Rate Limiting Elimination**: Bypasses the strict rate-limiting enforced by the public TAS.

### Python Integration with Local DB
```python
# Example of querying a local SQLite DB in a transform
import sqlite3
def query_local_db(ip_address):
    conn = sqlite3.connect('local_intel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT owner FROM assets WHERE ip=?", (ip_address,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Unknown"
```

## 9. Extending Maltego with API Wrappers
Another potent way to extend Maltego's capabilities is by wrapping other CLI tools directly into the UI. For instance, creating a transform that triggers `nmap` under the hood, parses the XML output, and plots the open ports automatically on the graph. This merges the active scanning world with passive OSINT.

## 10. Chaining Opportunities

- **Nmap**: Export discovered IP addresses from Maltego to a flat file and feed them into `nmap` for detailed service enumeration. See [[03 - Nmap Advanced Port Scanning]].
- **Amass/Sublist3r**: Feed the results of external subdomain enumeration tools back into Maltego using custom CSV imports to visualize complex relationships.
- **BloodHound**: While Maltego is for external OSINT, BloodHound performs similar graph-based analysis for internal Active Directory domains. Combining the mindset of both tools offers complete visibility. See [[04 - BloodHound Active Directory Mapping]].
- **Recon-ng**: Recon-ng modules can output to formats easily importable into Maltego, merging CLI efficiency with visual analysis.

## 9. Related Notes
- [[02 - OSINT Methodology and Frameworks]]
- [[07 - Shodan Web and CLI Complete Guide]]
- [[08 - Censys Search Syntax and API]]
- [[12 - Open Source Threat Intelligence]]
