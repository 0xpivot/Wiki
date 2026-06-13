---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.06 Detecting Domain Generation Algorithms DGAs"
---

# 90.06 Detecting Domain Generation Algorithms DGAs

## 1. Introduction to Domain Generation Algorithms (DGA)

Domain Generation Algorithms (DGAs) are programmatic methods utilized by various malware families—particularly botnets, ransomware, and Advanced Persistent Threats (APTs)—to dynamically generate a large number of pseudo-random domain names. The purpose of a DGA is to ensure resilient command and control (C2) communication. Instead of hardcoding a single C2 domain (which can be easily sinkholed, blacklisted, or seized by law enforcement), the malware generates hundreds or thousands of domains daily. The attacker only needs to register one or two of these predicted domains to establish communication with the infected endpoints.

### 1.1 The Necessity of DGAs from the Attacker's Perspective
In the early days of malware, C2 infrastructure relied on static IP addresses or static domains. Defenders quickly realized that by analyzing malware samples, they could extract these static indicators of compromise (IoCs) and block them at the firewall or DNS level. 
DGAs introduce an element of unpredictability and scale. By generating 10,000 domains a day, the attacker forces the defender to block an ever-changing list. Since the domains do not exist until the attacker registers them, traditional blocklists are perpetually playing catch-up.

## 2. Anatomy of a DGA

A typical DGA relies on a few core components:
- **Seed:** A shared secret or initial value known to both the malware and the attacker. This ensures both sides generate the exact same list of domains.
- **Time Element:** A variable that changes over time (e.g., current date, Twitter trending topics, FX rates). This ensures that the generated domains are different every day or every week.
- **Algorithm:** The mathematical function (often a pseudorandom number generator, or PRNG, sometimes utilizing hash functions or modular arithmetic) that combines the seed and the time element to produce strings.
- **Top-Level Domains (TLDs):** A list of appended suffixes (e.g., `.com`, `.ru`, `.xyz`, `.biz`, `.info`).

### 2.1 Types of DGAs
1. **Arithmetic (A-DGA):** Generates domains by calculating ASCII values based on PRNGs. Produces highly random, gibberish-looking domains (e.g., `xkqzwjyv.com`).
2. **Hash-Based (H-DGA):** Uses cryptographic hashes (like MD5 or SHA256) of a seed and time, converting the hex output into a domain.
3. **Wordlist-Based (W-DGA):** Concatenates words from a pre-defined dictionary (e.g., `purpleelephantsky.com`). These are much harder to detect via entropy analysis because they look like legitimate human-created domains.
4. **Permutation-Based (P-DGA):** Takes a legitimate base domain and permutes it (e.g., `google.com` -> `g00gle.com`, `goolge.com`).

## 3. Architecture and Network Flow

```text
    +-------------------------------------------------------------+
    |                 ENTERPRISE NETWORK                          |
    |                                                             |
    |   +-----------------+           +--------------------+      |
    |   |                 |           |                    |      |
    |   | Infected Host   |           | Internal DNS       |      |
    |   | (Running DGA)   |           | Server / Forwarder |      |
    |   |                 |           |                    |      |
    |   +--------+--------+           +---------+----------+      |
    |            |                              |                 |
    |            | 1. Query: xqkjzf.com         |                 |
    |            +----------------------------> |                 |
    |                                           | 2. Forward to   |
    |            4. Response: NXDOMAIN          |    Internet     |
    |            <----------------------------+ |                 |
    |                                           |                 |
    |   +-----------------+                     |                 |
    |   |                 | 5. Query:           |                 |
    |   | Infected Host   |    next-dga.ru      |                 |
    |   |                 +-------------------> |                 |
    |   +-----------------+                     |                 |
    +-------------------------------------------+-----------------+
                                                |
                                                | 3. Internet DNS Iteration
                                                v
                                      +--------------------+
                                      |                    |
                                      | Root / TLD Servers |
                                      |                    |
                                      +---------+----------+
                                                |
                                                | 6. Resolved (If Attacker Registered)
                                                v
                                      +--------------------+
                                      |                    |
                                      | Attacker C2 Server |
                                      | (198.51.100.4)     |
                                      +--------------------+
```

## 4. Detection Methodologies

Detecting DGAs requires analyzing DNS traffic at scale. Single DNS queries are rarely enough to convict a host; detection is based on aggregate behavior.

