---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Understanding Two-Factor Authentication (2FA)

Two-Factor Authentication (2FA) is an essential security measure used to verify the identity of a user attempting to access a system or service. It adds an extra layer of security beyond the traditional username and password combination. In 2FA, users are required to provide two different forms of identification: something they know (like a password) and something they have (like a code sent to their phone).

### Why 2FA Matters

2FA significantly reduces the risk of unauthorized access even if an attacker manages to obtain a user's password. This is particularly important in today’s digital landscape where data breaches and credential theft are increasingly common. According to the Verizon Data Breach Investigations Report (DBIR), stolen credentials are a leading cause of data breaches. Implementing 2FA can help mitigate this risk.

### How 2FA Works Under the Hood

Let's break down the process of 2FA:

1. **User Authentication**: The user provides their username and password.
2. **First Request**: A POST request containing the username and password is sent to the server.
3. **Second Request**: Upon successful authentication, the server sends a GET request to the `/login_to` endpoint, which triggers the sending of a 2FA code to the user's registered email or phone number.
4. **Third Request**: The user receives the 2FA code and enters it into the application. A POST request is then sent to the server with the 2FA code.
5. **Final Authentication**: The server verifies the 2FA code and grants access if everything checks out.

### Example Scenario

Consider a web application where a user logs in with their credentials. Here’s a detailed breakdown of the HTTP requests involved:

#### First Request: Username and Password

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 31

username=regular_user&password=user_password
```

#### Second Request: Triggering 2FA Code

```http
GET /login_to HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

#### Third Request: Entering 2FA Code

```http
POST /verify_2fa HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

code=0932
```

### Common Pitfalls and Vulnerabilities

Despite its benefits, 2FA is not immune to vulnerabilities. One common issue is **broken logic** in the implementation of 2FA. This can occur due to poor coding practices or misunderstandings about how the 2FA process should work.

#### Real-World Example: CVE-2021-3129

In 2021, a critical vulnerability was discovered in the 2FA implementation of several popular web applications (CVE-2021-3129). The vulnerability allowed attackers to bypass 2FA by manipulating the timing of requests. This highlights the importance of thorough testing and secure coding practices.

### How to Prevent / Defend Against Broken Logic in 2FA

#### Secure Coding Practices

1. **Validate Inputs**: Ensure that all inputs, including 2FA codes, are properly validated.
2. **Use Strong Algorithms**: Use strong cryptographic algorithms for generating and verifying 2FA codes.
3. **Rate Limiting**: Implement rate limiting to prevent brute-force attacks on the 2FA mechanism.

#### Detection and Prevention

1. **Automated Testing**: Use tools like Burp Suite to test the 2FA implementation for vulnerabilities.
2. **Logging and Monitoring**: Monitor access logs for suspicious activity, such as repeated failed 2FA attempts.
3. **Secure Configuration**: Harden configurations to ensure that 2FA cannot be bypassed through misconfiguration.

#### Secure vs. Vulnerable Code Examples

##### Vulnerable Code

```python
def verify_2fa(user_id, code):
    user = get_user_by_id(user_id)
    if user['2fa_code'] == code:
        return True
    return False
```

##### Secure Code

```python
import time

def verify_2fa(user_id, code):
    user = get_user_by_id(user_id)
    if user['2fa_code'] == code and time.time() - user['2fa_timestamp'] < 60:
        return True
    return False
```

### Practical Labs

To gain hands-on experience with 2FA vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on 2FA and related vulnerabilities.
- **OWASP Juice Shop**: Contains various security challenges, including those related to 2FA.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including 2FA issues.

### Conclusion

Understanding and implementing 2FA correctly is crucial for securing web applications against unauthorized access. By following secure coding practices, thoroughly testing implementations, and monitoring for suspicious activity, organizations can significantly enhance their security posture.

---
<!-- nav -->
[[08-Multi-Threading in Web Security|Multi-Threading in Web Security]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/00-Overview|Overview]] | [[10-Understanding the 2FA Process|Understanding the 2FA Process]]
