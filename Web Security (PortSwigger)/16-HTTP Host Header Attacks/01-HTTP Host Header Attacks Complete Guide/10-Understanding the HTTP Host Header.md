---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Understanding the HTTP Host Header

### What is the HTTP Host Header?

The HTTP `Host` header is a mandatory request header that specifies the domain name that the client wants to access. For instance, if a user wants to visit the site `RanaKhalil.com`, the user's browser will generate an HTTP request that includes the `Host` header specifying the domain of the site. Here’s an example of such a request:

```http
GET / HTTP/1.1
Host: RanaKhalil.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
```

In this example, the `Host` header is set to `RanaKhalil.com`.

### Why is the `Host` Header Necessary?

Historically, each IP address used to host a single domain. However, with the advent of cloud hosting, shared infrastructure, and the exhaustion of IPv4 addresses, it became common for multiple domains or applications to share the same IP address. This shift necessitated the introduction of the `Host` header to help identify which backend component the client wants to communicate with.

#### Historical Context

Before the widespread adoption of the `Host` header, each IP address was associated with a single domain. This meant that the server could determine which site to serve based solely on the IP address. However, this approach became unsustainable due to the following reasons:

- **IPv4 Address Exhaustion**: The number of available IPv4 addresses is limited, and they were quickly being exhausted. This led to the need for more efficient ways to manage IP addresses.
- **Cloud Hosting and Shared Infrastructure**: Modern web hosting often involves shared infrastructure where multiple domains are hosted on the same server. Without the `Host` header, it would be impossible to route traffic correctly to the intended domain.

### Virtual Hosting

Virtual hosting is a technique where a single web server hosts multiple websites or applications. In this scenario, the `Host` header is crucial because it allows the server to determine which site the client is trying to access through the specific IP address.

#### Example of Virtual Hosting

Consider a web server with the IP address `192.168.1.1`. This server hosts two different websites: `example.com` and `testsite.net`. When a client sends a request to `192.168.1.1`, the `Host` header will specify whether the request is intended for `example.com` or `testsite.net`.

Here’s an example of a request to `example.com`:

```http
GET / HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
```

And here’s an example of a request to `testsite.net`:

```http
GET / HTTP/1.1
Host: testsite.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
```

### Separate Web Servers

Another use case for the `Host` header is when each website is hosted on its own distinct web server. In this scenario, the `Host` header helps the load balancer or reverse proxy to route the request to the correct server.

#### Example of Separate Web Servers

Suppose we have two separate web servers, each hosting a different website. Server A hosts `example.com`, and Server B hosts `testsite.net`. A load balancer routes incoming requests to the appropriate server based on the `Host` header.

Here’s an example of a request to `example.com`:

```http
GET / HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
```

And here’s an example of a request to `testsite.net`:

```http
GET / HTTP/1.1
Host: testsite.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
```

### Potential Vulnerabilities

While the `Host` header is essential for routing requests correctly, it can also introduce vulnerabilities if not handled properly. One such vulnerability is the HTTP Host Header Attack, where an attacker manipulates the `Host` header to bypass security measures or gain unauthorized access.

#### Real-World Examples

One notable example of a Host Header Attack is the CVE-2018-1337, also known as "Cloudbleed." This vulnerability affected Cloudflare's CDN service, where an attacker could manipulate the `Host` header to leak sensitive information from other customers' websites.

Another example is the CVE-2019-11510, which affected the Jenkins Continuous Integration server. An attacker could manipulate the `Host` header to bypass authentication and gain unauthorized access to the server.

### How to Prevent / Defend Against HTTP Host Header Attacks

To prevent HTTP Host Header attacks, it is crucial to implement proper validation and sanitization of the `Host` header. Here are some steps to ensure security:

1. **Validate the `Host` Header**: Ensure that the `Host` header matches a list of allowed domains. This can be done using a whitelist approach.
2. **Sanitize the `Host` Header**: Remove any potentially malicious characters or patterns from the `Host` header.
3. **Use Secure Headers**: Implement additional security headers such as `Strict-Transport-Security` and `Content-Security-Policy` to further protect against attacks.
4. **Regular Audits and Monitoring**: Regularly audit and monitor your web server configurations to detect any suspicious activity related to the `Host` header.

#### Example of Secure Configuration

Here’s an example of a secure configuration using Nginx:

```nginx
server {
    listen 80;
    server_name example.com;

    if ($host != 'example.com') {
        return 444;
    }

    location / {
        root /var/www/example.com;
        index index.html;
    }
}
```

In this configuration, Nginx checks if the `Host` header matches `example.com`. If it does not match, the server returns a 444 status code, effectively closing the connection.

### Conclusion

The HTTP `Host` header is a critical component of modern web hosting, enabling the efficient management of multiple domains on a single IP address. While it provides significant benefits, it also introduces potential vulnerabilities if not handled securely. By implementing proper validation, sanitization, and monitoring, you can protect your web server from HTTP Host Header attacks and ensure the security of your applications.

### Practice Labs

For hands-on experience with HTTP Host Header attacks, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including HTTP Host Header attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and understand the intricacies of HTTP Host Header attacks and how to defend against them.

---
<!-- nav -->
[[09-Understanding Host Header Vulnerabilities|Understanding Host Header Vulnerabilities]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/01-HTTP Host Header Attacks Complete Guide/00-Overview|Overview]] | [[11-Web Cache Poisoning|Web Cache Poisoning]]
