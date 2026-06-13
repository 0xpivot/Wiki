---
tags: [vapt, subdomain-takeover, dns, email, advanced]
difficulty: advanced
module: "34 - Subdomain Takeover"
topic: "34.06 MX Takeover (email interception)"
---

# MX Takeover: Email Interception and Routing Hijacks

## 1. Introduction to MX Takeover
MX (Mail Exchange) Takeover is a specialized, stealthy, and deeply devastating form of subdomain takeover that specifically targets the email routing infrastructure of an organization. Unlike A or CNAME records which direct HTTP web traffic and require active user interaction to exploit, MX records instruct Mail Transfer Agents (MTAs) across the globe on where to deliver inbound emails for a specific domain or subdomain. 

When an organization configures an MX record pointing to an expired domain, an unregistered third-party service (like an abandoned Mailgun, Sendgrid, or Google Workspace tenant), or a misconfigured cloud mail provider, an attacker can claim that destination. Consequently, the attacker will silently receive all emails destined for that domain without the sender or the intended recipient ever realizing a interception has occurred. This leads directly to sensitive corporate data exposure, password reset hijacking, and the capability to execute highly privileged social engineering attacks.

## 2. Understanding Email Routing via MX Records
To comprehend the sheer impact of this attack, we must trace the lifecycle of an email at the protocol level. 

Imagine an external partner, Alice, sends a confidential document to `admin@internal.target.com`. Her mail server (e.g., Google Workspace) performs the following sequence to route the message:
1. Google's MTA queries the global DNS hierarchy for the MX records of the recipient domain `internal.target.com`.
2. The authoritative DNS server for `target.com` responds with the configured MX record: 
   `internal.target.com. IN MX 10 mail.abandoned-vendor.com.`
3. Google's MTA then queries the DNS for the A/AAAA record corresponding to `mail.abandoned-vendor.com` to find the actual IP address of the mail server.
4. Google establishes a TCP connection to the resolved IP address on Port 25 (SMTP) and initiates the SMTP handshake to deliver Alice's email.

If `abandoned-vendor.com` is completely unregistered, the DNS lookup in step 3 fails, the connection cannot be established, and Alice receives a bounce-back email indicating a delivery failure. 

However, if an attacker has proactively registered `abandoned-vendor.com` and set up a listening SMTP server, Google's MTA will happily deliver Alice's highly confidential email directly into the attacker's hands. The attacker acts as a black hole, absorbing all corporate communications.

## 3. Attack Flow Architecture and Interception Mechanics

```text
                                [ THE MX TAKEOVER ATTACK FLOW ]

  [ External Sender / Automated System ]
                |
                | 1. Sends critical email to reset-password@corp-portal.target.com
                |
  [ Sender's Mail Server (e.g., Exchange/Postfix) ]
                |
                | 2. DNS Query: "What is the authoritative MX record for corp-portal.target.com?"
                |----------------------------------------------------------> [ Global DNS Infrastructure ]
                                                                                   |
                | 3. Response: "MX 10 inbound.old-saas-provider.net"               |
                |<-----------------------------------------------------------------+
                |
                | 4. DNS Query: "What is the A record IP for inbound.old-saas-provider.net?"
                |----------------------------------------------------------> [ Global DNS Infrastructure ]
                                                                                   |
                | 5. Response: "198.51.100.99" (The Attacker's VPS IP)             |
                |<-----------------------------------------------------------------+
                |
                | 6. Initiates SMTP Connection (Port 25)
                |    to 198.51.100.99
                |------------------------------------------------------> [ Attacker's Malicious SMTP Server ]
                                                                         (Configured with Postfix Catch-All)
                                                                                   |
                                                                                   | 7. Accepts email cleanly (250 OK).
                                                                                   |    Extracts plaintext, attachments,
                                                                                   |    password reset links, OTP tokens.
                                                                                   V
                                                                          [ Attacker reads the email in plaintext ]
```

## 4. Vulnerability Conditions and Attack Vectors
An MX Takeover is viable and exploitable under two primary, distinct scenarios:

1. **The Dangling Domain Vector:** The MX record explicitly points to a fully qualified domain name (FQDN) that has expired and is currently available for public registration on the open market. This is the most direct form of the vulnerability.
2. **The Unclaimed SaaS Tenant Vector:** The MX record points to a shared SaaS provider's infrastructure (like `mx.sendgrid.net` or `inbound.mailgun.org`), but the target company has either deleted their account, migrated away, or simply failed to verify the domain within the SaaS platform's dashboard. An attacker can create a fresh, rogue account on that same SaaS platform and claim the target's domain as their own inbound routing domain, leveraging the SaaS provider to do the interception for them.

## 5. Step-by-Step Exploitation Walkthrough

### Phase 1: Massive Discovery and DNS Enumeration
The attacker starts by harvesting MX records for all known, enumerated subdomains. They rely on massive wordlists and passive datasets.
```bash
#!/bin/bash
# A simple script to extract MX records from a list of subdomains
cat all_live_subdomains.txt | while read sub; do
  mx_records=$(dig MX $sub +short)
  if [ ! -z "$mx_records" ]; then
    echo -e "[\033[1;34mINFO\033[0m] $sub -> $mx_records"
  fi
done > mx_records_found.txt
```

