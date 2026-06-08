---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.14 MFA Bypass — Backup Code Abuse"
---

# 16.14 — MFA Bypass: Backup Code Abuse

## What Are Backup Codes?

```
BACKUP CODES:
  Emergency one-time-use codes given to user when they set up MFA
  Used when: phone lost, authenticator app deleted, SIM card gone
  
  Typical format:
  8xxxxxxx-xxxxxxxx (8-character segments)
  123456789         (10-digit code)
  XXXXX-XXXXX       (5+5 alphanumeric)
  
  Usually 8-10 codes provided at setup
  Each is single-use (should be)
  
IMPORTANCE:
  Backup codes = permanent bypass to MFA!
  If exposed, any of the codes can be used until all consumed
```

---

## Backup Code Vulnerabilities

### 1. Brute Force (No Rate Limit)

```
FORMAT ANALYSIS:
  If backup codes are numeric:
  6-digit: 1 million combos
  8-digit: 100 million combos
  
  If backup codes are short alphanumeric:
  6 chars (a-z0-9): 36^6 = 2.1 billion (harder but feasible with GPU)
  
TEST:
  1. Find the backup code entry endpoint
  2. Try submitting many codes
  3. Check for rate limiting
  4. If no lockout → brute force is possible
  
  POST /mfa/backup
  backup_code=§FUZZ§
  → Payload: 000000 to 999999
```

### 2. Codes Stored in Plaintext

```
WHERE THIS MATTERS:
  - If database is leaked (SQLi, breach) → all backup codes exposed
  - If admin panel shows backup codes → insider threat
  - If backup codes visible in HTTP response
  
TEST:
  Look at your own backup codes in the profile/security page
  Are they shown in plaintext after initial generation?
  (They should ONLY be shown once, at creation time)
  
  Check: can you request to view your backup codes again?
  → If yes: codes in plaintext in DB (should be hashed)
  
REPORTING:
  If backup codes are not hashed → Medium severity finding
  "Backup MFA codes stored in plaintext in the database"
```

### 3. Unlimited Code Regeneration

```
ATTACK SCENARIO:
  Attacker has compromised user's password (but not phone)
  
  If app allows regenerating backup codes with just a password:
  POST /account/security/regenerate-backup-codes
  (No current MFA required!)
  
  → Attacker regenerates codes → invalidates victim's old codes
  → Uses new codes → bypasses MFA!
  
TEST:
  1. Login with password (first factor) to pre-MFA state
  2. Try: GET/POST /account/generate-backup-codes
  → If accessible without completing MFA → VULNERABILITY!
  → Should require MFA completion or current password re-entry!
```

### 4. API Endpoints Exposing Codes

```
CHECK:
  /api/user/security/backup-codes    → GET should never return codes!
  /api/account/mfa/status           → may expose code count/status
  
  Codes should NEVER appear in:
  - API responses after initial generation
  - Server logs
  - Browser history (no GET params with codes!)
  - Error messages
```

---

## Fix

```
SECURE BACKUP CODE IMPLEMENTATION:
  
  1. GENERATION:
     - Use cryptographically random generation:
     import secrets
     codes = [secrets.token_urlsafe(10) for _ in range(10)]
     
  2. STORAGE:
     - Store HASHED, never plaintext:
     import bcrypt
     hashed = [bcrypt.hashpw(c.encode(), bcrypt.gensalt()) for c in codes]
     # Store hashed_codes in DB, show plaintext ONCE to user, then discard
     
  3. DISPLAY:
     - Show only once at creation
     - Never display again (can't recover — only regenerate)
     
  4. USAGE:
     - Hash incoming code → compare to stored hashes
     - Delete matching hash immediately after use
     
  5. REGENERATION:
     - Require completed MFA (not just password!) to regenerate
     - Or require re-authentication with authenticator app
     - Invalidate all old codes immediately on regeneration
     
  6. RATE LIMIT:
     - Treat same as OTP: limit attempts, lockout on abuse
```

---

## Related Notes
- [[11 - MFA Bypass Response Manipulation]] — other MFA bypasses
- [[12 - MFA Bypass Code Reuse]] — OTP reuse
- [[13 - MFA Bypass Brute Force OTP]] — brute force numeric codes
- [[15 - MFA Bypass SIM Swapping]] — physical-layer bypass