### 4.1 Statistical and Entropy Analysis
The most common way to detect Arithmetic and Hash-based DGAs is by measuring the Shannon Entropy of the queried domain names.
Legitimate domains usually have a lower entropy because they consist of pronounceable words or predictable patterns. DGA domains like `zxcvbnmasdfghjkl.xyz` have an unusually high entropy and abnormal n-gram distribution.

*Formula for Shannon Entropy:*
$$ H(X) = - \sum_{i=1}^{n} P(x_i) \log_2 P(x_i) $$
Where $P(x_i)$ is the probability of character $x_i$ appearing in the domain name.

### 4.2 NXDOMAIN Rate Monitoring
Because the attacker only registers a tiny fraction of the generated domains, the infected host will generate a massive amount of DNS queries that resolve to `NXDOMAIN` (Non-Existent Domain). 
A standard workstation might generate a few NXDOMAINs a day due to typos. A DGA-infected workstation will generate hundreds or thousands in a short burst.

### 4.3 Subdomain Length and Consonant/Vowel Ratios
Evaluating the ratio of vowels to consonants can identify non-pronounceable domains. If a domain consists of 15 characters and 14 are consonants, it is highly suspicious.

## 5. Threat Hunting with Zeek

Zeek is incredibly powerful for monitoring DNS traffic. The `dns.log` file captures all DNS transactions, making it the primary data source for DGA hunting.

### 5.1 Zeek Command Line Hunting
To find hosts generating an excessive amount of NXDOMAIN responses, you can use `zeek-cut` and standard UNIX utilities:

```bash
cat dns.log | zeek-cut id.orig_h rcode_name query | grep NXDOMAIN | awk '{print $1}' | sort | uniq -c | sort -nr | head -n 10
```
*Explanation:* This command extracts the source IP, response code, and queried domain. It filters for `NXDOMAIN`, groups by source IP, and counts the occurrences. An IP with thousands of NXDOMAINs is a prime DGA suspect.

### 5.2 Advanced Zeek Script for DGA Detection
Below is a conceptual Zeek script that tracks NXDOMAINs per host over a rolling window. If the threshold is exceeded, it generates a Notice.

```zeek
module DGA_Detector;

export {
    redef enum Notice::Type += { High_NXDOMAIN_Rate };
    const nxdomain_threshold: double = 50.0;
    const tracking_interval: interval = 10 mins;
}

global nx_track: table[addr] of count &create_expire=tracking_interval &default=0;

event dns_message(c: connection, is_orig: bool, msg: dns_msg, len: count)
    {
    if ( ! is_orig && msg$rcode == 3 ) # rcode 3 is NXDOMAIN
        {
        local src = c$id$orig_h;
        nx_track[src] += 1;
        
        if ( nx_track[src] == nxdomain_threshold )
            {
            NOTICE([$note=High_NXDOMAIN_Rate,
                    $msg=fmt("Host %s has exceeded the NXDOMAIN threshold with %d queries.", src, nx_track[src]),
                    $src=src]);
            }
        }
    }
```

## 6. Threat Hunting with Suricata

Suricata provides signature-based detection for known DGA families and anomalous DNS behavior.

### 6.1 Suricata Rule for Excessive NXDOMAIN
While Suricata is better suited for payload inspection, it can utilize the `dns.rcode` keyword combined with thresholding to alert on DGA behavior.

```suricata
alert dns $HOME_NET any -> any any (msg:"ET HUNTING Suspicious High Volume NXDOMAIN Responses (DGA Potential)"; dns.rcode:3; threshold: type both, track by_src, count 100, seconds 60; classtype:bad-unknown; sid:1000001; rev:1;)
```

### 6.2 Detecting Known DGA TLDs
If intelligence indicates that a specific threat actor is utilizing obscure TLDs for their DGA (e.g., `.top`, `.pw`, `.bit`), you can write rules targeting those specific queries when the domain length is excessively long.

```suricata
alert dns $HOME_NET any -> any any (msg:"ET HUNTING Suspicious Long Domain Query with Obscure TLD"; dns.query; content:".pw"; endswith; pcre:"/^[a-z0-9]{15,}\.pw$/i"; classtype:bad-unknown; sid:1000002; rev:1;)
```

