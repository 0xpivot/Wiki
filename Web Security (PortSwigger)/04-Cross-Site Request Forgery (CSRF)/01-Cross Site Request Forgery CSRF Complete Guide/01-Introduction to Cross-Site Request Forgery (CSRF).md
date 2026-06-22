---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack where an attacker tricks a victim into performing unintended actions on a web application in which the victim is currently authenticated. This attack leverages the trust that the web application places in the victim's session to execute unauthorized commands. To understand CSRF thoroughly, it is essential to delve into the underlying mechanisms and the conditions necessary for such an attack to succeed.

### Prerequisites for a CSRF Attack

The primary prerequisite for a CSRF attack to be successful is that the victim must be authenticated with the target web application. This means that the victim has already provided their credentials (username and password) to the application, and the application has set a session cookie in the victim's browser. Every subsequent request made by the victim to the application includes this session cookie, which authenticates the user to the web application.

#### Example: Authentication Mechanism

Consider a banking application (`domainbank.com`). When a user logs in, the server responds with a session cookie:

```http
HTTP/1.1 200 OK
Set-Cookie: sessionid=abc123; Path=/; HttpOnly
```

This `sessionid` cookie is stored in the user's browser. Whenever the user makes a request to `domainbank.com`, the browser automatically includes this cookie in the request:

```http
GET /account HTTP/1.1
Host: domainbank.com
Cookie: sessionid=abc123
```

### The CSRF Attack Scenario

In a CSRF attack, the attacker crafts a malicious link or form that, when triggered by the victim, performs an action on the victim's behalf. The attacker can send this link via email, instant messaging, or embed it in a webpage. When the victim clicks on the link or submits the form, the web application interprets the request as coming from the authenticated user due to the presence of the session cookie.

#### Example: Malicious Link

Suppose the attacker wants to change the victim's email address on `domainbank.com`. The attacker crafts a URL like this:

```
https://domainbank.com/email/change?newEmail=attacker@example.com
```

If the victim clicks on this link, the request will be sent to the server with the session cookie included:

```http
GET /email/change?newEmail=attacker@example.com HTTP/1.1
Host: domainbank.com
Cookie: sessionid=abc123
```

Since the server sees the valid session cookie, it processes the request as if the victim intended to change their email address.

### Real-World Examples of CSRF Attacks

#### Recent Breaches and CVEs

One notable example of a CSRF attack occurred in 2021 when a vulnerability was discovered in the WordPress plugin "WPML Multilingual CMS." The vulnerability allowed attackers to perform unauthorized actions, such as changing user roles, through a CSRF attack. This vulnerability was assigned the CVE identifier CVE-2021-24705.

Another example is the CSRF vulnerability found in the popular social media platform Twitter in 2019 (CVE-2019-16441). This vulnerability allowed attackers to follow or unfollow users without their consent.

### How to Prevent / Defend Against CSRF Attacks

To defend against CSRF attacks, several strategies can be employed:

#### 1. Synchronizer Token Pattern

The synchronizer token pattern involves generating a unique token for each session and including it in both the form and the session. When the form is submitted, the server verifies that the token matches the one stored in the session.

##### Vulnerable Code Example

```html
<form action="https://domainbank.com/email/change" method="POST">
    <input type="hidden" name="newEmail" value="attacker@example.com">
    <button type="submit">Change Email</button>
</form>
```

##### Secure Code Example

```html
<form action="https://domainbank.com/email/change" method="POST">
    <input type="hidden" name="csrfToken" value="unique_token_value">
    <input type="hidden" name="newEmail" value="attacker@example.com">
    <button type="submit">Change Email</button>
</form>
```

Server-side verification:

```python
def handle_email_change(request):
    csrf_token = request.POST.get('csrfToken')
    session_token = request.session.get('csrfToken')
    
    if csrf_token != session_token:
        return HttpResponseForbidden("Invalid CSRF token")
    
    new_email = request.POST.get('newEmail')
    # Proceed with email change logic
```

#### 2. Referer Header Validation

Another approach is to validate the `Referer` header to ensure that the request originates from a trusted source. However, this method is less reliable because some browsers may not send the `Referer` header due to privacy settings.

##### Example

```python
def handle_email_change(request):
    referer = request.META.get('HTTP_REFERER')
    
    if not referer or not referer.startswith('https://domainbank.com'):
        return HttpResponseForbidden("Invalid Referer header")
    
    new_email = request.POST.get('newEmail')
    # Proceed with email change logic
```

#### 3. SameSite Cookie Attribute

Setting the `SameSite` attribute on cookies can help mitigate CSRF attacks. The `SameSite` attribute ensures that the cookie is only sent with requests originating from the same site.

##### Example

```http
Set-Cookie: sessionid=abc123; Path=/; HttpOnly; SameSite=Strict
```

### Common Pitfalls and Detection

#### Pitfall: Inadequate Token Management

One common pitfall is inadequate management of CSRF tokens. Tokens should be unique per session and regenerated frequently to prevent reuse.

#### Detection

To detect potential CSRF vulnerabilities, automated tools like Burp Suite, OWASP ZAP, and CSRFTester can be used. These tools simulate CSRF attacks and check if the application is vulnerable.

### Hands-On Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive module on CSRF attacks and mitigation techniques.
- **OWASP Juice Shop**: A deliberately insecure web application that includes CSRF vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including CSRF, for learning and testing.

### Conclusion

Understanding and defending against CSRF attacks is crucial for maintaining the security of web applications. By implementing robust defenses such as the synchronizer token pattern, validating the `Referer` header, and using the `SameSite` cookie attribute, developers can significantly reduce the risk of CSRF attacks. Regularly testing and auditing applications for CSRF vulnerabilities is also essential to ensure ongoing security.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[02-What is a CSRF Vulnerability|What is a CSRF Vulnerability]]
