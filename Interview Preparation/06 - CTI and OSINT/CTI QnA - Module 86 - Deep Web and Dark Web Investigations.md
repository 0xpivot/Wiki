---
tags: [interview, cti, osint, qna, scenario]
difficulty: expert
module: "Interview Prep - CTI and OSINT"
topic: "QnA - CTI Module 86"
---

# Deep Web and Dark Web Investigations

## Custom ASCII Diagram: Dark Web Investigation Architecture
```text
[Tor Network]                       [Investigation Environment]
      |                                        |
      v                                        v
+-----------+    Routing      +----------------------------------+
| Onion     | <-------------> | Whonix Workstation (Isolated)    |
| Services  |                 |  - Tor Browser / Proxychains     |
| (v3)      |                 |  - Scraping Scripts (Python)     |
+-----------+                 +----------------------------------+
      ^                                        | (VLAN / Host-Only)
      |                                        v
+-----------+                 +----------------------------------+
| I2P /     | <-------------> | Whonix Gateway (Tor Router)      |
| Freenet   |                 |  - Forces all traffic through Tor|
+-----------+                 +----------------------------------+
                                       |
                                       v
                             [Strict VPN / VPS Exit Node]
```

## Formal Technical Questions

**Q1: Explain the technical differences between the Surface Web, Deep Web, and Dark Web, and detail the underlying cryptography that enables Tor v3 onion services.**
**A:** 
- **Surface Web:** Content indexed by standard search engines (Google, Bing).
- **Deep Web:** Unindexed content requiring authentication, direct links, or payment walls (e.g., banking portals, corporate intranets, private databases).
- **Dark Web:** A subset of the Deep Web requiring specific software or protocols (Tor, I2P, Freenet) to access, designed for anonymity.
- **Tor v3 Cryptography:** Tor version 3 significantly upgraded the cryptography of onion services. v3 addresses are 56 characters long (base32 encoded) and represent the entire Ed25519 public key. This prevents directory nodes from enumerating hidden services (a flaw in v2). It utilizes SHA3-256 for hashing and curve25519 for key exchange. The hidden service creates "introduction points" on the Tor network and publishes their descriptors to a distributed hash table (DHT). Clients download the descriptor, connect to a "rendezvous point," and establish an end-to-end encrypted circuit.

**Q2: What is "Deanonymization" in the context of Dark Web investigations, and what are the primary techniques used by intelligence agencies and CTI analysts to achieve it?**
**A:** Deanonymization is the process of stripping the anonymity provided by networks like Tor to identify the true IP address or identity of an operator or user.
- **Techniques:**
  - **Traffic Correlation (Global Passive Adversary):** If an adversary controls or monitors both the entry node and the exit node (or the hidden service itself), they can correlate packet timing and sizes to link the Tor user to the destination.
  - **Browser Fingerprinting & Exploitation:** Using zero-day exploits against the Tor Browser (often based on Firefox) to execute JavaScript/WebAssembly that forces the underlying OS to beacon out its true IP address directly to the internet, bypassing the Tor proxy.
  - **OPSEC Failures (The most common CTI method):** Finding metadata in uploaded images (EXIF data), identifying reused usernames/emails on the surface web, tracking Bitcoin transactions from darknet markets to surface-level exchanges (KYC/AML bypass failures), or analyzing server misconfigurations where a hidden service accidentally exposes its true IP via an open status page (e.g., Apache `mod_status`).

**Q3: Detail the process of conducting a safe and secure investigation on the Dark Web. What are the critical OPSEC requirements for a CTI analyst?**
**A:** 
- **Environment:** Never use a personal or standard corporate machine. Use a dedicated virtualized environment, ideally Qubes OS or a Whonix setup (Gateway + Workstation) to ensure all traffic is forced through Tor and DNS leaks are impossible.
- **Persona Management:** Create dedicated sockpuppet accounts. Never mix personas. Use unique, generated passwords and PGP keys for each identity. Do not use surface web emails for dark web registration; use services like ProtonMail via Tor or SecMail.
- **Behavioral OPSEC:** Disable JavaScript in the Tor browser unless absolutely necessary (and then only temporarily). Do not download files directly to the host; if a file must be downloaded, analyze it in an isolated sandbox with no network connection, as documents (PDFs, Word) often contain beacons that call back via the clearnet.
- **Infrastructure:** Route the host machine through a trusted VPN before connecting to Tor, hiding the Tor usage from the local ISP.

## Scenario-Based Questions

**Scenario 1: You discover a database dump containing your organization's customer data being sold on a popular Tor-based forum. The seller goes by the handle "PhantomByte." Walk me through your investigation steps to ascertain the validity of the threat and profile the seller.**
**A:** 
1. **Verification (Data Sampling):** I will not immediately purchase the dump. Instead, I will look for the "proof" or sample data usually provided by sellers. I will cross-reference this sample against our internal databases to verify its authenticity, age, and scope. This determines the severity of the incident.
2. **Actor Profiling (Forum History):** I will search the forum for "PhantomByte's" post history. Are they a known Initial Access Broker (IAB)? Do they have high reputation/escrow stats? This helps determine if they are the actual hacker or just a reseller.
3. **Cross-Forum Correlation:** I'll use tools like DarkOwl or specialized scraping databases to search for "PhantomByte" across other defunct and active forums (e.g., RaidForums, BreachForums, XSS). 
4. **Communication & PGP:** I will extract their PGP public key from their profile. Analyzing the key creation date can indicate how long this persona has been active. I will also search the key fingerprint on the surface web.
5. **Financial Tracking:** If they list a Bitcoin or Monero address for direct contact/purchase, I will log it for blockchain analysis, looking for interactions with known threat groups or mixing services.

