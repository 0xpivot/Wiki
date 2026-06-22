---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Lab Setup: CSRF Where Token Validation Depends on Request Method

In this lab, we will explore a scenario where the web application attempts to block CSRF attacks but only applies defenses to certain types of requests. Specifically, the email change functionality is vulnerable to CSRF because the token validation depends on the request method.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select the "Learning Path" and then choose "CSRF".
6. Select the second lab titled "CSRF where token validation depends on the request method".

### Lab Objective

The objective of this lab is to exploit the CSRF vulnerability to change the email address of the user. We will achieve this by hosting an HTML page on our exploit server that triggers the CSRF attack.

### Credentials

The lab provides the following credentials for logging into the web application:

- **Username**: `victim`
- **Password**: `password`

### Setting Up Burp Suite

Before proceeding, ensure that Burp Suite Professional is set up correctly:

1. Open Burp Suite Professional.
2. Configure the proxy settings to intercept traffic between the browser and the web application.
3. Set up the repeater tool to test and analyze requests.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/06-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/08-Practice Labs|Practice Labs]]
