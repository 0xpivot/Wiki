---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## How to Prevent / Defend Against CORS Vulnerabilities

### Detection

To detect CORS vulnerabilities, you can use tools like Burp Suite, OWASP ZAP, or custom scripts to check the `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials` headers. These tools can help identify if the headers are set dynamically or incorrectly.

### Prevention

1. **Secure Configuration**:
   - Ensure that the `Access-Control-Allow-Origin` header is set to a specific origin rather than using the wildcard `*`.
   - Only set the `Access-Control-Allow-Credentials` header to `true` when necessary and ensure that the origin is correctly configured.

2. **Secure Coding Practices**:
   - Always validate and sanitize input to prevent dynamic generation of the `Access-Control-Allow-Origin` header.
   - Use secure coding practices to ensure that sensitive data is not exposed through CORS misconfigurations.

### Secure Code Fix

#### Vulnerable Code

```javascript
app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", req.headers.origin);
    res.header("Access-Control-Allow-Credentials", "true");
    next();
});
```

#### Fixed Code

```javascript
const allowedOrigins = ['https://example.com'];

app.use((req, res, next) => {
    const origin = req.headers.origin;
    if (allowedOrigins.includes(origin)) {
        res.header("Access-Control-Allow-Origin", origin);
        res.header("Access-Control-Allow-Credentials", "true");
    } else {
        res.header("Access-Control-Allow-Origin", "");
    }
    next();
});
```

### Hardening

- **Use Content Security Policy (CSP)**: Implement CSP to further restrict what resources can be loaded and executed within your web application.
- **Regular Audits**: Conduct regular security audits and penetration testing to identify and mitigate CORS vulnerabilities.

### Practice Labs

For hands-on practice with CORS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on CORS exploitation and mitigation.
- **OWASP Juice Shop**: Provides a vulnerable web application where you can practice identifying and exploiting CORS vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Another great resource for practicing web security concepts, including CORS.

By thoroughly understanding and implementing these preventive measures, you can significantly reduce the risk of CORS-related vulnerabilities in your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/09-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[11-Pre-flight Requests|Pre-flight Requests]]
