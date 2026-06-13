---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.07 Hunting for DNS Tunneling and Exfiltration"
---

# 90.07 Hunting for DNS Tunneling and Exfiltration

## 1. Introduction to DNS Tunneling

The Domain Name System (DNS) is foundational to internet connectivity. Because of its critical role, DNS traffic on UDP/TCP port 53 is almost universally permitted to traverse enterprise firewalls without deep packet inspection. Threat actors and red teams exploit this implicit trust by encapsulating non-DNS protocols or exfiltrated data within standard DNS queries and responses. This technique is known as DNS Tunneling.

DNS Tunneling serves two primary malicious purposes:
1. **Command and Control (C2):** Bypassing egress restrictions to communicate with an external C2 server.
2. **Data Exfiltration:** Smuggling sensitive data out of the network in small chunks encoded within DNS subdomains or specific record types.

### 1.1 The Mechanics of a DNS Tunnel
Unlike a Domain Generation Algorithm (DGA) which generates distinct root/subdomains for direct IP resolution, a DNS tunnel relies on the attacker controlling an authoritative nameserver for a specific delegated domain (e.g., `evil-domain.com`). 

The infected host sends data by encoding it into the subdomain of a query. 
For example: `[Base64_Encoded_Data].evil-domain.com`.
The local DNS server, not knowing the answer, forwards this query to the internet, eventually reaching the attacker's authoritative nameserver. The attacker logs the query, decodes the subdomain to retrieve the exfiltrated data, and then crafts a specific DNS response (often using `TXT`, `CNAME`, or `A` records) containing the C2 instructions back to the victim.

## 2. DNS Tunneling Architecture

```text
      [Victim Machine]                                    [Attacker Authoritative DNS]
      Running malware                                     (evil-domain.com)
             |                                                       ^
             | 1. Exfiltrate data: "password123"                     |
             |    Base64: "cGFzc3dvcmQxMjM"                          |
             |                                                       |
             v                                                       |
    +-----------------+                                     +--------+--------+
    |                 | 2. Query:                           |                 |
    | Local DNS Cache | cGFzc3dvcmQxMjM.evil-domain.com     | Root / TLD      |
    | (Corporate)     | ----------------------------------> | Infrastructure  |
    |                 |                                     |                 |
    +--------+--------+                                     +--------+--------+
             ^                                                       |
             | 5. Response: TXT "run_cmd:whoami"                     | 3. Delegate to evil-domain.com
             |                                                       v
             |                                              +--------+--------+
             | 4. Attacker decodes "cGFzc3dvcmQxMjM"        |                 |
             +--------------------------------------------- | Attacker Server |
                                                            | (C2 / Exfil)    |
                                                            +-----------------+
```

## 3. Characteristics of DNS Tunneling

Hunting for DNS tunneling requires understanding how anomalous DNS tunnel traffic differs from legitimate web browsing or service queries.

1. **Volume of Queries:** Tunneling requires massive amounts of queries to transmit meaningful data because the DNS protocol inherently limits payload size. A single file transfer might generate tens of thousands of requests.
2. **Subdomain Length and Entropy:** The subdomains are typically long, randomly generated, and heavily encoded (Base32, Base64, Hex). 
3. **Unusual Record Types:** While `A` and `AAAA` records are standard, tunnels frequently utilize `TXT` (can hold up to 255 characters per string, multiple strings per record), `NULL` (obsolete but allows arbitrary binary data up to 65535 bytes), `CNAME`, or `MX`.
4. **Orphaned DNS Packets:** Tunnels sometimes use direct UDP connections to external IPs bypassing the internal DNS architecture.

## 4. Threat Hunting with Zeek

Zeek's `dns.log` provides all the necessary telemetry to identify tunneling behavior based on volume, length, and record types.

### 4.1 Analyzing Subdomain Lengths
Adversaries maximize the 63-character limit per DNS label and 253-character limit per FQDN. Using `zeek-cut`, we can isolate the query lengths.

```bash
# Find queries with exceptionally long subdomains (e.g., > 50 characters)
cat dns.log | zeek-cut query | awk '{ if (length($0) > 50) print $0 }' | head -n 20
```

### 4.2 Analyzing Query Volume per Domain
If an internal host queries `evil-domain.com` 50,000 times in an hour, while normal domains like `google.com` sit at 500, it's a strong indicator of a tunnel.

```bash
# Extract the base domain from queries and count frequencies
cat dns.log | zeek-cut query | awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c | sort -nr | head -n 10
```

### 4.3 Zeek Script: Detecting Large TXT Responses
This script alerts when a DNS response contains an abnormally large TXT record, a classic hallmark of tools like `dnscat2` or `Iodine`.

```zeek
module DNSTunnel_Detect;

export {
    redef enum Notice::Type += { Large_TXT_Response };
    const txt_length_threshold: count = 150;
}

event dns_TXT_reply(c: connection, msg: dns_msg, ans: dns_answer, strings: string_vec)
    {
    for ( i in strings )
        {
        if ( |strings[i]| > txt_length_threshold )
            {
            NOTICE([$note=Large_TXT_Response,
                    $msg=fmt("Large TXT record detected: %s (Length: %d)", ans$query, |strings[i]|),
                    $sub=strings[i],
                    $conn=c]);
            }
        }
    }
```

## 5. Threat Hunting with Suricata

