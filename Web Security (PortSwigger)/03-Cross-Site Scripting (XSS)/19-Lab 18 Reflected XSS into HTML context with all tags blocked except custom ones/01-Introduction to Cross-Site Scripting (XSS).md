---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker manages to inject malicious scripts into a webpage viewed by other users. These scripts can execute within the victim's browser, potentially leading to unauthorized actions such as stealing sensitive data, session hijacking, or even taking control of the user's browser.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, usually in response to a user's input. This type of XSS is often exploited through phishing attacks.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is retrieved and executed when a user visits the affected page.
3. **DOM-based XSS**: The vulnerability exists in the client-side code rather than the server-side code. The script is executed based on the way the DOM (Document Object Model) is manipulated.

In this lab, we will focus on Reflected XSS, specifically in the context where all HTML tags are blocked except for custom ones.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[02-Background Theory XSS Vulnerabilities|Background Theory XSS Vulnerabilities]]
