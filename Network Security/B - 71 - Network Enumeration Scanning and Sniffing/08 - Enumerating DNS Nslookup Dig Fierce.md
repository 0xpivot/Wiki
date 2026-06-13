---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.08 Enumerating DNS Nslookup Dig Fierce"
---

# Enumerating DNS: Nslookup, Dig, and Fierce

## Introduction to DNS Enumeration
The Domain Name System (DNS) is often referred to as the phonebook of the Internet. Its primary function is to translate human-readable domain names (like `example.com`) into machine-readable IP addresses (like `192.0.2.1`). However, DNS infrastructure holds significantly more information than just IP mappings. It defines mail routing, domain ownership verification, cryptographic keys, and the internal structure of an organization's network.

For a Penetration Tester or Bug Bounty Hunter, DNS enumeration is a critical early phase of reconnaissance (Information Gathering). The goal of DNS enumeration is to map out the target's external (and sometimes internal) attack surface by discovering subdomains, identifying mail servers, locating administrative portals, and understanding the organizational hierarchy. Comprehensive DNS enumeration often reveals forgotten legacy systems, staging environments, and development servers—assets that are typically less secure than production systems. If you can control or poison the DNS process, you control the destination of the target's traffic.

## Understanding DNS Resource Records (RR)
Before using enumeration tools, one must understand the types of data stored in DNS. The fundamental building block of DNS is the Resource Record.
- **A Record (Address):** Maps a hostname to an IPv4 address. The most common record.
- **AAAA Record (Quad-A):** Maps a hostname to an IPv6 address.
- **CNAME (Canonical Name):** An alias that points one domain to another domain (e.g., `www.example.com` points to `example.com`). This is heavily targeted for Subdomain Takeover vulnerabilities.
- **MX (Mail Exchange):** Specifies the mail servers responsible for accepting email on behalf of the domain. Prioritized by a preference value.
- **NS (Name Server):** Identifies the authoritative DNS servers for a zone. These are the servers you query for definitive answers about the domain.
- **TXT (Text):** Used to hold arbitrary text data. Commonly used for SPF (Sender Policy Framework), DKIM, DMARC (email security), and domain ownership verification (e.g., Google site verification). Can also be abused for C2 communication.
- **SOA (Start of Authority):** Contains administrative information about the zone, including the primary name server, the email of the domain administrator, and serial numbers (crucial for tracking changes and managing zone transfers).
- **SRV (Service):** Specifies the location (hostname and port) of servers for specific services, such as Active Directory domain controllers, SIP servers, or XMPP servers.
- **PTR (Pointer):** Used for Reverse DNS lookups (mapping an IP address back to a hostname), primarily functioning in the `in-addr.arpa` domain.

## DNS Zone Transfers (AXFR)
A Zone Transfer (AXFR query) is a mechanism used by DNS servers to synchronize database records across multiple servers (typically from a primary server to secondary/slave servers). If a DNS server is misconfigured, it may allow *any* user on the internet to request a full zone transfer.

**Impact:** A successful zone transfer provides the attacker with a complete dump of all DNS records for that domain. This instantly reveals every subdomain, internal IP addresses mapped to public names, and the entire topological layout of the organization's network. It is considered the "Holy Grail" of DNS enumeration.
While modern DNS servers generally restrict AXFR queries to trusted IP addresses via ACLs, misconfigurations still frequently occur, especially in legacy environments, during migrations, or on secondary nameservers managed by third parties.

## Tool 1: Nslookup (The Legacy Standard)
`nslookup` (Name Server Lookup) is a legacy tool built into almost all operating systems (Windows, Linux, macOS). While largely superseded by `dig` for advanced usage by professionals, its ubiquity makes it extremely important, particularly when operating on compromised Windows hosts where `dig` is unavailable.

### Interactive vs. Non-Interactive Mode
- **Non-Interactive:** Used for quick, single queries directly from the command line.
  `nslookup example.com` (Returns the A record).
  `nslookup -type=mx example.com` (Queries specific record types).
