---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Introduction to HTTP Host Header Attacks and Web Cache Poisoning

Web cache poisoning is a type of attack where an attacker manipulates the caching mechanism of a web server or proxy to serve malicious content to unsuspecting users. This can lead to a variety of security issues, including cross-site scripting (XSS), cross-site request forgery (CSRF), and other forms of injection attacks. One of the most common vectors for this type of attack is through the manipulation of the `Host` header in HTTP requests.

### Background Theory

To understand web cache poisoning, it's essential to first grasp how web caching works. Web caching is a technique used to improve performance and reduce load on servers by storing copies of frequently accessed resources. When a client requests a resource, the cache checks if it already has a copy of that resource. If it does, it serves the cached copy instead of forwarding the request to the origin server. This reduces latency and bandwidth usage.

However, this caching mechanism can be exploited if the cache does not correctly differentiate between different requests. An attacker can manipulate the cache to store and serve malicious content, leading to a variety of security vulnerabilities.

### Key Concepts

#### Unkeyed Inputs

Unkeyed inputs are specific parts of an HTTP request that the web cache ignores when deciding whether to serve a cached response. These inputs are typically headers or query parameters that do not affect the content of the response. By manipulating these inputs, an attacker can inject a payload that will be served to other users.

For example, the `Host` header is often used as an unkeyed input because many caches do not consider it when determining if a response should be cached. This makes it an ideal vector for web cache poisoning attacks.

#### Steps to Construct a Web Cache Poisoning Attack

A typical web cache poisoning attack consists of three main steps:

1. **Identify and Evaluate Unkeyed Inputs**
2. **Elicit a Harmful Response from the Backend Server**
3. **Get the Response Cached**

Let's delve into each of these steps in detail.

### Step 1: Identify and Evaluate Unkeyed Inputs

The first step in constructing a web cache poisoning attack is to identify and evaluate unkeyed inputs. These are inputs that the web cache ignores when deciding whether to serve a cached response. Common examples of unkeyed inputs include:

- **Host Header**: The `Host` header specifies the domain name of the server being requested. Many caches do not consider this header when determining if a response should be cached.
- **User-Agent Header**: The `User-Agent` header contains information about the client making the request. Caches often ignore this header.
- **Accept-Language Header**: The `Accept-Language` header specifies the preferred language of the client. Caches may ignore this header.

To identify unkeyed inputs, you need to test the web cache to see which headers it considers when deciding whether to serve a cached response. This can be done using tools like Burp Suite or OWASP ZAP.

#### Example: Identifying Unkeyed Inputs

Consider the following HTTP request:

```http
GET /index.html HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept-Language: en-US,en;q=0.5
```

If the cache ignores the `Host`, `User-Agent`, and `Accept-Language` headers, then these can be used as unkeyed inputs.

### Step 2: Elicit a Harmful Response from the Backend Server

Once you have identified an unkeyed input, the next step is to see if that input can be used to deliver your payload and exploit a vulnerable functionality in the application. In this case, we will use the `Host` header as the unkeyed input.

#### Example: Eliciting a Harmful Response

Suppose the backend server is vulnerable to a reflected XSS attack. You can craft a request that includes a payload in the `Host` header:

```http
GET /index.html HTTP/1.1
Host: attacker.example.com"><script>alert('XSS')</script>
User-Agent: Mozilla/5.0
Accept-Language: en-US,en;q=0.5
```

When the server processes this request, it might reflect the `Host` header back in the response, leading to an XSS attack.

### Step 3: Get the Response Cached

The final step is to ensure that the harmful response is cached by the web cache. This can be achieved by making the request in such a way that the cache decides to store the response.

#### Example: Getting the Response Cached

To ensure that the response is cached, you can make the request in a way that the cache considers it a valid candidate for caching. For example, you can set the `Cache-Control` header to indicate that the response should be cached:

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Cache-Control: max-age=3600
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Welcome to Example.com</h1>
    <p><script>alert('XSS')</script></p>
