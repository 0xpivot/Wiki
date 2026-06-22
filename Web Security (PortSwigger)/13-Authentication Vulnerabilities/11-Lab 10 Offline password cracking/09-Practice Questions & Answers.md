---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. What is the primary goal of the lab titled "Offline Password Cracking"?**

The primary goal of the lab titled "Offline Password Cracking" is to obtain Carlos's stay logged in cookie, which contains his password hash, and then crack the hash to retrieve his password. After obtaining the password, the user needs to log in as Carlos and delete his account from the my account page.

**Q2. How does the lab demonstrate the vulnerability associated with storing password hashes in cookies?**

The lab demonstrates the vulnerability by storing the user’s password hash in a cookie without proper security measures such as the `HttpOnly` flag. This makes the cookie accessible via JavaScript, allowing an attacker to exploit an XSS vulnerability to steal the cookie containing the password hash.

**Q3. Explain how the XSS vulnerability in the comment functionality is exploited to steal the cookie.**

To exploit the XSS vulnerability in the comment functionality, an attacker injects a malicious script into the comment field. The script, when executed by other users visiting the blog post, redirects their browser to an exploit server and sends the user's cookies, including the stay logged in cookie, to the server. This is achieved by setting `document.location` to the exploit server URL with the stolen cookie appended.

**Q4. Why is it important to avoid using online services like CrackStation for real-world hashes?**

Using online services like CrackStation for real-world hashes is considered a breach of information security practices. Such services can expose sensitive data and compromise user privacy. It is important to handle real-world hashes securely and use appropriate offline tools or methods that comply with legal and ethical standards.

**Q5. How does the presence of the `HttpOnly` flag affect the exploitability of the cookie in this scenario?**

The `HttpOnly` flag prevents JavaScript from accessing the cookie, thereby mitigating the risk of XSS attacks stealing the cookie. In this lab, the absence of the `HttpOnly` flag allowed the attacker to exploit the XSS vulnerability to steal the cookie containing the password hash. If the `HttpOnly` flag were present, the exploit would not have been possible through JavaScript injection.

**Q6. Describe the process of decoding and cracking the password hash obtained from Carlos's cookie.**

After obtaining Carlos's stay logged in cookie, the hash is decoded from Base64 encoding. The decoded string contains the username and the MD5 hash of the password. The MD5 hash is then submitted to an online cracking service like CrackStation to retrieve the plaintext password. In this case, the password was found to be "Once Upon a Time".

**Q7. What recent real-world example can illustrate the risks of storing password hashes insecurely?**

A notable recent example is the LinkedIn data breach in 2012, where millions of hashed passwords were stolen. Although the passwords were hashed, they were not salted, making them vulnerable to brute-force attacks. This highlights the importance of using secure hashing algorithms and practices, such as salting and using strong, unique salts for each password, to protect against such breaches.

---
<!-- nav -->
[[08-Understanding Authentication Vulnerabilities|Understanding Authentication Vulnerabilities]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/11-Lab 10 Offline password cracking/00-Overview|Overview]]
