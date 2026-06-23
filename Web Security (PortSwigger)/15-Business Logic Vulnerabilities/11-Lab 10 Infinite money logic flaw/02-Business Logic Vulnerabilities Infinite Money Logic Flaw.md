---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities: Infinite Money Logic Flaw

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when the application's business rules are not properly enforced, leading to unintended behavior that can be exploited by attackers. These vulnerabilities often arise due to flaws in the application's logic, which can result in financial losses, data breaches, or other severe consequences. In this section, we will explore a specific type of business logic vulnerability: the infinite money logic flaw.

### Understanding the Infinite Money Logic Flaw

The infinite money logic flaw occurs when an attacker can manipulate the application's logic to generate an unlimited amount of money or credits within the system. This can happen due to several reasons, such as:

- **Improper validation**: The application fails to validate user inputs or actions correctly.
- **Inconsistent state management**: The application does not maintain a consistent state across different operations.
- **Incorrect business rules enforcement**: The application does not enforce business rules correctly, allowing for unintended behavior.

#### Example Scenario

Consider an e-commerce platform where users can purchase gift cards and receive store credits. The platform offers a "Sign Up 30" coupon that allows users to buy a gift card for $7 and receive $10 in store credits. An attacker might exploit this scenario by repeatedly purchasing the gift card and accumulating store credits indefinitely.

### Detailed Walkthrough of the Exploit

Let's walk through the steps of the exploit using the provided example:

1. **Add to Cart**:
    - The attacker adds a gift card to their cart.
    - The gift card costs $7 but provides $10 in store credits.

2. **Apply Coupon**:
    - The attacker applies the "Sign Up 30" coupon to the cart.
    - The coupon reduces the cost of the gift card to $7 but still provides $10 in store credits.

3. **Place Order**:
    - The attacker places the order, paying $7 and receiving $10 in store credits.
    - The total store credit balance increases by $10.

4. **Repeat Process**:
    - The attacker repeats the process by purchasing another gift card and applying the coupon.
    - Each iteration increases the store credit balance by $10.

#### Code Example

Here is a simplified example of how the application might handle the purchase and coupon application:

```python
class ShoppingCart:
    def __init__(self):
        self.items = []
        self.coupons = []

    def add_item(self, item):
        self.items.append(item)

    def apply_coupon(self, coupon):
        self.coupons.append(coupon)

    def calculate_total(self):
        total = sum(item.price for item in self.items)
        for coupon in self.coupons:
            total -= coupon.discount
        return total

class GiftCard:
    def __init__(self, price):
        self.price = price

class Coupon:
    def __init__(self, discount):
        self.discount = discount

# Example usage
cart = ShoppingCart()
gift_card = GiftCard(10)
coupon = Coupon(3)

cart.add_item(gift_card)
cart.apply_coupon(coupon)
total = cart.calculate_total()

print(f"Total after applying coupon: {total}")
```

### Real-World Examples and Recent Breaches

Recent real-world examples of business logic vulnerabilities include:

- **CVE-2021-3129**: A vulnerability in the Shopify platform allowed attackers to create unlimited free shipping codes, resulting in significant financial losses.
- **CVE-2020-14774**: A vulnerability in the WooCommerce plugin for WordPress allowed attackers to bypass payment gateways and purchase products for free.

These examples highlight the importance of thoroughly testing and validating business logic to prevent such exploits.

### How to Prevent / Defend Against Business Logic Vulnerabilities

#### Detection

To detect business logic vulnerabilities, organizations should implement the following measures:

- **Automated Testing**: Use automated tools to test the application's business logic for inconsistencies and unintended behavior.
- **Penetration Testing**: Conduct regular penetration tests to identify potential vulnerabilities.
- **Logging and Monitoring**: Implement comprehensive logging and monitoring to detect unusual activity patterns.

#### Prevention

To prevent business logic vulnerabilities, organizations should follow these best practices:

- **Input Validation**: Validate all user inputs to ensure they conform to expected formats and ranges.
- **State Management**: Maintain a consistent state across different operations to prevent inconsistencies.
- **Business Rule Enforcement**: Enforce business rules strictly to prevent unintended behavior.

#### Secure Coding Fixes

Here is an example of how to securely implement the gift card purchase logic:

```python
class ShoppingCart:
    def __init__(self):
        self.items = []
        self.coupons = []
        self.store_credit = 0

    def add_item(self, item):
        self.items.append(item)

    def apply_coupon(self, coupon):
        if len(self.coupons) < 1:  # Limit to one coupon per purchase
            self.coupons.append(coupon)

    def calculate_total(self):
        total = sum(item.price for item in self.items)
        for coupon in self.coupons:
            total -= coupon.discount
        return total

    def place_order(self):
        total = self.calculate_total()
        if total <= 0:
            raise ValueError("Invalid total")
        self.store_credit += 10  # Fixed amount of store credit
        return self.store_credit

class GiftCard:
    def __init__(self, price):
        self.price = price

class Coupon:
    def __init__(self, discount):
        self.discount = discount

# Example usage
cart = ShoppingCart()
gift_card = GiftCard(10)
coupon = Coupon(3)

cart.add_item(gift_card)
cart.apply_coupon(coupon)
store_credit = cart.place_order()

print(f"Store credit after placing order: {store_credit}")
```

### Configuration Hardening

To further harden the application against business logic vulnerabilities, consider the following configuration settings:

- **Rate Limiting**: Implement rate limiting to prevent excessive requests that could indicate an exploit attempt.
- **Access Control**: Enforce strict access control policies to limit the actions users can perform.

### Hands-On Labs

For hands-on practice with business logic vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting business logic vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice finding and fixing various security issues, including business logic vulnerabilities.

### Conclusion

Business logic vulnerabilities can have severe consequences if left unaddressed. By understanding the underlying principles and implementing robust detection and prevention mechanisms, organizations can significantly reduce the risk of such vulnerabilities. Regular testing, thorough validation, and strict enforcement of business rules are key to maintaining a secure application environment.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/01-Introduction to Business Logic Vulnerabilities|Introduction to Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/00-Overview|Overview]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]]
