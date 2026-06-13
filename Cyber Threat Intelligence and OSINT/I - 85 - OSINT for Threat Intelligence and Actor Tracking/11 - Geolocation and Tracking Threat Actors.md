---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.11 Geolocation and Tracking Threat Actors"
---

# 11 - Geolocation and Tracking Threat Actors

## Introduction

Tracking threat actors and geolocating their infrastructure or physical location is one of the most complex, high-stakes tasks within Cyber Threat Intelligence (CTI) and Open Source Intelligence (OSINT). Geolocation encompasses the identification of the real-world geographic location of a computer, mobile device, or the threat actor themselves. The discipline blends digital forensics, network analysis, imagery intelligence (IMINT), and behavioral profiling. Advanced Threat Actors (APTs) often employ robust Operations Security (OPSEC), utilizing multi-layered proxies, Tor networks, Bulletproof Hosting (BPH), and Virtual Private Networks (VPNs). Breaking through these layers requires a meticulously structured analytical approach.

To accurately locate an adversary, analysts must pivot off metadata, leverage third-party datasets, utilize telemetry from public internet scanners, and occasionally exploit OPSEC failures. Small mistakes—like an exposed timezone in a Git commit, a language pack in a malware binary, or a reflection in a photograph—can unravel an entire operation.

## Core Concepts of Geolocation and Actor Tracking

### 1. Network-Based Geolocation
Network geolocation relies on identifying the physical location of IP addresses, Autonomous System Numbers (ASNs), and domain infrastructure.
*   **IP Intelligence:** While standard IP geolocation databases (like MaxMind or IP2Location) are highly inaccurate for precise targeting, they provide baseline continental or country-level routing information.
*   **Latency Analysis (Triangulation):** By sending ICMP echo requests (pings) from multiple globally distributed vantage points, analysts can triangulate a server's physical location based on round-trip time (RTT). Speed-of-light constraints in fiber optics dictate that latency correlates with physical distance.
*   **BGP Routing Analysis:** Analyzing Border Gateway Protocol (BGP) routing tables to determine how data flows to a specific subnet, uncovering the true upstream providers behind bulletproof hosts.

### 2. Behavioral and Temporal Geolocation
Threat actors are human and are bound by human physiological needs, specifically sleep.
*   **Pattern of Life (PoL) Analysis:** By analyzing the timestamps of forum posts, code commits (GitHub/GitLab), malware compilation times, and server interaction logs, analysts can build a behavioral profile.
*   **Working Hours:** Aggregating activity logs often reveals a standard 9-to-5 working pattern in a specific timezone, or a distinct sleep cycle, which narrows down the geographic region of the operator.
*   **Linguistic Anomalies:** Use of specific regional slang, distinct keyboard layouts (like Cyrillic or QWERTZ), and localized date formats can betray an actor's native region.

### 3. Image and Media Intelligence (IMINT)
When threat actors post screenshots or photos (e.g., bragging on underground forums or dark web marketplaces), IMINT comes into play.
*   **EXIF Data:** Extraction of GPS coordinates, device models, and software versions from the metadata of unscrubbed images.
*   **Visual Chronolocation and Geolocation:** Identifying landmarks, street signs, weather patterns, sun shadows, and architectural styles to pinpoint the exact location an image was captured.

## Technical Architecture of Tracking

```text
+---------------------------------------------------------------------------------------+
|                       Threat Actor Tracking and Geolocation Flow                        |
+---------------------------------------------------------------------------------------+
|                                                                                       |
|   [Threat Actor]                                                                      |
|         |                                                                             |
|         |-- (OPSEC Failures / Artifacts)                                              |
|         v                                                                             |
|  +--------------------+    +--------------------+    +--------------------+           |
|  | Network Indicators |    | Digital Artifacts  |    | Behavioral Profile |           |
|  | - IP Addresses     |    | - PGP Keys         |    | - Activity Times   |           |
|  | - Domains / DNS    |    | - Code Repos       |    | - Forum Posts      |           |
|  | - TLS Certificates |    | - Mutexes / PDBs   |    | - Language / Slang |           |
|  +---------+----------+    +---------+----------+    +---------+----------+           |
|            |                         |                         |                      |
|            v                         v                         v                      |
|  +------------------------------------------------------------------------+           |
|  |                 Data Aggregation and Enrichment Layer                  |           |
|  |  [Shodan/Censys]   [RiskIQ/PassiveTotal]   [Maltego]   [OSINT Framework] |           |
|  +-----------------------------------+------------------------------------+           |
|                                      |                                                |
|                                      v                                                |
|  +------------------------------------------------------------------------+           |
|  |                       Correlation & Analysis                           |           |
|  |  1. Infrastructure Triangulation (Latency / BGP)                       |           |
|  |  2. Metadata Extraction (EXIF / Timezones)                             |           |
|  |  3. Pattern of Life (PoL) Mapping                                      |           |
|  +-----------------------------------+------------------------------------+           |
|                                      |                                                |
|                                      v                                                |
|                          [Geographic Attribution]                                     |
+---------------------------------------------------------------------------------------+
```

