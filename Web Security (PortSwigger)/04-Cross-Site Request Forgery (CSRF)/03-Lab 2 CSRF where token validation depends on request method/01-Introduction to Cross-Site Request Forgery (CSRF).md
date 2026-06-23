---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are currently authenticated. This attack exploits the trust that a web application has in the user's browser session. The attacker crafts a malicious request that appears to come from the victim's browser, thereby bypassing the authentication mechanisms.

### What is CSRF?

CSRF occurs when an attacker tricks a victim into performing an action on a website where the victim is authenticated. The attacker does not need to know the victim's credentials; instead, they leverage the fact that the victim is already logged in to the site. The attack typically involves embedding a malicious link, form, or JavaScript code within a webpage that the victim visits.

### Why Does CSRF Matter?

CSRF attacks can lead to serious consequences, such as unauthorized transactions, data modification, or account hijacking. For instance, an attacker could trick a victim into transferring money from their bank account or changing their email address on a social media platform. These actions can result in financial loss, identity theft, or other severe repercussions.

### How Does CSRF Work Under the Hood?

To understand how CSRF works, consider the following steps:

1. **Victim Authentication**: The victim logs into a web application and receives a session cookie.
2. **Malicious Link**: The attacker crafts a malicious link or form that performs an action on the web application.
3. **Victim Interaction**: The victim clicks on the malicious link or submits the form, which sends a request to the web application.
4. **Session Cookie**: Since the victim is authenticated, the request includes the session cookie, making the web application believe the request came from the victim.
5. **Action Execution**: The web application executes the action specified in the request, often without further verification.

### Real-World Example: CVE-2021-21972

In 2021, a CSRF vulnerability was discovered in the WordPress REST API (CVE-2021-21972). This vulnerability allowed attackers to perform various actions, such as creating new posts or modifying existing ones, without needing the victim's credentials. The attack relied on the victim being logged into their WordPress account and clicking on a malicious link.

### Common Pitfalls Without CSRF Protection

Without proper CSRF protection, web applications are vulnerable to these attacks. Some common pitfalls include:

- **No Token Validation**: Not validating tokens for every request.
- **Incomplete Token Validation**: Only validating tokens for certain types of requests.
- **Token Leakage**: Exposing tokens through predictable patterns or weak generation algorithms.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[02-CSRF Attack Scenario Token Validation Depending on Request Method|CSRF Attack Scenario Token Validation Depending on Request Method]]
