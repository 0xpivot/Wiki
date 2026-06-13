---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 43"
---

# Network QnA - Module 43 - ARP Spoofing and MITM

```text
       ARP Spoofing Man-In-The-Middle (MITM) Architecture
+------------------+                   +------------------+
|   Target Host    |                   |  Default Gateway |
|   IP: 10.0.0.5   |                   |  IP: 10.0.0.1    |
| MAC: AA:AA:AA:AA |                   | MAC: GG:GG:GG:GG |
+--------+---------+                   +--------+---------+
         |                                      |
         |    [Poisoned ARP Cache]              |    [Poisoned ARP Cache]
         |    10.0.0.1 -> MM:MM:MM:MM           |    10.0.0.5 -> MM:MM:MM:MM
         |                                      |
         +-----------------+  +-----------------+
                           |  |
                 +---------+--+---------+
                 |    Attacker Node     |
                 |    IP: 10.0.0.99     |
                 | MAC: MM:MM:MM:MM     |
                 | (IP Forwarding ON)   |
                 +----------------------+
```

## Formal Technical Questions

**Q1: Explain the fundamental vulnerability in the Address Resolution Protocol (ARP) that makes ARP Cache Poisoning possible.**
**Answer:**
ARP is a stateless and completely unauthenticated protocol designed to map Layer 3 IP addresses to Layer 2 MAC addresses. 
The vulnerabilities stem from two core behaviors:
1. **Lack of Authentication:** Any host on the local network can claim to have any IP address. When a host receives an ARP Reply, it blindly trusts the sender and updates its ARP cache.
2. **Stateless Nature:** A host will accept and process an ARP Reply even if it never sent an initial ARP Request. 
An attacker abuses this by sending unsolicited (Gratuitous) ARP Replies to a target host, claiming that the attacker's MAC address is associated with the Default Gateway's IP address. Simultaneously, the attacker sends an ARP Reply to the Gateway claiming their MAC is the target's IP. This places the attacker in the middle of the traffic flow.

