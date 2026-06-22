---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding the Lab Environment

In this lab, we will focus on a specific type of Reflected XSS vulnerability where angle brackets (`<` and `>`) are HTML-encoded. This means that the server encodes these characters to prevent them from being interpreted as HTML tags. However, this encoding does not necessarily prevent all forms of XSS attacks.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL: `https://portswigger.net/web-security`.
2. Click on the "Sign up" button to create an account.
3. Log in to your account.
4. Navigate to the "Academy" section.
5. Select "All Labs".
6. Search for "cross-site scripting labs".
7. Find and open "Lab No. 7: Reflected XSS into Attribute with Angle Brackets, HTML Encoded".

Once you have accessed the lab, you will see a built-in browser and Burp Suite integrated into the environment. All your requests will be intercepted by Burp Proxy, allowing you to analyze and modify them.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/10-Real-World Examples|Real-World Examples]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[12-Understanding the Lab Scenario|Understanding the Lab Scenario]]