</body>
</html>
```

In this example, the `Cache-Control` header indicates that the response should be cached for one hour (`max-age=3600`). This ensures that the harmful response is stored in the cache and served to subsequent requests.

### Real-World Examples

#### CVE-2021-23222: Akamai Web Cache Poisoning

In 2021, a critical vulnerability was discovered in Akamai's web caching infrastructure, tracked as CVE-2021-23222. This vulnerability allowed attackers to perform web cache poisoning attacks by manipulating the `Host` header. The vulnerability affected a wide range of websites that relied on Akamai's services, leading to potential XSS and CSRF attacks.

#### CVE-2022-22965: WordPress REST API Cache Poisoning

Another notable example is CVE-2022-22965, which affected the WordPress REST API. This vulnerability allowed attackers to perform web cache poisoning attacks by manipulating the `Host` header. The vulnerability was particularly dangerous because it affected a large number of WordPress sites, leading to potential XSS and CSRF attacks.

### How to Prevent / Defend Against Web Cache Poisoning

#### Detection

To detect web cache poisoning attacks, you can use various tools and techniques:

- **Web Application Firewalls (WAFs)**: WAFs can be configured to detect and block suspicious requests that might be indicative of a web cache poisoning attack.
- **Logging and Monitoring**: Regularly review logs to look for patterns that might indicate an attack. Look for unusual requests that contain suspicious payloads in unkeyed inputs.
- **Security Scanners**: Use security scanners like Burp Suite or OWASP ZAP to test your application for vulnerabilities related to web cache poisoning.

#### Prevention

To prevent web cache poisoning attacks, follow these best practices:

- **Validate and Sanitize Inputs**: Ensure that all inputs, including unkeyed inputs like the `Host` header, are validated and sanitized. This helps prevent attackers from injecting malicious payloads.
- **Use Secure Headers**: Set appropriate headers to control caching behavior. For example, use the `Cache-Control` header to specify how long a response should be cached.
- **Implement Content Security Policies (CSP)**: Use CSP to restrict the sources of content that can be loaded in your web pages. This helps mitigate the impact of XSS attacks.
- **Regularly Update and Patch**: Keep your web server and caching infrastructure up to date with the latest security patches.

#### Secure Coding Fixes

Here is an example of how to securely handle the `Host` header in a web application:

**Vulnerable Code:**

```python
def handle_request(request):
    host = request.headers.get('Host')
    response = f"<html><body>Welcome to {host}</body></html>"
    return response
```

**Secure Code:**

```python
import re

def handle_request(request):
    host = request.headers.get('Host')
    # Validate the host header
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', host):
        raise ValueError("Invalid Host header")
    
    # Sanitize the host header
    safe_host = re.sub(r'[^\w.-]', '', host)
    
    response = f"<html><body>Welcome to {safe_host}</body></html>"
    return response
```

In this example, the `Host` header is validated and sanitized to prevent malicious payloads from being injected.

### Configuration Hardening

To harden your web caching configuration, follow these guidelines:

- **Configure Cache-Control Headers**: Set appropriate `Cache-Control` headers to control caching behavior. For example, use `no-cache` or `no-store` to prevent sensitive data from being cached.
- **Use Secure Cookies**: Ensure that cookies are marked as `HttpOnly` and `Secure` to prevent them from being accessed by JavaScript and transmitted over HTTPS.
- **Limit Cache Size**: Limit the size of the cache to prevent it from becoming a target for denial-of-service (DoS) attacks.

### Conclusion

Web cache poisoning is a serious security threat that can lead to a variety of vulnerabilities, including XSS and CSRF attacks. By understanding the key concepts and steps involved in constructing a web cache poisoning attack, you can better defend against these threats. Regularly testing your application for vulnerabilities and implementing secure coding practices can help mitigate the risk of web cache poisoning attacks.

### Practice Labs

To gain hands-on experience with web cache poisoning attacks, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a dedicated module on web cache poisoning.
- **OWASP Juice Shop**: Provides a variety of web security challenges, including web cache poisoning.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security skills.

By completing these labs, you can gain practical experience in identifying and defending against web cache poisoning attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/04-Lab 3 Web cache poisoning via ambiguous requests/00-Overview|Overview]] | [[02-Introduction to HTTP Host Header Attacks|Introduction to HTTP Host Header Attacks]]
