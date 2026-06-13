---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 25"
---

# Web QnA - Module 25 - Advanced Race Conditions

```text
  [ Attacker (Multi-threading) ]
      |        |        |
    Req 1    Req 2    Req 3  (Sent exactly simultaneously via Turbo Intruder)
      |        |        |
      v        v        v
  +--------------------------+
  |  Web Application Server  |
  |                          |
  | Thread 1: Check Bal ($5) | -> OK!
  | Thread 2: Check Bal ($5) | -> OK!
  | Thread 3: Check Bal ($5) | -> OK!
  |                          |
  | Thread 1: Deduct ($5)    | -> Bal = $0
  | Thread 2: Deduct ($5)    | -> Bal = -$5
  | Thread 3: Deduct ($5)    | -> Bal = -$10
  |                          |
  | Thread 1: Add Item       |
  | Thread 2: Add Item       |
  | Thread 3: Add Item       |
  +--------------------------+
      |        |        |
      v        v        v
  [ Attacker receives 3 items for the price of 1! ]
```

## Formal Technical Questions

**Q1: What is a Time-of-Check to Time-of-Use (TOCTOU) vulnerability? Explain its mechanism in web applications.**
**Answer:**
A TOCTOU vulnerability is the fundamental mechanism behind most race conditions. It occurs when a system checks the state of a resource (Time-of-Check), and based on that state, performs an action (Time-of-Use). If the state of the resource can be modified by another concurrent thread or process *between* the check and the use, the system acts on invalid assumptions.
In web applications, this happens when multiple HTTP requests execute concurrently. For example, a coupon redemption endpoint checks if a coupon is valid (TOC). If it is, it applies the discount and then marks the coupon as used (TOU). If an attacker sends 10 requests simultaneously, all 10 threads might pass the TOC phase (validating the coupon is unused) before any single thread reaches the TOU phase (marking it used). The attacker successfully redeems a single-use coupon 10 times.

**Q2: Differentiate between a Single-Endpoint Race Condition and a Multi-Endpoint (Limit Overrun) Race Condition.**
**Answer:**
*Single-Endpoint Race Condition:* The attacker sends multiple concurrent requests to the exact same API endpoint. The goal is to abuse the logic of that specific function, such as bypassing rate limits, exploiting voting mechanisms, or redeeming gift cards multiple times. The TOCTOU window exists within the logic flow of a single controller.
*Multi-Endpoint Race Condition:* The attacker targets two or more different endpoints concurrently to create a conflicting state. For example, Endpoint A initiates a password reset and generates a token. Endpoint B processes the login. If the attacker sends concurrent requests to both, they might exploit a window where the database state is inconsistent, perhaps logging in while the password reset mechanism is actively modifying user attributes. This is much harder to execute but leads to complex logic bypasses.

**Q3: How does the introduction of HTTP/2 Single-Packet Attacks change the landscape of Race Condition exploitation?**
**Answer:**
Historically, exploiting race conditions relied on network synchronization. Attackers used tools to send multiple HTTP/1.1 requests simultaneously, hoping they arrived at the server at the exact same millisecond. Network jitter and latency made this highly unreliable.
HTTP/2 changes this completely via multiplexing. An attacker can use a technique called the "Single-Packet Attack." They prepare multiple HTTP/2 request streams, hold back the final byte of each request, and then send all the final bytes together in a single TCP packet.
This eliminates network jitter entirely. The web server receives all requests simultaneously at the exact same microsecond, perfectly aligning the threads. This makes race conditions that were previously considered "theoretical" or "too tight to exploit" highly reliable and deterministic.

## Scenario-Based Questions

**Q4: You are auditing a banking application. The transfer funds endpoint checks if `balance >= amount`, then performs an `UPDATE accounts SET balance = balance - amount`. You attempt a standard race condition with 50 concurrent requests to transfer out your entire balance, but the database uses strong locking and transactions. The attack fails. Is there any other way a race condition could be present in this architecture?**
**Answer:**
If the database transactions are perfectly isolated (e.g., `SERIALIZABLE` isolation level or using `SELECT ... FOR UPDATE`), the classic state-modification race condition will fail.
However, I would look for Race Conditions in non-database resources:
1. **Third-Party API Race Conditions:** If the bank integrates with an external ledger or a third-party notification system (like sending an SMS upon transfer), the race condition might trigger 50 SMS messages, costing the company money (Denial of Wallet) or bypassing daily SMS limits.
2. **File System Race Conditions:** If the application generates a PDF receipt for the transfer and temporarily writes it to disk using a predictable filename based on the user ID, concurrent requests might overwrite each other's temporary files, leading to corrupted data or reading another user's receipt.
3. **Session State/Cache Race Conditions:** If the balance check relies on a caching layer (like Redis) that isn't updated atomically with the primary database, a cache-invalidation race condition could exist.