## Tooling and Techniques

### 1. Censys and Shodan for Infrastructure Tracking
When an actor provisions a Command and Control (C2) server, they often reuse TLS certificates or SSH host keys across different deployments.
*   **Pivoting on SSH Host Keys:** If a threat actor misconfigures their deployment script, multiple servers may share the same SSH fingerprint.
*   **TLS Certificate JARM/JA3:** Fingerprinting the TLS handshake of a C2 server and querying Shodan/Censys for other IPs on the internet exhibiting the exact same fingerprint.

### 2. Timezone and Telemetry Analysis Tools
*   **GitFiti / GitHub Commit History:** Extracting the exact commit timestamps from public or leaked repositories belonging to the actor.
*   **ExifTool:** The standard utility for deep inspection of image, audio, and video metadata.

### 3. Open Source Intelligence (OSINT) Platforms
*   **Bellingcat's OSINT Toolkit:** A collection of tools for IMINT, chronolocation, and mapping.
*   **Epieos:** A tool to determine if an email address is registered to Google Services, Skype, or other platforms, often revealing Google Maps reviews or associated names.

## Real-World Attack Scenario

### The Hunt for "ShadowBroker22"
A ransomware affiliate, operating under the alias "ShadowBroker22", was highly active on a popular darknet forum. They claimed to be based in an untouchable jurisdiction, routing all communications through Tor and multiple proxy chains. 

**The OPSEC Failure:**
ShadowBroker22 posted a screenshot of a compromised Active Directory environment to prove their access to potential buyers. While they meticulously blurred the usernames and domain names, they failed to account for two minor details in the Windows taskbar:
1.  The system time was visible.
2.  A highly specific, custom weather widget was running in the system tray, showing "Partly Cloudy, 18°C".

**The Geolocation Process:**
1.  **Temporal Analysis:** The forum post timestamp was `14:32 UTC`. The system time in the screenshot was `17:32`. This indicated a `UTC+3` timezone.
2.  **Meteorological Correlation:** Analysts cross-referenced historical weather data for all major cities in the `UTC+3` timezone (which includes parts of Eastern Europe, the Middle East, and East Africa) that reported exactly 18°C and partly cloudy conditions at that specific time.
3.  **Linguistic Pivoting:** Previous forum posts by the actor used specific colloquialisms that heavily suggested a native Russian speaker.
4.  **Narrowing Down:** Combining the timezone (`UTC+3`), the language (Russian), and the highly specific weather data, the analysts pinpointed the location to a specific suburb of Saint Petersburg, Russia.
5.  **Infrastructure Correlation:** Simultaneous monitoring of known proxy exit nodes communicating with the compromised victim network showed a spike in encrypted traffic originating from a residential ISP in Saint Petersburg exactly during the time the actor claimed to be exfiltrating data.

This convergence of IMINT, temporal analysis, and network forensics successfully geolocated the threat actor without needing to crack their Tor encryption.

## Detailed Methodology: Step-by-Step Actor Tracking

### Step 1: Collection of Digital Exhaust
Gather every single digital artifact associated with the actor. This includes:
*   Email addresses, usernames, and aliases.
*   Cryptocurrency wallet addresses.
*   Compiled malware samples (specifically looking for Rich Header data, PDB paths, and compilation timestamps).
*   Public forum posts, tweets, or chat logs.

### Step 2: Pattern of Life (PoL) Generation
Map all collected timestamps to a unified timeline.
*   Convert all timestamps to UTC.
*   Plot the data on a 24-hour scatter plot or heat map.
*   Identify the "sleep window" (the contiguous 6-8 hour block with zero activity). Assuming standard human behavior, this window generally falls between 23:00 and 07:00 local time. This provides the actor's likely timezone.

### Step 3: Infrastructure Pivoting
Analyze the actor's known infrastructure (IPs, Domains).
*   Identify the hosting provider. Is it a known bulletproof hoster?
*   Use `whois` historical records to find the original registrant details before domain privacy was enacted.
*   Query Passive DNS (pDNS) databases (like RiskIQ or SecurityTrails) to find other domains hosted on the same IP.

### Step 4: Linguistic and Cultural Analysis
Analyze the text written by the actor.
*   Look for idioms, slang, or grammatical errors specific to non-native speakers of a language.
*   Analyze the spelling conventions (e.g., "color" vs "colour").
*   Check for cultural references or adherence to specific regional holidays (noting periods of unexpected inactivity during regional festivals).

### Step 5: Correlation and De-anonymization
Combine the geographic clues from PoL, infrastructure, and linguistics to form a hypothesis. Use tools like Maltego to visualize the connections and identify the central nodes that tie the digital persona to a physical identity or location.

