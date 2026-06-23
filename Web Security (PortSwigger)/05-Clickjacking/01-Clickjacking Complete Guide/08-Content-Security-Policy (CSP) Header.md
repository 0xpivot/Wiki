---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Content-Security-Policy (CSP) Header

The `Content-Security-Policy` (CSP) header provides a more comprehensive approach to securing web applications. It includes the `frame-ancestors` directive, which controls which origins can embed a resource within a frame or iframe.

### Syntax and Values

The `frame-ancestors` directive supports the following values:

1. **none**: No origins are allowed to frame the content.
2. **self**: Only the origin of the page itself is allowed to frame the content.
3. **domain**: Specific domains are allowed to frame the content.
4. *** (wildcard)**: Any domain is allowed to frame the content.

#### Example Configuration

Here’s an example of setting the `Content-Security-Policy` header with the `frame-ancestors` directive:

```http
HTTP/1.1 200 OK
Date: Mon, 23 May 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Security-Policy: frame-ancestors 'none'

<!DOCTYPE html>
<html>
<head>
    <title>Secure Page</title>
</head>
<body>
    <h1>Welcome to the Secure Page</h1>
</body>
</html>
```

In this example, the `frame-ancestors` directive is set to `none`, meaning no origins are allowed to frame the content.

### Pitfalls and Common Mistakes

While CSP is powerful, it also has potential pitfalls:

1. **Incorrect Configuration**: Setting `frame-ancestors` to `*` can leave the site vulnerable to clickjacking.
2. **Complexity**: Managing a complex CSP policy can be challenging and prone to errors.
3. **Browser Compatibility**: While most modern browsers support CSP, older browsers may not enforce it.

### How to Prevent / Defend

To effectively use CSP with the `frame-ancestors` directive:

1. **Set the Directive Correctly**: Ensure the `frame-ancestors` directive is set to `none` or `self`.
2. **Test Across Browsers**: Verify that the directive works across different browsers and versions.
3. **Regular Audits**: Conduct regular audits to ensure the CSP policy remains effective and up-to-date.

---
<!-- nav -->
[[07-Content Security Policy (CSP)|Content Security Policy (CSP)]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[09-Detection and Prevention|Detection and Prevention]]
