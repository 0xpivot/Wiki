---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.05 ARP Protocol and Layer 2 Networking"
---
# 05 - ARP Protocol and Layer 2 Networking

## 1. The Missing Link Between Layer 2 and Layer 3

To fully comprehend local network attacks, we must bridge the gap between logical addressing (IP addresses at OSI Layer 3) and physical addressing (MAC addresses at OSI Layer 2). 

When a computer wants to send data to another computer on the *same* local network (subnet), it encapsulates the data into an IP packet with the destination IP address. However, switches (which operate at Layer 2) do not understand IP addresses; they only forward frames based on physical MAC addresses.

Therefore, the sending computer must figure out the MAC address associated with the destination IP address before it can build the Ethernet frame and put it on the wire. This critical translation mechanism is the **Address Resolution Protocol (ARP)**.

## 2. Address Resolution Protocol (ARP) Mechanics

ARP is a simple, stateless protocol that operates over the local subnet broadcast domain. 

### The ARP Process: Request and Reply
1.  **The Problem:** Host A (`192.168.1.10`) wants to talk to Host B (`192.168.1.50`), but Host A does not know Host B's MAC address.
2.  **ARP Request:** Host A formulates an ARP Request packet: *"Who has 192.168.1.50? Tell 192.168.1.10."*
    *   This packet is encapsulated in a Layer 2 frame with a **Destination MAC of `FF:FF:FF:FF:FF:FF`** (the Ethernet Broadcast address).
    *   Because it's a broadcast, the switch floods it out of every port.
    *   Every device on the subnet receives the request, opens it, and checks the target IP.
