---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## HTTP Host Header Attacks

### Background Theory

The `Host` header is a crucial component of HTTP requests. It specifies the domain name of the server being contacted, allowing a single IP address to serve multiple websites. This header is essential for virtual hosting, where multiple domains share the same IP address. However, this flexibility can introduce security vulnerabilities if not handled correctly.

#### What is the `Host` Header?

The `Host` header is part of the HTTP request headers. It is defined in RFC 7230 and is required in HTTP/1.1 requests. Its primary function is to identify the host and port number of the resource being requested. For example:

```http
GET /index.html HTTP/1.1
Host: www.example.com
```

In this request, `www.example.com` is the host being accessed.

#### Why is the `Host` Header Important?

The `Host` header is critical for routing requests to the correct server and handling virtual hosting. Without it, a server would not know which site to serve when multiple domains are hosted on the same IP address.

### Vulnerability: Flawed Request Parsing

When a web application improperly parses the `Host` header, it can lead to various security issues, including Server-Side Request Forgery (SSRF). SSRF occurs when an attacker can manipulate the application to make unintended requests to internal resources or other external services.

#### Real-World Example: CVE-2021-21972

A notable example of an SSRF vulnerability due to improper `Host` header handling is CVE-2021-21972, affecting the Jenkins CI/CD platform. In this case, an attacker could craft a malicious `Host` header to trick the application into making requests to internal resources, potentially leading to unauthorized data exposure or further exploitation.

### Detailed Walkthrough

Let's delve into the specific scenario described in the lecture transcript.

#### Initial Setup

We start with a web application that allows users to delete accounts. The application uses the `Host` header to determine the target server. Here’s a typical HTTP request:

```http
POST /deleteUser HTTP/1.1
Host: www.example.com
Content-Type: application/x-www-form-urlencoded

username=carlos
```

This request attempts to delete the user `carlos`. However, the application fails to validate the `Host` header properly, leading to potential SSRF attacks.

#### Exploiting the Vulnerability

To exploit this vulnerability, we need to manipulate the `Host` header to point to an internal IP address or another controlled resource. Let's assume the internal IP address is `192.168.243.10`.

1. **Craft the Malicious Request**

   We modify the `Host` header to point to the internal IP address:

   ```http
   POST /deleteUser HTTP/1.1
   Host: 192.168.243.10
   Content-Type: application/x-www-form-urlencoded

   username=carlos
   ```

2. **Send the Request**

   Using a tool like Burp Suite, we intercept and modify the request:

   ```http
   POST /deleteUser HTTP/1.1
   Host: 192.168.243.10
   Content-Type: application/x-www-form-urlencoded

   username=carlos
   ```

3. **Observe the Response**

   The application should now attempt to contact the internal IP address. Depending on the server setup, this might result in a successful request or an error.

### Detailed Example

Let's walk through a more detailed example using a hypothetical web application.

#### Step-by-Step Mechanics

1. **Initial Request**

   The initial request to delete a user:

   ```http
   POST /deleteUser HTTP/1.1
   Host: www.example.com
   Content-Type: application/x-www-form-urlencoded

   username=carlos
   ```

2. **Intercept and Modify**

   Using Burp Suite, we intercept the request and modify the `Host` header:

   ```http
   POST /deleteUser HTTP/1.1
   Host: 192.168.243.10
   Content-Type: application/x-www-form-urlencoded

   username=carlos
   ```

3. **Send Modified Request**

   Send the modified request and observe the response:

   ```http
   HTTP/1.1 404 Not Found
   Date: Mon, 20 Mar 2023 12:00:00 GMT
   Server: Apache/2.4.41 (Ubuntu)
   Content-Length: 0
   Connection: close
   ```

   The response indicates that the resource was not found, suggesting that the internal IP address does not have a matching service.

### Common Pitfalls and Detection

#### Pitfall: Incorrect Validation

One common pitfall is failing to validate the `Host` header against a whitelist of allowed domains. This oversight can lead to SSRF attacks.

#### Detection

Detection of SSRF vulnerabilities often involves monitoring network traffic and analyzing logs for unexpected requests to internal IP addresses or other sensitive resources.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Validate the `Host` Header**

   Ensure that the `Host` header is validated against a whitelist of allowed domains. This prevents attackers from manipulating the header to point to unauthorized resources.

   ```python
   def validate_host_header(request):
       allowed_hosts = ['www.example.com', 'api.example.com']
       if request.headers['Host'] not in allowed_hosts:
           raise ValueError("Invalid Host header")
   ```

2. **Use Absolute URLs**

   When constructing URLs, use absolute URLs instead of relative ones to avoid unintended requests to internal resources.

   ```python
   def construct_url(host, path):
       return f"https://{host}{path}"
   ```

#### Configuration Hardening

1. **Web Server Configuration**

   Configure your web server to reject requests with invalid `Host` headers. For example, in Nginx:

   ```nginx
   http {
       include       mime.types;
       default_type  application/octet-stream;

       sendfile        on;
       keepalive_timeout  65;

       server {
           listen       80;
           server_name  www.example.com;

           location / {
               if ($host != 'www.example.com') {
                   return 444;
               }
               # Other configurations
           }
       }
   }
   ```

2. **Firewall Rules**

   Implement firewall rules to block outgoing requests to internal IP addresses or other sensitive resources.

#### Real-World Example: Secure Configuration

Consider a secure configuration for an application server:

```nginx
server {
    listen 80;
    server_name www.example.com;

    location / {
        if ($host != 'www.example.com') {
            return 444;
        }

        proxy_pass http://backend_server;
    }
}
```

In this configuration, any request with an invalid `Host` header is rejected.

### Practice Labs

For hands-on practice with HTTP Host Header attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including SSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to explore and understand the intricacies of HTTP Host Header attacks and how to defend against them.

### Conclusion

Understanding and defending against HTTP Host Header attacks is crucial for maintaining the security of web applications. By validating the `Host` header, using absolute URLs, and implementing proper configuration hardening, developers can significantly reduce the risk of SSRF and other related vulnerabilities. Regularly testing and auditing applications can help ensure they remain secure against these types of attacks.

---
<!-- nav -->
[[02-HTTP Host Header Attacks and SSRF Vulnerabilities|HTTP Host Header Attacks and SSRF Vulnerabilities]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/00-Overview|Overview]] | [[04-Lab Setup and Tools|Lab Setup and Tools]]
