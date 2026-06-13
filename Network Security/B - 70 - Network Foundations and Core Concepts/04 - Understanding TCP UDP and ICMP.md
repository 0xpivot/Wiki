---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.04 Understanding TCP UDP and ICMP"
---
# 04 - Understanding TCP, UDP, and ICMP

## 1. Introduction to Layer 3 and Layer 4 Protocols

While IP addressing (Layer 3) provides the logical mechanism to route a packet from Host A to Host B, it is essentially a "best-effort" delivery system. IP does not guarantee that a packet will arrive, nor does it inherently know which application on the receiving machine should process the data. 

To solve these problems, the TCP/IP suite relies heavily on Transport Layer (Layer 4) protocols—namely TCP and UDP—to handle end-to-end communication, port multiplexing, and reliability. Additionally, the Network Layer utilizes ICMP for diagnostics and error reporting.

For a penetration tester, mastering these three protocols is non-negotiable. Nmap port scanning, firewall evasion, DoS attacks, and reverse shells all manipulate the specific flags, states, and behaviors of TCP, UDP, and ICMP.

## 2. Transmission Control Protocol (TCP)

TCP is a **connection-oriented**, reliable transport protocol. It is used when data integrity is paramount (e.g., HTTP web traffic, SSH, FTP, SMTP email).

### Core Features of TCP:
*   **Reliable Delivery:** It uses sequence numbers and acknowledgments to ensure no packets are lost. If a packet is lost, it is retransmitted.
*   **Connection-Oriented:** A formal connection (handshake) must be established before data is sent, and formally torn down when finished.
*   **Order Maintained:** Packets arriving out of order are reassembled based on their sequence numbers.
*   **Flow Control:** Utilizes "Windowing" to tell the sender to slow down if the receiver's buffer is filling up.

### The TCP Header and Flags
The TCP header contains several control bits (Flags) that dictate the state of the connection. An attacker crafts packets with specific flag combinations to elicit specific responses from a target (e.g., in port scanning).

*   **SYN (Synchronize):** Used to initiate a connection.
*   **ACK (Acknowledgment):** Acknowledges received data or SYN requests.
*   **FIN (Finish):** Used to gracefully terminate a connection (no more data from sender).
*   **RST (Reset):** Abruptly terminates a connection. Used to reject connections to closed ports.
*   **PSH (Push):** Tells the receiver to process the data immediately rather than buffering it.
*   **URG (Urgent):** Indicates urgent data.

### The TCP 3-Way Handshake
Before any application data is sent, TCP establishes a connection via a 3-way handshake.
1.  **SYN:** Client sends a SYN packet to the server with a random initial Sequence Number (ISN).
2.  **SYN-ACK:** Server receives the SYN, allocates resources, and replies with a SYN-ACK packet. The ACK number is the Client's ISN + 1. It also sends its own random ISN.
3.  **ACK:** Client receives the SYN-ACK, and sends an ACK back to the server. The ACK number is the Server's ISN + 1. The connection is now ESTABLISHED.

### Visualizing the TCP Handshake and Port Scanning (ASCII Diagram)

