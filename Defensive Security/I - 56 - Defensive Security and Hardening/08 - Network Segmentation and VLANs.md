---
tags: [defense, hardening, security, vapt]
difficulty: intermediate
module: "56 - Defensive Security and Hardening"
topic: "56.08 Network Segmentation and VLANs"
---

# 56.08 Network Segmentation and VLANs

## Introduction
Network segmentation is a foundational architectural security strategy that involves dividing a larger computer network into smaller, isolated subnetworks. The primary goal is to limit the blast radius of a successful cyberattack. If an attacker breaches one segment, they cannot easily pivot or move laterally to other, more sensitive segments. Virtual Local Area Networks (VLANs) are the traditional, primary Layer 2 mechanism used to achieve this logical segmentation over shared physical network infrastructure.

## The Problem with Flat Networks
In a "flat" network, all devices (workstations, servers, printers, domain controllers, IoT devices) reside in the same broadcast domain and IP subnet. 
- **The Risk:** If a low-privileged device, like a smart thermostat or a receptionist's workstation, is compromised via phishing or an unpatched vulnerability, the attacker has unrestricted line-of-sight network access to domain controllers, critical databases, and executive workstations.
- **Lateral Movement:** Flat networks make lateral movement trivial. Tools like Responder (for LLMNR/NBT-NS poisoning) or simple port scanners can rapidly enumerate and exploit the entire organization without crossing any security boundaries.
- **Broadcast Storms:** Beyond security, flat networks suffer from performance degradation due to excessive ARP and broadcast traffic.

## Architectural Diagram: Segmented Network

```text
                                    INTERNET
                                       |
                                 +-----+-----+
                                 | Edge FW   |
                                 +-----+-----+
                                       |
+-----------------------------------------------------------------------------------+
|                                 DMZ (VLAN 10)                                     |
|  +--------------+     +--------------+     +--------------+                       |
|  | Web Server 1 |     | Web Server 2 |     | VPN Gateway  |  (Publicly Accessible)|
|  +--------------+     +--------------+     +--------------+                       |
+------------------------------+----------------------------------------------------+
                               |
                        +------+------+
                        | Internal FW | (Strict Access Control Lists Enforced Here)
                        +------+------+
                               |
             +-----------------+-----------------+
             |                                   |
+------------+-------------+        +------------+-------------+
|    Servers (VLAN 20)     |        | Workstations (VLAN 30)   |
|                          |        |                          |
|  +-------+  +---------+  |        |  +-------+  +-------+    |
|  | App   |  | DB      |  |        |  | HR    |  | Dev   |    |
|  | Server|  | Server  |  |        |  | PC    |  | PC    |    |
|  +-------+  +---------+  |        |  +-------+  +-------+    |
+--------------------------+        +--------------------------+
             |                                   |
+------------+-------------+        +------------+-------------+
| Management (VLAN 40)     |        |     IoT (VLAN 50)        |
|                          |        |                          |
|  +-------+  +---------+  |        |  +-------+  +-------+    |
|  | Admin |  | Sec     |  |        |  | Smart |  | IP    |    |
|  | Jump  |  | Tools   |  |        |  | TV    |  | Cam   |    |
|  +-------+  +---------+  |        |  +-------+  +-------+    |
+--------------------------+        +--------------------------+
```

## How VLANs Work
VLANs operate at Layer 2 (Data Link Layer) of the OSI model. 
1. **802.1Q Tagging:** A VLAN inserts a tag (a 4-byte header) into the Ethernet frame. This tag identifies which logical network the frame belongs to.
2. **Logical Separation:** Switches read these tags and ensure that broadcast traffic from VLAN 10 does not leak into VLAN 20. Devices on different VLANs cannot communicate with each other directly at Layer 2. To them, it appears they are on entirely separate physical switches.
3. **Inter-VLAN Routing:** To allow communication between different VLANs, traffic must be routed through a Layer 3 device (a router, a firewall, or a Layer 3 switch). This is the crucial point where security policies (Access Control Lists) are enforced. The router strips the tag, inspects the packet, applies firewall rules, and then re-tags it for the destination VLAN.

## Strategic Segmentation Zones

A properly segmented network categorizes assets based on trust levels and operational roles. This follows the principles of MAC (Mandatory Access Control) architecture on a macro level.

### 1. The DMZ (Demilitarized Zone)
- **Purpose:** Houses external-facing services (Web servers, DNS, Email gateways, VPN terminators).
- **Security Posture:** Highly exposed. The assumption is that these machines are constantly under attack. 
- **Rules:** The DMZ can talk to the internet. The internet can talk to the DMZ. The DMZ *cannot* initiate connections into the internal network. Internal networks can initiate connections to the DMZ (e.g., to update content or pull logs).

