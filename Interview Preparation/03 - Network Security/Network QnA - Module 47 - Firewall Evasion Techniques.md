---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 47"
---

# Network QnA - Module 47: Firewall Evasion Techniques

This document explores highly advanced techniques used to bypass stateful and stateless firewalls. It covers packet manipulation, fragmentation, and low-level protocol abuses.

## Formal Technical Questions

**Q1: Explain how IP fragmentation works and detail how the "Tiny Fragment" attack (CVE-1999-0157) bypasses stateless packet-filtering firewalls.**
*Answer:*
IP fragmentation occurs when a packet exceeds the MTU (Maximum Transmission Unit) of a network link. The sender breaks the payload into smaller chunks, giving each an IP header, a Fragment Offset, and setting the MF (More Fragments) flag on all but the last piece.
*   **The Attack:** Stateless firewalls (like early ACLs) make decisions by reading the TCP/UDP headers (Ports, Flags) located in the first IP fragment (Offset 0). If an attacker crafts an initial fragment so small (e.g., 8 bytes of payload) that it only contains the first half of the TCP header, the crucial information (like the destination port) is pushed into the *second* fragment.
*   **The Bypass:** The firewall inspects Fragment 1, sees no port rule violation, and passes it. It inspects Fragment 2, sees it has an offset > 0, assumes it's a valid continuation of Fragment 1, and passes it without checking ports. The destination host reassembles the fragments, resulting in a malicious connection to a filtered port. Modern firewalls mitigate this by requiring minimum fragment sizes or dropping fragments with offsets pointing into the transport header.

**Q2: Describe the TCP ACK scan (`nmap -sA`). What exactly does it determine, and why does it not determine if a port is "open"?**
*Answer:*
The TCP ACK scan sends a packet with only the ACK flag set.
*   **Mechanism:** According to RFC 793, if a host receives an unsolicited ACK packet, it must respond with an RST (Reset) packet, regardless of whether the port is open or closed.
*   **Purpose:** The scan maps firewall rule sets. It determines whether a firewall is stateful or stateless, and which ports are filtered.
    *   *Unfiltered:* If an RST is received, the port is marked "unfiltered". The firewall allowed the ACK packet to pass, and the target responded. We don't know if the port is open or closed, only that the firewall didn't block it.
    *   *Filtered:* If no response is received (or an ICMP unreachable), the packet was dropped by the firewall. The port is marked "filtered".
*   **Evasion Aspect:** By mapping unfiltered ports, an attacker can determine which ports can be used for secondary attacks, such as TCP Window scanning, or for establishing reverse shells that traverse the firewall without being dropped by stateful tracking.

**Q3: How does source routing evasion work at the network layer, and how do modern network stacks defend against it?**
*Answer:*
IP Strict Source Routing (SSR) and Loose Source Routing (LSR) are IP options that allow the sender to specify the exact path (a list of IP addresses) a packet must take through the network.
*   **The Exploit:** An attacker can craft a packet with a spoofed internal source IP address, but use source routing to instruct the network to route the return traffic back to the attacker's true external IP. This allows an external attacker to spoof trusted internal IPs and bypass firewall rules that allow traffic based on source IP trust.
*   **The Defense:** Modern operating systems and firewalls (e.g., Linux iptables/sysctl `net.ipv4.conf.all.accept_source_route = 0`) disable source routing by default. Firewalls are configured to drop any IP packets containing the LSR or SSR IP options, neutralizing the attack completely.

## Scenario-Based Questions

**Q4: You are performing a Black Box external penetration test. You run `nmap -sS $TARGET` and all ports return as `filtered`. You suspect a strict stateful firewall or IPS is dropping your SYN packets. How do you evade this to accurately map the internal services?**
*Answer:*
If standard SYN scans are dropped, I will systematically test firewall edge cases:
1.  **Decoy Scanning (`-D`):** I will spoof my source IP alongside dozens of decoy IPs (e.g., `nmap -sS -D RND:20 $TARGET`). This overwhelms the IPS alerting mechanism, potentially causing it to fail-open, or masking my true IP.
2.  **Fragmentation (`-f` or `--mtu 8`):** I will fragment the SYN packets to bypass poorly configured deep packet inspection engines.
3.  **Source Port Manipulation (`-g 53` or `-g 80`):** Many legacy firewalls blindly trust traffic originating from ports like UDP 53 (DNS) or TCP 80 (HTTP). By setting my source port to 53, I may bypass the stateless rules.
4.  **Zombie Scanning (`-sI`):** I will find an idle host on the internet with a predictable IP ID sequence and use it to perform a blind TCP Idle Scan. This reflects the scan off the zombie, completely hiding my IP and bypassing IP-based blocking.
5.  **Data Appending (`--data-length 25`):** Some firewalls drop SYN packets that have zero data payload, recognizing them as port scans. Appending random data makes the packet look like a legitimate, malformed connection attempt.

