---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 50"
---

# Network QnA - Module 50: DNS Amplification and Spoofing

This document provides expert-level analysis of Domain Name System (DNS) vulnerabilities, exploring cache poisoning, amplification physics, EDNS0 abuses, and DNSSEC implementation flaws.

## Formal Technical Questions

**Q1: Detail the mechanics of the "Kaminsky Bug" (DNS Cache Poisoning). How did it overcome traditional transaction ID (TXID) guessing defenses?**
*Answer:*
Traditional cache poisoning relied on guessing the 16-bit TXID of a DNS query. An attacker would send a query for `google.com` to a recursive resolver and flood it with spoofed responses. If the attacker guessed the TXID before the legitimate auth server responded, the resolver cached the malicious IP.
*   **The Problem:** The "Bailiwick Rule" and TTL caching meant that once `google.com` was legitimately resolved, it stayed in the cache for hours, preventing further attacks until the TTL expired.
*   **The Kaminsky Innovation:** Dan Kaminsky bypassed the TTL wait time by querying for *random, non-existent* subdomains (e.g., `123xyz.google.com`, `abc456.google.com`).
*   **The Attack:** Because the subdomain isn't cached, the resolver must query the authoritative server. The attacker floods the resolver with spoofed responses claiming to be the authoritative server. These spoofed responses answer for `123xyz.google.com`, but crucially, they include a malicious *Authority Record (NS)* and *Additional Record (A)* for the *entire* `google.com` domain (e.g., `google.com NS attacker.com`).
*   **The Result:** If the attacker guesses the TXID for any of the random subdomains, the resolver accepts the payload and poisons the cache for the entire base domain. This allows continuous, rapid-fire attempts without waiting for TTLs.

**Q2: Explain the role of EDNS0 (Extension Mechanisms for DNS) in modern DNS Amplification attacks. Why is the `ANY` record particularly dangerous?**
*Answer:*
Original DNS via UDP was restricted to a maximum payload size of 512 bytes. If a response was larger, the server set the Truncation (TC) flag, forcing the client to switch to TCP.
*   **EDNS0:** Introduced to support DNSSEC and IPv6, EDNS0 allows a client to advertise a larger UDP buffer size (e.g., 4096 bytes) using an OPT pseudo-resource record in the query.
*   **The Amplification Abuse:** An attacker spoofs the victim's IP and sends a small query (60 bytes) with an EDNS0 OPT record advertising a 4096-byte buffer.
*   **The `ANY` Record:** The attacker asks for the `ANY` record type (or `TXT`) of a domain with massive cryptographic keys or text records (e.g., `isc.org`). The authoritative server packs all A, AAAA, MX, NS, and TXT records into a massive UDP response (up to 4000+ bytes) and sends it to the victim. This yields an amplification factor of 50x to 70x, instantly congesting the victim's network.

**Q3: What is DNS Rebinding, and how does it bypass the Same-Origin Policy (SOP) in modern web browsers?**
*Answer:*
DNS Rebinding is an attack targeting web browsers to interact with internal network services that the attacker cannot reach directly.
*   **The Setup:** The attacker registers a domain (`attacker.com`) and configures a custom DNS server.
*   **The Execution:**
    1.  The victim clicks a link to `http://attacker.com`.
    2.  The attacker's DNS server responds with the attacker's public IP address, but with an extremely short TTL (e.g., 1 second).
    3.  The victim's browser loads the page, downloading a malicious JavaScript payload.
    4.  The JS waits a few seconds (for the TTL to expire).
    5.  The JS makes an asynchronous `fetch()` request back to `http://attacker.com/api`.
    6.  The browser's DNS cache has expired, so it queries DNS again.
    7.  *The Rebind:* This time, the attacker's DNS server responds with an internal IP address (e.g., `127.0.0.1` or `192.168.1.1`).
*   **The Bypass:** The browser believes it is still communicating with `attacker.com`. The SOP allows the request because the domain name matches. The JavaScript can now read data from the victim's local router or internal applications and exfiltrate it.

## Scenario-Based Questions

