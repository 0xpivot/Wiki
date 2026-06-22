---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It allows attackers to inject malicious scripts into web pages viewed by other users. These scripts can steal sensitive data, perform actions on behalf of the user, or even take control of the user's session. XSS vulnerabilities arise due to the lack of proper input validation and output encoding mechanisms in web applications.

### Types of XSS

There are three main types of XSS:

1. **Reflected XSS**: The injected script is reflected off a web server, often in response to a user request. The victim visits a URL that contains the malicious script. The script is executed when the page loads.
2. **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, comment field, visitor log, etc. The victim retrieves the malicious script when they access the stored information.
3. **DOM-based XSS**: The vulnerability lies in the client-side code rather than the server-side code. The script is executed based on the way the DOM (Document Object Model) is manipulated.

### Lab Overview: Reflected XSS into a JavaScript String

In this lab, we will focus on a specific type of reflected XSS where the injection occurs within a JavaScript string. The challenge is to break out of the string context and execute arbitrary JavaScript code. This scenario is particularly challenging because the application escapes single quotes and backslashes, making it harder to inject malicious scripts.

### Setup and Accessing the Lab

To access the lab, follow these steps:

1. Visit the Web Security Academy at [PortSwigger](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Navigate to the "Academy" section.
4. Search for "cross-site scripting labs".
5. Locate and open lab number 21 titled "Reflected XSS into a JavaScript string with single quote and backslash escaped".

For this lab, we will be using Burp Suite Professional, but the same techniques can be applied using the browser or Burp Suite Community Edition.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/22-Lab 21 Reflected XSS into a JavaScript string with single quote and backslash escaped/02-Exploiting the Vulnerability|Exploiting the Vulnerability]]
