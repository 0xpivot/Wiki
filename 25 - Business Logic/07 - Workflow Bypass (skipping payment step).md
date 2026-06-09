---
tags: [vapt, business-logic, e-commerce, critical]
difficulty: advanced
module: "25 - Business Logic"
topic: "25.07 Workflow Bypass (skipping payment step)"
---

# 25.07 — Workflow Bypass (Skipping Payment Step)

## What is it?
In complex web applications, users are expected to follow a strict, predetermined sequence of events. This is called a **State Machine** or **Workflow**. A classic example is the e-commerce checkout flow: 
`Cart` → `Shipping Details` → `Payment Gateway` → `Order Confirmation`.

A **Workflow Bypass** (often called Forced Browsing or State Machine Bypass) occurs when an application assumes that because a user is viewing Step 4, they must have successfully completed Step 3. If the backend fails to explicitly verify the state transition, an attacker can simply jump straight to the end of the workflow, completely skipping critical steps—such as paying for the items.

This is a critical logic flaw because it directly subverts the primary monetization mechanism of the application. It represents a fundamental disconnect between what the User Interface *forces* the user to do, and what the Backend API actually *enforces*.

Think of it like riding a roller coaster. The rules are: 1. Buy a ticket at the booth. 2. Give the ticket to the operator. 3. Get on the ride. But if the physical gate to the ride is left open, and the operator assumes anyone standing on the platform must have already bought a ticket, you can just hop the fence, walk onto the platform, and get on the ride for free. The system failed to check your "state" (Ticket Paid) before allowing the final action (Riding).

## ASCII Diagram
```text
================================================================================
                        THE STATE MACHINE BYPASS
================================================================================

[The Intended Workflow (Developer's Assumption)]
 ┌─────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
 │ Step 1  │ ───> │ Step 2       │ ───> │ Step 3       │ ───> │ Step 4       │
 │ Add to  │      │ Enter Address│      │ Submit Credit│      │ Order Placed!│
 │ Cart    │      │              │      │ Card & Pay   │      │ (DB Updated) │
 └─────────┘      └──────────────┘      └──────────────┘      └──────────────┘

[The Reality of HTTP (Stateless Protocol)]
Because HTTP is stateless, the attacker doesn't have to follow the arrows.
They can make direct API calls to ANY endpoint at ANY time.

[The Exploit]
 ┌─────────┐                                                  ┌──────────────┐
 │ Step 1  │                                                  │ Step 4       │
 │ Add to  │ ───────────────────────────────────────────────> │ API:         │
 │ Cart    │        (Attacker sends POST /order/confirm)      │ Order Placed!│
 └─────────┘                                                  └──────────────┘
                                                                     │
           [Backend Logic Flaw]:                                     │
           "They asked to confirm the order. Let me check the cart.  │
           Yep, there is an iPhone in the cart. I will generate      │
           a receipt and tell the warehouse to ship it."             │
           (The backend FORGOT to check if Payment == True!)         ▼
                                                           [Massive Financial Loss]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. **Map the Entire Workflow:** Go through the entire checkout (or registration/onboarding) process legitimately using a test account and a test credit card (or a low-value item if testing in production).
  2. **Record Traffic:** Ensure Burp Suite is capturing every single request and response. Look specifically for the final API call that confirms the order (e.g., `POST /api/checkout/complete` or `GET /order/success?order_id=123`).
  3. **Analyze State Tracking:** How does the application know you paid? Does the payment provider send a webhook? Does the client send a `payment_status=success` parameter?
  4. **The Jump Test:** 
     - Start a completely new session.
     - Add a high-value item to your cart.
     - Go to Step 1 (Cart).
     - Instead of clicking "Next", use Burp Suite Repeater to send the exact request for the final confirmation step (`POST /api/checkout/complete`).
  5. **Evaluate the Response:** If the server responds with "Order Successful" and gives you an order number, you have successfully bypassed the payment step.
  6. **Parameter Injection:** Sometimes the jump requires manipulating a parameter. If Step 2 sends `POST /checkout_step2 {"status": "shipping_set"}`, try jumping to step 3 and sending `{"status": "payment_complete"}`.

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's explore a scenario where the application relies on the client to report payment success.
  1. The checkout process redirects you to a third-party payment gateway (like PayPal).
  2. You log into PayPal and authorize the payment.
  3. PayPal redirects you back to the merchant: `https://shop.target.com/callback?payment_id=PAY-123&status=APPROVED`.
  4. The merchant server reads `status=APPROVED` and places the order.
  5. **The Exploit:** What happens if you add an item to your cart, and manually type `https://shop.target.com/callback?payment_id=FAKE-999&status=APPROVED` into your browser *without* ever going to PayPal?
  6. If the backend fails to verify the `payment_id` cryptographically with PayPal's backend server, it will blindly trust your URL parameters, assume you paid, and ship the item.

