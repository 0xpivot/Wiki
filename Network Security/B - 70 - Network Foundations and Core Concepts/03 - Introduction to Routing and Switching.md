---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.03 Introduction to Routing and Switching"
---
# 03 - Introduction to Routing and Switching

## 1. Introduction to Network Infrastructure

While IP addressing provides the logical coordinates of devices on a network, routers and switches are the actual physical and logical engines that move data from a source to a destination. Understanding the mechanics of routing and switching is critical for a penetration tester. It dictates how traffic flows, where boundaries and chokepoints exist, and how Man-in-the-Middle (MitM) or lateral movement attacks can be executed.

If you don't understand how a switch forwards a frame or how a router chooses a path, you cannot effectively exploit network misconfigurations.

## 2. Core Network Devices

### Hubs (Legacy Layer 1)
Hubs operate at the Physical Layer. They are "dumb" multi-port repeaters. When a frame enters one port on a hub, it is simply amplified and broadcasted out of *all* other ports, regardless of the destination MAC address.
*   **Security Implication:** In a hubbed network, any device running a packet sniffer (like Wireshark) in promiscuous mode can capture all traffic on the network. This makes passive reconnaissance incredibly easy. Hubs are largely extinct in modern enterprise networks.

### Switches (Layer 2)
Switches operate primarily at the Data Link layer. Unlike hubs, switches are intelligent. They learn which MAC addresses are connected to which physical ports and forward frames *only* to the specific port where the destination device resides.
*   **Security Implication:** Because traffic is unicast directly port-to-port, a standard packet sniffer will only see traffic destined for its own machine, plus broadcast/multicast traffic. To sniff traffic belonging to others on a switched network, an attacker must employ active techniques like ARP spoofing or CAM table overflow.

### Routers (Layer 3)
Routers operate at the Network layer. While switches connect devices within the *same* network, routers connect *different* networks together. They inspect the destination IP address of a packet and consult a Routing Table to determine the best path to forward the packet toward its ultimate destination.
*   **Security Implication:** Routers act as boundaries. They separate broadcast domains. They are often where Network Address Translation (NAT) and Access Control Lists (ACLs) are applied, serving as primary chokepoints for security enforcement.

## 3. Switching Mechanics and the CAM Table

The core function of a switch relies on its Content Addressable Memory (CAM) table, also known as the MAC Address Table.

### The Learning and Forwarding Process
1.  **Learning:** When a switch receives a frame, it looks at the *Source MAC Address*. It records this MAC address and the physical port the frame arrived on into its CAM table.
2.  **Forwarding (Known Unicast):** The switch then looks at the *Destination MAC Address* in the frame. If that MAC address is already in the CAM table, the switch forwards the frame *only* out of the corresponding port.
3.  **Flooding (Unknown Unicast & Broadcasts):** If the destination MAC address is NOT in the CAM table (Unknown Unicast), or if the frame is a Broadcast (MAC `FF:FF:FF:FF:FF:FF`), the switch "floods" the frame out of *all* ports except the one it arrived on.

### Switch Attack: CAM Table Overflow (MAC Flooding)
The CAM table has a finite memory capacity. In a CAM Table Overflow attack (e.g., using a tool like `macof`), an attacker bombards the switch with thousands of fake frames containing random, spoofed source MAC addresses.
*   **The Result:** The CAM table fills up instantly. When the switch receives legitimate frames, it cannot find the destination MAC in its full table, forcing it into "Fail-Open" mode.
*   **Fail-Open:** The switch reverts to hub-like behavior, flooding all unknown unicast traffic out of all ports. The attacker can now passively sniff all network traffic passing through the switch.

## 4. Virtual LANs (VLANs) and Trunking

VLANs allow network administrators to logically segment a single physical switch into multiple isolated virtual switches. Devices on different VLANs cannot communicate directly with each other via Layer 2; they require a router to route traffic between them.

*   **VLAN Tagging (802.1Q):** To identify which VLAN a frame belongs to when passing between switches, a 4-byte VLAN tag is inserted into the Ethernet header.
*   **Access Ports:** Connect to end devices (PCs). They belong to a single VLAN and strip the VLAN tag before sending data to the PC.
*   **Trunk Ports:** Connect switches to other switches or routers. They carry traffic for multiple VLANs and maintain the 802.1Q tags to keep traffic segregated.

### Switch Attack: VLAN Hopping
VLAN Hopping allows an attacker on one VLAN to gain unauthorized access to traffic on another VLAN.
1.  **Switch Spoofing:** An attacker connects to a port configured for Dynamic Trunking Protocol (DTP) and negotiates a trunk link. The attacker's machine acts like a switch, gaining access to all VLANs traversing the trunk.
2.  **Double Tagging:** An attacker prepends two 802.1Q VLAN tags to a frame. The first switch strips the outer tag (its native VLAN) and forwards the frame. The second switch sees the inner tag and forwards the frame into the victim's VLAN. This is generally a unidirectional attack.

## 5. Spanning Tree Protocol (STP)

In networks with redundant links (to prevent downtime if a cable breaks), switches can accidentally create endless forwarding loops. A broadcast frame would circulate forever, causing a "Broadcast Storm" that melts the network.
*   **STP (802.1D):** Spanning Tree Protocol detects these physical loops and logically blocks certain ports to create a loop-free logical topology.
*   **STP Attacks:** An attacker can inject forged BPDU (Bridge Protocol Data Unit) packets to force an STP recalculation, making the attacker's machine the "Root Bridge." This allows the attacker to intercept or drop traffic across the network infrastructure.

