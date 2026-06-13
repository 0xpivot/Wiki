---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.10 Hunting for Web Shells in HTTP Traffic"
---

# 90.10 Hunting for Web Shells in HTTP Traffic

## 1. Introduction to Web Shells

A web shell is a malicious script (written in PHP, ASP, JSP, or Python) uploaded to a compromised web server. It provides an adversary with a persistent, web-based interface to execute system commands, manage files, and pivot into the internal network. 

Because web shells operate over standard HTTP/HTTPS ports (80/443), their traffic naturally blends in with legitimate web server communications. The challenge for threat hunters is identifying the subtle anomalies that differentiate an attacker interacting with a web shell from a legitimate user interacting with a web application.

### 1.1 Types of Web Shells
- **One-Liners:** Tiny scripts like `<?php system($_GET['cmd']); ?>` that are easily hidden but lack advanced features.
- **Full-Featured:** Extensive scripts like `b374k`, `WSO`, or `C99` that provide full GUI interfaces, database management, and network scanning capabilities.
- **Memory-Resident / Fileless:** Web shells injected directly into the web application framework's memory (e.g., Tomcat filters, IIS modules) leaving no file on disk.

## 2. Web Shell Interaction Architecture

```text
    [Attacker / Client]                                    [Compromised Web Server]
    (Using Browser or Script)                              (10.0.5.20)
             |                                                    |
             | 1. Upload Web Shell via                            |
             |    File Upload Vulnerability / RCE                 |
             | -------------------------------------------------> |
             |                                                    |
             |                                              +-----+-----+
             |                                              | shell.php | Written to disk
             |                                              +-----+-----+
             | 2. HTTP POST Request                               |
             |    URI: /uploads/shell.php                         |
             |    Body: cmd=Y2F0IC9ldGMvcGFzc3dk (Base64)         |
             | -------------------------------------------------> |
             |                                                    |
             |                                              [Executes Command]
             |                                                    |
             | 3. HTTP 200 OK Response                            |
             |    Body: root:x:0:0:root:/root:/bin/bash           |
             | <------------------------------------------------- |
```

## 3. Web Shell Traffic Characteristics

Hunting web shells via network telemetry focuses on traffic anomalies, execution artifacts, and obfuscation signatures.

