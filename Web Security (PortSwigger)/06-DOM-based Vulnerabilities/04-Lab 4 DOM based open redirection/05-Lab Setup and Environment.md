---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Lab Setup and Environment

To understand and exploit DOM-based open redirection, we will use the PortSwigger Web Security Academy. This lab environment provides a controlled setting to practice and learn about web security vulnerabilities.

### Accessing the Lab

1. **Sign Up**: Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security) and sign up for an account.
2. **Navigate to Labs**: Once logged in, navigate to the "Academy" section and select "All Labs".
3. **Search for Lab**: Search for "DOM-based vulnerabilities" and find the lab titled "DOM-based Open Redirection".

### Setting Up Burp Suite

Burp Suite is a powerful tool for web application security testing. We will use it to intercept and modify HTTP requests.

1. **Start Burp Suite**: Launch Burp Suite and configure it to act as a proxy.
2. **Configure Browser**: Set your browser to use Burp Suite as a proxy.
3. **Access Lab**: Navigate to the lab URL using your configured browser.

### Initial Exploration

Once you have accessed the lab, the first step is to explore the page and identify any potential JavaScript that could be manipulated.

1. **Inspect Source Code**: Right-click on the page and select "View Page Source". Look for any JavaScript that reads URL parameters or performs actions based on user input.
2. **Intercept Requests**: Use Burp Suite to intercept and analyze HTTP requests. This will help you understand how the application processes URL parameters.

---
<!-- nav -->
[[04-How to Prevent  Defend Against DOM-Based Open Redirection|How to Prevent  Defend Against DOM-Based Open Redirection]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[06-Understanding DOM-Based Open Redirection|Understanding DOM-Based Open Redirection]]
