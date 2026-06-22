---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Understanding `window.postMessage`

`window.postMessage` is a method used to safely pass messages between windows, iframes, and even different domains. It allows for communication across origins, making it a powerful tool but also a potential vector for XSS attacks.

### Syntax of `window.postMessage`

```javascript
targetWindow.postMessage(message, targetOrigin, [transfer]);
```

- **targetWindow**: The window object of the target window.
- **message**: The message to be sent. This can be a string or a structured clone of a more complex object.
- **targetOrigin**: A string specifying the origin of the receiving window. This can be a specific origin or `"*"` to allow any origin.
- **transfer**: An optional array of objects to transfer ownership of, rather than copying them.

### Example Usage

```javascript
// Sending a message to the parent window
parent.postMessage("Hello from iframe", "*");

// Receiving a message in the parent window
window.addEventListener("message", function(event) {
    console.log("Received message:", event.data);
});
```

### Potential Risks

If the `targetOrigin` is set to `"*"`, any window can receive the message, potentially leading to XSS attacks. Additionally, if the message is not properly sanitized before being processed, it can execute arbitrary JavaScript.

---
<!-- nav -->
[[11-Understanding Web Messages and JSON Parsing|Understanding Web Messages and JSON Parsing]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/00-Overview|Overview]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/03-Lab 3 DOM XSS using web messages and JSONparse/13-Conclusion|Conclusion]]
