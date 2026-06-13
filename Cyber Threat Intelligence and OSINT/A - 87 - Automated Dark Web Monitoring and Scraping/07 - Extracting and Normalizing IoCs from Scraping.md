---
tags: [darkweb, scraping, automation, vapt]
difficulty: advanced
module: "87 - Automated Dark Web Monitoring and Scraping"
topic: "87.07 Extracting and Normalizing IoCs from Scraping"
---

# Extracting and Normalizing IoCs from Scraping

## 1. The Challenge of Unstructured Threat Data
Cyber Threat Intelligence (CTI) gathered through automated scraping is inherently unstructured. Whether the data originates from a dark web forum, a Telegram channel, a paste site, or a hacker's blog, it usually manifests as raw, noisy text. Embedded within this text are crucial Indicators of Compromise (IoCs): IP addresses, domain names, file hashes (MD5, SHA1, SHA256), email addresses, cryptocurrency wallets, and registry keys.

The primary objective of the extraction and normalization phase is to parse this chaotic raw text, accurately identify the IoCs, strip away obfuscation, and standardize the data into a machine-readable format (like JSON or STIX 2.1) so that it can be digested by SIEMs, SOARs, and Threat Intelligence Platforms (TIPs).

## 2. Extraction Strategies: Regular Expressions (Regex)
Regex is the foundational tool for IoC extraction. Because IoCs adhere to strict formatting rules (e.g., an IPv4 address is four octets separated by periods), regex can identify them with high confidence. However, regex must be crafted carefully to avoid devastating false positives.

### 2.1. Standard Regex Patterns
Building robust regex patterns is an art. A naive IPv4 regex like `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` will match invalid IPs like `999.999.999.999`. A robust IPv4 pattern looks like:
```regex
\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
```

Other critical patterns used in CTI extraction:
- **MD5 Hash**: `\b[a-fA-F0-9]{32}\b`
- **SHA256 Hash**: `\b[a-fA-F0-9]{64}\b`
- **Bitcoin Address**: `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b`
- **Monero (XMR) Address**: `\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b`
- **Email Address**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`

### 2.2. Overcoming Defanging and Obfuscation
Threat actors and security analysts alike often "defang" IoCs to prevent accidental execution, or to bypass automated spam filters on forums. 
Common defanging techniques include:
- `192.168.1[.]1` or `192.168.1(.)1`
- `hxxp://evil-domain[.]com`
- `admin[@]company.com`
- Base64 encoded payloads embedded within text

To extract these, your extraction engine must pre-process the text, accounting for brackets, parentheses, and intentional misspellings before running the core regex engine.

## 3. Architecture of an IoC Extraction Pipeline

```text
+-----------------------+      +-------------------------+      +-------------------------+
| Scraped Raw Text      |      | Pre-Processing          |      | Regex & Decoder Engine  |
| (Telegram, Forums,    | ---> | - Remove HTML tags      | ---> | - Decode Base64/Hex     |
| Pastebins)            |      | - Un-defang URLs        |      | - Match IPs, Hashes     |
+-----------------------+      +-------------------------+      +-------------------------+
                                                                             |
                                                                             v
+-----------------------+      +-------------------------+      +-------------------------+
| STIX 2.1 JSON Output  | <--- | Normalization & Dedupe  | <--- | Post-Processing Filter  |
| - Ready for SIEM      |      | - Standardize casing    |      | - Remove false positives|
| - Enrichment triggers |      | - Map to schemas        |      |   (e.g., 127.0.0.1)     |
+-----------------------+      +-------------------------+      +-------------------------+
```

## 4. Building the Extraction Engine in Python
To handle IoC extraction efficiently, we can use open-source libraries like `iocextract` or build a custom, highly-tuned solution using the `re` module. A custom solution is usually preferred for advanced use cases to minimize false positive ingestion.

