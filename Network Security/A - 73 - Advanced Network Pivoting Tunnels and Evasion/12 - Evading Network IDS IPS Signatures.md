---
tags: [network, advanced, pivoting, evasion, vapt]
difficulty: advanced
module: "73 - Advanced Network Pivoting Tunnels and Evasion"
topic: "73.12 Evading Network IDS IPS Signatures"
---

# 73.12 Evading Network IDS/IPS Signatures

## Introduction to Network IDS/IPS Architecture
Network Intrusion Detection Systems (NIDS) and Intrusion Prevention Systems (NIPS) are foundational components of defensive security architectures. Systems like Snort, Suricata, and Zeek monitor network traffic in real-time, matching packet payloads, flow characteristics, and protocol states against vast databases of known malicious signatures. While DPI focuses heavily on deep protocol parsing and behavioral anomalies, traditional NIDS/NIPS often rely heavily on deterministic pattern matching (though modern systems incorporate heuristic and behavioral capabilities).

For an adversary, an un-evaded NIDS is a massive operational risk. A single flagged packet can result in an IP block (via NIPS active response) or alert the Security Operations Center (SOC), triggering a full incident response investigation. Evading these systems requires deep protocol manipulation, targeting the specific ways in which NIDS parsers reconstruct and interpret network flows.

## Core Mechanisms of Signature Evasion
The fundamental theory behind IDS/IPS evasion is to create an intentional discrepancy between how the defensive sensor processes the traffic and how the target end-host processes it. If the sensor reconstructs the data differently than the target, the malicious signature will be broken at the sensor but successfully reassembled and executed at the target.

### 1. Fragmentation and Overlapping
One of the oldest yet continually relevant methods of evasion involves manipulating IP fragmentation. When a large packet is broken into smaller fragments, the NIDS must reassemble them to inspect the payload.
- **Simple Fragmentation**: Breaking the payload into incredibly small fragments (e.g., 8 bytes). If the NIDS fails to reassemble them due to buffer limitations or timeout configurations, the signature is not matched.
- **Overlapping Fragments**: Sending fragments with overlapping offsets but different data.
  - *Example*: Fragment A contains benign data. Fragment B overlaps Fragment A and contains malicious data. If the NIDS prefers the first fragment (Fragment A) and the target OS prefers the last overlapping fragment (Fragment B), the NIDS sees benign traffic while the target executes the malicious payload. The reverse is also possible depending on the OS (e.g., Windows vs. Linux IP stack implementations).

