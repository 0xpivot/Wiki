---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Understanding the Lab Setup

In the given lab scenario, we are dealing with a web application that has an unauthenticated admin panel at `/admin`. The application has implemented some form of access control, but it is flawed, allowing us to exploit it.

### Lab Environment

The lab environment is set up on the PortSwigger Web Security Academy platform. To access the lab, you need to:

1. Visit `portswigger.net/web-security`.
2. Sign up for an account if you don't already have one.
3. Navigate to the Academy section.
4. Select the appropriate learning path.
5. Choose the Access Control module.
6. Select Lab No. 5 titled "URL-based access control can be circumvented."

### Initial Observations

Upon accessing the lab, you will notice that the admin panel is located at `/admin`. However, the application has implemented some form of access control to prevent unauthorized access. Specifically, a front-end system has been configured to block external access to this path.

### Front-End vs. Back-End Access Control

The front-end system is typically implemented using JavaScript or other client-side technologies. While it can provide some level of protection, it is inherently insecure because client-side code can be easily bypassed or modified.

On the other hand, the back-end system is implemented using server-side technologies such as PHP, Java, or Python. This is generally more secure because it cannot be directly manipulated by the client.

### X-Original-URL Header

One key aspect of this lab is the use of the `X-Original-URL` header. This header is used by some frameworks to support URL rewriting or proxying. When a request is made to the server, the framework may check this header to determine the original URL requested by the client.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to understand how the `X-Original-URL` header can be used to bypass the front-end access control. By manipulating this header, we can trick the server into thinking that the request originated from an allowed path, thus gaining access to the admin panel.

### Step-by-Step Exploitation

1. **Identify the Vulnerable Path**: The admin panel is located at `/admin`.

2. **Check the Current Request**: Use Burp Suite to intercept the current request to the application. You will likely see a request to the main page of the application.

3. **Modify the Request**: Modify the intercepted request to include the `X-Original-URL` header. Set the value of this header to `/admin`.

4. **Send the Modified Request**: Send the modified request to the server. If the server is vulnerable, it will process the request as if it came from the `/admin` path, allowing you to access the admin panel.

### Example Code

Here is an example of how you might modify the request using Burp Suite:

```http
GET / HTTP/1.1
Host: vulnerable-app.com
User-Agent: Mozilla/5.0
Accept: */*
X-Original-URL: /admin
```

When you send this request, the server should respond with the contents of the admin panel.

### Common Pitfalls

1. **Client-Side Checks**: Relying solely on client-side checks is a common mistake. Always implement server-side validation to ensure proper access control.

2. **Header Manipulation**: Be aware that headers like `X-Original-URL` can be manipulated. Ensure that your application properly validates and sanitizes all input.

3. **Insufficient Logging**: Lack of proper logging can make it difficult to detect and respond to access control violations. Ensure that your application logs all access attempts and suspicious activity.

---
<!-- nav -->
[[08-Testing for Access Control Vulnerabilities|Testing for Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/06-Lab 5 URL based access control can be circumvented/10-Conclusion|Conclusion]]
