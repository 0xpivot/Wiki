---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.04 RiskIQ PassiveTotal and Passive DNS"
---

# 04 - RiskIQ PassiveTotal and Passive DNS

## Introduction

Passive DNS (pDNS) is arguably one of the most powerful and fundamental concepts in modern Cyber Threat Intelligence (CTI). While active DNS queries ask a nameserver "What IP does this domain point to *right now*?", Passive DNS asks the historical question, "What IPs has this domain *ever* pointed to, and what other domains have *ever* pointed to this IP?" Platforms like RiskIQ PassiveTotal (now heavily integrated into Microsoft Defender Threat Intelligence) aggregate, store, index, and correlate massive volumes of historical DNS resolution data.

For a CTI analyst, pDNS provides a literal "time machine" for internet infrastructure. Threat actors frequently rotate domains and IP addresses to evade blocklists, relying heavily on dynamic DNS or rapid infrastructure provisioning. By analyzing the historical resolutions of a known malicious domain or IP, analysts can map out the actor's broader infrastructure, identify historical campaigns, and uncover hidden connections between seemingly disparate attacks.

## Core Concepts of Passive DNS

### How Passive DNS Data is Collected

Passive DNS databases do not actively scan the internet like Shodan or Censys. Instead, they rely on a vast network of sensors strategically placed above caching recursive DNS resolvers (typically operated by ISPs, large enterprises, universities, or security vendors). 

When a user initiates a DNS query (e.g., browsing to `malicious-site.com`), the local resolver checks its cache. If it does not have the answer, it queries the authoritative nameserver. The pDNS sensor silently observes this response as it travels back to the user and records the transaction in a massive database.

The data recorded typically includes:
- **Domain Name** (e.g., `malicious-login.com`)
- **IP Address** (e.g., `192.0.2.50`)
- **Record Type** (A, AAAA, CNAME, MX, TXT)
- **Time First Seen** (The very first time the sensor ever saw this resolution)
- **Time Last Seen** (The most recent time the sensor saw this resolution)

Because the collection is entirely passive, it does not alert the threat actor that their infrastructure is being monitored. They simply see normal user traffic, unaware that the DNS metadata is being logged.

### The Value of Historical Data

Threat actors often reuse infrastructure to save costs, time, and effort.
- **Domain Parking**: An actor might register `evil.com` in January, point it to an IP (`1.2.3.4`) for testing, park it for six months, and then use it in a massive phishing campaign in July on a totally new IP (`5.6.7.8`). pDNS retains the memory that `evil.com` was once associated with `1.2.3.4`.
- **IP Reuse**: If `1.2.3.4` is later discovered to be a C2 server, the analyst can query pDNS to see that `evil.com` was historically connected to it, immediately burning the `evil.com` domain and flagging it as suspicious even before it is actively used in the July campaign.

## RiskIQ PassiveTotal / Defender TI in Depth

RiskIQ PassiveTotal is a premier platform for analyzing pDNS data, but it goes far beyond simple A-record lookups. It attempts to build a comprehensive "Internet Intelligence Graph."

### Key Features and Pivot Points

1. **Passive DNS Resolutions**: The core feature. Analysts can pivot seamlessly from Domain to IP, and IP to Domain, building out a web of connectivity.
2. **WHOIS Data Tracking**: Correlates historical WHOIS registration data (see [[05 - WHOIS History and Domain Registration Reversals]]) directly with the pDNS data, allowing analysts to cross-reference IPs with the emails used to register the domains.
3. **OSINT and Threat Intel Repositories**: RiskIQ ingests open-source intel feeds. If an IP or domain is searched, it instantly flags if it has been mentioned in community reports, vendor blogs, or Twitter feeds.
4. **Host Pairs / Trackers**: A highly advanced feature. RiskIQ operates its own web crawlers that visit pages and deeply analyze the Document Object Model (DOM). It records "Trackers" (Google Analytics IDs, New Relic IDs, Facebook Pixels) and "Host Pairs" (e.g., Domain A loads a JavaScript file from Domain B). 
   - *CTI Application*: Threat actors running massive phishing networks often reuse the exact same Google Analytics ID across hundreds of different phishing domains to track the "success" and click-through rates of their campaigns. Pivoting on a malicious Tracker ID can instantly reveal the entire phishing network, regardless of what IP they are hosted on.

## Methodology: Infrastructure Expansion

The process of using pDNS to map adversary infrastructure is often called "Infrastructure Expansion" or "Pivoting." It requires careful analysis to avoid "pollution" or false positives.

