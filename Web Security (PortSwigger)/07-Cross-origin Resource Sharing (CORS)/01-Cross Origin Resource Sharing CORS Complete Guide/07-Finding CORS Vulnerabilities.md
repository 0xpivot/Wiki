---
course: Web Security
topic: Cross-origin Resource Sharing (CORS)
tags: [web-security]
---

## Finding CORS Vulnerabilities

To identify CORS vulnerabilities, you can approach the task from both a white-box and a black-box perspective.

### White-Box Testing

White-box testing involves having access to the application source code and configuration files. Here’s how you can test for CORS vulnerabilities:

1. **Review Configuration Files**: Look for CORS-related configurations in files like `nginx.conf`, `web.config`, or `.htaccess`.
2. **Check Server Headers**: Ensure that the server is not setting overly permissive CORS headers.
3. **Validate Allowed Origins**: Verify that the allowed origins are correctly specified and validated.

### Black-Box Testing

Black-box testing involves probing the application without access to its source code. Here’s how you can test for CORS vulnerabilities:

1. **Use Browser Developer Tools**: Inspect network requests and responses to see if CORS headers are present.
2. **Test with Different Origins**: Make requests from different origins to see if the server allows them.
3. **Use Automated Tools**: Tools like Burp Suite, ZAP, and CORS Anywhere can help automate the testing process.

### Example: Testing CORS with Burp Suite

Here’s a step-by-step guide to testing CORS using Burp Suite:

1. **Set Up Burp Suite**: Configure Burp Suite as a proxy and intercept HTTP traffic.
2. **Make a Request**: Send a request to the target server and observe the response.
3. **Check CORS Headers**: Look for `Access-Control-Allow-Origin` and other CORS-related headers.

```http
GET /api/data HTTP/1.1
Host: example.com
Origin: http://attacker.com
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
```

In this example, the server is allowing requests from any origin (`*`), which is a potential security risk.

---
<!-- nav -->
[[06-Exploiting CORS Vulnerabilities|Exploiting CORS Vulnerabilities]] | [[Web Security (PortSwigger)/07-Cross-origin Resource Sharing (CORS)/01-Cross Origin Resource Sharing CORS Complete Guide/00-Overview|Overview]] | [[08-Further Reading|Further Reading]]
