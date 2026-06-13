---
tags: [vapt, business-logic, identity, advanced]
difficulty: advanced
module: "25 - Business Logic"
topic: "25.17 Phone Number Verification Bypass"
---

# 25.17 — Phone Number Verification Bypass

## What is it?
Similar to Email Verification Bypass, **Phone Number Verification Bypass** exploits flaws in how an application confirms a user's possession of a mobile device. This is heavily used in 2FA (Two-Factor Authentication), account recovery, and anti-fraud measures (e.g., "One account per phone number").

Bypassing this mechanism usually involves tricking the logic that handles the One-Time Password (OTP) verification, bypassing the rate limits that protect the OTP from brute-forcing, or manipulating the API endpoints to accept a verified status without ever seeing the SMS.

Think of it like a bouncer at a club who asks for the secret password. The bouncer texts the password to your friend's phone. You don't have your friend's phone. However, you notice the bouncer is extremely forgetful. You just rapidly yell 10,000 different words at him. Because he doesn't stop you or kick you out for guessing wrong, eventually you yell the correct word, and he lets you in. This is an OTP brute-force logic flaw.

## ASCII Diagram
```text
================================================================================
                    PHONE VERIFICATION BYPASS (OTP Brute Force)
================================================================================

[The OTP Mechanism]
Server sends a 4-digit code (0000-9999) to Victim's Phone.
There are only 10,000 possible combinations.

[The Logic Flaw]
The developer failed to implement a Rate Limit on the /verify_otp endpoint.

[The Exploit]
Attacker uses Burp Suite Intruder.
Sends 10,000 requests in 30 seconds.

POST /verify_otp {"code": "0000"} ──> 400 Bad Request
POST /verify_otp {"code": "0001"} ──> 400 Bad Request
...
POST /verify_otp {"code": "4892"} ──> 200 OK! (Session Granted!)

[Result: Attacker logs into Victim's account without having their phone.]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **OTP Brute Force:** Trigger an SMS code to your own phone. Do not look at the code. Go to the verification page and enter `0000`. Intercept the request in Burp Suite. Send it to Intruder. Set the payload to Numbers (0000 to 9999). Run the attack. If it succeeds, the OTP mechanism is fundamentally broken.
  2. **Response Manipulation:** Intercept the `POST /verify_otp` request. The server replies `{"success": false}`. Use Burp Intercept to change the response to `{"success": true}`. If the frontend JavaScript blindly trusts this and logs you in, and the backend doesn't re-verify the session token, you win.
  3. **The Pre-Auth Bypass:** (Similar to 25.16). Do not verify the phone. Try to access `/api/dashboard` directly.
  4. **Concurrent Requests (Race Condition):** If there is a rate limit (e.g., "Max 3 tries"), try sending 50 guesses simultaneously using the HTTP/2 Single Packet attack (See [[09 - Race Conditions in Financial Transactions]]).
  5. **Endpoint Confusion:** Sometimes `POST /api/v1/verify` has rate limiting, but the older `POST /api/v0/verify` or the mobile endpoint `POST /api/mobile/verify` forgot to implement the rate limit.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's explore an advanced logic flaw: **OTP Reusability**.
  1. The application requires phone verification to transfer funds.
  2. You initiate a transfer of $10 to your own alternate account.
  3. The server sends an OTP: `8812`.
  4. You enter `8812` and intercept the request. You forward it. The transfer succeeds.
  5. You initiate a new transfer, this time for $10,000.
  6. The server asks for an OTP. It sends a new one to your phone.
  7. **The Bypass:** Instead of entering the new OTP, you enter the *old* OTP: `8812`.
  8. The developer wrote: `if (submitted_otp == user.last_otp_generated)`. But what if the developer wrote `SELECT * FROM otps WHERE code = '8812' AND user_id = 42` and forgot to check if the code was already marked as "used"? 
  9. The server accepts the old, intercepted OTP and authorizes the $10,000 transfer.

- **Actual payloads:**
  **Brute-Forcing a 4-digit JSON OTP:**
  ```json
  {"phone_number": "+1234567890", "otp_code": "§0000§"}
  ```

## Real-World Example
A Bug Bounty hunter targeted a cryptocurrency wallet app. When recovering a password, the app sent a 6-digit OTP to the user's phone. A 6-digit OTP has 1 million combinations, which usually takes too long to brute force before the token expires (usually 10 minutes). However, the hunter noticed the app had a "Resend OTP" button. When clicked, the server generated a *new* 6-digit OTP, but crucially, it did not invalidate the *previous* OTP. 

The hunter wrote a script that clicked "Resend OTP" 1,000 times in 1 minute. The victim's phone received 1,000 SMS messages. More importantly, there were now 1,000 *different* valid 6-digit codes active simultaneously for that account. This mathematically reduced the brute-force space from 1-in-a-million to 1-in-1,000. The hunter then brute-forced the verification endpoint. Within seconds, one of their guesses matched one of the 1,000 active codes. The hunter bypassed the 2FA and stole the cryptocurrency.

## How to Fix It
- **Developer remediation:**
  1. **Strict Rate Limiting & Account Lockout:** OTP endpoints must have aggressive, IP-agnostic rate limiting. If an account experiences 5 incorrect OTP guesses, the OTP mechanism must be locked for that account for 15 minutes, rendering brute-forcing mathematically impossible.
  2. **OTP Invalidation:** The moment a new OTP is generated, the previous OTP for that user MUST be marked as invalid/deleted in the database.
  3. **State Invalidation on Use:** The moment an OTP is successfully used, it MUST be marked as consumed. It cannot be used for a subsequent transaction.

## Chaining Opportunities
- This vuln + [[12 - Rate Limit Bypass for Votes _ Likes]] → Bypassing the 5-attempt rate limit by rotating IP headers allows you to brute force the entire 10,000 OTP space.
- This vuln + Account Takeover (ATO) → Bypassing SMS 2FA is the final step in completely taking over a victim's account.

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[16 - Email Verification Bypass]]
