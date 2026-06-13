---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.15 MFA Bypass — SIM Swapping"
---

# 16.15 — MFA Bypass: SIM Swapping

## What Is SIM Swapping?

```
SMS-BASED 2FA WEAKNESS:
  Many apps send OTP via SMS to the user's phone number
  If attacker controls the victim's phone number → they receive the SMS!
  
SIM SWAP ATTACK:
  Attacker calls victim's mobile carrier (social engineering)
  "Hi, I lost my phone. Please transfer my number to this new SIM card"
  
  If carrier social engineering succeeds:
  → Victim's number transferred to attacker's SIM
  → All SMS messages to victim's number → go to attacker's phone
  → SMS OTPs → attacker receives them → bypasses SMS-based 2FA!
  
REAL WORLD EXAMPLES:
  - Twitter CEO Jack Dorsey: SIM-swapped (2019)
  - Cryptocurrency accounts: Frequent target (high-value)
  - Regular accounts: Targeted when attacker knows value
```

---

## Why SMS 2FA Is Weak

```
SMS 2FA IS VULNERABLE TO:
  1. SIM Swapping (social engineering the carrier)
  2. SS7 Attacks (telecom protocol vulnerabilities)
     → Intercept SMS globally without SIM swap
     → Requires telecom network access (nation-state/criminal)
  3. Phone malware → intercept SMS on victim's device
  4. SIM cloning (requires physical access to SIM)
  5. Carrier insider threats (telecom employee complicity)
  
NIST SP 800-63B (2017):
  Marked SMS OTP as "RESTRICTED" — not recommended for high-security use
  
WHY COMPANIES STILL USE IT:
  - Much better than no MFA at all
  - Users have phones (no app installation needed)
  - High adoption rate (TOTP apps have 70% dropout rate in setup)
```

---

## VAPT Relevance

```
IN A PENETRATION TEST:
  SIM swapping = out of scope (requires criminal activity against carrier)
  But the FINDING you should report is:
  
  "Application uses SMS-based OTP for MFA, which is susceptible to
   SIM swapping attacks. Recommend upgrading to TOTP (authenticator app)
   or FIDO2 (hardware key) for higher-security accounts."
  
IN BUG BOUNTY:
  You cannot SIM swap someone for a bug bounty
  But: If the app supports SMS-only MFA for admin accounts → noteworthy
  
IN RED TEAM ENGAGEMENTS:
  May be explicitly in scope if client wants to test
  Usually requires legal authorization AND coordination with carrier
```

---

## Evaluating 2FA Method Strength

```
MFA STRENGTH RANKING (weakest to strongest):
  
  1. SMS OTP (weakest):
     ✗ SIM swap, SS7 intercept, malware
     
  2. Email OTP:
     ✗ Email account compromise
     
  3. Time-based OTP (TOTP — Google Authenticator):
     ✓ Better than SMS
     ✗ Still susceptible to phishing (real-time OTP relay attacks)
     
  4. Push notification apps (Duo, Microsoft Authenticator):
     ✓ Out-of-band, harder to phish
     ✗ Push bombing (fatigue attacks — send many pushes, user accepts)
     
  5. FIDO2 / WebAuthn / Hardware Keys (strongest):
     ✓ Phishing-resistant (bound to origin)
     ✓ No OTP to intercept
     ✓ Physical key required
     ✗ Cost, setup complexity, key loss
     
REPORT RECOMMENDATION:
  "Upgrade high-privilege accounts to FIDO2/WebAuthn"
  "Consider TOTP as minimum for all user accounts"
  "Provide SMS as fallback only, not primary MFA"
```

---

## Push Notification Fatigue (MFA Bombing)

```
RELATED ATTACK: MFA BOMBING / PUSH FATIGUE:

1. Attacker has victim's password (compromised)
2. Attacker initiates login many times
3. Victim's phone receives many "Approve this login?" push notifications
4. Victim gets annoyed by constant notifications
5. Victim accidentally (or frustratedly) taps "Approve"!
6. Attacker is in!
   
Real example: Uber breach (2022) — employee approved push after social
engineering convinced them it was legitimate
   
DEFENSES:
  - Number matching: show a code on login page, require same code in push
  - Context in push: "Login attempt from IP x.x.x.x, Russia"
  - Limit login attempts before requiring additional verification
  - Alert on multiple rejected pushes
```

---

## Fix

```
RECOMMENDATIONS FOR APPLICATIONS:
  ✓ Offer TOTP (authenticator app) — better than SMS
  ✓ Support FIDO2/WebAuthn for high-security users
  ✓ If SMS used: additional device-binding or anomaly detection
  ✓ For push-based MFA: implement number matching to prevent fatigue attacks
  ✓ Allow users to upgrade their MFA method (SMS → TOTP → hardware key)
```

---

## Related Notes
- [[11 - MFA Bypass Response Manipulation]] — response-based bypass
- [[13 - MFA Bypass Brute Force OTP]] — brute force OTP codes
- [[28 - Defense Rate Limiting Lockout MFA]] — MFA configuration guidance