**Q5: During an internal Red Team engagement, you find a highly segmented VLAN. The router between your VLAN and the target VLAN uses strict Access Control Lists (ACLs) but does NOT do stateful tracking. You need to access an internal HTTP server. How do you bypass the ACL?**
*Answer:*
Because the router is stateless (e.g., standard Cisco extended ACLs), it only checks individual packets, not the state of the connection.
*   **ACK Tunneling/Evasion:** A stateless firewall will typically block incoming `SYN` packets to prevent connection establishment, but it *must* allow incoming `ACK` packets, assuming they are part of an already established outbound connection.
*   **The Exploit:** I can use tools like `hping3` or custom Python Scapy scripts to initiate a connection using an `ACK` packet. Alternatively, I can use a proxy tool like `Ptunnel` or set up an `ACK`-based covert channel (like `ackcmd`) if I have an agent on the other side.
*   **Session Splicing/Teardrop:** If I just need to send an exploit payload to the HTTP server, I will craft a packet with the `ACK` flag set, embedding my exploit in the payload. The stateless firewall passes it, and the vulnerable server application might still process the payload even without a full 3-way handshake, depending on the service.

**Q6: You are attempting to exfiltrate data past a Next-Generation Firewall (NGFW) that performs DPI (Deep Packet Inspection) and SSL Decryption. Standard DNS and ICMP exfiltration are immediately blocked. What is your next move?**
*Answer:*
NGFWs with SSL termination break standard C2 channels. I need a protocol that the firewall *cannot* decrypt or *refuses* to decrypt due to business logic.
1.  **Domain Fronting:** I will wrap my C2 traffic in HTTPS and point it to a high-reputation CDN (e.g., Fastly, Cloudflare). The SNI (Server Name Indication) in the TLS handshake points to a legitimate, highly trusted domain (e.g., `update.microsoft.com`), but the encrypted HTTP Host header inside points to my malicious CDN endpoint. The firewall allows it based on the SNI.
2.  **Protocol Smuggling (e.g., HTTP/2 over TLS):** I will establish a legitimate HTTP/2 connection. NGFWs often struggle to parse multiplexed HTTP/2 streams accurately. I can smuggle C2 frames inside long-lived gRPC streams.
3.  **Client Certificate Authentication:** I will host my C2 on an HTTPS server requiring Mutual TLS (mTLS). When the NGFW attempts to MITM the connection, it fails because it does not possess the client certificate. Many NGFWs are configured to "fail-open" or bypass inspection for mTLS connections to prevent breaking legitimate services.

## Deep-Dive Defensive Questions

**Q7: Explain the concept of "Asymmetric Routing" and how it causes problems for stateful firewalls. How do attackers potentially abuse this?**
*Answer:*
Asymmetric routing occurs when packets from host A to host B take a different network path than the return packets from B to A.
*   **The Problem:** A stateful firewall must see both sides of a TCP conversation to accurately track the state (SYN, SYN-ACK, ACK). If a firewall only sees the outbound SYN, but the return SYN-ACK takes a different route, the firewall marks the connection as incomplete. When host A sends the final ACK, the firewall drops it because it violates the state table.
*   **Attacker Abuse:** Attackers can purposefully manipulate routing (e.g., via BGP or ICMP redirects) to force an asymmetric route. If they can route their malicious payload through an interface where the firewall is configured to "fail-open" or bypass state checks due to known asymmetric issues, they bypass deep inspection.

**Q8: Your organization uses `iptables`. A junior admin wrote this rule to block an attacker: `iptables -A INPUT -s 10.10.10.5 -j DROP`. Explain why this rule might be ineffective and how an attacker could bypass it using fragmentation.**
*Answer:*
The rule blocks incoming packets based on the source IP.
*   **The Weakness:** While `iptables` *is* stateful, this specific raw rule applies to the filter table. If an attacker fragments their IP packets, the first fragment contains the IP header (with the blocked IP) and the TCP header. The *subsequent* fragments do NOT contain the TCP/UDP headers.
*   **The Bypass (Overlapping Fragments):** If the kernel's defragmentation logic (conntrack) is bypassed or misconfigured, an attacker could send a tiny first fragment that *spoofs* a trusted IP, passing the rule. The second fragment overwrites the IP header with the actual payload using overlapping fragment offsets.
*   **Correction:** The admin should ensure `netfilter` conntrack is active, which reassembles all fragments *before* passing them to the `INPUT` chain, neutralizing fragmentation attacks entirely.

