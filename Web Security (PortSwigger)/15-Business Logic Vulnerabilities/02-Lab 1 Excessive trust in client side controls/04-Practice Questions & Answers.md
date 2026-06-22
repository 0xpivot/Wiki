---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary vulnerability demonstrated in the lab titled "Excessive Trust in Client Side Controls"?**

The primary vulnerability demonstrated in the lab is the lack of proper server-side validation of client-supplied input. Specifically, the application does not validate the price parameter on the server side, allowing attackers to manipulate the price of items during the purchasing process.

**Q2. How can you exploit the vulnerability described in the lab? Provide a step-by-step explanation.**

To exploit the vulnerability, follow these steps:

1. **Log in**: Use the provided credentials to log in to the application.
2. **Add Item to Cart**: Identify the item you wish to purchase (e.g., the lightweight leather jacket). Note the actual price of the item.
3. **Manipulate Price Parameter**: Use Burp Suite or similar tool to intercept the request when adding the item to the cart. Modify the `price` parameter in the POST request to a lower value (e.g., `$1`).
4. **Place Order**: Proceed to checkout and place the order with the manipulated price.

By manipulating the `price` parameter, you can purchase the item for an unintended price, effectively exploiting the lack of server-side validation.

**Q3. Why is server-side validation important in web applications?**

Server-side validation is crucial in web applications because it ensures that all inputs and actions are checked against expected values and rules on the server. Relying solely on client-side validation can lead to security vulnerabilities, as attackers can bypass client-side checks and submit malicious or unexpected data directly to the server. Server-side validation helps prevent unauthorized actions, such as modifying prices or quantities, and ensures the integrity and security of the application.

**Q4. How would you fix the vulnerability described in the lab?**

To fix the vulnerability, implement server-side validation for all critical parameters, including the `price` parameter. Ensure that the server verifies the price of the item before processing any transactions. Here’s a high-level approach:

1. **Validate Input on the Server**: When the server receives a request to add an item to the cart or to place an order, validate the `price` parameter against the actual price stored in the database.
2. **Use Secure Tokens**: Implement CSRF protection to ensure that requests are legitimate and not forged.
3. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activities.

Example pseudocode for validating the price:

```python
def validate_price(item_id, submitted_price):
    # Fetch the actual price from the database
    actual_price = get_item_price_from_db(item_id)
    
    # Compare the submitted price with the actual price
    if submitted_price != actual_price:
        raise ValueError("Invalid price submitted")
```

**Q5. Can you provide a recent real-world example where excessive trust in client-side controls led to a security breach?**

One recent example is the **CVE-2021-21972**, which affected several e-commerce platforms. This vulnerability allowed attackers to manipulate the prices of products during the checkout process, leading to unauthorized discounts. The issue stemmed from insufficient server-side validation of the price parameter, similar to the vulnerability discussed in the lab. Attackers could exploit this to purchase items at significantly reduced prices, causing financial losses to the merchants.

In summary, the lack of proper server-side validation can lead to significant security risks, emphasizing the importance of robust validation mechanisms in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/00-Overview|Overview]]
