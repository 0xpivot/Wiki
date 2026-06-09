---
tags: [vapt, business-logic, e-commerce, intermediate]
difficulty: intermediate
module: "25 - Business Logic"
topic: "25.03 Quantity Manipulation (negative quantities)"
---

# 25.03 — Quantity Manipulation (Negative Quantities)

## What is it?
Quantity Manipulation occurs when an e-commerce or financial application fails to properly validate the boundaries and data types of a "quantity" or "amount" parameter. 

If developers secure the `price` parameter (as seen in [[25.02 Price Manipulation in E-commerce]]), attackers will naturally target the `quantity` parameter. If an attacker submits a negative quantity (e.g., `-1`), and the server calculates the total as `Price * Quantity` without ensuring the quantity is positive, the resulting total becomes negative.

This leads to catastrophic scenarios. If you put a $1,000 TV in your cart, and a $10 pen, but set the pen's quantity to `-100`, the server calculates: `$1000 + ($10 * -100) = $0`. You get the TV for free. Alternatively, a negative total might cause the payment gateway to actually *refund* the attacker's credit card.

Think of it like going to a bank and asking to deposit `-100` dollars. A smart teller would refuse. A poorly programmed computer might execute: `Bank Vault = Vault - (-100)`, effectively generating $100 out of thin air.

## ASCII Diagram
```text
[Attacker's Cart]
Item 1: iPhone       | Price: $1000 | Quantity: 1    | Subtotal:  $1000
Item 2: Phone Case   | Price: $10   | Quantity: -100 | Subtotal: -$1000
                                                       ────────────────
                                        Cart Total :  $0.00
                                        
[Server Logic]
Total = (1000 * 1) + (10 * -100)
Total = 1000 - 1000 = 0.

[Result]
Server processes the order. Attacker receives the iPhone for free.
```

## How to Find It
- **Manual steps:**
  1. Add an item to your cart.
  2. Go to the cart view and intercept the "Update Quantity" or "Checkout" request.
  3. Modify the quantity parameter to negative values (`-1`, `-10`).
  4. Modify the quantity to a value of zero (`0`).
  5. Modify the quantity to a fractional value (`0.5`).
  6. Modify the quantity to an extremely high value (`99999999999999999`) to test for Integer Overflow (which can wrap a large positive number into a negative number).
  7. Check the cart total. If the total drops, the vulnerability is present.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Find a way to add a negative quantity item to your cart.
  2. If the site prevents checking out with a negative overall cart balance, add a high-value item (like a laptop) to the cart with a quantity of `1`.
  3. Calculate exactly how many negative items you need to bring the total cart price down to `$0.01` or `$0.00`.
  4. Submit the modified request.
  5. Proceed to checkout and complete the purchase for the heavily discounted target item.

- **Actual payloads:**
  **Testing Variations on Quantity:**
  ```json
  {"qty": -1}
  {"qty": 0}
  {"qty": 0.5}
  {"qty": "-1"}
  {"qty": [1]}
  {"qty": 2147483648}  (Integer Overflow)
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request:**
  ```http
  POST /cart/update HTTP/1.1
  Host: shop.target.com
  Content-Type: application/x-www-form-urlencoded
  
  item_id=84&quantity=-5
  ```
  **Vulnerable Response:**
  ```http
  HTTP/1.1 200 OK
  
  {"cart_total": -50.00, "message": "Cart updated"}
  ```

## Real-World Example
A Bug Bounty hunter was testing a mobile food delivery app. The app allowed users to add toppings to their burger for $1.00 each. The user intercepted the request to add bacon and changed the quantity to `-15`. The server didn't validate the negative integer. The burger cost $10.00, and the `-15` bacon subtracted $15.00, resulting in a cart total of `-$5.00`. When the user clicked checkout, the app's backend interpreted the negative balance as a credit, and immediately added $5.00 to the user's in-app wallet balance, while simultaneously submitting the order to the restaurant.

## How to Fix It
- **Developer remediation:**
  Strictly validate the data type, boundaries, and logic of all numerical input.
  1. Ensure the quantity is cast to an integer (rejecting floats/decimals).
  2. Ensure the quantity is strictly greater than zero (`qty > 0`). If a user wants 0, they should use a separate "Remove from Cart" function.
  3. Use safe math libraries or large integer types to prevent Integer Overflow wrapping.

- **Code snippet:**
  **Java / Spring (Secure Quantity Validation):**
  ```java
  public void updateCart(int productId, int quantity) {
      // 1. Strict Boundary Check
      if (quantity <= 0) {
          throw new IllegalArgumentException("Quantity must be at least 1.");
      }
      
      // 2. Prevent Integer Overflow (Max 100 items per order)
      if (quantity > 100) {
          throw new IllegalArgumentException("Cannot order more than 100 items.");
      }
      
      // Safe to update
      Cart.update(productId, quantity);
  }
  ```

## Chaining Opportunities
- This vuln + [[25.02 Price Manipulation in E-commerce]] → Often found together as developers fail to grasp client-side trust issues.
- This vuln + Integer Overflows → If `-1` is blocked, submitting `4294967295` (32-bit max) + 1 might wrap the integer back to a negative number inside the backend database, bypassing the `quantity > 0` validation.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.04 Discount/Coupon Abuse]]
