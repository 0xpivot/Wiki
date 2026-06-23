---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Real-World Examples of CSRF Attacks

### Recent CVEs and Breaches

#### CVE-2021-3387: Microsoft Exchange Server

In 2021, a series of vulnerabilities were discovered in Microsoft Exchange Server, including a CSRF vulnerability. Attackers could trick users into performing actions like enabling remote access to the server. This allowed further exploitation and data exfiltration.

#### CVE-2022-22963: WordPress REST API

WordPress suffered from a CSRF vulnerability in its REST API. Attackers could craft requests to modify posts or delete content, leveraging the authenticated session of the victim.

### Detailed Example: Transfer Funds

Let's consider a detailed example of a CSRF attack involving a fund transfer on a banking website.

#### Vulnerable Code

```python
@app.route('/transfer', methods=['POST'])
def transfer_funds():
    amount = request.form['amount']
    recipient = request.form['recipient']
    # Perform transfer logic
    return "Transfer successful"
```

#### Attacker's Malicious Page

The attacker creates a malicious page with a hidden form:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Malicious Page</title>
</head>
<body>
    <form action="https://domainbank.com/transfer" method="POST">
        <input type="hidden" name="amount" value="1000">
        <input type="hidden" name="recipient" value="attacker_account">
    </form>
    <script>
        document.forms[0].submit();
    </script>
</body>
</html>
```

When the victim visits this page, their browser submits the form, potentially transferring funds to the attacker's account.

### Detection and Prevention

To detect and prevent CSRF attacks, several strategies can be employed:

1. **CSRF Tokens**: Include a unique, unpredictable token in each request.
2. **SameSite Cookies**: Configure cookies to be sent only for same-site requests.
3. **HTTP Headers**: Use headers like `X-Requested-With` to verify the origin of the request.

### Secure Coding Practices

#### Using CSRF Tokens

To mitigate CSRF, web applications should include a CSRF token in each request. This token is generated server-side and stored in the user's session. The token is then included in forms and verified on the server.

#### Example: Secure Transfer Funds

```python
from flask import Flask, request, session, redirect, url_for

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

@app.route('/transfer', methods=['GET', 'POST'])
def transfer_funds():
    if request.method == 'POST':
        amount = request.form['amount']
        recipient = request.form['recipient']
        # Perform transfer logic
        return "Transfer successful"
    else:
        return '''
            <form action="/transfer" method="POST">
                Amount: <input type="text" name="amount"><br>
                Recipient: <input type="text" name="recipient"><br>
                <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
                <input type="submit" value="Transfer">
            </form>
        '''

if __name__ == '__main__':
    app.run(debug=True)
```

### SameSite Cookies

Configure cookies to be sent only for same-site requests. This prevents the browser from sending cookies to external sites, reducing the risk of CSRF.

#### Example: Setting SameSite Attribute

```python
@app.after_request
def apply_caching(response):
    response.set_cookie('session_id', session['session_id'], samesite='Strict')
    return response
```

### HTTP Headers

Use headers like `X-Requested-With` to verify the origin of the request. This can help detect and prevent CSRF attacks.

#### Example: Verifying Origin

```python
@app.before_request
def verify_origin():
    if request.method == "POST":
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            abort(403)
```

### Hands-On Labs

To practice and understand CSRF attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on CSRF.
- **OWASP Juice Shop**: Provides a vulnerable web application for testing and learning.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security.

By thoroughly understanding and implementing these defenses, you can significantly reduce the risk of CSRF attacks on your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/11-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[13-Session Handling and Management|Session Handling and Management]]