```text
+---------------------------------------------------------------------------------+
|                       TCP 3-WAY HANDSHAKE & PORT SCANNING                       |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [NORMAL CONNECTION (Port Open)]                                                |
|  Client (Attacker)                                              Server (Target) |
|         | ----------- (1) SYN, Seq=100 ------------------------> |              |
|         | <---------- (2) SYN-ACK, Seq=300, Ack=101 ------------ |              |
|         | ----------- (3) ACK, Seq=101, Ack=301 ---------------> |              |
|         |                   [CONNECTION ESTABLISHED]             |              |
|                                                                                 |
|                                                                                 |
|  [STEALTH SYN SCAN - NMAP -sS (Port Open)]                                      |
|  Client (Attacker)                                              Server (Target) |
|         | ----------- (1) SYN ---------------------------------> |              |
|         | <---------- (2) SYN-ACK (Target says "I'm Open!") ---- |              |
|         | ----------- (3) RST (Attacker tears it down early) --> |              |
|         |        [Connection aborted, but attacker knows port is open]          |
|                                                                                 |
|                                                                                 |
|  [CONNECTION ATTEMPT (Port Closed)]                                             |
|  Client (Attacker)                                              Server (Target) |
|         | ----------- (1) SYN ---------------------------------> |              |
|         | <---------- (2) RST-ACK (Target says "Port Closed!") - |              |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### TCP-Based Attacks
*   **SYN Flood (DoS):** Attacker sends thousands of SYN packets with spoofed source IPs. The server replies with SYN-ACKs and leaves the connection "half-open," exhausting its connection queue and crashing the service.
*   **TCP Session Hijacking:** If an attacker can predict the TCP sequence numbers, they can inject malicious packets into an established session, effectively impersonating the trusted client.

## 3. User Datagram Protocol (UDP)

UDP is a **connectionless**, unreliable transport protocol. It is used for applications where speed is more critical than absolute reliability, or where the application handles error-correction itself (e.g., DNS, VoIP, Video Streaming, SNMP).

### Core Features of UDP:
*   **No Handshake:** Data is sent immediately without establishing a connection. "Fire and forget."
*   **Unreliable Delivery:** No acknowledgments. If a packet drops, it's gone.
*   **Unordered:** Packets are processed as they arrive.
*   **Low Overhead:** The UDP header is much smaller than TCP (only 8 bytes: Source Port, Dest Port, Length, Checksum).

### UDP-Based Attacks and Scanning
*   **UDP Port Scanning:** Because UDP does not reply with SYN-ACKs, scanning is difficult.
    *   If you send a UDP packet to an *open* port, the application usually does not respond at all (silence).
    *   If you send it to a *closed* port, the target OS should send back an `ICMP Port Unreachable` message.
    *   Therefore, UDP scanning relies on interpreting ICMP error messages or application-specific timeouts.
*   **UDP Amplification Attacks (DDoS):** An attacker sends a small UDP request with a spoofed source IP (the victim's IP) to a vulnerable server (like DNS or NTP). The server responds with a massive UDP response directed at the victim, amplifying the attacker's bandwidth by factors of up to 500x.

## 4. Internet Control Message Protocol (ICMP)

ICMP operates at the Network Layer (Layer 3) alongside IP. It is not used to transmit application data; instead, it is an administrative and diagnostic protocol used by routers and hosts to communicate network-level information, errors, and reachability.

### ICMP Types and Codes
ICMP messages are identified by a "Type" and a "Code" field.
*   **Type 8 (Echo Request):** Used by the `ping` command.
*   **Type 0 (Echo Reply):** The response to a `ping`.
*   **Type 3 (Destination Unreachable):** Extremely important for VAPT.
    *   *Code 0:* Net Unreachable (Routing failure).
    *   *Code 1:* Host Unreachable (Host down).
    *   *Code 3:* Port Unreachable (Often indicates a closed UDP port).
*   **Type 11 (Time Exceeded):** Sent when a packet's Time-To-Live (TTL) reaches zero. Used by `traceroute` to map network hops.

### ICMP-Based Attacks
*   **Ping Sweep:** Sending ICMP Echo Requests to an entire subnet to find live hosts.
*   **Smurf Attack (Legacy DoS):** Attacker sends an ICMP Echo Request to a subnet's broadcast address, spoofing the source IP as the victim. Every host on the subnet replies to the victim, flooding them.
*   **ICMP Tunneling / Exfiltration:** Because many firewalls allow outbound ICMP (pings), attackers can encapsulate data or command-and-control (C2) traffic inside the payload section of ICMP Echo requests/replies to bypass firewall rules.

## 5. Security Controls and Firewalling

Understanding these protocols is how you understand firewalls.
*   **Stateless Firewalls (Packet Filters):** Look only at individual packets. They block based on source/dest IP and ports. They are easily bypassed because they don't understand the TCP handshake state.
*   **Stateful Firewalls:** Track the TCP sequence numbers and connection state. They know if a packet is part of an established 3-way handshake. If an attacker sends a random ACK packet without a prior SYN/SYN-ACK, the stateful firewall drops it.
*   **Intrusion Detection Systems (IDS):** Analyze the flags and payloads. An IDS will trigger an alert if it sees a single IP sending thousands of SYN packets to different ports (port scanning behavior).

## 6. Conclusion for VAPT

When running `nmap -sS -sU -p- target.com`, you are directly manipulating TCP and UDP.
When your scan hangs or returns "filtered," it is because a firewall is silently dropping your SYN packets or blocking ICMP Unreachable responses. 
Mastery of VAPT requires moving beyond "running the tool" and visualizing the exact sequence of TCP flags and ICMP responses occurring on the wire.

---
## Chaining Opportunities
*   To understand how the payloads inside these TCP/UDP segments are translated to end-user applications, refer to the upper layers in [[01 - OSI Model and TCP IP Protocol Suite]].
*   These transport protocols rely entirely on the IP infrastructure detailed in [[02 - IP Addressing Subnetting and CIDR Notation]].
*   Understanding ICMP and TCP routing behaviors requires knowledge from [[03 - Introduction to Routing and Switching]].

## Related Notes
*   [[01 - OSI Model and TCP IP Protocol Suite]]
*   [[02 - IP Addressing Subnetting and CIDR Notation]]
*   [[03 - Introduction to Routing and Switching]]
