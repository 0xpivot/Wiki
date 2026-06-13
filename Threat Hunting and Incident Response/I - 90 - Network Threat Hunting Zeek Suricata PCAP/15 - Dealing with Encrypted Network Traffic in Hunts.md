---
tags: [threat-hunting, network, pcap, zeek, vapt]
difficulty: intermediate
module: "90 - Network Threat Hunting: Zeek, Suricata, PCAP"
topic: "90.15 Dealing with Encrypted Network Traffic in Hunts"
---

# Dealing with Encrypted Network Traffic in Hunts

## The Challenge of Ubiquitous Encryption
In the modern enterprise network, over 90% of all web traffic is encrypted via TLS (Transport Layer Security). While encryption is essential for privacy and security, it completely breaks traditional, payload-centric intrusion detection systems (IDS) and full packet capture (PCAP) analysis. When an adversary establishes a command and control (C2) channel or exfiltrates data over HTTPS, the network sensor only sees encrypted ciphertext. The underlying HTTP requests, User-Agent strings, requested URIs, and transferred files are entirely hidden.

To deal with this, organizations have two choices:
1. **TLS Inspection (Break and Inspect / MITM):** Using a proxy or firewall to decrypt the traffic, inspect the payload, and re-encrypt it. While effective, this is expensive, resource-intensive, introduces latency, and creates massive privacy and compliance headaches (e.g., decrypting banking or healthcare traffic). Furthermore, modern malware often uses Certificate Pinning, rendering MITM inspection impossible without breaking the communication entirely.
2. **Metadata and Behavioral Analysis:** The approach preferred by modern threat hunters. Instead of trying to decrypt the payload, hunters analyze the unencrypted metadata exchanged during the TLS handshake, combined with flow metrics (volume, timing), to identify malicious behavior.

## The Architecture of TLS Metadata Extraction

The TLS handshake contains a wealth of unencrypted information before the secure tunnel is established. 

```ascii
+-----------------------------------------------------------------------------------+
|                            THE TLS 1.2 HANDSHAKE                                    |
|                                                                                   |
|  +--------------------+                                   +--------------------+  |
|  |     CLIENT         |                                   |       SERVER       |  |
|  |   (Compromised)    |                                   |     (C2 Server)    |  |
|  +--------------------+                                   +--------------------+  |
|          |                                                          |             |
|          | 1. Client Hello (Cleartext)                              |             |
|          |    - TLS Version                                         |             |
|          |    - Cipher Suites Supported                             |             |
|          |    - Extensions: SNI (Server Name Indication)            |             |
|          |    - Extensions: ALPN (Protocol Negotiation)             |             |
|          |--------------------------------------------------------->|             |
|          |                                                          |             |
|          |                        2. Server Hello (Cleartext)       |             |
|          |                           - Chosen Cipher Suite          |             |
|          |                        3. Certificate (Cleartext in 1.2) |             |
|          |                           - Subject, Issuer, Validity    |             |
|          |<---------------------------------------------------------|             |
|          |                                                          |             |
|          | 4. Key Exchange & Cipher Spec (Encrypted)                |             |
|          |--------------------------------------------------------->|             |
|          |                                                          |             |
|          |                        5. Cipher Spec (Encrypted)        |             |
|          |<---------------------------------------------------------|             |
|          |                                                          |             |
|          | ================== SECURE TUNNEL ESTABLISHED =========== |             |
+----------|----------------------------------------------------------|-------------+
           v                                                          v
+-----------------------------------------------------------------------------------+
|                              ZEEK SENSOR LOGS                                       |
|  +-------------------------+  +------------------------+  +--------------------+  |
|  |       ssl.log           |  |       x509.log         |  |      conn.log      |  |
|  |  (SNI, JA3, JA3S, ALPN) |  | (Cert Issuer, Subject) |  | (Bytes, Duration)  |  |
|  +-------------------------+  +------------------------+  +--------------------+  |
+-----------------------------------------------------------------------------------+
```
*Note: In TLS 1.3, the server certificate is encrypted, hiding the X.509 metadata, making SNI and JA3 even more critical.*

## Advanced Threat Hunting Strategies without Decryption

### 1. JA3 and JA3S Fingerprinting
JA3, developed by Salesforce researchers, is a method for creating SSL/TLS client fingerprints. It hashes the specific, unencrypted fields sent in the `Client Hello` packet (TLS Version, Accepted Ciphers, List of Extensions, Elliptic Curves, and Elliptic Curve Formats). 
Because different applications use different TLS libraries (e.g., Chrome uses BoringSSL, Python uses OpenSSL, malware might use a custom minimal TLS stack), they generate unique JA3 hashes.

- **JA3:** Fingerprints the Client (the malware/browser).
- **JA3S:** Fingerprints the Server (the C2 infrastructure response).

**Hunting Strategy:** 
Maintain a database of known good JA3 hashes for your environment (e.g., the hash for Chrome on Windows 10, the hash for legitimate Windows Updates). Alert on rare or anomalous JA3 hashes making outbound connections. If an endpoint typically only exhibits the JA3 hash of Microsoft Edge, but suddenly exhibits the JA3 hash of a standard Python 3 `urllib` library connecting to an uncategorized IP, it strongly indicates a Python-based backdoor has been executed.

