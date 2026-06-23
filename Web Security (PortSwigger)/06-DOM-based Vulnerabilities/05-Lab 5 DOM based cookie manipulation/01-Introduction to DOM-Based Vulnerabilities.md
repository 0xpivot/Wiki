---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when a web application processes user input within the Document Object Model (DOM) without proper validation or sanitization. These vulnerabilities can lead to various attacks, including Cross-Site Scripting (XSS), which can result in unauthorized data theft, session hijacking, and other malicious activities.

### What is the Document Object Model (DOM)?

The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a document as a tree of objects, where each object corresponds to a part of the document. The DOM allows scripts to dynamically access and manipulate the content, structure, and style of a document.

### Why Are DOM-Based Vulnerabilities Important?

DOM-based vulnerabilities are significant because they can bypass traditional server-side protections. Unlike traditional XSS attacks, where the attacker injects malicious code through the server, DOM-based XSS occurs entirely on the client side. This makes it harder to detect and mitigate using standard server-side security measures.

### How Do DOM-Based Vulnerabilities Work?

In a typical DOM-based XSS scenario, an attacker injects malicious code into a web page through a user-controlled input, such as a URL parameter, form field, or cookie. The injected code is then executed by the browser when the page loads or interacts with the DOM.

### Real-World Example: CVE-2021-21972

One notable real-world example of a DOM-based vulnerability is CVE-2021-21972, which affected the popular web conferencing platform Zoom. The vulnerability allowed attackers to inject malicious JavaScript into the Zoom web client, leading to potential XSS attacks. This highlights the importance of securing client-side code against such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]] | [[02-DOM-Based Vulnerabilities|DOM-Based Vulnerabilities]]
