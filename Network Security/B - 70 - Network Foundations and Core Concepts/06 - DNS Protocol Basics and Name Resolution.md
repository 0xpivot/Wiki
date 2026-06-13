---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.06 DNS Protocol Basics and Name Resolution"
---

# DNS Protocol Basics and Name Resolution

## 1. Overview and Introduction
The Domain Name System (DNS) is one of the most critical foundational protocols of the modern Internet. Operating primarily over UDP port 53 (and TCP port 53 for specific use cases), DNS serves as the hierarchical, decentralized naming system that translates human-readable domain names (such as `www.example.com`) into the numerical IP addresses (such as `192.0.2.1` or `2001:db8::1`) required for routing packets across networks.

Without DNS, users would be required to memorize IP addresses for every service they wish to access. Furthermore, DNS provides abstraction, allowing administrators to change the underlying IP address of a service without affecting how end-users access it.

## 2. The Domain Namespace Hierarchy
The DNS namespace is organized as an inverted tree.
* **Root Domain (`.`):** The top of the hierarchy, managed by IANA/ICANN. There are 13 logical root server clusters globally (named A through M).
* **Top-Level Domains (TLDs):** The level immediately below the root, such as `.com`, `.org`, `.net`, and country-code TLDs like `.uk` or `.jp`.
* **Second-Level Domains (SLDs):** Domains directly registered by organizations or individuals, such as `example.com` or `google.com`.
* **Subdomains:** Further divisions within a second-level domain, such as `www.example.com` or `mail.internal.example.com`.

## 3. The DNS Resolution Process
DNS resolution typically involves two distinct types of queries: Recursive and Iterative.

### Recursive Queries
When a client (stub resolver) asks its configured Local DNS Server for an IP address, it typically sets the "Recursion Desired" (RD) bit. This tells the server, "Please find the complete answer for me and return the final IP address or an error."

### Iterative Queries
When the Local DNS Server does not have the answer in its cache, it must perform the legwork. It sends iterative queries to authoritative servers.
1. **Query to Root:** The local server asks a Root server for `www.example.com`. The Root server replies with a referral to the `.com` TLD servers.
2. **Query to TLD:** The local server asks the `.com` TLD server. The TLD server replies with a referral to the authoritative name servers for `example.com`.
3. **Query to Authoritative:** The local server asks the authoritative server for `www.example.com`. The authoritative server returns the actual A record (IP address).
4. **Caching:** The local server caches the response and returns it to the client.

## 4. DNS Record Types Explained
DNS holds various types of resource records (RRs).
* **A (Address):** Maps a hostname to a 32-bit IPv4 address.
* **AAAA (Quad-A):** Maps a hostname to a 128-bit IPv6 address.
* **CNAME (Canonical Name):** Aliases one name to another. If `www.example.com` is a CNAME to `example.com`, the resolver will restart the lookup for `example.com`.
* **MX (Mail Exchange):** Specifies the mail servers responsible for accepting email on behalf of the domain, along with a priority value.
* **NS (Name Server):** Delegates a DNS zone to use the specified authoritative name servers.
* **TXT (Text):** Holds arbitrary text data. Extensively used for email security verification (SPF, DKIM, DMARC) and domain ownership validation.
* **PTR (Pointer):** Used for Reverse DNS lookups. Maps an IP address back to a hostname using the `in-addr.arpa` or `ip6.arpa` domains.
* **SOA (Start of Authority):** Contains administrative information about the zone, including the primary name server, the email of the domain administrator, the zone serial number, and timers (Refresh, Retry, Expire, TTL).
* **SRV (Service):** Specifies the location (hostname and port number) of servers for specific services (e.g., Active Directory LDAP, SIP, XMPP).

## 5. DNS Packet Header and Message Format
DNS messages are encapsulated in UDP or TCP segments. A DNS message consists of five main sections:

1. **Header:** 12 bytes long. Contains:
   * **Transaction ID (16 bits):** Used to match responses to requests.
   * **Flags (16 bits):** Includes QR (Query/Response), Opcode, AA (Authoritative Answer), TC (Truncated), RD (Recursion Desired), RA (Recursion Available), Z (Reserved), and RCODE (Response Code: 0=NoError, 3=NXDomain, etc.).
   * **QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT (16 bits each):** The number of entries in the Question, Answer, Authority, and Additional sections, respectively.
2. **Question Section:** Contains the domain name being queried, the query type (e.g., A, MX), and the query class (usually IN for Internet).
3. **Answer Section:** Contains the resource records that answer the question.
4. **Authority Section:** Contains NS records pointing toward an authoritative name server.
5. **Additional Section:** Contains resource records that relate to the query but are not strictly answers to the question (e.g., the A records for the servers mentioned in the Authority section).