3.  **ARP Reply:** Host B sees that its IP matches the target IP in the request. It generates an ARP Reply: *"I have 192.168.1.50, and my MAC is BB:BB:BB:BB:BB:BB."*
    *   This reply is sent directly back to Host A as a **Unicast** frame (using Host A's source MAC address from the request).
    *   All other devices on the subnet ignore the request since the IP did not match theirs.

### The ARP Cache (Table)
To avoid spamming the network with broadcast requests every time a packet needs to be sent, devices maintain an ARP Cache (or ARP Table). This is a temporary memory store that maps IP addresses to MAC addresses.
*   When Host A receives the ARP Reply, it caches the mapping `192.168.1.50 -> BB:BB:BB:BB:BB:BB` for a short period (usually a few minutes).
*   You can view this cache on Windows or Linux using the command: `arp -a`.

## 3. Special ARP Types

*   **Gratuitous ARP:** An ARP Reply that was not prompted by an ARP Request. A host sends this broadcast to announce its IP and MAC to the entire network, forcing all other hosts to update their ARP caches. This is legitimately used when a machine boots up or changes its IP, but is heavily abused in attacks.
*   **Proxy ARP:** A technique where a router answers ARP requests intended for another device. It allows a router to act as a proxy for devices on different subnets, making them appear as if they are on the same physical network.
*   **RARP (Reverse ARP):** Legacy protocol where a device knows its MAC but needs to request an IP address (largely replaced by DHCP).

## 4. The Vulnerability: ARP Spoofing / Poisoning

The fundamental flaw of ARP is that it is **stateless and unauthenticated**.
1.  Hosts will accept an ARP Reply even if they never sent an ARP Request.
2.  Hosts will blindly overwrite their ARP cache with the new information provided in any ARP packet.
3.  There is no cryptographic mechanism in the standard ARP protocol to verify the sender's identity.

This opens the door for **ARP Spoofing** (also known as ARP Poisoning).

### How ARP Spoofing Works
An attacker aims to intercept traffic between two devices, usually a Victim PC and the Default Gateway (Router).
1.  The attacker sends a forged Gratuitous ARP message to the Victim PC stating: *"I am the Router (IP: 192.168.1.1), and my MAC is [Attacker's MAC]."*
2.  The Victim PC blindly updates its ARP cache. Now, any packet the Victim intends for the internet is sent physically to the Attacker's machine.
3.  Simultaneously, the attacker sends a forged ARP message to the Router stating: *"I am the Victim PC (IP: 192.168.1.50), and my MAC is [Attacker's MAC]."*
4.  The Router updates its ARP cache. Now, incoming internet traffic meant for the Victim is sent physically to the Attacker.

### Visualizing the ARP Spoofing Attack (ASCII Diagram)

```text
+---------------------------------------------------------------------------------+
|                       ARP SPOOFING (MAN-IN-THE-MIDDLE)                          |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [NORMAL TRAFFIC FLOW]                                                          |
|                                                                                 |
|  [Victim PC]  <================= (Direct L2 Comm) ===============>  [Router]    |
|  192.168.1.50                                                    192.168.1.1    |
|  MAC: AA:AA:AA                                                   MAC: RR:RR:RR  |
|                                                                                 |
|  Victim ARP Cache: 192.168.1.1 -> RR:RR:RR                                      |
|  Router ARP Cache: 192.168.1.50 -> AA:AA:AA                                     |
|                                                                                 |
|---------------------------------------------------------------------------------|
|                                                                                 |
|  [POISONED TRAFFIC FLOW]                                                        |
|                                                                                 |
|                  Attacker sends fake ARP to Victim:                             |
|                  "192.168.1.1 is at XX:XX:XX"                                   |
|                                     |                                           |
|  [Victim PC]                        |                             [Router]      |
|  192.168.1.50                       v                            192.168.1.1    |
|  MAC: AA:AA:AA                [Attacker PC]                      MAC: RR:RR:RR  |
|                               192.168.1.100                                     |
|                               MAC: XX:XX:XX                                     |
|                                     ^                                           |
|                  Attacker sends fake ARP to Router:                             |
|                  "192.168.1.50 is at XX:XX:XX"                                  |
|                                                                                 |
|                                                                                 |
|  NEW Victim ARP Cache: 192.168.1.1 -> XX:XX:XX   (Traffic goes to attacker)     |
|  NEW Router ARP Cache: 192.168.1.50 -> XX:XX:XX  (Traffic goes to attacker)     |
|                                                                                 |
|  Result: Victim ---> Attacker (Sniffs/Modifies) ---> Router ---> Internet       |
+---------------------------------------------------------------------------------+
```

## 5. Exploitation Impacts

Once an attacker has successfully poisoned the ARP caches and established a Man-in-the-Middle (MitM) position, they can execute several devastating attacks:

*   **Packet Sniffing / Eavesdropping:** Using tools like Wireshark or tcpdump, the attacker captures all unencrypted traffic (HTTP, FTP, Telnet), easily extracting plaintext passwords and session cookies.
*   **Traffic Manipulation / Injecting:** The attacker can alter data on the fly. For example, injecting malicious JavaScript hooks (e.g., using BeEF) into unencrypted web pages the victim visits.
*   **SSL/TLS Stripping:** Even if the victim attempts to visit an HTTPS site, the attacker can intercept the request, connect to the server securely themselves, but serve the victim a plaintext HTTP version of the site, capturing the login credentials.
*   **Denial of Service (DoS):** If the attacker poisons the ARP cache but does *not* enable IP forwarding on their own machine, all traffic from the victim simply drops into a black hole, instantly severing their network connection.

## 6. VAPT Tools for ARP Manipulation

During internal network penetration tests, several tools are used to execute these attacks:
*   **`arpspoof` (part of dsniff suite):** A classic, simple command-line tool to send forged ARP replies.
*   **Ettercap / Bettercap:** Comprehensive MitM frameworks that handle the ARP poisoning, packet forwarding, and automated credential sniffing/injection simultaneously.
*   **Responder:** While primarily used for LLMNR/NBT-NS poisoning, Responder leverages network broadcast mechanics conceptually similar to ARP to capture NTLM hashes.

## 7. Defense Mechanisms

Mitigating ARP spoofing requires intelligent network infrastructure; host-based defenses are generally insufficient.
*   **Dynamic ARP Inspection (DAI):** A Cisco switch security feature. The switch inspects all ARP packets. It uses a "DHCP Snooping Binding Database" to verify that the MAC address sending the ARP reply actually matches the IP address assigned to that physical port by the DHCP server. Invalid ARP packets are dropped.
*   **Static ARP Entries:** Manually configuring the ARP table on critical servers so they never update dynamically. Highly secure, but an administrative nightmare to maintain at scale.
*   **Network Segregation / VLANs:** ARP is a Layer 2 broadcast protocol. It cannot cross router boundaries. Segmenting the network into smaller VLANs limits the blast radius of an ARP spoofing attack.
*   **Encryption (Defense in Depth):** While it doesn't stop the MitM routing, enforcing end-to-end encryption (HTTPS, IPsec, SSH) ensures that even if an attacker intercepts the traffic via ARP spoofing, they cannot read or alter the contents.

## 8. Summary

ARP is the glue that binds the physical network to the logical network. Its implicit trust model is one of the most consistently exploitable vulnerabilities in internal enterprise networks. For a penetration tester, mastering ARP spoofing is the gateway to local network dominance.

---
## Chaining Opportunities
*   ARP operates exactly at the boundary of Layer 2 and Layer 3. Revisit [[01 - OSI Model and TCP IP Protocol Suite]] to review this encapsulation boundary.
*   Understanding how switches handle MAC addresses and Broadcasts is essential for executing ARP attacks without taking down the network. See [[03 - Introduction to Routing and Switching]].
*   Once you have a MitM position via ARP, you will intercept Transport layer protocols. Refresh your knowledge of these in [[04 - Understanding TCP UDP and ICMP]].

## Related Notes
*   [[01 - OSI Model and TCP IP Protocol Suite]]
*   [[02 - IP Addressing Subnetting and CIDR Notation]]
*   [[03 - Introduction to Routing and Switching]]