**Q9: Detail the mechanics of TCP Window manipulation as an evasion technique. How can an IPS be fooled by TTL and Window size discrepancies?**
*Answer:*
This relies on discrepancies between how the IPS reconstructs streams and how the end-host reconstructs streams.
*   **TTL Evasion:** The attacker sends a packet containing a malicious payload with a short TTL (Time to Live) that expires *after* the IPS, but *before* the target host. The IPS inspects the malicious payload, flags it, but passes it. The packet dies in transit. The attacker then sends a benign packet with a long TTL and the *same TCP sequence number*. The host receives it. The IPS, seeing a duplicate sequence number, ignores the second packet. The IPS logged an attack that never hit, while the target receives benign data (or vice versa to sneak a payload in).
*   **Window Evasion:** The attacker intentionally sends packets that exceed the target's advertised TCP Window size. The target OS will silently drop the data outside the window. If the IPS does not track the TCP Window size accurately, it will reconstruct the stream including the out-of-window data, failing to see the true payload the target host actually processed.

## Real-World Attack Scenario

### Attack Flow: The "Overlapping Fragment" Bypass
1.  **The Target:** An organization protects its internal Database server with an inline Intrusion Prevention System (IPS). The IPS blocks any SQL packets containing the string `' OR 1=1 --`.
2.  **The Technique:** The Red Team uses a custom Scapy script to execute an IP Fragment Overlap attack (specifically, the Ptacek/Newsham technique).
3.  **Fragment 1:** The attacker sends an IP fragment containing the SQL query `' O`. This fragment is perfectly benign. The IPS allows it.
4.  **Fragment 2:** The attacker sends a second fragment with the payload `R 1=1 --`. The IPS inspects this fragment. It does not see a full malicious signature, so it allows it.
5.  **Reassembly:** The target database server receives both fragments. Its OS kernel reassembles them based on the fragment offsets. The full string `' OR 1=1 --` is reconstructed in memory and passed to the database application.
6.  **The Breach:** The SQL injection executes successfully, bypassing the multi-million dollar IPS because the IPS failed to maintain a stateful reassembly buffer for fragmented IP packets.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
| IP Fragmentation Overlap Evasion (TCP/IP Reassembly Discrepancy)                  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Attacker]                       [Inline IPS]                       [Target OS]  |
|      |                                 |                                  |       |
|      | 1. Frag 1: Offset 0, Len 8      |                                  |       |
|      | Payload: "GET /mal"             | (Inspects: Clean)                |       |
|      |-------------------------------->|--------------------------------->|       |
|      |                                 |                                  |       |
|      | 2. Frag 2: Offset 4, Len 8      |                                  |       |
|      | Payload: "    ware"             | (Inspects: Clean)                |       |
|      |-------------------------------->|--------------------------------->|       |
|      |                                 |                                  |       |
|      | [IPS View: "GET /mal" + "ware"] |                                  |       |
|      | [IPS Reassembly misses overlap] |                                  |       |
|      |                                 |                                  |       |
|      |                                 | [Target OS Reassembly]           |       |
|      |                                 | Offset 0: G E T   / m a l        |       |
|      |                                 | Offset 4:         w a r e        |       |
|      |                                 | Result:   G E T   w a r e        |       |
|      |                                 | (Bypasses signature!)            |       |
+-----------------------------------------------------------------------------------+
```

## Chaining Opportunities
*   **Evasion -> Protocol Smuggling:** Use fragmentation to map open ports, then use HTTP Request Smuggling over an allowed port (80/443) to bypass WAF logic.
*   **Decoys -> Denial of Service:** Use massive amounts of decoy IP scanning (Spoofing) to fill up the firewall's state table, resulting in a SYN Flood / State Exhaustion DoS attack against the firewall itself.

## Related Notes
*   [[Interview Prep - Network Security]]
*   [[TCP-IP Deep Dive - Headers and Flags]]
*   [[Nmap Advanced Evasion Techniques]]
*   [[Snort and Suricata Rule Writing]]