**Scenario 2: An executive is being extorted via email. The attacker provided a custom `.onion` link containing a countdown timer and a chat interface for negotiation. How do you analyze this hidden service without tipping off the attacker?**
**A:** 
1. **Isolated Access:** I will access the `.onion` link strictly via a Whonix environment. I will not use the chat interface or engage with the threat actor initially.
2. **Source Code & Network Analysis:** I will inspect the HTML source code, JavaScript, and CSS of the site. I am looking for cloned templates, identifying comments, or unique backend frameworks. Ransomware groups (like LockBit or ALPHV) use standardized negotiation portals. Identifying the framework attributes the attack to a specific RaaS (Ransomware-as-a-Service) family.
3. **Misconfiguration Hunting:** I will aggressively but quietly scan the `.onion` address using Tor-aware tools (e.g., `proxychains nmap`). I'm looking for exposed SSH, database ports, or server status pages (`/server-status`) that might leak the true backend IP address of the server.
4. **Metadata Extraction:** If there are images (e.g., proof of stolen data) hosted on the site, I will download them via the Tor circuit and analyze them offline for EXIF data or steganographic payloads.

## Deep-Dive Defensive Questions

**Q1: What are the risks of "Active Engagement" (undercover interaction) with threat actors on the Dark Web, and what are the legal and ethical boundaries a CTI team must adhere to?**
**A:** 
- **Risks:** 
  - **Burned Persona:** The actor discovers the analyst's true identity or corporate affiliation, leading to retaliation (e.g., targeted DDoS or doxxing).
  - **Malware Exposure:** Receiving files during negotiation that compromise the analyst's environment.
  - **Entrapment/Tipping Off:** Spooking the actor, causing them to destroy evidence, leak the data immediately, or vanish before law enforcement can act.
- **Legal/Ethical Boundaries:** Analysts must operate under strict Rules of Engagement (ROE). They must avoid "hacking back" or performing unauthorized exploitation of the actor's infrastructure. They must not provide material support to terrorists or sanctioned entities (e.g., paying a ransom to a sanctioned group violates OFAC regulations). Coordination with legal counsel and law enforcement is critical before engaging.

**Q2: How can blockchain analysis be integrated into Dark Web investigations to track the financial operations of ransomware affiliates?**
**A:** 
- **Clustering Heuristics:** Analysts use tools like Chainalysis or Elliptic to track Bitcoin flows. They use heuristics like "Common-Input-Ownership" (if multiple addresses are used as inputs in a single transaction, they are assumed to be owned by the same entity) to cluster thousands of addresses into a single wallet representing the affiliate.
- **Chaser/Peel Chains:** Tracking funds as they move through a "peel chain" (a long series of transactions where a small amount is peeled off and the rest is sent to a new change address) to obfuscate the origin.
- **Deanonymization via Exchanges:** The ultimate goal is to track the funds from the Dark Web forum/ransom payment to a surface-level cryptocurrency exchange (e.g., Binance, Coinbase). Once the funds hit an exchange, law enforcement can subpoena the exchange for the KYC (Know Your Customer) data, revealing the affiliate's real-world identity.

## Real-World Attack Scenario
**The Takedown of AlphaBay**
AlphaBay was one of the largest darknet markets. Its deanonymization relied entirely on classic OPSEC failures rather than breaking Tor's cryptography.
- **The OPSEC Failure:** The creator, Alexandre Cazes, used his personal email address (`Pimp_Alex_91@hotmail.com`) in the welcome email sent to new users when the site first launched.
- **The Investigation:** Law enforcement correlated this surface-level email to his real identity. They then tracked his cryptocurrency wealth, noting that he was purchasing luxury cars and real estate in Thailand without a legitimate source of income. 
- **The Takedown:** By mapping his physical location, international law enforcement coordinated an arrest. Crucially, they arrested him while his laptop was open, logged in, and unencrypted as the site administrator, securing the servers and the master cryptographic keys before they could be locked down.

## Chaining Opportunities
- **Dark Web to Blockchain Analytics:** Extracting a cryptocurrency address from a dark web extortion portal (Module 86) and using blockchain heuristics to trace the funds to a centralized exchange for deanonymization.
- **Dark Web Scraping to Threat Intel Feeds:** Automating the collection of compromised credentials from dark web forums and directly feeding them into an organization's SIEM to trigger password resets (Module 87).

## Related Notes
- [[CTI QnA - Module 85 - OSINT for Threat Intelligence and Actor Tracking]]
- [[CTI QnA - Module 87 - Automated Dark Web Monitoring and Scraping]]
- [[Tor Network Architecture and Cryptography]]
- [[Cryptocurrency Tracing Methodologies]]
