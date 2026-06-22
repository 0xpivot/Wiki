---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. This can lead to various attacks such as stealing sensitive information, session hijacking, and defacement of websites. XSS vulnerabilities arise due to the lack of proper input validation and output encoding on web applications.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, typically in response to user input, such as a search query. The victim's browser executes the script because it comes from a trusted source.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is later served to unsuspecting victims.
3. **DOM-based XSS**: The vulnerability arises from client-side code that modifies the DOM based on untrusted data, leading to the execution of malicious scripts.

### Lab Overview: Reflected XSS into a JavaScript String with Angle Brackets HTML Encoded

In this lab, we will explore a specific type of reflected XSS vulnerability where the angle brackets (`<` and `>`) are HTML-encoded. The vulnerability occurs within a JavaScript string, making it more challenging to exploit. Our goal is to break out of the JavaScript string and execute a simple `alert` function to demonstrate the vulnerability.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/10-Lab 9 Reflected XSS into a JavaScript string with angle brackets HTML encoded/02-Background Theory|Background Theory]]
