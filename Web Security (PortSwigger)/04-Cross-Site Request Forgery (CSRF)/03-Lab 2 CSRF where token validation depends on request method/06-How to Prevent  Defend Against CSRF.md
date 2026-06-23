---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF

To prevent CSRF attacks, web applications should implement robust mechanisms to verify the authenticity of requests. Here are some best practices:

### Implement CSRF Tokens

CSRF tokens are unique, unpredictable values that are generated for each session and included in forms and AJAX requests. The server verifies the token before processing the request.

#### Example: Secure Form with CSRF Token

**Vulnerable Code:**

```html
<form action="/change-email" method="POST">
    <input type="text" name="email" value="new.email@example.com">
    <input type="submit" value="Change Email">
</form>
```

**Secure Code:**

```html
<form action="/change-email" method="POST">
    <input type="text" name="email" value="new.email@example.com">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="submit" value="Change Email">
</form>
```

**Server-Side Verification:**

```python
from flask import Flask, request, session

app = Flask(__name__)

@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    csrf_token = request.form['csrf_token']
    
    if csrf_token != session.get('csrf_token'):
        return "Invalid CSRF token", 403
    
    # Process the email change
    return "Email changed successfully"
```

### Use SameSite Cookies

Setting the `SameSite` attribute on cookies restricts their usage across different sites. This prevents CSRF attacks by ensuring that cookies are only sent in first-party contexts.

#### Example: Setting SameSite Attribute

```http
Set-Cookie: session=abc123; SameSite=Strict
```

### Validate HTTP Referer Header

Verifying the `Referer` header ensures that the request originates from the same site. This can be used as an additional layer of defense against CSRF attacks.

#### Example: Checking Referer Header

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/change-email', methods=['POST'])
def change_email():
    referer = request.headers.get('Referer')
    
    if not referer or not referer.startswith('https://vulnerable-app.example.com'):
        return "Invalid Referer", 403
    
    # Process the email change
    return "Email changed successfully"
```

### Use Content Security Policy (CSP)

Implementing a Content Security Policy (CSP) can help mitigate CSRF attacks by restricting the sources of content that can be loaded in the browser.

#### Example: CSP Header

```http
Content-Security-Policy: default-src 'self'
```

### Regular Security Audits

Regularly conduct security audits and penetration testing to identify and fix potential CSRF vulnerabilities.

### Conclusion

CSRF attacks are a significant threat to web applications. By implementing robust mechanisms such as CSRF tokens, SameSite cookies, and validating HTTP headers, web applications can effectively defend against these attacks. Always stay vigilant and regularly audit your applications to ensure they remain secure.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/05-Detection and Prevention|Detection and Prevention]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[07-Lab Setup CSRF Where Token Validation Depends on Request Method|Lab Setup CSRF Where Token Validation Depends on Request Method]]
