---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Introduction to 2FA Broken Logic

In this section, we will delve into the intricacies of a common vulnerability found in two-factor authentication (2FA) systems: broken logic. This issue arises when the logic governing the authentication process contains flaws that can be exploited by attackers. Understanding this vulnerability is crucial for both developers and security professionals to ensure robust authentication mechanisms.

### What is Two-Factor Authentication (2FA)?

Two-Factor Authentication (2FA) is a security mechanism that requires users to provide two different authentication factors to gain access to a system. These factors typically fall into one of three categories:

1. **Something you know** (e.g., password)
2. **Something you have** (e.g., mobile phone, hardware token)
3. **Something you are** (e.g., biometric data)

The combination of these factors significantly enhances security by making it much harder for unauthorized individuals to gain access.

### Why is 2FA Important?

2FA adds an extra layer of security to the authentication process. Even if an attacker manages to obtain a user's password, they would still need access to the second factor (such as a one-time password sent to the user's mobile device) to successfully authenticate. This makes it much more difficult for attackers to compromise accounts.

### Real-World Examples of 2FA Vulnerabilities

Recent breaches and vulnerabilities have highlighted the importance of proper implementation of 2FA. For instance, in 2021, a vulnerability in the 2FA system of a popular cryptocurrency exchange allowed attackers to bypass 2FA and steal funds. This incident underscores the critical nature of ensuring that 2FA systems are implemented correctly.

### Lab Setup

To understand and exploit the 2FA broken logic vulnerability, we will use the Web Security Academy provided by PortSwigger. You can sign up for an account at [portswigger.net/web-security](https://portswigger.net/web-security).

Once you have an account, follow these steps to access the lab:

1. Log in to your account.
2. Click on **Academy**.
3. Select **All Labs**.
4. Search for **authentication labs**.
5. Select **Lab Number 8: 2FA Broken Logic**.

### Lab Overview

In this lab, you will exploit a 2FA logic flaw to access Carlos' account. You have the following information:

- **Carlos's username**: `carlos`
- **Access to the email server**: You can receive 2FA verification codes.

Your goal is to exploit the 2FA logic flaw to gain access to Carlos' account.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/00-Overview|Overview]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/02-Introduction to Authentication Vulnerabilities|Introduction to Authentication Vulnerabilities]]
