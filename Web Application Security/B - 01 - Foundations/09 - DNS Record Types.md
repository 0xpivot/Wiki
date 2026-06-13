---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.09 DNS Record Types"
---

# 01.09 — DNS Record Types

## What is it?

DNS stores information about a domain in different **record types**. Each type answers a different question about the domain. Knowing all record types is essential for recon — they reveal mail servers, IP addresses, SPF policies, verification tokens, and sometimes internal infrastructure.

---

## All DNS Record Types — Reference

### A Record — IPv4 Address
Maps a hostname to an IPv4 address. The most common record.

```bash
dig google.com A

# Output:
# google.com.   300  IN  A  142.250.182.46
#               ↑TTL    ↑Class ↑Record   ↑IP Address
```

**VAPT use:** Find the server IP. If behind CDN, try to find the real origin IP.

---

### AAAA Record — IPv6 Address
Maps a hostname to an IPv6 address.

```bash
dig google.com AAAA
# google.com.  300  IN  AAAA  2607:f8b0:4004:c07::65
```

**VAPT use:** Some WAFs/CDNs only protect IPv4. Try the IPv6 address directly to bypass WAF.
```bash
# Get IPv6 address
dig target.com AAAA +short
# Connect directly bypassing WAF
curl -6 http://[2607:f8b0:4004:c07::65]/
```

---

### CNAME Record — Canonical Name (Alias)
Points one hostname to another hostname (not an IP directly).

```bash
dig www.github.com CNAME
# www.github.com.  3600  IN  CNAME  github.com.

dig blog.target.com CNAME
# blog.target.com.  300  IN  CNAME  target.wordpress.com.
#                                   ↑ If unclaimed → subdomain takeover!
```

**VAPT use — Subdomain Takeover:**
```
blog.target.com → CNAME → target.wordpress.com (unclaimed!)
  ↓
If target.wordpress.com is unclaimed on WordPress.com:
  ↓
Attacker claims it → controls blog.target.com → steal cookies,
serve phishing pages under legitimate domain
```

---

### MX Record — Mail Exchange
Points to mail servers for the domain.

```bash
dig target.com MX
# target.com.  3600  IN  MX  10  mail1.target.com.
# target.com.  3600  IN  MX  20  mail2.target.com.
#                         ↑ Priority (lower = preferred)
```

**VAPT use:**
- Find mail servers for phishing campaign targeting
- Mail servers often run older software — CVE hunting
- Try password spray against mail login portals
- Check for open relay (send email from any address)

```bash
# Check for open relay
nmap -p 25 --script smtp-open-relay target.com

# Enumerate users via SMTP VRFY
smtp-user-enum -M VRFY -U users.txt -t mail.target.com
```

---

### NS Record — Nameserver
Lists the authoritative nameservers for a domain.

```bash
dig target.com NS
# target.com.  172800  IN  NS  ns1.target.com.
# target.com.  172800  IN  NS  ns2.target.com.
```

**VAPT use:**
- Attempt zone transfer against each NS
- If NS is a third-party service that's unclaimed → NS takeover (rare but critical)
- Identify DNS provider for targeted attacks

```bash
# Try zone transfer against each nameserver
dig axfr @ns1.target.com target.com
dig axfr @ns2.target.com target.com
```

---

### TXT Record — Text
Stores arbitrary text. Used for SPF, DKIM, DMARC, domain verification, and often leaks internal info.

```bash
dig target.com TXT
# target.com.  300  IN  TXT  "v=spf1 include:_spf.google.com ~all"
# target.com.  300  IN  TXT  "google-site-verification=abc123"
# target.com.  300  IN  TXT  "MS=ms12345678"   ← Microsoft O365 verification
# target.com.  300  IN  TXT  "atlassian-domain-verification=abc"
# target.com.  300  IN  TXT  "docker-verification=abc123"
```

**VAPT use — SPF Analysis:**
```bash
dig target.com TXT | grep spf

# v=spf1 ip4:203.0.113.0/24 include:mailgun.org -all
#         ↑ IP ranges that can send email on behalf of domain
#         ↑ Reveals mail service providers and IP ranges

# SPF softfail (~all) = mail can be spoofed and delivered (just flagged)
# SPF hardfail (-all) = mail from unauthorized IPs rejected

# If SPF is missing → can spoof email from this domain!
```

**VAPT use — Domain Verification Tokens:**
```
google-site-verification=abc123
↓
Company verified ownership of domain to Google
Tells you they use Google Search Console / Google Workspace

MS=ms12345678
↓
Microsoft Office 365 verification
Tells you they use Microsoft 365 (target for phishing/password spray)
```

---

### SOA Record — Start of Authority
Contains administrative info about the DNS zone.

