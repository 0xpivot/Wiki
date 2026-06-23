---
course: Web Security
topic: WebSockets Vulnerabilities
tags: [web-security]
---

## Introduction to WebSockets and Their Role in Modern Web Applications

WebSockets provide a full-duplex communication channel over a single, long-lived connection between a client and a server. Unlike traditional HTTP requests, which are stateless and require a new connection for each request, WebSockets maintain a persistent connection, allowing for real-time data exchange. This makes them ideal for applications such as live chat, real-time collaboration tools, and online gaming.

### Background Theory

WebSockets operate over two protocols: `ws` for unencrypted connections and `wss` for encrypted connections using TLS. The WebSocket protocol starts with an HTTP handshake, after which the connection switches to a binary protocol for data exchange.

#### WebSocket Handshake Example

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

The server responds with:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbWXPNGu
```

After the handshake, the connection is established, and both parties can send and receive data frames.

### Real-World Examples

WebSockets are widely used in modern web applications. For instance, popular platforms like Slack and Facebook Messenger utilize WebSockets for real-time messaging. Additionally, financial trading platforms often rely on WebSockets to deliver real-time market updates.

---
<!-- nav -->
[[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/01-Introduction to WebSockets Vulnerabilities|Introduction to WebSockets Vulnerabilities]] | [[Web Security (PortSwigger)/14-WebSockets Vulnerabilities/03-Lab 3 Cross site WebSocket hijacking/00-Overview|Overview]] | [[03-Introduction to WebSockets|Introduction to WebSockets]]
