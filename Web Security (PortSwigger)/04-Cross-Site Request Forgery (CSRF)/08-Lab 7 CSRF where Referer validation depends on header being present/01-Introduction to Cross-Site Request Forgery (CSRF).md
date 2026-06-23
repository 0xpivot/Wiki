---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. The attacker exploits the trust that the web application places in the user's browser session. This attack is particularly dangerous because it can be used to perform actions such as transferring funds, changing passwords, or making purchases without the user's knowledge or consent.

### What is CSRF?

CSRF attacks occur when an attacker crafts a malicious request that is sent from the victim's browser to a web application. The web application trusts the request because it comes from an authenticated session. The attacker does not need to know the user's credentials; they simply need to trick the user into performing an action that the attacker desires.

### Why Does CSRF Matter?

CSRF attacks are significant because they can lead to unauthorized actions being performed on behalf of the victim. This can result in financial loss, data theft, or other serious consequences. For example, if an attacker can trick a user into transferring money from their bank account, the consequences can be severe.

### How Does CSRF Work Under the Hood?

To understand how CSRF works, consider the following scenario:

1. **Victim Authentication**: The victim logs into a web application, such as a banking site.
2. **Attacker's Malicious Request**: The attacker crafts a malicious request that performs an action, such as transferring money.
3. **Victim Execution**: The attacker tricks the victim into executing the malicious request. This could be through a link, an image, or any other means that causes the victim's browser to send the request.
4. **Web Application Trust**: The web application trusts the request because it comes from an authenticated session and processes the action.

### Real-World Example: CVE-2018-14656

One real-world example of a CSRF vulnerability is CVE-2018-14656, which affected the WordPress plugin "WP GDPR Compliance." The vulnerability allowed attackers to delete all user data by crafting a malicious request that was executed by the victim's browser. This highlights the importance of implementing robust CSRF protections.

### Common Pitfalls Without CSRF Protection

Without proper CSRF protection, web applications are vulnerable to attacks that can lead to unauthorized actions being performed. This can result in financial loss, data theft, and other serious consequences. Therefore, it is crucial to implement effective CSRF defenses.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/00-Overview|Overview]] | [[02-Lab 7 CSRF Exploitation Using Referer Header Validation|Lab 7 CSRF Exploitation Using Referer Header Validation]]
