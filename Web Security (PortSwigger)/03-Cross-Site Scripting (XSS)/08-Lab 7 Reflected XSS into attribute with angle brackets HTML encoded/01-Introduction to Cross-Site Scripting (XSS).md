---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. This can lead to various attacks such as stealing cookies, hijacking user sessions, defacing websites, and more. XSS vulnerabilities are categorized into three main types: **Reflected XSS**, **Stored XSS**, and **DOM-based XSS**. Each type has distinct characteristics and exploitation methods.

### Reflected XSS

Reflected XSS occurs when an attacker injects malicious script into a web page via a query parameter or form input. The server reflects the input back to the user without proper sanitization or validation. This type of XSS is often exploited through phishing emails or social engineering techniques.

### Stored XSS

Stored XSS happens when an attacker injects malicious script into a database or persistent storage. The script is then served to all users who visit the affected page. This type of XSS is more dangerous because it affects all users who view the page.

### DOM-based XSS

DOM-based XSS occurs when the vulnerability exists within the client-side JavaScript code rather than the server-side code. The script is executed based on user interaction with the page, such as clicking a link or submitting a form.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/02-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]]
