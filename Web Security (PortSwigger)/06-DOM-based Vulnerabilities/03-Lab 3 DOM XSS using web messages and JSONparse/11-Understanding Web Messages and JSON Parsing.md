---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Understanding Web Messages and JSON Parsing

Web messages are a mechanism for communication between different browsing contexts, such as iframes, popups, and windows. They allow scripts in one window to send messages to scripts in another window, even if they are on different domains.

JSON parsing is the process of converting a JSON string into a JavaScript object. This is commonly used to parse data received from APIs or other sources.

### Web Messaging API

The Web Messaging API consists of several methods and properties that enable communication between different browsing contexts. The key methods include:

- `postMessage()`: Sends a message to another window.
- `addEventListener('message', handler)`: Listens for incoming messages.

### JSON Parsing

JSON parsing is performed using the `JSON.parse()` method. This method takes a JSON string and converts it into a JavaScript object. However, if the JSON string contains malicious scripts, they can be executed during the parsing process, leading to a DOM-based XSS vulnerability.

### Example of Web Message and JSON Parsing

Consider a webpage that listens for web messages and parses the received data:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Web Message Listener</title>
</head>
<body>
    <script>
        window.addEventListener('message', function(event) {
            var data = JSON.parse(event.data);
            console.log(data.message);
        });
    </script>
</body>
</html>
```

An attacker can exploit this by sending a crafted message:

```javascript
window.postMessage('{"message": "<script>alert(\'XSS\')</script>"}', '*');
```

This will result in the execution of the malicious script in the victim's browser.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/10-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[12-Understanding `window.postMessage`|Understanding `window.postMessage`]]
