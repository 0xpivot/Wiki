---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.02 IP Addressing Subnetting and CIDR Notation"
---
# 02 - IP Addressing, Subnetting, and CIDR Notation

## 1. Introduction to IP Addressing

In the TCP/IP protocol suite, the Internet Protocol (IP) operates at the Network Layer (OSI Layer 3). Its primary function is to provide a logical addressing scheme that allows devices to be uniquely identified and enables packets to be routed across multiple diverse networks. Without IP addressing, the Internet as we know it could not exist.

For a penetration tester, IP addressing is the coordinate system of the battlefield. Understanding how IP addresses are structured, how networks are divided (subnetting), and how routers interpret these addresses is critical for network mapping, lateral movement, and pivoting during an engagement.

## 2. IPv4 Architecture

Internet Protocol version 4 (IPv4) is the most widely deployed network layer protocol.
*   **Size:** An IPv4 address is 32 bits long.
*   **Structure:** It is divided into four 8-bit sections called "octets."
*   **Representation:** To make them human-readable, IPv4 addresses are written in "dotted-decimal" format. Each octet is converted from binary to a decimal number ranging from 0 to 255.
    *   *Example:* `192.168.1.10`
    *   *Binary equivalent:* `11000000.10101000.00000001.00001010`

### Network vs. Host Portions
Every IP address has two distinct parts:
1.  **Network Portion (Network ID):** Identifies the specific network the device resides on. Routers use this to move packets between networks.
2.  **Host Portion (Host ID):** Identifies the specific device (node) within that network.

The separation between the network and host portions is determined by the **Subnet Mask**.

## 3. Classful Addressing (The Old Way)

Historically, IP addresses were divided into strict "Classes" based on their first few bits. While this system is largely obsolete due to CIDR, it's still heavily referenced in older literature and some legacy network configurations.

*   **Class A:** Designed for massive networks.
    *   First octet range: 1 - 126
    *   Default Subnet Mask: 255.0.0.0 (/8)
    *   Structure: `Network.Host.Host.Host`
    *   Supports 16.7 million hosts per network.
*   **Class B:** Designed for medium-to-large networks.
    *   First octet range: 128 - 191
    *   Default Subnet Mask: 255.255.0.0 (/16)
    *   Structure: `Network.Network.Host.Host`
    *   Supports 65,534 hosts per network.
*   **Class C:** Designed for small networks.
    *   First octet range: 192 - 223
    *   Default Subnet Mask: 255.255.255.0 (/24)
    *   Structure: `Network.Network.Network.Host`
    *   Supports 254 hosts per network.
*   **Class D:** Reserved for Multicasting (224 - 239).
*   **Class E:** Reserved for Experimental use (240 - 255).

## 4. Private vs. Public IP Space (RFC 1918)

Because the IPv4 address space (approx. 4.3 billion addresses) was rapidly depleting, the IETF reserved specific blocks of IP addresses strictly for internal, private use within organizations. These addresses are non-routable on the public Internet.

*   **Class A Private Block:** `10.0.0.0` to `10.255.255.255` (10.0.0.0/8)
*   **Class B Private Block:** `172.16.0.0` to `172.31.255.255` (172.16.0.0/12)
*   **Class C Private Block:** `192.168.0.0` to `192.168.255.255` (192.168.0.0/16)

**VAPT Note:** During internal pentests, you will almost exclusively encounter RFC 1918 addresses. To access the internet, devices on these networks use Network Address Translation (NAT) to map their private IP to a public, internet-routable IP.

### Special IPv4 Addresses
*   **Loopback (127.x.x.x):** Used for testing the local TCP/IP stack. `127.0.0.1` is "localhost".
*   **APIPA / Link-Local (169.254.x.x):** Automatically assigned if a device requests a DHCP address but no DHCP server responds.
*   **Network Address:** The first IP in a subnet (all host bits are 0). Identifies the network itself.
*   **Broadcast Address:** The last IP in a subnet (all host bits are 1). Used to send traffic to *all* hosts on the subnet.

## 5. Subnet Masks and Bitwise ANDing

A subnet mask is a 32-bit number that masks an IP address, separating the IP address into network and host addresses.
When a computer wants to send a packet, it must determine if the destination IP is on the *local* network or a *remote* network. It does this using a Bitwise AND operation between the IP address and the Subnet Mask.

*   `1 AND 1 = 1`
*   `1 AND 0 = 0`
*   `0 AND 1 = 0`
*   `0 AND 0 = 0`

### Visualizing Bitwise AND (ASCII Architecture Diagram)

```text
+-----------------------------------------------------------------------------+
|                     BITWISE AND OPERATION FOR ROUTING                       |
+-----------------------------------------------------------------------------+
| Scenario: Host 192.168.1.10 (Subnet 255.255.255.0) wants to talk to an IP.  |
| The host calculates its OWN Network ID first:                               |
|                                                                             |
| IP Address:    192  .   168  .    1   .   10                                |
| IP Binary:  11000000.10101000.00000001.00001010                             |
| Mask (Dec):    255  .   255  .   255  .    0                                |
| Mask (Bin): 11111111.11111111.11111111.00000000                             |
|             -----------------------------------  (Bitwise AND)              |
| Result:     11000000.10101000.00000001.00000000                             |
| Network ID:    192  .   168  .    1   .    0                                |
|                                                                             |
| -> If the Destination IP's Network ID matches 192.168.1.0, traffic is sent  |
|    directly via Layer 2 (ARP).                                              |
| -> If it does NOT match, traffic is sent to the Default Gateway (Router).   |
+-----------------------------------------------------------------------------+
```