1. **High POST-to-GET Ratio:** Legitimate web browsing involves many GET requests (images, CSS, HTML) and occasional POSTs. Web shell interaction is almost exclusively POST requests to a single URI, to prevent commands from being logged in web server access logs via GET parameters.
2. **Anomalous User-Agents:** Attackers often use automated tools or custom scripts (like Python-Requests or curl) without bothering to spoof legitimate browser User-Agents.
3. **Execution Output in Responses:** The HTTP responses will frequently contain command-line output (`uid=0(root)`, `Directory of C:\`, `Volume in drive C`).
4. **Obfuscation and Encoding:** Payloads sent to the shell are often Base64 encoded, XOR'd, or encrypted to evade simple keyword-matching IDS rules.

## 4. Threat Hunting with Zeek

Zeek's `http.log` provides comprehensive metadata for hunting web shells, allowing analysts to aggregate and baseline web traffic.

### 4.1 Hunting by File Extensions and URI Anomalies
Web shells are often dropped in directories meant for static content, like `/images/` or `/uploads/`. If a `.php` or `.jsp` file is being executed from an image directory, it is highly suspicious.

```bash
# Search http.log for executable scripts running from upload directories
cat http.log | zeek-cut id.orig_h method uri status | grep -E "\/uploads\/.*\.php"
```

### 4.2 Hunting by MIME-Type Mismatch
An attacker might rename `shell.php` to `shell.jpg` to bypass upload restrictions, but configure the server via `.htaccess` to execute it as PHP. Zeek analyzes the actual content transferred, not just the extension.

```bash
# Look for mismatched MIME types in HTTP responses
cat http.log | zeek-cut uri resp_mime_types | grep "image/jpeg" | grep "\.php"
```

### 4.3 Zeek Script: Detecting Command Output in HTTP Responses
This conceptual script inspects HTTP response bodies for common Linux command outputs, indicating a successful web shell execution.

```zeek
module WebShell_Hunt;

export {
    redef enum Notice::Type += { Potential_WebShell_Output };
    const suspicious_strings: pattern = /uid=[0-9]+\(.*\)|root:x:0:0/ ;
}

event http_entity_data(c: connection, is_orig: bool, length: count, data: string)
    {
    if ( ! is_orig && suspicious_strings in data )
        {
        NOTICE([$note=Potential_WebShell_Output,
                $msg=fmt("Suspicious command output detected in response from %s", c$http$uri),
                $conn=c]);
        }
    }
```

## 5. Threat Hunting with Suricata

Suricata is exceptionally adept at identifying the specific signatures of well-known web shells like **China Chopper**, **Weevely**, and **AntSword**.

### 5.1 Suricata Rule for China Chopper
China Chopper is an incredibly common, tiny web shell. The client interacts with the server using a very specific POST body structure containing `&z0=` and Base64 encoded payload.

```suricata
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS (msg:"ET EXPLOIT China Chopper Web Shell Interaction"; flow:established,to_server; content:"POST"; http_method; content:"&z0="; http_client_body; pcre:"/&z0=[A-Za-z0-9\+\/]+={0,2}/P"; classtype:web-application-attack; sid:5050001; rev:1;)
```

### 5.2 Detecting System Commands in URI
For simple one-liner GET-based web shells, attackers pass commands directly in the URI.

```suricata
alert http $EXTERNAL_NET any -> $HTTP_SERVERS any (msg:"ET HUNTING Suspicious OS Command in URI (Possible Web Shell)"; http.uri; pcre:"/(?:cmd|exec|system|passthru)=.*(?:cat|ls|whoami|id|pwd|wget)/i"; classtype:web-application-attack; sid:5050002; rev:1;)
```

## 6. Threat Hunting with PCAP and Wireshark

When isolating a web shell incident, PCAP analysis allows for full reconstruction of the attacker's actions.

### 6.1 Wireshark Display Filters
- Filter for all POST requests: `http.request.method == "POST"`
- Search for common Linux commands in the payload: `http.file_data contains "whoami" or http.file_data contains "/bin/bash"`
- Filter HTTP responses containing error messages typical of failed shell execution: `http.response.line contains "PHP Parse error"`

### 6.2 Following the TCP Stream
By right-clicking a suspicious HTTP POST packet and selecting **Follow -> TCP Stream**, you can view the entire request and response in plaintext. If the traffic is encrypted (HTTPS), you must provide Wireshark with the server's private RSA key or the TLS session keys (via SSLKEYLOGFILE) to decrypt and analyze the payload.

## 7. Real-World Attack Scenario

### 7.1 HAFNIUM and the ProxyLogon Exchange Vulnerability
In early 2021, the APT group HAFNIUM exploited zero-day vulnerabilities (ProxyLogon - CVE-2021-26855) in Microsoft Exchange servers globally. 

**Attack Flow:**
1. **SSRF Exploitation:** HAFNIUM utilized an SSRF vulnerability to authenticate as the local system.
2. **Web Shell Deployment:** They exploited a secondary arbitrary file write vulnerability to drop an ASPX web shell (often named `discover.aspx` or `help.aspx`) directly into the Exchange server's `OAB` (Offline Address Book) directory.
3. **Execution and Persistence:** The attackers sent HTTP POST requests containing China Chopper payloads to the dropped ASPX file. Because the web shell was running in the context of the Exchange worker process (which has high privileges), they instantly executed `whoami`, extracted the LSASS memory, and deployed secondary Cobalt Strike beacons.

Network defenders hunting for this activity relied heavily on PCAP and Zeek logs. The key indicator was a sudden spike in POST requests to anomalous `.aspx` files located in `/owa/auth/` or `/OAB/` directories, originating from foreign IP addresses.

## 8. Advanced Evasion Techniques
- **Steganography in Exfiltration:** Embedding command output in the Exif data of images returned by the web server to completely evade HTTP body inspection.
- **Time-Stomping:** Attackers will modify the MAC (Modified, Accessed, Created) timestamps of the dropped web shell to match legitimate files in the directory (e.g., setting the timestamp to 2018), making it harder to find via `find -mtime` forensic searches.
- **Custom Encryption:** Advanced shells like AntSword encrypt the POST bodies using AES, meaning NIDS and Zeek will only see binary blobs traversing the network, completely defeating keyword-based signature rules.

## 9. Incident Response Playbook

1. **Identification:**
   - Review WAF (Web Application Firewall) alerts for anomalous POST behavior or remote code execution attempts.
   - Correlate network alerts with File Integrity Monitoring (FIM) tools on the web server to verify if a new file was created.
2. **Containment:**
   - Revoke public access to the compromised server. Do not just delete the web shell file immediately, as the attacker may have a memory-resident backup or may trigger a destructive payload upon deletion.
   - Take a memory dump and disk snapshot of the server.
3. **Eradication:**
   - Remove the web shell file and clear any scheduled tasks or cron jobs created by the attacker.
   - Patch the vulnerability that allowed the initial file upload.
4. **Recovery:**
   - Restore the application from a known good backup.
   - Implement strict egress filtering on the web server (web servers generally should not be initiating outbound connections to the internet).

## 10. Chaining Opportunities
- Once a web shell is established, the attacker will attempt to move laterally deeper into the network using SMB or RDP. Pivot to [[09 - Detecting Lateral Movement via SMB and RDP]].
- If the web shell deploys a secondary implant (like a Cobalt Strike beacon), that beacon will likely communicate out via encrypted channels or DNS. Pivot to [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]] and [[07 - Hunting for DNS Tunneling and Exfiltration]].

## 11. Related Notes
- [[07 - Hunting for DNS Tunneling and Exfiltration]]
- [[08 - Analyzing Suspicious TLS SSL Traffic JA3 Fingerprinting]]
- [[09 - Detecting Lateral Movement via SMB and RDP]]
