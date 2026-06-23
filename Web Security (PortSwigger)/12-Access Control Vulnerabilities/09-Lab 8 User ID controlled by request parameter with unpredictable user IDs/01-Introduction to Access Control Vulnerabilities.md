---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web application security. They allow attackers to bypass intended restrictions on what authenticated users are allowed to do. One such vulnerability is the horizontal privilege escalation, which occurs when a user gains unauthorized access to resources belonging to other users within the same role or privilege level. In this chapter, we will delve deep into a specific type of horizontal privilege escalation vulnerability: user ID controlled by request parameters with unpredictable user IDs.

### Background Theory

#### What is Horizontal Privilege Escalation?

Horizontal privilege escalation is a type of access control vulnerability where a user gains unauthorized access to resources belonging to other users within the same role or privilege level. This contrasts with vertical privilege escalation, where a lower-privileged user gains access to higher-privileged resources.

#### Importance of Proper Access Control

Proper access control is crucial for maintaining the integrity and confidentiality of data in web applications. Without robust access controls, sensitive information can be exposed to unauthorized users, leading to data breaches and other security incidents.

### Understanding User IDs and GUIDs

#### What is a User ID?

A user ID is a unique identifier assigned to each user in a system. It is used to distinguish between different users and to manage their access to resources. User IDs can take various forms, including numeric IDs, alphanumeric strings, or GUIDs.

#### What is a GUID?

A GUID (Globally Unique Identifier) is a 128-bit number used to uniquely identify information in computer systems. GUIDs are designed to be unique across both space and time, making them ideal for identifying users in distributed systems.

### Real-World Example: CVE-2021-21972

One real-world example of a horizontal privilege escalation vulnerability involving user IDs is CVE-2021-21972, which affected the WordPress plugin "WP Customer Reviews." The vulnerability allowed an attacker to manipulate the `review_id` parameter in the URL to view and modify reviews belonging to other users. This could lead to unauthorized access to sensitive information and potential data tampering.

### Lab Setup and Environment

In this lab, we will use the Web Security Academy platform to explore a horizontal privilege escalation vulnerability involving user IDs controlled by request parameters. The lab environment is set up to simulate a web application where user accounts are identified using GUIDs.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the Web Security Academy website at `https://url.org.net/WebSecurity`.
2. Click on the sign-up button to create an account if you do not already have one.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for access control.
6. Choose the lab titled "User ID controlled by request parameter with unpredictable user IDs."

### Lab Objective

The objective of this lab is to find the GUID of the user named "Carlos" and compromise his account by submitting his API key as the solution.

### Lab Walkthrough

#### Logging into Your Account

First, log into your own account using the provided credentials. The credentials might look something like this:

```plaintext
Username: your_username
Password: your_password
```

Once logged in, navigate to the user account page. Notice that the page is loaded using the built-in browser in the Burp Suite proxy, ensuring that all requests are intercepted and analyzed.

### Analyzing the Request and Response

To understand the vulnerability, we need to analyze the HTTP request and response. Here is a typical HTTP request to the user account page:

```http
GET /account?user_id=your_guid HTTP/1.1
Host: url.org.net
Cookie: session=your_session_cookie
```

And the corresponding HTTP response:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=your_session_cookie; Path=/; HttpOnly
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>User Account</title>
</head>
<body>
    <h1>Welcome, your_username!</h1>
    <p>Your API Key: your_api_key</p>
</body>
</html>
```

### Identifying the Vulnerability

The vulnerability lies in the fact that the user ID is controlled by a request parameter (`user_id`). An attacker can manipulate this parameter to access the account of any user, provided they know the GUID.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to find the GUID of the user "Carlos." We can achieve this through various methods, such as brute-forcing, social engineering, or analyzing the application's behavior.

#### Brute-Forcing GUIDs

GUIDs are 128-bit numbers, which means there are approximately \(2^{128}\) possible GUIDs. Brute-forcing all possible GUIDs is impractical due to the sheer number of possibilities. However, if the GUID generation algorithm is weak or predictable, it may be feasible to narrow down the search space.

#### Social Engineering

Another method is to use social engineering techniques to obtain the GUID of "Carlos." This could involve tricking "Carlos" into revealing his GUID or intercepting communication where the GUID is transmitted.

#### Analyzing Application Behavior

We can also analyze the application's behavior to infer the GUID of "Carlos." For example, if the application generates GUIDs sequentially or based on some predictable pattern, we can make educated guesses about the GUID.

### Finding Carlos's GUID

Assume we have found the GUID of "Carlos" through one of the above methods. Let's say the GUID is `carlos_guid`.

#### Crafting the Exploit

Now, we can craft an HTTP request to access "Carlos's" account:

```http
GET /account?user_id=carlos_guid HTTP/1.1
Host: url.org.net
Cookie: session=your_session_cookie
```

And the corresponding HTTP response:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Set-Cookie: session=your_session_cookie; Path=/; HttpOnly
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
    <title>User Account</title>
</head>
<body>
    <h1>Welcome, carlos!</h1>
    <p>Your API Key: carlos_api_key</p>
</body>
</html>
```

### Submitting the Solution

Once we have obtained "Carlos's" API key, we can submit it as the solution to the lab.

### How to Prevent / Defend Against Access Control Vulnerabilities

#### Secure Coding Practices

1. **Validate Input**: Ensure that user input is validated and sanitized to prevent manipulation of request parameters.
2. **Use Strong Authentication Mechanisms**: Implement strong authentication mechanisms, such as multi-factor authentication, to ensure that only authorized users can access sensitive resources.
3. **Role-Based Access Control (RBAC)**: Implement RBAC to restrict access to resources based on user roles and permissions.

#### Secure Configuration

1. **Secure Session Management**: Use secure session management practices, such as setting the `HttpOnly` flag on cookies to prevent client-side scripts from accessing session data.
2. **Input Validation**: Configure input validation rules to reject invalid or suspicious input.

#### Detection and Monitoring

1. **Logging and Monitoring**: Implement logging and monitoring to detect and respond to suspicious activity. Monitor access logs for unusual patterns of access.
2. **Penetration Testing**: Regularly perform penetration testing to identify and mitigate access control vulnerabilities.

### Secure Code Examples

#### Vulnerable Code

```python
@app.route('/account')
def account():
    user_id = request.args.get('user_id')
    user = get_user_by_id(user_id)
    return render_template('account.html', user=user)
```

#### Secure Code

```python
@app.route('/account')
@login_required
def account():
    user_id = current_user.id
    user = get_user_by_id(user_id)
    return render_template('account.html', user=user)
```

### Conclusion

Access control vulnerabilities, particularly horizontal privilege escalation, pose significant risks to web applications. By understanding the underlying principles and implementing robust security measures, developers can mitigate these risks and protect sensitive data.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including access control vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and practicing web security.

By engaging with these labs, you can gain practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/09-Lab 8 User ID controlled by request parameter with unpredictable user IDs/00-Overview|Overview]] | [[02-Access Control Vulnerabilities User ID Controlled by Request Parameter with Unpredictable User IDs|Access Control Vulnerabilities User ID Controlled by Request Parameter with Unpredictable User IDs]]