## 6. Classless Inter-Domain Routing (CIDR)

Classful networks wasted millions of IP addresses. If a company needed 300 IPs, a Class C (254 IPs) was too small, forcing them to take a Class B (65,534 IPs) and wasting over 65,000 addresses.

CIDR abolished classes, allowing subnet masks to end on *any* bit boundary, not just /8, /16, or /24.
CIDR notation appends a slash and the number of network bits to the IP address.
*   `192.168.1.0/24` means the first 24 bits are the network portion.
*   `10.1.0.0/22` means the first 22 bits are the network portion.

## 7. Subnetting Math and Variable Length Subnet Masking (VLSM)

Subnetting is the process of borrowing bits from the host portion of an address to create smaller, isolated networks (subnets). VLSM allows a network administrator to use different subnet masks for different subnets within the same overall address space, optimizing IP allocation.

### The Magic Number Formula
To calculate the number of subnets and hosts:
*   **Number of Subnets:** `2^s` (where 's' is the number of borrowed network bits).
*   **Number of Hosts per Subnet:** `2^h - 2` (where 'h' is the number of remaining host bits. We subtract 2 for the Network ID and Broadcast IP).

### Subnetting Example
Given the network `192.168.10.0/24`, you need to create 4 subnets.
1.  **Current state:** /24 means 24 network bits, 8 host bits.
2.  **Borrowing bits:** To get 4 subnets, we need `2^s >= 4`. So, `s = 2`. We borrow 2 bits.
3.  **New Mask:** 24 + 2 = 26. The new CIDR is `/26`.
    *   Mask in binary: `11111111.11111111.11111111.11000000`
    *   Mask in decimal: `255.255.255.192`
4.  **Hosts per subnet:** Remaining host bits `h = 6`. Hosts = `2^6 - 2 = 62` usable hosts per subnet.
5.  **Subnet ranges:** The block size (Magic Number) is `256 - 192 = 64`.
    *   Subnet 1: `192.168.10.0/26` (Range: .1 to .62, Broadcast: .63)
    *   Subnet 2: `192.168.10.64/26` (Range: .65 to .126, Broadcast: .127)
    *   Subnet 3: `192.168.10.128/26` (Range: .129 to .190, Broadcast: .191)
    *   Subnet 4: `192.168.10.192/26` (Range: .193 to .254, Broadcast: .255)

## 8. IPv6 Addressing (Brief Overview)

Due to IPv4 exhaustion, IPv6 was introduced.
*   **Size:** 128 bits long (provides 3.4 x 10^38 addresses).
*   **Representation:** Eight groups of four hexadecimal digits separated by colons.
    *   *Example:* `2001:0db8:85a3:0000:0000:8a2e:0370:7334`
*   **Simplification rules:** Leading zeros can be omitted. Consecutive groups of zero value can be replaced with a double colon `::` (only once per address).
*   **No Broadcasts:** IPv6 uses Multicast heavily instead of Broadcasts.

## 9. VAPT Implications of IP Addressing and Subnetting

For a penetration tester, IP addressing is crucial for several phases of the attack lifecycle:

1.  **Scope Definition & Verification:** Clients provide scoping in CIDR notation (e.g., "You are authorized to test `10.50.0.0/16`"). If a pentester miscalculates the subnet bounds, they might inadvertently attack an out-of-scope system, leading to legal and professional disaster.
2.  **Network Mapping and Reconnaissance:**
    *   Attackers perform ping sweeps across subnet ranges. Knowing the broadcast address allows an attacker to send an ICMP Echo Request to the broadcast IP, potentially getting replies from many hosts simultaneously (though modern OSs drop these to prevent Smurf attacks).
3.  **Lateral Movement and Pivoting:**
    *   If an attacker compromises a DMZ server at `172.16.5.15/28`, they will analyze the routing tables to see what other subnets are accessible.
    *   If the network is poorly subnetted (a "flat network" where everything is on a massive /16 subnet), an attacker compromising a low-level workstation immediately has direct line-of-sight to Domain Controllers and production databases without hitting a routing firewall.
4.  **Evasion Techniques:**
    *   Understanding IP fragmentation and overlapping fragments (which rely heavily on IP headers) can help bypass Intrusion Detection Systems (IDS).
    *   Using obscure IP representations (e.g., converting dotted-decimal to pure decimal, octal, or hex formats) can bypass poorly written WAF filters or SSRF protections. For example, `http://127.0.0.1` can also be written as `http://2130706433`.

## 10. Summary

Mastery of IP addressing, subnet masking, and CIDR math is an absolute non-negotiable skill for any network engineer or penetration tester. It dictates how boundaries are drawn within an infrastructure and, consequently, how an attacker can cross them.

---
## Chaining Opportunities
*   IP Addressing is the logical layer that maps to physical MAC addresses via ARP. Read [[05 - ARP Protocol and Layer 2 Networking]] to understand this bridge.
*   To understand how packets move from one subnet to another, you must dive into routing mechanics in [[03 - Introduction to Routing and Switching]].
*   Once IP packets reach their destination, the Transport layer takes over. Proceed to [[04 - Understanding TCP UDP and ICMP]].

## Related Notes
*   [[01 - OSI Model and TCP IP Protocol Suite]]
*   [[03 - Introduction to Routing and Switching]]
*   [[04 - Understanding TCP UDP and ICMP]]
*   [[05 - ARP Protocol and Layer 2 Networking]]
