---
tags: [dns, axfr, cache-poisoning, spoofing, network]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.06 DNS"
---

# DNS — Zone Transfer (AXFR), Cache Poisoning, Spoofing

## 1. Introduction to Domain Name System (DNS)
The Domain Name System (DNS) is the phonebook of the Internet (RFC 1034/1035). It translates human-readable domain names (like `www.example.com`) into the machine-readable IP addresses (like `192.168.1.100`) required for network routing.

DNS is a critical, hierarchically distributed database. It primarily operates over **UDP Port 53** for standard queries and **TCP Port 53** for large responses and zone transfers. 

Because virtually every internet-connected service relies on DNS to function, compromising DNS infrastructure gives an attacker profound control over traffic routing, allowing for devastating Man-in-the-Middle attacks, phishing campaigns, and denial-of-service.

### 1.1 The DNS Hierarchy and Record Types
DNS operates in a tree structure:
1. **Root Servers (.)**: Direct queries to Top-Level Domain (TLD) servers.
2. **TLD Servers (.com, .org, .net)**: Direct queries to Authoritative Name Servers.
3. **Authoritative Servers**: Hold the actual, final DNS records for a specific domain (e.g., `ns1.example.com`).

**Crucial Record Types:**
- **A Record:** Maps a hostname to an IPv4 address.
- **AAAA Record:** Maps a hostname to an IPv6 address.
- **CNAME:** An alias mapping one hostname to another.
- **MX:** Mail Exchange record; dictates where email for the domain should be routed.
- **NS:** Name Server record; delegates a subdomain to another DNS server.
- **TXT:** Text records, heavily used for security verifications like SPF, DKIM, and DMARC.

## 2. ASCII Diagram: DNS Cache Poisoning Architecture

```text
    [Victim Client]
           | (1) "What is the IP of bank.com?"
           V
    [Local DNS Resolver (ISP/Corporate)] <-------[Attacker]
           |                                       |
           | (2) Forwards query to                 | (4) Attacker floods the Resolver
           |     Authoritative Server              |     with forged responses:
           V                                       |     "bank.com is 10.10.10.99!"
    [Authoritative Server for bank.com]            |     (Guessing the TXID)
           |                                       |
           | (3) Legitimate response:              |
           |     "bank.com is 203.0.113.5"         |
           V                                       V
      If the Attacker's forged response arrives FIRST and 
      matches the Transaction ID, the Resolver caches the fake IP.

      Result: ALL users querying that Resolver are secretly routed to the Attacker's fake bank site.
```

## 3. Zone Transfer (AXFR / IXFR) Attacks
A Zone Transfer is a legitimate administrative function used to replicate DNS databases across a set of DNS servers (usually from a Primary to a Secondary server for redundancy).

**The Mechanics:**
The command `AXFR` requests a complete transfer of all records in the zone. `IXFR` requests only the incremental changes. Because these responses are large, they occur over **TCP Port 53**.

**The Vulnerability:**
By default, early DNS servers (like older versions of BIND) did not restrict who could request a zone transfer. If an administrator fails to restrict `AXFR` requests strictly to the IP addresses of trusted secondary servers, *anyone* on the internet can ask for the entire domain database.

**The Risk:**
A successful zone transfer is an intelligence goldmine. It instantly reveals the entire internal and external network topology of the target organization. An attacker gains a complete list of all subdomains, staging servers, internal IP addresses, mail servers, and text records, massively accelerating the reconnaissance phase.

**Exploitation via Dig:**
```bash
dig axfr @ns1.example.com example.com
```

**Exploitation via Host:**
```bash
host -l example.com ns1.example.com
```
If successful, the output will dump hundreds or thousands of lines detailing every host within `example.com`.

## 4. DNS Cache Poisoning (DNS Spoofing)
Cache Poisoning is one of the most dangerous network attacks. It corrupts the cache of a DNS resolver, forcing it to return a fraudulent IP address for a legitimate domain.

**The Mechanics:**
When a recursive DNS resolver (like your ISP's DNS or Google's 8.8.8.8) receives a query it doesn't know, it asks the authoritative server. It uses a 16-bit Transaction ID (TXID) to track the request.
If an attacker can send a forged response to the resolver *before* the legitimate authoritative server responds, and the attacker correctly guesses the 16-bit TXID, the resolver accepts the forged response and caches it.

