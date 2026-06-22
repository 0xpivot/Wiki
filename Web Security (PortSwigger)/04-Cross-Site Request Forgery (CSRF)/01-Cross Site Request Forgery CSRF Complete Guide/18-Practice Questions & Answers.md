---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a CSRF vulnerability is and the conditions necessary for a page to be vulnerable to CSRF.**

A CSRF vulnerability, or Cross-Site Request Forgery, is an attack where an attacker tricks a victim into performing an unintended action while the victim is authenticated to a web application. For a page to be vulnerable to CSRF, the following conditions must be satisfied:

1. **Relevant Action**: The action being performed must have significant consequences for the victim, such as changing an email address or transferring funds.
2. **Cookie-Based Session Handling**: The application must use cookies to manage user sessions.
3. **No Unpredictable Request Parameters**: The request to perform the action should not require any unpredictable parameters, such as a CSRF token.

If any of these conditions are not met, the functionality is not vulnerable to CSRF.

**Q2. How would you exploit a CSRF vulnerability that involves a POST request?**

To exploit a CSRF vulnerability involving a POST request, you would typically create an HTML form with hidden fields that contain the necessary parameters for the action. The form would be designed to be submitted automatically when the victim visits a malicious webpage. Here’s an example:

```html
<html>
<head>
    <script>
        function autoSubmit() {
            document.getElementById('csrfForm').submit();
        }
    </script>
</head>
<body onload="autoSubmit()">
    <form id="csrfForm" action="http://vulnerable-app.com/change-email" method="POST">
        <input type="hidden" name="email" value="attacker@example.com" />
    </form>
</body>
</html>
```

When the victim visits the malicious webpage, the form is automatically submitted, causing the email address to be changed to the attacker’s email address.

**Q3. Why is the use of a referer header considered an inadequate defense against CSRF attacks?**

Using the referer header as a defense against CSRF attacks is considered inadequate because:

1. **Spoofing**: Referer headers can be spoofed under certain conditions, allowing an attacker to forge the origin of the request.
2. **Implementation Flaws**: Many implementations of referer header checks are flawed. For example, if the referer header is absent, some applications may accept the request without further verification. Additionally, substring matching rather than exact matching can lead to bypasses.

For instance, an attacker can craft a URL that includes the target domain as a query parameter, tricking the application into accepting the request:

```
http://malicious-site.com/?http://target-domain.com/
```

Since the application only checks for the presence of the domain in the referer header, it would accept the request, leading to a successful CSRF attack.

**Q4. Describe the steps involved in finding CSRF vulnerabilities from a black box perspective.**

From a black box perspective, the steps to find CSRF vulnerabilities are as follows:

1. **Map the Application**: Identify all key functionalities of the application.
2. **Identify Relevant Actions**: Determine which functionalities have significant consequences for the user.
3. **Check for Cookie-Based Session Handling**: Ensure the application uses cookies for session management.
4. **Look for Predictable Request Parameters**: Check if the actions can be performed with predictable parameters.
5. **Create Proof-of-Concept (PoC)**: Develop a PoC script to demonstrate the vulnerability, such as an HTML form or an image tag that triggers the action.

By following these steps, you can systematically identify and confirm CSRF vulnerabilities in the application.

**Q5. How do CSRF tokens help prevent CSRF attacks?**

CSRF tokens help prevent CSRF attacks by introducing an unpredictable parameter that must be included in the request. Here’s how they work:

1. **Token Generation**: A unique, random CSRF token is generated and associated with the user’s session.
2. **Token Transmission**: The token is included in the form or request as a hidden field or custom header.
3. **Validation**: When the request is received, the application validates that the token matches the one stored in the user’s session.
4. **Session Tying**: The token is tied to the user’s session to prevent an attacker from using their own token.

By requiring a valid CSRF token, the application ensures that the request originates from the legitimate user and not from a malicious source.

**Q6. Explain the difference between the 'strict' and 'lax' configurations of SameSite cookies and their implications for CSRF protection.**

SameSite cookies can be configured with either 'strict' or 'lax' attributes to control how cookies are sent with cross-origin requests:

- **Strict Configuration**: Cookies are only sent with requests originating from the same site. This prevents cookies from being sent with requests initiated by third-party sites, effectively blocking CSRF attacks. However, it can impair user experience in applications that integrate with third-party services.
  
- **Lax Configuration**: Cookies are sent with GET requests that result from top-level navigations (e.g., clicking a link), but not with other types of requests (e.g., POST). This provides a balance between security and usability, as it still blocks many forms of CSRF attacks while allowing some cross-origin interactions.

Both configurations enhance CSRF protection, but 'strict' is more secure while 'lax' offers a better user experience.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/17-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]]
