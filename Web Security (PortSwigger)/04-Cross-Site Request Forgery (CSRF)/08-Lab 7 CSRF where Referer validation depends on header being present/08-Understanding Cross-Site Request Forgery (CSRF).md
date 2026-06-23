---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Understanding Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. This can occur when an attacker crafts a malicious request that, when executed by the victim, performs actions such as changing account settings, transferring funds, or posting unauthorized content.

### What is a Referer Header?

A `Referer` header is an optional HTTP request header that contains the URL of the page that initiated the request. This header helps the server understand the context of the request, specifically where it originated from. The `Referer` header is often used by web servers to track navigation paths and for various security checks.

#### Syntax and Example Values

The `Referer` header follows this format:

```http
Referer: <URL>
```

For example:

```http
Referer: https://example.com/page.html
```

#### Security Impact

The `Referer` header can be used both positively and negatively from a security perspective. On one hand, it can help in identifying the origin of requests, which can be useful for detecting and preventing certain types of attacks. On the other hand, it can also leak sensitive information if not handled properly.

### How CSRF Attacks Work

In a typical CSRF attack, an attacker crafts a malicious request that, when executed by the victim, performs an action on behalf of the victim. This can happen through various methods, such as embedding a malicious image or script in a web page that the victim visits.

#### Example Scenario

Consider a scenario where a user is logged into a banking application. An attacker crafts a malicious HTML form that, when submitted, transfers money from the user's account to the attacker's account. If the user clicks on a link or visits a page containing this form, the form submission will be executed automatically due to the user's authenticated session.

### Referer Header Validation

One method to mitigate CSRF attacks is to validate the `Referer` header. By ensuring that the request originates from the same domain as the web application, the server can reduce the risk of unauthorized requests.

#### Mechanism

When a request is made to a web application, the server checks the `Referer` header to determine the origin of the request. If the `Referer` header matches the domain of the application, the request is considered valid. Otherwise, it is rejected.

#### Example Code

Here is an example of how a server might check the `Referer` header:

```python
def handle_request(request):
    referer = request.headers.get('Referer')
    if referer and referer.startswith('https://example.com'):
        # Process the request
        pass
    else:
        return "Invalid referrer header"
```

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example of a CSRF vulnerability in the WordPress REST API. In this case, an attacker could craft a malicious request that, when executed by a logged-in user, would modify the user's profile settings.

#### Exploit Details

The exploit involved crafting a POST request to the `/wp-json/wp/v2/users/<user_id>` endpoint, which would update the user's profile information. The attacker could embed this request in a malicious web page, and when the victim visited the page, their browser would automatically submit the request.

#### HTTP Request and Response

Here is an example of the HTTP request and response:

```http
POST /wp-json/wp/v2/users/1 HTTP/1.1
Host: example.com
Content-Type: application/json
Referer: http://malicious-site.com

{
  "name": "Attacker",
  "email": "attacker@example.com"
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "name": "Attacker",
  "email": "attacker@example.com"
}
```

### Lab Scenario: CSRF with Referer Validation

In the given lab scenario, the attacker sends a phishing link to the user, which should change the user's email address. However, the request fails because the `Referer` header does not match the expected domain.

#### Analysis

Let's analyze the steps involved in this scenario:

1. **Phishing Link**: The attacker sends a phishing link to the user.
2. **Request Execution**: When the user clicks the link, a request is sent to the server.
3. **Referer Header Check**: The server checks the `Referer` header to ensure it matches the expected domain.
4. **Validation Failure**: Since the `Referer` header does not match, the request is rejected.

#### HTTP Request and Response

Here is an example of the HTTP request and response:

```http
GET /change-email HTTP/1.1
Host: random-number.wap-security-academy.net
Referer: http://burpsuite.com

HTTP/1.1 400 Bad Request
Content-Type: text/html

Invalid referrer header
```

### Using Burp Suite for Analysis

Burp Suite is a powerful tool for analyzing and testing web applications. In this scenario, we can use Burp Suite to intercept and analyze the requests.

#### Steps

1. **Intercept Request**: Use Burp Suite to intercept the request sent by the phishing link.
2. **Modify Referer Header**: Modify the `Referer` header to match the expected domain.
3. **Send Modified Request**: Send the modified request to the server.

#### Example with Burp Suite

1. **Intercept Request**:

```http
GET /change-email HTTP/1.1
Host: random-number.wap-security-academy.net
Referer: http://burpsuite.com
```

2. **Modify Referer Header**:

```http
GET /change-email HTTP/1.1
Host: random-number.wap-security-academy.net
Referer: https://random-number.wap-security-academy.net
```

3. **Send Modified Request**:

```http
HTTP/1.1 200 OK
Content-Type: text/html

Email changed successfully
```

### How to Prevent / Defend Against CSRF

To effectively prevent CSRF attacks, several measures can be taken:

#### 1. Use Anti-CSRF Tokens

Anti-CSRF tokens are unique, unpredictable values that are generated for each user session and included in forms and AJAX requests. These tokens are validated on the server-side to ensure that the request originated from the legitimate user.

##### Example Code

```html
<form action="/change-email" method="POST">
  <input type="hidden" name="csrf_token" value="unique_token_value">
  <!-- Other form fields -->
</form>
```

Server-side validation:

```python
def handle_request(request):
    csrf_token = request.POST.get('csrf_token')
    if csrf_token == request.session['csrf_token']:
        # Process the request
        pass
    else:
        return "Invalid CSRF token"
```

#### 2. Validate Referer Header

While validating the `Referer` header can provide some level of protection, it is not foolproof. Some browsers allow users to disable the `Referer` header, and attackers can sometimes manipulate it.

##### Example Code

```python
def handle_request(request):
    referer = request.headers.get('Referer')
    if referer and referer.startswith('https://example.com'):
        # Process the request
        pass
    else:
        return "Invalid referrer header"
```

#### 3. Use SameSite Cookies

SameSite cookies are a feature that restricts cookies to first-party contexts. This prevents the browser from sending cookies along with cross-site requests, reducing the risk of CSRF attacks.

##### Example Configuration

```nginx
server {
  listen 80;
  server_name example.com;

  location / {
    add_header Set-Cookie "session=abc123; SameSite=Strict";
  }
}
```

#### 4. Implement Content Security Policy (CSP)

Content Security Policy (CSP) is a security measure that helps prevent cross-site scripting (XSS) and data injection attacks. By specifying allowed sources of content, CSP can help mitigate the risk of CSRF attacks.

##### Example Configuration

```nginx
server {
  listen 80;
  server_name example.com;

  location / {
    add_header Content-Security-Policy "default-src 'self'";
  }
}
```

### Conclusion

Cross-Site Request Forgery (CSRF) is a significant security threat that can lead to unauthorized actions being performed on behalf of authenticated users. By understanding the mechanisms behind CSRF attacks and implementing robust defenses, such as anti-CSRF tokens, referer header validation, SameSite cookies, and Content Security Policy, web applications can significantly reduce the risk of these attacks.

### Practice Labs

For hands-on practice with CSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating CSRF vulnerabilities.

---
<!-- nav -->
[[07-Lab Setup and Initial Exploration|Lab Setup and Initial Exploration]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/09-Conclusion|Conclusion]]