Example output:
```text
[INFO] intranet.target.com -> 10 mx1.dead-startup.com.
[INFO] marketing.target.com -> 10 mxa.mailgun.org.
```

### Phase 2: Vulnerability Validation and Profiling
The attacker carefully evaluates the findings to determine the exploit path:

**Scenario A: Dead Domain (`dead-startup.com`)**
The attacker performs a WHOIS lookup to check availability.
```bash
whois dead-startup.com | egrep -i "No match|Status: free|not found"
```
If available, the attacker immediately registers the domain via a standard registrar.

**Scenario B: Unclaimed SaaS (`mailgun.org`)**
The attacker recognizes `mxa.mailgun.org` as valid Mailgun infrastructure. They must test if the domain `marketing.target.com` is available to be claimed inside their own Mailgun tenant dashboard by attempting to add it as a receiving domain.

### Phase 3: Claiming the Target Infrastructure
Assuming Scenario A (Dead Domain), the attacker purchases `dead-startup.com`. 
They provision a Virtual Private Server (VPS) on DigitalOcean or AWS. They configure the DNS settings for `dead-startup.com`, pointing the `mx1.dead-startup.com` A-record to their new VPS IP address.

### Phase 4: Configuring a Postfix Catch-All Mail Server
To capture *every single* email sent to the subdomain, regardless of the specific user prefix (e.g., capturing `admin@`, `noreply@`, `it-support@`, `ceo@` simultaneously), the attacker configures a "Catch-All" SMTP server. Postfix is the industry standard for this.

**Main Configuration Snippet (`/etc/postfix/main.cf`):**
```text
myhostname = mx1.dead-startup.com
mydomain = dead-startup.com
virtual_alias_domains = intranet.target.com
virtual_alias_maps = pcre:/etc/postfix/virtual
```

**Catch-all PCRE mapping (`/etc/postfix/virtual`):**
```text
# This regex routes anything sent to @intranet.target.com to the local linux user 'attacker_local'
/.@intranet\.target\.com$/   attacker_local
```
After building the map (`postmap /etc/postfix/virtual`) and restarting Postfix (`systemctl restart postfix`), all emails destined for `*@intranet.target.com` are transparently delivered to a local inbox file on the attacker's server.

### Phase 5: Intercepting Traffic and Post-Exploitation
The attacker actively monitors the local inbox (`tail -f /var/mail/attacker_local`). 
Real-world, high-impact exploits at this stage include:
- **Password Resets and ATO:** The attacker goes to third-party services (Slack, Jira, GitHub, AWS, Azure) and triggers a "Forgot Password" flow for high-value users known to use the `@intranet.target.com` email addresses. The reset links land directly in the attacker's catch-all inbox, allowing instant account takeover.
- **SSO and MFA Bypasses:** Intercepting magic authentication links or One-Time Passwords (OTPs) sent via email used as a primary or secondary authentication factor.
- **Passive Information Disclosure:** Silently collecting internal corporate communications, automated cron job outputs containing sensitive data, server error alerts detailing internal network topologies, or financial reports sent to legacy automated mailing lists.

## 6. Deep Dive: B2B Trust Exploitation and SPF/DKIM
An MX Takeover allows the attacker not only to receive email but, combined with a lack of strict SPF/DKIM records on the hijacked subdomain, allows them to *send* emails that appear incredibly legitimate.

If an attacker sends a phishing email from `admin@intranet.target.com` to a partner company, the partner's spam filters will check the root domain's reputation. Because the attacker hijacked the legitimate subdomain, the email bypasses traditional filtering, exploiting the established Business-to-Business (B2B) trust relationship. This leads to high-success-rate Business Email Compromise (BEC) attacks.

## 7. Defensive Measures and Remediation
1. **Implement Null MX Records:** If a subdomain is strictly used for web hosting and does NOT send or receive email, it should explicitly declare this using a Null MX record. This tells all MTAs to immediately drop mail for this domain, preventing spoofing and routing issues.
   ```text
   intranet.target.com. IN MX 0 .
   ```
2. **Continuous DNS Audits:** Continuously monitor MX records to ensure they point to active, fully owned, and trusted infrastructure. Do not let records linger after vendor contracts expire.
3. **Strict SaaS Domain Verification:** Ensure that any domain added to an external mail provider (Sendgrid, Postmark, AWS SES, Mailgun) is strictly verified using DNS TXT records, preventing arbitrary claiming by attackers on shared platforms.

## 8. Chaining Opportunities
- **[[14 - Account Takeover (ATO)]]**: Triggering password resets for third-party SaaS applications utilizing the hijacked email addresses.
- **[[22 - Phishing & Social Engineering]]**: Using the hijacked subdomain to send perfectly authenticated, DMARC-compliant phishing emails to internal employees or external clients.
- **[[05 - NS Takeover]]**: Often, if you find a dangling NS record, you can forge the MX records yourself dynamically, achieving this attack vector as a secondary payload.
- **[[27 - Business Email Compromise (BEC)]]**: Leveraging the intercepted communications to inject fraudulent invoices into ongoing email threads.

## 9. Related Notes
- [[01 - DNS Fundamentals]]
- [[04 - Subdomain Takeover — Full Exploit Walkthrough]]
- [[05 - NS Takeover]]
- [[19 - Email Spoofing & DMARC]]
