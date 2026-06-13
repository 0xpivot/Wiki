---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.01 OSI Model and TCP IP Protocol Suite"
---
# 01 - OSI Model and TCP/IP Protocol Suite

## 1. Introduction to Network Models

In the realm of computer networking and cybersecurity, standardized conceptual models are paramount for understanding how disparate hardware and software components communicate. The Open Systems Interconnection (OSI) model and the Transmission Control Protocol/Internet Protocol (TCP/IP) suite are the two foundational architectures that dictate data transmission over networks.

For a penetration tester, comprehending these models is not merely an academic exercise. Every network-based attack, from a simple ping sweep to a sophisticated cross-site scripting (XSS) payload, occurs at specific layers of these models. Recognizing which layer an attack operates on allows a security professional to understand the mechanisms, constraints, and potential detection vectors of the exploit.

When conducting a Vulnerability Assessment and Penetration Testing (VAPT) engagement, an attacker fundamentally subverts the rules established by these protocols. The deeper the understanding of the rules, the easier it is to bend or break them.

## 2. The OSI Model: A Deep Dive

The OSI model is a conceptual framework created by the International Organization for Standardization (ISO) that characterizes and standardizes the communication functions of a telecommunication or computing system without regard to its underlying internal structure and technology. Its goal is the interoperability of diverse communication systems with standard protocols.

The model partitions a communication system into seven abstraction layers. A layer serves the layer above it and is served by the layer below it.

### Layer 1: Physical Layer
The Physical Layer is responsible for the transmission and reception of unstructured raw data between a device and a physical transmission medium. It converts the digital bits into electrical, radio, or optical signals.
*   **Core Functions:** Bit synchronization, bit rate control, physical topologies (star, bus, ring), transmission mode (simplex, half-duplex, full-duplex).
*   **Components:** Cables (Ethernet, Fiber), Hubs, Repeaters, Network Interface Cards (NICs), Modems.
*   **Protocols/Standards:** IEEE 802.3 (Ethernet physical layer), IEEE 802.11 (Wi-Fi physical layer), USB, Bluetooth.
*   **VAPT Perspective:** Physical security is the foundation. If an attacker has physical access, all other layers are compromised. Attacks include wiretapping, electromagnetic interference (EMI), jamming wireless signals, rogue devices (e.g., LAN Turtles, malicious access points), and environmental manipulation.

### Layer 2: Data Link Layer
The Data Link Layer provides node-to-node data transfer—a link between two directly connected nodes. It detects and possibly corrects errors that may occur in the physical layer.
*   **Sublayers:**
    *   **LLC (Logical Link Control):** Multiplexes protocols running at the network layer, and optionally provides flow control and acknowledgment.
    *   **MAC (Media Access Control):** Determines who is allowed to access the media at any one time. Assigns physical MAC addresses.
*   **Components:** Switches, Bridges, Wireless Access Points (WAPs).
*   **Protocols/Standards:** Ethernet (MAC), Point-to-Point Protocol (PPP), Frame Relay. ARP is often mapped here or at the boundary of L2/L3.
*   **VAPT Perspective:** Layer 2 relies heavily on trust. Attacks here include MAC spoofing (impersonating a trusted device), ARP poisoning (Man-in-the-Middle), Switch CAM table overflow (forcing a switch to act like a hub), VLAN hopping, and Spanning Tree Protocol (STP) manipulation.

### Layer 3: Network Layer
The Network Layer is responsible for packet forwarding including routing through intermediate routers. While the Data Link Layer handles node-to-node communication, the Network Layer handles host-to-host communication across multiple networks.
*   **Core Functions:** Logical addressing (IP addresses), Routing, Fragmentation and Reassembly.
*   **Components:** Routers, Layer 3 Switches, Firewalls.
*   **Protocols:** IP (IPv4, IPv6), ICMP, IPsec, IGMP, Routing protocols (OSPF, BGP, RIP).
*   **VAPT Perspective:** Attacks at this layer aim at routing infrastructure or logical addressing. IP spoofing, Route injection/hijacking (e.g., BGP hijacking), ICMP floods, Ping of Death, Smurf attacks, and IP fragmentation attacks (e.g., Teardrop).

