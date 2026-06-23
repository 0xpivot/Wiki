---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. This attack leverages the trust that a web application places in a user's browser. The attacker crafts a malicious request that appears to come from the victim, thus exploiting the victim's authentication credentials.

### Understanding CSRF

To understand CSRF, let's break down the components involved:

1. **Victim**: The user who is authenticated with the web application.
2. **Attacker**: The malicious actor who wants to exploit the victim's session.
3. **Web Application**: The target application that the attacker wants to manipulate.

#### How CSRF Works

The basic steps of a CSRF attack are as follows:

1. **Authentication**: The victim logs into the web application and receives a session cookie.
2. **Malicious Request**: The attacker crafts a malicious request that performs an action on behalf of the victim.
3. **Execution**: The victim is tricked into executing the malicious request, often through social engineering techniques such as clicking a link or visiting a compromised website.
4. **Action Execution**: The web application processes the request, thinking it came from the victim, and performs the action.

### Example Scenario: Email Change Functionality

Let's consider a specific scenario where the email change functionality is vulnerable to CSRF. The attacker aims to change the victim's email address to one controlled by the attacker, allowing them to reset the victim's password and fully compromise the account.

#### Vulnerable Action: Email Change

The email change functionality is a critical action because it allows the attacker to gain control over the victim's account. Here’s how the attack unfolds:

1. **Initial Setup**:
    - The victim logs into the web application and receives a session cookie.
    - The attacker knows the URL and form data required to change the email address.

2. **Crafting the Malicious Request**:
    - The attacker creates a malicious HTML form that submits the email change request.
    - The form includes the necessary fields to change the email address to one controlled by the attacker.

```html
<form id="csrf-form" action="https://example.com/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@example.com">
</form>
<script>
    document.getElementById('csrf-form').submit();
</script>
```

3. **Tricking the Victim**:
    - The attacker tricks the victim into loading the malicious HTML page, either through a phishing email or a compromised website.
    - When the victim loads the page, the form is automatically submitted, changing their email address to one controlled by the attacker.

4. **Password Reset**:
    - The attacker now controls the email address associated with the victim's account.
    - They can initiate a password reset request, which sends the reset code to the new email address.
    - The attacker retrieves the reset code and changes the password, fully compromising the account.

### Conditions for CSRF Vulnerability

For a web application to be vulnerable to CSRF, several conditions must be met:

1. **Relevant Action**:
    - The action being performed must have a detrimental effect on the victim. Changing the email address is a relevant action because it can lead to account compromise.

2. **Cookie-Based Session Handling**:
    - The application must use cookies for session management. This ensures that the session remains active even when the victim is tricked into executing the malicious request.

3. **No Unpredictable Request Parameters**:
    - The request should not contain any unpredictable parameters, such as a CSRF token. If the request contains a CSRF token, the attacker would need to predict or guess the token value, making the attack more difficult.

### Real-World Examples

Recent real-world examples of CSRF vulnerabilities include:

- **CVE-2021-21972**: A CSRF vulnerability was found in the WordPress REST API, allowing attackers to perform unauthorized actions on behalf of authenticated users.
- **CVE-2020-14182**: A CSRF vulnerability in the Atlassian Jira application allowed attackers to execute arbitrary actions, including modifying user settings.

### Detection and Prevention

#### How to Detect CSRF

Detecting CSRF vulnerabilities involves analyzing the web application for the following characteristics:

1. **Session Management**:
    - Check if the application uses cookies for session management.
    - Ensure that session cookies are marked with the `HttpOnly` flag to prevent access via JavaScript.

2. **Unpredictable Request Parameters**:
    - Look for the presence of CSRF tokens in forms and AJAX requests.
    - Verify that these tokens are unique per session and cannot be easily predicted.

3. **Referer Header Validation**:
    - Some applications rely on the `Referer` header to validate requests. However, this method is not reliable due to the possibility of the header being absent or manipulated.

#### How to Prevent CSRF

Preventing CSRF attacks involves implementing robust security measures:

1. **CSRF Tokens**:
    - Generate a unique CSRF token for each session and include it in forms and AJAX requests.
    - Validate the token on the server-side to ensure that the request originated from a legitimate source.

```python
# Example of generating and validating a CSRF token in Python Flask
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

@app.route('/change-email', methods=['GET', 'POST'])
def change_email():
    if request.method == 'POST':
        email = request.form['email']
        # Perform email change logic here
        return redirect(url_for('success'))
    return '''
        <form method="post">
            <input type="email" name="email">
            <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
            <input type="submit" value="Change Email">
        </form>
    '''

@app.route('/success')
def success():
    return 'Email successfully changed!'
```

2. **SameSite Cookie Attribute**:
    - Set the `SameSite` attribute on session cookies to `Strict` or `Lax` to prevent cross-site requests from sending the cookie.

```http
Set-Cookie: session=abc123; SameSite=Strict; Secure
```

3. **Content Security Policy (CSP)**:
    - Implement a Content Security Policy to restrict the sources of scripts and other resources that can be loaded in the browser.

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com
```

### Common Pitfalls

When implementing CSRF protection, common pitfalls include:

1. **Inconsistent Token Usage**:
    - Ensure that CSRF tokens are used consistently across all forms and AJAX requests.
    - Missing tokens in certain parts of the application can create vulnerabilities.

2. **Token Predictability**:
    - Use strong randomization techniques to generate CSRF tokens.
    - Avoid using predictable values such as timestamps or simple counters.

3. **Referer Header Reliance**:
    - Relying solely on the `Referer` header for CSRF protection is unreliable.
    - Modern browsers may strip the `Referer` header in certain scenarios, leading to false negatives.

### Conclusion

Cross-Site Request Forgery (CSRF) is a serious threat to web applications, especially when sensitive actions can be performed without additional verification. By understanding the conditions that make an application vulnerable to CSRF and implementing robust prevention measures, developers can significantly reduce the risk of such attacks.

### Practice Labs

For hands-on practice with CSRF vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on various web security topics, including CSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

These labs provide real-world scenarios and challenges to help you master the detection and prevention of CSRF attacks.

---
<!-- nav -->
[[02-Lab 8 CSRF with Broken Referer Validation|Lab 8 CSRF with Broken Referer Validation]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/00-Overview|Overview]] | [[04-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]]
