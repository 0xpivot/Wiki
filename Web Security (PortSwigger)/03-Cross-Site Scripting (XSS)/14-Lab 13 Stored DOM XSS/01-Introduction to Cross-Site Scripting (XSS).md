---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker injects malicious scripts into a webpage viewed by other users. These scripts can perform actions such as stealing cookies, session tokens, and other sensitive information. There are three main types of XSS: **Stored**, **Reflected**, and **DOM-based**. In this chapter, we will focus on **Stored DOM-based XSS**.

### What is Stored DOM-based XSS?

Stored DOM-based XSS is a variant of XSS where the malicious script is permanently stored on the server and then served to users. The key difference from traditional stored XSS is that the script is executed within the context of the Document Object Model (DOM) rather than being directly injected into the HTML.

#### Why Does Stored DOM-based XSS Matter?

Stored DOM-based XSS is particularly dangerous because the malicious script persists on the server and can affect multiple users over time. Unlike reflected XSS, which requires the victim to visit a specific URL, stored XSS can be triggered simply by viewing a page. This makes it easier for attackers to spread their malicious code.

### How Does Stored DOM-based XSS Work?

To understand how Stored DOM-based XSS works, let's break down the process:

1. **Injection**: An attacker injects a malicious script into a form field or any input that gets stored on the server.
2. **Storage**: The server stores the input, including the malicious script.
3. **Execution**: When another user views the page containing the stored input, the script is executed within the context of the DOM.

#### Example Scenario

Consider a web application that allows users to post comments. If the application does not properly sanitize user inputs, an attacker can inject a malicious script into a comment. When another user reads the comment, the script executes in their browser, potentially stealing their session cookies or performing other malicious actions.

### Real-World Examples

Recent real-world examples of Stored DOM-based XSS include:

- **CVE-2021-3116**: A vulnerability in the WordPress plugin "WPML Multilingual CMS" allowed attackers to inject malicious scripts into the site's database, which were then executed when users viewed affected pages.
- **CVE-2022-22965**: A vulnerability in the Atlassian Confluence application allowed attackers to inject malicious scripts into comments, which were then executed when other users viewed the comments.

### Mapping the Application

Before exploiting a Stored DOM-based XSS vulnerability, it's crucial to map the application and identify potential points of injection. This involves understanding how user inputs are handled and where they are stored.

#### Steps to Map the Application

1. **Identify Input Fields**: Look for forms, comments sections, and any other areas where users can submit data.
2. **Check Storage Mechanisms**: Determine how the application stores user inputs. Is it in a database? In a file system?
3. **Analyze Output Handling**: Examine how the application renders stored data. Are there any JavaScript functions that handle this data?

### Exploiting Stored DOM-based XSS

Let's walk through the steps to exploit a Stored DOM-based XSS vulnerability using the scenario described in the lecture.

#### Step 1: Access the Lab

The lab is hosted on the PortSwigger Web Security Academy. To access it:

1. Visit `https://portswigger.net/web-security`.
2. Sign up for an account if you don't already have one.
3. Log in and navigate to the "Academy" section.
4. Search for "cross-site scripting labs" and select lab number 13 titled "Store DomXSS".

#### Step 2: Identify the Vulnerable Functionality

In this lab, the vulnerable functionality is the block comment feature. We need to find out how user inputs are handled and where they are stored.

#### Step 3: Inject Malicious Script

To exploit the vulnerability, we need to inject a script that will execute when another user views the comment. A simple example would be to inject a script that calls the `alert` function.

```html
<script>alert('XSS');</script>
```

#### Step 4: Submit the Comment

Submit the comment with the injected script. The server should store this comment.

#### Step 5: Trigger the Vulnerability

When another user views the comment, the script should execute, triggering the `alert` function.

### Full HTTP Request and Response

Here is a complete example of the HTTP request and response for submitting the comment:

#### HTTP Request

```http
POST /submit-comment HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

comment=<script>alert('XSS');</script>
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Comment Submitted</title>
</head>
<body>
    <h1>Your comment has been submitted!</h1>
    <p><script>alert('XSS');</script></p>
</body>
</html>
```

### Mermaid Diagrams

#### Attack Chain Diagram

```mermaid
sequenceDiagram
    participant User as U
    participant Server as S
    participant Browser as B
    U->>S: POST /submit-comment
    S-->>B: HTTP 200 OK
    B->>B: Execute <script>alert('XSS');</script>
```

### Common Pitfalls

When dealing with Stored DOM-based XSS, there are several common pitfalls to avoid:

1. **Improper Sanitization**: Failing to properly sanitize user inputs can lead to successful exploitation.
2. **Inadequate Content Security Policy (CSP)**: Without a strong CSP, browsers may execute malicious scripts.
3. **Insufficient Input Validation**: Relying solely on client-side validation can be bypassed.

### How to Prevent / Defend Against Stored DOM-based XSS

#### Detection

To detect Stored DOM-based XSS vulnerabilities:

1. **Automated Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, or commercial scanners to identify potential vulnerabilities.
2. **Manual Testing**: Perform manual testing by injecting various payloads and observing the results.

#### Prevention

To prevent Stored DOM-based XSS:

1. **Input Sanitization**: Ensure all user inputs are sanitized before being stored or rendered.
2. **Content Security Policy (CSP)**: Implement a strict CSP to restrict the sources of executable scripts.
3. **Output Encoding**: Encode user inputs when rendering them in the DOM to prevent script execution.

#### Secure Coding Fixes

Here is an example of a vulnerable and secure code implementation:

##### Vulnerable Code

```javascript
// Vulnerable code
document.getElementById('comment').innerHTML = '<script>alert("XSS");</script>';
```

##### Secure Code

```javascript
// Secure code
document.getElementById('comment').textContent = '<script>alert("XSS");</script>';
```

### Configuration Hardening

#### Content Security Policy (CSP)

Implement a strong CSP to mitigate XSS attacks:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline';
```

### Hands-On Labs

For hands-on practice with Stored DOM-based XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Lab 13 "Store DomXSS".
- **OWASP Juice Shop**: Contains various XSS challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of XSS vulnerabilities to practice on.

### Conclusion

Understanding and preventing Stored DOM-based XSS is crucial for securing web applications. By mapping the application, identifying potential injection points, and implementing robust security measures, developers can significantly reduce the risk of such vulnerabilities. Always ensure proper sanitization, encoding, and the use of strong security policies to protect against XSS attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/14-Lab 13 Stored DOM XSS/00-Overview|Overview]] | [[02-Identifying the Vulnerability|Identifying the Vulnerability]]