**Q5: During a penetration test of a cryptocurrency exchange, you notice an OAuth integration for linking external wallets. The flow is standard: `/auth?state=xyz` -> User logs in -> `/callback?code=123&state=xyz`. You attempt to intercept the callback and replay it simultaneously using HTTP/2 multiplexing. Why would you do this, and what is the potential impact?**
**Answer:**
This is an attempt at a **Single-Use Token Race Condition**. OAuth authorization codes are meant to be strictly single-use. The backend should exchange the `code` for an access token and immediately invalidate the `code`.
If a TOCTOU vulnerability exists in the OAuth token exchange endpoint:
1. Both concurrent requests hit the `/callback` endpoint.
2. Both threads check the database: "Is code 123 valid?" -> Yes.
3. Both threads exchange the code with the OAuth provider (or internal microservice).
4. Both threads receive a valid session or token for the user.
5. Both threads mark the code as used.
The impact is that the attacker generates multiple valid sessions or access tokens from a single OAuth code. In a cryptocurrency exchange, this could allow the attacker to bypass "concurrent login limits" or exploit subsequent race conditions requiring multiple authenticated sessions, potentially leading to unauthorized parallel withdrawals.

## Deep-Dive Defensive Questions

**Q6: You are a database architect reviewing code for a high-frequency trading platform. The developers are using `READ COMMITTED` transaction isolation. Why is this insufficient to prevent TOCTOU race conditions, and what specific database mechanisms would you implement instead?**
**Answer:**
`READ COMMITTED` isolation guarantees that a transaction only reads data that has been committed by other transactions. However, it does **not** prevent another transaction from modifying the data *after* it has been read but *before* the current transaction finishes. 
In a TOCTOU scenario (Check Balance -> Deduct Balance), Thread A reads the balance ($100). Thread B reads the balance ($100). Thread A deducts $100 and commits. Thread B, having already read the balance as $100, also deducts $100 and commits. The balance is now -$100.
To prevent this, I would implement:
1. **Pessimistic Locking:** Use `SELECT ... FOR UPDATE`. This locks the specific rows being read. When Thread A reads the balance, Thread B's read request is blocked and must wait until Thread A completes its transaction and releases the lock.
2. **Optimistic Locking:** Add a `version` column to the table. The query becomes: `UPDATE accounts SET balance = balance - 100, version = version + 1 WHERE id = 1 AND version = [read_version]`. If Thread B tries to update using the old version, the database updates 0 rows, and the application throws a concurrency error.

**Q7: Explain the concept of "Idempotency Keys" and how they structurally mitigate Race Conditions in payment gateways and distributed systems.**
**Answer:**
An idempotency key is a unique identifier (usually a UUID) generated by the client and sent alongside a sensitive request (like processing a payment). 
The server guarantees that any request with the same idempotency key will only be processed **exactly once**, no matter how many times the request is received.
When the server receives a request:
1. It checks an atomic, distributed lock/cache (like Redis) for the idempotency key.
2. If the key exists and the status is "processing", it drops or blocks the concurrent request.
3. If the key exists and the status is "completed", it simply returns the cached response from the original successful request without executing the logic again.
4. If the key does not exist, it marks it as "processing", executes the logic (e.g., deducting funds), and updates the status to "completed".
Because this initial check and lock happen atomically at the very edge of the application (before complex database logic), it structurally eliminates TOCTOU windows. Even if an attacker sends 100 concurrent requests with the same idempotency key, 99 will be instantly rejected or returned the cached result.

## Defensive Coding Examples

**Insecure Implementation (Python/Flask SQLAlchemy):**
```python
@app.route('/transfer', methods=['POST'])
def transfer():
    user = User.query.get(current_user.id)
    # VULNERABLE: No lock is held between reading and writing
    if user.balance >= 100:
        user.balance -= 100
        db.session.commit()
        return "Transfer successful"
    return "Insufficient funds"
```

