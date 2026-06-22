---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Detection and Prevention of Brute Force Attacks

### Detection

To detect brute force attacks, organizations should monitor login attempts and look for patterns indicative of automated attacks. This includes:

1. **Rate Limiting**: Implement rate limiting to restrict the number of login attempts within a given time frame.
2. **Logging and Monitoring**: Log all login attempts and monitor for unusual activity, such as multiple failed attempts from the same IP address.
3. **Behavioral Analysis**: Use behavioral analysis tools to identify patterns of behavior that are indicative of brute force attacks.

### Prevention

To prevent brute force attacks, organizations should implement the following measures:

1. **Lockout Mechanisms**: Implement a lockout mechanism that temporarily locks an account after a certain number of failed login attempts.
2. **Captcha**: Use CAPTCHA to prevent automated bots from making login attempts.
3. **Multi-Factor Authentication (MFA)**: Require multi-factor authentication to ensure that even if an attacker guesses the password, they still need the second factor to authenticate.

### Secure Coding Practices

#### Vulnerable Code

```python
def login(username, password, otp):
    # Check if the username and password are correct
    if check_credentials(username, password):
        # Check if the OTP is correct
        if check_otp(otp):
            return "Login successful"
        else:
            return "Incorrect OTP"
    else:
        return "Invalid username or password"
```

#### Secure Code

```python
def login(username, password, otp):
    # Check if the username and password are correct
    if check_credentials(username, password):
        # Check if the OTP is correct
        if check_otp(otp):
            return "Login successful"
        else:
            # Increment failed OTP attempts
            increment_failed_attempts(username)
            if get_failed_attempts(username) >= 3:
                lock_account(username)
                return "Account locked due to multiple failed attempts"
            else:
                return "Incorrect OTP"
    else:
        return "Invalid username or password"
```

### Configuration Hardening

#### Nginx Configuration

```nginx
http {
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/s;

    server {
        location /login {
            limit_req zone=login_limit burst=5 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

#### Apache Configuration

```apache
<IfModule mod_security2.c>
    SecRule REQUEST_METHOD "@streq POST" \
        "id:'100',phase:1,t:none,nolog,pass,\
        initcol:ip=%{REMOTE_ADDR},\
        setvar:ip.login_attempts=+1,\
        expirevar:ip.login_attempts=600"
</IfModule>
```

### Real-World Example: Twitter Hack

In the Twitter hack of 2020, attackers exploited a vulnerability in Twitter’s internal systems to bypass 2FA. This highlights the importance of securing both the authentication mechanisms and the underlying infrastructure.

### Hands-On Labs

For hands-on practice with 2FA and brute force attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including 2FA and brute force attacks.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training. It includes scenarios where 2FA can be bypassed through brute force attacks.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training that includes vulnerabilities related to 2FA and brute force attacks.

By thoroughly understanding and implementing these security measures, organizations can significantly reduce the risk of brute force attacks on 2FA systems.

---
<!-- nav -->
[[05-Brute Force Attacks on 2FA|Brute Force Attacks on 2FA]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/15-Lab 14 2FA bypass using a brute force attack/00-Overview|Overview]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/15-Lab 14 2FA bypass using a brute force attack/07-Practice Questions & Answers|Practice Questions & Answers]]
