---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.13 SpiderFoot and Automating OSINT Gathering"
---

# 13 - SpiderFoot and Automating OSINT Gathering

## Introduction

In modern Cyber Threat Intelligence (CTI) and vulnerability assessment operations, the sheer volume of available open-source intelligence (OSINT) is staggering. Manually querying dozens of databases, search engines, threat intelligence feeds, and public registries for a single target (a domain, IP address, or individual) is inefficient and prone to human error. 

SpiderFoot is a highly extensible, automated OSINT reconnaissance tool that streamlines this process. It acts as an orchestration engine, taking a single target and simultaneously querying hundreds of integrated modules (data sources) to build a comprehensive intelligence profile. By automating the collection and correlation of data, SpiderFoot allows analysts to focus on interpreting the intelligence rather than hunting for it. It is heavily utilized for external attack surface management (EASM), threat actor profiling, and identifying data leaks.

## Core Concepts of Automated OSINT

### 1. Target Types and Seed Identification
Automation engines require a specific target type to determine which modules to execute. SpiderFoot recognizes various targets:
*   **Domains/Subdomains:** The primary entry point for organizational mapping.
*   **IPv4/IPv6 Addresses & Subnets:** Used for infrastructure mapping.
*   **Usernames and Email Addresses:** Crucial for threat actor tracking and credential leak discovery.
*   **Phone Numbers and Names:** Used for social engineering and personnel reconnaissance.
*   **Bitcoin Addresses:** For tracking financial flows in ransomware or extortion operations.

### 2. Modules and Integrations
SpiderFoot relies on a modular architecture. Each module is designed to interact with a specific API or perform a specific technique.
*   **Passive Modules:** Query third-party databases (like Shodan, HaveIBeenPwned, VirusTotal, or WHOIS registries) without directly interacting with the target's infrastructure. This maintains high OPSEC.
*   **Active Modules:** Interact directly with the target (e.g., performing DNS zone transfers, port scanning, or web scraping). This generates noise and can alert the target to the reconnaissance effort.

### 3. Data Correlation and Event Linkage
As modules return data, SpiderFoot acts as a correlation engine. If a module discovers an email address associated with a target domain, SpiderFoot automatically feeds that newly discovered email address back into its engine as a new target, subsequently running email-specific modules (like checking for data breaches) against it.

## Technical Architecture of SpiderFoot

