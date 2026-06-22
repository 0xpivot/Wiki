---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Clear Text Password Submission

### What is Clear Text Password Submission?

Clear text password submission refers to the practice of transmitting passwords in plain text over the network. This can occur in various contexts, including API calls, login forms, and other authentication mechanisms.

#### How Does Clear Text Password Submission Occur?

When a user submits a password through a form or an API call, the password is sent in plain text if the connection is not encrypted. This makes it susceptible to interception by attackers.

### Real-World Example

In the Hunter 2.0 platform, a vulnerability was identified where passwords were submitted in plain text over HTTP. This allowed attackers to intercept and steal user credentials.

### How to Prevent / Defend

#### Detection

To detect clear text password submission, you can use network monitoring tools like Wireshark to inspect traffic and look for unencrypted passwords.

#### Prevention

1. **Use HTTPS**: Ensure that all connections are encrypted using HTTPS. This prevents eavesdroppers from intercepting the passwords.
   
2. **Secure Coding Practices**: Avoid transmitting passwords in plain text. Use secure methods such as hashing and salting passwords on the server side.

3. **Configuration Hardening**: Ensure that your web server configurations enforce HTTPS for all endpoints that handle sensitive data.

### Secure Code Fix

#### Vulnerable Code

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_credentials(username, password):
        return jsonify({"message": "Logged in successfully"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

def check_credentials(username, password):
    # Dummy check
    return username == 'admin' and password == 'secret'

if __name__ == '__main__':
    app.run()
```

#### Fixed Code

Ensure that the application runs over HTTPS:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if check_credentials(username, password):
        return jsonify({"message": "Logged in successfully"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

def check_credentials(username, password):
    # Dummy check
    return username == 'admin' and password == 'secret'

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Use adhoc for testing, replace with actual certificates in production
```

---
<!-- nav -->
[[02-Basic Authorization Over HTTP|Basic Authorization Over HTTP]] | [[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/00-Overview|Overview]] | [[04-Missing HSTS|Missing HSTS]]
