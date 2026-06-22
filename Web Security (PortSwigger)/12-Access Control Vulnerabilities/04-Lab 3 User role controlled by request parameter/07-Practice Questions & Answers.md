---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a broken access control vulnerability as demonstrated in the lab.**

The broken access control vulnerability occurs when the application fails to properly enforce access controls, allowing unauthorized users to perform actions reserved for privileged users. In this lab, the application uses a cookie named `admin` to determine whether a user has administrative privileges. By manipulating this cookie, a regular user can gain administrative access. Specifically, changing the value of the `admin` cookie from `false` to `true` grants access to the admin panel, which is normally restricted to administrators.

**Q2. How would you exploit the broken access control vulnerability in the lab to delete the user Carlos?**

To exploit the broken access control vulnerability and delete the user Carlos, follow these steps:

1. Log in to the application using the provided credentials.
2. Identify the `admin` cookie in the session cookies.
3. Change the value of the `admin` cookie from `false` to `true`.
4. Access the admin panel by navigating to `/admin`.
5. Use the admin panel to delete the user Carlos.

This process involves altering the `admin` cookie to bypass the access control mechanism and gain unauthorized administrative access.

**Q3. Why is it important to script the exploit in Python, and what are the key components of the script?**

Scripting the exploit in Python is important because it automates the process, making it repeatable and easier to debug. Key components of the script include:

1. **Importing necessary modules**: Import `requests`, `sys`, `urllib3`, and `BeautifulSoup` to handle HTTP requests, command-line arguments, SSL warnings, and HTML parsing respectively.
2. **Disabling SSL warnings**: Use `urllib3.disable_warnings()` to avoid SSL certificate verification issues.
3. **Setting up the proxy**: Configure the proxy settings to route requests through Burp Suite for debugging.
4. **Main function**: Define the `main` function to handle command-line arguments and initiate the session.
5. **Get CSRF token function**: Implement a function to extract the CSRF token from the login page.
6. **Login function**: Use the extracted CSRF token to log in with the provided credentials.
7. **Exploit access control vulnerability**: Set the `admin` cookie to `true` and access the admin panel to delete the user Carlos.
8. **Error handling**: Check for successful login and deletion of the user, and handle failures appropriately.

**Q4. How does the script handle the CSRF token during the login process?**

The script handles the CSRF token by extracting it from the login page and including it in the POST request to log in. Here’s how it works:

1. **Extract CSRF token**: Perform a GET request to the login page (`/login`) and parse the response to extract the CSRF token.
   ```python
   def get_csrf_token(s, url):
       r = s.get(url + "/login", verify=False, proxies=proxies)
       soup = BeautifulSoup(r.text, 'html.parser')
       csrf_token = soup.find("input", {'name': 'csrf'})['value']
       return csrf_token
   ```
2. **Use CSRF token in login request**: Include the CSRF token along with the username and password in the POST request to the login endpoint.
   ```python
   csrf_token = get_csrf_token(s, url)
   data = {
       'csrf': csrf_token,
       'username': 'your_username',
       'password': 'your_password'
   }
   r = s.post(url + "/login", data=data, verify=False, proxies=proxies)
   ```

By including the CSRF token, the script ensures that the login request is valid and avoids any security mechanisms designed to prevent cross-site request forgery attacks.

**Q5. What recent real-world examples demonstrate the impact of broken access control vulnerabilities?**

Broken access control vulnerabilities have led to significant breaches in various organizations. For example:

- **CVE-2020-1938**: A vulnerability in the Zoom API allowed unauthorized users to access sensitive information and perform actions reserved for administrators. This was due to improper validation of user roles and permissions.
- **Capital One Breach (2019)**: A misconfigured web application firewall allowed an attacker to access sensitive customer data. The breach occurred because the firewall did not properly restrict access to internal systems, leading to unauthorized access to over 100 million records.

These examples illustrate the critical importance of enforcing strict access controls and validating user permissions to prevent unauthorized access and data breaches.

---
<!-- nav -->
[[06-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/00-Overview|Overview]]
