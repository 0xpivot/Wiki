---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities are a subset of Cross-Site Scripting (XSS) attacks that occur within the Document Object Model (DOM) of a webpage. Unlike traditional XSS attacks, which involve injecting malicious scripts through user input fields or URLs, DOM-based XSS vulnerabilities arise from the way a web application processes data within the DOM itself. These vulnerabilities can be particularly dangerous because they often bypass standard security measures like input validation and output encoding.

### What is the Document Object Model (DOM)?

The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a document as a tree of objects, allowing programs and scripts to dynamically access and update the content, structure, and style of a document. The DOM provides a structured representation of the document, enabling developers to manipulate the document's elements, attributes, and text content.

### Why Are DOM-Based Vulnerabilities Important?

DOM-based vulnerabilities are important because they can lead to significant security risks. An attacker can exploit these vulnerabilities to inject malicious scripts into a webpage, potentially leading to unauthorized access, data theft, or other malicious activities. Understanding and mitigating these vulnerabilities is crucial for maintaining the security of web applications.

### How Does DOM-Based XSS Work?

In a DOM-based XSS attack, an attacker injects malicious scripts into the DOM of a webpage. The script is executed within the context of the victim's browser, allowing the attacker to perform actions such as stealing cookies, redirecting the user to malicious sites, or executing arbitrary JavaScript code.

### Example of DOM-Based XSS

Consider a simple webpage that displays a greeting based on a query parameter:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Greeting Page</title>
</head>
<body>
    <h1 id="greeting"></h1>
    <script>
        var name = window.location.search.substring(1);
        document.getElementById('greeting').innerHTML = "Hello, " + name;
    </script>
</body>
</html>
```

If an attacker crafts a URL like `http://example.com/?name=<script>alert('XSS')</script>`, the script will be executed in the victim's browser, resulting in a DOM-based XSS attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[02-DOM-Based Vulnerabilities DOM XSS Using Web Messages and `JSON.parse`|DOM-Based Vulnerabilities DOM XSS Using Web Messages and `JSON.parse`]]
