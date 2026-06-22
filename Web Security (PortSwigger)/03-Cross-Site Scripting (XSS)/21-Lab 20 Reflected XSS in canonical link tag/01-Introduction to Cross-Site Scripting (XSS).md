---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker manages to inject malicious scripts into web pages viewed by other users. XSS attacks can lead to various harmful outcomes, such as stealing sensitive data, session hijacking, and defacement of websites.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off the web server, usually in response to a user request. The victim's browser executes the script when it receives the response.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is later served to unsuspecting victims.
3. **DOM-based XSS**: The vulnerability lies in client-side code rather than server-side code. The script modifies the DOM in a way that allows the execution of arbitrary JavaScript.

### Lab Overview: Reflected XSS in Canonical Link Tag

In this lab, we will focus on a specific type of Reflected XSS vulnerability that occurs within the `<link>` tag used for canonical URLs. The goal is to inject a script that triggers an `alert` function when certain key combinations are pressed.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/21-Lab 20 Reflected XSS in canonical link tag/02-Background Theory|Background Theory]]
