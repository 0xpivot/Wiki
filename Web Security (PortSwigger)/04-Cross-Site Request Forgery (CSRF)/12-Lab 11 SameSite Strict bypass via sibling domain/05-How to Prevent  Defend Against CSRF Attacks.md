---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## How to Prevent / Defend Against CSRF Attacks

### Detection

To detect CSRF attacks, implement logging and monitoring mechanisms to track unusual activity. Look for patterns such as unexpected requests from unfamiliar sources or repeated attempts to access sensitive endpoints.

### Prevention

#### 1. Use the SameSite Attribute

Ensure that cookies are marked with the `SameSite` attribute to prevent them from being sent with cross-site requests. Set the attribute to `Strict` or `Lax` depending on the application's requirements.

```http
Set-Cookie: sessionid=abc123; SameSite=Strict; Secure
```

#### 2. Implement Anti-CSRF Tokens

Use anti-CSRF tokens to verify that a request originated from a trusted source. Generate a unique token for each user session and include it in both the form and the server-side validation.

```html
<form action="/submit" method="post">
    <input type="hidden" name="csrf_token" value="unique_token">
    <!-- Other form fields -->
</form>
```

On the server side, validate the token before processing the request.

```python
def submit_form(request):
    if request.POST['csrf_token'] != request.session['csrf_token']:
        return HttpResponseForbidden("Invalid CSRF token")
    # Process the form
```

#### 3. Use Content Security Policy (CSP)

Implement a Content Security Policy (CSP) to restrict the sources from which scripts can be loaded. This helps prevent malicious scripts from being executed.

```http
Content-Security-Policy: script-src 'self'
```

### Secure Coding Fixes

#### Vulnerable Code

```javascript
var ws = new WebSocket('wss://example.com/shot');
ws.onopen = function() {
    ws.send('ready');
};
ws.onmessage = function(event) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://example.com/action', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({data: event.data}));
};
```

#### Secure Code

```javascript
var ws = new WebSocket('wss://example.com/shot');
ws.onopen = function() {
    ws.send('ready');
};
ws.onmessage = function(event) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://example.com/action', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRF-Token', 'unique_token');
    xhr.send(JSON.stringify({data: event.data}));
};
```

### Configuration Hardening

#### Nginx Configuration

Ensure that Nginx is configured to enforce the SameSite attribute and Content Security Policy.

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    location / {
        add_header Set-Cookie "sessionid=abc123; SameSite=Strict; Secure";
        add_header Content-Security-Policy "script-src 'self'";
    }
}
```

#### Apache Configuration

Similarly, configure Apache to enforce the SameSite attribute and Content Security Policy.

```apache
<VirtualHost *:443>
    ServerName example.com
    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/example.crt
    SSLCertificateKeyFile /etc/apache2/ssl/example.key

    Header always set Set-Cookie "sessionid=abc123; SameSite=Strict; Secure"
    Header always set Content-Security-Policy "script-src 'self'"
</VirtualHost>
```

### Mitigations

- **Regular Audits**: Conduct regular security audits to identify and address potential vulnerabilities.
- **User Education**: Educate users about the risks of clicking on suspicious links or downloading unknown files.
- **Update Dependencies**: Keep all dependencies up to date to ensure that known vulnerabilities are patched.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/04-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/12-Lab 11 SameSite Strict bypass via sibling domain/00-Overview|Overview]] | [[06-Lab Setup SameSite Strict Bypass via Sibling Domain|Lab Setup SameSite Strict Bypass via Sibling Domain]]
