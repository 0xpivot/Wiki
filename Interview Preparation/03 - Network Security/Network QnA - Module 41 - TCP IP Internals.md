---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 41"
---

# Network QnA - Module 41 - TCP/IP Internals

```text
       TCP/IP Protocol Suite & Packet Anatomy
+-------------------------------------------------------+
|                 Application Layer                     |
|           (HTTP, FTP, SMTP, DNS, SSH, BGP)            |
+-------------------------------------------------------+
|                  Transport Layer                      |
|  +-------------------------------------------------+  |
|  | TCP Header: | Src/Dst Port | SEQ # | ACK #      |  |
|  |             | Window Size  | Checksum| Flags    |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
|                   Internet Layer                      |
|  +-------------------------------------------------+  |
|  | IP Header:  | Version | IHL | TOS | Total Len   |  |
|  |             | TTL | Protocol | Header Checksum  |  |
|  |             | Src IP | Dst IP | Options         |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
|                Network Access Layer                   |
|  +-------------------------------------------------+  |
|  | Ethernet:   | Dest MAC | Src MAC | EtherType    |  |
|  |             | Payload | Frame Check Sequence    |  |
|  +-------------------------------------------------+  |
+-------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the detailed mechanics of the TCP 3-way handshake and the state transitions involved. How does a TCP SYN Flood abuse this process?**
**Answer:**
The TCP 3-way handshake establishes a reliable connection. The states and transitions are:
1. **SYN (Synchronize):** The client (in `CLOSED` state) sends a TCP segment with the SYN flag set to the server, specifying its Initial Sequence Number (ISN). The client transitions to `SYN_SENT`.
2. **SYN-ACK (Synchronize-Acknowledge):** The server (in `LISTEN` state) receives the SYN, allocates a Transmission Control Block (TCB) in a half-open queue, and replies with SYN-ACK. The server's ISN is generated, and the Acknowledgment number is set to client ISN + 1. Server transitions to `SYN_RCVD`.
3. **ACK (Acknowledge):** The client receives SYN-ACK, sends an ACK with Acknowledgment number set to server ISN + 1, and transitions to `ESTABLISHED`. The server receives the ACK and transitions to `ESTABLISHED`.

**SYN Flood Abuse:**
An attacker sends massive SYN requests with spoofed IPs. The server replies with SYN-ACKs and allocates TCB resources. Since the IPs are spoofed, the final ACK is never sent. The half-open connection queue fills up, causing a Denial of Service (DoS) for legitimate clients. Mitigation includes SYN Cookies, which encode the state in the TCP sequence number cryptographically.

**Q2: Differentiate between IP fragmentation and TCP segmentation. How do attackers leverage fragmentation for evasion?**
**Answer:**
- **TCP Segmentation:** Occurs at Layer 4. TCP divides an application data stream into segments based on the Maximum Segment Size (MSS). It ensures reliability and ordering.
- **IP Fragmentation:** Occurs at Layer 3. When an IP packet exceeds the Maximum Transmission Unit (MTU) (e.g., 1500 bytes for Ethernet), the sender or routers fragment the packet. All fragments share the same Identification field but have different Fragment Offsets.

**Evasion Techniques:**
1. **Tiny Fragment Attack:** The attacker creates IP fragments so small that the TCP header is split across multiple fragments. Firewalls inspecting only the first fragment might miss the destination port or TCP flags.
2. **Overlapping Fragments (Teardrop/Fragroute):** Attackers craft fragments with overlapping offsets. Different OSes reassemble them differently. If the IDS and target OS differ in reassembly, the IDS sees benign traffic while the target executes malicious payload.
3. **Fragmentation Timeout:** Sending fragments slowly without the final fragment exhausts the reassembly buffer, causing DoS.

**Q3: Describe the IP Time-To-Live (TTL) field. How can it be weaponized for network mapping and firewall evasion?**
**Answer:**
The IP TTL field (8 bits) prevents packets from looping infinitely. Every router decrements the TTL by 1. If it hits 0, the router drops the packet and sends an ICMP Time Exceeded.
**Weaponization:**
- **Traceroute:** Incrementally increasing TTLs map the routing hops.
- **Firewalking:** An attacker sends a packet to an internal host with a TTL engineered to expire *just after* the firewall. If the firewall drops it due to ACL, no response is sent. If permitted, the next hop drops it and sends ICMP Time Exceeded, revealing the firewall's ACL.
- **IDS Evasion:** A malicious packet is sent with a TTL that expires *after* the IDS but *before* the target. The IDS processes the payload, but it never reaches the target. A benign packet fills the missing sequence for the target.

## Scenario-Based Questions

**Q4: You are on a Red Team engagement. You have compromised a restricted Linux host that blocks all outbound TCP and UDP traffic, but allows outbound ICMP echo requests for troubleshooting. How do you establish a stable C2 channel?**
**Answer:**
I would establish an **ICMP Tunnel**.
Since ICMP Echo Requests (Type 8) and Responses (Type 0) are allowed, the data payload of the ICMP packets can encapsulate TCP/IP traffic.
1. **Deployment:** Deploy `ptunnel-ng` or `icmptunnel` on the compromised host and an external C2 server.
2. **Encapsulation:** The tunnel client reads data from a local TUN/TAP interface, encrypts it, and embeds it in the data section of an ICMP Echo Request.
3. **Egress:** The firewall observes standard ICMP pings to an external IP and permits them.
4. **Decapsulation:** The C2 server extracts the payload, processes the data, and embeds the response in an ICMP Echo Reply.
5. **Reliability:** The tunneling software implements its own sequence numbering and retransmission over the stateless ICMP protocol to ensure connection stability.

**Q5: During a penetration test, you capture a PCAP containing a suspected reverse shell session over TCP. The target network uses asynchronous routing, causing heavy out-of-order and duplicated packets. How do you reconstruct the exact session?**
**Answer:**
Reconstructing the session requires deep state tracking.
1. **Session Isolation:** Filter the PCAP by the specific 4-tuple (Source IP, Port, Destination IP, Port).
2. **Sequence Analysis:** TCP uses SEQ and ACK numbers. I would sort the packets based on their SEQ numbers relative to the ISN.
3. **Handling Re-transmissions:** In asynchronous routing, packets are duplicated. The reconstruction engine must discard duplicates based on identical SEQ numbers and payload lengths.
4. **Resolving Overlaps:** If overlapping segments exist with different data, the OS's specific TCP reassembly policy dictates which data is kept (e.g., first-come vs. last-come).
5. **Tooling:** Using `Wireshark`'s "Follow TCP Stream" or the CLI tool `tcpflow`, which automatically handles reassembly, ignoring retransmissions, and outputs the raw data stream into clean client-to-server and server-to-client files.

## Deep-Dive Defensive Questions

**Q6: What is TCP Window Scaling? How can an attacker abuse the Window Size field, and how does a modern firewall defend against it?**
**Answer:**
**TCP Window Scaling:** The TCP Window Size field is 16 bits (max 65,535 bytes). High-speed networks require larger windows. TCP Window Scaling (RFC 1323) introduces a shift count during the SYN handshake, multiplying the window size by up to $2^{14}$, allowing up to 1GB.
**Abuse (Zero Window Attack / Sockstress):**
An attacker establishes a TCP connection, requests a large resource, and advertises a TCP Window Size of Zero. This signals the server that the client buffer is full. The server enters a persist state, sending Zero Window Probes. The connection remains alive indefinitely, exhausting the server's memory and connection limits (TCP backlog).
**Defense:**
Modern stateful firewalls and Load Balancers act as TCP Proxies. They terminate the connection, manage window sizes independently, enforce aggressive timeouts for clients stuck in a zero-window state, and drop connections that consistently advertise abnormally small windows.

**Q7: Explain the concept of IP Source Routing. Why is it considered a security risk and how is it mitigated?**
**Answer:**
**IP Source Routing** is an IP option that allows the sender of a packet to specify the route (the specific hops) the packet should take through the network, rather than relying on the routers' dynamic routing tables.
- **Strict Source Routing:** Every hop is specified.
- **Loose Source Routing:** A list of specific waypoints is provided, but routers can use dynamic paths between waypoints.
**Security Risk:**
Attackers use Source Routing to bypass network filtering and route packets through hidden or unauthorized paths. For example, an attacker could route traffic through a trusted internal host to bypass a firewall, or use it to intercept return traffic by forcing the response to route back through an attacker-controlled router.
**Mitigation:**
Most modern routers and firewalls are configured by default to drop any IP packets containing the Source Route option (e.g., `no ip source-route` on Cisco devices).

## Real-World Attack Scenario

**Scenario: TCP Sequence Prediction and BGP Hijacking**
A state-sponsored actor targets a legacy BGP peering session between two ISP routers that relies on IP-based authentication without TCP MD5 or IPsec.
1. **Reconnaissance:** The attacker observes the TCP traffic (port 179) between Router A and Router B.
2. **Vulnerability Identification:** The attacker discovers that Router A uses a predictable pseudo-random number generator for its TCP Initial Sequence Numbers (ISNs).
3. **Spoofed Connection:** The attacker sends a SYN packet to Router B, spoofing the source IP of Router A.
4. **Blind Injection:** Router B responds to Router A with a SYN-ACK containing its own ISN. The attacker cannot see this packet.
5. **Sequence Prediction:** Using the predictable ISN vulnerability, the attacker floods Router B with ACK packets containing guessed Sequence and Acknowledgment numbers.
6. **Hijack:** One of the guessed ACKs is accepted. The TCP session is established. The attacker injects a spoofed BGP Update packet, injecting a malicious route into Router B's table, effectively blackholing or redirecting the target's traffic globally.

## Chaining Opportunities
- **OSINT & Recon:** TTL manipulation (Firewalking) is chained with nmap scans to map highly secure internal network topologies invisibly.
- **Protocol Smuggling:** Advanced HTTP Request Smuggling heavily relies on manipulating TCP segmentation and MTU sizes to bypass Web Application Firewalls (WAFs).
- **C2 Communications:** Custom C2 frameworks leverage raw sockets to manipulate TCP Window sizes and Urgent Pointers for covert data exfiltration.

## Related Notes
- [[01 - Transport Layer Security (TLS) Handshakes]]
- [[12 - Advanced Evasion Techniques in Network Intrusion Detection]]
- [[24 - Designing Custom Command and Control Protocols]]
- [[33 - Network Protocol Fuzzing Methodologies]]
- [[42 - VLAN Hopping and Layer 2 Attacks]]
- [[50 - Stateful vs Stateless Firewall Architectures]]