### Layer 4: Transport Layer
The Transport Layer provides the functional and procedural means of transferring variable-length data sequences from a source to a destination host.
*   **Core Functions:** Segmentation, Connection multiplexing (ports), Reliability (error recovery), Flow control (windowing).
*   **Components:** Load Balancers, Next-Gen Firewalls.
*   **Protocols:** TCP (Transmission Control Protocol), UDP (User Datagram Protocol), SCTP.
*   **VAPT Perspective:** Transport layer attacks often target the connection state mechanisms. Port scanning (SYN scans, UDP scans) maps the attack surface. SYN floods exhaust server resources. Session hijacking targets TCP sequence prediction. UDP amplification attacks abuse connectionless protocols for massive DoS.

### Layer 5: Session Layer
The Session Layer controls the dialogues (connections) between computers. It establishes, manages, and terminates the connections.
*   **Core Functions:** Dialog control (who communicates and when), Token management, Synchronization (checkpoints).
*   **Protocols:** NetBIOS, RPC, PPTP, SOCKS, NFS.
*   **VAPT Perspective:** Session hijacking (grabbing an active session token or identifier), RPC endpoint mapper enumeration to find vulnerable internal services, NetBIOS name spoofing for internal MitM.

### Layer 6: Presentation Layer
The Presentation Layer establishes context between application-layer entities. It translates data from the application layer into a common format for network transmission.
*   **Core Functions:** Data translation, Data encryption/decryption, Data compression.
*   **Protocols:** SSL/TLS (often considered layer 6/7), JPEG, MPEG, ASCII, EBCDIC.
*   **VAPT Perspective:** Cryptographic attacks. SSL/TLS stripping (downgrading HTTPS to HTTP), Downgrade attacks (POODLE, FREAK, Logjam), exploiting weak ciphers, Encoding bypass techniques to evade Intrusion Detection Systems (IDS).

### Layer 7: Application Layer
The Application Layer is the OSI layer closest to the end user. It provides network services directly to the user's applications.
*   **Core Functions:** Network virtual terminal, File transfer, access, and management (FTAM), Mail services, Directory services.
*   **Protocols:** HTTP, HTTPS, FTP, SMTP, DNS, SSH, Telnet, SNMP, DHCP.
*   **VAPT Perspective:** This is the most expansive attack surface today. Web application vulnerabilities (SQL Injection, Cross-Site Scripting, CSRF, Insecure Direct Object References), DNS spoofing/cache poisoning, SMTP relay abuse, Brute forcing application credentials, and exploiting logical flaws in application design.

## 3. The TCP/IP Protocol Suite

While the OSI model is a theoretical framework, the TCP/IP protocol suite is the practical implementation that powers the Internet. Developed by the Department of Defense (DoD), the TCP/IP model condenses the seven layers of the OSI model into four layers.

### The Four Layers of TCP/IP

1.  **Network Access Layer (Link Layer):** Maps to OSI Layers 1 and 2. It deals with the physical transmission of data and logical addressing on the local network (MAC). It defines how data is sent as frames over the physical medium.
2.  **Internet Layer:** Maps to OSI Layer 3. It is responsible for logical addressing (IP) and routing packets across multiple inter-connected networks.
3.  **Transport Layer:** Maps to OSI Layer 4. It handles end-to-end communication, error recovery, and flow control (TCP, UDP).
4.  **Application Layer:** Maps to OSI Layers 5, 6, and 7. It provides protocols that support end-user applications (HTTP, FTP, DNS).

### Comparing OSI and TCP/IP

Understanding the mapping between the two models is crucial for translating theoretical vulnerabilities into practical exploits during a VAPT engagement.

| OSI Layer | OSI Layer Name | TCP/IP Layer | PDU (Protocol Data Unit) |
| :--- | :--- | :--- | :--- |
| 7 | Application | Application | Data / Message |
| 6 | Presentation | Application | Data / Message |
| 5 | Session | Application | Data / Message |
| 4 | Transport | Transport | Segment (TCP) / Datagram (UDP) |
| 3 | Network | Internet | Packet |
| 2 | Data Link | Network Access | Frame |
| 1 | Physical | Network Access | Bit |

## 4. Encapsulation and Decapsulation

Data must traverse down the network stack on the sender's side, travel across the medium, and traverse up the network stack on the receiver's side. This process involves Encapsulation (adding headers) and Decapsulation (removing headers).

### The Encapsulation Process

When an application (e.g., a web browser) sends an HTTP GET request, it passes the data down to the Transport layer.
1.  **Transport Layer:** Adds a TCP header containing the source and destination ports. The PDU is now a **Segment**.
2.  **Internet/Network Layer:** Adds an IP header containing the source and destination IP addresses. The PDU is now a **Packet**.
3.  **Network Access/Data Link Layer:** Adds a frame header containing the source and destination MAC addresses, and a trailer (FCS - Frame Check Sequence) for error detection. The PDU is now a **Frame**.
4.  **Physical Layer:** Converts the frame into bits and transmits them over the physical medium.

