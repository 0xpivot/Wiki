---
tags: [vapt, business-logic, beginner]
difficulty: beginner
module: "25 - Business Logic"
topic: "25.01 What are Business Logic Flaws?"
---

# 25.01 — What are Business Logic Flaws?

## What is it?
Unlike typical vulnerabilities such as SQL Injection or XSS, where the application's code fails to properly handle raw syntax, **Business Logic Flaws** (or Logic Bugs) occur when the application's *design and rules* are flawed. 

The code itself might be perfectly secure—no injections, no buffer overflows, no cross-site scripting. However, the logic defining *how* the application should behave under specific, unexpected conditions is broken. These flaws exploit the assumptions made by developers about how users will interact with the system.

Because logic flaws are unique to the specific business rules of an application (e.g., an airline's booking process, a game's trading system, or a bank's transfer limit), they cannot be detected by automated scanners. Finding them requires human intuition, a deep understanding of the application's workflow, and asking "What happens if I do this out of order?"

Think of it like a vending machine. The machine is physically secure, and you can't break the glass. The logic is: "Insert $1. Press button. Dispense soda. Return change." A logic flaw is discovering that if you press the button *while* inserting the dollar, the machine gives you the soda *and* returns your dollar because the developer assumed humans couldn't do both at the exact same time.

## ASCII Diagram
```text
[Expected Workflow: Buying a Ticket]
1. Select Ticket ($100) ──> 2. Add to Cart ──> 3. Pay $100 ──> 4. Receive Ticket
       │                        │                 │                  │
       [OK]                     [OK]              [OK]               [OK]

[Attacker's Exploited Workflow (Logic Bypass)]
1. Select Ticket ($100) ──> 2. Add to Cart ──> 3. Go directly to step 4!
       │                        │                 │
       [OK]                     [OK]      [Developer forgot to check if step 3 happened!]
                                                  ▼
                                           4. Receive Ticket for FREE!
```

## How to Find It
- **Manual steps:**
  1. Map the application completely. You must understand *how* it is supposed to work before you can break it.
  2. Identify multi-step processes (e.g., shopping carts, password resets, onboarding flows).
  3. Identify all parameters related to state, price, quantity, limits, or user roles.
  4. Ask critical questions:
     - What happens if I drop a step in a multi-step process?
     - What happens if I send a negative number?
     - What happens if I send an array instead of a string?
     - What happens if I perform an action meant for step 4 while I am on step 1?
     - Can I transfer money to myself?
  5. Use Burp Suite Intercept to modify requests in transit, testing the application's response to unexpected states.

- **Tool commands with flags explained:**
  Tools cannot find logic flaws, but Burp Suite's `Repeater` and `Intruder` (or ZAP) are essential for manually manipulating parameters and sending unexpected data types:
  *(No specific terminal command; this requires deep proxy analysis).*

## How to Exploit It
- **Step-by-step walkthrough:**
  (Exploitation depends entirely on the specific logic flaw found. The following is a generalized approach).
  1. Identify a restriction (e.g., "You can only use one coupon per order").
  2. Find the mechanism enforcing the restriction (e.g., the server checks the `coupon_code` field).
  3. Attempt to bypass the mechanism. What if you send `coupon_code` twice in the same request? `?coupon=A&coupon=B`. Does the server apply both?
  4. What if you send the request to apply the coupon simultaneously from two different browser tabs (Race Condition)?
  5. Verify the financial or state impact of the bypass.

## Real-World Example
A classic example occurred in a major cryptocurrency exchange. The exchange allowed users to trade Bitcoin for Ethereum. The developer wrote logic that said: `user_btc_balance = user_btc_balance - trade_amount`. An attacker intercepted the trade request and changed the `trade_amount` to `-100`. The server executed: `user_btc_balance = user_btc_balance - (-100)`. Because subtracting a negative is addition, the attacker credited their own account with 100 Bitcoin while also receiving the corresponding Ethereum. The code was "secure" against SQLi, but the logic was fundamentally broken.

## How to Fix It
- **Developer remediation:**
  Fixing business logic flaws requires robust architecture and strict server-side validation. 
  1. Never trust the client. If an item costs $10, do not rely on the client sending `price=10`. Look up the price in the database based on the `item_id`.
  2. Implement strict State Machines. If a user is on Step 3, the server must explicitly verify they successfully completed Step 2.
  3. Validate data types and boundaries (e.g., quantities must be `> 0`).

## Chaining Opportunities
- This vuln + [[09 - Race Conditions in Financial Transactions]] → Logic flaws are frequently exploited via Race Conditions, taking advantage of the microsecond delay between the server checking a rule and enforcing it.
- This vuln + [[13 - Function-Level Access Control Bypass]] → Logic flaws often result in users accessing administrative or premium functions without authorization.

## Related Notes
- [[02 - Price Manipulation in E-commerce]]
- [[03 - Quantity Manipulation (negative quantities)]]
- [[07 - Workflow Bypass (skipping payment step)]]
