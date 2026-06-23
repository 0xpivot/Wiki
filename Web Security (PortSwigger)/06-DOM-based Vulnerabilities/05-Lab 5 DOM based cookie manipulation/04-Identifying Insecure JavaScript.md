---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Identifying Insecure JavaScript

### Inspecting the Page Source

To identify potential DOM-based vulnerabilities, we need to look for JavaScript code that processes user inputs directly from the DOM. Common sources of user input include URL parameters, cookies, and form fields.

#### Example: Insecure JavaScript Code

Consider the following JavaScript snippet:

```javascript
document.getElementById("content").innerHTML = decodeURIComponent(window.location.hash.substring(1));
```

This code takes the hash part of the URL (`window.location.hash`) and inserts it directly into the HTML content of an element with the ID `content`. This is a classic example of a DOM-based XSS vulnerability.

### Real-World Example: CVE-2-2021-21972

In the case of CVE-2021-21972, the Zoom web client had similar insecure JavaScript code that processed user inputs from the URL hash. This allowed attackers to inject malicious JavaScript into the page.

---
<!-- nav -->
[[03-How to Prevent  Defend Against DOM-Based Vulnerabilities|How to Prevent  Defend Against DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]] | [[05-Injecting Malicious Cookies|Injecting Malicious Cookies]]
