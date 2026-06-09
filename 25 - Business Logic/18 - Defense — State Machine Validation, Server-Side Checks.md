---
tags: [vapt, business-logic, defense, beginner]
difficulty: beginner
module: "25 - Business Logic"
topic: "25.18 Defense — State Machine Validation, Server-Side Checks"
---

# 25.18 — Defense: State Machine Validation, Server-Side Checks

## What is it?
Securing an application against Business Logic Flaws requires a fundamental paradigm shift in how developers think about trust and architecture. Because logic flaws cannot be caught by automated scanners (like SQLmap or Burp Scanner), defense relies entirely on rigorous engineering practices, threat modeling, and strict backend enforcement.

The two most critical defensive concepts are **Server-Side Checks (Zero Client Trust)** and **State Machine Validation**.

Think of it like building a secure bank vault. 
- **Zero Client Trust:** You don't ask the customer, "How much money did you bring?" and just write it down. You take the money, run it through your own counting machine, and verify the amount yourself. 
- **State Machine Validation:** You don't let someone into the vault just because they are standing in the hallway. You check: Did they pass the lobby security? Did they scan their ID at the manager's desk? You rigidly track their progression through the required sequence of states.

## Key Defensive Strategies

### 1. Zero Client Trust (Server-Side Checks)
The golden rule of web security is: **Never trust the client.** The browser, the mobile app, and the HTTP request are entirely under the attacker's control.
- **Price and Quantity:** If a user adds an item to a cart, the client should only send the `item_id`. The server must query the database to determine the price. The server must validate that `quantity > 0` and is an integer.
- **Role Enforcement:** Do not rely on hiding UI elements. If an endpoint is for Admins only, the very first line of code in the backend controller must be `if (user.role != 'ADMIN') throw ForbiddenException()`.
- **Limits and Quotas:** Do not trust the client when it says "I haven't reached my limit." The server must explicitly run `SELECT count(*) FROM actions WHERE user_id = X` before allowing the action.

### 2. Strict State Machine Enforcement
When an application has a multi-step process (e.g., Checkout, Onboarding, Password Reset), it must act as a rigid State Machine.
- An entity (like an `Order`) must have a distinct `status` column in the database (e.g., `CART_CREATED`, `ADDRESS_SET`, `PAYMENT_AUTHORIZED`, `COMPLETED`).
- Before transitioning to `COMPLETED`, the backend must explicitly assert that the current state is `PAYMENT_AUTHORIZED`. If an attacker tries to jump from `CART_CREATED` to `COMPLETED`, the assertion fails and the request is denied.
- Once a state transitions (e.g., a coupon is applied, or an order is locked), the previous states must be mathematically immutable.

### 3. Atomic Operations and Pessimistic Locking
To prevent Race Conditions and Double Submits:
- Use **Row-Level Locking** (`SELECT ... FOR UPDATE` in SQL) when querying balances or limits that are about to be modified. This forces concurrent threads to wait in line.
- Use **Idempotency Keys** for high-value transactions. Require the client to generate a unique UUID for the payment. If the server sees the same UUID twice, it ignores the second request, preventing accidental (or malicious) double-charges.

### 4. Threat Modeling (The "What If" Game)
Logic flaws are best caught during the design phase, not the testing phase. Developers must play the "What If" game:
- *What if the user skips Step 2?*
- *What if the user submits a negative number?*
- *What if the user submits an array instead of a string?*
- *What if two users do this at the exact same millisecond?*
- *What if the user changes their email address after verifying it?*

## ASCII Diagram
```text
================================================================================
                    SECURE ARCHITECTURE: THE STATE MACHINE
================================================================================

[Attacker attempts Workflow Bypass]
Attacker sends: POST /api/order/finalize {"cart_id": 99}

[Secure Backend Logic]
1. Server receives request for Cart 99.
2. Server loads Cart 99 from Database.
3. Server checks State Machine:
   if (Cart99.status != 'PAYMENT_AUTHORIZED') {
       return 403 Forbidden;  <-- ATTACK BLOCKED!
   }

[Attacker attempts Price Manipulation]
Attacker sends: POST /api/cart/add {"item_id": 5, "price": 0.01}

[Secure Backend Logic]
1. Server receives request.
2. Server completely IGNORES the "price" parameter.
3. Server queries DB: SELECT price FROM products WHERE id = 5;
4. Server adds item to cart with DB_PRICE ($500.00). <-- ATTACK BLOCKED!

================================================================================
```

## Developer Checklist
- [ ] Are prices and critical business data calculated strictly on the server?
- [ ] Is every API endpoint protected by explicit, server-side Role-Based Access Control (RBAC)?
- [ ] Are numerical inputs validated for type (integer), boundaries (min/max), and negative values?
- [ ] Are multi-step workflows governed by a rigid, database-backed state machine?
- [ ] Are high-value endpoints protected against Race Conditions using database locking or mutexes?
- [ ] Are rate limits implemented securely on the backend, tied to User IDs rather than spoofable IPs/Headers?
- [ ] Are actions that should only happen once protected by Idempotency Keys or strict status flags?

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.07 Workflow Bypass (skipping payment step)]]
- [[25.09 Race Conditions in Financial Transactions]]
