---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Detailed Explanation of CSRF Attack with Non-Session Cookie Token

In the previous section, we covered the basics of Cross-Site Request Forgery (CSRF) and how it works. Now, let's delve deeper into a specific scenario where the CSRF token is tied to a non-session cookie. This scenario adds an additional layer of complexity to the attack and defense mechanisms.

### Scenario Overview

In this scenario, the CSRF token is stored in a cookie that is not tied to the user's session. This means that the token is not invalidated when the user logs out or closes their browser. Instead, it remains valid until it expires or is explicitly revoked.

#### Key Concepts

1. **Non-Session Cookie**: A cookie that is not tied to the user's session and remains valid even after the user logs out.
2. **CSRF Token**: A unique token generated for each user session to prevent CSRF attacks.
3. **Cookie Tying**: The process of associating a CSRF token with a non-session cookie to ensure that the token is valid only for the intended user.

### How the Attack Works

Let's break down the steps involved in a CSRF attack where the token is tied to a non-session cookie:

1. **User Authentication**: The user logs into the web application, and the server sets a session cookie and a non-session cookie containing the CSRF token.
2. **Malicious Request**: The attacker crafts a malicious request that includes the session cookie and the non-session cookie containing the CSRF token.
3. **Execution**: The web application processes the request, including both cookies, and performs the action specified in the request.

#### Steps Involved

1. **Session and Non-Session Cookies**: When a user logs into a web application, the server sets two cookies: a session cookie and a non-session cookie containing the CSRF token.
2. **Malicious Link**: The attacker creates a malicious link or script that, when clicked or loaded, sends a request to the web application.
3. **Request Execution**: The web application processes the request, including both cookies, and performs the action specified in the request.

### CSRF Attack Chain with Non-Session Cookie

Let's visualize the attack chain using a mermaid diagram:

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant WebApp
    User->>WebApp: Login (Set Session and Non-Session Cookies)
    WebApp-->>User: Set-Cookie: sessionId=abc123
    WebApp-->>User: Set-Cookie: csrfToken=def456
    Attacker->>User: Click Malicious Link
    User->>WebApp: GET /transfer?amount=1000&to=attacker
    WebApp-->>User: Transfer Successful
```

### Prevention and Defense

To prevent CSRF attacks where the token is tied to a non-session cookie, web applications should implement robust defenses. Here are some key strategies:

1. **CSRF Tokens**: Generate a unique token for each user session and require it in every request. This ensures that even if an attacker crafts a malicious request, it will lack the required token.
2. **SameSite Cookies**: Use the `SameSite` attribute in cookies to restrict them from being sent in cross-site requests.
3. **HTTP Headers**: Implement security headers like `X-Frame-Options`, `Content-Security-Policy`, and `Referrer-Policy`.

#### Secure Coding Practices

Here’s an example of how to implement CSRF tokens securely with a non-session cookie:

**Vulnerable Code:**

```python
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # Perform the transfer
    return "Transfer successful"
```

**Secure Code:**

```python
@app.route('/transfer', methods=['POST'])
def transfer():
    csrf_token = request.form['csrf_token']
    if csrf_token != session['csrf_token']:
        abort(_http.HTTPStatus.FORBIDDEN)
    amount = request.form['amount']
    to_account = request.form['to']
    # Perform the transfer
    return "Transfer successful"
```

### Lab Exercise: PortSwigger Web Security Academy

To practice detecting and preventing CSRF attacks with non-session cookie tokens, you can use the PortSwigger Web Security Academy. This lab provides a realistic environment to test your skills in identifying and mitigating CSRF vulnerabilities.

### Conclusion

CSRF attacks where the token is tied to a non-session cookie are a significant threat to web applications. However, they can be effectively prevented through proper implementation of security measures such as CSRF tokens, SameSite cookies, and security headers. By understanding the mechanics of CSRF and implementing robust defenses, developers can protect their applications from these types of attacks.

---

---
<!-- nav -->
[[09-Detailed Explanation of CSRF Attack with Non-Session Cookie Token (Final Section)|Detailed Explanation of CSRF Attack with Non-Session Cookie Token (Final Section)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/06-Lab 5 CSRF where token is tied to non session cookie/00-Overview|Overview]] | [[11-How to Prevent  Defend Against CSRF|How to Prevent  Defend Against CSRF]]
