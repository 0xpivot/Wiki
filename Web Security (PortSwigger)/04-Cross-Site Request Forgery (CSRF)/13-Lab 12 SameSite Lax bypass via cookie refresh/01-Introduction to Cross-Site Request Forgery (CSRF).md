---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a user's browser into executing unwanted actions on a web application in which the user is authenticated. This attack exploits the trust that a web application places in the user's browser. The attacker crafts malicious requests that appear to come from the authenticated user, thus performing actions on their behalf without their knowledge or consent.

### What is CSRF?

CSRF attacks rely on the fact that web applications often trust the requests coming from a user's browser. When a user is authenticated to a web application, their browser sends cookies and other authentication tokens with each request to the server. An attacker can exploit this trust by crafting a malicious request that appears to come from the authenticated user.

### Why Does CSRF Matter?

CSRF attacks can lead to significant security issues, such as unauthorized transactions, data modification, or even account takeover. For example, an attacker could trick a user into changing their email address, which could then be used to reset the password and take control of the account.

### How Does CSRF Work Under the Hood?

To understand how CSRF works, let's break down the steps involved:

1. **User Authentication**: The user logs into a web application and receives session cookies or tokens.
2. **Malicious Request**: The attacker crafts a malicious request that includes actions the user would normally perform, such as changing an email address.
3. **Tricking the User**: The attacker tricks the user into clicking on a link or loading a page that contains the malicious request.
4. **Browser Execution**: The user's browser, which is authenticated to the web application, sends the malicious request to the server.
5. **Action Execution**: The server executes the action based on the authenticated session, without verifying the intent of the user.

### Real-World Example: CVE-2019-11510

One notable example of a CSRF vulnerability is CVE-2019-11510, which affected the WordPress REST API. This vulnerability allowed attackers to craft malicious requests that could modify user settings, including email addresses and passwords. By tricking users into clicking on a link, attackers could change the email address associated with the user's account, potentially leading to account takeover.

### Common Pitfalls Without CSRF Protection

Without proper CSRF protection, web applications are vulnerable to various attacks. Users may unknowingly execute actions that compromise their accounts or sensitive data. This can lead to financial losses, data breaches, and loss of trust in the web application.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/13-Lab 12 SameSite Lax bypass via cookie refresh/00-Overview|Overview]] | [[02-Lab 12 SameSite Lax Bypass via Cookie Refresh|Lab 12 SameSite Lax Bypass via Cookie Refresh]]
