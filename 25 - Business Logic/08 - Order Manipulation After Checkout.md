---
tags: [vapt, business-logic, e-commerce, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.08 Order Manipulation After Checkout"
---

# 25.08 — Order Manipulation After Checkout

## What is it?
E-commerce systems are designed around the concept of a finalized contract: you review your cart, you agree to a price, you pay, and the order is locked. **Order Manipulation After Checkout** occurs when the application allows the user to modify the contents of their order *after* the payment has been authorized, without forcing a recalculation or a new payment authorization.

This is a profound logic flaw because it violates the integrity of the transaction. If an attacker pays $5 for a cheap item, and then modifies the order in the database to contain a $1,000 item before the warehouse ships it, the company loses $995.

This vulnerability usually arises in modern, asynchronous microservice architectures. The "Payment Service" authorizes the card, but the "Cart Service" might still allow modifications, and the "Fulfillment Service" might blindly read whatever is currently in the cart when it generates the shipping label hours later.

Think of it like buying a coffee. You walk up to the register, order a $2 black coffee, and hand the cashier $2. The cashier turns around to process the receipt. While their back is turned, you quickly reach over the counter, grab a $15 bag of premium coffee beans, and drop it into your bag. The barista at the end of the counter sees your receipt for "1 Item" and hands you the black coffee, completely unaware you manipulated your haul post-payment.

## ASCII Diagram
```text
================================================================================
                   THE POST-CHECKOUT MANIPULATION
================================================================================

[The Timeline of an Order]

T=0: Attacker adds "Sticker ($1)" to Cart. (Cart ID: 99)
T=1: Attacker proceeds to Checkout.
T=2: Payment Gateway authorizes $1 on the Attacker's credit card.
T=3: Order is marked "PAID". Status becomes "PENDING_SHIPMENT".

       [THE VULNERABILITY WINDOW OPENS]

T=4: Attacker uses Burp Suite to send:
     POST /api/cart/99/add {"item": "MacBook Pro ($2000)"}

     [Backend Flaw]: The API allows adding items to Cart 99 because it 
     forgets to check if the Order Status is already "PAID/LOCKED".

T=5: Warehouse Worker arrives.
T=6: Warehouse system queries Cart 99 to print the packing slip.
T=7: System prints: "1x Sticker, 1x MacBook Pro".
T=8: Worker packs both items and ships them.

[Result: Attacker paid $1 for $2001 worth of goods.]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Add a low-cost item to your cart and proceed through the entire checkout flow.
  2. Pay for the item (using a test card in a staging environment, or a real card for a $1 item in production).
  3. Wait for the "Order Confirmation" screen. Note your Order ID or Cart ID.
  4. Go to Burp Suite HTTP History and find the request that previously added an item to your cart (e.g., `POST /api/cart/add`).
  5. Send that request to Repeater.
  6. Change the `item_id` to a highly expensive item. Ensure the `cart_id` or `order_id` in the request matches the order you just paid for.
  7. Send the request. 
  8. Check your "Order History" or "Invoice" in the web UI. Does the expensive item now appear on the finalized invoice? If yes, the logic is vulnerable.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. **Identify the lock mechanism:** Does the application use the same `cart_id` throughout the entire session, even after checkout? 
  2. **Test Modification:** After paying for Item A, try to execute `POST /cart/update` or `POST /order/edit`.
  3. **Test Swapping:** Instead of adding an item, try *swapping* an item. If you paid for a "Standard License" (Item ID: 10), try sending a request to update the product variant to "Enterprise License" (Item ID: 11).
  4. **Test Cancellation/Refund Logic:** What happens if you buy two items ($10 each, total $20). You pay $20. Then you exploit a flaw to remove one item. Does the system automatically refund you $10? What if you exploit a flaw to remove the *same* item twice? Does the system refund you $20, leaving you with one item and all your money back?

- **Actual payloads:**
  **Modifying a finalized order via API:**
  ```http
  POST /api/v1/orders/88192/items HTTP/1.1
  Host: api.target.com
  Content-Type: application/json
  Authorization: Bearer <token>
  
  {
    "action": "add",
    "product_sku": "EXPENSIVE-LAPTOP-001",
    "quantity": 1
  }
  ```

## Real-World Example
A security researcher was testing a major airline's ticketing system. The researcher booked a cheap domestic flight for $50 and went through the checkout process. The airline generated a PNR (Passenger Name Record) booking code. The researcher then went back to the flight search page, selected a $5,000 First Class international flight, and intercepted the "Add to Itinerary" request. They noticed a hidden parameter: `booking_reference=NEW`. The researcher changed it to their existing, paid PNR code: `booking_reference=ABC123_PAID`. The backend blindly added the First Class flight to the existing, finalized itinerary without triggering a new payment authorization. The researcher's ticket was instantly upgraded in the system.

## How to Fix It
- **Developer remediation:**
  1. **Immutable State (Locking):** The moment a payment is authorized, the associated Cart or Order object in the database must be rigidly locked. A database flag (e.g., `is_locked = true` or `status = "processing"`) must be set.
  2. **Enforce the Lock:** Every single API endpoint that modifies an order (add item, remove item, change variant) must check this flag: `if (order.is_locked) { return 403 Forbidden; }`.
  3. **Snapshotting:** The Fulfillment service should not query the dynamic "Cart" table. When checkout completes, the contents of the cart should be copied into an immutable `Order_Line_Items` table. Any future modifications to the cart should not affect the finalized line items.

## Chaining Opportunities
- This vuln + [[25.02 Price Manipulation in E-commerce]] → If you can't manipulate the price *before* checkout because the payment gateway is secure, try paying the full price for a cheap item, and manipulating the order *after* checkout to swap it for the expensive item.
- This vuln + [[10 - Chaining Playbook (E-commerce)]] → Demonstrates the critical importance of testing state transitions in business logic.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.07 Workflow Bypass (skipping payment step)]]