## 7. Analyzing DGA PCAPs with Wireshark and Tshark

When diving into full packet capture (PCAP) to analyze a suspected DGA incident, `tshark` is invaluable for rapid triage.

### 7.1 Tshark DGA Extraction
Extract all DNS queries that resulted in an NXDOMAIN, along with the source IP:

```bash
tshark -r suspicious.pcap -Y "dns.flags.rcode == 3" -T fields -e ip.src -e dns.qry.name
```

### 7.2 Wireshark Display Filters
- Filter for specific DGA lengths: `dns.qry.name matches "^[a-z0-9]{20,}\.[a-z]{2,3}$"`
- Show only queries that failed to resolve: `dns.flags.rcode == 3`
- Look for TXT record queries (sometimes used by DGAs for secondary payload delivery): `dns.qry.type == 16`

## 8. Real-World Attack Scenario

### 8.1 The SolarWinds SUNBURST DGA
During the infamous SolarWinds supply chain attack (UNC2452/Nobelium), the SUNBURST backdoor utilized an incredibly sophisticated, hybrid DGA. 
Instead of generating random gibberish, the SUNBURST DGA encoded the victim's internal Active Directory domain name and hostname into the subdomain string itself. 

**Flow of the Attack:**
1. SUNBURST activated and gathered the local AD domain (e.g., `corp.victim.com`).
2. It encoded this data using a custom base32 algorithm.
3. The encoded string was prepended to a hardcoded base domain: `[encoded-data].appsync-api.eu-west-1.avsvmcloud.com`.
4. The malware queried this domain.
5. The attackers running the authoritative nameserver for `avsvmcloud.com` received the query. Because they controlled the nameserver, they could decode the subdomain, revealing the victim's identity.
6. Based on the victim's value, the attackers would either return an NXDOMAIN (to remain dormant) or return a specific CNAME record pointing to a secondary active C2 infrastructure to initiate lateral movement.

This bypasses traditional "gibberish" entropy checks and highlights why DGA hunting must also include analyzing abnormally long subdomains on seemingly legitimate base domains (in this case, `avsvmcloud.com`).

## 9. Advanced Evasion Techniques

Modern malware is adapting to make DGA detection harder:
- **Dictionary DGAs:** Using English words concatenated together (e.g., `bluecarwindow.com`). This completely defeats standard Shannon entropy checks.
- **Timing Evasion:** Spacing out DNS requests over hours or days to bypass threshold-based NXDOMAIN detection alerts.
- **DoH/DoT:** Malware may route its DGA queries through DNS over HTTPS (DoH) or DNS over TLS (DoT) directly to public resolvers (like 8.8.8.8), entirely bypassing the enterprise's internal DNS logs and network-level inspection.

## 10. Incident Response Playbook

If a DGA infection is suspected based on high NXDOMAIN alerts:

1. **Identification:**
   - Query the SIEM for all DNS requests originating from the suspected endpoint.
   - Run entropy checks on the requested domains to confirm they are algorithmically generated.
   - Look for the single successful response (A record) amidst the sea of NXDOMAINs. This indicates the attacker's registered C2.
2. **Containment:**
   - Isolate the infected host from the network.
   - Block the resolved C2 IP address at the firewall.
   - Sinkhole the C2 domain internally to track any other infected hosts attempting to beacon out.
3. **Eradication:**
   - Image the endpoint for forensic analysis to identify the malware dropper.
   - Run advanced anti-malware scanners to remove the infection.
4. **Recovery:**
   - Reimage the machine if the infection is deeply rooted (e.g., rootkit).
   - Reset the user's credentials in Active Directory in case of credential harvesting.

## 11. Chaining Opportunities
- DGA detection often leads straight into identifying active C2 channels. Once the resolved DGA IP is identified, hunters can pivot to [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]] to inspect the encrypted payload.
- DNS activity that looks like a DGA but utilizes TXT records might actually be data exfiltration. Transition to [[07 - Hunting for DNS Tunneling and Exfiltration]] for further analysis.
- If lateral movement occurred before the DGA fired, investigate [[09 - Detecting Lateral Movement via SMB and RDP]].

## 12. Related Notes
- [[07 - Hunting for DNS Tunneling and Exfiltration]]
- [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]]
- [[09 - Detecting Lateral Movement via SMB and RDP]]
