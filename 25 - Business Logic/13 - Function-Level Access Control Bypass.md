---
tags: [vapt, business-logic, access-control, critical]
difficulty: advanced
module: "25 - Business Logic"
topic: "25.13 Function-Level Access Control Bypass"
---

# 25.13 — Function-Level Access Control Bypass

## What is it?
Also known as **Missing Function-Level Access Control** (or Vertical Privilege Escalation), this logic flaw occurs when an application correctly authenticates a user (proves who they are), but fails to securely verify their *authorization* (proves what they are allowed to do) before executing a sensitive function.

Many modern applications rely on the User Interface (UI) to enforce roles. If a user is a "Standard User", the UI simply hides the "Admin Dashboard" button or the "Delete User" button. However, the actual API endpoints (e.g., `DELETE /api/users/42`) remain entirely exposed and functional. 

If an attacker discovers the existence of these administrative or premium API endpoints and sends requests to them directly, the backend server executes them because it assumes "If they are calling this endpoint, the UI must have allowed them to, so they must be an admin."

Think of it like a corporate office building. You are a low-level employee. The security guard at the front desk checks your ID (Authentication). You walk into the elevator. The button for the "Executive Boardroom" on the 50th floor requires a special keycard to press (UI restriction). However, you discover that if you just walk into the stairwell and climb 50 flights of stairs, the door to the boardroom is completely unlocked (Missing Access Control). The company assumed that because the elevator button was restricted, the room itself was secure.

## ASCII Diagram
```text
================================================================================
                    MISSING FUNCTION-LEVEL ACCESS CONTROL
================================================================================

[The UI Illusion]
Standard User logs in.
UI renders:
- [View Profile]
- [Edit Profile]
(The [Delete Other Users] button is hidden).

[The Backend Reality]
Attacker ignores the UI. Looks at the Javascript source code.
Finds a hidden endpoint: `POST /api/v1/admin/delete_user`

[The Exploit]
Attacker (Standard User) ──> POST /api/v1/admin/delete_user {"id": 99}
                                  │
[API Server Logic]                ▼
"Ah, a request to delete User 99! Let me check the session."
"Is the user logged in? YES."
[FATAL FLAW]: The server FORGETS to check: `if (user.role == 'ADMIN')`
"Okay, deleting User 99."
                                  │
                                  ▼
                        [User 99 is deleted!]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **Map the Application from an Admin Perspective:** If possible, create two accounts on the target system (e.g., an Admin account and a Standard account). If you cannot create an Admin account, map the application thoroughly as a Standard user.
  2. **Discover Hidden Endpoints:** Look through the client-side JavaScript (`.js` files). Developers often bundle all routing logic into one file. Search for keywords like `admin`, `delete`, `superuser`, `manage`, `billing`, `roles`.
  3. **Guess Endpoints:** If your profile URL is `/api/user/profile`, try requesting `/api/admin/profile` or `/api/user/manage`.
  4. **The Forced Browsing Test:** 
     - While logged in as the Standard user, use Burp Suite to send a request to a known Admin endpoint.
     - Change the HTTP method: If `GET /api/users` is blocked, try `POST /api/users`, `PUT /api/users`, or `DELETE /api/users`. Sometimes the GET request has an access control check, but the developer forgot to put it on the DELETE request!
  5. **Parameter Tampering:** Intercept your profile update request. Try injecting administrative flags: `{"email": "me@me.com", "role": "admin", "is_admin": true}`. This is known as Mass Assignment, which leads to Access Control bypass.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's exploit a system where we only have a Standard user account.
  1. We browse the site and intercept traffic. We see we can edit our own posts via `PUT /api/posts/123`.
  2. We review the main JavaScript bundle using browser DevTools. We find a function called `suspendAccount(userId)`. It makes a request to `POST /api/admin/suspend`.
  3. Since we don't have the button, we manually construct the request in Burp Suite using our Standard user's session cookies.
  4. We send `POST /api/admin/suspend {"user_id": 1}` (User 1 is usually the main administrator).
  5. The server responds with `200 OK`. We have just suspended the administrator because the backend lacked an `isAdmin()` check.

- **Actual payloads:**
  **Method Tampering to bypass restrictions:**
  ```http
  # GET is blocked (403 Forbidden)
  GET /api/v1/users/export HTTP/1.1
  
  # POST might be allowed!
  POST /api/v1/users/export HTTP/1.1
  ```
  **URL Path Traversal / Normalization Bypass:**
  If a WAF blocks requests starting with `/admin`:
  ```http
  GET /api/v1/users/../admin/dashboard HTTP/1.1
  GET /admin%20/dashboard HTTP/1.1
  ```

## Real-World Example
A Bug Bounty hunter was testing a human resources portal. Standard employees could view their own paystubs via `GET /api/payroll/view`. The hunter noticed that the API path included a version number: `v2`. The hunter changed the URL to the deprecated `v1` API: `GET /api/v1/payroll/view`. The `v1` API was still active, but the developers had stopped updating it. Crucially, the `v1` API lacked the granular access controls added in `v2`. By using the `v1` API, the hunter was able to view the paystubs of the CEO and the entire executive board, achieving a massive data breach simply by altering the URL path.

## How to Fix It
- **Developer remediation:**
  1. **Default Deny:** The default stance of any API endpoint should be to reject the request. Access must be explicitly granted.
  2. **Backend Role Verification:** Every single endpoint that performs a sensitive action or returns sensitive data must explicitly check the user's role on the backend. Do not rely on UI obfuscation.
  3. **Centralized Middleware:** Do not write role checks inside individual functions (where developers might forget them). Implement centralized middleware. For example, route all admin endpoints under `/api/admin/*`, and apply a global middleware to that route that strictly enforces `if (session.role != 'ADMIN') return 403;`.

## Chaining Opportunities
- This vuln + [[25.15 Hidden API Parameters]] → Finding hidden endpoints is the first step; injecting hidden parameters into them is the second.
- This vuln + [[10 - Chaining Playbook (Privilege Escalation)]] → This is the definition of Vertical Privilege Escalation.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.14 Exploiting Trust Between Microservices]]
