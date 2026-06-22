---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Understanding HTTP Host Header Attacks

### Background Theory

The HTTP Host header is a crucial component of HTTP requests. It specifies the domain name of the server being contacted, allowing a single IP address to serve multiple websites. This header is essential for virtual hosting, where multiple domains share the same IP address. However, the flexibility provided by the Host header can also introduce security vulnerabilities, particularly when the server does not properly validate or sanitize the input.

### What is an HTTP Host Header Attack?

An HTTP Host Header attack occurs when an attacker manipulates the Host header in an HTTP request to achieve unauthorized access or perform malicious actions. The primary types of attacks include:

- **Host Header Injection**: Injecting arbitrary data into the Host header to bypass security checks or manipulate server behavior.
- **Web Cache Poisoning**: Exploiting the Host header to inject malicious content into a web cache, affecting other users.

### Why Does It Matter?

HTTP Host Header attacks can lead to several serious security issues:

- **Cross-Site Scripting (XSS)**: An attacker can inject malicious scripts into a web page viewed by other users.
- **Server Misconfiguration**: Improper handling of the Host header can result in server misconfiguration, leading to unauthorized access or data exposure.
- **Cache Poisoning**: Malicious content can be cached and served to legitimate users, compromising their experience and security.

### How Does It Work Under the Hood?

When a client sends an HTTP request to a server, the Host header is included in the request. The server uses this header to determine which website to serve. If the server does not properly validate the Host header, an attacker can manipulate it to achieve various goals.

#### Example of a Vulnerable Request

```http
GET /index.html HTTP/1.1
Host: attacker-controlled-domain.com
```

In this example, the attacker controls the `Host` header, potentially leading to unintended behavior on the server.

### Real-World Examples

Recent vulnerabilities and breaches involving HTTP Host Header attacks include:

- **CVE-2021-32790**: A vulnerability in the Apache HTTP Server allowed attackers to bypass security restrictions by manipulating the Host header.
- **CVE-2022-22965**: A vulnerability in Microsoft Exchange Server allowed attackers to inject malicious content into the web cache by manipulating the Host header.

### Detection and Prevention

#### Detection

To detect potential Host Header attacks, you can monitor HTTP requests for unusual or unexpected values in the Host header. Tools like Burp Suite, Wireshark, and custom logging mechanisms can help identify such anomalies.

#### Prevention

To prevent Host Header attacks, follow these best practices:

1. **Validate the Host Header**: Ensure that the Host header matches a list of valid domains.
2. **Use Content Security Policies (CSP)**: Implement CSP to mitigate the impact of XSS attacks.
3. **Regularly Update Software**: Keep your web server and related software up to date to patch known vulnerabilities.

### Secure Coding Fixes

#### Vulnerable Code Example

```python
# Vulnerable code example
def handle_request(request):
    host = request.headers.get('Host')
    if host:
        # Process the request using the host header
        process_request(host)
```

#### Secure Code Example

```python
# Secure code example
def handle_request(request):
    allowed_hosts = ['example.com', 'subdomain.example.com']
    host = request.headers.get('Host')
    if host and host in allowed_hosts:
        # Process the request using the host header
        process_request(host)
    else:
        raise ValueError("Invalid Host header")
```

### Web Cache Poisoning via Ambiguous Requests

Web cache poisoning occurs when an attacker injects malicious content into a web cache, which is then served to other users. The Host header can be manipulated to achieve this.

#### Step-by-Step Mechanics

1. **Identify the Vulnerability**: Determine if the server accepts and processes the Host header without proper validation.
2. **Inject Malicious Content**: Manipulate the Host header to inject malicious content into the cache.
3. **Exploit the Cache**: Serve the malicious content to other users who request the same resource.

#### Example of a Vulnerable Request

```http
GET /index.html HTTP/1.1
Host: attacker-controlled-domain.com
```

#### Example of a Secure Request

```http
GET /index.html HTTP/1.1
Host: example.com
```

### Real-World Example

Consider a scenario where an attacker manipulates the Host header to inject malicious JavaScript into a web cache. This JavaScript could then be served to other users, leading to an XSS attack.

#### Vulnerable Scenario

```http
GET /index.html HTTP/1.1
Host: attacker-controlled-domain.com
```

#### Secure Scenario

```http
GET /index.html HTTP/1.1
Host: example.com
```

### How to Prevent / Defend

#### Detection

Monitor HTTP requests for unusual or unexpected values in the Host header. Use tools like Burp Suite, Wireshark, and custom logging mechanisms to identify such anomalies.

#### Prevention

1. **Validate the Host Header**: Ensure that the Host header matches a list of valid domains.
2. **Use Content Security Policies (CSP)**: Implement CSP to mitigate the impact of XSS attacks.
3. **Regularly Update Software**: Keep your web server and related software up to date to patch known vulnerabilities.

### Complete Example

#### Vulnerable Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
    }
}
```

#### Secure Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        if ($host != 'example.com') {
            return 403;
        }
        proxy_pass http://backend;
    }
}
```

### Practice Labs

For hands-on practice with HTTP Host Header attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on web cache poisoning and Host Header injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios for testing and exploiting web cache poisoning.

### Conclusion

Understanding and preventing HTTP Host Header attacks is crucial for maintaining the security of web applications. By validating the Host header, implementing secure coding practices, and regularly updating software, you can significantly reduce the risk of such attacks.

---
<!-- nav -->
[[06-Lab Exercise Web Cache Poisoning via Ambiguous Requests|Lab Exercise Web Cache Poisoning via Ambiguous Requests]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]] | [[08-Understanding Web Cache Poisoning|Understanding Web Cache Poisoning]]
