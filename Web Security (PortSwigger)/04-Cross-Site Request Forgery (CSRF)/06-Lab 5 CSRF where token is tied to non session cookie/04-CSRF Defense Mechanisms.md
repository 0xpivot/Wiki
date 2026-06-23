---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## CSRF Defense Mechanisms

To defend against CSRF attacks, web applications typically employ several mechanisms, including:

1. **CSRF Tokens**: These are unique, unpredictable values that are generated for each user session and included in forms and requests.
2. **SameSite Cookies**: This attribute restricts cookies to first-party contexts, preventing them from being sent in cross-site requests.
3. **Referer Header Checks**: Ensuring that requests originate from the same origin as the web application.

### CSRF Token Mechanism

A CSRF token is a random value that is generated for each user session and included in forms and requests. When a user submits a form, the server verifies that the token matches the one stored in the session. If the tokens do not match, the request is rejected.

#### Example of CSRF Token Implementation

Let's consider a simple login form with a CSRF token:

```html
<form method="POST" action="/login">
    <input type="hidden" name="csrf_token" value="random_token_value">
    <label for="username">Username:</label>
    <input type="text" id="username" name="username">
    <label for="password">Password:</label>
    <input type="password" id="password" name="password">
    <button type="submit">Login</button>
</form>
```

On the server side, the CSRF token is verified:

```python
def login(request):
    csrf_token = request.POST.get('csrf_token')
    if csrf_token != request.session['csrf_token']:
        return HttpResponseForbidden("Invalid CSRF token")
    # Process login logic
```

### SameSite Cookie Attribute

The `SameSite` attribute is used to control whether a cookie is sent with cross-site requests. By setting `SameSite=Strict`, the cookie is only sent with requests originating from the same site. This prevents CSRF attacks by ensuring that the cookie is not sent in cross-site requests.

#### Example of Setting SameSite Attribute

In an HTTP response, the `Set-Cookie` header can include the `SameSite` attribute:

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; SameSite=Strict; Secure; HttpOnly
Content-Type: text/html
```

### Referer Header Checks

Another approach is to check the `Referer` header to ensure that requests originate from the same origin as the web application. However, this method is less reliable because the `Referer` header can be spoofed or omitted.

#### Example of Referer Header Check

On the server side, the `Referer` header can be checked:

```python
def process_request(request):
    referer = request.headers.get('Referer')
    if not referer or not referer.startswith('https://example.com'):
        return HttpResponseForbidden("Invalid Referer header")
    # Process request logic
```

---
<!-- nav -->
[[03-Lab 5 CSRF Where Token is Tied to Non-Session Cookie|Lab 5 CSRF Where Token is Tied to Non-Session Cookie]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/06-Lab 5 CSRF where token is tied to non session cookie/00-Overview|Overview]] | [[05-CSRF Token Tied to Non-Session Cookie|CSRF Token Tied to Non-Session Cookie]]
