---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the CSRF token not being tied to the user session makes the application vulnerable.**

The CSRF token not being tied to the user session means that the token can be reused across different sessions. In this scenario, an attacker can obtain a CSRF token from their own session and use it to craft a malicious request that targets another user's session. Since the token is not unique to the user's session, the server cannot distinguish between legitimate and malicious requests, leading to a successful CSRF attack. This is evident in the lab where the CSRF token from Carlos's session was used to change the email address of the victim's session.

**Q2. How would you exploit the CSRF vulnerability described in the lab? Provide a step-by-step explanation.**

To exploit the CSRF vulnerability:

1. Obtain a CSRF token from the attacker’s session.
2. Craft an HTML form that includes the CSRF token and the desired email address.
3. Ensure the form is set to automatically submit upon loading.
4. Host the HTML form on a web server.
5. Trick the victim into visiting the hosted page, which will automatically submit the form and change the email address.

Here is a sample HTML payload:

```html
<html>
<body onload="document.getElementById('csrf_form').submit()">
<form id="csrf_form" action="https://example.com/change-email" method="POST" target="csrf_iframe">
<input type="hidden" name="email" value="attacker@example.com">
<input type="hidden" name="csrf_token" value="obtained_token_value">
</form>
<iframe name="csrf_iframe" style="display:none;"></iframe>
</body>
</html>
```

**Q3. Why is the CSRF token not tied to the user session a critical flaw in web security?**

The CSRF token not being tied to the user session is a critical flaw because it undermines the purpose of CSRF protection. CSRF tokens are designed to ensure that a request originates from a trusted source within the user's session. When the token is not tied to the session, an attacker can reuse the token across different sessions, effectively bypassing the CSRF protection mechanism. This allows attackers to perform actions on behalf of the victim without their knowledge or consent, leading to potential account hijacking and data breaches.

**Q4. What recent real-world example demonstrates the importance of tying CSRF tokens to user sessions?**

One recent example is the 2021 breach of a major cryptocurrency exchange, where attackers exploited a CSRF vulnerability to steal funds from users' accounts. The exchange had implemented CSRF tokens, but these tokens were not properly tied to individual user sessions. As a result, attackers could reuse the tokens obtained from their own sessions to perform unauthorized transactions on other users' accounts. This highlights the critical importance of ensuring that CSRF tokens are uniquely associated with each user session to prevent such attacks.

**Q5. How can developers ensure that CSRF tokens are tied to user sessions effectively?**

Developers can ensure that CSRF tokens are tied to user sessions effectively by:

1. Generating a unique CSRF token for each user session.
2. Storing the CSRF token in a secure session variable.
3. Validating the CSRF token on the server side against the session variable before processing any form submissions.
4. Regenerating the CSRF token after each successful form submission to prevent replay attacks.
5. Using HTTP-only cookies to store the CSRF token to prevent access via JavaScript.

By implementing these measures, developers can significantly reduce the risk of CSRF attacks and ensure that the CSRF protection mechanism is effective.

**Q6. What are the three conditions that must be satisfied for a CSRF attack to be successful, as mentioned in the lab?**

The three conditions that must be satisfied for a CSRF attack to be successful are:

1. **Relevant Action**: The action performed by the CSRF attack must have significant consequences, such as changing an email address or making a financial transaction.
2. **Purely Cookie-Based Session Handling**: The application must rely solely on cookies for session management, without additional authentication mechanisms like multi-factor authentication.
3. **No Unpredictable Request Parameters**: The attacker must know all the parameters required to make the request successful, including any CSRF tokens or other security tokens.

In the lab, the application met the first two conditions but failed the third due to the CSRF token not being tied to the user session, making it vulnerable to CSRF attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/05-Lab 4 CSRF where token is not tied to user session/06-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/05-Lab 4 CSRF where token is not tied to user session/00-Overview|Overview]]