### 4.1 The Kaminsky Bug (2008)
Dan Kaminsky discovered a catastrophic flaw in DNS caching. Previously, attackers struggled to poison a cache because the resolver would only cache the answer for the exact query requested. If the cache was already populated with the real IP, the attacker had to wait for the TTL (Time to Live) to expire.
Kaminsky realized an attacker could query random, non-existent subdomains (e.g., `1.bank.com`, `2.bank.com`). The resolver *must* fetch these. The attacker then floods forged responses that not only answer the bogus query but also include a poisoned "Additional Section" redefining the authoritative Name Server (`NS` record) for the *entire* `bank.com` domain.
This allowed attackers to completely hijack entire top-level domains at the resolver level instantly.

## 5. Local DNS Spoofing (MITM)
On a Local Area Network (LAN), attackers don't need complex Kaminsky attacks; they can simply intercept traffic directly.

**The Mechanics:**
Using ARP Spoofing to become the Man-in-the-Middle, an attacker intercepts all DNS queries originating from the victim machine. The attacker's tool drops the legitimate query and immediately replies with a forged IP address pointing to the attacker's server.

**Exploitation via Ettercap / Bettercap / DNSChef:**
Attackers configure tools like `dnschef` to act as a rogue DNS server:
```bash
dnschef --fakeip 192.168.1.50 --fakedomains *.microsoft.com,*.google.com
```
All traffic destined for Microsoft or Google from the victim will be silently redirected to the attacker's IP (`192.168.1.50`).

## 6. DNS Amplification (DDoS)
DNS is heavily abused to launch Distributed Denial of Service (DDoS) attacks due to its use of the connectionless UDP protocol.

**The Mechanics:**
Because UDP does not require a handshake, an attacker can easily spoof the source IP address of a DNS request.
The attacker sends a small DNS query (e.g., requesting the `ANY` record for a large domain) to thousands of open, public DNS resolvers on the internet. Crucially, they spoof the source IP to be the *victim's* IP address.
The DNS resolvers process the request and send the massively amplified responses (often 50x larger than the request) directly to the victim. The victim's network is instantly overwhelmed by a tsunami of unsolicited DNS traffic.

## 7. Defensive Strategies & Mitigation

### 7.1 Securing Zone Transfers
- **Restrict AXFR/IXFR:** Configure the DNS server (e.g., in BIND's `named.conf`) to explicitly reject zone transfers from unauthorized IPs.
  ```text
  allow-transfer { 192.168.1.10; 192.168.1.11; }; // Only secondary servers
  ```
- **TSIG (Transaction Signature):** Use cryptographic keys to authenticate zone transfer requests between primary and secondary servers.

### 7.2 Defending Against Cache Poisoning
- **Source Port Randomization:** Modern DNS servers randomize both the 16-bit TXID *and* the UDP source port when making outbound recursive queries. This increases the entropy the attacker must guess from 65,536 to over 4 billion, rendering traditional cache poisoning statistically impossible.
- **DNSSEC (DNS Security Extensions):** The ultimate solution. DNSSEC cryptographically signs DNS records. Resolvers validate the digital signature against the domain's public key. Even if an attacker perfectly spoofs a response, they cannot forge the cryptographic signature, and the resolver will reject the poisoned data.

### 7.3 Network Defenses
- **Egress Filtering:** Prevent DNS amplification attacks by implementing BCP38 (Network Ingress Filtering) at the ISP level to drop packets with spoofed source IP addresses.
- **Block External DNS:** Corporate firewalls should forcefully redirect or block all outbound Port 53 traffic, forcing all internal clients to use the monitored corporate DNS resolvers.

## 8. Chaining Opportunities
- **AXFR to Virtual Host Routing:** Use a successful zone transfer to discover hidden staging environments (e.g., `dev-staging-v3.company.local`). Modify your local `/etc/hosts` file to reach these poorly secured internal web apps. -> [[01 - Web Application Reconnaissance]]
- **Local DNS Spoofing to Phishing:** Use ARP spoofing and `dnschef` to redirect the company's intranet portal (`intranet.corp`) to a pixel-perfect clone hosted on the attacker's machine, harvesting Active Directory credentials. -> [[15 - Social Engineering]]
- **DNS Exfiltration:** When exploiting a highly locked-down server with no outbound internet access, encode stolen data into DNS TXT queries (e.g., `base64data.attacker-domain.com`). The internal DNS server will recursively fetch it, bypassing firewall rules. -> [[20 - Command and Control (C2)]]

## 9. Related Notes
- [[02 - Man-in-the-Middle Attacks]]
- [[07 - DHCP — Starvation, Rogue DHCP Server]]
- [[01 - Information Gathering]]
- [[20 - Command and Control (C2)]]

---
*End of Note*