### 2. SNI (Server Name Indication) Analysis
SNI is an extension in the `Client Hello` that tells the server which hostname the client is attempting to connect to (necessary for servers hosting multiple virtual domains on one IP). 
- **Hunting Strategy:** Monitor the SNI field in Zeek's `ssl.log` and compare it to the actual IP address requested. If the SNI is `www.google.com`, but the destination IP belongs to a cheap VPS provider in Eastern Europe, it is a massive anomaly. Attackers frequently spoof SNI to bypass lazy firewall rules that only inspect the SNI field without verifying the IP reputation.

### 3. Certificate Anomalies (x509.log)
If the connection is TLS 1.2 or below, the server's certificate is sent in cleartext. Hunters can analyze this certificate for signs of malicious infrastructure.
- **Let's Encrypt Abuse:** While Let's Encrypt is a fantastic service for legitimate webmasters, it is also heavily abused by attackers because certificates are free and automated. An internal server making an outbound connection to a newly registered domain secured by a Let's Encrypt certificate should be scrutinized.
- **Self-Signed Certificates:** Legitimate public services rarely use self-signed certificates. Malware frameworks like Metasploit often generate self-signed certs by default. Look for certificates where the `Issuer` is exactly the same as the `Subject`, or where the `Subject` contains random alphanumeric strings.
- **Short Validity Periods:** Attackers know their infrastructure will be burned quickly, so they often use certificates valid for only 30 to 90 days.

### 4. Domain Fronting Detection
Domain Fronting is an evasion technique where an attacker uses a legitimate, highly trusted CDN (like Cloudflare or AWS CloudFront) to hide their C2 traffic. They put a trusted domain in the SNI (e.g., `ajax.microsoft.com`), but inside the encrypted HTTP tunnel, they place their malicious domain in the actual HTTP `Host` header. The CDN routes the traffic to the attacker based on the encrypted Host header.
- **Hunting Strategy without Decryption:** Domain fronting breaks the correlation between the DNS request and the destination IP. If an endpoint resolves `malicious-c2.com`, but the subsequent TLS connection has an SNI of `ajax.microsoft.com` going to an AWS edge node, this discrepancy indicates domain fronting.

## Real-World Attack Scenario

### The Scenario: Custom Go Malware via Let's Encrypt
A sophisticated threat actor compromised an HR workstation (`10.30.40.55`) and deployed a custom backdoor compiled in Go.

### The Attack Flow
1. **Infrastructure Setup:** The attacker registered a deceptive domain (`update-windows-service.com`) and obtained a free TLS certificate from Let's Encrypt.
2. **Execution:** The Go binary executed on the endpoint. Instead of using the native Windows cryptographic API (which would generate a standard Windows JA3 hash), the Go binary used its own statically compiled cryptographic libraries.
3. **Communication:** The malware established a TLS 1.2 connection to the attacker's server (`198.51.100.12`).

### How Metadata Analysis Detected the Activity
1. **JA3 Anomaly:** The threat hunter was reviewing a dashboard of rare JA3 hashes on the network. A new JA3 hash appeared originating from the HR subnet. Because the Go crypto library is unique, its JA3 hash did not match any known web browser or legitimate Windows background service.
2. **Pivoting to SSL Logs:** The hunter queried the SIEM for that specific JA3 hash. They found it was connecting to the IP `198.51.100.12`.
3. **Analyzing the X.509 Certificate:** The hunter examined the corresponding `x509.log` for that connection. They noted the certificate was issued by Let's Encrypt and the Subject Common Name (CN) was `update-windows-service.com`.
4. **Threat Intelligence Correlation:** Checking the domain against a WHOIS database revealed it was registered only 48 hours ago. A newly registered domain, secured via Let's Encrypt, communicating with a non-standard JA3 client hash provided overwhelming evidence of malicious C2 activity. 
5. **Correlation to Endpoint:** The hunter took the 5-tuple from the Zeek logs and queried Sysmon Event ID 3, instantly identifying the malicious `hr_document_v2.exe` (the compiled Go binary) as the source of the traffic.

## Best Practices for TLS Hunting
- **Embrace Zeek:** Ensure Zeek is properly configured to log `ssl.log` and `x509.log`. Ensure the JA3 script is loaded and functioning.
- **Baseline Your Environment:** You cannot find anomalous JA3 hashes if you don't know the baseline hashes of your legitimate applications (O365, internal custom apps, standard browsers).
- **Correlate with Endpoint:** A strange JA3 hash is only a pointer. You must correlate it with endpoint telemetry to determine exactly which process generated it.

## Chaining Opportunities
- **[[08 - Understanding Zeek Architecture and Logs]]**: Zeek is the primary tool for extracting TLS metadata like JA3, SNI, and X.509 without performing decryption.
- **[[14 - Correlating Network and Endpoint Events]]**: Once an anomalous TLS metadata fingerprint is found, correlation is required to identify the specific process on the host.
- **[[12 - Detecting Suspicious User Agent Strings]]**: In environments where TLS inspection *is* performed, correlating the decrypted User-Agent string against the TLS JA3 hash is the most robust method for detecting spoofing.

## Related Notes
- [[11 - Analyzing Network Flow NetFlow IPFIX Data]]
- [[13 - RITA Real Intelligence Threat Analytics for C2]]
- [[04 - Threat Hunting Methodologies]]
- [[22 - Advanced Persistent Threats (APTs) Tactics]]