## OPSEC and Considerations for the Analyst
When tracking advanced actors, analysts must practice rigorous OPSEC themselves.
*   **Never query actor infrastructure directly** from your personal or corporate IP address.
*   Always use non-attributable, disposable virtual machines connected via Tor or premium commercial VPNs.
*   Be aware of **Canary Tokens** or tracking pixels embedded in leaked documents or forum posts designed to de-anonymize researchers.

## Advanced Tracking Techniques: The Dark Web and Cryptocurrencies

### 1. Cryptographic Tracing (Blockchain Forensics)
When an actor operates a ransomware franchise or sells data on the dark web, they leave a financial trail on the blockchain.
*   **Wallet Clustering:** Threat actors rarely use a single Bitcoin address for all transactions. They generate new addresses for every victim. However, when cashing out, they must consolidate these funds. Blockchain analysis tools (like Chainalysis or Elliptic) monitor the ledger to cluster associated addresses based on co-spending behaviors (spending from multiple addresses in a single transaction).
*   **Exchange De-anonymization:** The ultimate goal of tracking crypto is to follow the funds to a "fiat off-ramp"—a centralized exchange where the actor converts crypto to traditional currency. These exchanges enforce Know Your Customer (KYC) regulations. While analysts cannot directly access KYC data, law enforcement can subpoena the exchange once the analyst provides the destination wallet address.
*   **Peel Chains:** A common money laundering technique where a large amount of cryptocurrency is passed through a series of wallets. At each step, a small amount is "peeled" off and sent to an exchange or a mixer, while the remainder continues down the chain. Recognizing the mathematical patterns of a peel chain allows analysts to track the funds despite the obfuscation attempts.

### 2. Dark Web Persona Infiltration
Sometimes passive geolocation is insufficient, requiring direct interaction with the actor.
*   **Forum Access:** Gaining access to tier-1 Russian cybercrime forums (like Exploit or XSS) requires significant financial investment (deposits) and vetting by existing members.
*   **Language Nuances:** When operating a sock puppet on these forums, using Google Translate is a guaranteed way to be identified as an outsider. Analysts must understand specific underground slang (e.g., using "drops" instead of "money mules", or "logs" for compromised credentials).
*   **Social Engineering the Actor:** Once a dialogue is established, analysts may attempt to send a weaponized document (a Canary Token) disguised as a "valuable target's network map" or a "proof of concept exploit." If the actor opens it outside of a secure sandbox, their true IP address is revealed to the analyst.

### 3. Exploiting Actor Misconfigurations
Threat actors frequently make mistakes when deploying their own infrastructure.
*   **Open Directories:** Actors often host malware payloads or exfiltrated data on hastily configured VPS instances. Sometimes, they forget to disable directory listing (e.g., `Options -Indexes` in Apache). Scanning these open directories can reveal bash history files (`.bash_history`), SSH keys, or configuration scripts that contain hardcoded IP addresses connecting back to their home network.
*   **Development Artifacts:** When compiling custom malware, actors may forget to strip debugging symbols. The resulting `.pdb` (Program Database) paths embedded in the binary often contain the exact directory structure of the actor's local machine, sometimes revealing their actual username (e.g., `C:\Users\Ivan\Desktop\Ransomware_v2\release.pdb`).

## Operational Security for the Threat Hunter
Tracking sophisticated adversaries places the analyst in the crosshairs.
*   **Deconfliction:** Before aggressively pursuing a high-profile actor, CTI teams must ensure they are not interfering with an ongoing law enforcement operation.
*   **The "Burn" Protocol:** If an analyst suspects their sock puppet or investigative infrastructure has been identified by the target, they must immediately initiate a burn protocol. This involves destroying all associated virtual machines, rotating VPN endpoints, abandoning the sock puppet, and ensuring no technical links connect the burned persona to the analyst's real identity.
*   **Data Handling:** All data exfiltrated from the dark web or actor infrastructure must be stored in encrypted, isolated enclaves. Malware samples should only be analyzed in strictly air-gapped sandboxes.

## Chaining Opportunities
*   Geolocating an actor's C2 server can be chained with [[14 - Identifying Command and Control C2 Servers via OSINT]] to map the entire backend architecture.
*   Extracted aliases and emails from tracking efforts can be ingested into [[13 - SpiderFoot and Automating OSINT Gathering]] for automated deep-web scraping.
*   The raw data collected during geolocation must be visualized and structured using [[12 - Utilizing Maltego for Infrastructure Graphing]].

## Related Notes
*   [[12 - Utilizing Maltego for Infrastructure Graphing]]
*   [[13 - SpiderFoot and Automating OSINT Gathering]]
*   [[14 - Identifying Command and Control C2 Servers via OSINT]]
*   [[15 - OSINT OPSEC Preventing Counter-Intelligence]]
