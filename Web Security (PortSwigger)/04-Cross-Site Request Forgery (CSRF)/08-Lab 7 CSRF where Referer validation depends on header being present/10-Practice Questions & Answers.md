---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the presence of a referer header can be used as a defense mechanism against CSRF attacks.**

The referer header is an optional HTTP header that indicates the URL of the page that linked to the resource being requested. Some web applications use this header to verify that requests are coming from a trusted source within their domain. By checking the referer header, the application can attempt to prevent cross-domain requests that might be part of a CSRF attack. For example, if a request originates from an external domain, the referer header will indicate this, and the application can reject the request to mitigate potential CSRF exploits.

**Q2. How would you exploit a CSRF vulnerability where the referer validation is implemented insecurely?**

To exploit a CSRF vulnerability where the referer validation is implemented insecurely, you would first identify whether the application checks for the presence of the referer header and performs no further validation if the header is missing. If the application only checks for the existence of the referer header and does not validate its contents, you can craft an exploit that omits the referer header entirely. This can be achieved by using HTML meta tags to instruct the browser not to send the referer header. Here’s an example payload:

```html
<!DOCTYPE html>
<html>
<head>
    <meta name="referrer" content="never">
</head>
<body>
    <form id="csrfForm" action="https://example.com/change-email" method="POST">
        <input type="hidden" name="email" value="attacker@example.com">
    </form>
    <script>
        document.getElementById('csrfForm').submit();
    </script>
</body>
</html>
```

This payload ensures that the referer header is not sent, bypassing the application's referer validation check.

**Q3. Why is relying solely on the referer header for CSRF protection considered insecure?**

Relying solely on the referer header for CSRF protection is considered insecure because the referer header can be easily manipulated or omitted by attackers. Modern browsers provide mechanisms to control the sending of the referer header, such as using HTML meta tags or JavaScript. Additionally, network configurations and proxies can strip the referer header, leading to false negatives. An attacker can exploit these weaknesses by crafting requests that omit or manipulate the referer header, thereby bypassing the application's defenses.

**Q4. How would you configure a web application to properly protect against CSRF attacks, considering the limitations of referer header validation?**

To properly protect against CSRF attacks, a web application should implement a combination of security measures beyond relying solely on the referer header. Key practices include:

1. **CSRF Tokens**: Use unique, unpredictable tokens for each session and validate these tokens on the server side for each request.
2. **SameSite Cookies**: Set the `SameSite` attribute on cookies to restrict their usage to same-site contexts, preventing them from being sent in cross-site requests.
3. **Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded, reducing the risk of XSS and related CSRF attacks.
4. **Double Submit Cookie Pattern**: Use a CSRF token stored in a cookie and also passed as a request parameter, ensuring both match before processing the request.

Here’s an example of setting a CSRF token in a session and validating it:

```python
# Server-side code to generate and validate CSRF token
import secrets

def generate_csrf_token():
    return secrets.token_hex(16)

def validate_csrf_token(request):
    session_token = request.session.get('csrf_token')
    request_token = request.POST.get('csrf_token')
    return session_token == request_token

# Example usage
request.session['csrf_token'] = generate_csrf_token()
if validate_csrf_token(request):
    # Process the request
    pass
else:
    # Handle CSRF validation failure
    pass
```

**Q5. Discuss recent real-world examples where CSRF vulnerabilities were exploited due to improper referer header validation.**

One notable example is the exploitation of a CSRF vulnerability in a web application that relied solely on referer header validation. In a specific incident, attackers crafted a malicious webpage that omitted the referer header, allowing them to bypass the application's defenses. This resulted in unauthorized actions being performed on behalf of users who visited the malicious page. Such incidents highlight the importance of implementing robust CSRF protections beyond simple referer checks.

For instance, a recent breach involved a financial service provider whose web application failed to properly validate CSRF tokens and relied on referer headers. Attackers exploited this by creating a phishing page that tricked users into performing unauthorized transactions. This underscores the necessity of comprehensive security measures to effectively protect against CSRF attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/09-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/08-Lab 7 CSRF where Referer validation depends on header being present/00-Overview|Overview]]
