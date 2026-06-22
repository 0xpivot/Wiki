---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an application takes untrusted data and sends it to a web browser without proper validation or escaping. XSS allows attackers to execute scripts in the victim’s browser, which can hijack user sessions, deface websites, or redirect the user to malicious sites.

### Types of XSS

There are three main types of XSS:

1. **Stored XSS**: The malicious script is permanently stored on the target servers, such as in a database, in a message forum, visitor log, comment field, etc. The victim then retrieves the malicious script when it accesses the stored information.
   
2. **Reflected XSS**: The malicious script comes from the current HTTP request. Reflected XSS is delivered to the user via an immediate HTTP response. The attacker has to deliver the attack code to the user, either via email or another site. The user clicks on a malicious link or submits a form that the attacker controls.

3. **DOM-Based XSS**: This type of XSS occurs when the vulnerability exists in client-side code rather than server-side code. The attacker injects malicious scripts through the client-side code, often by manipulating the Document Object Model (DOM).

### Lab Overview

In this lab, we will focus on a DOM-based XSS vulnerability in the `innerHTML` sink using the `location.search` source. The goal is to exploit this vulnerability to call the `alert` function.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/05-Lab 4 DOM XSS in innerHTML sink using source locationsearch/00-Overview|Overview]] | [[02-How to Prevent  Defend Against DOM-Based XSS|How to Prevent  Defend Against DOM-Based XSS]]
