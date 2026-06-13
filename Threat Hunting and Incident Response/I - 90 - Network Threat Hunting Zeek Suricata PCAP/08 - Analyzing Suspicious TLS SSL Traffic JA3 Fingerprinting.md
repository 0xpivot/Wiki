---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.08 Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting"
---

# 90.08 Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting

## 1. Introduction to Encrypted Traffic Analysis

As the internet has shifted almost entirely to encrypted communications (TLS/SSL), so too have malicious actors. Over 90% of malware now utilizes TLS to encrypt its Command and Control (C2) channels and data exfiltration. Traditional network intrusion detection systems (NIDS) that rely on deep packet inspection (DPI) to match static payload signatures are rendered blind by encryption.

To counter this, threat hunters must pivot from analyzing the *content* of the packet to analyzing the *context* and *metadata* of the encrypted session. This includes evaluating certificate anomalies, beaconing patterns, and most importantly, cryptographic fingerprinting techniques like **JA3** and **JA3S**.

### 1.1 What is JA3?
Developed by researchers at Salesforce (John Althouse, Jeff Atkinson, and Josh Atkins—hence "JA3"), JA3 is a method for creating SSL/TLS client fingerprints. 
Every TLS client (e.g., Chrome, Firefox, a Python script, a Metasploit payload) utilizes specific libraries (OpenSSL, SChannel, NSS). When initiating a connection, the client sends a "Client Hello" packet containing the TLS version, accepted cipher suites, and extensions. Because different applications and libraries build this Client Hello differently, the combination of these fields acts as a highly unique fingerprint.

## 2. The JA3 Fingerprinting Architecture

```text
    [Malware / Client]                                    [C2 / Web Server]
    (e.g., TrickBot payload)                              (e.g., Nginx)
             |                                                    |
             | 1. TLS Client Hello                                |
             |    - Version: TLS 1.2                              |
             |    - Ciphers: 49195, 49196, 52393...               |
             |    - Extensions: 0, 10, 11, 35, 16...              |
             | -------------------------------------------------> |
             |                                                    |
   +---------|----------------------------------------------------+
   |         v                                                    
   |  [Network Sensor (Zeek/Suricata)]                            
   |    Extracts parameters:                                      
   |    771,49195-49196-52393,0-10-11-35-16,29-23-24,0            
   |    Hashes to MD5: 6734f37431670b3ab4292b8f60f29984 (JA3)     
   |                                                              
   +--------------------------------------------------------------+
             |                                                    |
             | 2. TLS Server Hello                                |
             |    - Version: TLS 1.2                              |
             |    - Cipher Chosen: 49195                          |
             |    - Extensions: 0, 11, 16                         |
             | <------------------------------------------------- |
   +---------|----------------------------------------------------+
   |         v
   |  [Network Sensor]
   |    Hashes Server Hello to MD5 (JA3S)
   |    Matches JA3 + JA3S against Threat Intel Feeds
   +--------------------------------------------------------------+
```

## 3. How JA3 and JA3S Work

**JA3 (Client Fingerprint):**
The JA3 string is built by concatenating the decimal values of the following fields from the Client Hello, separated by commas:
`SSLVersion,CipherSuites,Extensions,EllipticCurves,EllipticCurveFormats`
This string is then MD5 hashed to produce a 32-character fingerprint.
*Example JA3:* `cd08e31494f9531f560d64c695473da9` (Standard Windows 10 Chrome client).

**JA3S (Server Fingerprint):**
JA3S fingerprints the Server Hello. It is simpler because the server only responds with the selected cipher and extensions. 
The combination of a specific malware JA3 and its corresponding C2 infrastructure JA3S forms a highly reliable dual-indicator. Even if the attacker changes their IP and Domain, if they use the same malware binary and C2 server software, the JA3/JA3S pair remains identical.

## 4. Threat Hunting with Zeek

Zeek natively supports extracting SSL metadata via the `ssl.log` file, and JA3/JA3S support is easily added via the `ja3.zeek` package.

### 4.1 Analyzing ssl.log for Anomalies
A fundamental hunting technique is looking for self-signed certificates, recently created certificates, or certificates with anomalous subject names.

```bash
# Find connections using self-signed certificates (where Issuer equals Subject)
cat ssl.log | zeek-cut id.orig_h server_name subject issuer | awk -F'\t' '{if ($3 == $4) print $0}'
```