## 6. Routing Mechanics

While switches use MAC addresses to forward frames locally, routers use IP addresses and Routing Tables to move packets across network boundaries.

### The Routing Process
1.  A host determines the destination IP is on a different subnet (using bitwise ANDing).
2.  The host sends the packet to its Default Gateway (a router interface).
3.  The router strips the Layer 2 frame, inspects the Layer 3 IP destination, and consults its Routing Table.
4.  The routing table dictates the "Next Hop" interface.
5.  The router encapsulates the packet into a *new* Layer 2 frame destined for the next hop's MAC address and sends it out.

### Visualizing a Routed and Switched Network (ASCII Diagram)

```text
+---------------------------------------------------------------------------------+
|                    ROUTING AND SWITCHING ARCHITECTURE                           |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [Attacker PC]                                             [Target Server]      |
|  IP: 10.0.1.50                                             IP: 10.0.2.100       |
|  MAC: AA:AA:..                                             MAC: CC:CC:..        |
|  VLAN 10 (Sales)                                           VLAN 20 (DB)         |
|       |                                                         |               |
|       | (Access Port)                                           | (Access Port) |
|       v                                                         v               |
|  +---------+                                               +---------+          |
|  | Switch A| =====(802.1Q Trunk Link carrying all VLANs)==>| Switch B|          |
|  +---------+                                               +---------+          |
|       |                                                         |               |
|       | (Trunk Port)                                            |               |
|       v                                                         |               |
|  +--------------------+                                         |               |
|  |   Core Router      | <---------------------------------------+               |
|  | (Default Gateway)  |                                                         |
|  | VLAN 10: 10.0.1.1  |                                                         |
|  | VLAN 20: 10.0.2.1  |                                                         |
|  +--------------------+                                                         |
|                                                                                 |
|  Flow from Attacker to Target:                                                  |
|  1. Attacker sends frame to Switch A (Dest MAC = Router's VLAN 10 MAC).         |
|  2. Switch A forwards up Trunk, adding VLAN 10 Tag.                             |
|  3. Router receives, strips tag. Sees IP dest is 10.0.2.100.                    |
|  4. Router routes packet from VLAN 10 interface to VLAN 20 interface.           |
|  5. Router creates NEW frame (Dest MAC = Target Server MAC), adds VLAN 20 Tag.  |
|  6. Router sends out Trunk to Switch B.                                         |
|  7. Switch B strips VLAN 20 Tag, forwards out Access port to Target Server.     |
+---------------------------------------------------------------------------------+
```

## 7. Static vs. Dynamic Routing

Routers must populate their routing tables to know where networks are located.
*   **Static Routing:** Administrators manually enter routes. Simple, secure, but impossible to maintain on large, shifting networks.
*   **Dynamic Routing:** Routers run protocols to automatically share network information with neighbor routers and build their tables dynamically.
    *   **IGP (Interior Gateway Protocols):** Used *within* an organization (Autonomous System). Examples: OSPF, EIGRP, RIP.
    *   **EGP (Exterior Gateway Protocols):** Used *between* different organizations/ISPs. Example: BGP (Border Gateway Protocol) - the routing protocol of the global Internet.

### Router Attacks: Route Spoofing / Injection
If dynamic routing protocols are not secured with authentication (e.g., OSPF MD5 authentication), an attacker can inject malicious routing updates.
*   An attacker advertises that their machine is the best route to a specific subnet.
*   The routers update their tables, and all traffic meant for that subnet is silently redirected to the attacker (a massive MitM attack).

## 8. Defenses and Mitigation Strategies

Network engineers implement various controls to prevent these L2/L3 attacks:
*   **Port Security:** Restricts switch ports to only allow specific, known MAC addresses. Limits the number of MACs per port to prevent CAM overflow.
*   **BPDU Guard:** Disables a port if it unexpectedly receives STP BPDU packets, preventing rogue root bridge attacks.
*   **Dynamic ARP Inspection (DAI):** Validates ARP packets against the DHCP snooping binding database, preventing ARP poisoning.
*   **VLAN Access Control Lists (VACLs) / Router ACLs:** Explicitly permit or deny traffic between VLANs at the routing boundary.
*   **Routing Protocol Authentication:** Requiring passwords or cryptographic hashes for routers to accept OSPF or BGP updates.

## 9. Summary for VAPT

When analyzing a target network, the topology dictates your movement. A flat network (one large VLAN) allows immediate lateral movement. A highly segmented network requires you to pivot through compromised hosts that have access to multiple VLANs, or attack the routing infrastructure directly.

---
## Chaining Opportunities
*   To fully exploit switched networks, understanding ARP poisoning is vital. Proceed to [[05 - ARP Protocol and Layer 2 Networking]].
*   The routing concepts here rely heavily on the logical IP structure defined in [[02 - IP Addressing Subnetting and CIDR Notation]].
*   Once traffic is routed, end-to-end communication is managed by Transport protocols. See [[04 - Understanding TCP UDP and ICMP]].

## Related Notes
*   [[01 - OSI Model and TCP IP Protocol Suite]]
*   [[02 - IP Addressing Subnetting and CIDR Notation]]
*   [[04 - Understanding TCP UDP and ICMP]]
*   [[05 - ARP Protocol and Layer 2 Networking]]
