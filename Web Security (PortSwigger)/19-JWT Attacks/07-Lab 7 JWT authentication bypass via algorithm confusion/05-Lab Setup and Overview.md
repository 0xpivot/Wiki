---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Lab Setup and Overview

To access the lab, follow these steps:

1. Visit [PortSwigger.net/Web Security](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Log in and navigate to the Academy section.
4. Search for the "JWT Authentication Bypass via Algorithm Confusion" lab.

This lab uses a JWT-based mechanism for handling sessions. The server uses a robust RSA key pair to sign and verify tokens. However, due to implementation flaws, this mechanism is vulnerable to algorithm confusion attacks.

### Objective of the Lab

The objective of this lab is to bypass the authentication mechanism by exploiting the algorithm confusion vulnerability. You will need to:

1. Obtain the server's public key.
2. Use this key to sign a modified session token.
3. Submit the modified token to gain unauthorized access.

---
<!-- nav -->
[[04-Introduction to JWT and Its Vulnerabilities|Introduction to JWT and Its Vulnerabilities]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[06-Detailed Steps of the Attack|Detailed Steps of the Attack]]