Suricata excels at detecting the specific, known signatures of off-the-shelf DNS tunneling tools like `dnscat2`, `Iodine`, `OzymanDNS`, and `Cobalt Strike` DNS beacons.

### 5.1 Suricata Rule for DNSCat2
`dnscat2` is a popular tunneling tool that creates an encrypted command-and-control channel over DNS. It has specific magic bytes and negotiation patterns.

```suricata
alert dns $HOME_NET any -> any 53 (msg:"ET MALWARE dnscat2 DNS tunnel active"; dns.query; content:"dnscat"; nocase; classtype:command-and-control; sid:2020001; rev:2;)
```

### 5.2 Detecting Abnormal TXT Queries
While legitimate services (like SPF checks) use TXT, high frequency from a single host implies abuse.

```suricata
alert dns $HOME_NET any -> $EXTERNAL_NET 53 (msg:"ET HUNTING Frequent TXT Record Queries - Potential Tunneling"; dns.query; pcre:"/^[A-Za-z0-9\+\/]{40,}\./"; threshold: type both, track by_src, count 50, seconds 60; classtype:bad-unknown; sid:2020002; rev:1;)
```

## 6. Threat Hunting with PCAP and Wireshark

When analyzing a packet capture containing a suspected DNS tunnel, specific Wireshark display filters allow rapid isolation of the malicious traffic.

### 6.1 Identifying the Tunnel in Wireshark
- Filter for TXT queries only: `dns.qry.type == 16`
- Filter for NULL queries: `dns.qry.type == 10`
- Find excessively long queries: `dns.qry.name.len > 100`

### 6.2 Analyzing Payload Fragmentation
Because DNS UDP packets are typically limited to 512 bytes (without EDNS0), attackers must fragment large files into hundreds of sequential queries.
By applying a filter like `dns.qry.name contains "evil-domain.com"`, you can export the packet bytes into a hex editor. If the attacker used basic Base64 without encryption, you can manually strip the base domain, concatenate the subdomains, and decode them to retrieve the exfiltrated file.

## 7. Real-World Attack Scenario

### 7.1 OilRig (APT34) DNS Tunneling
The Iranian threat group OilRig is notorious for relying heavily on custom DNS tunneling backdoors, such as **Helminth** and **DNSpionage**. 

**Attack Flow:**
1. **Initial Access:** OilRig compromised a victim via a spear-phishing document containing a malicious macro.
2. **Execution:** The macro deployed the Helminth VBScript backdoor.
3. **C2 via DNS:** Helminth executed local enumeration commands (`whoami`, `ipconfig`, `dir`) and wrote the output to a temporary text file.
4. **Exfiltration:** The script read the file, base64 encoded it in 30-byte chunks, and performed DNS `A` record queries like `01[base64_chunk]00.oilrig-c2.com`.
5. **Response:** The authoritative server parsed the chunks, rebuilt the text file, and responded with an `A` record containing a pseudo-IP (e.g., `11.0.0.1` meant "acknowledge", `11.0.0.2` meant "send next chunk").

By monitoring for high-frequency queries to a single external domain with highly entropic, sequentially numbered subdomains, defenders successfully identified and severed the Helminth C2 channel.

## 8. Advanced Evasion Techniques
- **DNS over HTTPS (DoH):** Attackers increasingly tunnel their DNS payloads directly over HTTPS to public resolvers (e.g., Cloudflare 1.1.1.1, Google 8.8.8.8). This makes the tunnel appear as standard TLS traffic, entirely bypassing `dns.log` monitoring.
- **Timing and Jitter:** Instead of blasting thousands of queries, advanced malware trickles the data out over days or weeks (e.g., one query every hour) to fly under volumetric threshold alerts.
- **Steganography in DNS:** Embedding malicious data within seemingly legitimate CNAME or SPF strings.

## 9. Incident Response Playbook

1. **Identification:**
   - Detect spikes in DNS requests matching a specific pattern or base domain.
   - Capture PCAP and extract the payload. Reverse engineer the encoding scheme to verify if sensitive data was successfully exfiltrated.
2. **Containment:**
   - Immediately block the base domain (e.g., `evil-domain.com`) at the DNS forwarder level.
   - Isolate the endpoint generating the traffic to halt data exfiltration.
3. **Eradication:**
   - Perform host-based forensics to locate the binary generating the tunnel requests (often a modified version of `dnscat2` or a custom implant).
   - Terminate the process and remove persistence mechanisms.
4. **Recovery:**
   - Review which files were exfiltrated by decoding the PCAP.
   - If sensitive intellectual property or credentials were stolen, initiate the corresponding breach notification and credential rotation procedures.

## 10. Chaining Opportunities
- Attackers rarely rely on a single channel. If DNS tunneling is detected, look for secondary persistence mechanisms attempting lateral movement via SMB or RDP. Pivot to [[09 - Detecting Lateral Movement via SMB and RDP]].
- Look at the endpoint executing the DNS queries. If it's a web server, the initial infection vector might have been a web shell. Pivot to [[10 - Hunting for Web Shells in HTTP Traffic]].
- For heavily encrypted tunneling, review [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]].

## 11. Related Notes
- [[06 - Detecting Domain Generation Algorithms DGAs]]
- [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]]
- [[10 - Hunting for Web Shells in HTTP Traffic]]