### Visualizing Encapsulation (ASCII Diagram)

```text
+-----------------------------------------------------------------------------------+
|                        ENCAPSULATION / DECAPSULATION FLOW                         |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Application Data (e.g., HTTP GET /)]                        <-- Layer 7/6/5     |
|          | Encapsulate                                                            |
|          v                                                                        |
|  [TCP Header] [Application Data]                              <-- Layer 4         |
|          |    (Segment)                                                           |
|          v                                                                        |
|  [IP Header]  [TCP Header] [Application Data]                 <-- Layer 3         |
|          |    (Packet)                                                            |
|          v                                                                        |
|  [MAC Hdr]    [IP Header]  [TCP Header] [App Data] [FCS]      <-- Layer 2         |
|          |    (Frame)                                                             |
|          v                                                                        |
|  101011000101010010100011110010100101010110001...             <-- Layer 1         |
|               (Bits over physical wire)                                           |
|                                                                                   |
|  --> At the destination, the process reverses (Decapsulation), stripping          |
|      the headers one by one as the data moves UP the stack.                       |
+-----------------------------------------------------------------------------------+
```

## 5. Packet Analysis and VAPT Relevance

When penetration testers use packet capture tools like Wireshark or tcpdump, they are inspecting these encapsulated PDUs. A core skill in network security is the ability to visually dissect a hex dump or protocol tree into its constituent layers.

For instance, consider a typical internal network penetration test:
1.  **Layer 2 Discovery:** The attacker uses ARP scanning (`arp-scan`, `netdiscover`) to map active MAC addresses and identify live hosts on the local subnet.
2.  **Layer 3 Mapping:** The attacker performs ICMP ping sweeps (`nmap -sn`) to find live hosts routed across subnets.
3.  **Layer 4 Scanning:** The attacker conducts SYN scans (`nmap -sS`) to enumerate open TCP and UDP ports, identifying running services.
4.  **Layer 7 Exploitation:** The attacker interacts with discovered services (e.g., SMB on port 445, HTTP on port 80) using specific application payloads to exploit vulnerabilities (like EternalBlue or SQLi).

Every step of the cyber kill chain is intrinsically linked to manipulating protocols at specific layers of the OSI model and TCP/IP stack. By recognizing the constraints of each layer, an attacker can craft payloads that bypass filtering (e.g., using L3 fragmentation to bypass L4 firewalls).

## 6. Security Controls per Layer

Defenders implement security controls that map directly to these layers:
*   **Layer 2:** Port Security limits MAC addresses per switch port. Dynamic ARP Inspection (DAI) prevents ARP spoofing. 802.1X provides Network Access Control.
*   **Layer 3:** Network Firewalls block unauthorized IP addresses. Access Control Lists (ACLs) on routers filter traffic. IPsec provides encrypted tunnels.
*   **Layer 4:** Stateful Firewalls track TCP connection states to block out-of-state packets. TCP SYN Cookies mitigate SYN flood attacks.
*   **Layer 7:** Web Application Firewalls (WAF) inspect HTTP traffic for SQLi/XSS. Intrusion Prevention Systems (IPS) scan application payloads for malware signatures.

## 7. Conclusion

The OSI and TCP/IP models are not just theoretical constructs; they are the literal blueprints of the digital world. A master penetration tester visualizes network traffic not as abstract data, but as layered constructs of headers and payloads. To attack a network successfully, you must first understand the fundamental rules governing its operation.

---
## Chaining Opportunities
*   Understanding Layer 2 boundaries and encapsulation is an essential prerequisite before attempting MAC or ARP manipulation detailed in [[05 - ARP Protocol and Layer 2 Networking]].
*   Layer 3 and Layer 4 fundamentals directly lead into the practical protocol analysis covered in [[04 - Understanding TCP UDP and ICMP]].
*   Knowing how IP routing works at Layer 3 prepares you for the infrastructure architecture discussed in [[03 - Introduction to Routing and Switching]].

## Related Notes
*   [[02 - IP Addressing Subnetting and CIDR Notation]]
*   [[03 - Introduction to Routing and Switching]]
*   [[04 - Understanding TCP UDP and ICMP]]
*   [[05 - ARP Protocol and Layer 2 Networking]]
