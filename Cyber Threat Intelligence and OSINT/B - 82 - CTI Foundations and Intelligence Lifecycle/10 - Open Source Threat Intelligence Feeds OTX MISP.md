---
tags: [cti, intelligence, threat-hunting, vapt]
difficulty: beginner
module: "82 - CTI Foundations and Intelligence Lifecycle"
topic: "82.10 Open Source Threat Intelligence Feeds OTX MISP"
---

# 82.10 - Open Source Threat Intelligence Feeds (OTX & MISP)

## Introduction to OSINT for Threat Intelligence

Cyber Threat Intelligence (CTI) programs do not, and cannot, exist in a vacuum. No single organization—regardless of budget or size—possesses complete, unhindered visibility into the complex global threat landscape. To build effective, proactive defenses, organizations must inherently rely on external intelligence sources to bridge their visibility gaps. 

While commercial, proprietary threat intelligence feeds (e.g., from vendors like CrowdStrike, Mandiant, or Recorded Future) provide highly curated, expertly vetted data, they are often cost-prohibitive for smaller organizations and can create data silos. 

**Open Source Threat Intelligence (OSINT)** and community-driven sharing platforms solve this issue and serve as the absolute backbone of global cybersecurity collaboration. They provide free, democratized, and instantaneous access to critical indicators of compromise (IoCs), adversary TTPs, and deep-dive campaign analysis. Two of the most critical and widely adopted foundational platforms in this entire ecosystem are **MISP (Malware Information Sharing Platform)** and **AlienVault OTX (Open Threat Exchange)**.

## Deep Dive: MISP (Malware Information Sharing Platform)

Originally developed by NATO in the early 2010s to combat targeted espionage, and now aggressively driven by the broader global security community, MISP is an open-source threat intelligence platform (TIP). It is arguably the most widely deployed open-source TIP globally, utilized extensively by military organizations, ISACs (Information Sharing and Analysis Centers), CERTs, and major private enterprises.

### Core Architecture and Data Model of MISP

MISP is meticulously designed not just as a one-way feed, but as a collaborative, bidirectional platform for creating, storing, enriching, and correlating threat intelligence.

1. **Events:** The fundamental data wrapper in MISP. An Event represents a specific, bounded incident, a detailed malware analysis report, or a distinct, ongoing threat campaign (e.g., "Emotet Malspam Campaign Q3 Targeting Healthcare").
2. **Attributes:** The individual technical indicators residing safely inside an Event. This includes granular data like IP addresses, file hashes (MD5, SHA1, SHA256), URLs, domain names, or even specific registry keys and mutexes.
3. **Objects:** Advanced, structured templates that group related Attributes together. For example, a "File" object contains separate attributes for the filename, the hash, the file size, and the compilation timestamp, creating rich, structured context rather than isolated data points.
4. **Galaxies:** High-level contextual concepts explicitly attached to Events. Common Galaxies include specific Threat Actor profiles (e.g., attributing the event to APT29), ransomware families (e.g., LockBit), or specific MITRE ATT&CK techniques utilized during the intrusion.
5. **Taxonomies:** Powerful tagging systems used to classify and regulate Events. The most common taxonomy is the TLP (Traffic Light Protocol) which dictates strict sharing restrictions (e.g., TLP:RED means do not share outside the organization), and Kill Chain phases to indicate the stage of the attack lifecycle.

### MISP Sharing Models and Network Synchronization

The true power of MISP lies precisely in its decentralized, peer-to-peer sharing capabilities.
- **Sync Servers:** Organizations host their own sovereign MISP instances internally and securely configure them to synchronize data continuously with trusted partner MISP instances via encrypted APIs.
- **Push vs. Pull:** A corporate SOC can dynamically pull specific subsets of intelligence from a partner (e.g., "Only pull Events tagged as TLP:GREEN and related specifically to the Financial sector"). Conversely, if the SOC discovers a brand new threat internally during an investigation, they can create a new Event and "Push" it to their trusted partners, enriching the global defense community in real-time.

