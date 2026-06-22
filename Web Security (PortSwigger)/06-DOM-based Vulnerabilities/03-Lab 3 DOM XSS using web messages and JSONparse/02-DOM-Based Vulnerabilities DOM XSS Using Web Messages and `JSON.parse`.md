---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## DOM-Based Vulnerabilities: DOM XSS Using Web Messages and `JSON.parse`

### Introduction to DOM-Based XSS

DOM-based Cross-Site Scripting (XSS) is a type of vulnerability that occurs when an application dynamically generates content based on user input, without proper validation or sanitization. Unlike traditional stored or reflected XSS, where the malicious script originates from the server, DOM-based XSS arises from the client-side JavaScript code that manipulates the Document Object Model (DOM).

#### What is DOM?

The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a document as a tree of objects, allowing scripts to access and manipulate the document's content, structure, and style. Each node in the DOM tree represents a part of the document, such as elements, attributes, text, comments, etc.

#### Why Does DOM-Based XSS Matter?

DOM-based XSS is particularly dangerous because it can bypass certain security mechanisms, such as Content Security Policy (CSP), which are designed to mitigate traditional XSS attacks. Since the malicious script is executed within the context of the victim's browser, it can perform actions that appear to come from the legitimate website, making it harder to detect and prevent.

### Understanding the Scenario

In this scenario, we have an application that includes an `<iframe>` element. The application listens for messages sent via the `window.postMessage` API and processes these messages using `JSON.parse`. Depending on the type of message received, different actions are taken, such as setting the source of an embedded media player.

#### Code Example: Application Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Acme Player</title>
</head>
<body>
    <iframe id="player" src="about:blank"></iframe>
    <script>
        window.addEventListener('message', function(event) {
            try {
                var data = JSON.parse(event.data);
                switch(data.type) {
                    case 'pageLoad':
                        // Perform some action
                        break;
                    case 'loadChannel':
                        // Perform some action
                        break;
                    case 'playerHeightChanged':
                        // Perform some action
                        break;
                    case 'setSource':
                        document.getElementById('player').src = data.url;
                        break;
                }
            } catch(e) {
                console.error('Error parsing message:', e);
            }
        });
    </script>
</body>
</html>
```

### Identifying the Vulnerability

The vulnerability lies in the way the application handles the `data.url` value. Specifically, the application sets the `src` attribute of the `<iframe>` element directly from the `url` property of the message without any validation or sanitization. This allows an attacker to inject malicious content into the `src` attribute, leading to a DOM-based XSS attack.

#### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example of a DOM-based XSS vulnerability found in the popular video conferencing platform Zoom. The vulnerability allowed attackers to inject arbitrary JavaScript code into the meeting interface, potentially compromising the security of users.

### Exploiting the Vulnerability

To exploit this vulnerability, an attacker would need to craft a message that, when parsed by the application, results in the execution of malicious JavaScript code. Here’s a step-by-step guide:

1. **Craft the Malicious Message**: The attacker needs to create a message that, when parsed, will result in the execution of malicious code. For example, the attacker might send a message with a `type` of `'setSource'` and a `url` that contains a script tag.

2. **Send the Message**: The attacker sends the crafted message to the application using the `window.postMessage` API.

#### Code Example: Crafting the Malicious Message

```javascript
// Attacker's code
var maliciousMessage = {
    type: 'setSource',
    url: 'javascript:alert("XSS")'
};

// Send the message to the target origin
window.postMessage(JSON.stringify(maliciousMessage), 'https://target-origin.com');
```

#### Full HTTP Request and Response

When the attacker sends the message, the following HTTP request and response occur:

```http
POST /path/to/target HTTP/1.1
Host: target-origin.com
Content-Type: application/json

{
    "type": "setSource",
    "url": "javascript:alert(\"XSS\")"
}

HTTP/1.1 200 OK
Content-Type: application/json

{
    "status": "success",
    "message": "Message received"
}
```

### How to Prevent / Defend Against DOM-Based XSS

#### Detection

To detect DOM-based XSS vulnerabilities, you can use automated tools such as static analysis tools (e.g., ESLint with plugins like `eslint-plugin-security`) and dynamic analysis tools (e.g., Burp Suite, OWASP ZAP). These tools can help identify insecure usage of user inputs in JavaScript code.

#### Prevention

1. **Input Validation and Sanitization**: Always validate and sanitize user inputs before using them in the DOM. Use libraries like DOMPurify to sanitize HTML content.

2. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded. This can help mitigate the impact of DOM-based XSS.

3. **Secure Coding Practices**: Follow secure coding practices such as avoiding direct assignment of user inputs to DOM properties. Instead, use methods that automatically escape special characters.

#### Secure Code Fix

Here’s how the secure version of the code should look:

```javascript
window.addEventListener('message', function(event) {
    try {
        var data = JSON.parse(event.data);
        switch(data.type) {
            case 'pageLoad':
                // Perform some action
                break;
            case 'loadChannel':
                // Perform some action
                break;
            case 'playerHeightChanged':
                // Perform some action
                break;
            case 'setSource':
                var sanitizedUrl = DOMPurify.sanitize(data.url);
                document.getElementById('player').src = sanitizedUrl;
                break;
        }
    } catch(e) {
        console.error('Error parsing message:', e);
    }
});
```

### Common Pitfalls and Best Practices

1. **Avoid Direct Assignment**: Avoid directly assigning user inputs to DOM properties. Always sanitize and validate inputs first.

2. **Use Libraries**: Utilize libraries like DOMPurify for sanitizing HTML content.

3. **Regular Audits**: Regularly audit your codebase for potential DOM-based XSS vulnerabilities.

### Hands-On Practice

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting various types of XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and testing web security vulnerabilities.

### Conclusion

DOM-based XSS is a critical vulnerability that can lead to significant security risks. By understanding the underlying principles, identifying potential vulnerabilities, and implementing robust prevention measures, you can significantly reduce the risk of such attacks. Always follow secure coding practices and regularly audit your codebase to ensure the highest level of security.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/01-Introduction to DOM-Based Vulnerabilities|Introduction to DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[03-DOM-Based Vulnerabilities and DOM XSS Using Web Messages and JSON.parse|DOM-Based Vulnerabilities and DOM XSS Using Web Messages and JSON.parse]]
