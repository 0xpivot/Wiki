---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what an authentication vulnerability is and provide an example.**

An authentication vulnerability arises from an insecure implementation of the authentication mechanisms in an application. This could be due to design flaws, business logic flaws, or configuration flaws. An example of an authentication vulnerability is weak password complexity requirements, where an application allows users to set very short or simple passwords, making it easier for attackers to guess or brute-force the passwords.

**Q2. How can default credentials contribute to authentication vulnerabilities? Provide a recent real-world example.**

Default credentials can lead to authentication vulnerabilities if they are not changed upon deployment. Attackers often use default credentials found in documentation or online to gain unauthorized access to systems. A recent example is the widespread use of default credentials in IoT devices, leading to the Mirai botnet attacks, where attackers exploited default login credentials to take control of numerous devices.

**Q3. Describe the Consumer Authentication Strength Maturity Model (CAST) and its importance.**

The CAST model helps users identify their current level of authentication strength and potential vulnerabilities. It ranges from Level 1 (shared passwords across multiple sites) to Level 6 (passwordless authentication). The importance lies in guiding users towards stronger authentication methods, such as multi-factor authentication (MFA), to protect against credential stuffing and other attacks.

**Q4. How can an application be vulnerable to brute force attacks on authentication mechanisms?**

An application is vulnerable to brute force attacks if it does not enforce proper restrictions on authentication attempts. For instance, if an application allows unlimited login attempts without locking out the account or imposing delays, an attacker can systematically try different combinations of usernames and passwords until they succeed. This is particularly risky for pages like the login, one-time password (OTP), or multi-factor authentication (MFA) pages.

**Q5. Explain how verbal error messages can be exploited to enumerate valid usernames.**

Verbal error messages can reveal whether a username is valid or not. For example, if an application returns an error message like "Incorrect password" when a valid username is entered but an incorrect password is provided, and "Invalid username" when an invalid username is entered, an attacker can use these messages to determine valid usernames by submitting various usernames and observing the responses.

**Q6. Why is it important to use HTTPS for transmitting user credentials? Provide an example of an intercepted HTTP request.**

HTTPS ensures that user credentials are transmitted securely over an encrypted channel, preventing interception by attackers. An example of an intercepted HTTP request might show a username and password sent in clear text, such as:

```
GET /login?username=admin&password=12345 HTTP/1.1
Host: vulnerableapp.com
```

In contrast, an HTTPS request would appear as encrypted data, such as:

```
POST /login HTTP/1.1
Host: secureapp.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 32

username=admin&password=12345
```

Here, the actual content is encrypted, making it unreadable to an attacker.

**Q7. Discuss the risks associated with insecure storage of credentials in a backend database.**

Storing credentials insecurely in a backend database, such as in plain text or using weak hashing algorithms, poses significant risks. If the database is compromised, attackers can easily obtain user passwords. For example, if passwords are stored in plain text, an attacker can directly use them to log in. Even if passwords are hashed using weak algorithms like MD5, they can be cracked relatively quickly. Proper practices include using strong, salted hashing algorithms like bcrypt or Argon2 to protect stored passwords.

**Q8. How can multi-stage login mechanisms be exploited if not properly designed?**

Multi-stage login mechanisms can be exploited if they lack proper session management and validation. For example, if the verification code is not tied to the user ID and the session is tracked using a cookie that can be manipulated, an attacker could log in with their own credentials and then change the cookie to target another user’s account. This allows the attacker to compromise any user’s account by using their own verification code and manipulating the session cookie.

---
<!-- nav -->
[[27-Weak Password Requirements|Weak Password Requirements]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]]