### Enterprise Automation with PyMISP

Because MISP is heavily API-driven, security automation engineers utilize the robust **PyMISP** Python library to interact with the platform programmatically, integrating it directly into SOAR platforms.

```python
# Example: Adding an IoC to MISP automatically via Python script
from pymisp import ExpandedPyMISP, MISPEvent, MISPAttribute

# Configuration for the internal MISP server
MISP_URL = 'https://misp.internal.corp'
MISP_KEY = 'YOUR_SECURE_API_KEY_HERE'

# Initialize the secure connection
misp = ExpandedPyMISP(MISP_URL, MISP_KEY, False)

def create_threat_event(ip_address, description):
    # 1. Create a new, blank Event object
    event = MISPEvent()
    event.info = f"Automated SOAR Alert: Suspicious C2 Infrastructure - {description}"
    event.distribution = 1 # 1 = Share with this community only
    event.threat_level_id = 2 # 2 = Medium Severity
    event.analysis = 1 # 1 = Initial Analysis Phase
    
    # Push the blank event to the MISP server to get an ID
    event = misp.add_event(event, pythonify=True)
    
    # 2. Add an IP attribute directly to the new Event
    attribute = MISPAttribute()
    attribute.type = 'ip-dst'
    attribute.value = ip_address
    attribute.comment = 'Observed communicating outbound with critical HR database server.'
    
    # Push the attribute to the server
    misp.add_attribute(event.id, attribute)
    print(f"[+] Successfully added Event ID: {event.id} containing Malicious IP: {ip_address}")

if __name__ == '__main__':
    create_threat_event('198.51.100.45', 'Potential Cobalt Strike Beacon Activity')
```

## Deep Dive: AlienVault OTX (Open Threat Exchange)

AlienVault OTX (now acquired and operated by AT&T Cybersecurity) operates on a slightly different paradigm than MISP. It functions essentially as a massive, centralized, crowdsourced social network specifically engineered for security professionals.

### The Pulse System Architecture
The core unit of intelligence in OTX is known as a **Pulse**. A Pulse is a curated collection of IoCs combined with a detailed narrative description. If an analyst reads a detailed blog post from a vendor about a new ransomware variant, they can use OTX's automated scraping tools to extract the IoCs directly from the blog text and instantly create a new Pulse.
Users "subscribe" to specific Pulses created by highly trusted researchers, trusted organizations, or specific topics. When a subscribed Pulse is updated with new indicators, the user's security infrastructure automatically downloads the new data.

### The OTX DirectConnect API
OTX provides the powerful DirectConnect API, allowing SIEMs, firewalls, and EDR solutions to seamlessly ingest Pulse data at machine speed. Many modern security tools feature native OTX integration plugins, requiring only the insertion of an API key to begin actively blocking malicious IPs on a global scale.

## Assessing and Ingesting OSINT Feed Quality

A critical, often overlooked challenge with free OSINT feeds is maintaining data quality. Ingesting everything blindly will inevitably destroy a SIEM with massive waves of false positives, causing alert fatigue. Defenders must rigorously evaluate feeds based on:
1. **Fidelity (Accuracy):** How often is a provided indicator a false positive? (e.g., blocking `8.8.8.8` Google DNS simply because a piece of malware pinged it to check for internet connectivity).
2. **Context:** Does the feed provide the critical *why* behind the indicator, or does it just dump a list of raw, contextless IPs?
3. **Decay (Freshness):** Threat actor infrastructure changes rapidly. An IP address heavily used for a targeted phishing campaign today might belong to a completely legitimate web hosting customer tomorrow. Feeds must be actively and aggressively aged out; indicators older than 30-60 days should typically be moved from an active "Block" policy to a passive "Alert/Log" policy.

## Visualizing MISP and OTX Integration Architecture