### 4.1. Refanging and Extraction Code
```python
import re
import base64

def refang_ioc(text):
    """
    Replaces common defanging techniques with standard formatting.
    """
    # Fix domains and IPs
    text = text.replace('[.]', '.').replace('(.)', '.').replace('{.}', '.')
    # Fix protocols
    text = text.replace('hxxp', 'http').replace('hXXp', 'http')
    # Fix emails
    text = text.replace('[@]', '@').replace('(at)', '@')
    return text

def decode_base64_chunks(text):
    """
    Attempts to identify and decode potential Base64 strings in the text.
    """
    # Simple heuristic to find possible b64 strings
    b64_pattern = re.compile(r'\b(?:[A-Za-z0-9+/]{4}){10,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\b')
    for match in b64_pattern.findall(text):
        try:
            decoded = base64.b64decode(match).decode('utf-8')
            # Append decoded content back to text for further analysis
            text += f"\n[DECODED]: {decoded}"
        except:
            pass
    return text

def extract_iocs(raw_text):
    """
    Extracts IPs, Domains, and SHA256 hashes from raw text.
    """
    # Pre-process text
    text_with_decoded = decode_base64_chunks(raw_text)
    clean_text = refang_ioc(text_with_decoded)
    
    iocs = {
        'ipv4': set(),
        'domains': set(),
        'sha256': set()
    }
    
    # IPv4 Pattern
    ipv4_pattern = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    iocs['ipv4'].update(ipv4_pattern.findall(clean_text))
    
    # SHA256 Pattern
    sha256_pattern = re.compile(r'\b[a-fA-F0-9]{64}\b')
    iocs['sha256'].update(sha256_pattern.findall(clean_text))
    
    # Simple Domain Pattern
    domain_pattern = re.compile(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b')
    iocs['domains'].update(domain_pattern.findall(clean_text))
    
    # Post-Processing: Remove common false positives (Localhost, private IPs)
    iocs['ipv4'] = {ip for ip in iocs['ipv4'] if not ip.startswith('127.') and not ip.startswith('10.') and not ip.startswith('192.168.') and not ip.startswith('169.254.')}
    
    return iocs

# Example usage
sample_text = "The malware communicates with hxxps://evil-c2[.]com and drops a payload with hash 8d26c59dbdb3c35b9122fb2ebdf01d81080bd1cde6d2b51266e74abfb906f233. The backup C2 is 198[.]51[.]100[.]42."

extracted = extract_iocs(sample_text)
print(extracted)
# Output: {'ipv4': {'198.51.100.42'}, 'domains': {'evil-c2.com'}, 'sha256': {'8d26c59dbdb3c35b9122fb2ebdf01d81080bd1cde6d2b51266e74abfb906f233'}}
```

## 5. Normalization and Data Modeling
Extracting the IoCs is only the first step. The data must be normalized to be useful. Normalization involves converting the extracted data into a standard schema.

A highly adopted standard is **STIX 2.1 (Structured Threat Information Expression)**. Normalizing our extracted IoCs into STIX format allows seamless integration with tools like MISP (Malware Information Sharing Platform), OpenCTI, and native SIEM ingestion APIs.

### 5.1. Creating STIX Indicator Objects
```python
import uuid
from datetime import datetime

def create_stix_indicator(ioc_type, ioc_value, source_context):
    """
    Wraps an extracted IoC into a STIX 2.1 Indicator object.
    """
    indicator_id = f"indicator--{uuid.uuid4()}"
    
    # Map our internal types to STIX patterning
    pattern_map = {
        'ipv4': f"[ipv4-addr:value = '{ioc_value}']",
        'domains': f"[domain-name:value = '{ioc_value}']",
        'sha256': f"[file:hashes.'SHA-256' = '{ioc_value}']"
    }
    
    stix_obj = {
        "type": "indicator",
        "spec_version": "2.1",
        "id": indicator_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "modified": datetime.utcnow().isoformat() + "Z",
        "name": f"Automated Extraction: {ioc_value}",
        "description": f"Extracted automatically from source: {source_context}",
        "pattern": pattern_map.get(ioc_type, ""),
        "pattern_type": "stix",
        "valid_from": datetime.utcnow().isoformat() + "Z"
    }
    
    return stix_obj
```

