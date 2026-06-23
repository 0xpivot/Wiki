---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Authentication Bypass via Flawed Signature Verification

### Background Theory

JSON Web Tokens (JWTs) are a widely adopted method for transmitting information between parties as a JSON object. They are compact, URL-safe means of representing claims to be transferred between two parties. JWTs consist of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm being used.
2. **Payload**: Contains the claims. Claims are statements about an entity (typically, the user) and additional data.
3. **Signature**: Used to verify the integrity of the message and ensure that the token was not tampered with.

The structure of a JWT looks like this:

```
<base64UrlEncode(header)>.<base64UrlEncode(payload)>.<signature>
```

### Importance of JWT Security

JWTs are often used for authentication and authorization purposes. However, if the implementation is flawed, especially in terms of signature verification, it can lead to severe security vulnerabilities. An attacker could potentially bypass authentication by manipulating the JWT.

### Real-World Example: CVE-2021-3278

In 2021, a critical vulnerability (CVE-2021-3278) was discovered in the `jwt-go` library, which is widely used in Go applications. This vulnerability allowed attackers to bypass authentication by manipulating the JWT. The issue stemmed from the fact that the library did not properly validate the token's signature, leading to unauthorized access.

### Steps to Extract CSRF Token

Before diving into JWT attacks, let's understand how to extract a CSRF token, which is often required for logging in to web applications.

#### Step-by-Step Process

1. **Perform a GET Request**:
   - Send a GET request to the `/login` endpoint to retrieve the login page.
   - This request may contain a CSRF token embedded within the HTML.

2. **Parse the Response**:
   - Use a library like `BeautifulSoup` to parse the HTML response.
   - Locate the `<input>` element with the `name` attribute set to `CSRF`.

3. **Extract the CSRF Token**:
   - Retrieve the value of the `value` attribute from the `<input>` element.

Here’s a detailed breakdown of the process:

```python
import requests
from bs4 import BeautifulSoup

def get_csrf_token(login_url):
    # Perform a GET request to the login endpoint
    response = requests.get(login_url, verify=False, proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})
    
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the input element with the name attribute set to CSRF
    csrf_input = soup.find('input', {'name': 'CSRF'})
    
    # Extract the value of the CSRF token
    csrf_token = csrf_input['value']
    
    return csrf_token

# Example usage
login_url = 'http://example.com/login'
csrf_token = get_csrf_token(login_url)
print(f'Extracted CSRF token: {csrf_token}')
```

### Explanation of Each Component

1. **GET Request**:
   - The `requests.get()` function sends a GET request to the specified URL.
   - The `verify=False` parameter disables SSL certificate verification, which is useful during testing but should be avoided in production environments.
   - The `proxies` parameter specifies a proxy server, typically used for debugging purposes with tools like Burp Suite.

2. **Parsing HTML**:
   - `BeautifulSoup` is used to parse the HTML content of the response.
   - The `find()` method searches for the first occurrence of an `<input>` element with the `name` attribute set to `CSRF`.

3. **Extracting CSRF Token**:
   - The `value` attribute of the `<input>` element contains the CSRF token, which is extracted and returned.

### Potential Pitfalls

- **SSL Verification**: Disabling SSL verification (`verify=False`) can expose your application to man-in-the-middle attacks. Always enable SSL verification in production environments.
- **Proxy Configuration**: Using a proxy server for debugging can introduce latency and potential security risks. Ensure that the proxy server is secure and trusted.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Enable SSL Verification**:
   - Always enable SSL verification to protect against man-in-the-middle attacks.
   
   ```python
   response = requests.get(login_url, verify=True)
   ```

2. **Use Strong CSRF Protection**:
   - Implement strong CSRF protection mechanisms, such as regenerating tokens after each successful login and ensuring that tokens are tied to specific sessions.

3. **Validate JWT Signatures**:
   - Ensure that JWT signatures are properly validated. Use libraries that enforce strict validation rules.

#### Detection and Prevention

1. **Static Code Analysis**:
   - Use static code analysis tools to identify potential issues in JWT handling and CSRF token management.
   
   ```bash
   # Example using Bandit for Python
   bandit -r .
   ```

2. **Dynamic Analysis**:
   - Conduct dynamic analysis using tools like Burp Suite to test for vulnerabilities in JWT and CSRF implementations.

3. **Penetration Testing**:
   - Regularly conduct penetration testing to identify and mitigate security weaknesses.

### Conclusion

Extracting and managing CSRF tokens is a crucial step in the authentication process. Understanding the underlying mechanisms and potential pitfalls is essential for securing web applications. By following best practices and implementing robust security measures, you can significantly reduce the risk of authentication bypass attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/02-Introduction to JWT Attacks|Introduction to JWT Attacks]] | [[Web Security (PortSwigger)/19-JWT Attacks/02-Lab 2 JWT authentication bypass via flawed signature verification/00-Overview|Overview]] | [[04-Introduction to JWT and Its Structure|Introduction to JWT and Its Structure]]
