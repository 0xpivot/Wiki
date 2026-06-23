---
course: API Security
topic: Transport Layer Security Issues
tags: [api-security]
---

## Basic Authorization Over HTTP

### What is Basic Authorization?

Basic authorization is an HTTP authentication mechanism where the client sends credentials in the form of a username and password, encoded using Base64. This method is specified in RFC 7617 and is widely used for simple authentication scenarios.

#### How Does Basic Authorization Work?

When a client wants to access a resource that requires authentication, the server responds with a `401 Unauthorized` status code and includes a `WWW-Authenticate` header. The client then sends the credentials in the `Authorization` header, prefixed with `Basic`.

```http
GET /protected-resource HTTP/1.1
Host: example.com
```

The server responds with:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Basic realm="Secure Area"
```

The client then sends the credentials:

```http
GET /protected-resource HTTP/1.1
Host: example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

Here, `dXNlcm5hbWU6cGFzc3dvcmQ=` is the Base64 encoding of `username:password`.

#### Why Is Basic Authorization Over HTTP Insecure?

Basic authorization over HTTP is insecure because the credentials are transmitted in plain text. Any attacker who intercepts the communication can easily decode the credentials and gain unauthorized access.

### Real-World Example

A real-world example of this vulnerability can be found in the CVE-2019-11510, where a misconfigured web application allowed basic authentication over HTTP, exposing user credentials to potential interception.

### How to Prevent / Defend

#### Detection

To detect basic authorization over HTTP, you can use tools like Burp Suite or Wireshark to inspect HTTP traffic and look for `Authorization: Basic` headers.

#### Prevention

1. **Use HTTPS**: Ensure that all communication is encrypted using HTTPS. This prevents eavesdroppers from intercepting the credentials.
   
2. **Secure Coding Practices**: Avoid using basic authorization over HTTP in your applications. Instead, use more secure methods such as OAuth or JWT.

3. **Configuration Hardening**: Ensure that your web server configurations enforce HTTPS for all endpoints that require authentication.

### Secure Code Fix

#### Vulnerable Code

```python
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/protected')
def protected():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return make_response('Could not verify your access.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return "You are authenticated!"

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

if __name__ == '__main__':
    app.run()
```

#### Fixed Code

Ensure that the application runs over HTTPS:

```python
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/protected')
def protected():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return make_response('Could not verify your access.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return "You are authenticated!"

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # Use adhoc for testing, replace with actual certificates in production
```

---
<!-- nav -->
[[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/01-Introduction to Transport Layer Security (TLS)|Introduction to Transport Layer Security (TLS)]] | [[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/00-Overview|Overview]] | [[API Security/20-Transport Layer Security Issues/02-Basic of Transport Layer Security/03-Clear Text Password Submission|Clear Text Password Submission]]
