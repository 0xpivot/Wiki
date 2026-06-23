---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. XSS enables attackers to inject client-side scripts into web pages viewed by other users. This can lead to various malicious activities such as stealing sensitive information, performing actions on behalf of the user, or defacing websites.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, usually in response to a user request. The victim receives the reflected script as part of the HTTP response from the server.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, in a message forum, visitor log, comment field, etc. The victim then retrieves the script from the server when the stored data is delivered in the HTTP response.
3. **DOM-Based XSS**: The vulnerability exists in the client-side JavaScript code rather than the server-side code. The script is executed based on the Document Object Model (DOM) manipulation.

### Lab Overview: Reflected DOM XSS

In this lab, we will focus on a specific type of XSS called Reflected DOM XSS. This type of vulnerability occurs when the server-side application processes data from a request and echoes the data in the response. A script on the page then processes the reflected data in an unsafe way, ultimately writing it to a dangerous sink.

To solve this lab, we need to create an injection that calls the `alert` function. This will demonstrate the exploitation of the DOM-based vulnerability.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/13-Lab 12 Reflected DOM XSS/02-Common Pitfalls and Detection|Common Pitfalls and Detection]]