**Secure Implementation (Pessimistic Locking with SQLAlchemy):**
```python
@app.route('/transfer', methods=['POST'])
def transfer():
    # SAFE: Applies a row-level lock (SELECT ... FOR UPDATE)
    # Other concurrent requests will block until this transaction commits.
    user = User.query.with_for_update().get(current_user.id)
    if user.balance >= 100:
        user.balance -= 100
        db.session.commit()
        return "Transfer successful"
    return "Insufficient funds"
```

## Bonus Practical Exercises

1. **Race Condition Testing with Burp Suite:**
   - Use the Burp Suite Repeater tab, select multiple tabs.
   - Use the "Send group in parallel" feature to issue single-packet HTTP/2 attacks against a mock shopping cart.
   - Try to apply a single 100% off coupon to multiple items simultaneously.
2. **Setup a Limit Overrun Lab:**
   - Write a Node.js script that allows a user to "like" a post once.
   - Intentionally separate the database read (`db.query('SELECT likes FROM posts')`) from the write (`db.query('UPDATE posts SET likes = likes + 1')`) with a small artificial `setTimeout(50ms)` delay.
   - Write a python script using `ThreadPoolExecutor` to send 20 concurrent requests and observe the final like count bypassing the expected +1 limit.

## Tooling & Automation

- **Turbo Intruder (Burp Extension):** The absolute best tool for testing race conditions. Allows you to write Python scripts that control the HTTP connection pool tightly, synchronizing the last byte of multiple requests perfectly.
- **Race the Web:** A command-line tool designed to send out requests concurrently to test for race conditions in REST APIs.
- **Nuclei:** Can be configured to send concurrent requests, although it lacks the extreme precision of Turbo Intruder's single-packet attack feature.

## Real-World Attack Scenario

**Scenario:** Exploiting a Multi-Step Password Reset Race Condition to takeover administrative accounts.
1. The application's password reset flow has two steps:
   - Step 1: `/api/reset/initiate` (Takes email, generates a 6-digit OTP, sends via email).
   - Step 2: `/api/reset/confirm` (Takes email, OTP, and new password).
2. The attacker wants to take over `admin@target.com` but does not have access to their email to receive the OTP.
3. The attacker notices that the OTP generation is tied to the user's email address in the database, updating an `otp_code` column.
4. The attacker prepares two requests:
   - Request A: `/api/reset/initiate` with `email=attacker@evil.com`. (The attacker owns this email).
   - Request B: `/api/reset/initiate` with `email=admin@target.com`.
5. The attacker uses HTTP/2 single-packet synchronization to send Request A and Request B at the exact same microsecond.
6. **The Race Condition:** The backend processes both requests concurrently. Both threads read the database and generate an OTP. 
7. Due to a TOCTOU flaw in the database write operation or a shared global variable for the mailer service, the application associates the OTP generated for `admin@target.com` with the email payload being sent to `attacker@evil.com`.
8. The attacker receives an OTP in their inbox at `attacker@evil.com`. Because of the race condition state-mixup, this OTP is actually the valid code for `admin@target.com` in the database.
9. The attacker submits the OTP to `/api/reset/confirm` with `email=admin@target.com` and changes the administrator's password, achieving full account takeover.

## Chaining Opportunities

- **Race Condition -> Account Takeover (ATO):** Exploiting race conditions in password resets, MFA validation, or OAuth token generation.
- **Race Condition -> Limit Overrun (Business Logic):** Bypassing limits on free trials, voting systems, inventory stocks, or promotional coupon redemptions.
- **Race Condition -> Financial Fraud:** Double-spending in cryptocurrency, manipulating shopping cart totals, or bypassing fund transfer limits.
- **Race Condition -> Privilege Escalation:** Exploiting concurrent user role assignment or permission updates.
- **Race Condition -> Denial of Service (DoS):** Exhausting database connections, API quotas, or SMS sending limits rapidly.

## Related Notes

- [[05 - Business Logic Vulnerabilities]]
- [[10 - Authentication and Authorization Flaws]]
- [[21 - Multi-Threading and Concurrency Issues]]
- [[29 - Advanced HTTP/2 Attacks]]
