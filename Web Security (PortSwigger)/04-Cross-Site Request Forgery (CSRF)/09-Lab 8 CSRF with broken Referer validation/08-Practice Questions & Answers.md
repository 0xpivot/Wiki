---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the email change functionality is considered a relevant action in the context of CSRF vulnerabilities.**

The email change functionality is considered a relevant action in the context of CSRF vulnerabilities because it can have a detrimental effect on the user. An attacker who exploits this functionality can change the user's email address to one controlled by the attacker. This allows the attacker to intercept password reset emails and gain unauthorized access to the user's account, thereby fully compromising the user's account.

**Q2. How does the application attempt to prevent CSRF attacks using the Referer header? Why is this mechanism flawed?**

The application attempts to prevent CSRF attacks by checking the Referer header to ensure that the origin of the CSRF script is the same as the origin of the application. This mechanism is flawed because the application only checks if the domain of the application is contained within the Referer header rather than ensuring that the entire Referer header matches the domain of the application. This allows attackers to bypass the defense by manipulating the Referer header to include the domain of the application as a query parameter.

**Q3. Describe how you would exploit the CSRF vulnerability by manipulating the Referer header. Provide an example payload.**

To exploit the CSRF vulnerability, you can manipulate the Referer header to include the domain of the application as a query parameter. Here’s an example payload:

```html
<script>
    // Change the Referer header to include the domain of the application as a query parameter
    history.pushState({}, "", "https://hacked-domain.com/?https://web-security-academy.net");
</script>

<form id="csrf-form" action="https://web-security-academy.net/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@example.com">
</form>

<script>
    // Submit the form automatically when the page loads
    document.getElementById('csrf-form').submit();
</script>
```

In this example, the `history.pushState` function is used to modify the Referer header to include the domain of the application (`https://web-security-academy.net`) as a query parameter. The form is then submitted automatically when the page loads, changing the user's email address to one controlled by the attacker.

**Q4. What recent real-world examples demonstrate the importance of proper Referer header validation in preventing CSRF attacks?**

One recent real-world example is the CVE-2021-21972 vulnerability found in the WordPress REST API. This vulnerability allowed attackers to perform CSRF attacks by manipulating the Referer header. The issue was that the WordPress REST API did not properly validate the Referer header, allowing attackers to bypass the CSRF protection mechanism. This highlights the importance of implementing robust Referer header validation to prevent such attacks.

**Q5. How would you configure a web server to ensure that query parameters are not stripped from the Referer header?**

To ensure that query parameters are not stripped from the Referer header, you can configure the web server to include the `Referrer-Policy` header with the value `unsafe-url`. This instructs the browser to include the full URL, including query parameters, in the Referer header. Here’s an example configuration for an Apache web server:

```apache
Header always set Referrer-Policy "unsafe-url"
```

This configuration ensures that the Referer header includes the full URL, making it more difficult for attackers to bypass Referer-based CSRF protections.

**Q6. Explain how the `history.pushState` method is used to manipulate the Referer header in the exploit.**

The `history.pushState` method is used to manipulate the Referer header by modifying the browser's session history stack. By calling `history.pushState`, you can change the current URL displayed in the browser without reloading the page. This change affects the Referer header that is sent with subsequent requests.

In the exploit, `history.pushState` is used to set the URL to a value that includes the domain of the application as a query parameter. When the form is submitted, the Referer header will contain this modified URL, bypassing the application's Referer validation mechanism.

Here’s an example:

```javascript
// Modify the Referer header by changing the current URL
history.pushState({}, "", "https://hacked-domain.com/?https://web-security-academy.net");

// Form submission code follows...
```

By setting the URL in this manner, the Referer header will include the domain of the application, allowing the CSRF attack to succeed.

**Q7. What steps can developers take to mitigate the risk of CSRF attacks, especially when dealing with broken Referer validation mechanisms?**

Developers can take several steps to mitigate the risk of CSRF attacks, even when dealing with broken Referer validation mechanisms:

1. **Implement CSRF Tokens**: Use unique, unpredictable tokens for each form submission. Ensure that these tokens are validated on the server side to prevent unauthorized submissions.

2. **Use SameSite Cookies**: Configure cookies with the `SameSite` attribute to restrict their usage to same-site requests. This helps prevent CSRF attacks by ensuring that cookies are not sent with cross-site requests.

3. **Double Submit Cookie Pattern**: Use a double submit cookie pattern where a CSRF token is embedded both in a cookie and as a hidden form field. Validate both values on the server side to ensure they match.

4. **HTTPOnly Cookies**: Set the `HttpOnly` flag on cookies to prevent them from being accessed via JavaScript, reducing the risk of XSS-based CSRF attacks.

5. **Regular Security Audits**: Conduct regular security audits and penetration testing to identify and fix potential CSRF vulnerabilities.

By implementing these measures, developers can significantly reduce the risk of CSRF attacks, even when Referer validation mechanisms are broken.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/07-Understanding the Lab Environment|Understanding the Lab Environment]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/09-Lab 8 CSRF with broken Referer validation/00-Overview|Overview]]