### 4.2 Hunting with JA3 Hashes
You can match the JA3 hashes generated by Zeek against known malicious hashes (e.g., from abuse.ch's SSL Blacklist).

```bash
# Extract the top 10 most rare JA3 hashes in the environment (potential anomalies)
cat ssl.log | zeek-cut ja3 | sort | uniq -c | sort -n | head -n 10
```

*Note: A rare JA3 isn't always malicious (it could be an obscure IoT device or old script), but it is the starting point for anomalous hunting.*

### 4.3 Zeek Script for JA3 Blacklisting
This script conceptually loads a known bad JA3 hash (e.g., Cobalt Strike default Beacon) and alerts when it traverses the network.

```zeek
@load /usr/share/zeek/site/ja3

module Malicious_JA3;

export {
    redef enum Notice::Type += { Known_Bad_JA3_Observed };
    const bad_ja3_hashes: set[string] = {
        "a0e9f5d64349fb13191bc781f81f42e1", # Example Trickbot JA3
        "c810842db7402dc4e9e0dcc7e089606d"  # Example Cobalt Strike JA3
    };
}

event ssl_client_hello(c: connection, version: count, record_version: count, possible_ts: time, client_random: string, session_id: string, ciphers: index_vec, comp_methods: index_vec)
    {
    if ( c$ssl?$ja3 && c$ssl$ja3 in bad_ja3_hashes )
        {
        NOTICE([$note=Known_Bad_JA3_Observed,
                $msg=fmt("Malicious JA3 Hash %s observed heading to %s", c$ssl$ja3, c$id$resp_h),
                $conn=c]);
        }
    }
```

## 5. Threat Hunting with Suricata

Suricata integrates the JA3 fingerprint natively into its ruleset, allowing for high-performance, real-time blocking or alerting.

### 5.1 Suricata Rule for Malicious JA3
If threat intelligence feeds provide a JA3 for a newly discovered ransomware variant, a rule can be rapidly deployed:

```suricata
alert tls $HOME_NET any -> $EXTERNAL_NET any (msg:"ET MALWARE Suspicious Cobalt Strike Default JA3 Fingerprint"; ja3.hash; content:"c810842db7402dc4e9e0dcc7e089606d"; classtype:command-and-control; sid:3030001; rev:1;)
```

### 5.2 Combining JA3 and SNI
Attackers often attempt "Domain Fronting" or host malicious payloads on legitimate cloud providers (e.g., AWS CloudFront, Azure). By combining a suspicious JA3 with a legitimate Server Name Indication (SNI), defenders can identify malware hiding in trusted cloud infrastructure.

```suricata
alert tls $HOME_NET any -> $EXTERNAL_NET any (msg:"ET MALWARE Python Requests JA3 heading to CDN (Possible C2)"; ja3.hash; content:"cd08e31494f9531f560d64c695473da9"; tls.sni; content:"cloudfront.net"; classtype:bad-unknown; sid:3030002; rev:1;)
```

## 6. Threat Hunting with PCAP and Wireshark

When examining raw packet captures, extracting the JA3 string manually helps verify automated alerts.

### 6.1 Wireshark Display Filters
- Filter for Client Hello packets: `tls.handshake.type == 1`
- Filter for Server Hello packets: `tls.handshake.type == 2`
- Filter for a specific JA3 hash (requires Wireshark 2.9.0+): `tls.handshake.ja3 == "c810842db7402dc4e9e0dcc7e089606d"`

To manually calculate it, you must expand the TLS layer -> Handshake Protocol -> Client Hello -> and evaluate the Cipher Suites and Extensions arrays.

## 7. Real-World Attack Scenario

### 7.1 Emotet and TrickBot C2 Beaconing
During a massive ransomware campaign in 2021, the Emotet loader was used to deploy TrickBot, which eventually dropped Ryuk ransomware. 
TrickBot communicates over HTTPS to various compromised residential routers acting as C2 proxies. Because the IP addresses were constantly changing and the domains were absent (direct IP communication), traditional blocklists failed.

**The Hunt:**
Defenders noticed rhythmic, periodic TLS connections (beaconing) occurring every 5 minutes (with 10% jitter) to external IPs. 
By analyzing the `ssl.log` in Zeek, hunters isolated the connection. Because TrickBot used a statically compiled Windows cryptography library with a very specific, rare set of ciphers and absent SNI, it produced a highly unique JA3 fingerprint.
Furthermore, the compromised C2 servers were running a specific version of Nginx that responded with an equally unique JA3S.
By pivoting on the `JA3 + JA3S` combination, the SOC was able to retrospectively query their SIEM and identify every infected host across the global enterprise instantly, despite the encryption hiding the payload.

### 7.2 The Limitations and Evolution (JA4)
It is important to note that sophisticated adversaries now utilize "Cipher Stunting"—randomizing their Client Hello parameters to change their JA3 hash on every request. To combat this, newer fingerprinting standards like **JA4+** are being developed, which incorporate network-level parameters (TCP window size) and behavioral metadata to create fingerprints that are significantly harder for attackers to randomize.

## 8. Advanced Evasion Techniques
- **TLS 1.3 Encrypted Client Hello (ECH):** A newer standard where the SNI and many extensions are encrypted. This heavily limits the visibility of NIDS and may reduce the effectiveness of standard JA3 matching if widely adopted by malware.
- **Malleable C2 Profiles:** Frameworks like Cobalt Strike allow operators to craft their TLS profiles to exactly mimic legitimate traffic (like mimicking a standard Firefox JA3 to AWS).
- **Cipher Stunting:** Dynamically altering the cipher suite list sent in the Client Hello for every single request to prevent a static JA3 hash from ever matching a blocklist.

## 9. Incident Response Playbook

1. **Identification:**
   - Detect matching JA3 hashes against a known threat feed (e.g., abuse.ch JA3 lists).
   - Investigate the endpoint for periodic beaconing over port 443 to suspicious or low-reputation IP addresses.
2. **Containment:**
   - Implement network blocks on the destination IP addresses or domains identified via SNI.
   - Quarantine the infected workstation.
3. **Eradication:**
   - Extract the active memory from the host to find the decrypted malware payload.
   - Run advanced EDR tools to eliminate the persistent binary.
4. **Recovery:**
   - Confirm all C2 traffic has ceased.
   - Review SIEM logs for any signs of data exfiltration over the identified TLS channel before containment occurred.

## 10. Chaining Opportunities
- Encrypted C2 channels often execute commands that result in lateral movement. If a malicious JA3 is spotted, the hunter must pivot to analyzing internal logs for PsExec, WMI, or RDP from that host. Pivot to [[09 - Detecting Lateral Movement via SMB and RDP]].
- If the TLS traffic reveals an SNI belonging to the enterprise's own external web applications, an attacker may be interacting with a backdoor. Pivot to [[10 - Hunting for Web Shells in HTTP Traffic]].

## 11. Related Notes
- [[06 - Detecting Domain Generation Algorithms DGAs]]
- [[07 - Hunting for DNS Tunneling and Exfiltration]]
- [[09 - Detecting Lateral Movement via SMB and RDP]]