1. **Start with an Indicator**: You have a known bad IP address (`203.0.113.10`) provided by the SOC.
2. **Query pDNS for the IP**: You ask PassiveTotal: "What domains have resolved to `203.0.113.10`?"
3. **Analyze Results**: PassiveTotal returns two domains: `phish-paypal.com` and `secure-login-update.net`.
4. **Pivot**: You now query pDNS for `secure-login-update.net`.
5. **Expand**: PassiveTotal shows that prior to pointing to the initial IP, `secure-login-update.net` pointed to `198.51.100.22` three months ago.
6. **Iterate**: You now query the new IP (`198.51.100.22`) and find five completely new domains.
7. **Filter Noise**: This is critical. Analysts must be careful to filter out "sinkholes" (IPs operated by security companies like Microsoft or Shadowserver to capture malicious traffic). If a domain points to a sinkhole, you cannot pivot on that sinkhole IP, as it will return millions of unrelated malicious domains. Similarly, shared hosting IPs (like those owned by GoDaddy or Cloudflare) will return thousands of legitimate domains sharing an IP with one malicious domain.

## Real-World Attack Scenario

### Scenario: Uncovering a Phishing Campaign via Tracker IDs

1. **Initial Phish**: Employees receive a targeted phishing email directing them to `portal-microsoft-auth[.]com`.
2. **Analysis**: The incident response team analyzes the domain. It resolves to a bulletproof hosting IP in Russia. The attack is mitigated locally.
3. **RiskIQ Investigation**: A CTI analyst enters `portal-microsoft-auth[.]com` into PassiveTotal. The pDNS data shows it was recently registered and points to an isolated IP. The standard pDNS pivot yields nothing new.
4. **Tracker Pivot**: The analyst checks the "Trackers" tab in PassiveTotal for that domain. They discover the domain incorporates a specific Jexscia analytics script with the ID `UA-98765432-1`. (The actor, treating the phishing campaign like a marketing campaign, wants to track how many victims click the link).
5. **Expansion**: The analyst pivots on the ID `UA-98765432-1` within PassiveTotal. The query asks: "What other domains on the entire internet contain this specific tracker ID?"
6. **Discovery**: PassiveTotal returns a list of 45 other domains, all registered in the last two weeks, utilizing variations of corporate brands (e.g., `okta-sso-verify[.]net`, `docusign-auth-req[.]com`, `hr-portal-login[.]org`). 
7. **Action**: The analyst has preemptively uncovered the actor's entire upcoming phishing infrastructure, allowing the organization to block all 45 domains at the firewall before the associated emails are even sent.

## ASCII Diagram: Passive DNS Pivoting

```text
                                Time t=0 (January)                     Time t=1 (June)
                                ------------------                     ---------------

    Actor Registers:      [ evil-c2.com ]                        [ evil-c2.com ]
                                 |                                      |
                                 V                                      V
    DNS Points to:        [ IP: 1.2.3.4 ]  (Test Server)         [ IP: 5.6.7.8 ] (Active Campaign)
                                 |
                                 V
    Later, Actor          [ phish.com ]
    re-uses IP:                  |
                                 V
                          [ IP: 1.2.3.4 ]

    ================================================================================================

    CTI Analyst Process (In June):

    1. Discovers active campaign:      [ IP: 5.6.7.8 ]
                                             |
    2. Queries pDNS (PassiveTotal):          V
       "What domains point here?"      [ evil-c2.com ]
                                             |
    3. Queries pDNS:                         V
       "Where has this domain          [ IP: 1.2.3.4 ]  <-- Uncovers Historical IP
       pointed previously?"                  |
                                             V
    4. Queries pDNS:                   [ phish.com ]    <-- Uncovers new Malicious Domain
       "What else points here?"                             associated with the same actor.
```

## Challenges and Limitations

- **Fast Flux DNS**: Advanced botnets use Fast Flux, constantly rotating the IP address associated with a domain (sometimes every few minutes) using a network of compromised consumer hosts. This generates massive amounts of pDNS noise, making traditional pivoting difficult and requiring algorithmic analysis to group the flux networks.
- **Shared Infrastructure**: As mentioned, if an actor hosts their malicious site on AWS, Cloudflare, Fastly, or a massive shared hosting provider, pivoting on the IP address will return thousands of legitimate domains. Analysts must recognize shared IP space and avoid pivoting on it to prevent analyzing false positives.
- **Data Completeness**: pDNS relies entirely on sensor placement. If an actor's infrastructure is strictly targeted and only queried by a handful of victims whose ISPs do not share data with the pDNS provider, those resolutions will not be recorded, leaving a blind spot.

## Chaining Opportunities

- Domains discovered during pDNS pivoting in PassiveTotal are prime candidates for historical registration analysis using [[05 - WHOIS History and Domain Registration Reversals]]. Correlating a pDNS domain to an actor's email is a massive intelligence win.
- IPs discovered via pDNS can be actively scanned using [[03 - Shodan and Censys for Tracking Threat Infrastructure]] to identify the specific C2 software, open ports, or vulnerabilities running on those historical servers.
- Dorking the newly discovered domains from pDNS using [[01 - Advanced Search Engine Dorking for Threat Intel]] might reveal exposed directories, backup files, or actor mistakes on the new infrastructure.

## Related Notes
- [[01 - Advanced Search Engine Dorking for Threat Intel]]
- [[03 - Shodan and Censys for Tracking Threat Infrastructure]]
- [[05 - WHOIS History and Domain Registration Reversals]]

