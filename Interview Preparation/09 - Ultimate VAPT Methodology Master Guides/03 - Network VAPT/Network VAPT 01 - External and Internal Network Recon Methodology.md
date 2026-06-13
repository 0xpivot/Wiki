---
tags: [vapt, methodology, network-security, interview, master-guide]
difficulty: expert
module: "Ultimate VAPT Master Guides - Network"
topic: "Master Guide - Network VAPT 01"
---

# Master Guide: External and Internal Network Recon Methodology

## 1. Interview Strategy: How to Explain Network Reconnaissance
When asked about your network reconnaissance methodology in a VAPT interview, avoid just saying "I run Nmap." An expert candidate must demonstrate a systematic, multi-layered approach. Structure your answer in phases:
1.  **Passive External:** Emphasize zero-touch discovery (OSINT, ASN mapping, WHOIS, DNS history, Shodan/Censys) to define the attack surface without alerting the target.
2.  **Active External:** Discuss stealthy port scanning, firewall/WAF evasion, and precise fingerprinting (Masscan to Nmap handoff).
3.  **Passive Internal:** Mention LLMNR/NBT-NS poisoning observation, ARP monitoring, and DHCP listening before making noise.
4.  **Active Internal:** Detail targeted scans, finding high-value targets (Domain Controllers, Backup Servers, SCCM), and enumerating Active Directory.
5.  **Always mention OPSEC:** Explain how you throttle scans, use decoys, or randomize source IPs/ports to simulate an APT rather than a noisy script kiddie.

*Key Interview Phrase:* "I approach reconnaissance as a funnel. I start with broad, passive intelligence gathering to map the entire perimeter, then slowly narrow my focus using targeted, low-noise active scanning techniques. My goal is to enumerate the maximum amount of attack surface with the minimum amount of network footprint."

---

## 2. External Network Reconnaissance Methodology

External recon focuses on identifying internet-facing assets belonging to an organization.

### Phase 1: Passive Reconnaissance & Asset Discovery

**ASN (Autonomous System Number) Discovery**
Large organizations own their IP space. Finding their ASN reveals all IP blocks routed to them.
- *Tools:* `whois`, `bgp.he.net`, `Amass`
- *Command:* `whois -h whois.radb.net -- '-i origin AS12345' | grep -Eo "([0-9.]+){4}/[0-9]+"`
- *Explanation:* By querying the regional internet registries (RIRs) and routing databases, we can extract the exact CIDR ranges the organization uses.

**Subdomain Enumeration**
Subdomains often point to forgotten infrastructure, staging environments, or vulnerable web applications.
- *Passive Tools:* `subfinder`, `assetfinder`, `Amass`, `crt.sh` (Certificate Transparency logs)
- *Command:* `subfinder -d target.com -all -recursive -o subdomains.txt`
- *Command:* `curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u`

**Cloud Asset Discovery**
Modern external infrastructure often lives in the cloud. We look for exposed S3 buckets, Azure blobs, or GCP buckets.
- *Tools:* `CloudBrute`, `S3Scanner`, `TruffleHog`
- *Technique:* Permutation scanning based on the company name (e.g., `target-dev`, `target-backup`, `target-prod`).

**Internet-Wide Port Scanners (OSINT)**
Before sending a single packet to the target, we query databases that have already scanned the internet.
- *Tools:* Shodan, Censys, FOFA, ZoomEye
- *Shodan Query:* `ssl:"Target Company" org:"Target ASN" port:"443,8443,3389,22"`
- *Interview Tip:* Mention how you use Shodan to find out-of-band management interfaces (ILO/iDRAC) or exposed RDP servers that the client might not even know about.

### Phase 2: Active Reconnaissance & Scanning

**DNS Enumeration & Brute-Forcing**
Active DNS enumeration involves interacting with the target's nameservers.
- *Zone Transfers (AXFR):* `dig axfr @ns1.target.com target.com` (Rarely works nowadays, but always test).
- *DNSSEC Zone Walking:* If NSEC records are used instead of NSEC3, you can walk the zone to reveal all subdomains. `ldns-walk target.com`.
- *Brute-forcing:* `ffuf -w subdomains.txt -u http://FUZZ.target.com -H "Host: FUZZ.target.com"` or `dnsx -d target.com -w wordlist.txt`.

**Port Scanning Methodology (The Masscan -> Nmap Pivot)**
Scanning a `/16` network with Nmap is too slow. The expert approach uses Masscan for discovery and Nmap for deep enumeration.
1.  *Initial Discovery:*
    `sudo masscan -p1-65535,U:53,161,500 198.51.100.0/24 --rate=1000 -e eth0 --router-mac <MAC> -oG masscan_results.txt`
