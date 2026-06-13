---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 42"
---

# Network QnA - Module 42 - VLAN Hopping and Layer 2 Attacks

```text
       Layer 2 Attack Topologies & Frame Mechanics
+-------------------------------------------------------+
| 802.1Q Double Tagging Frame Anatomy                   |
| +------+----------+----------+----------+---------+   |
| | MAC  | TPID x81 | TPID x81 | Ether    | Payload |   |
| | Hdr  | Native   | Target   | Type     |         |   |
| |      | VLAN ID  | VLAN ID  |          |         |   |
| +------+----------+----------+----------+---------+   |
+-------------------------------------------------------+
| Switch CAM Table Exhaustion (MAC Flooding)            |
| [Attacker] ---> Generates 100k random MACs ---> [SW1] |
| SW1 CAM Table Fills Up -> Fails open to HUB mode      |
| SW1 broadcasts all traffic -> [Attacker Sniffs]       |
+-------------------------------------------------------+
```

## Formal Technical Questions

**Q1: Explain the mechanics of VLAN Hopping via Switch Spoofing using Dynamic Trunking Protocol (DTP).**
**Answer:**
Switch Spoofing exploits the default configuration of many Cisco switches, where ports are set to `dynamic desirable` or `dynamic auto`. 
Dynamic Trunking Protocol (DTP) is used to automatically negotiate trunk links between switches.
- **Mechanism:** An attacker connects a host to a switch port and generates crafted DTP `desirable` frames using tools like Yersinia. The switch interprets the attacker's host as another switch and converts the access port into a trunk port (802.1Q). 
- **Impact:** As a trunk link, the attacker's port now receives broadcast and multicast traffic for all VLANs permitted on the trunk. Furthermore, the attacker can tag their outbound frames with any VLAN ID, allowing them to communicate directly with hosts on segregated VLANs, completely bypassing Layer 3 routers and firewalls.

**Q2: How does an 802.1Q Double Tagging attack work? What specific network conditions are required for it to be successful?**
**Answer:**
Double Tagging exploits the way some switches process 802.1Q tags when traffic is forwarded across trunk links.
- **Mechanism:** The attacker crafts an Ethernet frame with two 802.1Q tags. The outer tag belongs to the Native VLAN of the trunk link (the VLAN the attacker is currently on), and the inner tag belongs to the target VLAN.
- **Execution:** When the first switch receives the frame, it strips the outer tag (because it is the Native VLAN and native VLAN traffic crosses trunks untagged) and forwards the frame across the trunk. The second switch receives the frame, sees the inner tag, assumes it is the legitimate tag, and forwards the packet to the target VLAN.
- **Conditions:** This attack is strictly unidirectional. It requires the attacker to be on the Native VLAN of the trunk link connecting the switches. It is generally used for one-way exploitation, such as sending a malicious UDP packet or an exploit payload that doesn't require a TCP handshake.

**Q3: Describe MAC Flooding and its implications on a Layer 2 switch. How does a switch behave when its CAM table is exhausted?**
**Answer:**
A switch maintains a Content Addressable Memory (CAM) table that maps MAC addresses to physical switch ports.
- **Mechanism:** Using tools like `macof`, an attacker rapidly generates thousands of Ethernet frames with randomly spoofed source MAC addresses.
- **Exhaustion:** The switch attempts to learn all these new MAC addresses, rapidly filling the CAM table (which has limited memory).
- **Fail-Open:** Once the CAM table is full, the switch cannot learn new legitimate MAC addresses. For any incoming frame destined for a MAC not currently in the table, the switch must broadcast the frame out of all ports (like a traditional network Hub) to ensure delivery.
- **Impact:** The attacker can now sniff all unicast traffic destined for other hosts on the same VLAN, compromising confidentiality. Furthermore, legitimate traffic may be dropped, causing a Denial of Service.

## Scenario-Based Questions

**Q4: You are on a Red Team engagement inside a corporate office. You plug your device into a wall jack and land on a restrictive 'Guest' VLAN. You notice the switch port is configured with Port Security restricting MAC addresses. How do you bypass this and attempt lateral movement?**
**Answer:**
Bypassing Port Security requires impersonating an authorized device.
1. **Reconnaissance:** I would leave my interface in passive promiscuous mode and capture traffic to identify the legitimate MAC address of the device normally connected to that port (e.g., an IP phone or a corporate printer).
2. **Spoofing:** I would change my network interface's MAC address to match the authorized device (`macchanger -m <MAC> eth0`).
3. **VoIP VLAN Hopping:** If the authorized device was an IP phone, the port is likely configured for a Voice VLAN. I would inspect captured LLDP (Link Layer Discovery Protocol) or CDP (Cisco Discovery Protocol) packets to identify the Voice VLAN ID. 
4. **VLAN Tagging:** I would create a virtual sub-interface (e.g., `eth0.100`) tagged with the Voice VLAN ID. I can then request an IP via DHCP on the Voice VLAN, effectively jumping from the Guest VLAN to the Voice VLAN, which often has less restrictive routing to the internal corporate network.

