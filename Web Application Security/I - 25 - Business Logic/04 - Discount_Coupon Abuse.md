---
tags: [vapt, business-logic, e-commerce, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.04 Discount/Coupon Abuse"
---

# 25.04 — Discount/Coupon Abuse

## What is it?
E-commerce applications use coupons to drive sales. Business logic dictates that a coupon should only be used once per user, or that multiple coupons cannot be stacked, or that a 20% discount should only apply to specific items. 

Discount/Coupon Abuse occurs when the application fails to strictly enforce these rules. Attackers manipulate the application state to apply the same coupon multiple times, stack mutually exclusive coupons, or apply discounts to items that were supposed to be excluded.

Think of it like a store offering a "20% off your entire order" coupon. The cashier takes your coupon and applies it. But the cashier forgets to keep the physical coupon. You reach into your pocket, hand them the exact same coupon again, and they take another 20% off. You repeat this until the order is free.

## ASCII Diagram
```text
[Expected Logic]
Total: $100
1. Apply "WELCOME20" (-20%) -> Total: $80
2. Apply "WELCOME20" again -> Error: "Coupon already applied!"

[Flawed Logic (Array Injection)]
Total: $100
Attacker sends: {"coupons": ["WELCOME20", "WELCOME20", "WELCOME20"]}
Server loops through array without checking if applied:
   Loop 1: $100 - 20% = $80
   Loop 2: $80 - 20% = $64
   Loop 3: $64 - 20% = $51.20
```

## How to Find It
- **Manual steps:**
  1. Obtain a valid coupon code (e.g., sign up for a newsletter to get a 10% off code).
  2. Apply the code in the cart and intercept the request.
  3. **Stacking:** Try applying the same code again in a new request.
  4. **Array Injection:** Modify the JSON payload from a string to an array: `{"code": "WELCOME"}` -> `{"code": ["WELCOME", "WELCOME"]}`.
  5. **Parameter Pollution:** Send the parameter twice in a URL-encoded form: `code=WELCOME&code=WELCOME`.
  6. **Case Sensitivity:** If `WELCOME` is applied, try applying `welcome`, `WeLcOmE`, or `WELCOME ` (with a trailing space). Sometimes the backend uses case-sensitive checks for "already applied" but case-insensitive checks for calculating the discount.
  7. **Predictability:** If your code is `NEWUSER-4892`, try `NEWUSER-4893`. The generation algorithm might be predictable.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Add an item to your cart.
  2. Apply your coupon code and observe the discount.
  3. Use Burp Suite's Intruder or Repeater to spam the coupon application endpoint with the exact same request rapidly (testing for Race Conditions).
  4. Check the cart total. If the discount is applied multiple times, the logic is flawed.
  5. Alternatively, if there is a flat-rate coupon (e.g., "$10 off your order"), try adding it to a cart that totals $5. Does the total become -$5? Can you check out and gain credit?

- **Actual payloads:**
  **Parameter Pollution Payload:**
  ```http
  POST /apply_discount
  coupon=SAVE10&coupon=SAVE10&coupon=SAVE10
  ```
  **JSON Array Payload:**
  ```json
  {
    "cart_id": "123",
    "discount_codes": ["SAVE10", "SAVE10", "SAVE10"]
  }
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request (Race Condition / Rapid Submission):**
  ```http
  POST /cart/coupon HTTP/1.1
  Host: shop.target.com
  
  code=HALFOFF
  ```
  *(Sent 10 times concurrently)*
  
  **Vulnerable Response (Cart Data):**
  ```json
  {
    "original_price": 100.00,
    "discounts": [50.00, 25.00, 12.50],
    "final_price": 12.50
  }
  ```

## Real-World Example
A Bug Bounty hunter tested a major food delivery app. The app had a promotion: "Get $15 off your first order." The hunter created a new account, added a $15 meal to the cart, and applied the code. Then, the hunter noticed the cart allowed them to add a "Tip" for the driver. The hunter added a $100 tip. The system logic applied the $15 discount to the *entire* cart total, not just the food. The hunter changed the code to apply multiple times via Parameter Pollution. The system applied the $15 discount 8 times ($120 total discount). The hunter checked out, paying $0 for the food and the tip. The driver received a $100 tip paid directly out of the delivery company's pockets!

## How to Fix It
- **Developer remediation:**
  1. **Strict State Enforcement:** A cart should have a boolean flag or a dedicated database column for `applied_coupon`. Once a coupon is applied, any further attempts to apply a coupon should be rejected unless the first is removed.
  2. **Type Checking:** Ensure the input is a string, not an array.
  3. **Atomic Operations (Mutex):** Use database locking or mutexes when applying coupons to prevent Race Conditions from applying the same coupon simultaneously across multiple threads.

## Chaining Opportunities
- This vuln + [[09 - Race Conditions in Financial Transactions]] → The most common way to bypass "coupon already applied" checks is by sending 20 requests at the exact same millisecond.

## Related Notes
- [[01 - What are Business Logic Flaws?]]
- [[05 - Free Trial Abuse]]