**Q2: What is a Gratuitous ARP? How is it used legitimately, and how is it weaponized?**
**Answer:**
A Gratuitous ARP is an ARP broadcast where the Source and Destination IP addresses are the same. It is an unsolicited announcement of a host's IP-to-MAC mapping.
- **Legitimate Use:** It is used for Duplicate IP Address Detection (DAD) when a device boots up or changes IPs, and for High Availability (HA) failover (e.g., when a backup firewall takes over a virtual IP, it sends a Gratuitous ARP to update the switches' CAM tables).
- **Weaponization:** Attackers broadcast Gratuitous ARPs to update the ARP caches of *all* machines on the subnet simultaneously, pointing a critical IP (like the Gateway or an internal DNS server) to the attacker's MAC address, establishing a subnet-wide MITM position instantly.

**Q3: In the context of IPv6, ARP is replaced by the Neighbor Discovery Protocol (NDP). Can NDP be spoofed similarly to ARP?**
**Answer:**
Yes. IPv6 uses NDP, which operates over ICMPv6, to perform address resolution (replacing ARP) and Router Discovery.
- **NDP Spoofing:** Attackers can forge ICMPv6 Neighbor Advertisement (NA) messages to poison the neighbor cache of target hosts, achieving the exact same MITM result as ARP spoofing.
- **SLAAC/Router Advertisement (RA) Spoofing:** An attacker can broadcast rogue ICMPv6 Router Advertisements, claiming to be the default IPv6 router. Since IPv6 prioritizes SLAAC (Stateless Address Autoconfiguration), target hosts will auto-configure an IPv6 address and route all their IPv6 traffic through the attacker, completely bypassing IPv4 security controls and firewalls.

## Scenario-Based Questions

**Q4: You have successfully established an ARP spoofing MITM position against a corporate workstation. However, the target is browsing a secure intranet site using HTTPS, and HSTS (HTTP Strict Transport Security) is enforced. How do you attempt to intercept the plaintext credentials?**
**Answer:**
HSTS prevents browsers from accepting invalid certificates or downgrading to plaintext HTTP. Standard SSL Stripping will fail.
To bypass this, I would employ **DNS Spoofing combined with an Homograph Attack / Proxying**.
1. **DNS Interception:** Since I control the traffic, I intercept the DNS request for `secure.intranet.local`.
2. **Homograph/Subdomain Spoofing:** I reply to the DNS request with the IP of my attacker machine, but I must bypass the HSTS domain rule. I cannot serve a fake cert for `secure.intranet.local`. Instead, using a tool like `evilginx2` or `bettercap`, I redirect the victim's initial HTTP request (before HSTS kicks in, if I can force a link click via a phishing payload, or if I spoof a captive portal) to a look-alike domain, e.g., `secure.intranet-login.local`.
3. **Reverse Proxying:** I serve a valid TLS certificate for my look-alike domain. The target enters their credentials. My proxy forwards the credentials to the real `secure.intranet.local`, captures the session cookies, and passes the response back to the victim.

**Q5: During an engagement, you establish a MITM position via ARP poisoning. You notice heavy SMB (Server Message Block) traffic. You want to relay NTLM authentication to compromise a target server. What specific conditions must be met for SMB Relay to succeed?**
**Answer:**
For an NTLM Relay attack via SMB to be successful, several conditions are required:
1. **SMB Signing Disabled:** The target server (the one I am relaying *to*) must not require SMB signing. If SMB signing is enforced, the relay will fail because the attacker cannot sign the modified packets without the user's password hash.
2. **Privileged Context:** The user whose traffic I am intercepting and relaying must have administrative privileges on the target server.
3. **No Cross-Protocol Mitigation:** If relaying from SMB to SMB, protections like EPA (Extended Protection for Authentication) and SPN (Service Principal Name) target name validation must be absent or bypassable.
4. **Execution:** I use `ntlmrelayx.py`. I intercept the SMB connection from the victim, forward the NTLM negotiate/challenge/authenticate messages to the target server, and execute arbitrary commands (e.g., dumping SAM hashes) upon successful authentication.

## Deep-Dive Defensive Questions

**Q6: Explain how Dynamic ARP Inspection (DAI) prevents ARP spoofing at the switch level. What dependencies does DAI have?**
**Answer:**
DAI is a security feature on network switches that validates ARP packets on untrusted ports.
- **Mechanism:** When an ARP packet arrives on an untrusted port, DAI intercepts it. It checks the IP-to-MAC mapping in the packet against a trusted database. If the mapping is invalid, the switch drops the packet and logs an alert.
- **Dependencies:** DAI critically depends on **DHCP Snooping**. The trusted database DAI uses is the DHCP Snooping Binding Database, which dynamically maps IPs, MACs, and ports when clients receive DHCP leases.
- **Static Hosts:** For hosts with static IPs (which don't use DHCP), network administrators must manually configure static ARP ACLs in the switch, otherwise DAI will drop their legitimate ARP traffic.

**Q7: Can IPsec be used to mitigate ARP spoofing? Explain your reasoning.**
**Answer:**
Yes, IPsec mitigates the *impact* of ARP spoofing, even though it does not prevent the ARP cache poisoning itself.
- **Reasoning:** If IPsec (specifically in Transport Mode with ESP) is enforced for internal network communication, all traffic between hosts is mutually authenticated and encrypted.
- **Outcome:** An attacker can still poison the ARP cache and force the encrypted IPsec packets to route through their MAC address. However, because the attacker lacks the IPsec cryptographic keys, they cannot decrypt, read, or modify the payload. Any tampering will invalidate the integrity checks, causing the packets to be dropped. Thus, the MITM attack degrades into a mere Denial of Service or passive traffic flow analysis, preserving confidentiality and integrity.

## Real-World Attack Scenario

**Scenario: Complete Domain Compromise via IPv6 NDP Spoofing and NTLM Relay**
A Red Team operates in a mature Windows environment. The network has strict IPv4 security: static ARP, DHCP Snooping, and DAI are enforced. IPv6 is disabled on the network switches but left at default (enabled) on Windows workstations.
1. **The Flaw:** Windows machines prefer IPv6 over IPv4. If an IPv6 router is present, they will route traffic through it.
2. **Exploitation:** The attacker runs `mitm6`, broadcasting ICMPv6 Router Advertisements.
3. **Takeover:** All Windows workstations on the subnet automatically assign themselves an IPv6 address and set the attacker's machine as their IPv6 default gateway. IPv4 security controls are completely bypassed.
4. **DNS Spoofing:** When a workstation attempts to resolve an internal resource (e.g., WPAD for proxy auto-discovery), the request goes to the attacker via IPv6. The attacker replies with their own IPv6 address.
5. **Relay:** The victim machine connects to the attacker via SMB/HTTP over IPv6 and attempts to authenticate using NTLM.
6. **Compromise:** The attacker uses `ntlmrelayx` to relay this authentication to the Primary Domain Controller over LDAPS (Lightweight Directory Access Protocol Secure) to create a new Domain Admin account or grant DCSync privileges to their own computer account, completely compromising the Active Directory domain.

## Chaining Opportunities
- **Active Directory Exploitation:** ARP/NDP spoofing is the primary vehicle for capturing NetNTLM hashes to be used in Pass-the-Hash, NTLM Relaying, and Kerberos manipulation.
- **Web Exploitation:** MITM positions allow attackers to inject malicious JavaScript frameworks (like BeEF) directly into unencrypted HTTP traffic of targeted users.
- **Physical Security:** Plugging a rogue drop-box into a conference room port often immediately leads to an automated ARP spoofing campaign.

## Related Notes
- [[07 - NTLM Relaying and Active Directory Certificate Services]]
- [[19 - IPv6 Security Implications and Migration Risks]]
- [[34 - Mitigating MITM with 802.1X and NAC]]
- [[42 - VLAN Hopping and Layer 2 Attacks]]
- [[61 - SSL/TLS Interception in Enterprise Proxies]]
