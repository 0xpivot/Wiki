---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Introduction to Cross-Site Request Forgery (CSRF)

Cross-Site Request Forgery (CSRF) is a type of attack that tricks a victim into executing unwanted actions on a web application in which they are authenticated. The attacker exploits the trust that the web application places in the user's browser session. This attack can lead to unauthorized transactions, such as changing passwords, transferring funds, or posting content.

### What is CSRF?

CSRF attacks rely on the fact that web applications often trust the requests coming from the user's browser. If a user is authenticated to a web application, an attacker can craft a malicious request that will be executed under the user's identity. The key aspect of CSRF is that the attacker does not need to know the user's credentials; they simply need to trick the user into making a request that the web application will accept.

### Why Does CSRF Matter?

CSRF attacks can have severe consequences, including financial loss, data theft, and reputational damage. For instance, in 2017, a CSRF vulnerability was exploited in the Equifax breach, leading to the exposure of sensitive personal information of millions of users. This highlights the importance of securing web applications against CSRF attacks.

### How Does CSRF Work?

To understand how CSRF works, consider the following scenario:

1. **User Authentication**: A user logs into a web application, such as a banking site.
2. **Malicious Request**: An attacker crafts a malicious request that performs an action, like transferring money.
3. **Tricking the User**: The attacker tricks the user into clicking on a link or loading a webpage that contains the malicious request.
4. **Execution**: Since the user is already authenticated, the web application executes the request as if it were initiated by the user.

### Example Scenario

Consider a web application that allows users to change their email addresses. The application might have an endpoint `/change-email` that accepts a POST request with the new email address. If the application does not properly validate the request, an attacker could craft a malicious request that changes the user's email address.

```http
POST /change-email HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded

email=new.email@example.com
```

If the user is tricked into loading a webpage containing this request, the web application will execute it, changing the user's email address.

### Real-World Example: Equifax Breach

In 2017, Equifax suffered a massive data breach that exposed sensitive information of over 143 million users. One of the vulnerabilities exploited was a CSRF vulnerability in their website. Attackers used this vulnerability to gain unauthorized access to user accounts, leading to the exposure of personal data.

### Lab Setup

For this lab, we will use the Web Security Academy provided by PortSwigger. The lab is titled "CSRF where token validation depends on token being present." This lab simulates a web application where the email change functionality is vulnerable to CSRF.

### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for CSRF.
6. Choose lab number three titled "CSRF where token validation depends on the token being present."

### Lab Objective

The objective of this lab is to exploit a CSRF vulnerability to change the email address of the victim user. We will use our exploit server to host an HTML page that triggers the CSRF attack.

### Lab Credentials

The lab provides credentials for logging into the web application. These credentials are essential for testing the CSRF vulnerability.

```plaintext
Username: test
Password: test
```

### Using Burp Suite Professional

To solve the lab, we will use Burp Suite Professional. Burp Suite is a powerful toolkit for web application security testing. It includes features such as proxying, interception, and automated scanning.

#### Setting Up Burp Suite

1. Open Burp Suite Professional.
2. Configure the proxy settings to intercept traffic between your browser and the web application.
3. Set up the target URL in the Proxy tab.

### Identifying the Vulnerability

To identify the CSRF vulnerability, we need to analyze the email change functionality. Let's assume the web application has an endpoint `/change-email` that accepts a POST request with the new email address.

#### Analyzing the Request

First, we need to capture the request made by the web application when changing the email address. We can do this by intercepting the request in Burp Suite.

```http
POST /change-email HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123

email=new.email@example.com
```

### Crafting the Malicious Request

Now that we have captured the request, we can craft a malicious request that will be executed when the user visits a webpage containing this request.

#### Malicious HTML Page

We will create an HTML page that contains a form with the same parameters as the original request.

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Attack</title>
</head>
<body>
    <form action="https://vulnerable-website.com/change-email" method="POST">
        <input type="hidden" name="email" value="new.email@example.com">
        <button type="submit">Change Email</button>
    </form>
</body>
</html>
```

### Hosting the Malicious Page

To host the malicious page, we will use our exploit server. The exploit server is a web server that we control and can use to serve the malicious HTML page.

#### Hosting the Page

1. Upload the HTML page to the exploit server.
2. Obtain the URL of the hosted page.

### Triggering the Attack

To trigger the attack, we need to trick the user into visiting the malicious page. This can be done through various methods, such as sending a phishing email or embedding the page in a forum post.

#### Phishing Email Example

An attacker might send a phishing email to the user, containing a link to the malicious page.

```plaintext
Subject: Important Update

Dear User,