## 6. Transport Layer: UDP vs TCP Port 53
* **UDP Port 53:** The default transport for standard DNS queries. It is fast and stateless. However, UDP is limited to 512 bytes for DNS responses (unless EDNS0 is supported).
* **TCP Port 53:** Used in specific scenarios:
  * **Zone Transfers (AXFR/IXFR):** Replicating an entire DNS zone database between master and slave authoritative servers requires reliable transport.
  * **Large Responses:** If a DNS response exceeds the UDP payload limit, the server sets the TC (Truncated) bit in the header. The client must then retry the query over TCP to receive the full response.

## 7. DNS Security Mechanisms
Traditional DNS is unencrypted and lacks authentication, making it vulnerable to interception and spoofing.
* **DNSSEC (DNS Security Extensions):** Adds cryptographic signatures to existing DNS records. This provides data origin authentication and data integrity, preventing cache poisoning. It does not provide confidentiality (encryption).
* **DoT (DNS over TLS):** Encrypts standard DNS queries using a TLS tunnel (typically over TCP port 853), providing privacy and preventing eavesdropping.
* **DoH (DNS over HTTPS):** Encapsulates DNS queries within HTTP/2 and HTTPS traffic (TCP port 443). This bypasses traditional DNS port blocking and blends DNS traffic with regular web browsing.

## 8. Common DNS Attack Vectors
As a foundational protocol, DNS is a prime target for attackers.

* **DNS Cache Poisoning / Spoofing:** An attacker sends forged DNS responses to a recursive resolver, attempting to guess the Transaction ID and source port. If successful before the legitimate authoritative server replies, the resolver caches the malicious IP address, redirecting all subsequent clients to an attacker-controlled server.
* **DNS Amplification (DDoS):** An attacker sends a small DNS query (e.g., requesting `ANY` records) to an open recursive resolver using a spoofed source IP address belonging to the victim. The resolver sends a massive response (amplification factor can be 50x or more) to the victim, overwhelming their bandwidth.
* **Zone Transfers (AXFR) Information Disclosure:** If a DNS server is misconfigured to allow zone transfers from any IP address, an attacker can download the entire zone file. This reveals internal subdomains, server IP addresses, and the network topology.
* **DNS Rebinding:** An attack against web browsers where a malicious website rapidly changes the IP address of its domain name from a public IP to an internal, private IP (e.g., `127.0.0.1`). This bypasses the Same-Origin Policy (SOP), allowing the attacker's JavaScript to interact with internal services.
* **Typosquatting and IDN Homograph Attacks:** Registering domains that look visually identical to legitimate domains (e.g., replacing a Latin 'a' with a Cyrillic 'а') to deceive users during phishing campaigns.

## 9. ASCII Diagram: DNS Resolution and Cache Poisoning

```text
Normal Iterative Resolution:

      [Client]
         | (1) Recursive Query for www.example.com
         v
  [Local DNS Resolver]
         |
         | (2) Iterative Query to Root
         +---------------------------------> [Root Server]
         | <-------------------------------- (3) Refers to .com TLD
         |
         | (4) Iterative Query to TLD
         +---------------------------------> [.com TLD Server]
         | <-------------------------------- (5) Refers to Authoritative
         |
         | (6) Iterative Query to Auth
         +---------------------------------> [Authoritative Server]
         | <-------------------------------- (7) Returns Legitimate IP
         v
    Returns IP to Client

========================================================================
DNS Cache Poisoning Attack Flow:

      [Attacker]                              [Local DNS Resolver]
         |                                           |
         | (1) Query for random.example.com -------->|
         |     (Forces resolver to ask Auth server)  |
         |                                           |
         |                                           |---- (2) Query Auth ---> [Authoritative]
         |                                           |
         | (3) Flood forged responses <--------------|
         |     Guessing TXID and Source Port         |
         |     Payload: www.example.com = Evil IP    |
         |                                           |
         | (4) If TXID matches before Auth responds, |
         v     the cache is poisoned!                |
                                                     | <== (5) Legit Response arrives late
                                                           and is dropped.
```

## 10. Chaining Opportunities
* **Subdomain Enumeration to Application Exploitation:** Using tools like `Amass` or `Sublist3r` to find forgotten development subdomains (via DNS), leading to the discovery of vulnerable applications or exposed administrative interfaces.
* **AXFR to Active Directory Targeting:** A successful zone transfer against an internal DNS server can reveal the exact IP addresses of Domain Controllers (`_kerberos._tcp.dc._msdcs`), Exchange servers, and sensitive internal portals, perfectly mapping the network for lateral movement.
* **DNS Rebinding to SSRF:** Using a short TTL and DNS rebinding to bypass Server-Side Request Forgery (SSRF) protections. The initial validation resolves to a safe IP, but the subsequent fetch by the application resolves to `169.254.169.254` (AWS Metadata) or an internal database.

## 11. Related Notes
* [[07 - DHCP Protocol Basics and Address Allocation]]
* [[08 - HTTP HTTPS and TLS Handshake Explained]]
* [[01 - IP Addressing and Subnetting]]