```text
+-----------------------------------------------------------------------------------------+
|                           SpiderFoot Automation Architecture                            |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   [ Analyst Input ]                                                                     |
|    Target: example.com                                                                  |
|         |                                                                               |
|         v                                                                               |
|  +-----------------------------------------------------------------------------------+  |
|  |                           SpiderFoot Core Engine                                  |  |
|  |                                                                                   |  |
|  |  +----------------+      +------------------+      +---------------------------+  |  |
|  |  | Target Parser  | ---> | Module Scheduler | ---> | Correlation & Event Store |  |  |
|  |  +----------------+      +--------+---------+      +-------------+-------------+  |  |
|  +-----------------------------------|------------------------------|----------------+  |
|                                      |                              |                   |
|                                      v                              v                   |
|  +-----------------------------------------------------------------------------------+  |
|  |                              SpiderFoot Modules                                   |  |
|  |                                                                                   |  |
|  | [ DNS Resolution ]  [ Shodan / Censys ]  [ WHOIS History ]  [ Threat Intel Feeds ]|  |
|  | [ Web Scraping ]    [ Data Breach DBs ]  [ Cloud Storage ]  [ Social Media APIs ] |  |
|  +-----------------------------------------------------------------------------------+  |
|                 |                     |                    |                         |  |
|                 v                     v                    v                         v  |
|       (Direct Target Query)      (Third-Party APIs and External Datasets)               |
|                                                                                         |
|       <------------------------- (Data Returned and Correlated) --------------------->  |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

## Tooling and Configuration

### 1. API Key Management
SpiderFoot is significantly more powerful when configured with API keys for premium or rate-limited services. Analysts should populate the configuration with keys for:
*   Shodan, Censys, SecurityTrails, AlienVault OTX, Hunter.io, FullContact, and HaveIBeenPwned.

### 2. Scan Use Cases (Profiles)
SpiderFoot offers pre-defined scan profiles tailored to specific CTI requirements:
*   **Investigate:** Broad, passive scan designed to gather as much information as possible without alerting the target. Ideal for initial threat actor tracking.
*   **Footprint:** Focuses on mapping out the network infrastructure, subdomains, and cloud assets of an organization.
*   **Passive:** Strictly restricts the engine to only use modules that do not touch the target infrastructure, ensuring maximum OPSEC.
*   **All (Active & Passive):** The most aggressive profile, useful for authorized Red Team engagements but dangerous for clandestine CTI operations.

## Real-World Attack Scenario

### Identifying a Careless Insider Threat
A cybersecurity firm was hired to investigate a potential insider threat who was allegedly leaking sensitive proprietary code to a competitor. The only clue was an anonymous ProtonMail address used to negotiate the sale of the code: `dev_shadow_99@protonmail.com`.

**The Automated OSINT Investigation:**
1.  **Initial Configuration:** The analyst launched SpiderFoot, set the target to `dev_shadow_99@protonmail.com`, and selected the "Passive" profile to avoid alerting the actor.
2.  **Module Execution:** SpiderFoot automatically ran modules against HaveIBeenPwned, various username search engines, and Git repositories.
3.  **The Pivot (Automated):** A module identified that the username `dev_shadow_99` was registered on a niche programming forum years ago. SpiderFoot extracted the user profile from that forum.
4.  **Correlation:** The forum profile contained a link to a personal GitHub repository. SpiderFoot automatically parsed this repository and ran its source-code analysis modules.
5.  **The Discovery:** The GitHub module flagged an old, abandoned commit from 4 years prior. Within that commit, the user had accidentally hardcoded a personal Gmail address (`john.doe.1985@gmail.com`) instead of their anonymous handle.
6.  **Resolution:** SpiderFoot fed the newly discovered Gmail address back into the engine, which cross-referenced it with LinkedIn data, positively identifying the employee working within the target company's development team.

This complex chain of discovery—from an anonymous email, to a forum, to a GitHub repository, to a real identity—was completely automated by SpiderFoot in under 20 minutes.

## Detailed Methodology: Executing a SpiderFoot Investigation

### Step 1: Define the Scope and OPSEC Constraints
Before starting a scan, determine your OPSEC requirements. If investigating a highly capable APT or a sensitive target, you MUST ensure that only Passive modules are selected. An active scan (like a port scan) originating from your IP will immediately burn your investigation.

### Step 2: Configure Modules and APIs
Ensure your SpiderFoot instance is properly configured.
*   Navigate to the settings and input all available API keys.
*   Disable noisy modules (like active web crawling) if stealth is required.

### Step 3: Initiate the Scan
Input the target (Domain, IP, Username, etc.).
Select the appropriate use case (e.g., "Investigate" or "Footprint").
Initiate the scan. Be prepared: a comprehensive scan against a large organization's domain can take several hours to complete.

### Step 4: Triage and Filter Results
Once the scan is complete, analysts face a massive dataset. SpiderFoot provides data categorization to aid in triage.
*   **Identify Critical Data:** Look for "Data Leaks," "Vulnerabilities," "Open Ports," and "Cloud Storage" (e.g., open S3 buckets).
*   **Review Connections:** Examine the "Nodes" view to see how disparate pieces of information are linked.

### Step 5: Export and Further Analysis
SpiderFoot is an aggregator, not the final step.
*   Export the highly confident, relevant data points (IPs, domains, aliases).
*   Import this refined data into advanced graphing tools like Maltego for visual mapping.

## Deep Dive: Advanced SpiderFoot Modules and EASM

### 1. External Attack Surface Management (EASM) Integration
SpiderFoot is not solely for tracking threat actors; it is a foundational tool for EASM. Organizations use it to continuously monitor their own digital footprint to identify shadow IT and exposed assets before attackers do.
*   **Shadow IT Discovery:** Development teams often spin up unauthorized cloud instances (AWS, Azure, GCP) outside of central IT control. SpiderFoot's DNS brute-forcing and reverse-WHOIS modules can automatically link these rogue subdomains and IP blocks back to the parent organization.
*   **Continuous Monitoring:** SpiderFoot HX (the commercial version) allows for continuous, scheduled scanning. It monitors the attack surface on a daily or weekly basis, alerting analysts only when the state changes (e.g., a new port opens on a known server, or a new subdomain is registered).
*   **Vulnerability Mapping:** While not a vulnerability scanner itself, SpiderFoot integrates with CVE databases and Shodan. If it discovers a server running Apache 2.4.49, it will automatically cross-reference this with known vulnerabilities (like CVE-2021-41773) and flag the asset as highly critical.

### 2. Deep Web and Dark Web Modules
To track adversaries, OSINT must extend beyond the clear web.
*   **Onion Crawling:** SpiderFoot has modules designed to query Tor-to-Web gateways (like onion.ws) to search dark web forums and marketplaces for the target keyword, email, or cryptocurrency address.
*   **Pastebin and Text Dump Scraping:** Threat actors frequently dump stolen credentials or configuration files on sites like Pastebin. SpiderFoot continuously queries these sites via API to see if the target domain or employee emails appear in recent dumps.
*   **Ransomware Extortion Site Monitoring:** Advanced modules can query the RSS feeds or JSON APIs of known ransomware data leak sites (DLS) to determine if a target organization has been listed as a victim.

### 3. Cryptocurrency Tracing Modules
SpiderFoot can automate the initial stages of blockchain forensics.
*   **Bitcoin/Ethereum Address Enrichment:** If a target Bitcoin address is input, SpiderFoot queries APIs like Blockchain.info or BlockCypher to retrieve the wallet's current balance, total transactions, and timestamps of the first and last transactions.
*   **Abuse Database Cross-referencing:** The wallet address is automatically checked against databases like BitcoinAbuse to see if other victims have reported it in connection with ransomware, sextortion, or investment scams.

### 4. Handling API Rate Limits and Proxies
A significant challenge in automated OSINT is getting blocked by the platforms you are querying.
*   **Proxy Integration:** To avoid IP bans, SpiderFoot can be configured to route its active scanning modules through a pool of rotating proxies (e.g., Tor or commercial proxy networks).
*   **Rate Limit Throttling:** If a module queries an API too quickly (e.g., the GitHub API, which has strict rate limits), the API will return a HTTP 429 Too Many Requests error. SpiderFoot handles this natively by queuing the requests and adhering to the `Retry-After` headers provided by the service.

## Limitations and False Positives
*   **The Shared Hosting Conundrum:** If a target domain is hosted on Cloudflare or a shared GoDaddy server, SpiderFoot's IP modules will identify thousands of other domains hosted on that same IP. Analysts must configure SpiderFoot to stop pivoting on shared infrastructure, or the scan will run indefinitely and return useless noise.
*   **Data Staleness:** WHOIS databases and historical DNS records often contain outdated information. A domain that previously belonged to a malicious actor might now be parked or owned by a legitimate entity. Automated tools cannot easily discern context; human verification is always required.

## Chaining Opportunities
*   Data extracted from SpiderFoot (like a list of associated IP addresses or ASNs) can be fed into the methodologies discussed in [[11 - Geolocation and Tracking Threat Actors]] to determine the physical location of the infrastructure.
*   The raw CSV exports from SpiderFoot scans are ideal for importing directly into [[12 - Utilizing Maltego for Infrastructure Graphing]] to create human-readable visual relationship maps.
*   When conducting reconnaissance against malicious infrastructure, SpiderFoot's automated sub-domain discovery can rapidly identify hidden endpoints crucial for [[14 - Identifying Command and Control C2 Servers via OSINT]].

## Related Notes
*   [[11 - Geolocation and Tracking Threat Actors]]
*   [[12 - Utilizing Maltego for Infrastructure Graphing]]
*   [[14 - Identifying Command and Control C2 Servers via OSINT]]
*   [[15 - OSINT OPSEC Preventing Counter-Intelligence]]