**Q4: You are investigating a massive inbound traffic spike on your external firewall. The traffic consists entirely of UDP Port 53 responses, but your internal servers are not making any outbound DNS queries. What is happening, and how do you stop it?**
*Answer:*
The organization is the victim of a DNS Reflected Amplification DDoS attack.
*   **What is happening:** Attackers are querying open DNS resolvers on the internet, spoofing the source IP address to be our organization's external IP. The resolvers are sending the massive, unsolicited DNS responses to us.
*   **Mitigation Strategy:**
    1.  **Rate Limiting:** Immediately drop or heavily rate-limit incoming UDP 53 traffic that is not originating from our organization's known, trusted external DNS providers (like Google 8.8.8.8, Cloudflare, or our ISP's resolvers).
    2.  **Stateful Inspection:** Ensure the firewall is strictly stateful. It should automatically drop UDP 53 responses that do not have a corresponding state table entry (meaning we never sent the initial query).
    3.  **BGP RTBH / Scrubbing:** If the pipe is completely saturated upstream from the firewall, I must contact the ISP to implement Remotely Triggered Black Hole (RTBH) routing or redirect traffic through a scrubbing center (e.g., Akamai, Cloudflare) to absorb the volumetric attack.

**Q5: During a Red Team engagement, you find an internal network utilizing standard, unencrypted DNS. You have a foothold on a user's workstation. How do you exploit the DNS protocol to capture NTLMv2 hashes without directly attacking other hosts?**
*Answer:*
I will perform a WPAD (Web Proxy Auto-Discovery) spoofing attack via DNS/LLMNR.
1.  **The Flaw:** When Windows machines boot or open a browser, they often look for a proxy configuration file by automatically querying DNS for the hostname `wpad`.
2.  **The Exploit:** If the internal DNS zone does not have a static `wpad` record, the query fails. The workstation will then fall back to local broadcast protocols like LLMNR or NBT-NS.
3.  **Execution:** I will run `Responder` on my compromised workstation. When another machine broadcasts a request for `wpad`, Responder answers, claiming to be the WPAD server.
4.  **Hash Capture:** The victim machine connects to my rogue server to download the `wpad.dat` file. Responder prompts the victim for authentication (401 Unauthorized), causing the victim's OS to automatically send their NTLMv2 hash, which I capture for offline cracking.

**Q6: You are reviewing a company's BIND DNS server configuration. You notice they allow "Zone Transfers" (`AXFR`) to `ANY`. What is the security implication, and how would you demonstrate the impact to management?**
*Answer:*
*   **The Implication:** An AXFR (Authoritative Zone Transfer) request is designed for master-slave DNS server synchronization. By allowing `ANY` IP to request an AXFR, the organization is leaking its entire DNS zone file to the public internet.
*   **The Impact:** This provides an attacker with a complete, perfectly accurate map of the organization's external (and potentially internal, if split-horizon isn't configured) infrastructure. It reveals hidden subdomains, staging servers, development environments, and internal naming conventions.
*   **Demonstration:** I would run the command: `dig @target-dns-server.com targetdomain.com AXFR`. I would then present the output to management, highlighting sensitive subdomains like `vpn.target.com`, `dev-db.target.com`, or `git.target.com`, proving that reconnaissance is done instantly and silently.

## Deep-Dive Defensive Questions

**Q7: Explain how DNSSEC (DNS Security Extensions) prevents cache poisoning attacks. Does DNSSEC encrypt the DNS traffic?**
*Answer:*
*   **Mechanism:** DNSSEC adds cryptographic signatures to existing DNS records. It introduces new record types: RRSIG (Resource Record Signature), DNSKEY (Public Key), and DS (Delegation Signer).
*   **Prevention:** When a resolver receives a response, it verifies the RRSIG against the DNSKEY. Because an attacker cannot forge the cryptographic signature without the private key, the resolver will reject any spoofed, cache-poisoning payloads.
*   **Encryption:** **NO.** DNSSEC provides *authentication* and *data integrity*, but it does NOT provide *confidentiality*. The DNS queries and responses are still transmitted in plaintext. To encrypt DNS, protocols like DoH (DNS over HTTPS) or DoT (DNS over TLS) must be used.

**Q8: Describe the defense mechanism known as "Source Port Randomization." How did it specifically mitigate the Kaminsky attack?**
*Answer:*
*   **The Pre-Kaminsky State:** Resolvers used to send DNS queries using a static or highly predictable source UDP port (e.g., 53 or incrementing from 1024). The only variable an attacker had to guess was the 16-bit TXID (65,536 possibilities), which is easily brute-forced in seconds.
*   **The Mitigation:** Source Port Randomization forces the resolver to use a random, ephemeral UDP source port for every outgoing query.
*   **The Mathematical Impact:** The attacker must now guess BOTH the 16-bit TXID AND the 16-bit Source Port. This increases the search space from $2^{16}$ (65,536) to $2^{32}$ (over 4.2 billion) possibilities. It becomes computationally unfeasible to flood the resolver with enough spoofed packets to guess both values before the legitimate authoritative server responds.

