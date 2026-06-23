---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Introduction to Basic Authorization Over HTTP

Transport Layer Security (TLS) issues are critical in the realm of API security, especially when dealing with basic authorization over HTTP. This section delves into the vulnerabilities associated with basic access authentication over HTTP and provides comprehensive guidance on how to mitigate these risks.

### Background Theory

Basic access authentication is a simple method for an HTTP user agent to provide a username and password when making a request. This method is defined in RFC 7617 and is widely supported by web servers and clients. However, it is inherently insecure when used over plain HTTP due to the lack of encryption.

#### How Basic Authentication Works

When a client makes a request to a server that requires basic authentication, the server responds with a `401 Unauthorized` status and includes a `WWW-Authenticate` header. The client then sends the credentials in the `Authorization` header using Base64 encoding.

```http
GET /protected-resource HTTP/1.1
Host: example.com
```

The server responds with:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Basic realm="Secure Area"
```

The client then sends the credentials:

```http
GET /protected-resource HTTP/1.1
Host: example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

Here, `dXNlcm5hbWU6cGFzc3dvcmQ=` is the Base64 encoded string of `username:password`.

### Vulnerabilities of Basic Authentication Over HTTP

The primary vulnerability of basic authentication over HTTP is the transmission of credentials in clear text. Since HTTP does not encrypt data, anyone with access to the network traffic can intercept and read the credentials.

#### Real-World Examples

One notable example of this vulnerability was observed in the Equifax breach of 2017. Although the breach itself was primarily due to an unpatched Apache Struts vulnerability, the use of basic authentication over HTTP contributed to the overall insecurity of the system.

### Packet Sniffing Attack

Packet sniffing is a technique used to capture and analyze network packets. An attacker can use tools like Wireshark to intercept and read the credentials transmitted over HTTP.

#### Using Wireshark for Demonstration

Wireshark is a powerful network protocol analyzer that can be used to capture and display network traffic. Here’s how to set up Wireshark to demonstrate the interception of basic authentication credentials:

1. **Install Wireshark**: Download and install Wireshark from the official website.
2. **Start Capture**: Open Wireshark and start a new capture. Select the appropriate network interface.
3. **Send Request**: Make a request to a server that requires basic authentication over HTTP.
4. **Analyze Traffic**: Wireshark will capture the network traffic, including the HTTP request and response. You can filter the traffic to view only HTTP traffic.

```mermaid
sequenceDiagram
    participant Client
    participant Server
    participant Wireshark
    Client->>Server: GET /protected-resource HTTP/1.1
    Server-->>Client: HTTP/1.1 401 Unauthorized
    Client->>Server: GET /protected-resource HTTP/1.1
    Client->>Server: Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
    Wireshark-->>Client: Capturing traffic
    Wireshark-->>Server: Capturing traffic
```

### Pitfalls and Common Mistakes

1. **Using HTTP Instead of HTTPS**: Always use HTTPS to encrypt the communication between the client and the server.
2. **Hardcoding Credentials**: Avoid hardcoding credentials in your application. Use environment variables or secure vaults instead.
3. **Ignoring Security Headers**: Ensure that security headers such as `Strict-Transport-Security` are properly configured.

### How to Prevent / Defend

#### Detection

To detect the use of basic authentication over HTTP, you can use network monitoring tools like Wireshark or intrusion detection systems (IDS).

#### Prevention

1. **Use HTTPS**: Always use HTTPS to encrypt the communication between the client and the server.
2. **Configure Strict-Transport-Security (HSTS)**: HSTS ensures that the browser only communicates with the server over HTTPS.

```http
HTTP/1.1 200 OK
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

3. **Avoid Basic Authentication**: Consider using more secure authentication methods such as OAuth 2.0 or JWT.

#### Secure Coding Fixes

Here is an example of how to securely configure an API to use HTTPS and HSTS:

**Vulnerable Code:**

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/protected-resource')
def protected_resource():
    auth = request.authorization
    if auth and auth.username == 'admin' and auth.password == 'secret':
        return "Welcome, admin!"
    else:
        return "Unauthorized", 401

if __name__ == '__main__':
    app.run()
```

**Secure Code:**

```python
from flask import Flask, request
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)

@app.route('/protected-resource')
def protected_resource():
    auth = request.authorization
    if auth and auth.username == 'admin' and auth.password == 'secret':
        return "Welcome, admin!"
    else:
        return "Unauthorized", 401

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
```

In this example, `Flask-Talisman` is used to enforce HSTS and other security headers.

### Hands-On Labs

For practical experience with API security and basic authentication, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on broken authentication and sensitive data exposure.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for testing and learning purposes.

### Conclusion

Basic access authentication over HTTP is inherently insecure due to the transmission of credentials in clear text. By understanding the vulnerabilities and implementing proper security measures, you can significantly reduce the risk of unauthorized access. Always use HTTPS and consider more secure authentication methods to protect your APIs.

---
<!-- nav -->
[[API Security/20-Transport Layer Security Issues/01-Basic Authorization over HTTP/00-Overview|Overview]] | [[02-Transport Layer Security Issues Basic Authorization Over HTTP|Transport Layer Security Issues Basic Authorization Over HTTP]]