```bash
dig target.com SOA
# target.com.  900  IN  SOA  ns1.target.com. admin.target.com. (
#                             2024010101  ← serial number
#                             3600        ← refresh interval
#                             900         ← retry interval
#                             604800      ← expire
#                             300 )       ← minimum TTL

# admin.target.com → this is the admin email with @ replaced by .
# So: admin@target.com is the DNS admin contact!
```

**VAPT use:** `admin.target.com.` in SOA → admin email = `admin@target.com` → target for spear phishing.

---

### PTR Record — Pointer (Reverse DNS)
Maps an IP address back to a hostname. Used for reverse lookups.

```bash
# Reverse lookup of 8.8.8.8
dig -x 8.8.8.8
# 8.8.8.8.in-addr.arpa.  21599  IN  PTR  dns.google.

# Bulk reverse lookups reveal internal hostnames from IPs
for ip in $(seq 1 254); do
  host 192.168.1.$ip 2>/dev/null | grep "domain name"
done
```

**VAPT use:** Reverse DNS reveals hostnames from IPs — find internal server names, role identification (db1.internal, vpn.corp.local).

---

### SRV Record — Service
Specifies location (host and port) of specific services.

```bash
dig _ldap._tcp.target.com SRV
# _ldap._tcp.target.com.  600  IN  SRV  0 100 389 dc1.target.com.
#                                        ↑Pri ↑Weight ↑Port ↑Host

dig _kerberos._tcp.target.com SRV
# _kerberos._tcp.target.com.  600  IN  SRV  0 100 88 dc1.target.com.
```

**VAPT use:** SRV records reveal:
- Active Directory domain controllers (`_ldap._tcp`, `_kerberos._tcp`)
- SIP servers (`_sip._tcp`)
- XMPP servers
Internal infrastructure that shouldn't be public

---

### CAA Record — Certification Authority Authorization
Specifies which CAs are allowed to issue SSL certs for the domain.

```bash
dig target.com CAA
# target.com.  3600  IN  CAA  0 issue "letsencrypt.org"
# target.com.  3600  IN  CAA  0 issue "digicert.com"
```

**VAPT use:** Tells you which CA they use — if a CA is vulnerable or if you can phish the CA's issuance process.

---

### DMARC — Email Security Policy (TXT record)
```bash
dig _dmarc.target.com TXT
# _dmarc.target.com. 300 IN TXT "v=DMARC1; p=reject; rua=mailto:dmarc@target.com"
#                                           ↑ policy: none/quarantine/reject
```

**VAPT use — Email Spoofing:**
```
p=none     → DMARC not enforced → can spoof email from this domain
p=quarantine → Goes to spam → might still work for phishing
p=reject   → Spoofed email rejected → need to use similar-looking domain

No DMARC record → No email spoofing protection at all!
```

---

## Full Recon — All Records at Once

```bash
# Get everything
dig target.com ANY

# dnsrecon — comprehensive
dnsrecon -d target.com -t std

# dnsx — resolve many records
echo "target.com" | dnsx -a -aaaa -cname -mx -ns -txt -ptr -soa

# fierce — all-in-one DNS recon
fierce --domain target.com

# theHarvester — includes DNS
theHarvester -d target.com -b all
```

---

## Security Context — DNS Records Tell You Everything

```
From DNS records alone you can learn:
┌────────────────────────────────────────────────────────┐
│  A/AAAA  → Web server IPs, CDN vs direct              │
│  CNAME   → Third-party services, takeover candidates  │
│  MX      → Mail provider, email attack surface        │
│  NS      → DNS provider                               │
│  TXT     → Email security, third-party services used  │
│  SOA     → Admin email address                        │
│  SRV     → Active Directory, internal services        │
│  PTR     → Internal hostnames from IPs                │
│  DMARC   → Can we spoof email from this domain?       │
│  SPF     → What IPs/services send mail for them       │
└────────────────────────────────────────────────────────┘
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Zone transfer open | Restrict AXFR to specific IPs |
| CNAME to unclaimed service | Audit all CNAME records, claim or remove |
| Missing SPF / DMARC | Add SPF (-all) and DMARC (p=reject) records |
| SOA exposes admin email | Use a role email that's not a phishing target |
| SRV records exposing internal services | Remove internal SRV records from public DNS |
| TXT records with sensitive info | Audit TXT records, remove unnecessary ones |

---

## Related Notes
- [[08 - DNS How Domain Names Resolve]] — DNS resolution process
- [[Module 34 - Subdomain Takeover]] — CNAME takeover
- [[Module 05 - Recon]] — DNS enumeration tools
- [[Module 46 - Social Engineering]] — email spoofing via missing SPF/DMARC
