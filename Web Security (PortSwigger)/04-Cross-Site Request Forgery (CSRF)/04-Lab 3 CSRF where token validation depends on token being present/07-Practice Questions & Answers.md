---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the presence of a CSRF token does not necessarily prevent a CSRF attack in this lab.**

The presence of a CSRF token does not necessarily prevent a CSRF attack in this lab because the backend implementation checks the CSRF token only if it is present. If the CSRF token is absent, the request is accepted without validation. This means that an attacker can simply omit the CSRF token from their malicious request, and the server will still process the request, leading to a successful CSRF attack.

**Q2. How would you exploit the CSRF vulnerability in this lab using the Burp Suite Professional?**

To exploit the CSRF vulnerability using Burp Suite Professional:

1. Intercept the POST request to change the email address.
2. Remove the CSRF token from the intercepted request.
3. Send the modified request to Burp Repeater.
4. Use the "Generate CSRF POC" feature under Engagement Tools to generate a proof-of-concept HTML payload.
5. Include the auto-submit script option to automatically submit the form.
6. Copy the generated HTML and host it on the exploit server.
7. Deliver the exploit to the victim by sending them the link to the hosted HTML.

Here is an example of the generated HTML payload:

```html
<html>
<body onload="document.getElementById('csrf_form').submit()">
<form id="csrf_form" action="http://example.com/change_email" method="POST">
<input type="hidden" name="email" value="test3@test.ca" />
</form>
</body>
</html>
```

**Q3. How would you manually exploit the CSRF vulnerability in this lab using the Burp Suite Community Edition?**

To manually exploit the CSRF vulnerability using Burp Suite Community Edition:

1. Intercept the POST request to change the email address.
2. Remove the CSRF token from the intercepted request.
3. Create an HTML form with the same parameters as the intercepted request.
4. Add a script to automatically submit the form when the page loads.
5. Host the HTML form on your own web server.
6. Send the link to the victim to trigger the CSRF attack.

Here is an example of the manual HTML payload:

```html
<html>
<body onload="document.getElementById('csrf_form').submit()">
<form id="csrf_form" action="http://example.com/change_email" method="POST">
<input type="hidden" name="email" value="test5@test.ca" />
</form>
</body>
</html>
```

**Q4. Why is the CSRF token not considered an unpredictable request parameter in this lab?**

The CSRF token is not considered an unpredictable request parameter in this lab because its presence is not mandatory for the request to be processed. The backend implementation checks the CSRF token only if it is present; otherwise, it accepts the request without validating the token. This makes the CSRF token non-mandatory and thus not an effective safeguard against CSRF attacks.

**Q5. Discuss recent real-world examples of CSRF vulnerabilities and how they were exploited.**

One notable example is the CSRF vulnerability in the Tesla Model S cars, reported in 2019 (CVE-2019-18135). Attackers could craft a malicious website that, when visited by a Tesla owner, could send commands to the car via the Tesla mobile app. This could potentially lock the car or even start it remotely.

Another example is the CSRF vulnerability in the WordPress REST API, discovered in 2017 (CVE-2017-1000367). Attackers could craft a malicious link that, when clicked by a logged-in WordPress admin, could execute arbitrary actions such as creating new posts or modifying existing ones.

In both cases, the vulnerabilities were exploited due to the lack of proper CSRF protection mechanisms, allowing attackers to trick authenticated users into performing unintended actions on behalf of the attacker.

---
<!-- nav -->
[[06-Understanding CSRF Tokens|Understanding CSRF Tokens]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/04-Lab 3 CSRF where token validation depends on token being present/00-Overview|Overview]]
