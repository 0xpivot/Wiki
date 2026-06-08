---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.03 Credential Stuffing"
---

# 16.03 — Credential Stuffing

## What Is Credential Stuffing?

```
CONTEXT:
  Billions of username:password pairs are available from data breaches
  (LinkedIn 2016, Adobe 2013, RockYou2021 → 8.4 billion credentials!)
  
  FACT: ~65% of people reuse passwords across sites!
  
CREDENTIAL STUFFING:
  Take a leaked credential list (user:pass pairs)
  → Try EACH PAIR against a TARGET SITE
  → If someone reused their LinkedIn password on your target... 
     you get in WITHOUT cracking anything!
  
DIFFERENCE FROM BRUTE FORCE:
  Brute force: One user, many passwords (guessing)
  Cred stuffing: Many users, their known passwords (trying known combos)
  
  Credential stuffing has FAR higher success rates because:
  - Real passwords users actually used
  - Targets specific person's known credentials
  - Password reuse is extremely common
```

---

## Breach Databases and Sources

```
PUBLIC/SEMI-PUBLIC SOURCES:
  HaveIBeenPwned (haveibeenpwned.com):
    - Check if email was in a breach
    - API available for checking
    - Does NOT provide the actual passwords
    
  breach-parse (GitHub):
    - Tools for organizing breach data
    
  dehashed.com:
    - Searchable breach database (paid)
    - Useful for authorized OSINT on a target organization
    
  scylla.sh / intelx.io:
    - Search across many breaches

WORDLISTS WITH KNOWN PASSWORDS:
  /usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt
  Contains 14 million real passwords from RockYou breach!
  
CORPORATE OSINT:
  Find employees via LinkedIn
  Check breached databases for their work emails
  Try found passwords against corporate VPN/webmail/Citrix
```

---

## Attack Setup

```bash
# BASIC CREDENTIAL STUFFING WITH HYDRA:
# Format: username:password per line in credentials.txt

hydra -C credentials.txt target.com https-post-form \
  "/login:email=^USER^&password=^PASS^:F=Login failed" \
  -t 5 -w 5

# CREATE CREDENTIAL LIST FROM SEPARATE LISTS:
paste -d: users.txt passwords.txt > credentials.txt
# → alice:password123
#   bob:hunter2
#   carol:qwerty

# BURP INTRUDER — PITCHFORK MODE:
# Position 1: §username§
# Position 2: §password§
# Payload set 1: usernames.txt
# Payload set 2: corresponding_passwords.txt
# → Each pair tried together (not all combinations!)
```

---

## Slow and Distributed Stuffing (Evading Detection)

```
PROBLEM WITH FAST STUFFING:
  - Triggers rate limiting quickly
  - IP gets blocked
  - Security alerts fire on many failed logins
  
SLOW STUFFING TACTICS:
  1. Low rate: 1 request per 3-5 seconds
  2. Rotate user agents (look like different browsers)
  3. Rotate IP addresses (proxy pool, Tor, cloud IPs)
  4. Distribute across many source IPs
  5. Time-of-day: less monitoring at 3 AM
  
IMPORTANT ETHICAL NOTE:
  In authorized VAPT tests, confirm scope explicitly!
  - Is credential stuffing in scope?
  - Are production accounts in scope? (usually NO!)
  - Use test accounts or clearly agreed scope
  
IN BUG BOUNTY:
  Usually out of scope or requires specific permission
  Check the program's policy before attempting!
```

---

## Fix

```
DEFENSES:
  ✓ Multi-Factor Authentication (MFA) — #1 defense!
    Stuffed credential = useless without second factor
    
  ✓ Credential breach monitoring
    Check user passwords against HaveIBeenPwned API
    Prompt users to change if found in breach
    
  ✓ Rate limiting — limit login attempts per IP
  
  ✓ Behavioral anomaly detection
    Same IP trying many different usernames = stuffing!
    Flag unusual login patterns (new country, device fingerprint)
    
  ✓ CAPTCHA — makes automation harder
  
  ✓ Passwordless / passkeys — eliminates reuse entirely
```

---

## Related Notes
- [[01 - Username Enumeration]] — find valid accounts first
- [[02 - Password Brute Force]] — guessing vs stuffing comparison
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
