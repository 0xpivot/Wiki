---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the conditions necessary for a CSRF attack to be possible.**

The three conditions necessary for a CSRF attack to be possible are:
1. **Relevant Action**: There must be an action that, if compromised, can lead to dangerous consequences. For example, changing an email address can allow an attacker to reset the password and take over the account.
2. **Cookie-Based Session Handling**: The application must use cookies to handle sessions. This means that the session identifier is stored in a cookie, which is sent with each request.
3. **No Unpredictable Request Parameters**: The attacker must know all the parameters required for the request to be successful. If there are unpredictable parameters, such as a CSRF token, the attacker cannot predict the exact request needed to exploit the vulnerability.

**Q2. How does the application in the lab attempt to defend against CSRF attacks, and why is it incomplete?**

The application attempts to defend against CSRF attacks by using a CSRF token, which is typically validated for POST requests. However, this defense is incomplete because:
- The CSRF token is not validated for GET requests.
- The application allows changing the request method from POST to GET, which bypasses the CSRF token validation.
- Since the application does not enforce CSRF token validation for GET requests, an attacker can exploit this by sending a GET request to perform actions that should require a POST request.

**Q3. How would you exploit the CSRF vulnerability in this lab using an HTML page hosted on an exploit server?**

To exploit the CSRF vulnerability, you can create an HTML page with a form that sends a GET request to change the email address. Here’s an example of how to script this:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSRF Exploit</title>
</head>
<body>
    <h1>Hello World</h1>
    <form id="csrfForm" action="http://example.com/my-account/change-email" method="GET">
        <input type="hidden" name="email" value="attacker@example.com">
    </form>
    <script>
        document.getElementById('csrfForm').submit();
    </script>
    <iframe name="csrfIframe" style="display:none;"></iframe>
</body>
</html>
```

This script creates a form that automatically submits a GET request to change the email address to `attacker@example.com`. The form submission is hidden within an iframe, so the user does not see the form submission process.

**Q4. Why is the CSRF token not checked for GET requests in this lab, and how does this affect the security of the application?**

The CSRF token is not checked for GET requests because the application assumes that GET requests are only used for retrieving data and not for modifying data. This assumption is incorrect because the application allows changing the request method from POST to GET, which can be used to modify data.

This affects the security of the application because:
- An attacker can craft a malicious link that, when clicked, sends a GET request to perform actions that should require a POST request.
- Without proper validation of the CSRF token for GET requests, the attacker can bypass the CSRF protection mechanism.
- This vulnerability allows the attacker to perform unauthorized actions, such as changing the email address, leading to potential account takeover.

**Q5. How would you fix the CSRF vulnerability in this lab to prevent such attacks?**

To fix the CSRF vulnerability, the application should validate the CSRF token for all types of requests, including GET requests. Here are the steps to implement this fix:
1. **Generate a CSRF Token**: Generate a unique CSRF token for each session.
2. **Include the CSRF Token**: Include the CSRF token in all forms and requests, both POST and GET.
3. **Validate the CSRF Token**: Validate the CSRF token on the server side for all requests, ensuring that the token matches the expected value.

By enforcing CSRF token validation for all request methods, the application can prevent attackers from exploiting the vulnerability by changing the request method.

**Q6. Reference a recent real-world example (CVE or breach) where a similar CSRF vulnerability was exploited. Explain how it was exploited.**

A recent real-world example is the CVE-2021-30116, which affected the WordPress REST API. The vulnerability allowed attackers to perform unauthorized actions via CSRF attacks.

In this case, the vulnerability was exploited by:
1. **Crafting a Malicious Link**: The attacker crafted a malicious link that, when clicked, sent a POST request to the WordPress REST API to perform actions such as creating or modifying posts.
2. **Bypassing CSRF Protection**: The WordPress REST API did not properly validate the CSRF token for certain actions, allowing the attacker to bypass the CSRF protection mechanism.
3. **Exploiting the Vulnerability**: When a user clicked the malicious link, the attacker could perform unauthorized actions on the WordPress site, leading to potential data loss or unauthorized content modification.

By understanding and fixing similar vulnerabilities, developers can enhance the security of their applications against CSRF attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/14-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]]
