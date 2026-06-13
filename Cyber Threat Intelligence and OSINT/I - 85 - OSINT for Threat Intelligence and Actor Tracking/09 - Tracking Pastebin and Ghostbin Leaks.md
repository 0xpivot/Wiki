---
tags: [osint, threat-intel, actor-tracking, vapt]
difficulty: intermediate
module: "85 - OSINT for Threat Intelligence and Actor Tracking"
topic: "85.09 Tracking Pastebin and Ghostbin Leaks"
---

# 85.09 Tracking Pastebin and Ghostbin Leaks

## Introduction to Paste Sites in Threat Intel

Paste sites, originally designed for developers to share snippets of code or configuration files quickly, have evolved into a cornerstone of the cybercriminal ecosystem. Platforms like Pastebin, Ghostbin, ControlC, and JustPaste.it offer anonymous, text-based hosting with virtually zero barrier to entry. For a Cyber Threat Intelligence (CTI) analyst, these platforms represent a massive, continuously updating repository of Threat Actor (TA) operational data, malware staging, and breached information.

Because these sites allow users to publish text anonymously and provide "raw" text output views, they are structurally perfect for automated scripting, making them a favorite tool for malware authors and hacktivists alike.

## The Role of Paste Sites in the Cyber Kill Chain

Threat Actors utilize paste sites across multiple phases of an attack:

### 1. Payload Hosting and Staging
Malware rarely contains its entire payload within the initial executable (to evade antivirus). Instead, a lightweight "stager" is deployed. This stager executes a command (e.g., using PowerShell or `curl`) to fetch the primary malicious code from a paste site. 
- The stager accesses the `raw` URL of the paste (e.g., `https://pastebin.com/raw/a1b2c3d4`).
- This technique abuses the implicit trust network defenses often grant to domains like Pastebin.

### 2. Dead Drop Resolvers (DDR)
To prevent their Command and Control (C2) infrastructure from being hardcoded and easily blocked, TAs use paste sites as Dead Drop Resolvers. The malware reaches out to a specific Pastebin URL. The text on that paste contains the current, operational IP address of the C2 server. If the C2 server is taken down, the TA simply updates the Pastebin post with a new IP, and the entire botnet seamlessly migrates.

### 3. Data Leaks and Doxxing
Hacktivists and lower-tier cybercriminals frequently use paste sites to dump compromised databases, leaked credential combolists (username:password formats), and doxed personal identifiable information (PII) of targets.

## Characteristics of Major Paste Sites

- **Pastebin.com:** The most famous. Heavily moderated now, but still widely abused. Offers a Pro API for scraping.
- **Ghostbin / ControlC / Rentry.co:** Alternatives that offer less moderation, syntax highlighting, and varying degrees of anonymity. Often favored when Pastebin actively blocks malicious IP ranges.
- **JustPaste.it:** Frequently used by hacktivists and political extremists to publish manifestos alongside target lists.

## Searching and Scraping Paste Sites

Because of the sheer volume of data published every second, manual analysis is impossible. Analysts rely on automated scraping and targeted dorking.

### 1. Search Operators and Dorking
While Pastebin's internal search is limited, Google indexes public pastes heavily.
- `site:pastebin.com "password" "admin" "companyname.com"`
- `site:pastebin.com "BEGIN RSA PRIVATE KEY"`
- `site:pastebin.com "Invoke-Mimikatz" OR "DownloadString"`

