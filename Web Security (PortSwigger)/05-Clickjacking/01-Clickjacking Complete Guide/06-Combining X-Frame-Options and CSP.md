---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Combining X-Frame-Options and CSP

For maximum security, it is recommended to use both `X-Frame-Options` and `Content-Security-Policy` headers. This ensures compatibility across different browsers and provides a layered defense.

### Example Configuration

Here’s an example of combining both headers:

```http
HTTP/1.1 200 OK
Date: Mon, 23 May 2 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'self'

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

In this example, both headers are set to restrict framing to the same origin.

### Pitfalls and Common Mistakes

When combining both headers:

1. **Consistency**: Ensure both headers are consistent in their restrictions.
2. **Testing**: Test the combined headers across different browsers to ensure they work as expected.
3. **Maintenance**: Regularly review and update the headers to maintain security.

### How to Prevent / Defend

To effectively combine `X-Frame-Options` and CSP:

1. **Set Both Headers**: Ensure both headers are set to restrict framing.
2. **Test Across Browsers**: Verify that both headers work across different browsers and versions.
3. **Regular Audits**: Conduct regular audits to ensure both headers remain effective and up-to-date.

---
<!-- nav -->
[[05-Clickjacking An In-Depth Analysis|Clickjacking An In-Depth Analysis]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[07-Content Security Policy (CSP)|Content Security Policy (CSP)]]