2.  *Extraction:* Parse the open ports and IPs.
3.  *Deep Fingerprinting (Nmap):*
    `sudo nmap -sC -sV -p <open_ports> -Pn --min-rate 100 -iL live_hosts.txt -oA nmap_detailed`

**Evasion Techniques (If WAF/IDS is present)**
- Decoy Scans: `nmap -D RND:10 198.51.100.5`
- Fragmenting Packets: `nmap -f` or `--mtu 24`
- Source Port Manipulation: `nmap -g 53` (Bypasses naive stateless firewalls that allow all DNS traffic).

---

## ASCII Diagram: External Recon Workflow

```text
                        [ Target Organization ]
                               |
       +-----------------------+------------------------+
       |                       |                        |
[ ASN/BGP Mapping ]    [ OSINT/Shodan ]        [ Subdomain Enum ]
  bgp.he.net            Censys / FOFA           Subfinder / Amass
  whois (RIRs)          Search for IPs          crt.sh / DNS dump
       |                       |                        |
       +-----------+-----------+------------+-----------+
                   |                        |
            [ Target IP Ranges ]      [ Target Domains ]
                   |                        |
           [ Masscan Fast Scan ]      [ DNS Brute-force ]
           (Ports 1-65535, UDP)       (dnsx / puredns)
                   |                        |
                   +----------+-------------+
                              |
                     [ Nmap Deep Scan ]
                 (Version Detection, Scripts)
                              |
                    [ Attack Surface Map ]
                 (Ready for Vulnerability Analysis)
```

---

## 3. Internal Network Reconnaissance Methodology

Internal recon assumes you have initial access (e.g., via a compromised endpoint, VPN, or physical plug-in). The goal here is stealth and identifying paths to Domain Admin.

### Phase 1: Passive Internal Discovery

When you first land on an internal network, **do not run Nmap immediately**. A noisy scan will trigger EDR/NDR solutions (like Darktrace or ExtraHop).

**Listening to the Wire**
Start by sniffing broadcast and multicast traffic.
- *Tool:* Wireshark, `tcpdump`, or `Responder` (in Analyze mode).
- *Command:* `sudo responder -I eth0 -A`
- *What to look for:*
  - ARP Requests (Reveals live hosts and IP subnets).
  - LLMNR/NBT-NS/mDNS queries (Reveals hostnames and missing network shares).
  - OSPF/EIGRP/RIP routing protocols (Reveals network topology and adjacent subnets).
  - DHCP traffic (Reveals gateway, DNS servers, and PXE boot servers).

**IPv6 Local Link Discovery**
Many internal networks ignore IPv6, but it is enabled by default on Windows.
- Ping the all-nodes multicast address: `ping6 -I eth0 ff02::1`
- This forces all IPv6-enabled devices on the segment to reply, bypassing IPv4 host isolation or firewalls.

### Phase 2: Active Internal Discovery

**Host Discovery (Ping Sweeps and ARP)**
If stealth is less of a concern, active host discovery maps the subnet.
- *ARP Ping (Local Subnet):* `netdiscover -r 10.10.10.0/24` or `arp-scan -l`
- *ICMP Ping (Routed Subnets):* `nmap -sn 10.10.0.0/16`

**Targeted Service Enumeration**
Instead of scanning all ports on all hosts, search for specific services indicative of high-value targets.
- *Domain Controllers:* Scan for ports 53 (DNS), 88 (Kerberos), 389 (LDAP), 445 (SMB).
  `nmap -p 53,88,389,445 --open 10.10.0.0/16`
- *Web Servers & Intranet:* Ports 80, 443, 8080, 8443.
- *Databases:* 1433 (MSSQL), 1521 (Oracle), 3306 (MySQL).

**Active Directory Reconnaissance**
Once the Domain Controller is located, extract AD data without needing high privileges (any authenticated user can query LDAP).
- *Tools:* BloodHound (SharpHound), PowerView, `enum4linux`, `ldapsearch`.
- *SharpHound:* `Invoke-BloodHound -CollectionMethod All -Domain target.local`
- *LDAP Anonymous Bind Check:* `nmap -p 389 --script ldap-search 10.10.10.5`
- *Interview Tip:* Explain that BloodHound uses Graph Theory to map the shortest path to Domain Admin by analyzing ACLs, sessions, and group memberships. It is the gold standard for AD recon.

### Phase 3: Finding Vulnerability Vectors

- **SMB Shares:** Hunt for passwords in SYSVOL or open network shares.
  `crackmapexec smb 10.10.10.0/24 --shares`
