---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into a trusted website, which then gets executed by unsuspecting users. XSS attacks can lead to various security issues such as stealing cookies, session tokens, and other sensitive data, or even taking control of user accounts.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off the web server, usually in the form of an error message, search result, or any other response that includes data provided by the user. The victim executes the script when they visit a malicious link or interact with a compromised page.
   
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, comment field, visitor log, etc. The victim executes the script when they view the stored information.
   
3. **DOM-based XSS**: The vulnerability lies in the client-side code rather than the server-side code. The script is executed based on the way the DOM is manipulated by JavaScript.

### Lab Overview

In this lab, we will focus on a **Reflected XSS** vulnerability where the web application allows certain SVG tags and events to be reflected back in the response. Our goal is to exploit this vulnerability to call the `alert` function, demonstrating the potential impact of such an attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/02-Background Theory|Background Theory]]
