---
tags: [vapt, business-logic, saas, beginner]
difficulty: beginner
module: "25 - Business Logic"
topic: "25.05 Free Trial Abuse"
---

# 25.05 — Free Trial Abuse

## What is it?
Software-as-a-Service (SaaS) platforms frequently offer a "14-day Free Trial" to attract users to their premium tiers. Business logic dictates that a user (or a company) is only entitled to one free trial. 

Free Trial Abuse occurs when an attacker exploits logic flaws in the user identification or billing process to continuously extend their free trial indefinitely, effectively gaining permanent access to a premium service without ever paying.

While creating thousands of email addresses to sign up for thousands of trials is technically "abuse," it is generally considered out-of-scope for Bug Bounties. True Free Trial Abuse involves exploiting a logic flaw *within a single account* or bypassing the mechanisms meant to tie an identity to a trial period.

Think of it like getting a free sample at a bakery. The rule is "One sample per customer." If you put on a fake mustache, walk out, and walk back in to get another sample, that's just normal fraud (out-of-scope). But if you find a way to reach over the counter and reset the baker's "Samples Given" counter to zero, so you can stand there and eat unlimited samples without a disguise, that is a logic flaw.

## ASCII Diagram
```text
[Expected Logic]
Day 1: User signs up -> Trial ends on Day 14.
Day 15: User tries to use premium feature -> Server blocks access.

[Flawed Logic (Downgrade/Upgrade Bypass)]
Day 13: User clicks "Cancel Subscription". Server sets account to "Free".
Day 14: User clicks "Start Free Trial".
       │
[Server Logic]
Does user have an active trial? NO. (They cancelled it yesterday).
Action: Start new 14-day trial!
       ▼
[Result]
Attacker loops this process every 13 days, gaining infinite premium access on one account.
```

## How to Find It
- **Manual steps:**
  1. Sign up for a free trial on the target application.
  2. Identify how the application tracks the trial (e.g., a database timestamp, a JWT token claim, a Stripe billing ID).
  3. Test the Subscription Lifecycle:
     - Cancel the trial. Does the UI let you start a *new* trial?
     - Downgrade to a free tier, then attempt to upgrade back to the trial tier.
  4. Test parameter manipulation: Intercept the request that starts the trial. Does it include a parameter like `trial_days=14`? Change it to `trial_days=9999`.
  5. Test email aliases (if the app relies solely on email for identity tracking): Sign up with `victim@gmail.com`. When the trial ends, sign up with `victim+1@gmail.com`. If the app treats it as a new user but links to the same workspace, the identity tracking is flawed.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Intercept the API request made when clicking "Start Trial".
  2. Look for any user-controlled inputs governing time.
  3. Change `"plan": "premium_trial"` to `"plan": "premium"` with `"price": 0` (See [[25.02 Price Manipulation in E-commerce]]).
  4. If the trial relies on a Stripe/Braintree token, cancel the trial in the SaaS app, but intercept the cancellation request and prevent it from reaching the payment provider. Desyncing the SaaS app state from the Payment Gateway state often leads to infinite premium access.

- **Actual payloads:**
  **Manipulating Trial Duration Parameters:**
  ```json
  {
    "user_id": "1004",
    "plan_id": "pro",
    "trial_length_days": 3650
  }
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request (Downgrade/Upgrade Loop):**
  ```http
  POST /api/billing/subscribe HTTP/1.1
  Host: saas.target.com
  
  {"plan": "enterprise_trial"}
  ```
  *(Server grants 14 days. Attacker immediately sends:)*
  ```http
  POST /api/billing/cancel HTTP/1.1
  Host: saas.target.com
  ```
  *(Server sets trial_active = false. Attacker sends subscribe again. Server grants 14 more days!)*

## Real-World Example
A security researcher was testing a cloud video editing platform. The platform offered a 7-day trial of the "Pro" tier. The researcher noticed that the trial expiration date was stored inside the user's JWT (JSON Web Token) that the client browser used to authenticate API requests. While the JWT signature prevented the researcher from tampering with the date directly, they discovered a logic flaw in the "Sync Account" feature. If the user changed their timezone in their profile settings, the backend re-issued a new JWT. By intercepting the timezone update and injecting a timezone offset of `-9999 hours`, the backend calculated the new trial expiration date relative to the manipulated timezone, effectively extending the trial by a year.

## How to Fix It
- **Developer remediation:**
  1. **Strict Identity Tracking:** A trial must be tied to a rigid, immutable unique identifier. Do not rely solely on email addresses (which can use `+` aliases). Track trials by Credit Card Fingerprint, Phone Number, or rigid Workspace IDs.
  2. **Immutable Timestamps:** The `trial_start` and `trial_end` dates must be generated entirely on the server-side, stored securely in the database, and never derived from client-side input or relative timezone calculations.
  3. **State Integrity:** Once an account uses a trial, a boolean flag (`has_used_trial = true`) must be permanently flipped in the database.

## Chaining Opportunities
- This vuln + [[25.07 Workflow Bypass (skipping payment step)]] → Bypass the step that requires entering a credit card to begin the trial, allowing mass creation of trial accounts without financial verification.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.06 Account Limit Bypass]]
