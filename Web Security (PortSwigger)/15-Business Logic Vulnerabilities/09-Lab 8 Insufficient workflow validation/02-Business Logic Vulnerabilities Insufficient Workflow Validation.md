---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities: Insufficient Workflow Validation

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when the application's business rules are not properly enforced, leading to unintended behavior that can be exploited by attackers. These vulnerabilities often arise due to insufficient validation of user inputs, improper handling of workflows, and inadequate enforcement of business rules. In the context of web applications, business logic vulnerabilities can lead to financial losses, data breaches, and other severe consequences.

### Understanding the Scenario

In the given scenario, we have a web application where users can purchase items using store credit. The specific item in question is a leather jacket priced at $1,337. Users also have the option to apply coupons to reduce the cost. The goal is to determine if there are any vulnerabilities in the workflow that allow an attacker to purchase the jacket for less than its actual price.

### Analyzing the Workflow

The workflow involves several steps:

1. **View Item Details**: The user clicks on the "view details" button to see the item's information.
2. **Add Item to Cart**: The user adds the item to their shopping cart.
3. **Checkout**: The user proceeds to checkout and places the order.

#### Step-by-Step Analysis

1. **View Item Details**:
    - The user navigates to the item's details page.
    - This step typically involves fetching the item's information from the server.

2. **Add Item to Cart**:
    - The user clicks on the "add to cart" button.
    - This action triggers a POST request to the server with the following parameters:
        - `product_id`: The unique identifier of the item.
        - `redirect`: A parameter used for redirection after the action.
        - `quantity`: The number of items to be added to the cart.

    ```http
    POST /cart/add HTTP/1.1
    Host: example.com
    Content-Type: application/x-www-form-urlencoded

    product_id=123&redirect=true&quantity=1
    ```

3. **Checkout**:
    - The user proceeds to the checkout page.
    - This step involves another POST request to the server with the following parameter:
        - `csrf_token`: A token used to prevent Cross-Site Request Forgery (CSRF) attacks.

    ```http
    POST /checkout HTTP/1.1
    Host: example.com
    Content-Type: application/x-www-form-urlencoded

    csrf_token=abc123
    ```

### Identifying Potential Vulnerabilities

To identify potential vulnerabilities, we need to analyze the workflow and the parameters involved in each step.

#### Parameter Analysis

1. **Product ID**:
    - The `product_id` parameter is used to specify which item is being added to the cart.
    - If this parameter is not properly validated, an attacker could manipulate it to add a different item or a non-existent item to the cart.

2. **Redirect Parameter**:
    - The `redirect` parameter is used for redirection purposes.
    - If this parameter is not properly validated, an attacker could manipulate it to redirect the user to a malicious site.

3. **Quantity Parameter**:
    - The `quantity` parameter specifies the number of items to be added to the cart.
    - If this parameter is not properly validated, an attacker could manipulate it to add more items than intended, potentially exceeding the user's store credit.

4. **CSRF Token**:
    - The `csrf_token` parameter is used to prevent CSRF attacks.
    - If this parameter is not properly validated, an attacker could bypass CSRF protection and perform unauthorized actions.

### Real-World Examples

#### Example 1: CVE-2021-21972

In 2021, a vulnerability was discovered in the WooCommerce plugin for WordPress. The vulnerability allowed attackers to manipulate the quantity parameter during the checkout process, leading to unauthorized purchases.

```http
POST /wc-api/v3/cart HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "product_id": 123,
  "quantity": 1000
}
```

This vulnerability was exploited to perform unauthorized purchases, resulting in significant financial losses for merchants.

#### Example 2: CVE-2022-22965

Another example is the vulnerability discovered in the Magento e-commerce platform. The vulnerability allowed attackers to manipulate the product ID parameter during the checkout process, leading to unauthorized access to premium products.

```http
POST /checkout/cart/updateItems HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "cartItem": {
    "quoteId": "123",
    "items": [
      {
        "product_id": 456,
        "qty": 1
      }
    ]
  }
}
```

This vulnerability was exploited to gain unauthorized access to premium products, resulting in significant financial losses for merchants.

### How to Prevent / Defend

To prevent business logic vulnerabilities, it is essential to enforce proper validation and enforcement of business rules. Here are some best practices:

1. **Input Validation**:
    - Validate all user inputs to ensure they meet the expected criteria.
    - Use server-side validation to prevent manipulation of input parameters.

2. **Parameter Validation**:
    - Validate all parameters involved in the workflow to ensure they are within the expected range.
    - Use strong typing and validation libraries to enforce parameter constraints.

3. **CSRF Protection**:
    - Implement robust CSRF protection mechanisms to prevent unauthorized actions.
    - Use tokens and validate them on the server-side to ensure authenticity.

4. **Business Rule Enforcement**:
    - Enforce business rules on the server-side to ensure proper workflow execution.
    - Use conditional statements and validation logic to enforce business rules.

### Secure Code Fix

Here is an example of how to implement secure code to prevent business logic vulnerabilities:

#### Vulnerable Code

```python
def add_to_cart(product_id, quantity):
    # Add item to cart without validation
    cart.add_item(product_id, quantity)
```

#### Secure Code

```python
def add_to_cart(product_id, quantity):
    # Validate product_id and quantity
    if not validate_product_id(product_id):
        raise ValueError("Invalid product ID")
    if not validate_quantity(quantity):
        raise ValueError("Invalid quantity")

    # Add item to cart
    cart.add_item(product_id, quantity)
```

### Detection and Prevention

To detect and prevent business logic vulnerabilities, it is essential to perform regular security assessments and code reviews. Here are some tools and techniques:

1. **Static Application Security Testing (SAST)**:
    - Use SAST tools to analyze the codebase for potential vulnerabilities.
    - Identify and fix issues related to input validation, parameter validation, and business rule enforcement.

2. **Dynamic Application Security Testing (DAST)**:
    - Use DAST tools to simulate attacks and identify vulnerabilities in the running application.
    - Identify and fix issues related to CSRF protection, input validation, and parameter validation.

3. **Code Reviews**:
    - Perform regular code reviews to identify and fix potential vulnerabilities.
    - Ensure that all user inputs are properly validated and business rules are enforced.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including business logic vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training and research.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Business logic vulnerabilities can have severe consequences for web applications. By understanding the workflow, analyzing the parameters, and implementing proper validation and enforcement of business rules, developers can prevent such vulnerabilities. Regular security assessments and code reviews are essential to detect and fix potential issues.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/09-Lab 8 Insufficient workflow validation/01-Introduction to Business Logic Vulnerabilities|Introduction to Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/09-Lab 8 Insufficient workflow validation/00-Overview|Overview]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/09-Lab 8 Insufficient workflow validation/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]]