**Q9: What is Response Rate Limiting (RRL) in BIND/Knot DNS? How does it differentiate between legitimate massive DNS usage and an amplification attack?**
*Answer:*
RRL is a mitigation technique implemented directly on Authoritative DNS servers to stop them from being used as reflectors in DDoS attacks.
*   **The Mechanism:** RRL tracks the rate of identical or highly similar responses sent to a specific client /24 subnet.
*   **The Differentiation:** If a legitimate ISP resolver (like Google) asks for many different records, RRL allows it. However, if a single IP subnet rapidly requests the exact same `ANY` or `TXT` record (typical of a spoofed amplification attack), the RRL threshold is breached.
*   **The Action:** Instead of responding to every query, the authoritative server begins dropping the queries, or better, it returns a truncated (TC) response or a SLIP response. This forces the client to retry over TCP. A spoofed victim IP won't complete the TCP 3-way handshake, neutralizing the UDP amplification physics entirely.

## Real-World Attack Scenario

### Attack Flow: DNS Rebinding for AWS Metadata Extraction
1.  **Setup:** The attacker registers `malicious.com`. They point the NS records to a custom DNS server they control.
2.  **Phishing:** The attacker sends a phishing link `http://aws-auth.malicious.com` to an administrator working inside a corporate AWS VPC.
3.  **Initial Resolution:** The admin clicks the link. The attacker's DNS server responds with the attacker's public IP, setting a TTL of 1 second.
4.  **Payload Delivery:** The browser loads a malicious webpage containing a hidden iframe and an asynchronous JavaScript payload.
5.  **The Rebind:** The JavaScript waits 2 seconds, then attempts to fetch data from `http://aws-auth.malicious.com/latest/meta-data/iam/security-credentials/`.
6.  **Resolution 2:** The browser queries DNS again because the TTL expired. The attacker's DNS server now responds with `169.254.169.254` (The AWS Instance Metadata Service IP).
7.  **Data Exfiltration:** The browser connects to the metadata service. The SOP allows this because the domain name (`aws-auth.malicious.com`) hasn't changed. The metadata service returns the temporary AWS IAM access keys. The JavaScript reads the keys and POSTs them back to the attacker's external server.
8.  **Compromise:** The attacker uses the stolen IAM keys to access the AWS environment and exfiltrate S3 buckets.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
| Kaminsky DNS Cache Poisoning Attack Workflow                                      |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Attacker]                       [Target Resolver]             [Auth Server]     |
|      |                                 |                              |           |
|      | 1. Query: rand1.google.com      |                              |           |
|      |-------------------------------->|                              |           |
|      |                                 | 2. Recursive Query           |           |
|      |                                 |----------------------------->|           |
|      | 3. FLOOD of Spoofed Responses   |                              |           |
|      |    Spoofed Src: [Auth Server]   |                              |           |
|      |    TXID: Guessing 1-65535       |                              |           |
|      |    Ans: rand1 is 1.1.1.1        |                              |           |
|      |    Auth: google.com NS hacker   |                              |           |
|      |================================>|                              |           |
|      |                                 |                              |           |
|      | [!] TXID Guessed Correctly!     |                              |           |
|      | [!] Cache is Poisoned!          |                              |           |
|      |                                 | 4. Legitimate Response       |           |
|      |                                 |<-----------------------------|           |
|      |                                 | (Dropped: TXID already used) |           |
|      |                                 |                              |           |
|      | 5. Victim queries google.com    |                              |           |
|      |-------------------------------->|                              |           |
|      |                                 | 6. Redirected to Hacker NS   |           |
|      |<--------------------------------|                              |           |
+-----------------------------------------------------------------------------------+
```

## Chaining Opportunities
*   **Cache Poisoning -> MITM:** Poisoning the DNS cache allows redirection of MX records. Attackers can route all corporate email through their infrastructure, perform SSL stripping, and steal credentials.
*   **Zone Transfer -> AD Compromise:** Chain an AXFR vulnerability to map the internal network, locate the Domain Controllers and Certificate Authorities, and launch targeted Kerberoasting or AS-REP Roasting attacks.

## Related Notes
*   [[Interview Prep - Network Security]]
*   [[Cryptography - DNSSEC and RRSIG]]
*   [[Web Exploitation - Same Origin Policy and Rebinding]]
*   [[Active Directory Evasion - LLMNR and NBT-NS]]
