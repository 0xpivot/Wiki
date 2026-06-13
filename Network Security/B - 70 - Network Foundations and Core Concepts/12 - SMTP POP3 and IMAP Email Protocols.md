---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.12 SMTP POP3 and IMAP Email Protocols"
---

# 70.12 SMTP POP3 and IMAP Email Protocols

## 1. Overview of the Email Ecosystem
Email delivery uses a store-and-forward architecture.
- **MUA (Mail User Agent):** Client software (Outlook).
- **MTA (Mail Transfer Agent):** Routing server (Postfix).
- **MDA (Mail Delivery Agent):** Storage server (Dovecot).

## 2. Simple Mail Transfer Protocol (SMTP)
Operates on Port 25 (Relay), 587 (Submission), 465 (SMTPS).
SMTP is text-based. Key commands:
- `HELO` / `EHLO`: Identify client.
- `MAIL FROM`: Envelope sender.
- `RCPT TO`: Envelope recipient.
- `DATA`: Message payload (headers + body).

## 3. POP3 and IMAP
Used for retrieval.
- **POP3 (Port 110/995):** Downloads and deletes. Simple states.
- **IMAP (Port 143/993):** Synchronizes folders. Leaves mail on server.

## 4. ASCII Diagram: Email Delivery Flow
```text
  [Sender MUA]
       | (SMTP Port 587)
       v
  [Sender MTA] ------(SMTP Port 25)-----> [Receiver MTA]
                                                |
                                                v
                                          [Receiver MDA]
                                                |
  [Receiver MUA] <---(IMAP Port 993)------------+
```

## 5. Security Extensions
- **STARTTLS:** Upgrades plaintext connections to TLS.
- **SPF (Sender Policy Framework):** DNS TXT record specifying authorized sending IPs.
- **DKIM (DomainKeys Identified Mail):** Cryptographic signature added to email headers.
- **DMARC:** Policy dictating actions for SPF/DKIM failures.

## 6. VAPT Context and Exploitation
- **Open Relays:** Testing if the server relays mail for non-local domains.
- **User Enumeration:** Utilizing `VRFY` and `EXPN` commands.
- **Phishing:** Main vector for initial access payload delivery.

## Chaining Opportunities
- **Lateral Movement:** Pivot through compromised segments using [[11 - SSH Protocol Basics and Key Authentication]].
- **Payload Delivery:** Combine with [[12 - SMTP POP3 and IMAP Email Protocols]] for access.
- **Recon:** Findings feed into [[13 - SNMP Protocol Basics and Community Strings]].
- **Evasion:** Bypasses [[14 - Firewalls IDS IPS and NAT Explained]].
- **VPNs:** Compare with [[15 - VPNs IPsec and Tunneling Basics]].

## Related Notes
- [[11 - SSH Protocol Basics and Key Authentication]]
- [[12 - SMTP POP3 and IMAP Email Protocols]]
- [[13 - SNMP Protocol Basics and Community Strings]]
- [[14 - Firewalls IDS IPS and NAT Explained]]
- [[15 - VPNs IPsec and Tunneling Basics]]

## 7. Extended SMTP Transaction and Hardened Config Reference
Below is a full sequence of an authenticated ESMTP transaction, followed by a deeply hardened Postfix `main.cf` template designed to prevent open relaying and enforce TLS.

### 7.1 ESMTP Dialogue Example
```text
S: 220 mail.example.com ESMTP Postfix
C: EHLO attacker.com
S: 250-mail.example.com
S: 250-PIPELINING
S: 250-SIZE 10240000
S: 250-VRFY
S: 250-ETRN
S: 250-STARTTLS
S: 250-ENHANCEDSTATUSCODES
S: 250-8BITMIME
S: 250-DSN
S: 250 CHUNKING
C: STARTTLS
S: 220 2.0.0 Ready to start TLS
C: [ TLS Handshake occurs ]
C: EHLO attacker.com
S: 250-mail.example.com
S: 250-AUTH PLAIN LOGIN
S: 250-8BITMIME
C: AUTH LOGIN
S: 334 VXNlcm5hbWU6
C: dGVzdHVzZXI=
S: 334 UGFzc3dvcmQ6
C: c3VwZXJzZWNyZXQ=
S: 235 2.7.0 Authentication successful
C: MAIL FROM:<ceo@example.com>
S: 250 2.1.0 Ok
C: RCPT TO:<employee@example.com>
S: 250 2.1.5 Ok
C: DATA
S: 354 End data with <CR><LF>.<CR><LF>
C: Subject: Urgent Wire Transfer
C: Please process immediately.
C: .
S: 250 2.0.0 Ok: queued as 12345ABC
C: QUIT
S: 221 2.0.0 Bye
```

### 7.2 Postfix `main.cf` Hardening Template
```text
# Basic Network Settings
myhostname = mail.example.com
mydomain = example.com
myorigin = $mydomain
inet_interfaces = all
inet_protocols = ipv4
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain

# Relay and Anti-Spam Restrictions
mynetworks = 127.0.0.0/8, 192.168.1.0/24
relay_domains = $mydestination
smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, defer_unauth_destination
smtpd_recipient_restrictions = 
    permit_mynetworks,
    permit_sasl_authenticated,
    reject_unauth_destination,
    reject_invalid_hostname,
    reject_non_fqdn_hostname,
    reject_non_fqdn_sender,
    reject_non_fqdn_recipient,
    reject_unknown_sender_domain,
    reject_unknown_recipient_domain,
    reject_unauth_pipelining,
    reject_rbl_client zen.spamhaus.org

# TLS Configuration (Enforcing Encryption)
smtpd_tls_security_level = may
smtpd_tls_auth_only = yes
smtpd_tls_cert_file = /etc/ssl/certs/mail.example.com.crt
smtpd_tls_key_file = /etc/ssl/private/mail.example.com.key
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_protocols = !SSLv2, !SSLv3, !TLSv1, !TLSv1.1
smtpd_tls_mandatory_ciphers = high

# SASL Authentication
smtpd_sasl_auth_enable = yes
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_security_options = noanonymous

# Denial of Service Protections
smtpd_client_connection_count_limit = 10
smtpd_client_connection_rate_limit = 30
smtpd_client_message_rate_limit = 100
smtpd_error_sleep_time = 1s
smtpd_soft_error_limit = 10
smtpd_hard_error_limit = 20
message_size_limit = 10485760

# Information Disclosure Mitigations
disable_vrfy_command = yes
smtpd_helo_required = yes
strict_rfc821_envelopes = yes
```
