---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Using POST Requests for Credentials

### What Are POST Requests?

POST requests are HTTP methods used to send data to a server. Unlike GET requests, which append data to the URL, POST requests send data in the body of the request, making it less visible and less likely to be logged.

### Why Use POST Requests?

Using POST requests to transmit credentials reduces the risk of exposure through URL logging and shoulder surfing. GET requests can leave traces in browser history, server logs, and proxy logs, making them more vulnerable.

### How to Use POST Requests

Always use POST requests to transmit credentials. Ensure that the server-side logic processes these requests securely.

#### Real-World Example: SQL Injection (CVE-2018-1281)

SQL injection vulnerabilities can occur when user input is improperly sanitized. Using POST requests can help mitigate this risk by keeping sensitive data out of the URL.

### How to Prevent / Defend

**Detection:**
- Review server logs for GET requests containing sensitive data.
- Use security scanners to identify insecure usage of HTTP methods.

**Prevention:**
- Always use POST requests for transmitting credentials.
- Sanitize and validate all user inputs.

**Secure Coding Fix:**
```http
# Example of a POST request
POST /api/login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=admin&password=secret
```

---
<!-- nav -->
[[22-Using Encrypted Channels|Using Encrypted Channels]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[24-Verification and Validation Logic|Verification and Validation Logic]]
