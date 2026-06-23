---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## SameSite Attribute and CSRF Mitigation

The SameSite attribute is a security feature introduced by web browsers to mitigate CSRF attacks. It controls whether a cookie should be sent with cross-origin requests.

### What is the SameSite Attribute?

The SameSite attribute is added to cookies and specifies whether the cookie should be sent with cross-origin requests. There are three possible values for the SameSite attribute:

1. **Strict**: The cookie will only be sent with requests originating from the same site as the one that set the cookie.
2. **Lax**: The cookie will be sent with top-level navigations and with POST requests, but not with subresource loads like images or scripts.
3. **None**: The cookie will be sent with all requests, regardless of origin. This value requires the Secure attribute to be set.

### Why Does the SameSite Attribute Matter?

The SameSite attribute helps prevent CSRF attacks by controlling the context in which cookies are sent. By setting the SameSite attribute to `Strict` or `Lax`, web applications can reduce the risk of CSRF attacks.

### How Does the SameSite Attribute Work Under the Hood?

When a browser receives a cookie with the SameSite attribute, it enforces the specified behavior:

- **Strict**: The cookie is only sent with requests originating from the same site.
- **Lax**: The cookie is sent with top-level navigations and POST requests, but not with subresource loads.
- **None**: The cookie is sent with all requests, but only if the Secure attribute is set.

### Real-World Example: SameSite Attribute in Practice

Consider a scenario where a web application sets a cookie with the SameSite attribute set to `Lax`. An attacker tries to craft a malicious request to change the user's email address. If the user clicks on a link that triggers a cross-origin request, the cookie will not be sent because the request is not a top-level navigation or a POST request. This prevents the CSRF attack from succeeding.

### Common Pitfalls Without the SameSite Attribute

Without the SameSite attribute, web applications are more susceptible to CSRF attacks. Attackers can craft malicious requests that include the necessary cookies, leading to unauthorized actions being executed on behalf of the user.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/13-Lab 12 SameSite Lax bypass via cookie refresh/05-How to Prevent  Defend Against CSRF Attacks|How to Prevent  Defend Against CSRF Attacks]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/13-Lab 12 SameSite Lax bypass via cookie refresh/00-Overview|Overview]] | [[07-SameSite Lax Bypass via Cookie Refresh|SameSite Lax Bypass via Cookie Refresh]]