## 6. Contextual Enrichment
Raw IoCs lack context. An IP address is meaningless unless we know who owns it, where it is located, and if it has a malicious history.
The extraction pipeline should immediately hand off normalized IoCs to an enrichment service that queries APIs such as:
- **VirusTotal**: For hash reputation and domain resolutions.
- **Shodan / Censys**: For open ports, TLS certificates, and banners on IP addresses.
- **GreyNoise**: To filter out Internet background noise and benign scanners (massively reducing SIEM alert fatigue).

## Real-World Attack Scenario
A threat actor uploads a text file to a dark web paste site containing the configuration details of a newly deployed Cobalt Strike team server, including the IPv4 address, domain name, and the SHA256 hashes of the generated beacons. 

Our automated scraper pulls the raw paste. The text contains heavily defanged IoCs (`198[.]51[.]100[.]42`) to avoid automated takedowns. The IoC Extraction Pipeline refangs the text, successfully parsing the Cobalt Strike C2 IP and beacon hashes. The hashes are normalized into STIX 2.1 format and automatically ingested into the organization's SIEM and MISP instance, creating high-fidelity blocklist rules. When an internal endpoint later attempts to beacon out to that IP, the firewall blocks the connection, stopping the ransomware deployment before lateral movement occurs.

## Chaining Opportunities
- The initial source of the text often comes from tools built in [[06 - Scraping Telegram Channels with Telethon]] and dark web crawlers.
- Once IoCs are extracted and formatted, they must be indexed for searching, bridging the gap to [[10 - Ingesting Scraped Data into Elasticsearch]].
- To extract complex relationships, this can be combined with [[08 - NLP for Identifying Credential Leaks in Dumps]].

## Related Notes
- [[12 - Automating MISP Integrations]]
- [[15 - Evaluating Threat Intelligence Feeds]]
- [[04 - Bypassing Anti-Scraping Mechanisms]]

## 7. Advanced YARA Rule Generation from Extracted Strings
Once IoCs (like IPs and domains) are extracted, they are highly valuable. However, CTI analysts often encounter malware configurations or raw memory dumps posted on paste sites. Extracting plain strings from these dumps can automatically fuel the generation of YARA rules.

YARA is a tool aimed at helping malware researchers identify and classify malware samples.
If the extraction pipeline identifies unique, high-entropy strings or specific mutexes from a raw paste, it can automatically generate a templated YARA rule.

### 7.1. Automated YARA Templating
```python
def generate_yara_rule(rule_name, strings_list):
    """
    Generates a basic YARA rule from extracted unique strings.
    """
    rule = f'rule {rule_name} {{\n'
    rule += '    meta:\n'
    rule += '        author = "Automated Extraction Engine"\n'
    rule += '        description = "Auto-generated from Dark Web Paste"\n'
    rule += '    strings:\n'
    
    for idx, string in enumerate(strings_list):
        # Escape quotes and backslashes
        safe_string = string.replace("\\", "\\\\").replace('"', '\\"')
        rule += f'        $s{idx} = "{safe_string}" ascii wide\n'
        
    rule += '    condition:\n'
    rule += f'        any of them\n'
    rule += '}\n'
    
    return rule

# Example usage on extracted unique API endpoints
extracted_strings = ["/api/v1/bot/register", "mutex_global_ransom_v2"]
print(generate_yara_rule("DarkWeb_Botnet_Config", extracted_strings))
```

## 8. Storing Extracted Data: Graph Databases vs. Relational
While STIX 2.1 JSON is great for transportation, storing relationships between IoCs is critical. A relational database struggles with the concept of "IP A was mentioned by Author B who also posted Domain C".

Using a Graph Database (like Neo4j or ArangoDB) is highly recommended for storing extracted IoCs. 
- **Nodes**: IP Addresses, Domains, Hashes, Authors, Forums.
- **Edges (Relationships)**: `POSTED_BY`, `RESOLVES_TO`, `COMMUNICATES_WITH`.

By modeling the extracted IoCs as a graph, analysts can run queries to find infrastructure overlap between seemingly unrelated threat actors, significantly enhancing the intelligence value of the raw scrape.