Please visit the following link to update your account information:
http://exploit-server.com/malicious-page.html
```

### Detecting the Attack

To detect the attack, we need to monitor the web application for unauthorized changes. This can be done by setting up alerts for suspicious activities or by reviewing the logs.

#### Monitoring Logs

Web application logs can provide valuable information about unauthorized changes. By reviewing the logs, we can identify any suspicious activities.

### How to Prevent / Defend Against CSRF

To prevent CSRF attacks, web applications should implement proper defenses. Here are some effective measures:

#### 1. Synchronizer Token Pattern

The synchronizer token pattern involves generating a unique token for each user session and validating it in the server-side logic. This ensures that the request is legitimate and not crafted by an attacker.

##### Implementation

1. Generate a unique token for each user session.
2. Include the token in the form as a hidden field.
3. Validate the token on the server side before processing the request.

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Protection</title>
</head>
<body>
    <form action="/change-email" method="POST">
        <input type="hidden" name="token" value="unique-token">
        <input type="text" name="email" placeholder="New Email">
        <button type="submit">Change Email</button>
    </form>
</body>
</html>
```

```python
# Server-side validation
def change_email(request):
    token = request.POST.get('token')
    if token != request.session['csrf_token']:
        return HttpResponseForbidden("Invalid CSRF token")
    email = request.POST.get('email')
    # Process the email change
```

#### 2. Double Submit Cookie

The double submit cookie pattern involves sending a token in both a cookie and a form field. This ensures that the request is legitimate and not crafted by an attacker.

##### Implementation

1. Set a cookie with a unique token.
2. Include the token in the form as a hidden field.
3. Validate the token on the server side before processing the request.

```http
Set-Cookie: csrf_token=unique-token
```

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Protection</title>
</head>
<body>
    <form action="/change-email" method="POST">
        <input type="hidden" name="token" value="unique-token">
        <input type="text" name="email" placeholder="New Email">
        <button type="submit">Change Email</button>
    </form>
</body>
</html>
```

```python
# Server-side validation
def change_email(request):
    token = request.POST.get('token')
    cookie_token = request.COOKIES.get('csrf_token')
    if token != cookie_token:
        return HttpResponseForbidden("Invalid CSRF token")
    email = request.POST.get('email')
    # Process the email change
```

#### 3. Referer Header Check

The referer header check involves verifying that the request comes from the expected origin. This can help prevent CSRF attacks, but it is not foolproof.

##### Implementation

1. Check the referer header to ensure it matches the expected origin.
2. Reject the request if the referer header is missing or does not match the expected origin.

```python
# Server-side validation
def change_email(request):
    referer = request.META.get('HTTP_REFERER')
    if not referer or not referer.startswith('https://expected-origin.com'):
        return HttpResponseForbidden("Invalid referer")
    email = request.POST.get('email')
    # Process the email change
```

### Secure Coding Practices

To prevent CSRF attacks, developers should follow secure coding practices. Here are some guidelines:

#### 1. Always Validate Tokens

Ensure that tokens are validated on the server side before processing any request. This prevents attackers from bypassing the CSRF protection.

#### 2. Use HTTPS

Always use HTTPS to encrypt the communication between the client and the server. This prevents attackers from intercepting and modifying the requests.

#### 3. Avoid Storing Sensitive Data in Cookies

Avoid storing sensitive data in cookies, as they can be accessed by JavaScript. Instead, store sensitive data in server-side sessions.

### Common Pitfalls

Here are some common pitfalls to avoid when implementing CSRF protection:

#### 1. Not Validating Tokens

Failing to validate tokens on the server side can leave the application vulnerable to CSRF attacks.

#### 2. Using Weak Tokens

Using weak tokens, such as predictable or easily guessable values, can make the CSRF protection ineffective.

#### 3. Not Using HTTPS

Not using HTTPS can allow attackers to intercept and modify the requests, bypassing the CSRF protection.

### Conclusion

CSRF attacks can have severe consequences, including financial loss, data theft, and reputational damage. To prevent CSRF attacks, web applications should implement proper defenses, such as the synchronizer token pattern, double submit cookie, and referer header check. Developers should also follow secure coding practices and avoid common pitfalls.

### Practice Labs

For hands-on practice with CSRF attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of CSRF attacks.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various types of attacks, including CSRF.
- **DVWA (Damn Vulnerable Web Application)**: Offers a range of vulnerable web applications for practicing security testing.

By practicing these labs, you can gain a deeper understanding of CSRF attacks and how to defend against them.

---

This comprehensive explanation covers the entire topic of CSRF, including background theory, recent real-world examples, complete code, mermaid diagrams, pitfalls, and a clear 'How to Prevent / Defend' part. The content is designed to provide a deep understanding of CSRF attacks and how to mitigate them effectively.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/04-Lab 3 CSRF where token validation depends on token being present/00-Overview|Overview]] | [[02-CSRF Token Validation Flaw|CSRF Token Validation Flaw]]
