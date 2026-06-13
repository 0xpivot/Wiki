---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.03 Shodan and Censys for Tracking Threat Infrastructure"
---

# 03 - Shodan and Censys for Tracking Threat Infrastructure

## Introduction

Shodan and Censys are often described colloquially as "search engines for the Internet of Things," but to a Cyber Threat Intelligence (CTI) analyst, they represent the absolute pinnacle of passive infrastructure tracking. While traditional search engines like Google index web page *content* (HTML, text, images), Shodan and Censys index the *responses* (service banners, HTTP headers, cryptographic certificates, raw protocol handshakes) from network ports across the entire global IPv4 address space, and increasingly, the IPv6 space.

By continuously scanning the internet, these platforms build vast, historically rich databases of exposed services, open ports, software versions, and X.509 certificates. Threat actors, despite their best efforts to remain covert, must spin up infrastructure to conduct operations—Command and Control (C2) servers, phishing landing pages, payload delivery servers, VPN nodes, and proxy networks. If this infrastructure touches the public internet, it inevitably gets scanned. The art of CTI involves writing highly specific, mathematically precise queries to identify the unique "fingerprints" of adversary tools amidst the cacophony of the global internet.

## Core Concepts of Active Internet Scanning

### The Scanning Methodology
Both platforms perform mass, continuous active scanning, typically utilizing stateless scanning tools like ZMap or Masscan to achieve high-speed coverage of the entire IPv4 space in a matter of hours. They probe common ports (80, 443, 22, 3389, 53, etc.) and, when a port is found open, they perform deeper protocol-specific handshakes to extract metadata.

### Service Banners and Application Fingerprinting
A banner is the metadata returned by a service upon initial connection. 
- *Example*: Connecting to port 22 might return `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1`.
This single string reveals the protocol (SSH), the specific software version (OpenSSH 8.2p1), and the underlying operating system (Ubuntu). Threat actors often use specific, unpatched, or misconfigured software, or they deploy custom malware frameworks (like Cobalt Strike, Sliver, Metasploit, Brute Ratel) that return distinct, recognizable banners or very specific HTTP response headers.

## Shodan in Depth

Shodan focuses heavily on parsing the banners of various protocols, ranging from standard HTTP/HTTPS to complex Industrial Control System (ICS) protocols like Modbus, DNP3, and Siemens S7. It is highly effective for finding exposed databases (Elasticsearch, MongoDB), vulnerable IoT devices, and default C2 installations.

### Key Shodan Operators for CTI
- **`port:`**: Filters by open port (e.g., `port:3389` for RDP, `port:5900` for VNC).
- **`org:` / `asn:`**: Filters by the organization or Autonomous System Number (ASN). Threat actors frequently utilize "bulletproof" hosting providers or specific ASNs known to ignore abuse complaints. Tracking these ASNs is a common CTI practice.
- **`http.title:` / `http.html:`**: Searches within the HTTP response title or body. Useful for finding specific phishing kits or default C2 panel logins.
- **`ssl.cert.subject.cn:` / `ssl.cert.issuer.cn:`**: Searches for specific Common Names in SSL/TLS certificates. Critical for tracking infrastructure relying on custom or self-signed certificates.
- **`http.favicon.hash:`**: A highly effective, mathematically sound fingerprinting technique. Shodan calculates a MurmurHash3 of the `favicon.ico` file. Many C2 frameworks or phishing kits have default favicons.

#### The Favicon Hash Technique Explained
If an analyst identifies a malicious server running a specific phishing kit, they can download the `favicon.ico`, calculate its MurmurHash3, and query Shodan (`http.favicon.hash:<hash>`) to find *every other server* on the internet hosting that exact same phishing kit, regardless of what domain or IP it resides on.

```python
# Calculating a Shodan Favicon Hash in Python
import mmh3
import requests
import codecs

def get_favicon_hash(url):
    try:
        response = requests.get(url, verify=False, timeout=5)
        # Shodan uses a specific base64 encoding scheme for the hash calculation
        favicon = codecs.encode(response.content, 'base64')
        hash_value = mmh3.hash(favicon)
        return hash_value
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage on a suspected malicious panel
target_favicon_url = 'http://malicious-c2.com/favicon.ico'
hash_val = get_favicon_hash(target_favicon_url)
if hash_val:
    print(f"[+] Shodan Dork generated: http.favicon.hash:{hash_val}")
    print("[*] Plug this into Shodan to find identical panels.")
```

## Censys in Depth

While similar in concept to Shodan, Censys places a much stronger emphasis on highly structured data and has historically possessed exceptional, granular capabilities regarding X.509 Certificate parsing. Censys allows for deeply nested queries into specific certificate fields, making it invaluable for tracking actor infrastructure based on their TLS setup and automated certificate issuance patterns.

### Key Censys Capabilities
Censys aggregates data into primary datasets: Hosts (IPs) and Certificates.
- **Certificate Tracking**: Threat actors often reuse the exact same self-signed certificate across multiple C2 servers, or they use automated scripts to generate Let's Encrypt certificates with highly predictable naming conventions or Subject Alternative Names (SANs).
- **The Pivot**: The core Censys workflow. An analyst can find a malicious IP, extract the SHA-256 fingerprint of its SSL certificate, pivot to the Censys Certificate dataset to find the certificate details, and then pivot *back* to the Hosts dataset to find all other IPs that have ever presented that specific certificate globally.

#### Censys Query Example: Hunting Cobalt Strike
To find Cobalt Strike team servers based on their default self-signed certificate characteristics:
`services.tls.certificates.leaf_data.subject.organization="Cobalt Strike"` 
*(Note: Sophisticated actors change this default setting, but lazy actors or default deployments are still caught by this).*

