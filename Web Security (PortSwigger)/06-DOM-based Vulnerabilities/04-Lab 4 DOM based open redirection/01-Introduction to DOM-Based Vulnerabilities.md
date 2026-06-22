---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities occur when a web application uses client-side JavaScript to manipulate the Document Object Model (DOM) in a way that can be influenced by untrusted input. These vulnerabilities arise because the browser interprets and executes the JavaScript code, which can lead to various security issues such as cross-site scripting (XSS), information disclosure, and open redirection attacks.

### What is the Document Object Model (DOM)?

The Document Object Model (DOM) is a programming interface for web documents. It represents the page so that programs can change the document structure, style, and content. The DOM represents the document as a tree structure, with each node representing a part of the document. For example, elements, attributes, and text are all represented as nodes in the DOM tree.

### Why Are DOM-Based Vulnerabilities Important?

DOM-based vulnerabilities are significant because they can bypass traditional server-side protections. Since the manipulation happens on the client side, attackers can exploit these vulnerabilities even if the server-side code is secure. This makes them particularly dangerous and often overlooked in security assessments.

### How Do DOM-Based Vulnerabilities Work?

In a typical scenario, a web application might use JavaScript to dynamically update parts of the page based on user input or URL parameters. If this input is not properly sanitized, an attacker can inject malicious content that will be executed by the browser. This can lead to various types of attacks, including:

- **Cross-Site Scripting (XSS)**: An attacker can inject scripts that execute in the context of the victim’s session.
- **Information Disclosure**: Sensitive data can be leaked through JavaScript.
- **Open Redirection**: An attacker can redirect the user to a malicious site.

### Real-World Example: CVE-2021-21972

One real-world example of a DOM-based vulnerability is CVE-2021-21972, which affected the popular web conferencing platform Zoom. The vulnerability allowed an attacker to inject arbitrary JavaScript into the meeting room URL, leading to potential XSS attacks. This demonstrates how critical it is to ensure that all client-side code is secure against such manipulations.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]] | [[02-DOM-Based Vulnerabilities Understanding and Mitigating DOM-Based Open Redirection|DOM-Based Vulnerabilities Understanding and Mitigating DOM-Based Open Redirection]]
