---
tags: [vapt, business-logic, e-commerce, beginner]
difficulty: beginner
module: "25 - Business Logic"
topic: "25.02 Price Manipulation in E-commerce"
---

# 25.02 — Price Manipulation in E-commerce

## What is it?
Price Manipulation is a classic Business Logic Flaw in e-commerce applications. It occurs when an application relies on the client (the user's browser) to supply the price of an item during the checkout process, rather than looking up the definitive price in a secure backend database.

Developers often make the mistake of passing the price in hidden HTML form fields, JSON POST bodies, or URL parameters to make the shopping cart code easier to write. Because attackers control everything sent from their browser, they can intercept the request, change the price to `$0.01`, and submit the order. If the backend fails to re-verify the price against the database, the attacker successfully purchases the item for a penny.

Think of it like shopping at a grocery store where the cashier blindly trusts you. You pick up a $500 TV, cross out the barcode, write "$1.00" on it with a sharpie, and hand it to the cashier. The cashier scans your sharpie note and charges you $1.00.

## ASCII Diagram
```text
[Expected Flow]
User clicks "Add to Cart"
Browser sends: POST /cart/add (item_id=123, price=500.00)
       │
[Server]
Reads price=500.00. Adds to database cart.
User checks out and pays $500.00.

[Attacker Flow]
Attacker intercepts the "Add to Cart" request in Burp Suite.
Browser sends: POST /cart/add (item_id=123, price=500.00)
       │
[Burp Proxy]
Attacker modifies request:
POST /cart/add (item_id=123, price=0.01)
       │
[Server]
Reads price=0.01. FAILS to check database! Adds to cart.
Attacker checks out and pays $0.01 for a $500 item!
```

## How to Find It
- **Manual steps:**
  1. Navigate to an e-commerce store or premium subscription portal.
  2. Turn on Burp Suite Intercept.
  3. Add an item to your cart or initiate a checkout.
  4. Carefully examine the POST request. Look for parameters like `price`, `cost`, `amount`, `total`, `discount`, or `product_price`.
  5. If you see the price in the request, modify it to a lower value (e.g., `0.01` or `1`).
  6. Forward the request and check your cart. If the item is in the cart with your modified price, the logic is flawed.
  7. **Crucial:** You must follow the entire checkout flow. Sometimes the cart displays the manipulated price, but the final payment gateway recalculates it correctly. You must verify the final charge.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Add an expensive item to the cart.
  2. Intercept the request.
  3. Locate the JSON or form-data parameter dictating the price.
  4. Change the value: `"price": 1.00`.
  5. Proceed to the payment gateway. If the gateway asks you to pay $1.00, the exploit is successful.
  6. *Bug Bounty Tip:* Never complete the payment with a stolen credit card or a real card for a manipulated item unless explicitly permitted by the rules of engagement. Stop at the payment gateway confirmation screen.

- **Actual payloads:**
  **Intercepted JSON Body:**
  ```json
  {
    "productId": "88A92",
    "quantity": 1,
    "price": 999.99
  }
  ```
  **Modified Payload:**
  ```json
  {
    "productId": "88A92",
    "quantity": 1,
    "price": 0.01
  }
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request:**
  ```http
  POST /api/v1/cart/items HTTP/1.1
  Host: shop.target.com
  Content-Type: application/json
  
  {"item_id": 42, "item_price": 0.00}
  ```
  **Vulnerable Response:**
  ```http
  HTTP/1.1 200 OK
  
  {"status": "success", "cart_total": 0.00, "message": "Item added!"}
  ```

## Real-World Example
A Bug Bounty hunter was testing a software vendor that sold expensive enterprise licenses. The site didn't use a `price` parameter, but it did use a `currency` parameter. The hunter intercepted the checkout request: `POST /checkout {"license_id": 5, "currency": "USD"}`. The license cost $5,000 USD. The hunter changed the currency to a highly inflated currency (e.g., `"currency": "VND"` for Vietnamese Dong, where $1 USD = ~24,000 VND). The server logic assumed the price was 5,000 *of whatever currency was submitted*. The payment gateway charged the hunter 5,000 VND (about $0.20 USD) for a $5,000 license!

## How to Fix It
- **Developer remediation:**
  Never trust the client to provide the price of an item. The client should only ever provide the `item_id` and the `quantity`.
  
  When an item is added to the cart, the server must query the database for the canonical price associated with that `item_id`. When calculating the final total for the payment gateway, the server must recalculate the total from scratch based on the database prices, ignoring any price data stored locally in the user's browser or cookies.

- **Code snippet:**
  **Python (Secure Cart Addition):**
  ```python
  @app.route('/add_to_cart', methods=['POST'])
  def add_to_cart():
      item_id = request.json.get('item_id')
      quantity = request.json.get('quantity', 1)
      
      # 1. Look up the item in the secure database
      product = Database.get_product(item_id)
      if not product:
          return abort(404)
          
      # 2. Use the database price, NEVER trust client input for price
      cart_item = {
          'id': product.id,
          'name': product.name,
          'price': product.price, # Securely fetched from DB
          'quantity': quantity
      }
      
      session['cart'].append(cart_item)
      return jsonify({"success": True})
  ```

## Chaining Opportunities
- This vuln + [[25.03 Quantity Manipulation (negative quantities)]] → If the price parameter is secure, try manipulating the quantity parameter instead.

## Related Notes
- [[25.01 What are Business Logic Flaws?]]
- [[25.03 Quantity Manipulation (negative quantities)]]