## Advanced Fingerprinting: JARM

JARM is an active TLS server fingerprinting tool developed by Salesforce. It is arguably the most powerful addition to infrastructure tracking in recent years. Instead of passively reading banners, JARM sends 10 distinct, specialized TLS Client Hello packets to a server and records the specific attributes of the server's TLS Server Hello responses. The resulting 62-character hash uniquely identifies the precise TLS configuration and library stack of the server.

Both Shodan and Censys heavily integrate JARM searching. Because malware C2 servers (like Trickbot, Cobalt Strike, Sliver, or Metasploit) often use custom or specific TLS libraries (e.g., a specific version of OpenSSL bundled with the malware, or a custom Go TLS implementation), their JARM hash is often completely distinct from legitimate web servers like Apache or Nginx.

- *Shodan Query*: `ssl.jarm:<hash>`
- *Censys Query*: `services.tls.jarm_hash:"<hash>"`

## Real-World Attack Scenario

### Scenario: Tracking a Cobalt Strike Campaign via JARM and Certs

1. **Initial Indicator**: A SOC analyst receives an IOC from a compromised host: a suspicious HTTPS beaconing connection to `198.51.100.45` on port 443.
2. **Shodan Analysis**: The CTI analyst queries `198.51.100.45` in Shodan. The results show port 443 is open, but the HTTP response returns a `404 Not Found` with a specific `Content-Length: 0` and an unusually formatted `Date` header. This anomaly is a known characteristic of an unconfigured Cobalt Strike Team Server.
3. **JARM Fingerprinting**: The analyst notes the JARM hash associated with this IP in Shodan: `2ad2ad16d2ad2ad22c2ad2ad2ad2ad...`. This specific hash is known within the CTI community to correlate strongly with default Java-based TLS servers used by Cobalt Strike.
4. **Certificate Extraction**: The analyst looks at the SSL certificate presented by that IP. It is a self-signed certificate with the Subject `CN=Major Cobalt Strike, OU=Advanced Threat, O=Malware, L=Nowhere, C=XX`. (The actor failed to modify the default Malleable C2 profile).
5. **Pivoting in Censys**: The analyst takes the SHA-256 fingerprint of that certificate and searches the Censys Certificate dataset. They find the certificate.
6. **Infrastructure Expansion**: The analyst pivots from the Certificate back to the Censys Hosts dataset to find all IPs that have presented this exact certificate. Censys returns 12 different IP addresses across various bulletproof hosting providers.
7. **Result**: The analyst has proactively identified 12 additional C2 servers belonging to the same actor before they were even used in an attack, allowing the firewall team to preemptively block the entire cluster.

## ASCII Diagram: Active Scanning and Pivoting

```text
                                (1) Mass Port Scanning (ZMap/Masscan)
    +-----------------+        ====================================>     +------------------+
    |                 |                                                  |   Adversary C2   |
    |  Shodan/Censys  |        <====================================     |   (IP: X.X.X.X)  |
    |  Scanners       |        (2) Banner Grab / TLS Handshake / JARM    +------------------+
    |                 |            Returns: "HTTP 404", Cert Hash,
    +-----------------+                     JARM Hash, Favicon
             |
             | (3) Parse, Index & Store
             V
    +-----------------+
    |                 |   (4) CTI Analyst queries specific Hash
    |  Search Engine  |  <---------------------------------------------  +------------------+
    |  Index (DB)     |                                                  |   CTI Analyst    |
    |                 |  --------------------------------------------->  |                  |
    +-----------------+   (5) DB returns IPs: X.X.X.X, Y.Y.Y.Y, Z.Z.Z.Z  +------------------+
                                  (All sharing the same C2 profile)
                                              |
                                              | (6) Proactive Defense
                                              V
                                    +------------------+
                                    | Corporate Firewalls|
                                    | Block new IPs      |
                                    +------------------+
```

## Defensive Countermeasures and Actor Evasion

Threat actors are acutely aware of Shodan and Censys and actively attempt to evade indexing.
- **Malleable C2 Profiles**: Frameworks like Cobalt Strike allow operators to heavily modify their HTTP responses, headers, and certificates to mimic legitimate traffic (e.g., masquerading as a jQuery update or an Amazon AWS endpoint), making their fingerprints blend in with legitimate noise.
- **Firewall Rules (UFW/IPTables)**: Advanced actors configure their infrastructure to drop traffic specifically from known Shodan, Censys, and Shadowserver scanner IP ranges, preventing their servers from being indexed in the first place.
- **Reverse Proxies / CDNs**: Actors place their C2 servers behind Cloudflare or Fastly. Shodan will only scan the CDN's edge node, hiding the true infrastructure IP and specific service banner from the public internet. Analysts must then rely on finding configuration errors that leak the origin IP.

## Chaining Opportunities

- IPs discovered via Shodan/Censys can be fed directly into [[04 - RiskIQ PassiveTotal and Passive DNS]] to determine what domains have resolved to those malicious IPs over time, expanding the web of intelligence.
- If an actor uses a specific custom domain found in an SSL certificate via Censys, that domain can be investigated using [[05 - WHOIS History and Domain Registration Reversals]] to find the registrant's email or associated aliases.
- Open directories found via Shodan can be systematically dorked using techniques from [[01 - Advanced Search Engine Dorking for Threat Intel]] to extract files without setting off active alerts on the target server.

## Related Notes
- [[01 - Advanced Search Engine Dorking for Threat Intel]]
- [[02 - Reverse Image Searching and EXIF Data Analysis]]
- [[04 - RiskIQ PassiveTotal and Passive DNS]]
- [[05 - WHOIS History and Domain Registration Reversals]]

