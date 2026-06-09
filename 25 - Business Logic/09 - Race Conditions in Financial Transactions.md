---
tags: [vapt, business-logic, race-conditions, advanced]
difficulty: advanced
module: "25 - Business Logic"
topic: "25.09 Race Conditions in Financial Transactions"
---

# 25.09 — Race Conditions in Financial Transactions

## What is it?
A **Race Condition** (specifically a Time-of-Check to Time-of-Use or TOCTOU flaw) is a deeply technical business logic flaw that occurs when a multi-threaded application processes concurrent requests without properly locking shared resources (like a database row).

In financial transactions, the logic is usually:
1. **Check:** Does the user have >= $100 in their account?
2. **Action:** Transfer $100 to User B.
3. **Update:** Deduct $100 from User A's account.

If User A has exactly $100 and sends *two* transfer requests at the exact same millisecond, Thread 1 and Thread 2 might both execute Step 1 simultaneously. Both threads see that User A has $100. Both threads proceed to Step 2. Both threads transfer $100 to User B. Finally, both threads deduct $100. User B receives $200, and User A's balance either goes to -$100, or drops to $0 (if the deduction logic is weak), effectively conjuring money out of thin air.

Think of it like a joint bank account with two ATM debit cards. You and your partner walk up to two different ATMs at the exact same time. The account has $500. You both press "Withdraw $500" at the exact same millisecond. The central bank computer checks the balance for ATM 1: "$500 available". One microsecond later, it checks the balance for ATM 2: "$500 available" (because ATM 1 hasn't dispensed the cash and updated the database yet). Both ATMs dispense $500. You walk away with $1000 from a $500 account.

## ASCII Diagram
```text
================================================================================
                        THE RACE CONDITION
================================================================================

[Initial State: Account Balance = $100]

[Attacker sends 2 identical POST requests concurrently]

   THREAD 1 (Request A)                     THREAD 2 (Request B)
   ──────────────────────                   ──────────────────────
1. SELECT balance FROM db;                  
   (balance = 100)
                                         1. SELECT balance FROM db;
                                            (balance = 100)

2. if (balance >= 100) {                 2. if (balance >= 100) {
      // TRUE! Proceed.                       // TRUE! Proceed.

3. Transfer $100 to Target.              3. Transfer $100 to Target.
                                            (Target now has +$200!)

4. UPDATE balance = balance - 100;       4. UPDATE balance = balance - 100;
   (balance = 0)                            (balance = -100, or just 0 if flawed)
   }                                        }

[Result: $200 transferred, but only $100 existed!]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Identify any feature that involves a limited resource: transferring money, spending loyalty points, redeeming a gift card, applying a discount code, or claiming a unique username.
  2. Map the exact HTTP request that executes the action.
  3. You cannot test this manually in a standard browser. You must send requests concurrently (simultaneously) so they hit the backend server at the exact same time.
  4. Use Burp Suite Intruder or Repeater (Group Send).
  5. **The HTTP/2 Single-Packet Attack:** Modern race condition testing utilizes HTTP/2 multiplexing to put 20 requests inside a single TCP packet. This ensures the server receives all 20 requests at the literal exact same microsecond, eliminating network latency or jitter.

- **Tool commands with flags explained:**
  Using `ffuf` to attempt a basic concurrent race condition (sending 50 requests simultaneously):
  ```bash
  # -t 50 uses 50 concurrent threads. 
  # This relies on network timing, which is less reliable than HTTP/2 Single-Packet.
  ffuf -w dummy_list_of_50_items.txt \
       -u "https://bank.com/api/transfer" \
       -X POST -d '{"to":"attacker", "amount": 100}' \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer <token>" \
       -t 50
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Create two accounts: Attacker (Balance: $50) and Receiver (Balance: $0).
  2. Capture the transfer request from Attacker to Receiver for $50.
  3. Send the request to Burp Suite Repeater.
  4. Duplicate the request tab 20 times.
  5. Add all 20 tabs to a "Tab Group".
  6. Click the drop-down next to the Send button and select **"Send group in parallel (last-byte sync)"**. (This is the HTTP/2 single-packet attack feature in Burp Suite).
  7. Check the Receiver's balance. If the Receiver has $100, $150, or $1000, you have successfully won the race.

- **Actual payloads:**
  **The Target Request (Sent 20 times concurrently):**
  ```http
  POST /api/v1/wallet/transfer HTTP/2
  Host: crypto.target.com
  Authorization: Bearer eyJhb...
  
  {
    "recipient_wallet": "0xAttackerWallet123",
    "amount": 50.00
  }
  ```

- **Real HTTP request/response examples:**
  **Concurrent Responses:**
  *Response 1:* `HTTP/2 200 OK {"msg": "Transfer successful"}`
  *Response 2:* `HTTP/2 200 OK {"msg": "Transfer successful"}`
  *Response 3:* `HTTP/2 200 OK {"msg": "Transfer successful"}`
  *Response 4:* `HTTP/2 400 Bad Request {"msg": "Insufficient funds"}`
  *(The attacker managed to get 3 threads to execute before the database locked, turning $50 into $150).*

## Real-World Example
A highly critical vulnerability was found in a massive global cryptocurrency exchange. The exchange allowed users to convert fiat currency (USD) to cryptocurrency (BTC). The attacker deposited $1,000 USD. They then wrote a custom script using an HTTP/2 library to pack 50 identical `POST /convert {"from": "USD", "to": "BTC", "amount": 1000}` requests into a single TCP frame. The exchange's microservices received all 50 requests at the exact same CPU cycle. 48 of the requests hit a race condition, bypassing the balance check. The exchange deducted the $1,000 USD (dropping the balance to negative, which the UI couldn't even display properly) but credited the attacker with 48,000 USD worth of Bitcoin. The attacker immediately withdrew the Bitcoin to an external wallet, resulting in a multi-million dollar loss for the exchange before they caught it.

## How to Fix It
- **Developer remediation:**
  1. **Pessimistic Database Locking (Row-Level Locking):** When querying the balance, use `SELECT ... FOR UPDATE`. This tells the database to physically lock that user's row. Any other thread attempting to read that balance will be frozen and put into a queue until the first thread finishes the update and releases the lock.
  2. **Atomic Operations:** Rely on the database engine to do the math, rather than the application code. Instead of `SELECT -> IF -> UPDATE`, use a single atomic query: `UPDATE accounts SET balance = balance - 100 WHERE user_id = 42 AND balance >= 100`. If the balance drops below 100, the query updates 0 rows, and the application knows the transfer failed.
  3. **Idempotency Keys:** Require the client to send a unique `transaction_id` with every request. The server strictly enforces that a specific `transaction_id` can only be processed once.

## Chaining Opportunities
- This vuln + [[25.04 Discount/Coupon Abuse]] → Apply the exact same 10% coupon 10 times concurrently.
- This vuln + [[25.12 Rate Limit Bypass for Votes / Likes]] → Bypass brute-force protections by sending 50 password guesses concurrently before the "Max 5 Attempts" counter updates.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.10 Double Submit / Double Spend]]
