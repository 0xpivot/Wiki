---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Detailed Explanation of CSRF Attack Mechanics

### Understanding the Attack Vector

In the given example, the attacker sends a link to the victim user. When the user clicks the link, the web application processes the request to change the user’s email address. However, the user is unaware of this action because they only see a "hello world" message.

#### Step-by-Step Breakdown

1. **Victim User Session**: The user is logged into the web application.
2. **Malicious Link**: The attacker sends a link to the victim user, which contains a crafted request to change the email address.
3. **User Interaction**: When the user clicks the link, the web application receives the request to change the email address.
4. **Hidden Action**: The user sees only a "hello world" message, unaware that their email address is being changed in the background.

### Crafting the Malicious Request

The attacker crafts a request that, when executed by the victim user, will perform the desired action. This can be done using various methods, such as:

- **HTML Forms**: Embedding a form in a webpage that automatically submits when loaded.
- **JavaScript**: Using JavaScript to submit a request programmatically.
- **Iframes**: Embedding an iframe in a webpage that loads a hidden form.

#### Example Code

Here is an example of a malicious HTML form that changes the user’s email address:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Crafted Request</title>
</head>
<body onload="document.getElementById('csrfForm').submit()">
    <form id="csrfForm" action="https://example.com/change-email" method="POST">
        <input type="hidden" name="email" value="attacker@example.com" />
    </form>
</body>
</html>
```

When the victim user visits this webpage, the form is automatically submitted, changing their email address.

### Detecting CSRF Attacks

Detecting CSRF attacks can be challenging, but there are several indicators to look for:

- **Unexpected Requests**: Unusual requests that do not match the user’s typical behavior.
- **Hidden Actions**: Requests that perform actions without the user’s knowledge or consent.
- **Gateway Timeouts**: Errors indicating that the server did not receive the expected request.

### Real-World Example: Gateway Timeout

In the given example, the web application received a request to change the email address, but it resulted in a gateway timeout. This indicates that the request was not properly validated, leading to an error.

#### Full HTTP Request and Response

Here is an example of the full HTTP request and response:

**Request:**

```http
POST /change-email HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

email=attacker%40example.com
```

**Response:**

```http
HTTP/1.1 504 Gateway Timeout
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 0
Connection: close
```

### How to Prevent / Defend Against CSRF Attacks

To prevent CSRF attacks, web applications should implement robust mechanisms to validate requests. Here are some effective techniques:

#### CSRF Tokens

CSRF tokens are unique identifiers generated for each user session. These tokens are included in forms and requests to ensure that the request is valid and originated from the user.

##### Vulnerable Code

Here is an example of a vulnerable form without CSRF tokens:

```html
<form action="/change-email" method="POST">
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    <button type="submit">Change Email</button>
</form>
```

##### Secure Code

Here is an example of a secure form with CSRF tokens:

```html
<form action="/change-email" method="POST">
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <button type="submit">Change Email</button>
</form>
```

#### SameSite Cookies

SameSite cookies ensure that cookies are only sent in first-party contexts, preventing them from being used in cross-site requests.

##### Vulnerable Configuration

Here is an example of a vulnerable cookie configuration:

```http
Set-Cookie: session_id=abc123; Path=/; HttpOnly
```

##### Secure Configuration

Here is an example of a secure cookie configuration:

```http
Set-Cookie: session_id=abc123; Path=/; HttpOnly; SameSite=Strict
```

#### HTTP Headers

Using HTTP headers like `Content-Type` and `Origin` can help validate requests and prevent CSRF attacks.

##### Vulnerable Request

Here is an example of a vulnerable request:

```http
POST /change-email HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

email=attacker%40example.com
```

##### Secure Request

Here is an example of a secure request:

```http
POST /change-email HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
Content-Type: application/x-www-form-urlencoded
Content-Length: 29
Origin: https://example.com

email=attacker%40example.com
```

### Detection and Monitoring

To detect and monitor CSRF attacks, web applications should implement logging and monitoring mechanisms. This includes:

- **Logging Requests**: Logging all requests to identify unusual patterns.
- **Monitoring Behavior**: Monitoring user behavior to detect unexpected actions.
- **Alerting Mechanisms**: Setting up alerting mechanisms to notify administrators of potential attacks.

### Hands-On Labs

For hands-on practice with CSRF attacks and defenses, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on CSRF attacks and defenses.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning about web application security.

By thoroughly understanding the mechanics of CSRF attacks and implementing robust defense mechanisms, web applications can significantly reduce the risk of these attacks.

### Conclusion

Cross-Site Request Forgery (CSRF) is a serious security threat that can lead to significant data manipulation and account takeover. By understanding the mechanics of CSRF attacks, implementing robust defense mechanisms, and regularly monitoring and logging requests, web applications can effectively mitigate the risk of these attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/03-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/05-Detection and Prevention|Detection and Prevention]]
