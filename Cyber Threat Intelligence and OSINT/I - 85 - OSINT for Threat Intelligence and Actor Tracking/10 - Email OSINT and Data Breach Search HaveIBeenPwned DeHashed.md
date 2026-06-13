---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.10 Email OSINT and Data Breach Search HaveIBeenPwned DeHashed"
---

# 85.10 Email OSINT and Data Breach Search HaveIBeenPwned DeHashed

## Introduction to Email OSINT and Breach Data

Email addresses are the universal unique identifiers of the digital age. Almost every service, social media platform, forum, and banking application requires an email address for registration. For a Cyber Threat Intelligence (CTI) analyst, an email address is often the holy grail of pivoting. It bridges the gap between technical infrastructure (domains, IPs) and the human Threat Actor (TA).

Email OSINT involves analyzing an email address to discover linked accounts, true identities, and organizational affiliations. This process is supercharged by the existence of Data Breach Databases—massive repositories of compromised data collected from thousands of hacked websites over the past two decades. By querying an email address against these databases, analysts can uncover historical passwords, which often leads to identifying the TA's activities across different underground forums.

## The Value of Email Addresses in CTI

1. **Infrastructure Pivoting (WHOIS):** Historically, registering a domain required providing a real email address to the WHOIS database. While privacy protections (like GDPR) have masked much of this, historical WHOIS records still exist. If an analyst finds the email used to register a malicious C2 domain in 2015, that email can be tracked.
2. **Identifying TA Personas:** TAs often compartmentalize their lives, but laziness prevails. A TA might use `hacker_guy99@protonmail.com` for their cybercrime activities, but accidentally use the same password or recovery email linked to their personal `john.smith@gmail.com` account.
3. **Corporate Attack Surface (Defensive CTI):** Analysts use email OSINT to find exposed corporate credentials. If a company executive's work email is found in a recent breach with a cleartext password, the organization is at immediate risk of a targeted phishing or credential stuffing attack.

## Exploring Data Breach Databases

### 1. Have I Been Pwned (HIBP)
Created by Troy Hunt, HIBP is the industry standard for safe breach verification. 
- **Capabilities:** Allows searching by email or phone number to see *which* breaches the identifier was involved in. It does NOT provide the leaked passwords.
- **API Use:** Highly useful for automated corporate monitoring. Organizations can verify their entire domain to receive alerts when employee emails appear in new breaches.

### 2. DeHashed
DeHashed is an incredibly powerful, commercial data breach search engine built specifically for CTI and security professionals.
- **Capabilities:** Unlike HIBP, DeHashed provides the raw breached data, including cleartext passwords, cracked hashes, names, IP addresses, and physical addresses.
- **Advanced Pivoting:** An analyst can search for a specific password (e.g., `DarkL0rd!2020`) and find every other email address globally that has used that exact password, often revealing a TA's alternate identities.

### 3. Other Notable Databases
- **IntelligenceX (intelx.io):** An archival search engine that searches the dark web, document sharing platforms, and historical breach data simultaneously. Excellent for finding raw paste dumps containing the target email.
- **Leak-Lookup / Snusbase / BreachDirectory:** Alternative databases that offer varying datasets and pricing models, often containing specialized gaming forum or underground forum breaches.

## Email Verification and Enumeration Techniques

Before spending hours researching an email, analysts must verify if it actually exists.

### SMTP Verification
Analysts can manually interact with a mail server to verify an inbox without sending an email.
```bash
$ nc mx1.targetdomain.com 25
HELO targetdomain.com
MAIL FROM:<test@example.com>
RCPT TO:<target.user@targetdomain.com>
# A 250 OK response usually indicates the inbox exists.
# A 550 response means it does not.
```
*Note: Many modern mail servers disable VRFY/EXPN commands and use "catch-all" configurations, making this technique less reliable today.*

### OSINT Enumeration Tools
1. **Holehe:** A phenomenal Python tool that checks if an email is attached to an account on over 120 sites (Twitter, Instagram, Imgur, Github, etc.). It achieves this by exploiting the "forgot password" or registration functions of these sites without alerting the target.
2. **GHunt:** A specialized OSINT tool for extracting information from Google Accounts using only an email address. It can reveal the user's name, Google Maps reviews, YouTube channel, and occasionally their physical location.
3. **Epieos:** A web-based tool that automates Holehe and GHunt functionalities, providing a clean visual report of where an email is registered.

