---
tags: [vapt, business-logic, limits, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.06 Account Limit Bypass"
---

# 25.06 — Account Limit Bypass

## What is it?
In many web applications, particularly SaaS platforms, games, or fintech applications, users are subjected to strict **Account Limits**. These limits are core business rules designed to monetize the platform or prevent abuse. For example:
- "Free users can only create 3 projects."
- "Standard tier accounts can only transfer $5,000 per day."
- "A user can only vote once per poll."
- "You can only invite 5 friends to earn referral credits."

**Account Limit Bypass** occurs when the application fails to securely, consistently, and atomically verify these limits across all possible interfaces or states. Instead of the limit being a hard, server-side rule that cannot be physically broken, it is often implemented as a weak UI check, a client-side restriction, or a poorly designed database query that can be tricked.

When an attacker bypasses these limits, they gain access to premium features, hoard resources, or execute unauthorized transactions, causing direct financial loss or operational disruption to the business. 

Think of it like a library that only allows you to borrow 3 books at a time. The librarian checks your account, sees you have 0 books, and says "You can borrow up to 3." An attacker walks up to 5 different librarians at the exact same time, hands them each 3 books, and because the librarians don't communicate with each other fast enough (or because they only check the limit *before* stamping the books, not *during*), the attacker walks out with 15 books. Or, alternatively, the attacker realizes the "Self-Checkout" kiosk doesn't actually have the 3-book limit programmed into it at all.

## ASCII Diagram
```text
================================================================================
                        THE ANATOMY OF A LIMIT BYPASS
================================================================================

[Scenario: App allows a maximum of 3 API keys for free users]

[Phase 1: The UI Check (Easily Defeated)]
   [Browser UI] ──> "User has 3 keys. Hide the 'Create Key' button."
      │
      └─> [Attacker Action] ──> Ignores the UI. Uses Burp Suite to send the 
                                POST /api/keys/create request manually.

[Phase 2: The Weak API Check (The Logic Flaw)]
   [Attacker] ──> POST /api/keys/create
      │
      ▼
   [API Server]
      ├─ Step 1: SELECT count(*) FROM keys WHERE user_id = 42; 
      │          (Returns 3)
      │
      ├─ Step 2: if (count < 3) { ... } else { return ERROR }
      │          Wait! The developer used `<` instead of `<=`, or maybe
      │          the attacker sent 10 requests at the exact same millisecond
      │          before the database had time to update the count!
      │
      ▼
[Phase 3: Parameter Manipulation Bypass]
   [Attacker] ──> POST /api/keys/create
                  {"plan_type": "enterprise", "key_name": "hacked"}
      │
      ▼
   [API Server] 
      ├─ Checks limit for "enterprise" plan instead of "free" plan because
      │  the attacker injected the `plan_type` parameter which the server
      │  blindly trusted!
      │
      └─> Result: 4th Key Created Successfully.
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **Identify Limits:** Read the documentation or pricing page of the target application. Look for exact numbers (e.g., "Max 5 team members", "100 MB upload limit", "50 API requests per hour").
  2. **Reach the Limit:** Interact with the application normally until you hit the restriction. Observe how the application stops you (e.g., the button turns gray, an error popup appears, or the API returns a `403 Forbidden`).
  3. **Test UI Bypasses:** If the button is simply disabled in HTML (`<button disabled>`), remove the `disabled` attribute using browser DevTools and click it. 
  4. **Test Direct API Interaction:** Capture the original request used to create the resource (e.g., adding a team member). Use Burp Suite Repeater to send that exact request again *after* you have hit the limit. If the API doesn't enforce the limit on the backend, it will succeed.
  5. **Test Alternative Endpoints:** Sometimes the web UI endpoint (`/api/v1/web/add_user`) has the limit enforced, but the mobile app endpoint (`/api/v1/mobile/add_user`) or an older API version (`/api/v0/add_user`) forgot to implement the check.
  6. **Test Array Injection:** If you are adding a user, change the JSON payload from a single string to an array of 100 users. The limit check might only count the array as "1 request" but the processing loop might add all 100 users.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's walk through an Array Injection limit bypass.
  1. The application limits you to sending 5 SMS invitations per day.
  2. You send 1 invitation. The POST body looks like: `{"phone": "+1234567890"}`.
  3. You send 4 more. You hit the limit. The server responds with `{"error": "Daily limit reached."}`.
  4. You wait 24 hours, or create a new account, so your limit is reset to 0/5.
  5. You intercept the very first invitation request.
  6. You change the payload to an array of 50 phone numbers: `{"phone": ["+1...", "+2...", ..., "+50..."]}`.
  7. The server receives the request. The logic check says: "User has sent 0 invitations today. Limit is 5. Allow request."
  8. The execution code loops over the `phone` parameter. Because it doesn't re-check the limit *inside* the loop, it sends all 50 SMS messages.
  9. You have successfully bypassed the 5 SMS limit, costing the company money.

- **Actual payloads:**
  **Array Injection Bypass:**
  ```json
  // Expected
  { "invitee_email": "friend@gmail.com" }
  
  // Exploit
  { "invitee_email": ["a@g.com", "b@g.com", "c@g.com", "d@g.com", "e@g.com", "f@g.com"] }
  ```
  **Parameter Pollution (Alternative to Arrays):**
  ```http
  POST /invite
  email=a@g.com&email=b@g.com&email=c@g.com&email=d@g.com
  ```

- **Real HTTP request/response examples:**
  **Testing an API limit with Burp Repeater:**
  ```http
  POST /api/v2/projects/create HTTP/1.1
  Host: saas.target.com
  Content-Type: application/json
  Authorization: Bearer <free_tier_token>
  
  {"name": "Project Number 4"}
  ```
  **Vulnerable Response (Backend failed to check tier):**
  ```http
  HTTP/1.1 201 Created
  
  {"status": "success", "project_id": "8891", "message": "Project created."}
  ```

## Real-World Example
A Bug Bounty hunter was testing a cloud storage provider. Free accounts were strictly limited to storing 5 Gigabytes of data. When the user attempted to upload a file through the web interface that exceeded this limit, the browser calculated the file size and blocked the upload via JavaScript. The hunter used a python script to interact directly with the `/upload` API endpoint. They discovered that while the backend *did* check the total account size, it only did so *after* the file was fully uploaded and written to disk. If the account was over the limit, it would mark the account as "Storage Full" to prevent *future* uploads, but it didn't delete the file that just pushed it over the limit. The hunter wrote a script to concurrently upload ten 100-Gigabyte files at the exact same time. The server accepted all of them simultaneously, resulting in a free account storing 1 Terabyte of data before the "Storage Full" flag was finally flipped.

## How to Fix It
- **Developer remediation:**
  1. **Server-Side Enforcement is Mandatory:** Never rely on the client (browser/mobile app) to enforce business rules. The server must act as the ultimate source of truth.
  2. **Atomic Checks:** Limit checks must occur inside the same database transaction as the action itself to prevent race conditions. 
  3. **Loop Awareness:** If an endpoint accepts bulk actions (arrays or multiple parameters), the limit check must calculate the *size* of the bulk action against the remaining quota before processing begins (e.g., `if (current_count + array.length > MAX_LIMIT)`).
  4. **Strict Type Validation:** Do not allow arrays to be passed to fields that expect strings.

## Chaining Opportunities
- This vuln + [[09 - Race Conditions in Financial Transactions]] → The absolute best way to bypass a hard server-side limit check is to execute a Race Condition, smashing the endpoint with 30 requests before the database has time to increment the usage counter.
- This vuln + [[04 - Discount_Coupon Abuse]] → Bypassing the limit of "One coupon per customer."

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[09 - Race Conditions in Financial Transactions]]
