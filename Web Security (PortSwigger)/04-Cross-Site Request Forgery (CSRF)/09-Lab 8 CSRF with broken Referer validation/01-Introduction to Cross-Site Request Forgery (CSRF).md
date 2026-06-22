---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. The attacker exploits the trust that the web application places in the user's browser to perform actions that the user did not intend to perform. This can lead to unauthorized transactions, data modification, or other malicious activities.

### What is CSRF?

CSRF attacks rely on the fact that web applications often trust the requests coming from the user's browser without verifying their authenticity. An attacker crafts a malicious request and tricks the victim into sending it to the target web application. Since the victim is already authenticated with the application, the application processes the request as if it were legitimate.

#### Example Scenario

Consider a banking website where a user is logged in and has the ability to transfer funds. An attacker could create a malicious link or embed a script in a webpage that, when clicked or loaded, sends a request to the bank's server to transfer money from the victim's account to the attacker's account. If the victim clicks the link or visits the malicious page, the bank's server will process the request because the victim is already authenticated.

### Why Does CSRF Matter?

CSRF attacks can have severe consequences, including financial loss, data theft, and reputational damage. They exploit the trust relationship between the user and the web application, making them particularly dangerous. Understanding how CSRF works and how to defend against it is crucial for both developers and users.

### How CSRF Works Under the Hood

To understand how CSRF works, let's break down the components involved:

1. **Victim**: The user who is authenticated with the web application.
2. **Attacker**: The person who wants to trick the victim into performing an action.
3. **Web Application**: The target application where the action is performed.
4. **Malicious Request**: The crafted request sent by the attacker.

The attacker crafts a request that performs an action on the web application. This request is embedded in a link, image, or script that the victim is likely to interact with. When the victim interacts with the malicious content, the request is sent to the web application, and since the victim is authenticated, the web application processes the request as if it were legitimate.

### Real-World Examples

Recent real-world examples of CSRF vulnerabilities include:

- **CVE-2021-21972**: A CSRF vulnerability was found in the WordPress plugin "WP User Avatar." An attacker could force a logged-in user to upload an avatar from a remote URL, potentially leading to arbitrary code execution.
- **CVE-2020-14882**: A CSRF vulnerability was discovered in the "WordPress REST API" plugin. An attacker could force a logged-in user to delete posts or modify settings.

These examples highlight the importance of implementing robust defenses against CSRF attacks.

### Detection and Prevention

Detecting and preventing CSRF attacks involves several strategies:

1. **Token-Based Protection**: Using unique tokens for each session and validating these tokens with each request.
2. **SameSite Cookies**: Configuring cookies to be sent only in first-party contexts.
3. **Referer Header Validation**: Checking the `Referer` header to ensure requests come from the same origin.
4. **Content Security Policy (CSP)**: Implementing CSP to restrict the sources of content that can be loaded.

### Lab Setup

In this lab, we will explore a scenario where the `Referer` header validation is broken, allowing an attacker to bypass the protection mechanism. We will use the PortSwigger Web Security Academy to set up and demonstrate the attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/00-Overview|Overview]] | [[02-Lab 8 CSRF with Broken Referer Validation|Lab 8 CSRF with Broken Referer Validation]]
