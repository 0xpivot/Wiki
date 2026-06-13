---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.12 Enumerating SMTP VRFY EXPN"
---

# 12 - Enumerating SMTP VRFY EXPN

## Introduction

The Simple Mail Transfer Protocol (SMTP) is the beating heart of email routing on the Internet and internal corporate networks. Designed in the early days of the Internet, SMTP was built with functionality and reliability in mind, with security introduced much later as a patchwork of extensions (e.g., TLS, SPF, DKIM, DMARC). 

For penetration testers and red teamers, an internal or external SMTP server represents a massive intelligence goldmine. Through built-in protocol commands, an attacker can enumerate valid user accounts, verify email addresses, identify distribution list memberships, and discover the underlying network architecture. This enumeration is critical for setting up targeted phishing campaigns, brute-forcing portals, or spraying credentials across internal domains.

This document explores the mechanics of SMTP, focusing heavily on the `VRFY` and `EXPN` commands, and details how to extract intelligence from poorly configured mail servers.

---

## Protocol Deep Dive: SMTP Mechanics

SMTP operates primarily over the following TCP ports:
- **Port 25:** Unencrypted default routing port. Used for relaying messages between mail servers (MTA to MTA).
- **Port 465:** Originally SMTPS (Implicit SSL). Deprecated but still widely encountered.
- **Port 587:** Message Submission port. Modern standard for email clients (MUA) sending mail to servers, enforcing STARTTLS for encryption.

SMTP uses a plaintext, command-and-response format. An attacker connects to the server and issues text commands. The server responds with 3-digit numerical codes, similar to HTTP or FTP.

### Core SMTP Commands
Before understanding enumeration, one must grasp the basic SMTP transaction flow:
1. `HELO` / `EHLO`: The client identifies itself to the server. `EHLO` is the extended version, which prompts the server to list all the advanced features it supports (like `STARTTLS`, `AUTH`, `PIPELINING`).
2. `MAIL FROM:` Specifies the sender's email address.
3. `RCPT TO:` Specifies the recipient's email address.
4. `DATA`: Signals the beginning of the email body and headers. Concluded by a single period (`.`) on a line by itself.
5. `QUIT`: Terminates the session.

### The VRFY and EXPN Commands

The primary commands used for reconnaissance are `VRFY` (Verify) and `EXPN` (Expand). These commands were originally designed to help mail administrators debug routing issues and allow servers to check if a user actually existed before accepting a large payload.

- **VRFY (Verify):** Used to verify whether a specific user mailbox exists on the server.
  - *Command:* `VRFY sanchit`
  - *Valid Response:* `250 2.1.5 Sanchit <sanchit@corporate.local>`
  - *Invalid Response:* `550 5.1.1 User unknown`

- **EXPN (Expand):** Used to expand a mailing list or alias. If a mailing list is queried, the server will respond with every individual email address contained within that alias.
  - *Command:* `EXPN all-engineers`
  - *Valid Response:* 
    `250-2.1.5 John Doe <jdoe@corporate.local>`
    `250-2.1.5 Jane Smith <jsmith@corporate.local>`
    `250 2.1.5 Admin <admin@corporate.local>`

---

## ASCII Diagram: SMTP Enumeration Flow

```text
+-----------------------------------------------------------------------------------+
|                        SMTP ENUMERATION ATTACK FLOW                               |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +----------------+                                        +-------------------+  |
|  |                | ---- (1) TCP SYN (Port 25) ----------> |                   |  |
|  |                | <--- (2) TCP SYN-ACK ----------------- |                   |  |
|  |    Attacker    | ---- (3) TCP ACK --------------------> |    SMTP Server    |  |
|  |                |                                        |   (Postfix/Exim/  |  |
|  |                | <--- (4) 220 mail.corp.local ESMTP --- |    Exchange)      |  |
|  |                | ---- (5) HELO attacker.com ----------> |                   |  |
|  |                | <--- (6) 250 mail.corp.local Hello --- |                   |  |
|  |                |                                        |                   |  |
|  |    [PHASE 1]   | ---- (7) VRFY admin -----------------> |                   |  |
|  |   Enumerating  | <--- (8) 250 Admin <admin@corp.com> -- |  (Valid User)     |  |
|  |    Users       |                                        |                   |  |
|  |                | ---- (9) VRFY fakeuser123 -----------> |                   |  |
|  |                | <--- (10) 550 User unknown ----------- |  (Invalid User)   |  |
|  |                |                                        |                   |  |
|  |    [PHASE 2]   | ---- (11) EXPN it-admins ------------> |                   |  |
|  |   Expanding    | <--- (12) 250-alice@corp.com --------- |  (List Expanded)  |  |
|  |    Aliases     | <--- (13) 250-bob@corp.com ----------- |                   |  |
|  +----------------+                                        +-------------------+  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## Enumeration Methodology

### 1. Banner Grabbing and Feature Discovery
Connect to the server to grab the banner, which usually reveals the software type (e.g., Postfix, Sendmail, Microsoft Exchange) and OS version.

```bash
nc -nv 10.10.10.25 25
```
*Output:*
```text
(UNKNOWN) [10.10.10.25] 25 (smtp) open
220 mail.target.local ESMTP Postfix (Ubuntu)
```

Issue the `EHLO` command to see what features are supported.
```bash
EHLO attacker.local
```
*Output:*
```text
250-mail.target.local
250-PIPELINING
250-SIZE 10240000
250-VRFY
250-ETRN
250-STARTTLS
250-ENHANCEDSTATUSCODES
250-8BITMIME
250 DSN
```
*Note the presence of `250-VRFY` indicating the command is active.*

### 2. Manual VRFY and EXPN Testing
Manually typing commands helps verify if the server is actively protecting against enumeration or if it allows unlimited queries.

```bash
VRFY root
250 2.1.5 root <root@mail.target.local>