- **Vulnerability Scanners:** Run Nessus or OpenVAS ONLY if the client permits noisy scanning and NDR bypass is not in scope. For stealth, use localized nmap scripts (e.g., `--script smb-vuln*`).

---

## ASCII Diagram: Internal Recon Workflow

```text
               [ Initial Internal Access ]
                     (VPN / Phishing / Physical)
                               |
                  +------------+------------+
                  |                         |
          [ Passive Sniffing ]      [ Environment Checks ]
          (Responder -A, tcpdump)   (whoami, ipconfig, env)
                  |                         |
          [ Observe Protocols ]     [ Identify AD Domain ]
         (LLMNR, ARP, IPv6, OSPF)           |
                  |                         |
                  +------------+------------+
                               |
                   [ Active Host Discovery ]
                  (ARP Scans, ICMP Sweeps)
                               |
                  [ Targeted Port Scanning ]
             (Hunt for DCs: 88, 389, 445, 3268)
                               |
                   [ Active Directory Recon ]
                (BloodHound, LDAP queries, SMB)
                               |
                    [ Lateral Movement Map ]
                (Identify shortest path to DA)
```

---

## 4. Real-World Attack Scenario

**Scenario: From External Obscurity to Internal Footprint**
1. **External OSINT:** During an external VAPT engagement, the pentester found the target's ASN and ran `Amass`. A forgotten subdomain `legacy-vpn.target.com` was discovered pointing to an IP within the target's netblock.
2. **Port Scanning:** Masscan revealed port 443 open. Nmap fingerprinting identified it as an outdated Pulse Secure VPN appliance.
3. **Exploitation:** The tester used CVE-2019-11510 (Arbitrary File Read) to read the `/data/config/dsengine.rsa` file and extract plain-text session cookies, bypassing MFA.
4. **Internal Pivot & Passive Recon:** Once connected to the VPN, the tester did *not* run Nmap. Instead, they spun up Wireshark. Within 10 minutes, they observed broadcast LLMNR traffic looking for `FILE-SERVER-02`.
5. **Active AD Recon:** The tester queried the DNS server for SRV records (`_ldap._tcp.dc._msdcs.target.local`) to find the exact IP of the Domain Controller. They used a low-privileged AD credential (found on an internal wiki via SMB mapping) to run SharpHound remotely via a SOCKS proxy.
6. **Result:** The BloodHound graph revealed that the compromised VPN user had `GenericAll` rights over a Helpdesk group, leading directly to a path to Domain Admin.

---

## 5. Chaining Opportunities

Network Recon is useless in isolation; it must be chained into active exploitation:
- **Recon -> Exploitation:** Finding port 445 open and verifying the OS version leads directly to chaining `MS17-010 (EternalBlue)` or `SMBGhost`.
- **Recon -> Spoofing:** Observing LLMNR queries for non-existent hosts chains perfectly into Responder poisoning, forcing NTLMv2 hashes to be sent to the attacker.
- **Recon -> Lateral Movement:** Identifying open RDP (3389) or WinRM (5985) ports during internal recon sets the stage for Pass-the-Hash or Overpass-the-Hash attacks.

---

## 6. Related Notes

- [[Network VAPT 02 - Exploiting Layer 2 and Layer 3 Vulnerabilities]] - Proceed here to learn how to abuse the internal network protocols discovered during passive recon (ARP, DHCP, STP).
- [[Network VAPT 03 - Attacking Network Services SMB FTP SSH]] - Learn how to exploit the specific service ports discovered during your Nmap scans.
- [[Network VAPT 05 - Pivoting and Lateral Movement Methodologies]] - Learn how to proxy your reconnaissance tools deep into segregated internal networks.
- [[Active Directory Reconnaissance Master Guide]] - Deep dive into BloodHound, LDAP querying, and Kerberos enumeration.

---
**Disclaimer:** This material is designed for interview preparation and authorized penetration testing only. Never conduct network reconnaissance or scanning on infrastructure you do not explicitly own or have written permission to test. Unauthorized scanning can lead to severe legal consequences.

---

