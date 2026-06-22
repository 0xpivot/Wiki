---
course: Web Security
topic: WebSockets Vulnerabilities
tags: [web-security]
---

## Preventing Cross-Site WebSocket Hijacking

To prevent CSWH attacks, several security measures can be implemented:

### Secure Coding Practices

1. **Use Secure Headers**: Ensure that your WebSocket endpoints are protected by appropriate security headers such as `Access-Control-Allow-Origin` and `Origin`.
2. **Validate User Input**: Always validate and sanitize user input to prevent injection attacks.

#### Example of Secure Headers

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: sN55CuWjJDMUZgSSPiVxuBuiY2E=
Access-Control-Allow-Origin: https://secure.example.com
```

### Secure Configuration

1. **Enable WebSocket Origin Checking**: Configure your WebSocket server to check the origin of incoming connections.
2. **Use HTTPS**: Ensure that all WebSocket connections are made over HTTPS to prevent man-in-the-middle attacks.

#### Example of WebSocket Origin Checking

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws, req) {
    const origin = req.headers.origin;
    if (origin !== 'https://secure.example.com') {
        ws.close(4407, 'Invalid origin');
        return;
    }
    ws.on('message', function incoming(message) {
        console.log('received: %s', message);
    });
});
```

### Detection and Monitoring

1. **Log WebSocket Activity**: Log all WebSocket activity to monitor for suspicious behavior.
2. **Use Security Tools**: Utilize security tools like Burp Suite or Wireshark to analyze WebSocket traffic and detect potential attacks.

#### Example of Logging WebSocket Activity

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', function connection(ws, req) {
    const origin = req.headers.origin;
    if (origin !== 'https://secure.example.com') {
        ws.close(4407, 'Invalid origin');
        return;
    }
    ws.on('message', function incoming(message) {
        console.log(`Received message from ${origin}: ${message}`);
    });
});
```

### Hands-On Practice

For hands-on practice with WebSockets vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including WebSockets.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning about web security vulnerabilities.

These labs provide practical scenarios where you can test and understand the concepts discussed in this chapter.

---
<!-- nav -->
[[06-How to Prevent  Defend Against CSWH|How to Prevent  Defend Against CSWH]] | [[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/00-Overview|Overview]] | [[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/08-Conclusion|Conclusion]]
