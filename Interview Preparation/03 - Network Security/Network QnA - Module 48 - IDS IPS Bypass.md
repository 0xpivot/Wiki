---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 48"
---

# Network QnA - Module 48: IDS/IPS Bypass Techniques

This document delves into the intricate methods attackers use to circumvent Intrusion Detection Systems (IDS) and Intrusion Prevention Systems (IPS), focusing on stream reassembly, protocol mutation, and timing attacks.

## Formal Technical Questions

**Q1: Explain the concept of "TCP Session Splicing." How does it evade signature-based IDS, and what specific tool popularized this technique?**
*Answer:*
TCP Session Splicing is an evasion technique where an attacker delivers their payload across multiple, extremely small TCP segments.
*   **Mechanism:** Instead of sending an HTTP GET request with a malicious payload in a single packet, the attacker breaks the payload down so that each TCP packet carries only 1 or 2 bytes of the payload.
*   **The Evasion:** Early or poorly configured signature-based IDSes (like older Snort versions without Stream5 preprocessors) would inspect each packet individually. Since a signature for `cmd.exe` is 7 bytes long, an IDS looking at a 1-byte packet will never trigger the signature.
*   **The Tool:** The tool `whisker` (and later `Nikto` via LibWhisker) popularized this for web attacks.
*   **The Defense:** Modern IDSes use stream reassembly engines (like Snort's `stream_tcp`). They buffer the TCP segments, reassemble the entire stream into a virtual buffer, and *then* run the signature matching against the full reassembled stream.

**Q2: What is "Polymorphic Shellcode," and why does it render static IPS signatures obsolete? Detail the structural components of a polymorphic payload.**
*Answer:*
Polymorphic shellcode is executable code that changes its binary signature every time it is generated, while keeping its underlying functionality intact.
*   **The Evasion:** IPS engines rely on known byte sequences (signatures) to identify malware (e.g., a specific sequence of NOP sleds or the exact hex of a `/bin/sh` execve call). Polymorphism alters these bytes, defeating exact-match signatures.
*   **Components:**
    1.  **NOP Sled Mutation:** Instead of using standard `0x90` (NOP) instructions, the engine uses equivalent innocuous instructions (e.g., `INC EAX; DEC EAX`, or `XCHG EBX, EBX`).
    2.  **Decoder Stub:** The actual malicious shellcode is encrypted (e.g., using a rotating XOR key). A small, dynamically generated decoder stub is placed at the beginning of the payload.
    3.  **Encrypted Payload:** The encoded malicious instructions.
*   **Execution:** When the target executes the payload, the decoder stub runs first, decrypts the payload in memory, and jumps to it. Since the encryption key and the decoder stub's assembly instructions change every time, the network signature is entirely randomized.

**Q3: Describe the "Insertion Attack" in the context of IDS evasion. How does it rely on differences in protocol parsing between the IDS and the target host?**
*Answer:*
An insertion attack aims to confuse the IDS into reading data that the actual target host will discard.
*   **Mechanism:** The attacker inserts garbage packets into the data stream that the IDS will process, but the target system will drop due to strict RFC adherence or OS-specific IP stack behavior.
*   **Example (Bad Checksum):** An attacker sends a TCP stream containing the payload `A T T A C K`. They intentionally send the `T` and `C` packets with an invalid TCP checksum.
*   **The Result:** The IDS (if improperly configured) might ignore the bad checksum, process all packets, and reconstruct the stream as `A T T A C K`. The target host's OS kernel, strictly adhering to RFCs, silently drops the packets with bad checksums. The target host reconstructs `A A K`.
*   **The Impact:** The attacker has "inserted" characters into the IDS's view of the stream, effectively blinding it to the true payload that reached the target.

## Scenario-Based Questions

**Q4: You are targeting a web server protected by an inline Suricata IPS. Standard directory traversal (`../../../etc/passwd`) is immediately blocked. How do you mutate the protocol to bypass the IPS while still having the web server process the request?**
*Answer:*
I will employ protocol mutation and encoding evasions:
1.  **URL Encoding Variations:** Standard `%2E%2E%2F` might be caught. I will try double URL encoding (`%252e%252e%252f`), hex encoding, or non-standard UTF-8 Unicode overlong encodings (e.g., `%c0%ae%c0%ae%c0%af`).
2.  **Directory Self-Referencing:** I can pad the path with excessive self-referential directories: `//././././../../../././etc/./passwd`. The IPS might have a finite regex evaluation limit and time out, while the backend Apache/Nginx server will normalize it.
3.  **HTTP Parameter Pollution (HPP):** If the payload is via GET parameters, I will split the payload across multiple parameters with the same name: `?file=.../&file=../&file=etc/passwd`. The IPS might only inspect the first parameter, while the backend application concatenates them.
4.  **Whitespace Mutation:** I will replace standard spaces with alternative whitespaces (Tab `%09`, Carriage Return `%0d`, Line Feed `%0a`) which the IPS regex might fail to account for, but the web server normalizes.

**Q5: During a penetration test, you successfully compromise a DMZ server. You need to establish a C2 channel to the internet, but the corporate Next-Gen IPS blocks all outbound connections that don't match strict protocol definitions (e.g., only HTTP/TLS allowed). How do you establish C2?**
*Answer:*
I need to use a Covert Channel via Protocol Tunneling.
*   **DNS Tunneling:** Even strict environments usually allow the DMZ to query internal DNS, which recursively queries the internet. I will use a tool like `Iodine` or `dnscat2`. My C2 commands will be encoded as subdomains in DNS TXT or CNAME requests (e.g., `base64_payload.attacker.com`). The IPS sees standard DNS traffic.
*   **ICMP Tunneling:** If ping is allowed outbound for monitoring, I can use `ptunnel` to encapsulate my C2 traffic within the data payload of ICMP Echo Request/Reply packets.
*   **TLS SNI Routing / Domain Fronting:** I will wrap my C2 in standard TLS on port 443. To bypass the IPS's SNI filtering, I will use Domain Fronting (if a suitable CDN is available) or use a legitimate-looking SNI while the actual encrypted HTTP Host header routes to my infrastructure.

**Q6: You are using `fragroute` to attack a target. You select a configuration that uses TCP overlapping segments with differing data. What specific OS fingerprinting knowledge do you need to make this attack successful against the target while evading the IDS?**
*Answer:*
TCP overlapping occurs when two TCP segments have sequence numbers that cover the same byte range in the stream, but contain different payload data.
*   **The OS Fingerprinting Requirement:** I must know exactly how the *target OS* handles overlapping segments (the Reassembly Policy).
    *   **First-In (Windows):** The OS prefers the original data and discards the new overlapping data.
    *   **Last-In (Linux/Cisco):** The OS prefers the new overlapping data and overwrites the original data.
*   **The Attack Execution:** If the target is Linux, I must format the attack so the *benign* data arrives first (to satisfy the IDS, if the IDS uses a First-In policy), and the *malicious* data arrives second. The Linux target will overwrite the benign data with the malicious payload. If I misidentify the OS, the target will reconstruct the benign stream and the attack will fail.

## Deep-Dive Defensive Questions

**Q7: How does a modern IPS utilize "Target-Based IDS" concepts to defeat evasion techniques like fragmentation and overlapping TCP segments?**
*Answer:*
A traditional IDS assumes a static reassembly policy (e.g., it always uses Last-In). Target-Based IDS (like Snort's Target-Based Stream Reassembly) dynamically alters its reassembly behavior based on the specific host receiving the traffic.
*   **Mechanism:** The IDS integrates with an asset management database or passive OS fingerprinting engine (like `p0f`).
*   **Execution:** When a stream of overlapping packets is destined for `10.0.0.5`, the IDS checks its database. It sees `10.0.0.5` is running Windows Server 2019. The IDS stream preprocessor instantly switches to a "Windows (First-In)" reassembly policy for that specific connection. This ensures the IDS reconstructs the exact same data stream that the target host will execute, completely nullifying insertion/evasion attacks based on OS discrepancies.

**Q8: Your SOC has deployed a new Suricata cluster in IPS (inline) mode. What are the performance and security trade-offs of enabling deep stream reassembly and flow tracking?**
*Answer:*
*   **Security Benefit:** Deep stream reassembly prevents Session Splicing and Fragment Overlap attacks. It is critical for detecting application-layer attacks (like SQLi or XSS) that span multiple packets.
*   **Performance Trade-off (Latency):** The IPS must buffer packets before forwarding them. This introduces latency, which can degrade real-time applications (VoIP, high-frequency trading).
*   **Resource Exhaustion (State Table):** Tracking millions of concurrent TCP flows consumes massive amounts of RAM. Attackers can exploit this via State Exhaustion DoS (e.g., SYN floods or leaving open connections).
*   **Mitigation:** To balance this, we must configure strict stream timeout limits, implement hardware offloading (e.g., using SmartNICs or AF_PACKET/PF_RING for zero-copy packet processing), and set maximum buffer depths for flow tracking.

**Q9: Explain the concept of "Evasion via Asymmetric Routing" and how placing an IDS on a SPAN port can lead to false negatives.**
*Answer:*
*   **The Setup:** An IDS connected to a switch SPAN (Port Mirror) operates in passive mode.
*   **The Problem:** If the network uses asymmetric routing, outbound traffic leaves via Router A, but inbound return traffic comes through Router B. If the SPAN port is only monitoring Router A, the IDS only sees half of the TCP conversation (e.g., the client's HTTP GET, but not the server's HTTP 200 OK payload).
*   **The False Negative:** Many stateful IDS stream preprocessors require seeing the 3-way handshake to establish state. If they miss the SYN-ACK, they drop the state and ignore the subsequent payload. Furthermore, if the malicious payload is delivered in the server's response (e.g., an exploit kit delivery), an IDS monitoring only the outbound router will be completely blind to the attack.

## Real-World Attack Scenario

### Attack Flow: The Desynchronization Attack
1.  **The Objective:** A Red Team needs to exploit a vulnerability in an internal Apache Struts server (`10.0.50.100`) protected by a Snort IPS.
2.  **The Setup:** They establish a standard TCP connection. They need to desynchronize the TCP sequence numbers between the IPS and the target.
3.  **The Execution (Post-SYN):** After the 3-way handshake, the attacker sends a TCP packet with the RST (Reset) flag set. Crucially, the packet is crafted with a TTL (Time-to-Live) of 15.
4.  **IPS View:** The Snort IPS is 10 hops away. It receives the RST packet, processes it, and tears down the stateful tracking for that connection in its memory.
5.  **Target View:** The Apache server is 20 hops away. The RST packet expires in transit (TTL hits 0) and is dropped by a router. The Apache server never receives the RST and keeps the connection fully established.
6.  **The Kill:** The attacker now sends the actual malicious Apache Struts payload across the existing connection. The IPS sees this traffic but, having torn down the state, categorizes it as "out of state" or orphaned packets. Depending on the IPS configuration (if it fails-open on orphaned packets), it passes the traffic without signature inspection. The target receives the payload and is compromised.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
| TCP Desynchronization Evasion (TTL Manipulation)                                  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Attacker]                       [Snort IPS]                       [Target OS]   |
|      |                                 | (Hop 10)                        | (Hop 20)|
|      | 1. SYN                          |                                 |         |
|      |-------------------------------->|-------------------------------->|         |
|      | 2. SYN-ACK                      |                                 |         |
|      |<--------------------------------|<--------------------------------|         |
|      | 3. ACK                          |                                 |         |
|      |-------------------------------->|-------------------------------->|         |
|      |                                 | [State: ESTABLISHED]            |         |
|      |                                 |                                 |         |
|      | 4. RST (TTL=12)                 |                                 |         |
|      |-------------------------------->|    *Packet dies at Hop 12*      |         |
|      |                                 | [State: CLOSED]                 |         |
|      |                                 |                                 |         |
|      | 5. Malicious Payload            |                                 |         |
|      |-------------------------------->| (No state tracking!)            |         |
|      |                                 | (IPS ignores/passes packet)     |         |
|      |                                 |-------------------------------->|         |
|      |                                 |                                 | [PWNED] |
+-----------------------------------------------------------------------------------+
```

## Chaining Opportunities
*   **IDS Evasion -> Payload Obfuscation:** Chain TCP Overlapping with heavily obfuscated/encoded payloads (e.g., XORed MSFVenom shellcode). Even if the IDS manages to reassemble the stream, the static signatures won't match the obfuscated bytes.
*   **Desync -> WAF Bypass:** Once the network IPS is desynchronized, apply the same logic to HTTP/2 multiplexing to desynchronize the application-layer WAF, creating a dual-layer bypass.

## Related Notes
*   [[Interview Prep - Network Security]]
*   [[Snort Preprocessors and Stream Reassembly]]
*   [[Red Teaming - Covert Channels]]
*   [[TCP-IP Deep Dive - TCP State Machine]]