```mermaid
flowchart LR
    subgraph External["External Communities"]
        OTX["AlienVault OTX<br/>(Crowdsourced IoCs)"]
        Abuse["Abuse.ch Feeds<br/>(URLhaus, SSL Black)"]
        MISP["Partner MISP Server<br/>(Sector ISAC)"]
    end

    subgraph Internal["Internal Corporate Network"]
        SOAR["SOAR Platform / TIP Orchestrator<br/>(De-duplication, Allowlisting, Context)"]
        SIEM["Corporate SIEM<br/>(Splunk / Sentinel)"]
        FW["Perimeter Firewall<br/>(Palo Alto, Forti)"]
    end

    OTX -->|(API Polling)| SIEM
    OTX --> SOAR
    Abuse --> SOAR
    MISP <-->|(MISP Sync Protocol)| SOAR
    SOAR --> SIEM
    SOAR -->|(Automated Blocking)| FW
```

## Other Notable OSINT Feeds
Beyond the giants of MISP and OTX, the security community relies heavily on specialized, highly focused data feeds:
- **Abuse.ch:** A legendary, non-profit project operated out of Switzerland providing incredibly high-fidelity, specialized feeds including:
  - **URLhaus:** Actively tracking and sharing malware distribution URLs.
  - **MalwareBazaar:** Sharing actual, raw malware samples for researchers.
  - **ThreatFox:** Sharing specific IoCs (IPs, domains) exclusively associated with malware C2.
- **CISA KEV (Known Exploited Vulnerabilities):** The definitive, mandatory list maintained by the US government cataloging CVEs that are actively being exploited in the wild. This feed is absolutely essential for prioritizing vulnerability management and patching cycles.
- **PhishTank:** A massive, collaborative clearinghouse for data and information about phishing URLs across the internet.

## Real-World Attack Scenario: Alert Enrichment via OSINT

**The Scenario:** A Tier-1 SOC analyst receives a low-severity alert from the perimeter firewall regarding a blocked outbound HTTP connection from an internal user workstation to the IP address `103.15.22.XX`. 

**The Traditional Investigation:** The analyst executes a basic WHOIS lookup, observes that the IP is registered in an overseas datacenter, shrugs, assumes it was merely aggressive adware or tracking, and immediately closes the ticket as a false positive.

**The OSINT-Enriched Investigation:**
1. The organization's SIEM is deeply integrated with their central internal MISP instance.
2. When the firewall alert fires, the SIEM automatically queries MISP for the IP `103.15.22.XX`.
3. MISP immediately returns a critical hit. The IP is part of a detailed Event created just two days ago by an allied Financial ISAC, explicitly tagged with the `Galaxy` attribute: **APT32 (OceanLotus)**.
4. The Event details indicate that this specific IP address is utilized exclusively for secondary Command and Control channels, and is only accessed *after* successful, deep lateral movement.
5. **The Action:** The analyst suddenly realizes this is absolutely not adware; it is indicative of a critical, ongoing nation-state breach. The alert severity is instantly escalated to Critical, and the full Incident Response playbook for APT compromise is aggressively activated. The external OSINT feed fundamentally transformed a seemingly benign alert into a crucial, company-saving detection.

## Chaining Opportunities

- Feeds from OTX and MISP are heavily reliant on the foundational distinction between **IoCs and IoAs**; OSINT feeds primarily distribute static IoCs, while internal teams must develop the behavioral IoAs.
- To share intelligence smoothly between different, heterogeneous platforms (e.g., moving data from a MISP instance to a generic TAXII server), the raw data is formally translated into **STIX/TAXII** standards.
- Intelligence sourced and curated from these platforms directly drives the **Intelligence Driven Incident Response (IDIR)** process by enriching internal alerts and guiding threat hunting hypotheses.

## Related Notes

- [[07 - Intelligence Driven Incident Response]]
- [[08 - Indicators of Compromise IoC vs Indicators of Attack IoA]]
- [[09 - STIX and TAXII Standards Explained]]
- [[06 - Lockheed Martin Cyber Kill Chain]]
