---
tags: [vapt, business-logic, fraud, beginner]
difficulty: beginner
module: "25 - Business Logic"
topic: "25.11 Referral Abuse / Self-Referral"
---

# 25.11 — Referral Abuse / Self-Referral

## What is it?
Marketing departments love Referral Programs: "Invite a friend! When they sign up and spend $10, you both get $10 in credit!"

**Referral Abuse** occurs when the application's business logic fails to enforce strict identity separation between the Referrer (the person inviting) and the Referee (the person joining), or fails to enforce the "spending" prerequisite before issuing the reward. 

Attackers exploit this by acting as both the Referrer and the Referee (Self-Referral). They create a massive loop, inviting themselves using fake email addresses or email aliases, generating infinite store credit or premium access without ever bringing real value or new customers to the business.

Think of it like a gym offering a free month if you bring a new friend. You walk in, point to a mannequin wearing a hat, say "This is my friend Bob," and the gym hands you a free month because they never actually checked if Bob was a real, paying human being.

## ASCII Diagram
```text
================================================================================
                        THE SELF-REFERRAL LOOP
================================================================================

[Attacker's Main Account] ──> Generates Link: https://app.com/join?ref=ATTACKER1

[The Exploit Loop]
       ┌─────────────────────────────────────────────────────────────┐
       │ 1. Attacker opens Incognito Window.                         │
       │ 2. Navigates to: https://app.com/join?ref=ATTACKER1         │
       │ 3. Signs up with: attacker+fake1@gmail.com                  │
       │ 4. Backend Logic Flaw:                                      │
       │    "A new user signed up! Give ATTACKER1 $10 credit!"       │
       │    (Backend forgot to require the new user to spend money!) │
       │ 5. Attacker abandons the fake account.                      │
       └─────────────────────────────────────────────────────────────┘

[Result]
Attacker repeats the loop 100 times. Main account gains $1000 in free credit.
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Find a referral feature in the application. Note your unique referral code or link.
  2. Log out or open a private browsing window.
  3. Sign up using your own referral link. Use an email alias (e.g., if your real email is `john@gmail.com`, sign up with `john+ref1@gmail.com`. Gmail routes both to the same inbox).
  4. Check the application's rules. Usually, it says "Friend must verify email and make a purchase."
  5. **Test the Prerequisites:** 
     - Does the main account get the reward immediately upon sign-up?
     - Does the main account get the reward after simply clicking the email verification link?
     - What if the new account makes a purchase using a fake credit card that gets declined? Does the system issue the reward before verifying the card cleared?
  6. **Test Identity Separation:** Does the system allow the referral if both accounts use the exact same IP address? What if both accounts use the exact same credit card for billing?

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a system that requires the new user to make a $5 purchase.
  1. Main Account (A) generates referral link.
  2. Attacker creates Fake Account (B) via the link.
  3. Fake Account (B) adds a $5 item to the cart.
  4. Fake Account (B) uses the new user welcome bonus (e.g., "$5 off your first order") to pay $0 for the item.
  5. The backend logic checks: "Did Account B make a purchase? Yes, an order exists."
  6. The backend issues $10 referral credit to Account A.
  7. Attacker repeats this infinitely.

- **Actual payloads:**
  *(This vulnerability relies heavily on workflow manipulation rather than specific payloads. However, automating it via scripts is common).*
  **Using Email Aliases for mass registration:**
  ```text
  attacker+001@gmail.com
  attacker+002@gmail.com
  ```
  **Using Catch-All Domains:**
  If you own `attacker.com`, you can set up a catch-all email rule.
  ```text
  randomword@attacker.com
  anotherword@attacker.com
  ```

## Real-World Example
A Bug Bounty hunter was analyzing a popular rideshare app. The app offered a $20 credit if you referred a friend and they took their first ride. The hunter found a separate logic flaw in the "Driver" application. The hunter signed up as a Driver. Then, using their personal account, they referred an alias account (`hunter+1@gmail.com`). The alias account requested a ride. The hunter, acting as the Driver, accepted the ride. The hunter drove 1 block, ended the ride, and charged the alias account $5. The backend system saw the alias account completed a ride. It issued the $20 referral bonus to the main account. The hunter paid $5 to themselves (minus platform fees) to generate $20 in free rides, an infinite money glitch.

## How to Fix It
- **Developer remediation:**
  1. **Strict Prerequisites:** Referral bonuses must *never* be issued on sign-up. They must be issued asynchronously, only after the referred user has generated actual, settled, non-refundable revenue for the business that exceeds the cost of the bonus.
  2. **Fraud Analytics (Device & IP Fingerprinting):** The backend must run analytics on referrals. If the Referrer and Referee share the same IP address, Browser User-Agent, or physical Device ID, the referral should be flagged for manual review or silently dropped.
  3. **Payment Identity Matching:** If Account A refers Account B, and Account B attempts to pay for their first order using the exact same Credit Card hash stored on Account A, the transaction must be blocked for fraud.
  4. **Alias Normalization:** Normalize emails before checking for duplicates (e.g., strip everything after the `+` sign for Gmail addresses).

## Chaining Opportunities
- This vuln + [[07 - Workflow Bypass (skipping payment step)]] → Skip the required payment step on the referred account to instantly trigger the reward on the main account.

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[04 - Discount_Coupon Abuse]]
