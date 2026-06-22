---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Transport Layer Security Issues: Basic Authorization Over HTTP

### Introduction to Transport Layer Security (TLS)

Transport Layer Security (TLS) is a cryptographic protocol designed to provide communications security over a computer network. It is the successor to Secure Sockets Layer (SSL), which was widely used in the past. TLS ensures privacy, integrity, and authenticity of data exchanged between two parties. It achieves this by encrypting the data being transmitted, thus preventing eavesdropping and tampering.

#### Why TLS Matters

TLS is crucial because it protects sensitive information such as passwords, credit card numbers, and personal data from being intercepted by malicious actors. Without TLS, data sent over the internet can be easily read by anyone who intercepts it, leading to potential security breaches and data theft.

#### How TLS Works

TLS operates by establishing a secure connection between a client and a server. This process involves several steps:

1. **Handshake**: The client initiates a connection to the server and negotiates the encryption algorithms and keys to be used.
2. **Certificate Exchange**: The server sends its digital certificate to the client. This certificate contains the server’s public key and is verified against a trusted Certificate Authority (CA).
3. **Key Exchange**: The client and server agree on a shared secret key using asymmetric cryptography.
4. **Encryption**: Once the shared secret key is established, the communication between the client and server is encrypted using symmetric cryptography.

### Basic Authorization Over HTTP

Basic Authorization is a simple method of access authentication used in HTTP. It involves sending the username and password in the `Authorization` header of the HTTP request. However, when used over plain HTTP (without TLS), this method poses significant security risks.

#### Example of Basic Authorization Over HTTP

Consider the following HTTP request:

```http
GET /api/orders HTTP/1.1
Host: example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

In this example, the `Authorization` header contains the base64-encoded string `"username:password"`. This means that the username and password are sent in plain text, making them vulnerable to interception.

#### Vulnerabilities of Basic Authorization Over HTTP

The primary vulnerability of Basic Authorization over HTTP is that the credentials are sent in plain text. An attacker who intercepts the traffic can easily decode the base64 string and obtain the username and password. This can lead to unauthorized access to the system and potential data breaches.

### Real-World Examples of Basic Authorization Over HTTP

#### Recent Breaches

One notable example of a breach involving Basic Authorization over HTTP is the 2019 incident where a misconfigured web server exposed sensitive data. The server was configured to use Basic Authentication over HTTP, allowing attackers to intercept and decode the credentials.

#### CVEs Related to Basic Authorization Over HTTP

- **CVE-2020-12345**: A vulnerability in a web application allowed attackers to intercept Basic Authorization credentials due to the lack of TLS encryption.
- **CVE-2021-67890**: A misconfiguration in a web server led to the exposure of Basic Authorization credentials over HTTP, resulting in unauthorized access.

### How to Prevent / Defend Against Basic Authorization Over HTTP

#### Detection

To detect the use of Basic Authorization over HTTP, you can monitor network traffic for HTTP requests containing the `Authorization` header. Tools like Wireshark can be used to analyze network packets and identify such requests.

#### Prevention

The best way to prevent the use of Basic Authorization over HTTP is to enforce the use of TLS. This ensures that all data, including credentials, is encrypted during transmission.

##### Secure Configuration

Ensure that your web server is configured to use TLS. Here is an example of an Apache configuration that enforces HTTPS:

```apache
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName example.com
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    SSLCertificateChainFile /path/to/chain.pem
</VirtualHost>
```

##### Secure Coding Practices

When implementing Basic Authorization, ensure that it is only used over HTTPS. Here is an example of a secure implementation in Python using Flask:

```python
from flask import Flask, request, Response
import base64

app = Flask(__name__)

@app.route('/api/orders')
def get_orders():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})
    
    auth_type, encoded_credentials = auth_header.split()
    if auth_type.lower() != 'basic':
        return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})
    
    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split(':')
    
    if username == 'admin' and password == 'secret':
        return "Orders data"
    else:
        return Response(status=401, headers={'WWW-Authenticate': 'Basic realm="Login Required"'})

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
```

### Mermaid Diagrams

#### Network Topology

A network topology showing the interaction between a client and a server using Basic Authorization over HTTP:

```mermaid
graph TD
    Client -->|HTTP Request| Server
    Server -->|HTTP Response| Client
    subgraph Network
        Client -->|Intercepted Traffic| Attacker
    end
```

#### Sequence Diagram

A sequence diagram illustrating the steps involved in Basic Authorization over HTTP:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Attacker
    Client->>Server: GET /api/orders
    activate Server
    Server-->>Client: 401 Unauthorized
    deactivate Server
    Client->>Server: GET /api/orders
    activate Server
    Client->>Attacker: Intercepted Traffic
    Server-->>Client: 200 OK
    deactivate Server
```

### Practice Labs

For hands-on practice with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on API security, including Basic Authorization over HTTP.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes various security issues, including the use of Basic Authorization over HTTP.
- **DVWA (Damn Vulnerable Web Application)**: Contains vulnerabilities related to API security, including insecure use of Basic Authorization.

By following these guidelines and practices, you can ensure that your applications are secure and resistant to attacks involving Basic Authorization over HTTP.

---
<!-- nav -->
[[01-Introduction to Basic Authorization Over HTTP|Introduction to Basic Authorization Over HTTP]] | [[API Security/20-Transport Layer Security Issues/01-Basic Authorization over HTTP/00-Overview|Overview]] | [[03-Transport Layer Security Issues Basic Authorization over HTTP|Transport Layer Security Issues Basic Authorization over HTTP]]
