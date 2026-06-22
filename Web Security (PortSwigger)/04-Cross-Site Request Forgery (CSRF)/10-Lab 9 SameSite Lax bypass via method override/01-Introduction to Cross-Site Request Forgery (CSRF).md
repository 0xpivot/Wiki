---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. The attacker exploits the trust that the web application places in the user's browser session. This attack can be particularly dangerous because it leverages the user's existing authentication to perform malicious actions.

### What is CSRF?

CSRF occurs when an attacker crafts a malicious request that is executed by the victim's browser. The request is sent to a web application that the victim is already authenticated with. Since the request originates from the victim's browser, the web application assumes it is a legitimate action initiated by the user.

#### Example Scenario

Consider a banking website where a user is logged in. An attacker could craft a link that, when clicked, transfers money from the user's account to the attacker's account. If the user clicks the link, the bank's server will execute the transfer because the user is already authenticated.

### Why Does CSRF Matter?

CSRF attacks can lead to significant financial loss, data theft, and other malicious activities. They exploit the trust between the user and the web application, making them difficult to detect and prevent.

### How Does CSRF Work Under the Hood?

To understand CSRF, we need to look at the HTTP protocol and how web applications handle requests. When a user interacts with a web application, their browser sends HTTP requests to the server. These requests include cookies that contain session information, allowing the server to authenticate the user.

#### Steps in a CSRF Attack

1. **Authentication**: The victim logs into a web application, establishing a session.
2. **Malicious Request**: The attacker crafts a malicious request that performs an action on the web application.
3. **Execution**: The victim's browser executes the malicious request, sending it to the web application.
4. **Action Execution**: The web application processes the request, assuming it is a legitimate action from the authenticated user.

### Real-World Examples

#### Recent Breaches

One notable example is the CSRF attack on the Tesla Model S car. In 2016, researchers discovered that an attacker could send a malicious link to a Tesla owner, causing the car to unlock and start. This was possible because the Tesla app did not properly implement CSRF protection.

#### CVEs

CVE-2021-21972 is a recent example where a CSRF vulnerability was found in the WordPress plugin "WP User Frontend." This allowed attackers to perform unauthorized actions, such as changing user passwords.

### Lab Setup

In this lab, we will focus on a specific type of CSRF attack that bypasses the `SameSite` attribute set to `Lax`. The `SameSite` attribute is designed to mitigate CSRF attacks by controlling whether cookies are sent with cross-site requests.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select "All Labs".
6. Search for "cross-site request forgery" labs.
7. Find and open lab number nine titled "SameSite Lacks Bypass via method override".

### Lab Objective

The objective of this lab is to perform a CSRF attack that changes the victim's email address. The change email function is vulnerable to CSRF, and you should use the provided exploit server to host your attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/10-Lab 9 SameSite Lax bypass via method override/00-Overview|Overview]] | [[02-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]]
