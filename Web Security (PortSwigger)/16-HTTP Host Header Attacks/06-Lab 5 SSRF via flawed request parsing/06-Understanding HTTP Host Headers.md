---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## Understanding HTTP Host Headers

The HTTP `Host` header is a critical component of the HTTP protocol, used to specify the domain name of the server being contacted. This header is essential for virtual hosting, where multiple domains share the same IP address. The `Host` header allows the server to determine which site to serve based on the requested domain.

### Purpose and Syntax

The `Host` header is included in every HTTP request and follows the format:

```
GET /path/to/resource HTTP/1.1
Host: www.example.com
```

Here, `www.example.com` is the domain name of the server being contacted. The `Host` header is required for HTTP/1.1 and higher versions of the protocol.

### Why the `Host` Header Matters

The `Host` header is crucial for several reasons:
1. **Virtual Hosting**: Multiple websites can be hosted on a single IP address by using different `Host` headers.
2. **Security**: Proper handling of the `Host` header helps prevent various types of attacks, including Server-Side Request Forgery (SSRF).

### Potential Vulnerabilities

Improper handling of the `Host` header can lead to vulnerabilities such as SSRF. SSRF occurs when an application makes a request to an internal or external resource based on user input, without proper validation. If the `Host` header is not correctly validated, an attacker can manipulate it to make requests to unintended hosts.

### Real-World Example: CVE-2021-21972

A notable example of an SSRF vulnerability involving the `Host` header is CVE-2021-21972, which affected the Jenkins Continuous Integration server. In this case, an attacker could inject malicious content into the `Host` header, leading to unauthorized access to internal resources.

### How to Prevent / Defend

#### Detection

To detect potential SSRF vulnerabilities, you can use tools like Burp Suite, which includes features like Intruder and Repeater to test for such issues.

#### Prevention

1. **Validate Input**: Ensure that the `Host` header is validated against a whitelist of allowed domains.
2. **Use Secure Libraries**: Utilize libraries that handle HTTP requests securely, such as `axios` or `fetch`, which have built-in protections.
3. **Secure Coding Practices**: Implement secure coding practices to avoid untrusted input in HTTP requests.

### Secure Code Fix

Here’s an example of how to properly validate the `Host` header in a Node.js application:

```javascript
const express = require('express');
const app = express();

const allowedHosts = ['www.example.com', 'subdomain.example.com'];

app.use((req, res, next) => {
    const host = req.get('Host');
    if (!allowedHosts.includes(host)) {
        return res.status(403).send('Forbidden');
    }
    next();
});

app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

In this example, the `Host` header is checked against a list of allowed hosts. If the host is not in the list, a `403 Forbidden` response is returned.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/05-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/06-Lab 5 SSRF via flawed request parsing/07-Practice Questions & Answers|Practice Questions & Answers]]