**Q5: During an internal pentest, you need to execute a Man-In-The-Middle (MITM) attack against an entire subnet, but ARP spoofing is triggering the IDS and failing due to Dynamic ARP Inspection (DAI). How can you achieve MITM at Layer 2 without ARP spoofing?**
**Answer:**
If DAI blocks ARP spoofing, I would pivot to a **Spanning Tree Protocol (STP) Root Bridge Attack**.
- **Concept:** STP prevents Layer 2 routing loops by electing a Root Bridge (the central switch through which traffic flows). The election is based on the Bridge ID (Priority + MAC address).
- **Execution:** I would use Yersinia to broadcast malicious STP Bridge Protocol Data Units (BPDUs) asserting a Bridge Priority of 0 (the highest priority) and a very low MAC address.
- **Impact:** The switches on the network will elect my attacker machine as the new Root Bridge. Consequently, the spanning tree topology recalculates, and a significant portion of the inter-switch traffic will be routed through my machine.
- **Mitigation:** I must enable IP forwarding on my machine and bridge the interfaces carefully to avoid causing a catastrophic network loop, while passively sniffing the transit traffic.

## Deep-Dive Defensive Questions

**Q6: What is DHCP Snooping, and how does it prevent Layer 2 attacks like DHCP Starvation and Rogue DHCP Servers?**
**Answer:**
DHCP Snooping is a Layer 2 security feature that acts like a firewall between untrusted hosts and trusted DHCP servers.
- **Mechanism:** It categorizes switch ports as either 'Trusted' or 'Untrusted'. Trusted ports are connected to legitimate DHCP servers or uplinks. Untrusted ports are connected to end-user devices.
- **Rogue DHCP Prevention:** If a DHCP Offer packet (which should only come from a server) is received on an Untrusted port, the switch immediately drops the packet and can disable the port (err-disable).
- **DHCP Starvation Prevention:** DHCP Snooping limits the rate of DHCP Discover packets allowed on Untrusted ports. If an attacker floods Discover packets with spoofed MACs to exhaust the IP pool, the rate-limit triggers and shuts down the port.
- **Binding Database:** It builds a DHCP Snooping Binding Database mapping MAC addresses, IPs, lease times, VLANs, and ports, which is crucial for features like Dynamic ARP Inspection.

**Q7: Explain the concept of Private VLANs (PVLANs). How do they restrict lateral movement within the same IP subnet?**
**Answer:**
Private VLANs provide Layer 2 isolation between ports within the same broadcast domain (subnet). They divide a primary VLAN into secondary VLANs.
There are three types of PVLAN ports:
1. **Promiscuous (P-Port):** Typically connected to a router/firewall. It can communicate with all other ports within the PVLAN.
2. **Isolated (I-Port):** Connected to endpoints. An Isolated port can *only* communicate with Promiscuous ports. It cannot communicate with other Isolated ports, even if they are in the same subnet.
3. **Community (C-Port):** Ports assigned to the same community can communicate with each other and with the Promiscuous port, but not with other communities or Isolated ports.
**Security Implication:** PVLANs strictly enforce zero-trust at the access edge. Even if an attacker compromises a server on an Isolated port, they cannot perform Layer 2 pivoting (ARP spoofing, direct exploitation) against adjacent servers in the same subnet.

## Real-World Attack Scenario

**Scenario: Escaping an ESXi Management Network via Double Tagging**
An attacker gains access to a low-privileged Virtual Machine (VM) hosted on a VMware ESXi cluster.
1. **Architecture Analysis:** The attacker identifies that the VM's vSwitch port group is assigned to VLAN 50 (Native/Untagged on the physical switch trunk). The hypervisor management interfaces (vCenter, vMotion) reside on VLAN 10.
2. **Exploitation:** The physical switch trunk port connecting to the ESXi host uses VLAN 50 as the Native VLAN. The attacker crafts a malicious 802.1Q Double-Tagged frame. 
   - Outer Tag: VLAN 50.
   - Inner Tag: VLAN 10.
   - Payload: A single-packet UDP exploit targeting an unauthenticated deserialization vulnerability in the vCenter service.
3. **Execution:** The attacker transmits the packet. The physical switch receives it, strips the outer VLAN 50 tag (native), and forwards the packet out other trunk ports. 
4. **Impact:** The internal switch network reads the inner VLAN 10 tag and delivers the malicious payload directly to the vCenter server. The attacker gains Remote Code Execution on the vCenter server, effectively taking over the entire virtualization infrastructure without ever possessing an IP address on VLAN 10.

## Chaining Opportunities
- **Physical Intrusions:** Layer 2 attacks are heavily chained with rogue hardware implants (like LAN Turtles or Raspberry Pis) dropped during physical penetration tests.
- **Active Directory Compromise:** Layer 2 MITM attacks (like STP spoofing) are used to intercept internal DNS and SMB traffic, chaining into NTLM relay attacks against Domain Controllers.
- **Virtualization Escapes:** VLAN hopping techniques are critical for breaking out of restricted virtual networks in misconfigured SDDC (Software Defined Data Center) environments.

## Related Notes
- [[04 - Virtual Switch Security in ESXi and Hyper-V]]
- [[17 - Yersinia Protocol Exploitation Framework]]
- [[28 - Bypassing Network Access Control (NAC) Systems]]
- [[43 - ARP Spoofing and MITM]]
- [[55 - Spanning Tree Protocol Enhancements and Flaws]]