### 2. Internal Server Zone
- **Purpose:** Houses internal applications, Active Directory domain controllers, and file servers.
- **Security Posture:** Protected. No direct internet access.
- **Rules:** Only specific ports required for specific services are allowed from the Workstation zone (e.g., allow 389/636 for LDAP). No outbound internet access without going through a strict proxy.

### 3. Database Zone (Highly Restricted)
- **Purpose:** The crown jewels. Stores all sensitive data (PII, Financials).
- **Security Posture:** Maximum isolation. 
- **Rules:** Cannot access the internet. Cannot be accessed by workstations directly. Only explicitly authorized Application Servers in the Internal Server zone can communicate with the databases over designated ports.

### 4. Workstation Zone
- **Purpose:** End-user devices and laptops.
- **Security Posture:** High risk due to human interaction (phishing, web browsing).
- **Rules:** Workstations often need internet access, but should be prevented from communicating with each other (Client Isolation/Private VLANs) to stop wormable malware (like ransomware) from spreading peer-to-peer.

### 5. IoT / Guest Zones
- **Purpose:** Untrusted devices (smart TVs, visitor laptops, smart fridges).
- **Security Posture:** Zero trust. 
- **Rules:** Internet access only. Absolutely no routing into internal company networks.

## Best Practices for Segmentation

1. **Avoid Over-Segmentation:** Creating hundreds of VLANs can create a management nightmare and routing performance bottlenecks. Segment logically based on business function and risk.
2. **Implement Strict ACLs:** Segmentation without strict Access Control Lists (ACLs) is useless. The router connecting the VLANs must act as a choke point, enforcing a **[[07 - Firewall Rules Allowlist vs Denylist]]** (default deny) policy. If VLANs can route freely to each other, you do not have segmentation.
3. **Client Isolation:** Within a workstation or guest VLAN, enable Private VLANs (PVLANs) or client isolation so devices in the same subnet cannot talk to each other.
4. **Secure the Management Plane:** Switches, hypervisors, and routers must be managed on a dedicated out-of-band management VLAN. Never manage network infrastructure from a standard user VLAN.
5. **Monitor Inter-VLAN Traffic:** Since all inter-VLAN traffic passes through a Layer 3 boundary, this is the ideal place to deploy **[[10 - Intrusion Detection IDS vs IPS]]** to monitor for lateral movement attempts.

## Advanced Concepts: Microsegmentation and SDN
Traditional VLANs provide macroscopic segmentation. 
- **SDN (Software-Defined Networking):** Abstracts the control plane from the data plane. Technologies like VXLAN overcome the 4,096 VLAN limitation, allowing for millions of isolated networks, primarily used in large data centers and cloud environments.
- **Microsegmentation:** Takes segmentation further, often implemented via SDN or host-based firewalls. It isolates workloads down to the individual VM or container level, regardless of their physical network location or IP subnet. This means even if two servers are on the same VLAN, they cannot communicate unless explicitly permitted by policy. This is a core tenant of **[[09 - Zero Trust Architecture]]**.

## Weaknesses and Exploits
- **VLAN Hopping:** Attackers can craft specialized packets (Double Tagging) or exploit misconfigured switch ports (DTP - Dynamic Trunking Protocol negotiation) to inject traffic into a VLAN they do not belong to. Ensure switch ports are statically configured as access or trunk ports.
- **Router Misconfiguration:** If the inter-VLAN router has a permissive ACL (e.g., `permit ip any any`), the segmentation is bypassed entirely.
- **Dual-Homed Systems:** Servers equipped with two network cards connected to two different VLANs bridge the gap. If compromised, an attacker can use the server as a router to bypass the firewall completely.

## Chaining Opportunities
- Attackers look to bypass **[[08 - Network Segmentation and VLANs]]** by exploiting vulnerabilities in the routing layer or finding dual-homed servers.
- Effective segmentation relies heavily on applying the **[[03 - Principle of Least Privilege]]** to the network routing rules.
- Directly supports the implementation of **[[09 - Zero Trust Architecture]]** by establishing clear physical and logical boundaries.
- **[[06 - Database Hardening]]** is incomplete without isolating the database into its own highly restricted VLAN segment.

## Related Notes
- [[01 - Security Baselines]]
- [[02 - Defense in Depth]]
- [[07 - Firewall Rules Allowlist vs Denylist]]
- [[09 - Zero Trust Architecture]]
- [[10 - Intrusion Detection IDS vs IPS]]