- **Interactive:** Launched simply by typing `nslookup`. You enter a specific prompt (`>`) where you can set configurations and perform multiple lookups sequentially.
  ```text
  > server 8.8.8.8    (Change the DNS server you are querying to Google's Public DNS)
  > set type=any      (Query all available record types)
  > example.com
  > set type=mx
  > example.com
  > exit
  ```

## Tool 2: Dig (Domain Information Groper)
`dig` is the Swiss Army knife of DNS querying in Unix-like environments. It is far more flexible, provides more detailed and highly parsable output, and is the preferred tool for network administrators and penetration testers. It does not have an interactive mode; everything is passed via command-line arguments.

### Basic Syntax
`dig [server] [domain] [type]`
- `server`: The DNS server to query (prefix with `@`, e.g., `@8.8.8.8`). If omitted, it uses the system's default DNS server found in `/etc/resolv.conf`.
- `domain`: The target domain name.
- `type`: The resource record type (A, MX, TXT, ANY, AXFR).

### Common Dig Commands
1. **Basic A Record Lookup:** `dig example.com`
2. **Querying a Specific Nameserver:** `dig @8.8.8.8 example.com`
3. **Querying Specific Record Types:**
   `dig example.com MX`
   `dig example.com TXT`
4. **The "ANY" Query:** Attempts to return all known records for the domain. Note that modern DNS servers often drop or restrict ANY queries due to their use in DDoS amplification attacks via UDP spoofing.
   `dig example.com ANY`
5. **Short Output:** Only print the IP address or data value, highly useful for bash scripting and piping to other tools.
   `dig +short example.com`
6. **Reverse Lookup:** Resolves an IP to a hostname using PTR records.
   `dig -x 192.0.2.1`

### Attempting a Zone Transfer with Dig
To attempt a zone transfer, you first need to identify the authoritative nameservers for the domain.
1. Find the NS records: `dig +short example.com NS`
   (Assume this returns `ns1.example.com` and `ns2.example.com`)
2. Query each nameserver directly requesting an AXFR:
   `dig @ns1.example.com example.com AXFR`
   `dig @ns2.example.com example.com AXFR`
If successful, you will see a massive list of every record in the zone. If it fails, you will typically see `Transfer failed` or `Connection refused`.

## Tool 3: Fierce (DNS Brute-forcing and Enumeration)
When zone transfers fail, the next logical step is Subdomain Brute-forcing. This involves taking a large dictionary (wordlist) of common subdomain names (e.g., `dev`, `test`, `staging`, `vpn`, `admin`, `api`) and querying the DNS server to see if they resolve to valid IP addresses.

`fierce` is a highly effective Perl script (now largely rewritten in Python 3 as `fierce-domain-scanner`) designed specifically for this task. It is important to note that `fierce` is not an IP scanner; it strictly operates over the DNS protocol to find contiguous IP space and hostnames.

### How Fierce Works
1. It queries the DNS servers of the target domain to find the nameservers.
2. It attempts a Zone Transfer (AXFR) against all discovered nameservers.
3. If the zone transfer fails, it falls back to a dictionary-based brute-force attack against the domain.
4. It attempts to find contiguous IP space by looking at the resolved IPs of discovered subdomains, attempting to identify the organization's corporate network blocks, and then performs reverse lookups against those blocks.

### Basic Fierce Usage
`fierce --domain example.com`
This simple command automatically executes the zone transfer attempts and then proceeds to brute-force subdomains using its default, built-in wordlist.

### Advanced Fierce Options
- Using a custom wordlist (crucial for finding obscure, organization-specific subdomains):
  `fierce --domain example.com --wordlist /opt/SecLists/Discovery/DNS/subdomains-top1million-110000.txt`
- Specifying DNS servers to use for resolution (useful to bypass local DNS rate limiting or ISP filtering):
  `fierce --domain example.com --dns-servers 8.8.8.8 1.1.1.1`

---

## ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------+
|                      DNS Enumeration & Zone Transfer Attack Flow            |
+-----------------------------------------------------------------------------+

                                [ Attacker Machine ]
                                (Running dig / fierce)
                                          |
                                          |
   Phase 1: Identify Authoritative        | (1) dig example.com NS
            Nameservers                   |------------------------------------> [ Local / Public DNS ]
                                          |<------------------------------------
                                          |     Response: ns1.example.com
                                          |               ns2.example.com
                                          |
   Phase 2: Attempt Zone Transfer         |
            (AXFR)                        | (2) dig @ns1.example.com example.com AXFR
                                          |------------------------------------> [ Authoritative NS1 ]
                                          |                                        (Misconfigured)
                                          |<====================================
                                          |    Response: FULL ZONE DUMP
                                          |    (dev.ex.com, vpn.ex.com, etc.)
                                          |
        *If Phase 2 Fails*                |
                                          |
   Phase 3: Subdomain Brute-Forcing       | (3) Query: dev.example.com A
            (using Fierce + Wordlist)     |------------------------------------> [ Authoritative NS1 ]
                                          |<------------------------------------ (NXDOMAIN - Not Found)
                                          |
                                          | (4) Query: staging.example.com A
                                          |------------------------------------> [ Authoritative NS1 ]
                                          |<------------------------------------ (Response: 10.0.5.50)
                                          |
                                          | (5) Query: admin.example.com A
                                          |------------------------------------> [ Authoritative NS1 ]
                                          |<------------------------------------ (Response: 10.0.5.51)
```

## Defensive Perspective and Mitigation
Defending against DNS enumeration involves adhering to strict configuration best practices:
- **Restrict Zone Transfers:** Ensure that AXFR queries are explicitly denied for all IP addresses except the specific, authorized secondary/slave nameservers. In BIND, this is the `allow-transfer { trusted_ips; };` directive.
- **Split-Horizon DNS:** Maintain separate DNS infrastructures for internal and external networks. Internal DNS should resolve highly sensitive internal subdomains (e.g., `secret-db.corp.local`), while external DNS only resolves public-facing assets. Never expose internal zones to the internet.
- **Rate Limiting:** Implement DNS query rate limiting on the authoritative servers to slow down brute-force enumeration tools like `fierce`, `gobuster`, or `ffuf`.
- **DNSSEC (NSEC/NSEC3 Walking):** While DNSSEC provides cryptographic integrity to prevent DNS spoofing, improperly configured NSEC records allow attackers to "walk" the zone and enumerate all subdomains cryptographically without even guessing. NSEC3 with proper salt and iterations mitigates this zone walking vulnerability.
- **Monitor DNS Logs:** Watch for excessive NXDOMAIN responses from single IPs, which is a clear indicator of a dictionary-based subdomain brute-force attack in progress.

## Chaining Opportunities
- **OSINT to DNS Brute-forcing:** Use tools like `theHarvester` or `Amass` to gather initial subdomains via passive OSINT, then feed those into active DNS brute-forcing tools to find related environments. See [[01 - Open Source Intelligence OSINT Basics]].
- **Subdomain Takeover:** If DNS enumeration reveals a CNAME pointing to an external service (like AWS S3, GitHub Pages, or Heroku) that has been deleted or unregistered, an attacker can register that service and take over the subdomain. See [[25 - Subdomain Takeover Vulnerabilities]].
- **Web Application Testing:** Every discovered subdomain becomes a new target for web application vulnerability scanning and manual testing. Often, `dev.` subdomains lack the WAF protections of the main site. See [[40 - Web Application Architecture and Attack Surface]].
- **Network Scanning:** The IP addresses resolved from DNS enumeration form the target scope for Nmap port scanning. See [[04 - Nmap Advanced Port Scanning]].

## Related Notes
- [[02 - Domain Name System DNS Architecture]]
- [[11 - Enumerating Web Services and Virtual Hosts]]
- [[21 - Active Directory DNS Integration]]
