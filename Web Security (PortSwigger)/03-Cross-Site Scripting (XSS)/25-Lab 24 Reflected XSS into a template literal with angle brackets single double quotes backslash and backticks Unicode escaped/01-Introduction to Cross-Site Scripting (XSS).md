---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. This can lead to various harmful outcomes, such as stealing sensitive information, hijacking user sessions, or performing actions on behalf of the victim. XSS vulnerabilities arise due to insufficient input validation and output encoding on the server side.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, typically in response to a user request. The attacker tricks the victim into making a request to the server that includes the malicious script. This type of XSS is often exploited through phishing emails or social engineering tactics.

2. **Stored XSS**: The injected script is permanently stored on the server, such as in a database, forum post, comment field, or user profile. When the victim visits the page containing the stored script, the script executes.

3. **DOM-Based XSS**: The vulnerability arises from client-side code that dynamically modifies the DOM based on untrusted data. The script is executed on the client side without involving the server.

### Lab Overview

In this lab, we will focus on a reflected XSS vulnerability within a search block functionality. The reflection occurs inside a template string with angle brackets, single and double quotes, HTML encoded characters, and backticks. Our goal is to exploit this vulnerability by injecting a script that calls the `alert` function.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/25-Lab 24 Reflected XSS into a template literal with angle brackets single double quotes backslash and backticks Unicode escaped/02-Background Theory|Background Theory]]