- **Actual payloads:**
  **Direct Endpoint Jumping:**
  ```http
  # Bypassing the /pay endpoint entirely
  POST /api/order/finalize HTTP/1.1
  Host: ecom.target.com
  Cookie: session=xyz123
  
  {"cart_id": "88912"}
  ```
  **Client-Side Status Manipulation:**
  ```http
  POST /checkout/submit HTTP/1.1
  Host: ecom.target.com
  
  cart_id=88912&payment_status=PAID&transaction_id=NULL
  ```

- **Real HTTP request/response examples:**
  **The Drop-Step Attack:**
  *Normal Flow:*
  1. `POST /cart`
  2. `POST /address`
  3. `POST /payment`
  4. `POST /confirm`
  
  *Exploit Flow (Dropping Step 3):*
  1. `POST /cart`
  2. `POST /address`
  3. `POST /confirm`
  
  *Vulnerable Response:*
  ```http
  HTTP/1.1 200 OK
  
  {"message": "Thank you! Your order #99812 will be shipped to the address provided."}
  ```

## Real-World Example
A highly publicized vulnerability occurred on a major pizza delivery website. The site allowed users to pay with a credit card or with loyalty points. The flow was: 
1. Build Pizza. 
2. Go to Checkout. 
3. Select Payment Method. 
4. If "Points" is selected, the client sends `POST /redeem_points`. 
5. The server checks if the user has enough points. If yes, it deducts the points and generates a `payment_token`. 
6. The client sends `POST /place_order` with the `payment_token`.

A Bug Bounty hunter noticed that the `POST /place_order` endpoint did not actually verify *what* the `payment_token` was or *if* it was valid; it only checked that the parameter was not empty! The hunter built an order for 100 pizzas, skipped the payment step entirely, and sent `POST /place_order {"payment_token": "literally_anything"}`. The backend logic said "Token is present. Order is paid." The hunter successfully placed a $2,000 order for free.

## How to Fix It
- **Developer remediation:**
  1. **Strict State Machine Enforcement:** The backend database must track the "Order State" (e.g., `CREATED` -> `SHIPPING_SET` -> `PAYMENT_AUTHORIZED` -> `COMPLETED`).
  2. Before executing the `COMPLETED` logic, the backend must assert: `if (order.state != PAYMENT_AUTHORIZED) { throw Error; }`.
  3. **Cryptographic Verification:** Never trust client-provided payment statuses (like `status=APPROVED` in a URL). The backend server must communicate directly with the payment gateway (via secure Webhooks or backend API calls) to verify that a transaction actually occurred and that the funds were captured for the exact amount required.

## Chaining Opportunities
- This vuln + [[25.05 Free Trial Abuse]] → Bypass the credit-card verification step required to start a free trial, allowing for mass generation of premium accounts.
- This vuln + [[10 - Chaining Playbook (E-commerce)]] → An essential part of the complete e-commerce destruction playbook.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.08 Order Manipulation After Checkout]]
