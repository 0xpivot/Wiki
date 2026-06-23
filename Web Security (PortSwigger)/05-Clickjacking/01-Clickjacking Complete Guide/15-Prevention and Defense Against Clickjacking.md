---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Prevention and Defense Against Clickjacking

### Content Security Policy (CSP)

Content Security Policy (CSP) is a security measure that helps mitigate various types of attacks, including clickjacking. One of the key directives in CSP is the `frame-ancestors` directive, which specifies which origins are allowed to embed a resource within a frame or iframe.

#### Syntax and Usage

The `frame-ancestors` directive is added to the `Content-Security-Policy` header in the HTTP response. Here is an example of how to configure it:

```http
HTTP/1.1 200 OK
Content-Security-Policy: frame-ancestors 'self'
```

In this example, `'self'` means that only the origin itself is allowed to frame the resource. You can also specify specific origins:

```http
HTTP/1.1 200 OK
Content-Security-Policy: frame-ancestors https://trusted-origin.com
```

#### Limitations

While CSP is a powerful tool, it is important to note that the `frame-ancestors` directive is not supported by all browsers. Therefore, it is recommended to use a combination of CSP and other measures to ensure comprehensive protection.

### X-Frame-Options Header

The `X-Frame-Options` header is another mechanism to prevent clickjacking. It specifies whether or not a browser should be allowed to render a page in a frame or iframe. There are three possible values for this header:

- `DENY`: The page cannot be displayed in a frame.
- `SAMEORIGIN`: The page can only be displayed in a frame on the same origin as the page itself.
- `ALLOW-FROM uri`: The page can only be displayed in a frame on the specified origin.

Here is an example of how to configure the `X-Frame-Options` header:

```http
HTTP/1.1 200 OK
X-Frame-Options: DENY
```

### SameSite Cookies

SameSite cookies are a feature that helps prevent cross-site request forgery (CSRF) attacks and can also be used to defend against clickjacking attacks on authenticated pages. The `SameSite` attribute determines when a website's cookies are included in requests originating from other domains.

#### Syntax and Usage

The `SameSite` attribute can take one of three values:

- `Strict`: The cookie will only be sent in a first-party context.
- `Lax`: The cookie will be sent for same-site requests and cross-site top-level navigations.
- `None`: The cookie will be sent for all requests, regardless of the context.

Here is an example of how to configure the `SameSite` attribute:

```http
HTTP/1.1 200 OK
Set-Cookie: sessionid=abc; SameSite=Strict
```

### How to Prevent / Defend

#### Detection

To detect clickjacking vulnerabilities, you can use automated tools like Burp Suite, ZAP (Zed Attack Proxy), or manual testing techniques. These tools can help identify if a website is susceptible to clickjacking by checking for the presence of appropriate security headers.

#### Prevention

1. **Implement CSP with `frame-ancestors`**:
   Ensure that the `frame-ancestors` directive is properly configured to restrict framing to trusted origins.

2. **Use `X-Frame-Options`**:
   Set the `X-Frame-Options` header to either `DENY` or `SAMEORIGIN` to prevent framing by untrusted sites.

3. **Configure SameSite Cookies**:
   Set the `SameSite` attribute to `Strict` or `Lax` to prevent cookies from being sent in cross-site requests.

#### Secure Coding Fixes

Here is an example of how to implement these measures in a web application:

```python
from flask import Flask, make_response

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response("Hello, World!")
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.set_cookie('sessionid', 'abc', samesite='Strict')
    return response

if __name__ == '__main__':
    app.run()
```

### Common Pitfalls

1. **Browser Compatibility**:
   Ensure that the security measures you implement are compatible with all major browsers. Some older browsers may not support certain features.

2. **Configuration Errors**:
   Incorrectly configuring security headers can leave your application vulnerable. Always test your configurations thoroughly.

3. **Third-Party Scripts**:
   Third-party scripts can introduce vulnerabilities. Ensure that any third-party scripts you use are from trusted sources and do not override your security settings.

### Real-World Example: Recent Breach

A recent example of a clickjacking attack occurred in 2021, where a popular social media platform was exploited due to a misconfigured `X-Frame-Options` header. Attackers were able to create a malicious overlay that tricked users into sharing sensitive information. This breach highlights the importance of proper configuration and regular security audits.

### Hands-On Labs

For hands-on practice with clickjacking, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs on clickjacking and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By thoroughly understanding and implementing the preventive measures discussed, you can significantly reduce the risk of clickjacking attacks on your web applications.

---
<!-- nav -->
[[14-Prevention Techniques for Clickjacking|Prevention Techniques for Clickjacking]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[16-Real-World Examples|Real-World Examples]]
