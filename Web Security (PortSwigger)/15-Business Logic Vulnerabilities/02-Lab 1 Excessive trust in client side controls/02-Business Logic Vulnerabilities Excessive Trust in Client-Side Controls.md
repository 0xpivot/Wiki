---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities: Excessive Trust in Client-Side Controls

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when the application logic is flawed, leading to unintended behavior that can be exploited by attackers. These vulnerabilities often arise due to excessive trust placed in client-side controls, which can be manipulated by malicious users. In this section, we will delve into the specifics of such vulnerabilities, using a practical example from a web application's shopping cart functionality.

### Understanding the Scenario

In the given scenario, the application allows users to add items to their cart and proceed to checkout. The critical aspect to note is that the application relies heavily on client-side controls for validating the price of items. This reliance can lead to significant security issues if the server does not independently validate these inputs.

#### Key Concepts

- **Client-Side Controls**: These are mechanisms implemented on the client side (usually in JavaScript) to enforce certain rules or validations. Examples include form validation, input sanitization, and conditional checks.
- **Server-Side Controls**: These are mechanisms implemented on the server side to ensure that all data received from the client is valid and safe to process. Examples include input validation, parameter sanitization, and business rule enforcement.

### Analyzing the Vulnerability

Let's break down the steps involved in identifying and exploiting this vulnerability:

1. **Adding Items to the Cart**:
    - The user adds an item to the cart, and the application sends a POST request to the `/cart` endpoint.
    - The request includes parameters such as the item ID and the price.

2. **Checkout Process**:
    - When the user proceeds to checkout, the application sends another request to the server.
    - The server processes the request and redirects the user to the payment page.

#### Example Request and Response

```http
POST /cart HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 20

item_id=1&price=1337
```

```http
HTTP/1.1 302 Found
Location: /checkout
Content-Length: 0
```

### Identifying the Flaw

The flaw in this scenario lies in the fact that the server trusts the client-side controls to validate the price of the item. If the server does not independently verify the price, an attacker can manipulate the request to set the price to a lower value, effectively bypassing the intended pricing mechanism.

#### Exploitation Steps

1. **Identify the Vulnerable Parameter**:
    - The `price` parameter in the `/cart` endpoint is the key focus.
    - An attacker can modify this parameter to any desired value.

2. **Manipulate the Request**:
    - The attacker can intercept the request and change the `price` parameter to a lower value, such as `$0`.

#### Example Exploitation

```http
POST /cart HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

item_id=1&price=0
```

### Real-World Examples and Recent Breaches

Business logic vulnerabilities have been exploited in numerous real-world scenarios. One notable example is the breach of a popular e-commerce platform where attackers were able to manipulate product prices, leading to significant financial losses.

#### CVE Example: CVE-2021-XXXX

In CVE-2021-XXXX, a vulnerability was discovered in a web application where the server did not validate the quantity of items added to the cart. Attackers could manipulate the quantity to negative values, resulting in unauthorized refunds.

### How to Prevent / Defend

To prevent business logic vulnerabilities related to excessive trust in client-side controls, several measures can be taken:

1. **Independent Server-Side Validation**:
    - Ensure that all inputs received from the client are independently validated on the server side.
    - Implement robust validation mechanisms to check for valid ranges and values.

2. **Secure Coding Practices**:
    - Use secure coding practices to avoid common pitfalls such as trusting client-side controls.
    - Validate all inputs against a whitelist of acceptable values.

3. **Configuration Hardening**:
    - Harden server configurations to minimize the risk of exploitation.
    - Use security tools like Web Application Firewalls (WAFs) to detect and mitigate suspicious activities.

#### Secure Code Example

**Vulnerable Code**:
```python
@app.route('/cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    price = request.form['price']
    # Add item to cart without validation
    return redirect('/checkout')
```

**Fixed Code**:
```python
@app.route('/cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['item_id']
    price = request.form['price']
    # Validate price against database
    if not validate_price(item_id, price):
        abort(400, description="Invalid price")
    # Add item to cart
    return redirect('/checkout')

def validate_price(item_id, price):
    # Fetch actual price from database
    actual_price = get_item_price_from_db(item_id)
    return int(price) == actual_price
```

### Detection and Monitoring

To detect and monitor for business logic vulnerabilities, implement the following strategies:

1. **Logging and Monitoring**:
    - Enable detailed logging of all requests and responses.
    - Monitor logs for suspicious activities such as unusual price values or quantities.

2. **Security Tools**:
    - Use security tools like static analysis tools and dynamic analysis tools to identify potential vulnerabilities.
    - Regularly perform security assessments and penetration testing.

### Hands-On Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including business logic vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training and research.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

Business logic vulnerabilities are a significant threat to web applications, especially when there is excessive trust in client-side controls. By understanding the underlying principles and implementing robust security measures, developers can mitigate these risks and ensure the integrity of their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/01-Introduction to Business Logic Vulnerabilities|Introduction to Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/00-Overview|Overview]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]]
