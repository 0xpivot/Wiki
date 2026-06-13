---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.15 Account Takeover via Email Domain Takeover"
---
# Account Takeover via Email Domain Takeover

## Introduction to Email Domain Takeover

Email Domain Takeover is a sophisticated vulnerability that occurs when an attacker gains control over a domain or subdomain used by an organization to route incoming emails. Once control is established, the attacker can intercept, read, and reply to emails intended for employees or services within that domain.

The most critical impact of this vulnerability is mass Account Takeover (ATO). By controlling the email domain, an attacker can trigger password reset requests for third-party services (e.g., AWS, GitHub, Slack, Jira) linked to `@vulnerable-domain.com` addresses and capture the password reset links sent via email.

## DNS Fundamentals for Email

Understanding email routing requires a grasp of specific DNS records:
- **MX (Mail Exchange)**: Directs email to a specific mail server. E.g., `MX 10 aspmx.l.google.com`.
- **A / CNAME**: If no MX record exists, mail transfer agents (MTAs) fall back to the A or CNAME record of the domain.
- **TXT (SPF/DKIM/DMARC)**: Used for email authentication, but primarily for *sending* limits, not receiving routing.

## Vectors of Domain Takeover

### 1. Expired Domains
An organization registers a domain (e.g., `company-legacy.com`), uses it for employee emails, and subsequently forgets to renew it. 
An attacker buys the expired domain from a registrar, sets up an MX record pointing to their own server, and creates a "catch-all" inbox. Any password reset sent to `employee@company-legacy.com` falls right into the attacker's hands.

### 2. Subdomain Takeover (CNAME/NS Hijacking)
A company configures an MX record or CNAME for a subdomain pointing to a third-party service (e.g., `support.company.com CNAME company.zendesk.com`).
If the company stops using Zendesk but leaves the CNAME in their DNS, an attacker can register `company.zendesk.com` on Zendesk's platform. They now control the subdomain. 
If the subdomain was configured to receive mail, the attacker can intercept emails sent to `*@support.company.com`.

### 3. Third-Party Mail Routing Misconfigurations
Organizations use services like Mailgun, SendGrid, or AWS SES to route incoming emails. 
If DNS records still point to Mailgun, but the organization deletes the domain from their Mailgun dashboard, an attacker can claim that domain in their own Mailgun account. Mailgun will verify the domain because the DNS records are still intact, granting the attacker full control over incoming mail routing.

## Anatomy of the Attack: Pre-Account Takeover

Often, attackers target SaaS platforms (like Slack or Notion) using a method called Pre-Account Takeover.
1. An attacker identifies that `corp-dev.com` is an abandoned domain used by developers.
2. They register `corp-dev.com` and set up an MX record to their inbox.
3. They attempt to register an account on Slack/GitHub using `admin@corp-dev.com`.
4. If an account already exists, they trigger a password reset.
5. If the account doesn't exist, they create it, intercept the email verification, and wait for internal employees to share sensitive data with the "trusted" domain account.

### ASCII Diagram: The Domain Takeover Flow

```text
       DNS INFRASTRUCTURE                        TARGET (e.g., GitHub)
       ------------------                        ---------------------
                                                          |
1. Target Company forgets to                              |
   renew 'company-old.com'                                |
                                                          |
2. Attacker buys 'company-old.com'                        |
   via Namecheap                                          |
                                                          |
3. Attacker configures MX Record:                         |
   company-old.com MX 10 attacker-mail.com                |
                                                          |
4. Attacker requests password reset --------------------->|
   for 'ceo@company-old.com'                              |
                                                          |
                                                          | 5. GitHub generates reset link.
                                                          |    Queries DNS for MX of company-old.com
                                                          |    DNS replies: attacker-mail.com
                                                          |
6. GitHub sends email to attacker-mail.com <--------------|
   [ "Click here to reset your password..." ]             |
                                                          |
7. Attacker clicks link, changes password,                |
   and achieves full Account Takeover!                    |
                                                          v
```

## Internal Domain Takeovers (`.local`, `.corp`)

Historically, systems fell back to NetBIOS or LLMNR for resolving internal domains (e.g., `exchange.corp.local`). While not directly exploitable over the internet, an attacker inside the network can spoof these resolutions. If internal applications send password resets or administrative alerts to unregistered internal domains, an attacker can set up an internal SMTP relay to capture them.

## Advanced Scenario: Dangling DNS leading to Email Routing

Sometimes an A record points to an ephemeral IP (like an unallocated AWS Elastic IP). An attacker can allocate and reallocate Elastic IPs until they obtain the dangling IP. Once they have the IP, they can host an SMTP server on port 25.
Since MTAs fall back to the A record when no MX record is present, the attacker's server will receive all email destined for that subdomain.

## Detection and Exploitation Tools

- **Sublist3r / Amass / dnsrecon**: Used to enumerate subdomains and identify dangling CNAMEs or unresolving domains.
- **subjack / nuclei**: Automated scanners that identify vulnerable subdomain takeovers.
- **Catch-All Mailboxes**: Attackers use services like Google Workspace or custom Postfix setups configured as a catch-all (`*@hijacked-domain.com`) to ensure no emails are missed.

## Mitigation Strategies

1. **DNS Hygiene**: Regularly audit and prune DNS zones. Remove CNAME, A, and MX records for services no longer in use.
2. **Domain Renewal Tracking**: Centralize domain registration and automate renewal payments. Lock domains to prevent unauthorized transfers.
3. **Verify Third-Party Services**: Before deleting a domain from a service like Mailgun or AWS SES, delete the corresponding DNS records first to prevent dangling misconfigurations.
4. **SSO and Identity Management**: Rely on centralized Single Sign-On (SAML/OIDC) rather than email-based password resets for critical infrastructure. If an email domain is hijacked, the attacker still needs the central IdP credentials to access SaaS platforms.
5. **DMARC/SPF/DKIM**: While these protect outgoing mail from spoofing, configuring strict policies can sometimes alert administrators to anomalous infrastructure usage.

## Chaining Opportunities
- **Privilege Escalation**: Resetting passwords for administrative accounts on AWS, Azure, or source code repositories.
- **Information Disclosure**: Intercepting sensitive automated reports, invoices, or PII sent to the hijacked domain.
- **Social Engineering / Phishing**: Using the hijacked domain to send highly credible internal phishing emails, leveraging the inherited domain reputation.

## Related Notes
- [[06 - Subdomain Takeover]]
- [[33 - Cloud Security Flaws]]
- [[24 - Password Reset Poisoning]]
- [[48 - Open Source Intelligence (OSINT)]]
