---
course: Web Security
topic: WebSockets Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against CSWH

### Detection

Detecting CSWH attacks involves monitoring WebSocket traffic for unusual patterns. Tools like Wireshark can be used to analyze WebSocket traffic and identify potential hijacking attempts.

### Prevention

Preventing CSWH requires implementing several security measures:

1. **Origin Validation**: Ensure that WebSocket connections are only accepted from trusted origins.
2. **Token-Based Authentication**: Use tokens to authenticate WebSocket connections, ensuring that only authorized clients can establish connections.
3. **Same-Origin Policy**: Enforce the same-origin policy to restrict interactions between different domains.

#### Secure Coding Practices

Here is an example of how to implement token-based authentication in a WebSocket server:

```javascript
const WebSocket = require('ws');
const express = require('express');
const app = express();
const wss = new WebSocket.Server({ noServer: true });

app.use(express.json());

app.post('/connect', (req, res) => {
    const { token } = req.body;
    if (!isValidToken(token)) {
        return res.status(401).send('Invalid token');
    }
    res.send('Token validated successfully');
});

function isValidToken(token) {
    // Implement your token validation logic here
    return true; // Placeholder
}

wss.on('connection', (ws, req) => {
    const { token } = req.query;
    if (!isValidToken(token)) {
        ws.close(4000, 'Invalid token');
        return;
    }
    ws.on('message', (message) => {
        console.log(`Received message: ${message}`);
    });
});

const server = app.listen(8080, () => {
    console.log('Server listening on port 8080');
});
server.on('upgrade', (request, socket, head) => {
    wss.handleUpgrade(request, socket, head, (ws) => {
        wss.emit('connection', ws, request);
    });
});
```

### Configuration Hardening

Hardening configurations involves setting up security policies and ensuring that WebSocket connections are properly secured. For example, in an Nginx configuration, you might set up WebSocket proxying with origin validation:

```nginx
http {
    map $http_origin $allowed_origin {
        default "";
        "http://trusted.origin.com" "http://trusted.origin.com";
    }

    server {
        listen 80;

        location /chat {
            proxy_pass http://websocket_backend;
            proxy_set_header Origin $allowed_origin;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Mitigations

Mitigating CSWH involves a combination of technical controls and operational practices:

1. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.
2. **User Education**: Educate users about the risks of clicking on suspicious links or visiting untrusted websites.
3. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to potential CSWH attacks.

### Full HTTP Request and Response Example

Here is a complete example of an HTTP request and response for establishing a WebSocket connection:

#### HTTP Request

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

#### HTTP Response

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbWXPNGu
```

### Expected Result

Upon successful establishment of the WebSocket connection, the server and client can exchange data frames in real-time.

---
<!-- nav -->
[[05-Hands-On Practice Labs|Hands-On Practice Labs]] | [[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/00-Overview|Overview]] | [[07-Preventing Cross-Site WebSocket Hijacking|Preventing Cross-Site WebSocket Hijacking]]
