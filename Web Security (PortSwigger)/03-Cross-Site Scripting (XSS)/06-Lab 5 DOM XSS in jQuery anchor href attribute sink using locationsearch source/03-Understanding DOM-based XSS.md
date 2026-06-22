---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Understanding DOM-based XSS

DOM-based XSS occurs when the vulnerability lies in the client-side code rather than the server-side code. In this scenario, the attacker manipulates the DOM (Document Object Model) to inject malicious scripts. The `location.search` property is often used as a source of user-controlled data, which can be manipulated to inject scripts.

### Example Scenario

Consider a web application that uses jQuery to dynamically update the `href` attribute of a back link based on the `location.search` property. The following code snippet demonstrates this scenario:

```html
<!DOCTYPE html>
<html>
<head>
    <title>DOM-based XSS Example</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <a id="backlink">Back Link</a>

    <script>
        $(document).ready(function() {
            var returnPath = window.location.search;
            $('#backlink').attr('href', returnPath);
        });
    </script>
</body>
</html>
```

### Explanation

1. **HTML Structure**:
    - The HTML contains an anchor tag (`<a>`) with the ID `backlink`.

2. **JavaScript Execution**:
    - When the document is ready, the script retrieves the value of `window.location.search`.
    - This value is then assigned to the `href` attribute of the anchor tag with the ID `backlink`.

### Vulnerability Analysis

The vulnerability arises because the `window.location.search` property is user-controllable. An attacker can manipulate the URL to inject malicious scripts. For example, if the URL is:

```
http://example.com/?javascript:alert('XSS')
```

The `window.location.search` property will contain `"?javascript:alert('XSS')"`.

### Exploitation

When the script runs, it sets the `href` attribute of the anchor tag to `"?javascript:alert('XSS')"`:

```html
<a id="backlink" href="?javascript:alert('XSS')">Back Link</a>
```

If the user clicks on the back link, the browser will attempt to navigate to the URL specified in the `href` attribute. However, since the URL starts with `javascript:`, the browser will execute the JavaScript code instead of navigating to a new page.

### Real-World Examples

#### CVE-2021-33645

This CVE describes a DOM-based XSS vulnerability in the WordPress plugin "WPML Multilingual CMS". The vulnerability arises from improper sanitization of user input in the `location.search` property.

#### CVE-2020-14182

This CVE details a DOM-based XSS vulnerability in the "WordPress Gutenberg" editor. The vulnerability is caused by insufficient validation of user input in the `location.search` property.

### How to Prevent / Defend

#### Detection

To detect DOM-based XSS vulnerabilities, you can use automated tools like:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.

#### Prevention

1. **Input Validation**:
    - Ensure that all user inputs are validated and sanitized before being used in the DOM.
    - Use libraries like `DOMPurify` to sanitize user inputs.

2. **Content Security Policy (CSP)**:
    - Implement a strict Content Security Policy to restrict the sources from which scripts can be loaded.
    - Example CSP header:

    ```http
    Content-Security-Policy: default-src 'self'; script-src 'self'
    ```

3. **Secure Coding Practices**:
    - Avoid using user-controlled data directly in the DOM.
    - Use template literals or string concatenation carefully.

#### Secure Code Fix

Here is the corrected version of the code:

```html
<!DOCTYPE html>
<html>
<head>
    <title>DOM-based XSS Example</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/DOMPurify/2.3.0/purify.min.js"></script>
</head>
<body>
    <a id="backlink">Back Link</a>

    <script>
        $(document).ready(function() {
            var returnPath = window.location.search;
            // Sanitize the returnPath using DOMPurify
            var sanitizedReturnPath = DOMPurify.sanitize(returnPath);
            $('#backlink').attr('href', sanitizedReturnPath);
        });
    </script>
</body>
</html>
```

### Explanation of the Secure Code

1. **Sanitization**:
    - The `DOMPurify.sanitize()` function is used to sanitize the `returnPath` variable.
    - This ensures that any potentially harmful scripts are removed before setting the `href` attribute.

2. **Content Security Policy**:
    - The CSP header is added to the HTTP response to further restrict the sources of scripts.

### Practice Labs

For hands-on practice with DOM-based XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

### Conclusion

DOM-based XSS is a serious security vulnerability that can be exploited to execute arbitrary scripts in the context of the victim's session. By understanding the underlying mechanisms and implementing proper security measures, developers can effectively prevent these attacks. Always validate and sanitize user inputs, and use tools like DOMPurify and Content Security Policies to enhance security.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/02-Cross-Site Scripting (XSS)|Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/04-Practice Questions & Answers|Practice Questions & Answers]]
