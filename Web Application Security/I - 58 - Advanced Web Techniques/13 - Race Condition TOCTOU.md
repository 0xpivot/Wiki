---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.13 Race Condition TOCTOU"
---
# Race Conditions and TOCTOU Vulnerabilities

## Introduction to Race Conditions
A race condition is a concurrency flaw that occurs when multiple threads, processes, or requests attempt to access and modify shared resources simultaneously without proper synchronization. The outcome of the execution depends entirely on the unpredictable timing or "race" of the threads.

In web applications, these flaws typically manifest as logical errors, allowing attackers to bypass business constraints, duplicate assets, or manipulate states in ways the developer never intended.

## TOCTOU: Time-of-Check to Time-of-Use
The most common manifestation of a race condition in web applications is the TOCTOU flaw.
A TOCTOU vulnerability happens when a system checks a condition (the "Check"), and then acts upon that condition (the "Use"). If an attacker can alter the state of the system between the Check and the Use, they can invalidate the premise of the Check and execute unauthorized actions.

### The Classic Example: Fund Transfer
Consider an application that allows users to transfer funds. The logic looks like this:

```php
// 1. Time of Check
$balance = get_balance($user_id);
if ($balance >= $transfer_amount) {
    // [ RACE WINDOW ]
    
    // 2. Time of Use
    $new_balance = $balance - $transfer_amount;
    update_balance($user_id, $new_balance);
    add_funds_to_recipient($recipient_id, $transfer_amount);
}
```

If an attacker with $100 sends two concurrent requests to transfer $100, both requests might hit Step 1 simultaneously. 
- Request A sees $100.
- Request B sees $100.
- Both pass the check.
- Request A updates balance to $0 and sends $100.
- Request B updates balance to $0 (or negative) and sends *another* $100.

The attacker has magically generated $100 out of thin air.

## ASCII Diagram: TOCTOU Flow

```text
Timeline            Thread 1 (Request A)                Thread 2 (Request B)
   |
   |                [ CHECK ]
  T1                SELECT balance -> 100
   |
   |                                                    [ CHECK ]
  T2                                                    SELECT balance -> 100
   |
   |                (Condition passes: 100 >= 100)      (Condition passes: 100 >= 100)
   |
   |                [ USE ]
  T3                UPDATE balance = 0
   |                Send 100 to Recipient
   |
   |                                                    [ USE ]
  T4                                                    UPDATE balance = 0 
   |                                                    Send 100 to Recipient
   v
   
RESULT: System lost 100 units. Attacker gained 200 units from 100.
```

## Common Web Scenarios for Race Conditions

1. **Coupon/Gift Card Application**: Applying a single-use promo code multiple times simultaneously.
2. **Inventory/Ticketing Systems**: Purchasing an item when only 1 is left in stock, resulting in negative inventory.
3. **Voting/Rating Systems**: Submitting multiple upvotes from a single user.
4. **File Uploads**: Overwriting critical files during temporary file processing before antivirus/validation deletes the malicious file.
5. **OAuth/Session State**: Reusing authorization codes or password reset tokens.

## Exploitation Techniques

### The Single-Packet Attack (HTTP/2 Concurrent Streams)
Historically, race conditions were difficult to exploit because network latency caused requests to arrive milliseconds apart, often missing the microscopic race window.

Modern exploitation leverages HTTP/2 multiplexing. An attacker can construct a single TCP packet containing multiple HTTP/2 frames. When the server receives this packet, it unpacks and processes all requests at the exact same instant, perfectly aligning the execution threads.

### Exploitation Tools
- **Turbo Intruder (Burp Suite)**: The premier tool for race conditions. It supports custom Python scripts to manage connection pooling, pipeline requests, and synchronize the last byte of the HTTP request to ensure simultaneous server processing.
- **Race the Web**: A Go-based tool for testing race conditions in web applications.
- **ZAP**: Includes plugins for concurrent request sending.

## Advanced Scenarios: File System Races
Some web frameworks handle uploads by first writing the file to a temporary directory, checking its extension or contents, and then deleting it if it's invalid or moving it to a permanent location if valid.

If an attacker uploads a PHP webshell (`shell.php`), the server writes it to `/tmp/shell.php`. It then takes a few milliseconds to scan it and delete it. 
During that tiny window, the attacker can rapidly issue a GET request to `/tmp/shell.php` to execute the shell before the cleanup thread removes it.

## Mitigation Strategies

Fixing race conditions requires careful management of concurrency, state, and shared resources.

### 1. Database Transactions and Locks (Pessimistic Locking)
Use atomic operations or explicit locks when updating rows. `SELECT ... FOR UPDATE` locks the row, preventing other threads from reading or modifying it until the transaction commits.

```sql
BEGIN;
SELECT balance FROM users WHERE id = 1 FOR UPDATE;
-- Thread 2 will block here until Thread 1 commits.
UPDATE users SET balance = balance - 100 WHERE id = 1;
COMMIT;
```

### 2. Optimistic Locking
Use a version column or a timestamp. Before updating, check if the version has changed since it was read. If it has, abort the transaction and retry.

```sql
UPDATE users SET balance = balance - 100, version = 2 
WHERE id = 1 AND version = 1;
-- If affected_rows == 0, a race occurred. Handle error.
```

### 3. Atomic Operations
Whenever possible, perform the check and the use in a single, atomic operation.

```sql
UPDATE users SET balance = balance - 100 
WHERE id = 1 AND balance >= 100;
```

### 4. Mutexes and Application-Level Locks
In backend code (Node.js, Python, Java), use distributed locks (like Redis Redlock) or in-memory mutexes to ensure only one thread can execute a critical section of code for a specific user/resource at a time.

```python
# Pseudo-code using Redis lock
with redis.lock(f"transfer_lock_{user_id}"):
    balance = get_balance(user_id)
    if balance >= amount:
        update_balance(user_id, balance - amount)
```

## Chaining Opportunities
- **Business Logic Flaws**: Bypassing paid tiers, draining wallets, or duplicating assets.
- **Remote Code Execution (RCE)**: Exploiting TOCTOU in file uploads to execute malicious scripts before validation.
- **Authentication Bypass**: Racing password resets or multifactor authentication (MFA) token validation.

## Related Notes
- [[12 - Timing Attacks Remote Timing Analysis]]
- [[08 - Business Logic Vulnerabilities]]
- [[25 - Insecure Direct Object References (IDOR)]]
- [[42 - File Upload Vulnerabilities]]
