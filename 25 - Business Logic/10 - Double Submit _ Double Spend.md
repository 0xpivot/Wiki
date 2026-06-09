---
tags: [vapt, business-logic, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.10 Double Submit / Double Spend"
---

# 25.10 — Double Submit / Double Spend

## What is it?
**Double Submit** (often called Double Spend in financial contexts) is a business logic flaw closely related to Race Conditions, but it doesn't always require microsecond-perfect concurrency. It occurs when an application fails to ensure that a specific, high-value action is executed exactly one time (Idempotency).

While Race Conditions exploit the timing gap *between* database queries, Double Submit exploits the lack of a tracking mechanism for the transaction itself. If a user clicks "Submit Payment" twice rapidly because their internet is slow, does the application charge them twice for the same cart? If an attacker captures a valid API request that spends a $10 gift card, and replays that identical request an hour later, does the application accept it again?

If the application processes the duplicate request without recognizing that it represents an action that has already been finalized, it suffers from a Double Submit flaw.

Think of it like depositing a physical check at a bank. You hand the teller a check for $100. They add $100 to your account and hand the check back to you by mistake. You walk to a different teller, hand them the exact same check, and they add another $100 to your account. The bank failed to stamp the check "VOID" (state tracking) or record the check's unique serial number (Idempotency Key).

## ASCII Diagram
```text
================================================================================
                        THE DOUBLE SUBMIT FLAW
================================================================================

[Attacker intercepts a valid transaction]
POST /redeem_gift_card
{"code": "GIFT-A1B2", "amount": 50}

[Server processes Request 1]
1. Is code GIFT-A1B2 valid? YES.
2. Add $50 to Attacker's Wallet.
3. [Flaw]: Forgets to mark GIFT-A1B2 as "used" in the database!

[Attacker sends the exact same request 5 minutes later]
POST /redeem_gift_card
{"code": "GIFT-A1B2", "amount": 50}

[Server processes Request 2]
1. Is code GIFT-A1B2 valid? YES. (Because it wasn't marked used!)
2. Add another $50 to Attacker's Wallet.
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify actions that should only happen once: submitting an order, redeeming a code, claiming a daily reward, voting in a poll, or creating an account.
  2. Intercept the HTTP request for that action in Burp Suite.
  3. Send the request to Repeater.
  4. Allow the first request to process normally. Verify the action succeeded (e.g., your account balance increased).
  5. Without changing anything, press "Send" again in Repeater.
  6. Analyze the response. If it succeeds again, you have a Double Submit vulnerability.
  7. **Network Lag Simulation:** In the web UI, try clicking the "Submit" button 10 times very rapidly before the page reloads.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a "Redeem Daily Reward" feature.
  1. The application allows you to click a button once per day to get 10 free coins.
  2. You intercept the request: `POST /api/rewards/claim_daily`.
  3. You send it to Burp Intruder.
  4. Set the payload type to "Null payloads" and set it to generate 100 requests.
  5. Start the attack.
  6. The server receives 100 identical requests. Because the developer didn't properly log the timestamp of the claim *before* issuing the reward, or didn't implement an idempotency key, the server processes all 100 requests sequentially.
  7. You receive 1,000 coins instead of 10.

- **Actual payloads:**
  **Replaying a POST request:**
  ```http
  POST /api/checkout/pay HTTP/1.1
  Host: shop.com
  Cookie: session=xyz
  
  cart_id=8812&payment_token=tok_visa_123
  ```
  *(If the server charges the card twice, it is a critical flaw).*

## Real-World Example
A Bug Bounty hunter was testing a peer-to-peer payment app (similar to Venmo). The app allowed users to request money from friends. If the friend approved, the app sent `POST /approve_request {"request_id": "REQ-99"}`. The hunter created two accounts, sent a request for $50, and intercepted the approval. The hunter sent the approval request to Repeater and mashed the "Send" button 5 times. The backend processed the approval sequentially. It saw the request was valid, deducted $50 from the victim, and gave $50 to the attacker. It did this 5 times. The victim's account was drained of $250, but the attacker's original request was only for $50. The application failed to mark `REQ-99` as `STATUS=COMPLETED` until the very end of the function, allowing the duplicate HTTP requests to slip through the validation check.

## How to Fix It
- **Developer remediation:**
  1. **Idempotency Keys:** Every high-value transaction (payments, redemptions) must require a unique, client-generated `Idempotency-Key` header (usually a UUID). The server checks if it has seen this key before. If yes, it returns the cached response of the *first* execution and completely ignores the duplicate request.
  2. **Immediate State Invalidations:** If redeeming a code, the absolute first step in the database transaction must be `UPDATE codes SET status='used' WHERE code='XYZ' AND status='active'`. If the query returns 0 updated rows, abort the transaction immediately. Do not calculate the reward until the code is successfully locked/voided.
  3. **UI Debouncing:** On the frontend, immediately disable the "Submit" button via JavaScript the millisecond it is clicked to prevent accidental double-clicks from slow users. (Note: This is UX defense, not security defense; the backend must still be secured).

## Chaining Opportunities
- This vuln + [[25.09 Race Conditions in Financial Transactions]] → If sequential Double Submits are blocked by the database, use Race Conditions to squeeze the duplicate requests through before the database can update the state.
- This vuln + [[25.11 Referral Abuse / Self-Referral]] → Claim the same referral bonus multiple times.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.09 Race Conditions in Financial Transactions]]
