---
course: Web Security
topic: SQL Injection
tags: [web-security]
---

## Lab Setup

To understand and practice SQL Injection, we will use the Web Security Academy provided by PortSwigger. This platform offers a variety of labs that simulate real-world vulnerabilities, including SQL Injection.

### Accessing the Lab

1. **Sign Up**: Visit the URL `portswigger.net/web-security` and click on the sign-up button to create an account.
2. **Log In**: Once you have an account, log in to the Web Security Academy.
3. **Navigate to Labs**: Click on the "Academy" tab and select "All Labs".
4. **Search for Lab**: Use the search function to find the "Visible Error-Based SQL Injection" lab.
5. **Start Lab**: Select the lab and begin the exercise.

### Lab Overview

The lab contains a SQL injection vulnerability in a tracking cookie used for analytics. The application constructs a SQL query using the value of the cookie, but the results of the query are not returned. The database contains a table called `users` with columns `username` and `password`. The goal is to leak the password for the administrator user and log into their account.

### Tools Used

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **Browser**: Any modern web browser (e.g., Chrome, Firefox).

### Setting Up Burp Suite

1. **Install Burp Suite**: Download and install Burp Suite from the official website.
2. **Configure Proxy**: Set up Burp Suite as a proxy in your browser settings.
3. **Intercept Requests**: Enable interception in Burp Suite to capture and modify HTTP requests.

---
<!-- nav -->
[[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/03-How to Prevent  Defend Against SQL Injection|How to Prevent  Defend Against SQL Injection]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/00-Overview|Overview]] | [[Web Security (PortSwigger)/02-SQL Injection/19-Lab 18 Visible error based SQL injection/05-Practice Labs|Practice Labs]]