## 7. Deep Dive: Advanced Passive OSINT Techniques
While standard tools like Subfinder and Amass are excellent, an expert VAPT methodology incorporates advanced OSINT correlation.
- **GitHub Dorking for Internal Architecture:** Attackers often find Terraform, Ansible, or Kubernetes YAML files mistakenly committed to public repositories. Searching for `org:"TargetName" filename:docker-compose.yml` can reveal the internal IP schema, required ports, and database credentials before you even send a packet.
- **Historical DNS Analysis:** Services like SecurityTrails or DNSDumpster maintain records of old DNS pointers. A subdomain that used to point to AWS might now point to an on-premise IP. Attackers use this to bypass cloud WAFs (like Cloudflare) by hitting the origin IP directly.
- **Certificate Transparency (CT) Logs Deep Dive:** CT logs record every SSL/TLS certificate issued. By querying `crt.sh`, you don't just find subdomains; you find the exact environments (e.g., `staging-api.v2.target.com`). This is a zero-touch method that cannot be blocked by the target.
- **BGP Hijacking Context:** Understanding Border Gateway Protocol is crucial. If the target does not implement RPKI (Resource Public Key Infrastructure), their ASN might be vulnerable to BGP hijacking, allowing an advanced attacker to reroute their traffic entirely.

## 8. Advanced Active Directory Recon (BloodHound Deep Dive)
BloodHound is not just a tool; it's an implementation of Graph Theory for offensive security.
- **Cypher Queries:** Expert candidates should mention custom Cypher queries. Instead of just looking for "Shortest Path to Domain Admin", an expert might run: `MATCH p=(u:User)-[:HasSession]->(c:Computer)-[:AdminTo]->(t:Computer) RETURN p`. This query finds where users are logged in and if those sessions can be hijacked to gain admin on another machine.
- **Kerberoasting Prep:** During internal recon, querying LDAP for accounts with the `servicePrincipalName` (SPN) attribute set is critical. This identifies service accounts (usually highly privileged) that can be targeted for Kerberoasting without needing to scan any ports.
- **AS-REP Roasting Prep:** Similarly, looking for users with `DONT_REQ_PREAUTH` enabled in AD allows the attacker to request a Kerberos ticket for the user and crack it offline, again, without a single Nmap scan.

## 9. Comprehensive Tool Reference Matrix
To fully prepare for the interview, memorize the exact use cases for these tools:
| Tool | Layer / Phase | Primary Use Case | OPSEC Risk |
|------|---------------|------------------|------------|
| Nmap | Active Recon | Deep fingerprinting and NSE script execution. | High (Easily detected by Snort/Suricata) |
| Masscan | Active Recon | Asynchronous, stateless, ultra-fast port discovery across /8 subnets. | High (Volumetric anomaly detection) |
| Amass | Passive/Active | Deep DNS enumeration, certificate parsing, and ASN mapping. | Low (Mostly passive API calls) |
| Responder | Passive Internal | Sniffing LLMNR/NBT-NS broadcasts on local subnets. | Medium (Active poisoning triggers some NDRs) |
| BloodHound | Active Internal | Mapping Active Directory ACLs and sessions. | Medium (Large LDAP queries can be flagged) |
| enum4linux | Active Internal | Extracting SID, users, and groups via SMB null sessions. | High (Legacy SMBv1 traffic is noisy) |
| dnsx | Active Recon | Fast, multi-threaded DNS resolution and brute-forcing. | Low (Blends with normal DNS traffic) |

## 10. Blue Team: Log Analysis and Detection Engineering
An expert VAPT candidate must know how their attacks look to the defense.
- **Nmap Detection:** Firewalls and IDS (like Snort) detect Nmap not just by port volume, but by signature. A default Nmap SYN scan uses a specific TCP window size (often 1024 or 2048) and specific TCP options.
- **BloodHound Detection:** SharpHound performs thousands of LDAP queries (Event ID 4662) and accesses the SAM of every computer (Event ID 4624/4634 Logon/Logoff). Defenders tune their SIEM to alert when a single user queries thousands of objects in seconds.
- **Responder Detection:** When Responder poisons LLMNR, it sends UDP packets from an unauthorized IP. Defenders deploy Honey-Tokens (fake SPNs or LLMNR queries) and alert if any machine tries to respond to them.

## 11. Common Interview Pitfalls and How to Avoid Them
1.  **"I run Nmap with -A"**: The `-A` flag (Aggressive) runs OS detection, version scanning, script scanning, and traceroute. It is incredibly noisy and slow. Never say this in an interview for a stealthy engagement. Instead, say you use `-sS` (SYN scan) and cherry-pick your NSE scripts.
2.  **Skipping the Passive Phase**: If the interviewer asks how you start a black-box test, do not say "ping sweep." Emphasize that passive OSINT is the only zero-risk way to gather intelligence.
3.  **Forgetting IPv6**: Internal networks are often dual-stack. Mentioning that you use IPv6 multicast to find hosts when IPv4 ICMP is blocked shows deep protocol knowledge.
4.  **Ignoring the Cloud**: Modern networks extend into AWS/Azure. Mentioning that you check for exposed S3 buckets during external recon demonstrates a modern methodology.
