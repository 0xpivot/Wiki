---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the double-submit cookie technique and its limitations in preventing CSRF attacks.**

The double-submit cookie technique involves sending a CSRF token both as a cookie and as a request parameter. When a request is made, the server checks if the token in the cookie matches the token in the request parameter. If they match, the request is considered legitimate; otherwise, it is rejected.

However, this technique has limitations:
1. **Cookie Injection Vulnerability**: If the application allows for HTTP header injection, an attacker can inject a custom CSRF cookie into the user’s session. This allows the attacker to set the CSRF token to a known value, enabling a CSRF attack.
2. **Stateful Applications**: The double-submit cookie technique is designed for stateless applications, such as those using JWT tokens. In stateful applications where sessions are managed via cookies, the CSRF token must be stored on the server side, making it harder to ensure the token's uniqueness and security.

**Q2. How would you exploit a CSRF vulnerability where the token is duplicated in the cookie?**

To exploit a CSRF vulnerability where the token is duplicated in the cookie, follow these steps:

1. **Identify the Vulnerable Parameter**: Identify the parameter that is vulnerable to CSRF, such as the email change functionality.
2. **Inject the CSRF Token**: Use HTTP header injection to inject a custom CSRF token into the user’s session. For example, if the application allows for dynamic generation of HTTP headers, you can inject a `Set-Cookie` header to set the CSRF token to a known value.
3. **Craft the Exploit Page**: Create an HTML page that includes a form with the necessary parameters, including the CSRF token set to the same value as the injected cookie. Additionally, include an image tag or an iframe to trigger the CSRF attack without alerting the user.

Here’s an example payload:

```html
<html>
<body>
<h1>Hello World</h1>
<form action="https://example.com/my-account/change-email" method="POST">
<input type="hidden" name="email" value="attacker@example.com">
<input type="hidden" name="csrf" value="known-value">
</form>
<img src="https://example.com/search?term=%0D%0ASet-Cookie:%20csrf=known-value" onerror="document.forms[0].submit()">
</body>
</html>
```

4. **Host and Deliver the Exploit**: Host the exploit page on a server and deliver it to the victim. When the victim visits the page, the CSRF attack will be triggered, changing their email address.

**Q3. Why is the double-submit cookie technique considered insecure in stateful applications?**

The double-submit cookie technique is considered insecure in stateful applications due to the following reasons:

1. **Session Management**: Stateful applications typically manage sessions using cookies stored on the server side. This means that the CSRF token must also be stored on the server side to ensure its uniqueness and security.
2. **HTTP Header Injection**: If the application allows for HTTP header injection, an attacker can inject a custom CSRF cookie into the user’s session, setting the CSRF token to a known value. This bypasses the protection offered by the double-submit cookie technique.
3. **Token Storage**: In stateful applications, the CSRF token must be stored securely on the server side. If the token is not stored securely, an attacker can potentially retrieve the token and use it to perform a CSRF attack.

**Q4. How would you configure a stateful application to mitigate CSRF vulnerabilities effectively?**

To mitigate CSRF vulnerabilities effectively in a stateful application, consider the following configurations:

1. **Use Secure Cookies**: Ensure that cookies are marked as `HttpOnly` and `Secure` to prevent JavaScript access and ensure transmission over HTTPS.
2. **CSRF Tokens**: Generate unique, unpredictable CSRF tokens for each session and store them securely on the server side.
3. **Validate Tokens**: Validate the CSRF token on the server side for every request that modifies state. Ensure that the token in the request matches the token stored in the session.
4. **SameSite Attribute**: Set the `SameSite` attribute for cookies to `Strict` or `Lax` to prevent the browser from sending cookies with cross-site requests.
5. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded, reducing the risk of XSS attacks that can lead to CSRF.

Example configuration:

```python
# Flask example
from flask import Flask, session, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = some_random_string()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token
```

By implementing these measures, you can significantly reduce the risk of CSRF attacks in stateful applications.

**Q5. What recent real-world examples demonstrate the risks of CSRF vulnerabilities?**

Recent real-world examples that demonstrate the risks of CSRF vulnerabilities include:

1. **CVE-2021-21972**: A CSRF vulnerability was discovered in the WordPress REST API, allowing attackers to perform unauthorized actions on behalf of authenticated users. This vulnerability could be exploited to change user settings or even delete posts.
2. **CVE-2021-39148**: A CSRF vulnerability was found in the Atlassian Jira application, allowing attackers to perform actions such as creating issues or modifying project settings on behalf of authenticated users.

These examples highlight the importance of implementing robust CSRF protections in web applications to prevent unauthorized actions and protect user data.

---
<!-- nav -->
[[08-Understanding CSRF Tokens|Understanding CSRF Tokens]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/07-Lab 6 CSRF where token is duplicated in cookie/00-Overview|Overview]]
