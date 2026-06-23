---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Lab 11: SameSite Strict Bypass via Sibling Domain

In this lab, we will demonstrate how to bypass the `SameSite=Strict` attribute using a sibling domain. We will walk through the process step-by-step, including crafting the malicious link and verifying the bypass.

### Prerequisites

Before starting the lab, ensure you have the following:

1. **Target Application**: A web application with the `SameSite=Strict` attribute set on its session cookies.
2. **Sibling Domain**: A domain that shares the same top-level domain as the target application.
3. **Burp Suite**: A tool for intercepting and manipulating HTTP requests.

### Step-by-Step Walkthrough

1. **Register Sibling Domain**:
   - Register a domain that is a sibling of the target domain. For example, if the target domain is `example.com`, register `sub.example.com`.

2. **Craft Malicious Link**:
   - Craft a malicious link that, when clicked, sends a request to the target domain. For example:
     ```html
     <a href="https://example.com/action?param=value">Click Here</a>
     ```

3. **URL Encode Script**:
   - If the malicious link contains JavaScript, ensure it is URL-encoded. For example, using Burp Suite:
     ```plaintext
     javascript:alert('XSS');
     ```
     Encoded:
     ```plaintext
     javascript%3Aalert%28%27XSS%27%29
     ```

4. **Intercept Request**:
   - Use Burp Suite to intercept the request sent from the sibling domain. Ensure the session cookie is transmitted.

5. **Verify Bypass**:
   - Verify that the unauthorized action is performed on the target domain.

### Complete Example

Let's walk through a complete example, including the HTTP request and response.

#### Target Application: `example.com`

#### Sibling Domain: `sub.example.com`

#### Malicious Link:
```html
<a href="https://example.com/action?param=value">Click Here</a>
```

#### URL-Encoded Script:
```plaintext
javascript%3Aalert%28%27XSS%27%29
```

#### HTTP Request:
```http
POST /action HTTP/1.1
Host: example.com
Cookie: session=abc123
Content-Type: application/x-www-form-urlencoded

param=value&script=javascript%3Aalert%28%27XSS%27%29
```

#### HTTP Response:
```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Action Performed</title>
</head>
<body>
    <h1>Thanks! I hope this doesn't come back to bite me.</h1>
</body>
</html>
```

### How to Prevent / Defend Against the Lab Scenario

To prevent the sibling domain bypass in this lab scenario, implement the following defenses:

1. **Strict Content Security Policy (CSP)**:
   - Configure CSP to restrict the sources of content that can be loaded on the page.
   - Example CSP header:
     ```http
     Content-Security-Policy: default-src 'self'; script-src 'self';
     ```

2. **Subresource Integrity (SRI)**:
   - Ensure that external resources are loaded securely and cannot be tampered with.
   - Example SRI hash:
     ```html
     <script src="https://example.com/script.js" integrity="sha384-abc123"></script>
     ```

3. **Server-Side Validation**:
   - Validate all inputs on the server-side to prevent unauthorized actions.
   - Example secure code:
     ```python
     def handle_action(request):
         param = request.POST.get('param')
         if not param:
             return HttpResponseBadRequest("Invalid parameter")
         # Perform action
         return HttpResponse("Action performed successfully")
     ```

### Vulnerable vs Secure Code

#### Vulnerable Code:
```python
def handle_action(request):
    param = request.POST.get('param')
    # Perform action without validation
    return HttpResponse("Action performed successfully")
```

#### Secure Code:
```python
def handle_action(request):
    param = request.POST.get('param')
    if not param:
        return HttpResponseBadRequest("Invalid parameter")
    # Perform action
    return HttpResponse("Action performed successfully")
```

### Detection and Monitoring

To detect and monitor CSRF attempts, implement the following:

1. **Log Analysis**:
   - Regularly review server logs to detect any unusual activity that might indicate a CSRF attempt.
   - Example log entry:
     ```plaintext
     [20/Mar/2023:12:00:00] "POST /action HTTP/1.1" 200 1234
     ```

2. **Security Tools**:
   - Use security tools like Burp Suite to intercept and analyze HTTP requests.
   - Example Burp Suite interception:
     ```plaintext
     POST /action HTTP/1.1
     Host: example.com
     Cookie: session=abc123
     Content-Type: application/x-www-form-urlencoded

     param=value&script=javascript%3Aalert%28%27XSS%27%29
     ```

### Practice Labs

For hands-on practice with CSRF and sibling domain bypass, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF and related vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Includes labs on CSRF and other web application vulnerabilities.

By thoroughly understanding and implementing these defensive measures, you can significantly reduce the risk of CSRF attacks and ensure the security of your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/01-Introduction to Cross-Site Request Forgery (CSRF)|Introduction to Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/00-Overview|Overview]] | [[03-Bypassing SameSite=Strict via Sibling Domain|Bypassing SameSite=Strict via Sibling Domain]]
