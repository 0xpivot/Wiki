---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how username enumeration via account lockout works.**

Username enumeration via account lockout occurs when an application locks an account after a certain number of failed login attempts. An attacker can exploit this by repeatedly attempting to log in with various usernames and observing whether the account gets locked. If the account is locked, it indicates that the username exists and is valid. This method allows attackers to identify valid usernames, which they can then use to attempt to brute-force the corresponding passwords.

**Q2. How would you exploit a username enumeration vulnerability using Burp Suite Intruder?**

To exploit a username enumeration vulnerability using Burp Suite Intruder, follow these steps:

1. Identify a login form on the target website.
2. Send a login request through Burp Suite Proxy.
3. Use Burp Suite Intruder to send multiple requests with different usernames.
4. Configure Intruder to use a list of candidate usernames and a fixed empty password.
5. Set the attack type to "Cluster Bomb" to send each username multiple times.
6. Analyze the responses to determine which usernames trigger an account lockout message.
7. Once a valid username is identified, switch to brute-forcing the password using a similar approach.

Here is an example configuration:

```plaintext
Request:
POST /login HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

username=USERNAME&password=

Payloads:
Position 1: Cluster Bomb
- Usernames: carlos, admin, user, acid
- Passwords: (empty)

Attack Type: Cluster Bomb
```

**Q3. Why is it important to understand the logic behind account lockout mechanisms?**

Understanding the logic behind account lockout mechanisms is crucial because it helps in identifying potential vulnerabilities. For instance, if the account lockout mechanism does not properly handle valid passwords during a lockout period, an attacker might still be able to brute-force the password. This was demonstrated in the lab where the correct password allowed access despite the account being locked out temporarily. By understanding such flaws, security professionals can design more robust systems and mitigate risks effectively.

**Q4. How would you configure a secure account lockout mechanism to prevent enumeration attacks?**

To configure a secure account lockout mechanism that prevents enumeration attacks, consider the following best practices:

1. **Limit Login Attempts**: Implement a reasonable limit on the number of failed login attempts before locking the account.
2. **Soft Lockout Period**: After the account is locked, enforce a soft lockout period (e.g., 1 minute) before allowing further login attempts.
3. **Consistent Error Messages**: Ensure that the error messages returned to the user are consistent regardless of whether the username exists or not. For example, always return "Invalid username or password" without specifying which part is incorrect.
4. **Rate Limiting**: Apply rate limiting to slow down automated login attempts.
5. **Account Lockout Notification**: Notify the user via email or SMS when their account is locked out.

Example configuration:

```plaintext
if (failed_attempts >= 5) {
    lock_account(username);
    notify_user(username);
    reset_failed_attempts(username);
    set_soft_lockout_period(username, 60); // 1 minute
}
```

**Q5. Discuss recent real-world examples of vulnerabilities related to account lockout mechanisms.**

One notable example is the CVE-2021-26084, which affected several versions of Microsoft Exchange Server. This vulnerability allowed attackers to bypass account lockout policies by exploiting a flaw in the server's authentication mechanism. Specifically, the server did not correctly handle certain types of requests, allowing attackers to make repeated login attempts without triggering the lockout mechanism. This enabled attackers to perform brute-force attacks on user accounts, leading to unauthorized access.

Another example is the CVE-2020-1938, which affected Cisco Identity Services Engine (ISE). This vulnerability allowed attackers to bypass account lockout policies by exploiting a flaw in the server's handling of RADIUS authentication requests. The flaw allowed attackers to make repeated login attempts without triggering the lockout mechanism, enabling them to perform brute-force attacks on user accounts.

In both cases, the vulnerabilities were due to flaws in the implementation of account lockout mechanisms, highlighting the importance of thorough testing and secure coding practices.

---
<!-- nav -->
[[02-Authentication Vulnerabilities Username Enumeration via Account Lockout|Authentication Vulnerabilities Username Enumeration via Account Lockout]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/08-Lab 7 Username enumeration via account lock/00-Overview|Overview]]
