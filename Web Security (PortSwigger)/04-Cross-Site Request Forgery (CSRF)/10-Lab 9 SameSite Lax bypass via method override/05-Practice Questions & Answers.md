---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the lack of a SameSite attribute in the session cookie is significant in this lab.**

The absence of a SameSite attribute in the session cookie means that the browser will use its default setting, which is `Lax` for Chrome. This configuration restricts the session cookie from being sent in cross-domain POST requests, making it harder to exploit CSRF vulnerabilities. However, it allows GET requests to pass the session cookie, which can be exploited if the functionality can be coerced into a GET request.

**Q2. How would you exploit the CSRF vulnerability in this lab despite the SameSite attribute being set to `Lax`?**

To exploit the CSRF vulnerability despite the SameSite attribute being set to `Lax`, we can use the `_method` parameter to override the HTTP method. By sending a GET request with the `_method` parameter set to `POST`, we can simulate a POST request. This bypasses the restriction imposed by the `Lax` setting, allowing us to change the email address.

Here’s an example of how to craft the exploit:

```html
<script>
document.location = 'https://example.com/my-account/change-email?email=test@test.com&_method=POST';
</script>
```

This script, when executed in the victim's browser, will change their email address.

**Q3. Why is it important to ensure that the exploit is triggered through a top-level navigation rather than an iframe?**

The `Lax` SameSite attribute ensures that the session cookie is only sent with top-level navigations, meaning the request must originate from the main browser window and not from an iframe. If the exploit is embedded in an iframe, the session cookie will not be sent, and the CSRF attack will fail. Ensuring the exploit is triggered through a top-level navigation guarantees that the session cookie is included in the request, allowing the attack to succeed.

**Q4. What is the significance of the `_method` parameter in web frameworks, and how does it help in this lab?**

The `_method` parameter is used in some web frameworks to override the HTTP method of a request. It allows developers to simulate different HTTP methods (like POST) using a different method (like GET). In this lab, the `_method` parameter is crucial because it enables us to bypass the `Lax` SameSite restriction by simulating a POST request with a GET request. This is necessary since the `Lax` configuration blocks POST requests from cross-domain origins.

**Q5. How would you modify the exploit script to ensure that the email addresses are unique for each victim?**

To ensure that the email addresses are unique for each victim, you can dynamically generate the email address using a variable or a counter. Here’s an example using a simple counter:

```html
<script>
var counter = 1;
document.location = 'https://example.com/my-account/change-email?email=test' + counter + '@test.com&_method=POST';
counter++;
</script>
```

Alternatively, you can use a timestamp or a random number generator to create unique email addresses:

```html
<script>
var timestamp = new Date().getTime();
document.location = 'https://example.com/my-account/change-email?email=test' + timestamp + '@test.com&_method=POST';
</script>
```

This ensures that each victim receives a unique email address, preventing conflicts due to duplicate entries.

**Q6. Discuss a recent real-world example where a SameSite attribute misconfiguration led to a security breach.**

A notable example is the Twitter OAuth flaw discovered in 2020 (CVE-2020-28487). The issue arose from a misconfigured SameSite attribute on cookies used in the OAuth process. The cookies were set with `SameSite=None`, but without the `Secure` flag, allowing attackers to steal OAuth tokens via cross-site scripting (XSS) attacks. This misconfiguration enabled attackers to bypass the intended security measures, leading to unauthorized access to user accounts.

In this lab, understanding the importance of proper SameSite attribute configuration helps prevent similar vulnerabilities. Always ensure that cookies are configured correctly, especially when dealing with sensitive operations like authentication and authorization.

---
<!-- nav -->
[[04-Understanding SameSite Attribute|Understanding SameSite Attribute]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/10-Lab 9 SameSite Lax bypass via method override/00-Overview|Overview]]
