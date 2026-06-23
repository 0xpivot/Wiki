---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are currently authenticated. This attack exploits the trust that a web application has in an authenticated user session. The attacker crafts a malicious request that appears to come from the authenticated user, thereby performing actions such as changing passwords, transferring funds, or posting unauthorized content.

### What is CSRF?

CSRF occurs when an attacker tricks a victim into submitting a request to a web application that the victim is authenticated against. The web application trusts the request because it comes from an authenticated user, but the actual intent of the request is controlled by the attacker.

#### Example Scenario

Consider a scenario where a user is logged into their bank account. An attacker sends the user an email with a link to a malicious website. When the user clicks the link, the malicious site sends a request to the bank's website to transfer money from the user's account to the attacker's account. Since the user is already authenticated with the bank, the bank's website processes the request as if it came from the user.

### Why Does CSRF Matter?

CSRF attacks are significant because they can lead to unauthorized actions being performed on behalf of the authenticated user. This can result in financial losses, data breaches, and other serious consequences. Understanding and preventing CSRF is crucial for securing web applications.

### How CSRF Works Under the Hood

To understand how CSRF works, let's break down the steps involved:

1. **Authentication**: The user logs into a web application and receives a session cookie.
2. **Malicious Request**: The attacker crafts a malicious request that includes the necessary parameters to perform an action on the web application.
3. **Victim Interaction**: The attacker tricks the victim into interacting with the malicious request, often through social engineering techniques like phishing emails or malicious websites.
4. **Request Execution**: When the victim interacts with the malicious request, the web application processes the request as if it came from the authenticated user.

### Real-World Examples

Recent real-world examples of CSRF vulnerabilities include:

- **CVE-2021-21972**: A CSRF vulnerability was found in the WordPress REST API, allowing attackers to create new users or modify existing ones.
- **CVE-2020-14182**: A CSRF vulnerability in the Cisco Webex Meetings Server allowed attackers to execute arbitrary commands on the server.

These examples highlight the importance of implementing robust CSRF protections in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/07-Lab 6 CSRF where token is duplicated in cookie/00-Overview|Overview]] | [[02-CSRF Prevention Techniques|CSRF Prevention Techniques]]
