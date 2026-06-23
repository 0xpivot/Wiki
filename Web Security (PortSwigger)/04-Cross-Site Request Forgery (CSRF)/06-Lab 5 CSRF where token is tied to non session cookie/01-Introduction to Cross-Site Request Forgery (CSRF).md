---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a user's browser into executing unwanted actions on a web application in which the user is currently authenticated. This attack exploits the trust that a web application has in the user's browser. The attacker does not need to know the user's credentials; instead, they leverage the fact that the user is already authenticated to the web application.

### Why CSRF Matters

CSRF attacks can lead to unauthorized transactions, such as transferring funds, changing passwords, or making purchases. These actions can result in financial loss, data theft, and other serious consequences. Therefore, it is crucial to understand how CSRF works and how to defend against it.

### How CSRF Works Under the Hood

To understand CSRF, let's break down the components involved:

1. **User**: The authenticated user who is tricked into performing unintended actions.
2. **Web Application**: The target application where the action is performed.
3. **Attacker**: The malicious actor who crafts the attack.
4. **Browser**: The medium through which the attack is executed.

#### Step-by-Step Mechanics

1. **Authentication**: The user logs into the web application and receives a session cookie.
2. **Attack Setup**: The attacker crafts a malicious link or script that performs an action on the web application.
3. **User Interaction**: The user clicks on the malicious link or visits a page containing the malicious script.
4. **Action Execution**: The user's browser sends a request to the web application, which includes the session cookie, thus authenticating the request.
5. **Unintended Action**: The web application executes the action as if it were initiated by the user.

### Real-World Example: CVE-2019-11510

CVE-2019-11510 is a real-world example of a CSRF vulnerability found in the WordPress REST API. The vulnerability allowed attackers to perform unauthorized actions, such as deleting posts, by tricking authenticated users into clicking on a malicious link. This demonstrates the real-world impact of CSRF attacks and the importance of implementing proper defenses.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/06-Lab 5 CSRF where token is tied to non session cookie/00-Overview|Overview]] | [[02-Lab Overview CSRF where Token is Tied to Non-Session Cookie|Lab Overview CSRF where Token is Tied to Non-Session Cookie]]