### 2. Identifying Malicious Payloads (Obfuscation)
TAs rarely upload cleartext malware. Analysts must look for signs of obfuscation:
- **Base64 Encoding:** Massive blocks of alphanumeric characters ending in `=` or `==`. Analysts must decode this to reveal the true script.
- **Hex Encoding:** Long strings of `\x41\x42` or `4A 5B`.
- **PowerShell Obfuscation:** Use of backticks (`` ` ``), randomized variable names, and string concatenation designed to evade static analysis.

## Real-World Attack Scenario

### Discovering a Botnet's Dead Drop Resolver

**The Setup:**
During an incident response engagement, an analyst reverse-engineers a malicious Word macro. The macro contains a heavily obfuscated PowerShell command that, when decoded, reveals a request to `https://pastebin.com/raw/XyZ123AB`.

**The Investigation:**
1. The analyst navigates to the raw URL. The paste contains a single Base64 encoded string: `MTk4LjUxLjEwMC40NTo4NDQz`.
2. The analyst decodes the Base64 string, revealing the IP and port of the TA's actual C2 server: `198.51.100.45:8443`.
3. Instead of just blocking the IP, the analyst sets up an automated monitor on that specific Pastebin URL. 
4. Three days later, the botnet's C2 server goes offline. The TA updates the paste with a new Base64 string. The analyst's monitor triggers immediately, decodes the new string, and automatically pushes the new C2 IP to the organization's firewall blocklist, effectively neutralizing the botnet's ability to re-establish control.

## Architecture & Investigation Flow Diagram

```text
+-----------------------+
|  Compromised Host     |
|  (Executes Stager)    |
+-----------+-----------+
            |
            | 1. HTTP GET request to Raw Paste URL
            v
+-----------------------+       +------------------------+
|   Pastebin.com        |       |   Malicious Paste      |
|   (Dead Drop Resolver)|------>|   Content (Base64):    |
|                       |       |   "MjAzLjAuMTEzLjg4"   |
+-----------+-----------+       +-----------+------------+
                                            |
                                            | 2. Malware Decodes Payload
                                            v
                                +------------------------+
                                |  Actual C2 Server      |
                                |  IP: 203.0.113.88      |
                                +------------------------+

**CTI Analyst Workflow:**
Analyst monitors Pastebin -> Detects Base64 string -> Decodes IP -> Pre-emptively blocks C2.
```

## Automating Paste Site Monitoring

Proactive threat intelligence requires continuous, automated monitoring of paste sites.

1. **PasteHunter:** A popular Python tool that connects to the Pastebin API (or scrapes other sites) and scans all newly published pastes against a repository of YARA rules. If a paste matches a rule (e.g., matches the signature of a known credential dump format), an alert is generated.
2. **Dumpmon:** An older but conceptually foundational Twitter bot/script that monitors paste sites for passwords, API keys, and database dumps.
3. **Scavenger:** A tool designed to collect and parse intelligence from various paste sites, focusing on credential leaks.

### Writing YARA Rules for Pastes
Analysts write custom YARA rules to detect infrastructure. For example, a rule to catch a specific PowerShell downloader syntax:
```yara
rule Suspicious_PS_Downloader {
    strings:
        $s1 = "Net.WebClient" nocase
        $s2 = "DownloadString" nocase
        $s3 = "pastebin.com/raw/" nocase
    condition:
        all of them
}
```

## Legal and Ethical Considerations

Monitoring paste sites often exposes analysts to vast amounts of Personally Identifiable Information (PII) and compromised credentials belonging to third parties.
- **Handling Data:** Analysts must ensure they do not accidentally store or distribute cleartext PII. Data should be hashed or heavily redacted upon ingestion into the CTI database.
- **Interacting with Infrastructure:** Merely viewing a paste is passive. However, if the paste tracks viewer IPs (which TAs sometimes set up to monitor researchers), the analyst's OPSEC is blown. Always use VPNs or Tor when accessing these URLs.

## Chaining Opportunities
- **[[08 - Code Repository Intelligence GitHub GitLab Search]]** - Pastes often contain links pointing back to GitHub repositories where the heavier malware payloads are stored.
- **[[10 - Email OSINT and Data Breach Search HaveIBeenPwned DeHashed]]** - Extracting emails from dumped combolists on paste sites and verifying them across breach databases.
- **[[02 - Passive Infrastructure Enumeration]]** - Taking C2 IPs discovered in Dead Drop Resolvers and running passive DNS analysis to find associated domains.

## Related Notes
- [[01 - OSINT Fundamentals and Methodology]]
- [[11 - Dark Web Intelligence and Tor Hidden Services]]
- [[12 - Automating OSINT Workflows]]
