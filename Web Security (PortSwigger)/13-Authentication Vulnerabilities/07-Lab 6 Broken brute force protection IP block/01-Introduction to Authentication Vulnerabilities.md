---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Introduction to Authentication Vulnerabilities

Authentication vulnerabilities are critical weaknesses in web applications that allow attackers to gain unauthorized access to user accounts. One such vulnerability is the broken brute force protection, which occurs when a web application fails to effectively limit the number of login attempts an attacker can make. This allows the attacker to perform a brute-force attack, systematically trying different combinations of usernames and passwords until the correct one is found.

### What is Brute Force Attack?

A brute force attack is a method used by attackers to guess a password by trying every possible combination of characters until the correct one is found. This type of attack can be time-consuming but is often successful against weak or commonly used passwords.

### Why Does Brute Force Protection Matter?

Brute force attacks can be highly effective against poorly protected systems. Without proper brute force protection mechanisms, an attacker can repeatedly attempt to log in with different passwords until they succeed. This can lead to unauthorized access to sensitive data, financial losses, and reputational damage.

### How Does Brute Force Protection Work?

Effective brute force protection typically involves several mechanisms:

1. **Rate Limiting**: Limiting the number of login attempts within a certain time frame.
2. **Account Lockout**: Temporarily locking an account after a certain number of failed login attempts.
3. **IP Blocking**: Blocking the IP address of an attacker after multiple failed login attempts.
4. **Captcha Verification**: Requiring users to complete a captcha challenge after a certain number of failed login attempts.

### Real-World Example: CVE-2021-21972

In 2021, a significant vulnerability was discovered in the WordPress plugin "WPForms". The plugin had a broken brute force protection mechanism, allowing attackers to perform brute force attacks on the admin login page. This vulnerability was assigned the CVE identifier CVE-2021-21972. The lack of proper rate limiting and account lockout mechanisms made it possible for attackers to repeatedly attempt login attempts until they succeeded.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/07-Lab 6 Broken brute force protection IP block/00-Overview|Overview]] | [[02-Authentication Vulnerabilities Broken Brute Force Protection IP Block|Authentication Vulnerabilities Broken Brute Force Protection IP Block]]
