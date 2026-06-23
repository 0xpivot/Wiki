---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Introduction to DOM-Based Vulnerabilities

DOM-based vulnerabilities are a class of security issues that arise due to the way web applications handle and manipulate data within the Document Object Model (DOM). The DOM is a programming interface for HTML and XML documents, providing a structured representation of the document as a tree of nodes. Each node represents a part of the document, such as elements, attributes, text, comments, etc.

### What is DOM-Based XSS?

DOM-based Cross-Site Scripting (XSS) is a type of XSS vulnerability where the attacker injects malicious scripts into the DOM rather than the server-side code. This occurs when the application dynamically modifies the DOM based on untrusted input, such as user-controlled data from URLs, cookies, or other sources.

#### Why Does DOM-Based XSS Matter?

DOM-based XSS can lead to severe security implications, including:

- **Data Theft**: Attackers can steal sensitive information like session tokens, cookies, or personal data.
- **Account Takeover**: By injecting malicious scripts, attackers can hijack user sessions and perform actions on behalf of the user.
- **Phishing Attacks**: Malicious scripts can redirect users to phishing sites or display fake login forms.
- **Defacement**: Attackers can alter the appearance of the website, causing reputational damage.

### Real-World Examples

Recent real-world examples of DOM-based XSS vulnerabilities include:

- **CVE-2021-21972**: A DOM-based XSS vulnerability was found in the WordPress plugin "WPML Multilingual CMS." The vulnerability allowed attackers to inject malicious scripts via the `wpml-config.xml` file.
- **CVE-2020-14182**: A DOM-based XSS vulnerability was discovered in the Atlassian Jira software. The vulnerability allowed attackers to inject malicious scripts via the `jql` parameter in the URL.

### How DOM-Based XSS Works

To understand how DOM-based XSS works, let's break down the process:

1. **Untrusted Input**: The application receives untrusted input from various sources, such as URL parameters, cookies, or user input.
2. **Dynamic Content Modification**: The application uses JavaScript to dynamically modify the DOM based on this untrusted input.
3. **Execution of Malicious Scripts**: If the untrusted input contains malicious scripts, they will be executed within the context of the victim's browser.

### Example Scenario

Consider a web application that displays a greeting message based on the `name` parameter in the URL:

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

If an attacker crafts a URL like `https://example.com/?name=<script>alert('XSS')</script>`, the script will be executed in the victim's browser, leading to a DOM-based XSS attack.

### How to Detect DOM-Based XSS

Detecting DOM-based XSS requires a combination of static analysis and dynamic testing:

1. **Static Analysis**: Tools like ESLint, SonarQube, or custom static analysis scripts can help identify potential DOM-based XSS vulnerabilities by scanning for unsafe JavaScript operations.
2. **Dynamic Testing**: Using tools like Burp Suite, OWASP ZAP, or manual testing, you can simulate attacks and observe the behavior of the application.

### How to Prevent DOM-Based XSS

Preventing DOM-based XSS involves several best practices:

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being used in the DOM.
2. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded.
3. **Use Safe Methods**: Use safer methods to update the DOM, such as `textContent` instead of `innerHTML`.

#### Secure Code Example

Here’s a comparison between vulnerable and secure code:

**Vulnerable Code:**

```javascript
var name = window.location.search.substring(1);
document.getElementById('greeting').innerHTML = "Hello, " + name;
```

**Secure Code:**

```javascript
var name = window.location.search.substring(1);
document.getElementById('greeting').textContent = "Hello, " + "name";
```

### Lab Setup: DOMXSS Using Web Messages

In this lab, we will demonstrate a simple web message vulnerability using the PortSwigger Web Security Academy. The goal is to exploit the DOM-based XSS vulnerability and call the `print` function on the victim user.

#### Accessing the Lab

1. **Sign Up**: Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security) and sign up for an account.
2. **Navigate to Labs**: Once logged in, go to the "Academy" section and select "All Labs."
3. **Search for Lab**: Search for "DOM-based vulnerabilities" and select "Lab Number One: DOMXSS using web messages."

#### Lab Environment

The lab environment includes a built-in browser in Burp Suite, which allows you to intercept and modify HTTP requests.

### Step-by-Step Walkthrough

1. **Access the Lab**: Open the lab and note that all your requests are being intercepted by Burp Suite.
2. **View Page Source**: Right-click on the page and select "View Page Source" to inspect the JavaScript code.

#### Inspecting the Page Source

Let's assume the page source looks something like this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Web Message Lab</title>
</head>
<body>
    <div id="message"></div>
    <script>
        var message = new URLSearchParams(window.location.search).get('msg');
        document.getElementById('message').innerHTML = message;
    </script>
</body>
</html>
```

This code dynamically sets the content of the `#message` div based on the `msg` parameter in the URL.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to craft a URL that injects a malicious script into the `msg` parameter.

#### Crafting the Exploit

1. **Craft the URL**: Construct a URL that includes a script tag, such as `https://example.com/?msg=<script>alert('XSS');</script>`.
2. **Intercept the Request**: Use Burp Suite to intercept the request and modify the `msg` parameter.
3. **Send the Request**: Send the modified request to the server.

#### Full HTTP Request and Response

Here’s an example of the full HTTP request and response:

```http
GET /?msg=%3Cscript%3Ealert(%27XSS%27)%3B%3C%2Fscript%3E HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Cookie: session_id=abc123
Connection: close

HTTP/1.1 200 OK
Date: Mon, 10 Jan 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 204
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Web Message Lab</title>
</head>
<body>
    <div id="message"><script>alert('XSS');</script></div>
    <script>
        var message = new URLSearchParams(window.location.search).get('msg');
        document.getElementById('message').innerHTML = message;
    </script>
</body>
</html>
```

### Sequence Diagram

A sequence diagram can help visualize the interaction between the client and the server during the exploitation process:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: GET /?msg=%3Cscript%3Ealert(%27XSS%27)%3B%3C%2Fscript%3E
    Server-->>Client: 200 OK
    Client->>Client: Execute <script>alert('XSS');</script>
```

### How to Prevent / Defend

#### Detection

- **Static Analysis**: Use tools like ESLint or SonarQube to scan for unsafe JavaScript operations.
- **Dynamic Testing**: Use tools like Burp Suite or OWASP ZAP to simulate attacks and observe the behavior of the application.

#### Prevention

1. **Input Validation**: Validate and sanitize all user inputs before using them in the DOM.
2. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded.
3. **Use Safe Methods**: Use safer methods to update the DOM, such as `textContent` instead of `innerHTML`.

#### Secure Coding Practices

Here’s a comparison between vulnerable and secure code:

**Vulnerable Code:**

```javascript
var message = new URLSearchParams(window.location.search).get('msg');
document.getElementById('message').innerHTML = message;
```

**Secure Code:**

```javascript
var message = new URLSearchParams(window.location.search).get('msg');
document.getElementById('message').textContent = message;
```

### Conclusion

Understanding and preventing DOM-based XSS vulnerabilities is crucial for securing web applications. By following best practices and using tools effectively, you can mitigate the risks associated with these vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including those focused on DOM-based XSS.
- **OWASP Juice Shop**: Provides a vulnerable web application for learning and practicing web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning about web security vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating DOM-based XSS vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/01-Lab 1 DOM XSS using web messages/00-Overview|Overview]] | [[02-DOM-Based Vulnerabilities and DOM-XSS Using Web Messages|DOM-Based Vulnerabilities and DOM-XSS Using Web Messages]]