### 2. TCP Session Manipulation
Similar to IP fragmentation, TCP provides mechanisms for evasion through segmentation and flow control.
- **TCP Stream Insertion**: An attacker sends a packet with a malicious payload but calculates the TTL (Time to Live) so that the packet reaches the NIDS but expires before reaching the target. The attacker then sends a benign packet with the same sequence number that reaches the target. The NIDS parses the malicious packet (perhaps ignoring it if it's not a complete signature) or becomes confused, while the target only processes the benign data, or vice versa.
- **TCP Overlapping**: Sending segments that overlap in sequence numbers. As with IP fragmentation, different operating systems resolve overlapping TCP segments differently.
- **Out-of-Order Packets**: Sending the malicious payload out of sequence. If the NIDS lacks the memory to buffer the entire stream until the missing packets arrive, it may drop the stream from inspection, allowing the out-of-order packets to reach the target undetected.

### 3. Payload Obfuscation and Encoding
If the traffic cannot be manipulated at the network layer, the payload itself must be transformed to avoid signature detection.
- **Polymorphism and Metamorphism**: Changing the payload structure without altering its function. In shellcode, this involves using different registers, inserting NOP sleds (or using alternative instructions like `INC EAX; DEC EAX` instead of standard `0x90` NOPs), and employing polymorphic decoders.
- **Application-Layer Encoding**: If exploiting a web server, the attacker can use extensive URL encoding, double URL encoding, Unicode encoding, or non-standard HTTP methods. For example, a signature looking for `SELECT * FROM` might be bypassed by `%53%45%4C%45%43%54%20%2A%20%46%52%4F%4D`.
- **Chunked Transfer Encoding**: In HTTP/1.1, data can be sent in chunks. By breaking the malicious payload across multiple small chunks, simple regex-based NIDS rules will fail to match the contiguous string.

### 4. Timing and Evasion
NIDS sensors maintain state tables for active connections. These tables have finite memory and timeout values.
- **Slow and Low Scanning**: Sending packets at incredibly slow intervals. If the interval exceeds the NIDS state timeout, the NIDS drops the connection from its memory, preventing it from aggregating the events into an alert.
- **Resource Exhaustion**: Flooding the NIDS with massive amounts of benign fragmented traffic or complex regex-triggering payloads. This forces the NIDS CPU or memory utilization to spike. Many enterprise sensors are configured to "fail-open" (pass traffic without inspection) when overloaded to prevent network outages.

## Architecture: TCP Overlapping Evasion

Below is a conceptual architecture demonstrating how TTL manipulation and TCP overlapping can deceive a NIDS sensor.

```ascii
                      +-------------------+
                      |   Attacker Node   |
                      | (Crafting Packets)|
                      +--------+----------+
                               |
                               | 1. Packet A: Sequence 100, Payload="EVIL", TTL=10
                               | 2. Packet B: Sequence 100, Payload="GOOD", TTL=64
                               V
                      +-------------------+
                      |   Network Router  |
                      |   (Decrements TTL)|
                      +--------+----------+
                               | TTL becomes 9 (Pkt A) and 63 (Pkt B)
                               V
                      +-------------------+     NIDS reassembles sequence 100
                      |   NIDS Sensor     | --> Sees "EVIL" (but maybe it's not enough
                      | (Passive Monitor) |     to trigger a generic alert, or it assumes
                      +--------+----------+     "EVIL" is the valid payload).
                               |
                               | Packet A (TTL=9) travels further.
                               | Router 2, Router 3, ..., Router 10.
                               | Packet A TTL reaches 0 and is dropped!
                               | Packet B (TTL=54) continues.
                               V
                      +-------------------+
                      | Target Web Server |
                      |   (Vulnerable)    |
                      +-------------------+
                        Target receives Packet B: "GOOD". 
                        If Attacker reversed this logic (Packet A = "GOOD" dropped, 
                        Packet B = "EVIL" reaches target), the NIDS is blinded.
```

## Advanced Techniques: Snort and Suricata Rule Bypassing
Understanding rule structure is critical. A standard Snort rule might look like this:
`alert tcp any any -> $HTTP_SERVERS $HTTP_PORTS (msg:"SQL Injection Attempt"; content:"UNION SELECT"; http_uri; sid:10001; rev:1;)`

### Bypass Vectors:
1. **Case Sensitivity**: If the rule does not specify `nocase`, sending `uNiOn SeLeCt` bypasses the check entirely.
2. **Whitespace Manipulation**: SQL parsers often ignore excessive whitespace or inline comments. Changing `UNION SELECT` to `UNION/**/SELECT` or `UNION%0ASELECT` (newline) can evade simple string matches.
3. **Protocol Mismatch**: The rule specifies `$HTTP_PORTS` (usually 80, 443). If the attacker can force the web server to listen on a non-standard port (e.g., via a misconfiguration or a pivot), the NIDS rule simply won't apply to the traffic.
4. **Header Manipulation**: Utilizing HTTP pipelining or malformed headers that the NIDS parser rejects (dropping the inspection) but the robust modern web server accepts and processes.

## Operational Constraints
Evasion is not guaranteed. Modern NIPS utilize complex protocol normalizers. For instance, Snort's `frag3` and `stream5` preprocessors are specifically designed to normalize fragmented IP packets and overlapping TCP streams to match the specific quirks of the target OS (if configured correctly with host attribute tables).

To successfully evade a well-tuned system, attackers must perform extensive reconnaissance to identify the target OS, allowing them to tailor their overlapping fragments to match the exact reassembly logic of the target, thereby ensuring the NIDS normalization fails to align with reality.

## Conclusion
Evading Network IDS/IPS is a highly technical discipline that exploits the fundamental complexities of network protocol standards. By manipulating fragmentation, TCP states, timing, and payload encoding, an attacker can create a divergence in reality between the defensive sensor and the target host, allowing malicious actions to occur under the radar.

## Chaining Opportunities
- **[[11 - Bypassing Deep Packet Inspection DPI]]**: While IDS looks for signatures, DPI analyzes application state. Evading both simultaneously requires complex obfuscation.
- **[[13 - Double Pivoting and Multi-hop Routing]]**: Bouncing through multiple internal systems can scramble traffic flow characteristics, further confusing internal IDS deployments.
- **[[15 - C2 Infrastructure Traffic Obfuscation]]**: Malleable C2 profiles specifically use memory and encoding evasion to defeat NIDS signatures on outbound beacons.

## Related Notes
- [[06 - Custom Tooling and Shellcode Obfuscation]]
- [[10 - Firewall Evasion Techniques]]
- [[22 - Vulnerability Research and Exploit Development]]
