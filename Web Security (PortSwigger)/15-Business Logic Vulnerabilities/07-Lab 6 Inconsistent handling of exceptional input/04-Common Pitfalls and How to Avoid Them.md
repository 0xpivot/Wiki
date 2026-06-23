---
course: Web Security
topic: Business Logic Vulnerabilities
tags: [web-security]
---

## Common Pitfalls and How to Avoid Them

### Pitfall: Inadequate Validation

Inadequate validation of user inputs can lead to business logic vulnerabilities. For example, if the application does not validate email addresses properly, it might allow unauthorized access.

#### Secure Coding Fix

Ensure that all user inputs are validated according to business rules. Use regular expressions to validate email addresses and implement proper error handling.

```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# Example usage
email = "attacker@exploitserver.net"
if validate_email(email):
    print("Valid email")
else:
    print("Invalid email")
```

### Pitfall: Missing CSRF Protection

Missing CSRF protection can lead to CSRF attacks. Ensure that all forms include CSRF tokens and that the server properly validates them.

#### Secure Coding Fix

Generate and validate CSRF tokens for all forms.

```python
from flask import Flask, session, request

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        csrf_token = session.get('csrf_token')
        if csrf_token != request.form['csrf_token']:
            return "CSRF token mismatch", 400
        # Proceed with login
    else:
        session['csrf_token'] = generate_csrf_token()
    return render_template('login.html')

def generate_csrf_token():
    import os
    return os.urandom(16).hex()
```

### Pitfall: Inconsistent Error Messages

Inconsistent error messages can leak information to attackers. Ensure that error messages are consistent and do not reveal sensitive information.

#### Secure Coding Fix

Use generic error messages and ensure that they do not reveal sensitive information.

```python
def login(username, password):
    if not validate_credentials(username, password):
        return "Invalid username or password", 401
    # Proceed with login
```

---
<!-- nav -->
[[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/07-Lab 6 Inconsistent handling of exceptional input/03-Business Logic Vulnerabilities|Business Logic Vulnerabilities]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/07-Lab 6 Inconsistent handling of exceptional input/00-Overview|Overview]] | [[Web Security (PortSwigger)/15-Business Logic Vulnerabilities/07-Lab 6 Inconsistent handling of exceptional input/05-Detection and Prevention|Detection and Prevention]]
