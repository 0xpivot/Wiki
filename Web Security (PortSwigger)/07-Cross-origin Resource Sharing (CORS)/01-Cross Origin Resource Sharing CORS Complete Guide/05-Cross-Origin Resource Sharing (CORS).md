---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## Cross-Origin Resource Sharing (CORS)

Cross-Origin Resource Sharing (CORS) is a mechanism that allows web servers to specify which domains are permitted to access resources hosted on their servers. This is necessary because the Same Origin Policy restricts cross-origin requests by default.

### What is CORS?

CORS is a security feature implemented by web browsers to allow or deny cross-origin requests based on specific headers sent by the server. These headers inform the browser whether a resource can be accessed from a different origin.

### How CORS Works

When a browser makes a cross-origin request, it first sends a preflight request to the server. The preflight request is an `OPTIONS` request that includes the `Access-Control-Request-Method` and `Access-Control-Request-Headers` headers. The server responds with appropriate CORS headers to indicate whether the actual request is allowed.

#### Example Preflight Request

```http
OPTIONS /api/data HTTP/1.1
Host: api.example.com
Origin: http://client.example.com
Access-Control-Request-Method: GET
Access-Control-Request-Headers: Authorization
```

#### Example Preflight Response

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://client.example.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Authorization
Access-Control-Max-Age: 86400
```

If the preflight response indicates that the actual request is allowed, the browser proceeds with the actual request.

#### Example Actual Request

```http
GET /api/data HTTP/1.1
Host: api.example.com
Origin: http://client.example.com
Authorization: Bearer abcdefg
```

#### Example Actual Response

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://client.example.com
Content-Type: application/json
{
  "data": "some data"
}
```

### CORS Headers

Several headers are used in CORS to control access to resources:

- **`Access-Control-Allow-Origin`:** Specifies the origins that are allowed to access the resource. It can be a specific origin or `*` to allow all origins.
- **`Access-Control-Allow-Methods`:** Lists the HTTP methods that are allowed for the resource.
- **`Access-Control-Allow-Headers`:** Lists the headers that are allowed in the request.
- **`Access-Control-Max-Age`:** Indicates how long the results of a preflight request can be cached.

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-3427 (CORS Misconfiguration):** This vulnerability occurred due to improper configuration of CORS headers, allowing unauthorized access to sensitive resources.
  
- **CVE-2022-23305 (CORS Bypass):** This vulnerability allowed attackers to bypass CORS restrictions through a crafted request.

### How to Prevent / Defend

#### Detection

To detect potential CORS misconfigurations, you can use tools like:

- **Burp Suite:** A comprehensive toolkit for web application security testing.
- **OWASP ZAP:** An open-source web application security scanner.

#### Prevention

To prevent CORS misconfigurations, follow these best practices:

- **Configure CORS Headers Properly:** Ensure that CORS headers are configured correctly to allow only trusted origins.
- **Use Content Security Policy (CSP):** Implement strict CSP rules to control the sources of content that can be loaded.
- **Validate User Input:** Always validate user input to prevent injection attacks.

#### Secure Coding Fixes

Here’s an example of how to configure CORS headers securely:

```javascript
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'http://client.example.com');
  res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Authorization');
  res.header('Access-Control-Max-Age', 86400);
  next();
});
```

In this example, the `Access-Control-Allow-Origin` header is set to a specific origin, and other CORS headers are configured to allow only trusted methods and headers.

### Conclusion

Cross-Origin Resource Sharing (CORS) is a critical mechanism that allows web servers to control access to resources across different origins. By understanding how CORS works and implementing proper security measures, you can better secure your web applications against potential threats.

---

---
<!-- nav -->
[[04-Access-Control-Allow-Origin Header|Access-Control-Allow-Origin Header]] | [[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[06-Exploiting CORS Vulnerabilities|Exploiting CORS Vulnerabilities]]
