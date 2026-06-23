---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when an application does not correctly enforce the intended business rules, leading to unexpected behavior that can be exploited by attackers. These vulnerabilities often arise due to excessive trust in client-side controls, which can be manipulated to bypass intended restrictions. In this chapter, we will delve into the specifics of such vulnerabilities, focusing on the scenario where a web application fails to properly validate user input on the server side, allowing attackers to exploit logic flaws in the purchasing workflow.

### Background Theory

#### What Are Business Logic Vulnerabilities?

Business logic vulnerabilities are flaws in the implementation of business rules within an application. These rules define how the application should behave under various conditions. When these rules are not enforced correctly, attackers can manipulate the application to perform actions that were not intended by the developers. Common scenarios include unauthorized transactions, data manipulation, and privilege escalation.

#### Why Do They Matter?

These vulnerabilities matter because they can lead to significant financial losses, data breaches, and reputational damage. Unlike traditional vulnerabilities like SQL injection or cross-site scripting (XSS), business logic vulnerabilities are often harder to detect and mitigate because they rely on the specific context and rules of the application.

### Real-World Examples

#### Recent Breaches and CVEs

One notable example is the breach at Equifax in 2017, where attackers exploited a vulnerability in the Apache Struts framework to gain unauthorized access to sensitive data. Although this was not strictly a business logic vulnerability, it highlights the importance of ensuring that all aspects of an application are secure.

Another example is the CVE-2021-21972, which affected several e-commerce platforms. Attackers could manipulate the shopping cart to purchase items at reduced prices, leading to significant financial losses for the affected companies.

### Lab Setup: Excessive Trust in Client-Side Controls

To understand and practice mitigating business logic vulnerabilities, we will use the PortSwigger Web Security Academy. This lab is designed to demonstrate how excessive trust in client-side controls can lead to exploitable vulnerabilities.

#### Accessing the Lab

1. **Sign Up**: Visit `https://portswigger.net/web-security` and sign up for an account.
2. **Navigate to Labs**: Once logged in, go to the "Academy" section and select "All Labs".
3. **Search for Lab**: Search for "business logic vulnerabilities" and select "Lab Number One: Excessive Trust in Client-Side Controls".

### Lab Overview

The goal of this lab is to exploit a logic flaw in the purchasing workflow to buy items at an unintended price. The application does not adequately validate user input on the server side, allowing attackers to manipulate the purchase process.

#### User Credentials

To start the lab, you will need to log in using the provided credentials:
```plaintext
Username: user
Password: password
```

### Exploiting the Vulnerability

#### Understanding the Vulnerability

The vulnerability arises because the application trusts client-side controls to enforce business rules. Specifically, the application allows users to specify the price of items they wish to purchase without validating this input on the server side.

#### Steps to Exploit

1. **Log In**: Use the provided credentials to log in to the application.
2. **Identify the Vulnerable Endpoint**: Look for the endpoint responsible for processing purchases. This is typically a POST request to a URL like `/api/purchase`.
3. **Manipulate the Request**: Modify the request to include a lower price for the item you wish to purchase. For example, if the original price is $100, you might set it to $1.

#### Example Request and Response

Here is a sample HTTP request and response:

```http
POST /api/purchase HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "item_id": 1,
  "quantity": 1,
  "price": 1
}
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json

{
  "status": "success",
  "message": "Purchase successful",
  "order_id": 12345
}
```

### How to Prevent / Defend

#### Detection

To detect business logic vulnerabilities, you can use automated tools like static application security testing (SAST) and dynamic application security testing (DAST) tools. Additionally, manual code reviews and penetration testing can help identify such vulnerabilities.

#### Prevention

1. **Server-Side Validation**: Always validate user input on the server side. Do not rely solely on client-side controls.
2. **Use Secure Coding Practices**: Follow secure coding guidelines to ensure that business rules are correctly implemented.
3. **Implement Input Sanitization**: Sanitize all user inputs to prevent malicious data from being processed.
4. **Regular Audits**: Conduct regular security audits and penetration tests to identify and mitigate vulnerabilities.

#### Secure Code Fix

Here is an example of how to implement server-side validation to prevent the vulnerability:

**Vulnerable Code**:
```python
@app.route('/api/purchase', methods=['POST'])
def purchase():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    price = data['price']
    # Process purchase
    return jsonify({"status": "success", "message": "Purchase successful"})
```

**Fixed Code**:
```python
@app.route('/api/purchase', methods=['POST'])
def purchase():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    # Fetch the actual price from the database
    actual_price = get_item_price_from_db(item_id)
    if data['price'] != actual_price:
        return jsonify({"status": "error", "message": "Invalid price"}), 400
    # Process purchase
    return jsonify({"status": "success", "message": "Purchase successful"})
```

### Conclusion

Business logic vulnerabilities are a critical aspect of web security that can lead to significant financial and reputational damage. By understanding the underlying principles and implementing proper mitigation strategies, you can protect your applications from such vulnerabilities.

### Practice Labs

For hands-on experience, you can use the following labs:
- **PortSwigger Web Security Academy**: Offers a variety of labs to practice identifying and exploiting business logic vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning about web security vulnerabilities.

By engaging with these labs, you can gain practical experience in detecting and mitigating business logic vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/02-Lab 1 Excessive trust in client side controls/00-Overview|Overview]] | [[02-Business Logic Vulnerabilities Excessive Trust in Client-Side Controls|Business Logic Vulnerabilities Excessive Trust in Client-Side Controls]]
