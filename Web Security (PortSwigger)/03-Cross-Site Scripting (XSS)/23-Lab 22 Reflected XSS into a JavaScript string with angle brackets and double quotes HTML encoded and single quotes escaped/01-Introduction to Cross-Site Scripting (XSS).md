---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into a trusted website, which then gets executed by unsuspecting users. XSS attacks can lead to various harmful outcomes such as stealing cookies, session tokens, and other sensitive data, defacing websites, or even redirecting users to malicious sites.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off the web server, usually in the form of an HTTP response. This type of XSS is often exploited through phishing emails or social engineering techniques.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, comment field, visitor log, etc. Every user who visits the affected page will execute the script.
3. **DOM-based XSS**: The vulnerability exists in client-side code rather than server-side code. The script is executed based on the DOM manipulation performed by the application.

### Context of the Lab

In this lab, we will focus on a specific type of Reflected XSS where the input is reflected in a JavaScript string. The challenge is to break out of the string context and execute arbitrary JavaScript code despite the fact that angle brackets (`<` and `>`) and double quotes (`"`) are HTML-encoded, and single quotes (`'`) are escaped.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/00-Overview|Overview]] | [[02-Detailed Walkthrough of the Lab|Detailed Walkthrough of the Lab]]