VRFY invaliduser
550 5.1.1 <invaliduser>: Recipient address rejected: User unknown in local recipient table

EXPN support
250-2.1.5 helpdesk@target.local
250 2.1.5 oncall@target.local
```

### 3. RCPT TO User Enumeration
If `VRFY` and `EXPN` are disabled (which is common in modern setups), attackers can use the `RCPT TO` command. You begin an email transaction and observe the server's response to the `RCPT TO` command.

```text
HELO attacker.local
MAIL FROM:<test@attacker.local>
250 2.1.0 Ok
RCPT TO:<admin@target.local>
250 2.1.5 Ok                <--- (User Exists)
RCPT TO:<fakeuser@target.local>
550 5.1.1 User unknown      <--- (User Does Not Exist)
```

### 4. Automated Enumeration Tools

Manually testing hundreds of users is inefficient. Several tools automate this process perfectly.

**smtp-user-enum:**
A classic tool written specifically for this task. It supports testing via VRFY, EXPN, or RCPT TO.

*Testing via VRFY:*
```bash
smtp-user-enum -M VRFY -U /usr/share/wordlists/metasploit/unix_users.txt -t 10.10.10.25
```

*Testing via RCPT TO:*
```bash
smtp-user-enum -M RCPT -U /usr/share/seclists/Usernames/Names/names.txt -t 10.10.10.25
```

**Nmap NSE Scripts:**
Nmap possesses excellent scripts for SMTP enumeration, including open-relay checking.
```bash
nmap -p 25 --script smtp-enum-users.nse --script-args smtp-enum-users.methods={VRFY} 10.10.10.25
nmap -p 25 --script smtp-commands 10.10.10.25
nmap -p 25 --script smtp-open-relay 10.10.10.25
```

**Metasploit:**
```bash
msfconsole
use auxiliary/scanner/smtp/smtp_enum
set RHOSTS 10.10.10.25
set USER_FILE /usr/share/wordlists/rockyou.txt
run
```

### 5. Open Relay Testing
An Open Relay is an SMTP server configured in such a way that it allows anyone on the internet to send emails through it, to any destination, without authentication. Spammers heavily target open relays.

To test manually:
```text
HELO attacker.local
MAIL FROM:<spoofed@CEO.com>
RCPT TO:<attacker-personal-email@gmail.com>
DATA
Subject: Open Relay Test
This is a test.
.
QUIT
```
If the server accepts the `RCPT TO` to an external domain and queues the message, it is an open relay.

---

## Defense, Hardening, and Mitigation

Protecting SMTP requires configuring the Mail Transfer Agent (MTA) strictly.

1. **Disable VRFY and EXPN:** 
   These commands are not needed for modern email delivery. 
   - In **Postfix**, add the following to `main.cf`: 
     `disable_vrfy_command = yes`
   - In **Sendmail**, configure the `PrivacyOptions` in `sendmail.mc`: 
     `O PrivacyOptions=authwarnings,novrfy,noexpn,restrictqrun`

2. **Prevent RCPT TO Enumeration (Tarpitting):**
   If attackers fall back to `RCPT TO`, you can implement tarpitting. Tarpitting deliberately slows down the server's response after a certain number of errors or `RCPT TO` requests in a single session. This makes dictionary attacks unfeasibly slow.

3. **Disable Open Relaying:**
   Strictly configure the MTA to only relay mail for authenticated users, or IP addresses originating from within the trusted internal network (`mynetworks` in Postfix). External connections should only be allowed to send mail destined *for* the local domain.

4. **Catch-All Addresses (Double-edged Sword):**
   Some organizations configure a "catch-all" address. Any email sent to `<anything>@domain.com` returns a valid `250 OK`. This breaks enumeration tools because every query looks valid. However, this creates a massive spam problem for the organization.

5. **Rate Limiting and IPS:**
   Implement Intrusion Prevention Systems to detect and drop connections performing anomalous volumes of SMTP commands per minute.

---

## Chaining Opportunities
- Valid internal usernames enumerated via `VRFY` can be fed directly into password spraying attacks against Active Directory, VPN portals, or SSH. (See [[82 - Lateral Movement via SSH and WinRM]]).
- If `EXPN` reveals that `it-support@corp.local` points to external contractor email addresses, social engineering and phishing attacks can be hyper-targeted.
- Successful open relay findings can be used to bypass external email filters (SPF/DKIM) by sending phishing emails directly from the internal corporate network MTA.

## Related Notes
- [[11 - Enumerating FTP and TFTP]]
- [[13 - Vulnerability Scanning with Nessus and OpenVAS]]
- [[14 - Active vs Passive Reconnaissance in Networks]]
- [[82 - Lateral Movement via SSH and WinRM]]
