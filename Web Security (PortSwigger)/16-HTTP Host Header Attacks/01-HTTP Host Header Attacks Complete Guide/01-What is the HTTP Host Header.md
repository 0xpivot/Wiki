---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## What is the HTTP Host Header?

The HTTP Host header is a crucial component of the Hypertext Transfer Protocol (HTTP) used to specify the domain name or IP address of the server being requested. This header is essential because it allows a single server to host multiple websites, a practice known as virtual hosting. When a client sends an HTTP request to a server, the Host header tells the server which website or application to serve.

### Why Does the Host Header Exist?

The Host header was introduced in HTTP/1.1 to support virtual hosting. Before this, servers could only host one website per IP address. With the introduction of the Host header, a single server can handle requests for multiple domains, making efficient use of IP addresses and simplifying server management.

#### Example of Virtual Hosting

Consider a server with the IP address `192.168.1.1`. This server hosts two websites: `example.com` and `testsite.net`. When a client sends a request to `192.168.1.1`, the Host header specifies which website to serve:

```http
GET /index.html HTTP/1.1
Host: example.com
```

The server uses the Host header to determine that the request is intended for `example.com` and serves the appropriate content.

### Common Use Cases

The Host header is used in various scenarios, including:

- **Virtual Hosting**: Serving multiple websites from a single IP address.
- **Reverse Proxy**: Routing requests to different backend servers based on the Host header.
- **Load Balancing**: Distributing traffic across multiple servers based on the Host header.

### Real-World Examples

One real-world example of the Host header in action is Google's load balancing infrastructure. Google uses the Host header to route requests to the appropriate data center, ensuring optimal performance and reliability.

### How the Host Header Works Under the Hood

When a client sends an HTTP request, the Host header is included in the request headers. The server reads this header and uses it to determine which website or application to serve. Here’s a detailed breakdown of the process:

1. **Client Sends Request**: The client sends an HTTP request to the server, including the Host header.
2. **Server Reads Host Header**: The server reads the Host header to determine which website or application to serve.
3. **Content Delivery**: The server delivers the appropriate content based on the Host header.

### HTTP Request Example

Here is a complete HTTP request with the Host header:

```http
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

### HTTP Response Example

Here is a corresponding HTTP response:

```http
HTTP/1.1 200 OK
Date: Mon, 27 Jul 2021 12:28:53 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: keep-alive

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example.com</h1>
</body>
</html>
```

### Mermaid Diagram: Request Flow

A mermaid diagram can help visualize the request flow involving the Host header:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: GET /index.html HTTP/1.1\r\nHost: example.com
    Server-->>Client: HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n<!DOCTYPE html>\r\n<html>\r\n<head>\r\n<title>Example Page</title>\r\n</head>\r\n<body>\r\n<h1>Welcome to Example.com</h1>\r\n</body>\r\n</html>
```

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[02-Finding and Exporting Host Header Vulnerabilities|Finding and Exporting Host Header Vulnerabilities]]
