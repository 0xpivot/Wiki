---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications where an attacker can inject malicious scripts into web pages viewed by other users. This can lead to various harmful outcomes such as stealing sensitive data, session hijacking, and even full control of the user's browser. XSS vulnerabilities arise due to improper input validation and output encoding practices.

### Types of XSS Vulnerabilities

There are three main types of XSS vulnerabilities:

1. **Stored XSS**: Malicious scripts are permanently stored on the target servers, such as in a database, comment field, visitor log, etc. These scripts are then served to users when they visit the affected page.
   
2. **Reflected XSS**: Malicious scripts are reflected off a web server, typically via a search query, error message, or similar response. The attacker must lure the victim into clicking a specially crafted link or submitting a form.
   
3. **DOM-Based XSS**: Malicious scripts are executed based on the Document Object Model (DOM) of the web page. Unlike stored and reflected XSS, the script injection happens client-side and does not involve the server sending the malicious script.

### AngularJS and DOM-Based XSS

AngularJS is a popular JavaScript framework used for building dynamic web applications. One of its key features is the ability to bind data to the DOM using expressions enclosed in double curly braces (`{{ }}`). This feature can introduce DOM-based XSS vulnerabilities if user input is not properly sanitized or encoded.

### Lab Overview

In this lab, we will explore a DOM-based XSS vulnerability in an AngularJS application. The specific scenario involves encoding angle brackets and double quotes, which are often used to inject malicious scripts. Our goal is to exploit this vulnerability to execute a JavaScript `alert` function.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/12-Lab 11 DOM XSS in AngularJS expression with angle brackets and double quotes HTML encoded/02-Background Theory|Background Theory]]
