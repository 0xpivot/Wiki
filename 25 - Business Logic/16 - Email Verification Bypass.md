---
tags: [vapt, business-logic, identity, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.16 Email Verification Bypass"
---

# 25.16 — Email Verification Bypass

## What is it?
Applications use **Email Verification** to establish a baseline of trust. It proves that the user controls the email address they are claiming to own. This is critical for password resets, preventing spam, and establishing corporate identity (e.g., "Only `@google.com` emails can join this workspace").

**Email Verification Bypass** occurs when the application's logic is flawed in how it enforces or tracks the verification state. An attacker can register an account, skip or trick the verification step, and gain access to features restricted to "verified" users, or worse, gain access to corporate networks by claiming an email address they do not actually own.

Think of it like applying for a passport. The government asks for your birth certificate (Email Verification). You say, "I don't have it right now, can I just go into the back room and wait?" The clerk says "Sure," and points you to the waiting room. However, the waiting room is the same room where they print the passports, and no one inside the room checks if you actually showed your certificate at the front desk.

## ASCII Diagram
```text
================================================================================
                    EMAIL VERIFICATION BYPASS (Pre-Auth)
================================================================================

[Expected Workflow]
1. POST /register {"email": "ceo@target.com"}
2. Server sets `verified = false`. Sends email with 6-digit code.
3. UI blocks access to the dashboard until code is entered.

[The Exploit (Forced Browsing)]
Attacker knows `verified = false`, but ignores the UI.
Attacker sends: GET /api/dashboard
                 Cookie: session=xyz

[Backend Flaw]
Server says: "Valid session cookie! Here is the dashboard data!"
(The backend FORGOT to check `if (user.verified == true)` on the dashboard endpoint!)

[Result: Attacker accesses the system without ever reading the email!]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **The Pre-Auth Bypass:** 
     - Register an account with an email you control.
     - DO NOT click the verification link in your email.
     - Look at the UI. It probably says "Please verify your email."
     - Try to forcefully navigate to `/dashboard`, `/profile`, or use Burp Suite to send `POST /api/create_item`. If the API endpoints allow you to perform actions, the verification is only enforced on the frontend UI.
  2. **The Post-Auth Email Change (Critical):**
     - Register an account with an email you control: `attacker@gmail.com`.
     - Verify it. Your account is now `verified=true`.
     - Go to your profile settings. Change your email to a high-value target: `ceo@target.com`.
     - Does the application immediately set `verified=false` upon changing the email?
     - If the application updates the email to `ceo@target.com` but leaves `verified=true`, you have just bypassed verification and stolen a corporate identity!
  3. **Response Manipulation:**
     - Intercept the `GET /api/user/me` request that the frontend uses to check verification status.
     - The server responds `{"verified": false}`.
     - Use Burp Intercept to modify the *response* to `{"verified": true}`. 
     - If the frontend drops the verification wall, and the backend doesn't re-check, you win.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit the "Post-Auth Email Change" flaw.
  1. Target application: A bug bounty platform that automatically grants access to private company programs if your email ends in `@company.com`.
  2. Create an account with `hacker@gmail.com`.
  3. Verify `hacker@gmail.com` using the link sent to your inbox.
  4. Your database record is now: `{email: "hacker@gmail.com", verified: true}`.
  5. Go to Account Settings -> Change Email.
  6. Submit `admin@company.com`.
  7. The application sends a verification link to `admin@company.com` (which you don't control).
  8. *However*, the developer wrote the logic poorly: `UPDATE users SET email = 'admin@company.com' WHERE id = 1`. 
  9. The developer forgot to write `verified = false`.
  10. You refresh the page. The application reads: `{email: "admin@company.com", verified: true}`.
  11. The platform automatically grants you access to all of `@company.com`'s private bug bounty programs.

- **Actual payloads:**
  **Mass Assignment during Registration (See [[25.15 Hidden API Parameters]]):**
  ```json
  {
    "email": "victim@target.com",
    "password": "Password1!",
    "email_verified": true,
    "status": "active"
  }
  ```

## Real-World Example
A security researcher tested a popular team-collaboration tool (similar to Slack). The tool allowed anyone with a `@domain.com` email address to automatically join that company's internal workspace. The researcher discovered that during the OAuth login process with Google, the application read the Google account's primary email, but if the Google account had a secondary "Recovery Email" listed, the application sometimes merged them. The researcher added the target company's CEO email as their unverified recovery email in Google. When they logged into the collaboration tool via Google OAuth, the tool extracted the unverified recovery email, assumed Google had verified it, and instantly dropped the researcher into the target company's highly confidential internal workspace.

## How to Fix It
- **Developer remediation:**
  1. **Strict Backend Enforcement:** Every single API endpoint must verify the user's state. Middleware should be used: `if (!user.isEmailVerified) return 403 Forbidden;`.
  2. **State Revocation on Change:** If a user changes their email address, the backend MUST immediately and atomically set `verified = false` before updating the email column.
  3. **Verification Tokens:** Do not rely on sequential integers for verification codes (e.g., `123456`) unless heavy rate-limiting is applied (See [[25.12 Rate Limit Bypass for Votes / Likes]]). Use cryptographically secure, long random tokens sent via email links.

## Chaining Opportunities
- This vuln + [[25.15 Hidden API Parameters]] → Injecting `is_verified=true` during registration.
- This vuln + [[24.01 What is Open Redirect?]] → Stealing the verification token by manipulating the callback URL in the verification email.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.17 Phone Number Verification Bypass]]
