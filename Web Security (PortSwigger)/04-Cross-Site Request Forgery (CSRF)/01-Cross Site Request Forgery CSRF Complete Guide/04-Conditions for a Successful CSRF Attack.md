---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Conditions for a Successful CSRF Attack

For a CSRF attack to be successful, three conditions must be met:

1. **Relevant Action**: The action being performed must have significant consequences, such as transferring money or changing account settings.
2. **Cookie-Based Session Handling**: The web application must rely on cookies for session management.
3. **No Unpredictable Request Parameters**: The request must not contain any parameters that the attacker cannot predict.

### Relevant Action

A relevant action is one that has meaningful consequences. For example, transferring funds, changing passwords, or deleting accounts. These actions are typically protected by authentication mechanisms but can still be exploited through CSRF if not properly safeguarded.

### Cookie-Based Session Handling

Most web applications use cookies to manage user sessions. When a user logs in, the server sets a session cookie that the browser sends with subsequent requests. This cookie identifies the user to the server. In a CSRF attack, the attacker relies on the presence of this cookie to authenticate the request.

### No Unpredictable Request Parameters

To prevent CSRF, web applications often include an additional parameter called a CSRF token. This token is unique per session and unpredictable to the attacker. When the attacker attempts to forge a request, they cannot provide the correct CSRF token, causing the request to be rejected.

---
<!-- nav -->
[[03-CSRF Tokens and Cookies|CSRF Tokens and Cookies]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/01-Cross Site Request Forgery CSRF Complete Guide/05-Cross-Site Request Forgery (CSRF)|Cross-Site Request Forgery (CSRF)]]
