---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Lab Setup and Environment

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the "Sign Up" button to create an account if you haven't already.
3. Once logged in, navigate to the "Academy" section.
4. Search for "cross-site scripting labs".
5. Locate and open lab number 18 titled "Reflected XSS into HTML Context with all tags blocked except custom ones".

The lab environment includes a built-in browser and Burp Suite, which intercepts all your requests. You can use either the professional or community edition of Burp Suite for this lab.

### Understanding the Lab Goal

The primary objective of this lab is to perform a cross-site scripting attack that injects a custom tag and automatically alerts on the document.cookie. This means that the injected script should display the cookies of the user when the page is loaded.

---
<!-- nav -->
[[13-Identifying Client-Supplied Input|Identifying Client-Supplied Input]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[15-Lab Walkthrough Reflected XSS with Custom Tags|Lab Walkthrough Reflected XSS with Custom Tags]]