## Real-World Attack Scenario

### De-anonymizing a Threat Actor via Password Reuse

**The Setup:**
A CTI analyst is tracking a ransomware operator. Through reverse engineering the malware, they find a hardcoded recovery email address: `crypt0_k1ng@protonmail.com`.

**The Investigation:**
1. The analyst queries `crypt0_k1ng@protonmail.com` in Holehe and finds it is registered to a Twitter account, but the account is locked and provides no intel.
2. The analyst searches the email in DeHashed. The email appears in a 2018 breach of a specialized underground carding forum. The breach record reveals the cleartext password used by the TA: `P@ssw0rd_K1ng_99!`.
3. Recognizing this as a highly specific password, the analyst pivots. They run a reverse search in DeHashed for the exact password string `P@ssw0rd_K1ng_99!`.
4. The search returns one other result: the email `david.miller.1992@yahoo.com`, which was compromised in a massive LinkedIn breach in 2012.
5. The analyst uses standard SOCMINT techniques on `david.miller.1992@yahoo.com`, uncovering a public Facebook profile, real location, and employer, successfully correlating the anonymous ransomware operator to a real-world identity due to their failure to practice password hygiene across a decade.

## Architecture & Investigation Flow Diagram

```text
+-----------------------+
|  Initial Indicator    |
|  crypt0_k1ng@         |
|  protonmail.com       |
+-----------+-----------+
            |
            | 1. Query Breach Database (DeHashed)
            v
+-----------------------+       +------------------------+
|  Breach Record        |       |   Extracted Password   |
|  (Carding Forum 2018) |------>|   "P@ssw0rd_K1ng_99!"  |
+-----------+-----------+       +-----------+------------+
                                            |
                                            | 2. Reverse Pivot on Password
                                            v
                                +------------------------+
                                |  Secondary Email       |
                                |  david.miller.1992@    |
                                |  yahoo.com             |
                                +-----------+------------+
                                            |
            +-------------------------------+
            | 3. OSINT / Enumeration (GHunt / Facebook)
            v
+-----------------------+
|  Real Identity        |
|  Name: David Miller   |
|  DOB: 1992            |
|  Location: Identified |
+-----------------------+
```

## Automating Email OSINT Workflows

Manual querying is slow. Analysts use frameworks to automate this pipeline.
- **Maltego:** Analysts use transforms (e.g., from Pipl, SocialNet, or HIBP integrations) to visually map the connections between an email, a breach, and a social persona.
- **SpiderFoot:** An automated OSINT framework where an analyst inputs an email address, and the tool concurrently queries hundreds of APIs (including HIBP, DeHashed, and social platforms) to generate a comprehensive footprint report.

## Defensive Applications (Securing the Organization)

This intelligence is not just for hunting adversaries; it is crucial for enterprise defense.
- **Credential Screening:** Organizations must ingest breach data and screen employee passwords against it. If an employee tries to set a password that exists in a known breach database, the Active Directory policy should reject it.
- **Executive Monitoring:** High-value targets (Executives, IT Admins) should have their corporate and known personal emails continuously monitored for inclusion in new breaches to preempt spear-phishing campaigns.

## Chaining Opportunities
- **[[07 - Social Media Intelligence SOCMINT on Threat Actors]]** - Taking the secondary email found via breach data and running it through Sherlock to find active social media profiles.
- **[[02 - Passive Infrastructure Enumeration]]** - Using the email address to query historical WHOIS databases (like DomainTools) to find other malicious domains registered by the actor.
- **[[09 - Tracking Pastebin and Ghostbin Leaks]]** - Searching Pastebin for the specific password hash discovered in the breach database to find raw, unindexed dumps.

## Related Notes
- [[01 - OSINT Fundamentals and Methodology]]
- [[07 - Social Media Intelligence SOCMINT on Threat Actors]]
- [[12 - Automating OSINT Workflows]]
